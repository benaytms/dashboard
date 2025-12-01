import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import dash
from dash import Dash, html, dcc, Input, Output
import logging
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
clean_data_path = os.path.join(project_root, 'clean_data')

df_pres_resp = pd.read_csv(os.path.join(clean_data_path, "presenciais_dadosavdisciplinas.csv"))
df_pres_q = pd.read_csv(os.path.join(clean_data_path, "presenciais_perguntas.csv"))
df_pres_disc = pd.read_csv(os.path.join(clean_data_path, "presenciais_disciplinas.csv"))

df_curso_resp = pd.read_csv(os.path.join(clean_data_path, "cursos_dadosavcursos.csv"))
df_curso_q = pd.read_csv(os.path.join(clean_data_path, "cursos_perguntas.csv"))
df_curso_info = pd.read_csv(os.path.join(clean_data_path, "cursos_curso.csv"))

df_ead_resp = pd.read_csv(os.path.join(clean_data_path, "ead_pesq423_discip.csv"))
df_ead_q = pd.read_csv(os.path.join(clean_data_path, "ead_perguntas.csv"))
df_ead_disc = pd.read_csv(os.path.join(clean_data_path, "ead_disciplinas.csv"))

df_inst_resp = pd.read_csv(os.path.join(clean_data_path, "institucional_pesquisa_442.csv"))
df_inst_q = pd.read_csv(os.path.join(clean_data_path, "institucional_perguntas.csv"))
df_inst_unidades = pd.read_csv(os.path.join(clean_data_path, "institucional_unidades.csv"))

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
    
    if "NOME_DISCIPLINA_DISC" in df.columns:
        df.rename(columns={"NOME_DISCIPLINA_DISC": "NOME_DISCIPLINA"}, inplace=True)
    
    return df

def processar_dados_institucional():
    df = df_inst_resp.merge(df_inst_q, on=["ID_PERGUNTA", "ID_QUESTIONARIO"], how="left")
    df = df.merge(df_inst_unidades, on="SIGLA_LOTACAO", how="left")
    
    if "PERGUNTA_y" in df.columns: df.rename(columns={"PERGUNTA_y": "PERGUNTA"}, inplace=True)
    if "PERGUNTA_x" in df.columns: df.drop(columns=["PERGUNTA_x"], inplace=True)
    
    if "LOTACAO_x" in df.columns:
        df.rename(columns={"LOTACAO_x": "LOTACAO"}, inplace=True)
        
        colunas_para_remover = ["LOTACAO_y", "SIGLA_LOTACAO"]
        for col in colunas_para_remover:
            if col in df.columns:
                df.drop(columns=[col], inplace=True)
    
    return df

df_presencial = processar_dados_presenciais()
df_cursos = processar_dados_cursos()
df_ead = processar_dados_ead()
df_institucional = processar_dados_institucional()

ordem_likert = ["Discordo", "Desconheço", "Concordo"]

logging.getLogger('werkzeug').disabled = True
logging.getLogger('dash').disabled = True

class DevNull:
    def write(self, msg):
        pass
    def flush(self):
        pass

sys.stderr = DevNull()

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server 

cores_ufpr = {
    'verde_principal': '#008450',
    'verde_secundario': '#4CAF50',
    'azul': '#0056A3',
    'amarelo': '#FFD700',
    'laranja': '#FF8C00',
    'vermelho': '#DC143C',
    'cinza_claro': '#F8F9FA',
    'cinza_medio': '#E9ECEF',
    'cinza_escuro': '#6C757D',
    'branco': '#FFFFFF'
}

