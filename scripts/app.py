import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output

# =============================================================
# CARREGAR TODOS OS DADOS
# =============================================================

# Dados Presenciais
df_pres_resp = pd.read_csv("../clean_data/presenciais_dadosavdisciplinas.csv")
df_pres_q = pd.read_csv("../clean_data/presenciais_perguntas.csv")
df_pres_disc = pd.read_csv("../clean_data/presenciais_disciplinas.csv")

# Dados Cursos
df_curso_resp = pd.read_csv("../clean_data/cursos_dadosavcursos.csv")
df_curso_q = pd.read_csv("../clean_data/cursos_perguntas.csv")
df_curso_info = pd.read_csv("../clean_data/cursos_curso.csv")

# Dados EAD
df_ead_resp = pd.read_csv("../clean_data/ead_pesq423_discip.csv")
df_ead_q = pd.read_csv("../clean_data/ead_perguntas.csv")
df_ead_disc = pd.read_csv("../clean_data/ead_disciplinas.csv")

# Dados Institucional
df_inst_resp = pd.read_csv("../clean_data/institucional_pesquisa 442.csv")
df_inst_q = pd.read_csv("../clean_data/institucional_perguntas.csv")
df_inst_unidades = pd.read_csv("../clean_data/institucional_unidades.csv")

# =============================================================
# PROCESSAR DADOS PARA CADA CATEGORIA
# =============================================================

def processar_dados_presenciais():
    df = df_pres_resp.merge(df_pres_q, on=["ID_PERGUNTA", "ID_QUESTIONARIO"], how="left")
    df = df.merge(df_pres_disc, on=["COD_DISCIPLINA", "COD_CURSO"], how="left", suffixes=("_x", "_DISC"))
    
    if "CURSO_x" in df.columns: df.rename(columns={"CURSO_x": "CURSO"}, inplace=True)
    if "PERGUNTA_y" in df.columns: df.rename(columns={"PERGUNTA_y": "PERGUNTA"}, inplace=True)
    if "PERGUNTA_x" in df.columns: df.drop(columns=["PERGUNTA_x"], inplace=True)
    
    return df

def processar_dados_cursos():
    df = df_curso_resp.merge(df_curso_q, on=["ID_PERGUNTA", "ID_QUESTIONARIO"], how="left")
    df = df.merge(df_curso_info, on="COD_CURSO", how="left")
    
    if "CURSO_x" in df.columns: df.rename(columns={"CURSO_x": "CURSO"}, inplace=True)
    if "SETOR_CURSO_x" in df.columns: df.rename(columns={"SETOR_CURSO_x": "SETOR_CURSO"}, inplace=True)
    if "PERGUNTA_y" in df.columns: df.rename(columns={"PERGUNTA_y": "PERGUNTA"}, inplace=True)
    if "PERGUNTA_x" in df.columns: df.drop(columns=["PERGUNTA_x"], inplace=True)
    
    return df

def processar_dados_ead():
    df = df_ead_resp.merge(df_ead_q, on=["ID_PERGUNTA", "ID_QUESTIONARIO"], how="left")
    df = df.merge(df_ead_disc, on=["COD_DISCIPLINA", "COD_CURSO"], how="left", suffixes=("_x", "_DISC"))
    
    if "CURSO_x" in df.columns: df.rename(columns={"CURSO_x": "CURSO"}, inplace=True)
    if "PERGUNTA_y" in df.columns: df.rename(columns={"PERGUNTA_y": "PERGUNTA"}, inplace=True)
    if "PERGUNTA_x" in df.columns: df.drop(columns=["PERGUNTA_x"], inplace=True)
    
    return df

def processar_dados_institucional():
    df = df_inst_resp.merge(df_inst_q, on=["ID_PERGUNTA", "ID_QUESTIONARIO"], how="left")
    df = df.merge(df_inst_unidades, on="SIGLA_LOTACAO", how="left")
    
    if "PERGUNTA_y" in df.columns: df.rename(columns={"PERGUNTA_y": "PERGUNTA"}, inplace=True)
    if "PERGUNTA_x" in df.columns: df.drop(columns=["PERGUNTA_x"], inplace=True)
    
    # Verificar se a coluna LOTACAO existe, caso contrário usar SIGLA_LOTACAO
    if "LOTACAO" not in df.columns and "SIGLA_LOTACAO" in df.columns:
        df["LOTACAO"] = df["SIGLA_LOTACAO"]
    
    return df

