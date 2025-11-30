import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

df_resp = pd.read_csv("../clean_data/presenciais_dadosavdisciplinas.csv")
df_q = pd.read_csv("../clean_data/presenciais_perguntas.csv")
df_disc = pd.read_csv("../clean_data/presenciais_disciplinas.csv")

df = df_resp.merge(
    df_q,
    on=["ID_PERGUNTA", "ID_QUESTIONARIO"],
    how="left"
)

df = df.merge(
    df_disc,
    on=["COD_DISCIPLINA", "COD_CURSO"],
    how="left",
    suffixes=("_x", "_DISC")
)

if "CURSO_x" in df.columns:
    df.rename(columns={"CURSO_x": "CURSO"}, inplace=True)
if "CURSO_DISC" in df.columns:
    df.rename(columns={"CURSO_DISC": "CURSO_DISCIPLINA"}, inplace=True)

if "SETOR_CURSO_x" in df.columns:
    df.rename(columns={"SETOR_CURSO_x": "SETOR_CURSO"}, inplace=True)
if "SETOR_CURSO_DISC" in df.columns:
    df.rename(columns={"SETOR_CURSO_DISC": "SETOR_CURSO_DISCIPLINA"}, inplace=True)

if "PERGUNTA_y" in df.columns:
    df.rename(columns={"PERGUNTA_y": "PERGUNTA"}, inplace=True)
if "PERGUNTA_x" in df.columns:
    df.drop(columns=["PERGUNTA_x"], inplace=True)

ordem_likert = ["Discordo", "Desconheço", "Concordo"]

app = Dash(__name__)

perguntas_unicas = sorted(df["PERGUNTA"].dropna().unique())
mapeamento_perguntas = {}
opcoes_perguntas = []

for i, pergunta in enumerate(perguntas_unicas, 1):
    palavras = pergunta.split()[:7]
    label_resumido = " ".join(palavras) + "..." if len(palavras) == 7 else pergunta
    label_final = f"P{i}: {label_resumido}"
    
    mapeamento_perguntas[label_final] = pergunta
    opcoes_perguntas.append({
        "label": label_final,
        "value": label_final
    })

app.layout = html.Div([
    html.H1("Avaliação de Disciplinas Presenciais", style={"marginBottom": "20px"}),

    html.Div([
        html.Label("ID da Pesquisa"),
        dcc.Dropdown(
            id="filtro-id",
            options=[{"label": str(id_pesquisa), "value": id_pesquisa} for id_pesquisa in sorted(df["ID_PESQUISA"].dropna().unique())],
            multi=True,
            placeholder="Selecione o(s) ID(s)"
        ),
    ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

    html.Div([
        html.Label("Curso"),
        dcc.Dropdown(
            id="filtro-curso",
            options=[{"label": c, "value": c} for c in sorted(df["CURSO"].dropna().unique())],
            multi=True,
            placeholder="Selecione o(s) curso(s)"
        ),
    ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

    html.Div([
        html.Label("Pergunta"),
        dcc.Dropdown(
            id="filtro-pergunta",
            options=opcoes_perguntas,
            multi=True,
            placeholder="Selecione a(s) pergunta(s)",
            style={'minWidth': '450px'}
        ),
    ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

    html.Br(), html.Br(),

    dcc.Graph(id="grafico-likert"),
])

@app.callback(
    Output("grafico-likert", "figure"),
    Input("filtro-id", "value"),
    Input("filtro-curso", "value"),
    Input("filtro-pergunta", "value"),
)
def atualizar_graficos(ids, cursos, perguntas_selecionadas):
    dff = df.copy()

    if ids:
        dff = dff[dff["ID_PESQUISA"].isin(ids)]
    if cursos:
        dff = dff[dff["CURSO"].isin(cursos)]
    if perguntas_selecionadas:
        perguntas_completas = [mapeamento_perguntas[p] for p in perguntas_selecionadas]
        dff = dff[dff["PERGUNTA"].isin(perguntas_completas)]

    likert_df = (
        dff.groupby(["PERGUNTA", "RESPOSTA"])
           .size()
           .reset_index(name="Quantidade")
    )
    
    total_por_pergunta = likert_df.groupby("PERGUNTA")["Quantidade"].transform('sum')
    likert_df["Percentual"] = (likert_df["Quantidade"] / total_por_pergunta * 100).round(1)
    
    likert_df["RESPOSTA"] = pd.Categorical(
        likert_df["RESPOSTA"],
        categories=ordem_likert,
        ordered=True
    )
    
    taxa_concordo = (
        likert_df[likert_df["RESPOSTA"] == "Concordo"]
        .set_index("PERGUNTA")["Percentual"]
        .to_dict()
    )
    
    likert_df["ordem_concordo"] = likert_df["PERGUNTA"].map(taxa_concordo).fillna(0)
    likert_df.sort_values(["ordem_concordo", "PERGUNTA", "RESPOSTA"], ascending=[False, True, True], inplace=True)

    fig_likert = px.bar(
        likert_df,
        x="Percentual",
        y="PERGUNTA",
        color="RESPOSTA",
        barmode="stack",
        title="Distribuição de Respostas por Pergunta",
        labels={
            "PERGUNTA": "Pergunta", 
            "Percentual": "Percentual de Respostas (%)", 
            "RESPOSTA": "Resposta"
        },
        color_discrete_map={
            "Concordo": "#2E8B57",
            "Desconheço": "#FFA500",
            "Discordo": "#DC143C"
        },
        hover_data={"Quantidade": True, "Percentual": True}
    )
    
    fig_likert.update_layout(
        margin=dict(l=150, r=50, t=80, b=50),
        legend=dict(
            title="Respostas:",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        title=dict(
            text="Distribuição de Respostas por Pergunta",
            x=0.5,
            xanchor="center",
            font=dict(size=20, family="Arial")
        ),
        font=dict(size=12)
    )
    
    fig_likert.update_xaxes(
        ticksuffix="%",
        range=[0, 100]
    )
    
    fig_likert.update_yaxes(
        title=None,
        categoryorder="total ascending"
    )
    
    totais = likert_df.groupby("PERGUNTA")["Quantidade"].sum().reset_index()
    
    for idx, row in totais.iterrows():
        fig_likert.add_annotation(
            x=105,
            y=row["PERGUNTA"],
            text=f"n={row['Quantidade']}",
            showarrow=False,
            xanchor="left",
            font=dict(size=10, color="gray")
        )

    return fig_likert

if __name__ == "__main__":
    app.run(debug=True)