estilos = {
    'container_principal': {
        'backgroundColor': cores_ufpr['cinza_claro'],
        'minHeight': '100vh',
        'padding': '20px',
        'fontFamily': 'Segoe UI, Arial, sans-serif'
    },
    'header': {
        'backgroundColor': cores_ufpr['verde_principal'],
        'color': cores_ufpr['branco'],
        'padding': '25px',
        'borderRadius': '12px',
        'marginBottom': '25px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.1)',
        'textAlign': 'center'
    },
    'titulo_principal': {
        'fontSize': '2.5rem',
        'fontWeight': '700',
        'marginBottom': '8px',
        'color': cores_ufpr['branco']
    },
    'subtitulo': {
        'fontSize': '1.1rem',
        'fontWeight': '300',
        'color': cores_ufpr['branco'],
        'opacity': '0.9'
    },
    'tabs_container': {
        'backgroundColor': cores_ufpr['branco'],
        'borderRadius': '12px',
        'padding': '0',
        'marginBottom': '25px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'
    },
    'tab': {
        'backgroundColor': cores_ufpr['cinza_medio'],
        'color': cores_ufpr['cinza_escuro'],
        'padding': '15px 25px',
        'border': 'none',
        'fontWeight': '600',
        'fontSize': '14px'
    },
    'tab_selecionada': {
        'backgroundColor': cores_ufpr['verde_principal'],
        'color': cores_ufpr['branco'],
        'border': 'none',
        'fontWeight': '600'
    },
    'card': {
        'backgroundColor': cores_ufpr['branco'],
        'borderRadius': '12px',
        'padding': '20px',
        'marginBottom': '20px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.06)',
        'border': f"1px solid {cores_ufpr['cinza_medio']}"
    },
    'filtros_container': {
        'backgroundColor': cores_ufpr['branco'],
        'borderRadius': '12px',
        'padding': '20px',
        'marginBottom': '25px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'
    },
    'dropdown': {
        'backgroundColor': cores_ufpr['branco'],
        'border': f"1px solid {cores_ufpr['cinza_medio']}",
        'borderRadius': '8px'
    },
    'grafico_container': {
        'backgroundColor': cores_ufpr['branco'],
        'borderRadius': '12px',
        'padding': '15px',
        'marginBottom': '20px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.06)',
        'border': f"1px solid {cores_ufpr['cinza_medio']}"
    },
    'kpi_card': {
        'backgroundColor': cores_ufpr['branco'],
        'borderRadius': '12px',
        'padding': '20px',
        'textAlign': 'center',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.06)',
        'border': f"1px solid {cores_ufpr['cinza_medio']}"
    },
    'grafico_principal': {
        'backgroundColor': cores_ufpr['branco'],
        'borderRadius': '12px',
        'padding': '15px',
        'marginBottom': '20px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.06)',
        'border': f"1px solid {cores_ufpr['cinza_medio']}",
        'width': '100%'
    },
    'grafico_duplo': {
        'backgroundColor': cores_ufpr['branco'],
        'borderRadius': '12px',
        'padding': '15px',
        'marginBottom': '20px',
        'boxShadow': '0 2px8px rgba(0,0,0,0.06)',
        'border': f"1px solid {cores_ufpr['cinza_medio']}",
        'width': '48%',
        'display': 'inline-block'
    },
    'treemap_container': {
        'backgroundColor': cores_ufpr['branco'],
        'borderRadius': '12px',
        'padding': '15px',
        'marginBottom': '20px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.06)',
        'border': f"1px solid {cores_ufpr['cinza_medio']}",
        'width': '100%'
    }
}

def criar_grafico_likert(dff, perguntas_selecionadas=None, mapeamento_perguntas=None):
    if perguntas_selecionadas and mapeamento_perguntas:
        perguntas_completas = [mapeamento_perguntas[p] for p in perguntas_selecionadas]
        dff = dff[dff["PERGUNTA"].isin(perguntas_completas)]
    
    if dff.empty:
        fig = go.Figure()
        fig.add_annotation(text="Selecione pelo menos uma pergunta para visualizar", 
                          xref="paper", yref="paper", x=0.5, y=0.5, xanchor='center', yanchor='middle',
                          showarrow=False, font=dict(size=16))
        fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
        return fig
    
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
            "Concordo": cores_ufpr['verde_principal'],
            "Desconheço": cores_ufpr['amarelo'],
            "Discordo": cores_ufpr['vermelho']
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
            x=1,
            bgcolor='rgba(255,255,255,0.8)'
        ),
        title=dict(
            text="Distribuição de Respostas por Pergunta",
            x=0.5,
            xanchor="center",
            font=dict(size=18, family="Arial", color=cores_ufpr['cinza_escuro'])
        ),
        font=dict(size=12, family="Segoe UI"),
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    fig.update_xaxes(ticksuffix="%", range=[0, 100], gridcolor=cores_ufpr['cinza_medio'])
    fig.update_yaxes(title=None, categoryorder="total ascending", gridcolor=cores_ufpr['cinza_medio'])
    
    totais = likert_df.groupby("PERGUNTA")["Quantidade"].sum().reset_index()
    for idx, row in totais.iterrows():
        fig.add_annotation(
            x=105, y=row["PERGUNTA"], text=f"n={row['Quantidade']}",
            showarrow=False, xanchor="left", font=dict(size=10, color=cores_ufpr['cinza_escuro'])
        )

    return fig

def criar_grafico_satisfacao_geral(dff):
    if dff.empty:
        fig = go.Figure()
        fig.add_annotation(text="Nenhum dado para exibir", 
                          xref="paper", yref="paper", x=0.5, y=0.5, xanchor='center', yanchor='middle',
                          showarrow=False, font=dict(size=16))
        fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
        return fig
    
    valores = {"Discordo": 1, "Desconheço": 2, "Concordo": 3}
    dff["valor_num"] = dff["RESPOSTA"].map(valores)
    
    distribuição_respostas = dff["RESPOSTA"].value_counts(normalize=True) * 100
    
    fig = px.pie(
        values=distribuição_respostas.values,
        names=distribuição_respostas.index,
        title="Distribuição Geral de Respostas",
        color_discrete_map={
            "Concordo": cores_ufpr['verde_principal'],
            "Desconheço": cores_ufpr['amarelo'],
            "Discordo": cores_ufpr['vermelho']
        }
    )
    
    fig.update_layout(
        title=dict(x=0.5, xanchor="center", font=dict(color=cores_ufpr['cinza_escuro'])),
        height=400,
        paper_bgcolor='white',
        plot_bgcolor='white',
        legend=dict(bgcolor='rgba(255,255,255,0.8)')
    )
    
    fig.update_traces(
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Percentual: %{percent}<extra></extra>',
        marker=dict(line=dict(color='white', width=2))
    )
    
    return fig