# =============================================================
# INICIALIZAR DADOS
# =============================================================

df_presencial = processar_dados_presenciais()
df_cursos = processar_dados_cursos()
df_ead = processar_dados_ead()
df_institucional = processar_dados_institucional()

ordem_likert = ["Discordo", "Desconheço", "Concordo"]

app = Dash(__name__)

# =============================================================
# FUNÇÕES AUXILIARES PARA GRÁFICOS
# =============================================================

def criar_grafico_likert(dff, perguntas_selecionadas=None, mapeamento_perguntas=None):
    if perguntas_selecionadas and mapeamento_perguntas:
        perguntas_completas = [mapeamento_perguntas[p] for p in perguntas_selecionadas]
        dff = dff[dff["PERGUNTA"].isin(perguntas_completas)]
    
    if dff.empty:
        return px.bar(title="Selecione pelo menos uma pergunta para visualizar")
    
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

    fig = px.bar(
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
    
    fig.update_layout(
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
            font=dict(size=18, family="Arial")
        ),
        font=dict(size=12),
        height=500
    )
    
    fig.update_xaxes(ticksuffix="%", range=[0, 100])
    fig.update_yaxes(title=None, categoryorder="total ascending")
    
    totais = likert_df.groupby("PERGUNTA")["Quantidade"].sum().reset_index()
    for idx, row in totais.iterrows():
        fig.add_annotation(
            x=105, y=row["PERGUNTA"], text=f"n={row['Quantidade']}",
            showarrow=False, xanchor="left", font=dict(size=10, color="gray")
        )

    return fig

def criar_grafico_satisfacao_geral(dff):
    if dff.empty:
        return px.pie(title="Nenhum dado para exibir")
    
    valores = {"Discordo": 1, "Desconheço": 2, "Concordo": 3}
    dff["valor_num"] = dff["RESPOSTA"].map(valores)
    
    distribuição_respostas = dff["RESPOSTA"].value_counts(normalize=True) * 100
    
    fig = px.pie(
        values=distribuição_respostas.values,
        names=distribuição_respostas.index,
        title="Distribuição Geral de Respostas",
        color_discrete_map={
            "Concordo": "#2E8B57",
            "Desconheço": "#FFA500", 
            "Discordo": "#DC143C"
        }
    )
    
    fig.update_layout(
        title=dict(x=0.5, xanchor="center"),
        height=400
    )
    
    return fig

def criar_grafico_top_cursos(dff):
    if dff.empty:
        return px.bar(title="Nenhum dado para exibir")
    
    valores = {"Discordo": 1, "Desconheço": 2, "Concordo": 3}
    dff["valor_num"] = dff["RESPOSTA"].map(valores)
    
    media_curso = dff.groupby("CURSO")["valor_num"].mean().reset_index()
    media_curso = media_curso.nlargest(15, "valor_num")
    
    max_pontuacao = media_curso["valor_num"].max()
    titulo = f"Top 15 Cursos com Melhor Avaliação (Pontuação: 1-{max_pontuacao:.2f})"
    
    fig = px.bar(
        media_curso,
        x="valor_num",
        y="CURSO",
        title=titulo,
        labels={"valor_num": "Pontuação Média", "CURSO": "Curso"},
        orientation='h',
        color="valor_num",
        color_continuous_scale="Viridis",
        range_color=[1, 3]
    )
    
    fig.update_layout(
        title=dict(x=0.5, xanchor="center"),
        xaxis=dict(range=[1, 3]),
        height=500,
        coloraxis_showscale=False
    )
    
    return fig