def criar_grafico_top_cursos(dff):
    if dff.empty:
        fig = go.Figure()
        fig.add_annotation(text="Nenhum dado para exibir", 
                          xref="paper", yref="paper", x=0.5, y=0.5, xanchor='center', yanchor='middle',
                          showarrow=False, font=dict(size=16))
        fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
        return fig
    
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
        title=dict(x=0.5, xanchor="center", font=dict(color=cores_ufpr['cinza_escuro'])),
        xaxis=dict(range=[1, 3], gridcolor=cores_ufpr['cinza_medio']),
        height=500,
        coloraxis_showscale=False,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig

def criar_grafico_treemap_setor(dff):
    if dff.empty:
        fig = go.Figure()
        fig.add_annotation(text="Nenhum dado para exibir", 
                          xref="paper", yref="paper", x=0.5, y=0.5, xanchor='center', yanchor='middle',
                          showarrow=False, font=dict(size=16))
        fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
        return fig
    
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
        lambda x: f"{x['SETOR_CURSO'][:25]}...<br>({x['Total_Respostas']} resp)", 
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
        title=dict(x=0.5, xanchor="center", font=dict(color=cores_ufpr['cinza_escuro'])),
        height=600,
        font=dict(size=14, family="Segoe UI"),
        margin=dict(t=50, l=25, r=25, b=25),
        paper_bgcolor='white'
    )
    
    fig.update_coloraxes(showscale=False)
    fig.update_traces(
        textfont=dict(size=16, family="Segoe UI"),
        hovertemplate='<b>%{label}</b><br>Total Respostas: %{value}<br>Pontuação Média: %{color:.2f}<extra></extra>'
    )
    
    return fig

def criar_grafico_treemap_departamento(dff):
    if dff.empty:
        fig = go.Figure()
        fig.add_annotation(text="Nenhum dado para exibir", 
                          xref="paper", yref="paper", x=0.5, y=0.5, xanchor='center', yanchor='middle',
                          showarrow=False, font=dict(size=16))
        fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
        return fig
    
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
        lambda x: f"{x['DEPARTAMENTO'][:25]}...<br>({x['Total_Respostas']} resp)", 
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
        title=dict(x=0.5, xanchor="center", font=dict(color=cores_ufpr['cinza_escuro'])),
        height=600,
        font=dict(size=14, family="Segoe UI"),
        margin=dict(t=50, l=25, r=25, b=25),
        paper_bgcolor='white'
    )
    
    fig.update_coloraxes(showscale=False)
    fig.update_traces(
        textfont=dict(size=16, family="Segoe UI"),
        hovertemplate='<b>%{label}</b><br>Total Respostas: %{value}<br>Pontuação Média: %{color:.2f}<extra></extra>'
    )
    
    return fig