def criar_grafico_treemap_setor(dff):
    if dff.empty:
        return px.treemap(title="Nenhum dado para exibir")
    
    valores = {"Discordo": 1, "Desconheço": 2, "Concordo": 3}
    dff["valor_num"] = dff["RESPOSTA"].map(valores)
    
    setor_stats = dff.groupby("SETOR_CURSO").agg({
        "valor_num": "mean",
        "RESPOSTA": "count"
    }).reset_index()
    setor_stats.rename(columns={"RESPOSTA": "Total_Respostas"}, inplace=True)
    
    setor_stats = setor_stats.nlargest(10, "Total_Respostas")
    
    if len(setor_stats) > 10:
        outros_total = setor_stats.iloc[10:]["Total_Respostas"].sum()
        outros_media = setor_stats.iloc[10:]["valor_num"].mean()
        
        top_10 = setor_stats.head(10).copy()
        outros_row = pd.DataFrame({
            "SETOR_CURSO": ["Outros"],
            "valor_num": [outros_media],
            "Total_Respostas": [outros_total]
        })
        
        setor_stats = pd.concat([top_10, outros_row], ignore_index=True)
    
    setor_stats['label_completo'] = setor_stats.apply(
        lambda x: f"{x['SETOR_CURSO']}<br>Respostas: {x['Total_Respostas']}", 
        axis=1
    )
    
    fig = px.treemap(
        setor_stats,
        path=["label_completo"],
        values="Total_Respostas",
        color="valor_num",
        color_continuous_scale="RdYlGn",
        title="Top 10 Setores por Volume de Respostas",
        range_color=[1, 3]
    )
    
    fig.update_layout(
        title=dict(x=0.5, xanchor="center"),
        height=600,
        font=dict(size=14),
        margin=dict(t=50, l=25, r=25, b=25)
    )
    
    fig.update_coloraxes(showscale=False)
    fig.update_traces(
        textfont=dict(size=16, family="Arial"),
        hovertemplate='<b>%{label}</b><br>Total Respostas: %{value}<br>Pontuação Média: %{color:.2f}<extra></extra>'
    )
    
    return fig

def criar_grafico_treemap_departamento(dff):
    if dff.empty:
        return px.treemap(title="Nenhum dado para exibir")
    
    valores = {"Discordo": 1, "Desconheço": 2, "Concordo": 3}
    dff["valor_num"] = dff["RESPOSTA"].map(valores)
    
    depto_stats = dff.groupby("DEPARTAMENTO").agg({
        "valor_num": "mean",
        "RESPOSTA": "count"
    }).reset_index()
    depto_stats.rename(columns={"RESPOSTA": "Total_Respostas"}, inplace=True)
    
    depto_stats = depto_stats.nlargest(10, "Total_Respostas")
    
    if len(depto_stats) > 10:
        outros_total = depto_stats.iloc[10:]["Total_Respostas"].sum()
        outros_media = depto_stats.iloc[10:]["valor_num"].mean()
        
        top_10 = depto_stats.head(10).copy()
        outros_row = pd.DataFrame({
            "DEPARTAMENTO": ["Outros"],
            "valor_num": [outros_media],
            "Total_Respostas": [outros_total]
        })
        
        depto_stats = pd.concat([top_10, outros_row], ignore_index=True)
    
    depto_stats['label_completo'] = depto_stats.apply(
        lambda x: f"{x['DEPARTAMENTO']}<br>Respostas: {x['Total_Respostas']}", 
        axis=1
    )
    
    fig = px.treemap(
        depto_stats,
        path=["label_completo"],
        values="Total_Respostas",
        color="valor_num",
        color_continuous_scale="RdYlGn",
        title="Top 10 Departamentos por Volume de Respostas",
        range_color=[1, 3]
    )
    
    fig.update_layout(
        title=dict(x=0.5, xanchor="center"),
        height=600,
        font=dict(size=14),
        margin=dict(t=50, l=25, r=25, b=25)
    )
    
    fig.update_coloraxes(showscale=False)
    fig.update_traces(
        textfont=dict(size=16, family="Arial"),
        hovertemplate='<b>%{label}</b><br>Total Respostas: %{value}<br>Pontuação Média: %{color:.2f}<extra></extra>'
    )
    
    return fig

# =============================================================
# NOVAS FUNÇÕES PARA EAD E INSTITUCIONAL
# =============================================================