def criar_grafico_distribuicao_cursos(dff):
    if dff.empty:
        fig = go.Figure()
        fig.add_annotation(text="Nenhum dado para exibir", 
                          xref="paper", yref="paper", x=0.5, y=0.5, xanchor='center', yanchor='middle',
                          showarrow=False, font=dict(size=16))
        fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
        return fig
    
    curso_respostas = dff.groupby(["CURSO", "RESPOSTA"]).size().reset_index(name="Quantidade")
    
    totais_curso = curso_respostas.groupby("CURSO")["Quantidade"].sum().reset_index()
    totais_curso = totais_curso.nlargest(15, "Quantidade")
    
    curso_respostas = curso_respostas[curso_respostas["CURSO"].isin(totais_curso["CURSO"])]
    
    total_por_curso = curso_respostas.groupby("CURSO")["Quantidade"].transform('sum')
    curso_respostas["Percentual"] = (curso_respostas["Quantidade"] / total_por_curso * 100).round(1)
    
    curso_respostas["RESPOSTA"] = pd.Categorical(
        curso_respostas["RESPOSTA"],
        categories=ordem_likert,
        ordered=True
    )
    
    taxa_concordo = (
        curso_respostas[curso_respostas["RESPOSTA"] == "Concordo"]
        .set_index("CURSO")["Percentual"]
        .to_dict()
    )
    
    curso_respostas["ordem_concordo"] = curso_respostas["CURSO"].map(taxa_concordo).fillna(0)
    curso_respostas.sort_values(["ordem_concordo", "CURSO", "RESPOSTA"], 
                               ascending=[False, True, True], inplace=True)

    fig = px.bar(
        curso_respostas,
        x="Percentual",
        y="CURSO",
        color="RESPOSTA",
        barmode="stack",
        title="Distribuição de Respostas por Cursos (Top 15)",
        labels={
            "CURSO": "Curso", 
            "Percentual": "Percentual de Respostas (%)", 
            "RESPOSTA": "Resposta"
        },
        color_discrete_map={
            "Concordo": cores_ufpr['verde_principal'],
            "Desconheço": cores_ufpr['amarelo'],
            "Discordo": cores_ufpr['vermelho']
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
            x=1,
            bgcolor='rgba(255,255,255,0.8)'
        ),
        title=dict(x=0.5, xanchor="center", font=dict(color=cores_ufpr['cinza_escuro'])),
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    fig.update_xaxes(ticksuffix="%", range=[0, 100], gridcolor=cores_ufpr['cinza_medio'])
    fig.update_yaxes(title=None, categoryorder="total ascending", gridcolor=cores_ufpr['cinza_medio'])
    
    totais = curso_respostas.groupby("CURSO")["Quantidade"].sum().reset_index()
    for idx, row in totais.iterrows():
        fig.add_annotation(
            x=105, y=row["CURSO"], text=f"n={row['Quantidade']}",
            showarrow=False, xanchor="left", font=dict(size=10, color=cores_ufpr['cinza_escuro'])
        )

    return fig

def criar_grafico_distribuicao_disciplinas_ead(dff):
    if dff.empty:
        fig = go.Figure()
        fig.add_annotation(text="Nenhum dado para exibir", 
                          xref="paper", yref="paper", x=0.5, y=0.5, xanchor='center', yanchor='middle',
                          showarrow=False, font=dict(size=16))
        fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
        return fig
    
    if "NOME_DISCIPLINA" in dff.columns and not dff["NOME_DISCIPLINA"].isna().all():
        coluna_disciplina = "NOME_DISCIPLINA"
    else:
        coluna_disciplina = "COD_DISCIPLINA" 
    
    disciplina_respostas = dff.groupby([coluna_disciplina, "RESPOSTA"]).size().reset_index(name="Quantidade")
    
    totais_disciplina = disciplina_respostas.groupby(coluna_disciplina)["Quantidade"].sum().reset_index()
    totais_disciplina = totais_disciplina.nlargest(15, "Quantidade")
    
    disciplina_respostas = disciplina_respostas[disciplina_respostas[coluna_disciplina].isin(totais_disciplina[coluna_disciplina])]
    
    total_por_disciplina = disciplina_respostas.groupby(coluna_disciplina)["Quantidade"].transform('sum')
    disciplina_respostas["Percentual"] = (disciplina_respostas["Quantidade"] / total_por_disciplina * 100).round(1)
    
    disciplina_respostas["RESPOSTA"] = pd.Categorical(
        disciplina_respostas["RESPOSTA"],
        categories=ordem_likert,
        ordered=True
    )
    
    taxa_concordo = (
        disciplina_respostas[disciplina_respostas["RESPOSTA"] == "Concordo"]
        .set_index(coluna_disciplina)["Percentual"]
        .to_dict()
    )
    
    disciplina_respostas["ordem_concordo"] = disciplina_respostas[coluna_disciplina].map(taxa_concordo).fillna(0)
    disciplina_respostas.sort_values(["ordem_concordo", coluna_disciplina, "RESPOSTA"], 
                                    ascending=[False, True, True], inplace=True)

    fig = px.bar(
        disciplina_respostas,
        x="Percentual",
        y=coluna_disciplina,
        color="RESPOSTA",
        barmode="stack",
        title="Distribuição de Respostas por Disciplinas EAD (Top 15)",
        labels={
            coluna_disciplina: "Disciplina", 
            "Percentual": "Percentual de Respostas (%)", 
            "RESPOSTA": "Resposta"
        },
        color_discrete_map={
            "Concordo": cores_ufpr['verde_principal'],
            "Desconheço": cores_ufpr['amarelo'],
            "Discordo": cores_ufpr['vermelho']
        },
        hover_data={"Quantidade": True, "Percentual": True}
    )
    
    fig.update_layout(
        margin=dict(l=200, r=50, t=80, b=50),
        legend=dict(
            title="Respostas:",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.8)'
        ),
        title=dict(x=0.5, xanchor="center", font=dict(color=cores_ufpr['cinza_escuro'])),
        height=600,
        font=dict(size=11, family="Segoe UI"),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    fig.update_xaxes(ticksuffix="%", range=[0, 100], gridcolor=cores_ufpr['cinza_medio'])
    fig.update_yaxes(title=None, categoryorder="total ascending", gridcolor=cores_ufpr['cinza_medio'])
    
    totais = disciplina_respostas.groupby(coluna_disciplina)["Quantidade"].sum().reset_index()
    for idx, row in totais.iterrows():
        fig.add_annotation(
            x=105, y=row[coluna_disciplina], text=f"n={row['Quantidade']}",
            showarrow=False, xanchor="left", font=dict(size=9, color=cores_ufpr['cinza_escuro'])
        )

    return fig

def criar_grafico_treemap_disciplinas_ead(dff):
    if dff.empty:
        fig = go.Figure()
        fig.add_annotation(text="Nenhum dado para exibir", 
                          xref="paper", yref="paper", x=0.5, y=0.5, xanchor='center', yanchor='middle',
                          showarrow=False, font=dict(size=16))
        fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
        return fig
    
    valores = {"Discordo": 1, "Desconheço": 2, "Concordo": 3}
    dff["valor_num"] = dff["RESPOSTA"].map(valores)
    
    if "NOME_DISCIPLINA" in dff.columns and not dff["NOME_DISCIPLINA"].isna().all():
        coluna_disciplina = "NOME_DISCIPLINA"
    else:
        coluna_disciplina = "COD_DISCIPLINA"
    
    disciplina_stats = dff.groupby(coluna_disciplina).agg({
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
            coluna_disciplina: ["Outros"],
            "valor_num": [outros_media],
            "Total_Respostas": [outros_total]
        })
        
        disciplina_stats = pd.concat([top_10, outros_row], ignore_index=True)
    
    disciplina_stats['label_completo'] = disciplina_stats.apply(
        lambda x: f"{x[coluna_disciplina][:30]}...<br>({x['Total_Respostas']} resp)", 
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
        title=dict(x=0.5, xanchor="center", font=dict(color=cores_ufpr['cinza_escuro'])),
        height=600,
        font=dict(size=14, family="Segoe UI"),
        margin=dict(t=50, l=25, r=25, b=25),
        paper_bgcolor='white'
    )
    
    fig.update_traces(
        textfont=dict(size=14, family="Segoe UI"),
        texttemplate='<b>%{label}</b>',
        hovertemplate='<b>%{label}</b><br>Total Respostas: %{value}<br>Pontuação Média: %{color:.2f}<extra></extra>'
    )
    fig.update_coloraxes(showscale=False)
    
    return fig

def criar_grafico_distribuicao_unidades_institucional(dff):
    if dff.empty:
        fig = go.Figure()
        fig.add_annotation(text="Nenhum dado para exibir", 
                          xref="paper", yref="paper", x=0.5, y=0.5, xanchor='center', yanchor='middle',
                          showarrow=False, font=dict(size=16))
        fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
        return fig
    
    valores = {"Discordo": 1, "Desconheço": 2, "Concordo": 3}
    dff["valor_num"] = dff["RESPOSTA"].map(valores)
    
    if "LOTACAO" in dff.columns and not dff["LOTACAO"].isna().all():
        coluna_unidade = "LOTACAO"
    else:
        coluna_unidade = "SIGLA_LOTACAO"
    
    unidade_respostas = dff.groupby([coluna_unidade, "RESPOSTA"]).size().reset_index(name="Quantidade")
    
    totais_unidade = unidade_respostas.groupby(coluna_unidade)["Quantidade"].sum().reset_index()
    totais_unidade = totais_unidade.nlargest(10, "Quantidade")
    
    unidade_respostas = unidade_respostas[unidade_respostas[coluna_unidade].isin(totais_unidade[coluna_unidade])]
    
    total_por_unidade = unidade_respostas.groupby(coluna_unidade)["Quantidade"].transform('sum')
    unidade_respostas["Percentual"] = (unidade_respostas["Quantidade"] / total_por_unidade * 100).round(1)
    
    unidade_respostas["RESPOSTA"] = pd.Categorical(
        unidade_respostas["RESPOSTA"],
        categories=ordem_likert,
        ordered=True
    )
    
    fig = px.bar(
        unidade_respostas,
        x="Percentual",
        y=coluna_unidade,
        color="RESPOSTA",
        barmode="stack",
        title="Distribuição de Respostas por Unidade (Top 10)",
        labels={
            coluna_unidade: "Unidade", 
            "Percentual": "Percentual de Respostas (%)", 
            "RESPOSTA": "Resposta"
        },
        color_discrete_map={
            "Concordo": cores_ufpr['verde_principal'],
            "Desconheço": cores_ufpr['amarelo'],
            "Discordo": cores_ufpr['vermelho']
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
            x=1,
            bgcolor='rgba(255,255,255,0.8)'
        ),
        title=dict(x=0.5, xanchor="center", font=dict(color=cores_ufpr['cinza_escuro'])),
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    fig.update_xaxes(ticksuffix="%", range=[0, 100], gridcolor=cores_ufpr['cinza_medio'])
    
    return fig

def criar_grafico_treemap_unidades_institucional(dff):
    if dff.empty:
        fig = go.Figure()
        fig.add_annotation(text="Nenhum dado para exibir", 
                          xref="paper", yref="paper", x=0.5, y=0.5, xanchor='center', yanchor='middle',
                          showarrow=False, font=dict(size=16))
        fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
        return fig
    
    valores = {"Discordo": 1, "Desconheço": 2, "Concordo": 3}
    dff["valor_num"] = dff["RESPOSTA"].map(valores)
    
    if "LOTACAO" in dff.columns and not dff["LOTACAO"].isna().all():
        coluna_unidade = "LOTACAO"
    else:
        coluna_unidade = "SIGLA_LOTACAO"
    
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
        lambda x: f"{x[coluna_unidade][:25]}...<br>({x['Total_Respostas']} resp)", 
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
        title=dict(x=0.5, xanchor="center", font=dict(color=cores_ufpr['cinza_escuro'])),
        height=600,
        font=dict(size=14, family="Segoe UI"),
        margin=dict(t=50, l=25, r=25, b=25),
        paper_bgcolor='white'
    )
    
    fig.update_coloraxes(showscale=False)
    fig.update_traces(
        textfont=dict(size=16, family="Segoe UI"),
        hovertemplate='<b>%{label}</b><br>Total Respostas: %{value}<br>Pontuação Média: %{color:.2f}<extra></extra>'
    )
    
    return fig

componentes_iniciais = {
    'filtro-id-cursos': dcc.Dropdown(id="filtro-id-cursos", options=[], multi=True),
    'filtro-curso-cursos': dcc.Dropdown(id="filtro-curso-cursos", options=[], multi=True),
    'grafico-satisfacao-cursos': dcc.Graph(id="grafico-satisfacao-cursos"),
    'grafico-distribuicao-cursos': dcc.Graph(id="grafico-distribuicao-cursos"),
    'grafico-treemap-setores': dcc.Graph(id="grafico-treemap-setores"),
    
    'filtro-id-presencial': dcc.Dropdown(id="filtro-id-presencial", options=[], multi=True),
    'filtro-curso-presencial': dcc.Dropdown(id="filtro-curso-presencial", options=[], multi=True),
    'filtro-pergunta-presencial': dcc.Dropdown(id="filtro-pergunta-presencial", options=[], multi=True),
    'grafico-likert-presencial': dcc.Graph(id="grafico-likert-presencial"),
    'grafico-satisfacao-presencial': dcc.Graph(id="grafico-satisfacao-presencial"),
    'grafico-treemap-departamentos': dcc.Graph(id="grafico-treemap-departamentos"),
    
    'filtro-id-ead': dcc.Dropdown(id="filtro-id-ead", options=[], multi=True),
    'filtro-programa-ead': dcc.Dropdown(id="filtro-programa-ead", options=[], multi=True),
    'filtro-pergunta-ead': dcc.Dropdown(id="filtro-pergunta-ead", options=[], multi=True),
    'grafico-distribuicao-disciplinas-ead': dcc.Graph(id="grafico-distribuicao-disciplinas-ead"),
    'grafico-satisfacao-ead': dcc.Graph(id="grafico-satisfacao-ead"),
    'grafico-treemap-disciplinas-ead': dcc.Graph(id="grafico-treemap-disciplinas-ead"),
    
    'filtro-id-institucional': dcc.Dropdown(id="filtro-id-institucional", options=[], multi=True),
    'filtro-unidade-institucional': dcc.Dropdown(id="filtro-unidade-institucional", options=[], multi=True),
    'grafico-satisfacao-institucional': dcc.Graph(id="grafico-satisfacao-institucional"),
    'grafico-distribuicao-unidades-institucional': dcc.Graph(id="grafico-distribuicao-unidades-institucional"),
    'grafico-treemap-unidades-institucional': dcc.Graph(id="grafico-treemap-unidades-institucional"),
}

def criar_layout_cursos():
    componentes_iniciais['filtro-id-cursos'].options = [
        {"label": str(id_pesquisa), "value": id_pesquisa} 
        for id_pesquisa in sorted(df_cursos["ID_PESQUISA"].dropna().unique())
    ]
    componentes_iniciais['filtro-curso-cursos'].options = [
        {"label": c, "value": c} for c in sorted(df_cursos["CURSO"].dropna().unique())
    ]
    
    return html.Div(style=estilos['card'], children=[
        html.H3("📊 Avaliação de Cursos", style={'color': cores_ufpr['verde_principal'], 'marginBottom': '20px', 'textAlign': 'center'}),
        
        html.Div(style=estilos['filtros_container'], children=[
            html.Div([
                html.Label("🔍 ID da Pesquisa", style={'fontWeight': '600', 'marginBottom': '5px'}),
                componentes_iniciais['filtro-id-cursos']
            ], style={"width": "48%", "display": "inline-block", "padding": "10px", "marginRight": "2%"}),

            html.Div([
                html.Label("📚 Curso", style={'fontWeight': '600', 'marginBottom': '5px'}),
                componentes_iniciais['filtro-curso-cursos']
            ], style={"width": "48%", "display": "inline-block", "padding": "10px", "marginLeft": "2%"}),
        ]),

        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px'}, children=[
            html.Div(children=[
                componentes_iniciais['grafico-satisfacao-cursos']
            ], style=estilos['grafico_duplo']),
            
            html.Div(children=[
                componentes_iniciais['grafico-distribuicao-cursos']
            ], style=estilos['grafico_duplo']),
        ]),
        
        html.Div(children=[
            componentes_iniciais['grafico-treemap-setores']
        ], style=estilos['treemap_container'])
    ])