def criar_grafico_treemap_disciplinas_ead(dff):
    if dff.empty:
        return px.treemap(title="Nenhum dado para exibir")
    
    valores = {"Discordo": 1, "Desconheço": 2, "Concordo": 3}
    dff["valor_num"] = dff["RESPOSTA"].map(valores)
    
    # Usar NOME_DISCIPLINA para o treemap
    disciplina_stats = dff.groupby("NOME_DISCIPLINA").agg({
        "valor_num": "mean",
        "RESPOSTA": "count"
    }).reset_index()
    disciplina_stats.rename(columns={"RESPOSTA": "Total_Respostas"}, inplace=True)
    
    disciplina_stats = disciplina_stats.nlargest(10, "Total_Respostas")
    
    if len(disciplina_stats) > 10:
        outros_total = disciplina_stats.iloc[10:]["Total_Respostas"].sum()
        outros_media = disciplina_stats.iloc[10:]["valor_num"].mean()
        
        top_10 = disciplina_stats.head(10).copy()
        outros_row = pd.DataFrame({
            "NOME_DISCIPLINA": ["Outros"],
            "valor_num": [outros_media],
            "Total_Respostas": [outros_total]
        })
        
        disciplina_stats = pd.concat([top_10, outros_row], ignore_index=True)
    
    disciplina_stats['label_completo'] = disciplina_stats.apply(
        lambda x: f"{x['NOME_DISCIPLINA']}<br>Respostas: {x['Total_Respostas']}", 
        axis=1
    )
    
    fig = px.treemap(
        disciplina_stats,
        path=["label_completo"],
        values="Total_Respostas",
        color="valor_num",
        color_continuous_scale="RdYlGn",
        title="Top 10 Disciplinas EAD por Volume de Respostas",
        range_color=[1, 3]
    )
    
    fig.update_layout(
        title=dict(x=0.5, xanchor="center"),
        height=600,
        font=dict(size=14),
        margin=dict(t=50, l=25, r=25, b=25)
    )
    
    fig.update_coloraxes(showscale=False)
    fig.update_traces(
        textfont=dict(size=16, family="Arial"),
        hovertemplate='<b>%{label}</b><br>Total Respostas: %{value}<br>Pontuação Média: %{color:.2f}<extra></extra>'
    )
    
    return fig

def criar_grafico_evolucao_ead(dff):
    if dff.empty:
        return px.line(title="Nenhum dado para exibir")
    
    valores = {"Discordo": 1, "Desconheço": 2, "Concordo": 3}
    dff["valor_num"] = dff["RESPOSTA"].map(valores)
    
    evolucao = dff.groupby("ID_PESQUISA")["valor_num"].mean().reset_index()
    
    fig = px.line(
        evolucao,
        x="ID_PESQUISA",
        y="valor_num",
        title="Evolução Temporal da Avaliação EAD",
        labels={"ID_PESQUISA": "ID da Pesquisa", "valor_num": "Pontuação Média"},
        markers=True
    )
    
    fig.update_layout(
        title=dict(x=0.5, xanchor="center"),
        height=400,
        xaxis=dict(range=[evolucao["ID_PESQUISA"].min(), evolucao["ID_PESQUISA"].max()])
    )
    
    return fig

def criar_grafico_top_unidades_institucional(dff):
    if dff.empty:
        return px.bar(title="Nenhum dado para exibir")
    
    valores = {"Discordo": 1, "Desconheço": 2, "Concordo": 3}
    dff["valor_num"] = dff["RESPOSTA"].map(valores)
    
    # Usar LOTACAO ou SIGLA_LOTACAO dependendo da disponibilidade
    coluna_unidade = "LOTACAO" if "LOTACAO" in dff.columns else "SIGLA_LOTACAO"
    
    media_unidade = dff.groupby(coluna_unidade)["valor_num"].mean().reset_index()
    media_unidade = media_unidade.nlargest(15, "valor_num")
    
    max_pontuacao = media_unidade["valor_num"].max()
    titulo = f"Top 15 Unidades com Melhor Avaliação (Pontuação: 1-{max_pontuacao:.2f})"
    
    fig = px.bar(
        media_unidade,
        x="valor_num",
        y=coluna_unidade,
        title=titulo,
        labels={"valor_num": "Pontuação Média", coluna_unidade: "Unidade"},
        orientation='h',
        color="valor_num",
        color_continuous_scale="Viridis",
        range_color=[1, 3]
    )
    
    fig.update_layout(
        title=dict(x=0.5, xanchor="center"),
        xaxis=dict(range=[1, 3]),
        height=500,
        coloraxis_showscale=False
    )
    
    return fig

def criar_grafico_treemap_unidades_institucional(dff):
    if dff.empty:
        return px.treemap(title="Nenhum dado para exibir")
    
    valores = {"Discordo": 1, "Desconheço": 2, "Concordo": 3}
    dff["valor_num"] = dff["RESPOSTA"].map(valores)
    
    # Usar LOTACAO ou SIGLA_LOTACAO dependendo da disponibilidade
    coluna_unidade = "LOTACAO" if "LOTACAO" in dff.columns else "SIGLA_LOTACAO"
    
    unidade_stats = dff.groupby(coluna_unidade).agg({
        "valor_num": "mean",
        "RESPOSTA": "count"
    }).reset_index()
    unidade_stats.rename(columns={"RESPOSTA": "Total_Respostas"}, inplace=True)
    
    unidade_stats = unidade_stats.nlargest(10, "Total_Respostas")
    
    if len(unidade_stats) > 10:
        outros_total = unidade_stats.iloc[10:]["Total_Respostas"].sum()
        outros_media = unidade_stats.iloc[10:]["valor_num"].mean()
        
        top_10 = unidade_stats.head(10).copy()
        outros_row = pd.DataFrame({
            coluna_unidade: ["Outros"],
            "valor_num": [outros_media],
            "Total_Respostas": [outros_total]
        })
        
        unidade_stats = pd.concat([top_10, outros_row], ignore_index=True)
    
    unidade_stats['label_completo'] = unidade_stats.apply(
        lambda x: f"{x[coluna_unidade]}<br>Respostas: {x['Total_Respostas']}", 
        axis=1
    )
    
    fig = px.treemap(
        unidade_stats,
        path=["label_completo"],
        values="Total_Respostas",
        color="valor_num",
        color_continuous_scale="RdYlGn",
        title="Top 10 Unidades por Volume de Respostas",
        range_color=[1, 3]
    )
    
    fig.update_layout(
        title=dict(x=0.5, xanchor="center"),
        height=600,
        font=dict(size=14),
        margin=dict(t=50, l=25, r=25, b=25)
    )
    
    fig.update_coloraxes(showscale=False)
    fig.update_traces(
        textfont=dict(size=16, family="Arial"),
        hovertemplate='<b>%{label}</b><br>Total Respostas: %{value}<br>Pontuação Média: %{color:.2f}<extra></extra>'
    )
    
    return fig

# =============================================================
# LAYOUT COM ABAS
# =============================================================

app.layout = html.Div([
    html.H1("Dashboard de Avaliações UFPR", style={"marginBottom": "20px"}),
    
    dcc.Tabs(id="tabs-principais", value='tab-cursos', children=[
        dcc.Tab(label='Cursos', value='tab-cursos'),
        dcc.Tab(label='Disciplinas Presenciais', value='tab-presencial'),
        dcc.Tab(label='Disciplinas EAD', value='tab-ead'),
        dcc.Tab(label='Institucional', value='tab-institucional'),
    ]),
    
    html.Div(id="conteudo-tab")
])

# =============================================================
# LAYOUTS PARA CADA ABA
# =============================================================