def criar_layout_presencial():
    perguntas_unicas = sorted(df_presencial["PERGUNTA"].dropna().unique())
    opcoes_perguntas = []

    for i, pergunta in enumerate(perguntas_unicas, 1):
        palavras = pergunta.split()[:6]
        label_resumido = " ".join(palavras) + "..." if len(palavras) == 6 else pergunta
        label_final = f"P{i}: {label_resumido}"
        opcoes_perguntas.append({"label": label_final, "value": label_final})

    componentes_iniciais['filtro-id-presencial'].options = [
        {"label": str(id_pesquisa), "value": id_pesquisa} 
        for id_pesquisa in sorted(df_presencial["ID_PESQUISA"].dropna().unique())
    ]
    componentes_iniciais['filtro-curso-presencial'].options = [
        {"label": c, "value": c} for c in sorted(df_presencial["CURSO"].dropna().unique())
    ]
    componentes_iniciais['filtro-pergunta-presencial'].options = opcoes_perguntas

    return html.Div(style=estilos['card'], children=[
        html.H3("🎓 Disciplinas Presenciais", style={'color': cores_ufpr['verde_principal'], 'marginBottom': '20px', 'textAlign': 'center'}),
        
        html.Div(style=estilos['filtros_container'], children=[
            html.Div([
                html.Label("🔍 ID da Pesquisa", style={'fontWeight': '600', 'marginBottom': '5px'}),
                componentes_iniciais['filtro-id-presencial']
            ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

            html.Div([
                html.Label("📚 Curso", style={'fontWeight': '600', 'marginBottom': '5px'}),
                componentes_iniciais['filtro-curso-presencial']
            ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

            html.Div([
                html.Label("❓ Pergunta", style={'fontWeight': '600', 'marginBottom': '5px'}),
                componentes_iniciais['filtro-pergunta-presencial']
            ], style={"width": "40%", "display": "inline-block", "padding": "10px"}),
        ]),

        html.Div(children=[
            componentes_iniciais['grafico-likert-presencial']
        ], style=estilos['grafico_principal']),
        
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px'}, children=[
            html.Div(children=[
                componentes_iniciais['grafico-satisfacao-presencial']
            ], style=estilos['grafico_duplo']),
            
            html.Div(children=[
                componentes_iniciais['grafico-treemap-departamentos']
            ], style=estilos['grafico_duplo']),
        ])
    ])

def criar_layout_ead():
    perguntas_unicas = sorted(df_ead["PERGUNTA"].dropna().unique())
    opcoes_perguntas = []

    for i, pergunta in enumerate(perguntas_unicas, 1):
        palavras = pergunta.split()[:6]
        label_resumido = " ".join(palavras) + "..." if len(palavras) == 6 else pergunta
        label_final = f"P{i}: {label_resumido}"
        opcoes_perguntas.append({"label": label_final, "value": label_final})

    componentes_iniciais['filtro-id-ead'].options = [
        {"label": str(id_pesquisa), "value": id_pesquisa} 
        for id_pesquisa in sorted(df_ead["ID_PESQUISA"].dropna().unique())
    ]
    componentes_iniciais['filtro-programa-ead'].options = [
        {"label": c, "value": c} for c in sorted(df_ead["CURSO"].dropna().unique())
    ]
    componentes_iniciais['filtro-pergunta-ead'].options = opcoes_perguntas

    return html.Div(style=estilos['card'], children=[
        html.H3("💻 Disciplinas EAD", style={'color': cores_ufpr['verde_principal'], 'marginBottom': '20px', 'textAlign': 'center'}),
        
        html.Div(style=estilos['filtros_container'], children=[
            html.Div([
                html.Label("🔍 ID da Pesquisa", style={'fontWeight': '600', 'marginBottom': '5px'}),
                componentes_iniciais['filtro-id-ead']
            ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

            html.Div([
                html.Label("🎯 Programa EAD", style={'fontWeight': '600', 'marginBottom': '5px'}),
                componentes_iniciais['filtro-programa-ead']
            ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

            html.Div([
                html.Label("❓ Pergunta", style={'fontWeight': '600', 'marginBottom': '5px'}),
                componentes_iniciais['filtro-pergunta-ead']
            ], style={"width": "40%", "display": "inline-block", "padding": "10px"}),
        ]),

        html.Div(children=[
            componentes_iniciais['grafico-distribuicao-disciplinas-ead']
        ], style=estilos['grafico_principal']),
        
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px'}, children=[
            html.Div(children=[
                componentes_iniciais['grafico-satisfacao-ead']
            ], style=estilos['grafico_duplo']),
            
            html.Div(children=[
                componentes_iniciais['grafico-treemap-disciplinas-ead']
            ], style=estilos['grafico_duplo']),
        ])
    ])

def criar_layout_institucional():
    if "LOTACAO" in df_institucional.columns:
        unidades_unicas = sorted(df_institucional["LOTACAO"].dropna().unique())
    else:
        unidades_unicas = sorted(df_institucional["SIGLA_LOTACAO"].dropna().unique())
    
    componentes_iniciais['filtro-id-institucional'].options = [
        {"label": str(id_pesquisa), "value": id_pesquisa} 
        for id_pesquisa in sorted(df_institucional["ID_PESQUISA"].dropna().unique())
    ]
    componentes_iniciais['filtro-unidade-institucional'].options = [
        {"label": c, "value": c} for c in unidades_unicas
    ]

    return html.Div(style=estilos['card'], children=[
        html.H3("🏛️ Avaliação Institucional", style={'color': cores_ufpr['verde_principal'], 'marginBottom': '20px', 'textAlign': 'center'}),
        
        html.Div(style=estilos['filtros_container'], children=[
            html.Div([
                html.Label("🔍 ID da Pesquisa", style={'fontWeight': '600', 'marginBottom': '5px'}),
                componentes_iniciais['filtro-id-institucional']
            ], style={"width": "48%", "display": "inline-block", "padding": "10px", "marginRight": "2%"}),

            html.Div([
                html.Label("🏢 Unidade", style={'fontWeight': '600', 'marginBottom': '5px'}),
                componentes_iniciais['filtro-unidade-institucional']
            ], style={"width": "48%", "display": "inline-block", "padding": "10px", "marginLeft": "2%"}),
        ]),

        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px'}, children=[
            html.Div(children=[
                componentes_iniciais['grafico-satisfacao-institucional']
            ], style=estilos['grafico_duplo']),
            
            html.Div(children=[
                componentes_iniciais['grafico-distribuicao-unidades-institucional']
            ], style=estilos['grafico_duplo']),
        ]),
        
        html.Div(children=[
            componentes_iniciais['grafico-treemap-unidades-institucional']
        ], style=estilos['treemap_container'])
    ])

app.layout = html.Div(style=estilos['container_principal'], children=[
    html.Div(style=estilos['header'], children=[
        html.H1("Dashboard de Avaliações UFPR", style=estilos['titulo_principal']),
        html.P("Análise de Satisfação e Desempenho Acadêmico", style=estilos['subtitulo']),
    ]),
    
    html.Div(style=estilos['tabs_container'], children=[
        dcc.Tabs(
            id="tabs-principais", 
            value='tab-cursos',
            children=[
                dcc.Tab(
                    label='📊 Cursos', 
                    value='tab-cursos',
                    style=estilos['tab'],
                    selected_style=estilos['tab_selecionada']
                ),
                dcc.Tab(
                    label='🎓 Disciplinas Presenciais', 
                    value='tab-presencial',
                    style=estilos['tab'],
                    selected_style=estilos['tab_selecionada']
                ),
                dcc.Tab(
                    label='💻 Disciplinas EAD', 
                    value='tab-ead',
                    style=estilos['tab'],
                    selected_style=estilos['tab_selecionada']
                ),
                dcc.Tab(
                    label='🏛️ Institucional', 
                    value='tab-institucional',
                    style=estilos['tab'],
                    selected_style=estilos['tab_selecionada']
                ),
            ]
        ),
    ]),
    
    html.Div(id="conteudo-tab")
])

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
    else:
        return html.Div("Selecione uma aba")

@app.callback(
    Output("grafico-satisfacao-cursos", "figure"),
    Output("grafico-distribuicao-cursos", "figure"),
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
    fig_distribuicao_cursos = criar_grafico_distribuicao_cursos(dff)
    fig_treemap_setores = criar_grafico_treemap_setor(dff)
    
    return fig_satisfacao, fig_distribuicao_cursos, fig_treemap_setores

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
    
    if ids: 
        dff = dff[dff["ID_PESQUISA"].isin(ids)]
    if cursos: 
        dff = dff[dff["CURSO"].isin(cursos)]
    
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
    Output("grafico-distribuicao-disciplinas-ead", "figure"),
    Output("grafico-satisfacao-ead", "figure"),
    Output("grafico-treemap-disciplinas-ead", "figure"),
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
    
    fig_distribuicao_disciplinas = criar_grafico_distribuicao_disciplinas_ead(dff)
    fig_satisfacao = criar_grafico_satisfacao_geral(dff)
    fig_treemap_disciplinas = criar_grafico_treemap_disciplinas_ead(dff)
    
    return fig_distribuicao_disciplinas, fig_satisfacao, fig_treemap_disciplinas

@app.callback(
    Output("grafico-satisfacao-institucional", "figure"),
    Output("grafico-distribuicao-unidades-institucional", "figure"),
    Output("grafico-treemap-unidades-institucional", "figure"),
    Input("filtro-id-institucional", "value"),
    Input("filtro-unidade-institucional", "value"),
)
def atualizar_graficos_institucional(ids, unidades):
    dff = df_institucional.copy()
    
    if ids: 
        dff = dff[dff["ID_PESQUISA"].isin(ids)]
    if unidades: 
        if "LOTACAO" in dff.columns:
            coluna_unidade = "LOTACAO"
        else:
            coluna_unidade = "SIGLA_LOTACAO"
        dff = dff[dff[coluna_unidade].isin(unidades)]
    
    fig_satisfacao = criar_grafico_satisfacao_geral(dff)
    fig_distribuicao = criar_grafico_distribuicao_unidades_institucional(dff)
    fig_treemap_unidades = criar_grafico_treemap_unidades_institucional(dff)
    
    return fig_satisfacao, fig_distribuicao, fig_treemap_unidades

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8050, dev_tools_silence_routes_logging=True)