def criar_layout_presencial():
    perguntas_unicas = sorted(df_presencial["PERGUNTA"].dropna().unique())
    mapeamento_perguntas = {}
    opcoes_perguntas = []

    for i, pergunta in enumerate(perguntas_unicas, 1):
        palavras = pergunta.split()[:6]
        label_resumido = " ".join(palavras) + "..." if len(palavras) == 6 else pergunta
        label_final = f"P{i}: {label_resumido}"
        mapeamento_perguntas[label_final] = pergunta
        opcoes_perguntas.append({"label": label_final, "value": label_final})

    return html.Div([
        html.H3("Disciplinas Presenciais"),
        
        html.Div([
            html.Div([
                html.Label("ID da Pesquisa"),
                dcc.Dropdown(
                    id="filtro-id-presencial",
                    options=[{"label": str(id_pesquisa), "value": id_pesquisa} 
                            for id_pesquisa in sorted(df_presencial["ID_PESQUISA"].dropna().unique())],
                    multi=True,
                    placeholder="Selecione o(s) ID(s)"
                ),
            ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

            html.Div([
                html.Label("Curso"),
                dcc.Dropdown(
                    id="filtro-curso-presencial",
                    options=[{"label": c, "value": c} for c in sorted(df_presencial["CURSO"].dropna().unique())],
                    multi=True,
                    placeholder="Selecione o(s) curso(s)"
                ),
            ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

            html.Div([
                html.Label("Pergunta"),
                dcc.Dropdown(
                    id="filtro-pergunta-presencial",
                    options=opcoes_perguntas,
                    multi=True,
                    placeholder="Selecione a(s) pergunta(s)",
                    style={'minWidth': '450px', 'fontSize': '12px'}
                ),
            ], style={"width": "40%", "display": "inline-block", "padding": "10px"}),
        ]),

        html.Br(), html.Br(),

        dcc.Graph(id="grafico-likert-presencial"),
        
        html.Div([
            html.Div([
                dcc.Graph(id="grafico-satisfacao-presencial"),
            ], style={"width": "50%", "display": "inline-block"}),
            
            html.Div([
                dcc.Graph(id="grafico-treemap-departamentos"),
            ], style={"width": "50%", "display": "inline-block"}),
        ])
    ])

def criar_layout_cursos():
    return html.Div([
        html.H3("Avaliação de Cursos"),
        
        html.Div([
            html.Div([
                html.Label("ID da Pesquisa"),
                dcc.Dropdown(
                    id="filtro-id-cursos",
                    options=[{"label": str(id_pesquisa), "value": id_pesquisa} 
                            for id_pesquisa in sorted(df_cursos["ID_PESQUISA"].dropna().unique())],
                    multi=True,
                    placeholder="Selecione o(s) ID(s)"
                ),
            ], style={"width": "50%", "display": "inline-block", "padding": "10px"}),

            html.Div([
                html.Label("Curso"),
                dcc.Dropdown(
                    id="filtro-curso-cursos",
                    options=[{"label": c, "value": c} for c in sorted(df_cursos["CURSO"].dropna().unique())],
                    multi=True,
                    placeholder="Selecione o(s) curso(s)"
                ),
            ], style={"width": "50%", "display": "inline-block", "padding": "10px"}),
        ]),

        html.Br(), html.Br(),

        html.Div([
            html.Div([
                dcc.Graph(id="grafico-satisfacao-cursos"),
            ], style={"width": "50%", "display": "inline-block"}),
            
            html.Div([
                dcc.Graph(id="grafico-top-cursos"),
            ], style={"width": "50%", "display": "inline-block"}),
        ]),
        
        html.Div([
            html.Div([
                dcc.Graph(id="grafico-treemap-setores"),
            ], style={"width": "100%", "display": "inline-block"}),
        ])
    ])

def criar_layout_ead():
    perguntas_unicas = sorted(df_ead["PERGUNTA"].dropna().unique())
    mapeamento_perguntas = {}
    opcoes_perguntas = []

    for i, pergunta in enumerate(perguntas_unicas, 1):
        palavras = pergunta.split()[:6]
        label_resumido = " ".join(palavras) + "..." if len(palavras) == 6 else pergunta
        label_final = f"P{i}: {label_resumido}"
        mapeamento_perguntas[label_final] = pergunta
        opcoes_perguntas.append({"label": label_final, "value": label_final})

    return html.Div([
        html.H3("Disciplinas EAD"),
        
        html.Div([
            html.Div([
                html.Label("ID da Pesquisa"),
                dcc.Dropdown(
                    id="filtro-id-ead",
                    options=[{"label": str(id_pesquisa), "value": id_pesquisa} 
                            for id_pesquisa in sorted(df_ead["ID_PESQUISA"].dropna().unique())],
                    multi=True,
                    placeholder="Selecione o(s) ID(s)"
                ),
            ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

            html.Div([
                html.Label("Programa EAD"),
                dcc.Dropdown(
                    id="filtro-programa-ead",
                    options=[{"label": c, "value": c} for c in sorted(df_ead["CURSO"].dropna().unique())],
                    multi=True,
                    placeholder="Selecione o(s) programa(s)"
                ),
            ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

            html.Div([
                html.Label("Pergunta"),
                dcc.Dropdown(
                    id="filtro-pergunta-ead",
                    options=opcoes_perguntas,
                    multi=True,
                    placeholder="Selecione a(s) pergunta(s)",
                    style={'minWidth': '450px', 'fontSize': '12px'}
                ),
            ], style={"width": "40%", "display": "inline-block", "padding": "10px"}),
        ]),

        html.Br(), html.Br(),

        dcc.Graph(id="grafico-likert-ead"),
        
        html.Div([
            html.Div([
                dcc.Graph(id="grafico-satisfacao-ead"),
            ], style={"width": "50%", "display": "inline-block"}),
            
            html.Div([
                dcc.Graph(id="grafico-treemap-disciplinas-ead"),
            ], style={"width": "50%", "display": "inline-block"}),
        ]),
        
        html.Div([
            html.Div([
                dcc.Graph(id="grafico-evolucao-ead"),
            ], style={"width": "100%", "display": "inline-block"}),
        ])
    ])

def criar_layout_institucional():
    # Usar LOTACAO ou SIGLA_LOTACAO dependendo da disponibilidade
    coluna_unidade = "LOTACAO" if "LOTACAO" in df_institucional.columns else "SIGLA_LOTACAO"
    unidades_unicas = sorted(df_institucional[coluna_unidade].dropna().unique())
    
    return html.Div([
        html.H3("Avaliação Institucional"),
        
        html.Div([
            html.Div([
                html.Label("ID da Pesquisa"),
                dcc.Dropdown(
                    id="filtro-id-institucional",
                    options=[{"label": str(id_pesquisa), "value": id_pesquisa} 
                            for id_pesquisa in sorted(df_institucional["ID_PESQUISA"].dropna().unique())],
                    multi=True,
                    placeholder="Selecione o(s) ID(s)"
                ),
            ], style={"width": "50%", "display": "inline-block", "padding": "10px"}),

            html.Div([
                html.Label("Unidade"),
                dcc.Dropdown(
                    id="filtro-unidade-institucional",
                    options=[{"label": c, "value": c} for c in unidades_unicas],
                    multi=True,
                    placeholder="Selecione a(s) unidade(s)"
                ),
            ], style={"width": "50%", "display": "inline-block", "padding": "10px"}),
        ]),

        html.Br(), html.Br(),

        html.Div([
            html.Div([
                dcc.Graph(id="grafico-satisfacao-institucional"),
            ], style={"width": "50%", "display": "inline-block"}),
            
            html.Div([
                dcc.Graph(id="grafico-top-unidades-institucional"),
            ], style={"width": "50%", "display": "inline-block"}),
        ]),
        
        html.Div([
            html.Div([
                dcc.Graph(id="grafico-treemap-unidades-institucional"),
            ], style={"width": "100%", "display": "inline-block"}),
        ])
    ])

# =============================================================
# CALLBACKS
# =============================================================

@app.callback(
    Output("conteudo-tab", "children"),
    Input("tabs-principais", "value")
)
def render_conteudo(tab_selecionada):
    if tab_selecionada == 'tab-presencial':
        return criar_layout_presencial()
    elif tab_selecionada == 'tab-cursos':
        return criar_layout_cursos()
    elif tab_selecionada == 'tab-ead':
        return criar_layout_ead()
    elif tab_selecionada == 'tab-institucional':
        return criar_layout_institucional()

@app.callback(
    Output("grafico-satisfacao-cursos", "figure"),
    Output("grafico-top-cursos", "figure"),
    Output("grafico-treemap-setores", "figure"),
    Input("filtro-id-cursos", "value"),
    Input("filtro-curso-cursos", "value"),
)
def atualizar_graficos_cursos(ids, cursos):
    dff = df_cursos.copy()
    
    if ids: 
        dff = dff[dff["ID_PESQUISA"].isin(ids)]
    if cursos: 
        dff = dff[dff["CURSO"].isin(cursos)]
    
    fig_satisfacao = criar_grafico_satisfacao_geral(dff)
    fig_top_cursos = criar_grafico_top_cursos(dff)
    fig_treemap_setores = criar_grafico_treemap_setor(dff)
    
    return fig_satisfacao, fig_top_cursos, fig_treemap_setores

@app.callback(
    Output("grafico-likert-presencial", "figure"),
    Output("grafico-satisfacao-presencial", "figure"),
    Output("grafico-treemap-departamentos", "figure"),
    Input("filtro-id-presencial", "value"),
    Input("filtro-curso-presencial", "value"),
    Input("filtro-pergunta-presencial", "value"),
)
def atualizar_graficos_presencial(ids, cursos, perguntas_selecionadas):
    dff = df_presencial.copy()
    
    if ids: dff = dff[dff["ID_PESQUISA"].isin(ids)]
    if cursos: dff = dff[dff["CURSO"].isin(cursos)]
    
    perguntas_unicas = sorted(df_presencial["PERGUNTA"].dropna().unique())
    mapeamento_perguntas = {}
    for i, pergunta in enumerate(perguntas_unicas, 1):
        palavras = pergunta.split()[:6]
        label_resumido = " ".join(palavras) + "..." if len(palavras) == 6 else pergunta
        label_final = f"P{i}: {label_resumido}"
        mapeamento_perguntas[label_final] = pergunta
    
    fig_likert = criar_grafico_likert(dff, perguntas_selecionadas, mapeamento_perguntas)
    fig_satisfacao = criar_grafico_satisfacao_geral(dff)
    fig_treemap = criar_grafico_treemap_departamento(dff)
    
    return fig_likert, fig_satisfacao, fig_treemap

@app.callback(
    Output("grafico-likert-ead", "figure"),
    Output("grafico-satisfacao-ead", "figure"),
    Output("grafico-treemap-disciplinas-ead", "figure"),
    Output("grafico-evolucao-ead", "figure"),
    Input("filtro-id-ead", "value"),
    Input("filtro-programa-ead", "value"),
    Input("filtro-pergunta-ead", "value"),
)
def atualizar_graficos_ead(ids, programas, perguntas_selecionadas):
    dff = df_ead.copy()
    
    if ids: 
        dff = dff[dff["ID_PESQUISA"].isin(ids)]
    if programas: 
        dff = dff[dff["CURSO"].isin(programas)]
    
    perguntas_unicas = sorted(df_ead["PERGUNTA"].dropna().unique())
    mapeamento_perguntas = {}
    for i, pergunta in enumerate(perguntas_unicas, 1):
        palavras = pergunta.split()[:6]
        label_resumido = " ".join(palavras) + "..." if len(palavras) == 6 else pergunta
        label_final = f"P{i}: {label_resumido}"
        mapeamento_perguntas[label_final] = pergunta
    
    fig_likert = criar_grafico_likert(dff, perguntas_selecionadas, mapeamento_perguntas)
    fig_satisfacao = criar_grafico_satisfacao_geral(dff)
    fig_treemap = criar_grafico_treemap_disciplinas_ead(dff)
    fig_evolucao = criar_grafico_evolucao_ead(dff)
    
    return fig_likert, fig_satisfacao, fig_treemap, fig_evolucao

@app.callback(
    Output("grafico-satisfacao-institucional", "figure"),
    Output("grafico-top-unidades-institucional", "figure"),
    Output("grafico-treemap-unidades-institucional", "figure"),
    Input("filtro-id-institucional", "value"),
    Input("filtro-unidade-institucional", "value"),
)
def atualizar_graficos_institucional(ids, unidades):
    dff = df_institucional.copy()
    
    if ids: 
        dff = dff[dff["ID_PESQUISA"].isin(ids)]
    if unidades: 
        # Usar LOTACAO ou SIGLA_LOTACAO dependendo da disponibilidade
        coluna_unidade = "LOTACAO" if "LOTACAO" in dff.columns else "SIGLA_LOTACAO"
        dff = dff[dff[coluna_unidade].isin(unidades)]
    
    fig_satisfacao = criar_grafico_satisfacao_geral(dff)
    fig_top_unidades = criar_grafico_top_unidades_institucional(dff)
    fig_treemap_unidades = criar_grafico_treemap_unidades_institucional(dff)
    
    return fig_satisfacao, fig_top_unidades, fig_treemap_unidades

if __name__ == "__main__":
    app.run(debug=True)