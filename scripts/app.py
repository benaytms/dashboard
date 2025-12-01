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
    
    # CORREÇÃO: Garantir que NOME_DISCIPLINA seja preservada
    if "NOME_DISCIPLINA_DISC" in df.columns:
        df.rename(columns={"NOME_DISCIPLINA_DISC": "NOME_DISCIPLINA"}, inplace=True)
    
    return df

def processar_dados_institucional():
    df = df_inst_resp.merge(df_inst_q, on=["ID_PERGUNTA", "ID_QUESTIONARIO"], how="left")
    df = df.merge(df_inst_unidades, on="SIGLA_LOTACAO", how="left")
    
    if "PERGUNTA_y" in df.columns: df.rename(columns={"PERGUNTA_y": "PERGUNTA"}, inplace=True)
    if "PERGUNTA_x" in df.columns: df.drop(columns=["PERGUNTA_x"], inplace=True)
    
    # CORREÇÃO: Usar explicitamente a LOTACAO da tabela PESQUISA 442 (LOTACAO_x)
    print("Colunas disponíveis após merge:", df.columns.tolist())
    
    if "LOTACAO_x" in df.columns:
        print(f"LOTACAO_x (PESQUISA 442) - Primeiros 5: {df['LOTACAO_x'].dropna().unique()[:5]}")
        if "LOTACAO_y" in df.columns:
            print(f"LOTACAO_y (Unidades) - Primeiros 5: {df['LOTACAO_y'].dropna().unique()[:5]}")
        
        # Usar LOTACAO_x (da tabela PESQUISA 442) como a coluna principal
        df.rename(columns={"LOTACAO_x": "LOTACAO"}, inplace=True)
        
        # Remover colunas conflitantes
        colunas_para_remover = ["LOTACAO_y", "SIGLA_LOTACAO"]
        for col in colunas_para_remover:
            if col in df.columns:
                df.drop(columns=[col], inplace=True)
                print(f"Removida coluna: {col}")
    
    print(f"Coluna LOTACAO final - Primeiros 5: {df['LOTACAO'].dropna().unique()[:5]}")
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
# NOVAS FUNÇÕES PARA EAD
# =============================================================

def criar_grafico_distribuicao_cursos(dff):
    """Distribuição de Respostas por Cursos"""
    if dff.empty:
        return px.bar(title="Nenhum dado para exibir")
    
    # Calcular distribuição de respostas por curso (top 15 por volume)
    curso_respostas = dff.groupby(["CURSO", "RESPOSTA"]).size().reset_index(name="Quantidade")
    
    # Calcular totais por curso para ordenação
    totais_curso = curso_respostas.groupby("CURSO")["Quantidade"].sum().reset_index()
    totais_curso = totais_curso.nlargest(15, "Quantidade")
    
    # Filtrar apenas os top 15 cursos
    curso_respostas = curso_respostas[curso_respostas["CURSO"].isin(totais_curso["CURSO"])]
    
    # Calcular percentuais
    total_por_curso = curso_respostas.groupby("CURSO")["Quantidade"].transform('sum')
    curso_respostas["Percentual"] = (curso_respostas["Quantidade"] / total_por_curso * 100).round(1)
    
    # Ordenar as categorias
    curso_respostas["RESPOSTA"] = pd.Categorical(
        curso_respostas["RESPOSTA"],
        categories=ordem_likert,
        ordered=True
    )
    
    # Ordenar cursos por percentual de "Concordo" (decrescente)
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
        title=dict(x=0.5, xanchor="center"),
        height=500
    )
    
    fig.update_xaxes(ticksuffix="%", range=[0, 100])
    fig.update_yaxes(title=None, categoryorder="total ascending")
    
    # Adicionar anotações com número total de respostas
    totais = curso_respostas.groupby("CURSO")["Quantidade"].sum().reset_index()
    for idx, row in totais.iterrows():
        fig.add_annotation(
            x=105, y=row["CURSO"], text=f"n={row['Quantidade']}",
            showarrow=False, xanchor="left", font=dict(size=10, color="gray")
        )

    return fig

def criar_grafico_distribuicao_disciplinas_ead(dff):
    """Distribuição de Respostas por Disciplinas EAD usando NOME_DISCIPLINA"""
    if dff.empty:
        return px.bar(title="Nenhum dado para exibir")
    
    # CORREÇÃO: Verificar explicitamente se NOME_DISCIPLINA existe e tem dados
    if "NOME_DISCIPLINA" in dff.columns and not dff["NOME_DISCIPLINA"].isna().all():
        coluna_disciplina = "NOME_DISCIPLINA"
        print(f"Usando NOME_DISCIPLINA, {dff[coluna_disciplina].nunique()} disciplinas únicas")
    else:
        coluna_disciplina = "COD_DISCIPLINA" 
        print("Usando COD_DISCIPLINA como fallback")
    
    # Calcular distribuição de respostas por disciplina (top 15 por volume)
    disciplina_respostas = dff.groupby([coluna_disciplina, "RESPOSTA"]).size().reset_index(name="Quantidade")
    
    # Calcular totais por disciplina para ordenação
    totais_disciplina = disciplina_respostas.groupby(coluna_disciplina)["Quantidade"].sum().reset_index()
    totais_disciplina = totais_disciplina.nlargest(15, "Quantidade")
    
    # Filtrar apenas as top 15 disciplinas
    disciplina_respostas = disciplina_respostas[disciplina_respostas[coluna_disciplina].isin(totais_disciplina[coluna_disciplina])]
    
    # Calcular percentuais
    total_por_disciplina = disciplina_respostas.groupby(coluna_disciplina)["Quantidade"].transform('sum')
    disciplina_respostas["Percentual"] = (disciplina_respostas["Quantidade"] / total_por_disciplina * 100).round(1)
    
    # Ordenar as categorias
    disciplina_respostas["RESPOSTA"] = pd.Categorical(
        disciplina_respostas["RESPOSTA"],
        categories=ordem_likert,
        ordered=True
    )
    
    # Ordenar disciplinas por percentual de "Concordo" (decrescente)
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
            "Concordo": "#2E8B57",
            "Desconheço": "#FFA500",
            "Discordo": "#DC143C"
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
            x=1
        ),
        title=dict(x=0.5, xanchor="center"),
        height=600,
        font=dict(size=11)
    )
    
    fig.update_xaxes(ticksuffix="%", range=[0, 100])
    fig.update_yaxes(title=None, categoryorder="total ascending")
    
    # Adicionar anotações com número total de respostas
    totais = disciplina_respostas.groupby(coluna_disciplina)["Quantidade"].sum().reset_index()
    for idx, row in totais.iterrows():
        fig.add_annotation(
            x=105, y=row[coluna_disciplina], text=f"n={row['Quantidade']}",
            showarrow=False, xanchor="left", font=dict(size=9, color="gray")
        )

    return fig

def criar_grafico_treemap_disciplinas_ead(dff):
    """Treemap das disciplinas EAD por volume de respostas usando NOME_DISCIPLINA"""
    if dff.empty:
        return px.treemap(title="Nenhum dado para exibir")
    
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
    
    # MELHORIA: Texto mais compacto e legível
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
        title=dict(x=0.5, xanchor="center"),
        height=600,
        font=dict(size=14),
        margin=dict(t=50, l=25, r=25, b=25)
    )
    
    fig.update_traces(
        textfont=dict(size=14, family="Arial"),
        texttemplate='<b>%{label}</b>',
        hovertemplate='<b>%{label}</b><br>Total Respostas: %{value}<br>Pontuação Média: %{color:.2f}<extra></extra>'
    )
    fig.update_coloraxes(showscale=False)
    
    return fig

# =============================================================
# FUNÇÕES PARA INSTITUCIONAL
# =============================================================

def criar_grafico_distribuicao_unidades_institucional(dff):
    if dff.empty:
        return px.bar(title="Nenhum dado para exibir")
    
    valores = {"Discordo": 1, "Desconheço": 2, "Concordo": 3}
    dff["valor_num"] = dff["RESPOSTA"].map(valores)
    
    # CORREÇÃO: Garantir que LOTACAO seja usada quando disponível
    if "LOTACAO" in dff.columns and not dff["LOTACAO"].isna().all():
        coluna_unidade = "LOTACAO"
        print(f"Distribuição Unidades - Usando LOTACAO, {dff[coluna_unidade].nunique()} unidades únicas")
    else:
        coluna_unidade = "SIGLA_LOTACAO"
        print("Distribuição Unidades - Usando SIGLA_LOTACAO como fallback")
    
    # Calcular distribuição de respostas por unidade
    unidade_respostas = dff.groupby([coluna_unidade, "RESPOSTA"]).size().reset_index(name="Quantidade")
    
    # Resto da função permanece igual...
    
    # Calcular totais por unidade para ordenação
    totais_unidade = unidade_respostas.groupby(coluna_unidade)["Quantidade"].sum().reset_index()
    totais_unidade = totais_unidade.nlargest(10, "Quantidade")
    
    # Filtrar apenas as top 10 unidades
    unidade_respostas = unidade_respostas[unidade_respostas[coluna_unidade].isin(totais_unidade[coluna_unidade])]
    
    # Calcular percentuais
    total_por_unidade = unidade_respostas.groupby(coluna_unidade)["Quantidade"].transform('sum')
    unidade_respostas["Percentual"] = (unidade_respostas["Quantidade"] / total_por_unidade * 100).round(1)
    
    # Ordenar as categorias
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
        title=dict(x=0.5, xanchor="center"),
        height=500
    )
    
    fig.update_xaxes(ticksuffix="%", range=[0, 100])
    
    return fig

def criar_grafico_treemap_unidades_institucional(dff):
    if dff.empty:
        return px.treemap(title="Nenhum dado para exibir")
    
    valores = {"Discordo": 1, "Desconheço": 2, "Concordo": 3}
    dff["valor_num"] = dff["RESPOSTA"].map(valores)
    
    # CORREÇÃO: Garantir que LOTACAO seja usada quando disponível
    if "LOTACAO" in dff.columns and not dff["LOTACAO"].isna().all():
        coluna_unidade = "LOTACAO"
        print(f"Treemap Unidades - Usando LOTACAO, {dff[coluna_unidade].nunique()} unidades únicas")
    else:
        coluna_unidade = "SIGLA_LOTACAO"
        print("Treemap Unidades - Usando SIGLA_LOTACAO como fallback")
    
    unidade_stats = dff.groupby(coluna_unidade).agg({
        "valor_num": "mean",
        "RESPOSTA": "count"
    }).reset_index()
    unidade_stats.rename(columns={"RESPOSTA": "Total_Respostas"}, inplace=True)
    
    # Resto da função permanece igual...
    
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
            
            # ALTERAÇÃO: Substituir "grafico-top-cursos" por "grafico-distribuicao-cursos"
            html.Div([
                dcc.Graph(id="grafico-distribuicao-cursos"),
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

        # REMOÇÃO: Gráfico likert removido completamente
        # Gráfico principal no topo
        dcc.Graph(id="grafico-distribuicao-disciplinas-ead"),
        
        html.Div([
            html.Div([
                dcc.Graph(id="grafico-satisfacao-ead"),
            ], style={"width": "50%", "display": "inline-block"}),
            
            html.Div([
                dcc.Graph(id="grafico-treemap-disciplinas-ead"),
            ], style={"width": "50%", "display": "inline-block"}),
        ])
    ])

def criar_layout_institucional():
    # DEBUG: Verificar se LOTACAO existe no DataFrame processado
    print("Layout Institucional - Colunas disponíveis:", df_institucional.columns.tolist())
    
    # CORREÇÃO: Forçar uso de LOTACAO
    if "LOTACAO" in df_institucional.columns:
        unidades_unicas = sorted(df_institucional["LOTACAO"].dropna().unique())
        print(f"Layout usando LOTACAO - {len(unidades_unicas)} unidades")
    else:
        unidades_unicas = sorted(df_institucional["SIGLA_LOTACAO"].dropna().unique())
        print(f"Layout usando SIGLA_LOTACAO (fallback) - {len(unidades_unicas)} unidades")
    
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
        # ... resto do layout

        html.Br(), html.Br(),

        html.Div([
            html.Div([
                dcc.Graph(id="grafico-satisfacao-institucional"),
            ], style={"width": "50%", "display": "inline-block"}),
            
            html.Div([
                dcc.Graph(id="grafico-distribuicao-unidades-institucional"),
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
    fig_distribuicao_cursos = criar_grafico_distribuicao_cursos(dff)  # NOVA FUNÇÃO
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
    
    # REMOÇÃO: Código do likert removido
    # Apenas 3 gráficos agora
    
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
        # CORREÇÃO: Forçar uso de LOTACAO
        if "LOTACAO" in dff.columns:
            coluna_unidade = "LOTACAO"
            print(f"Callback - Filtrando por LOTACAO: {unidades}")
        else:
            coluna_unidade = "SIGLA_LOTACAO"
            print(f"Callback - Filtrando por SIGLA_LOTACAO: {unidades}")
        dff = dff[dff[coluna_unidade].isin(unidades)]
    
    # DEBUG detalhado
    print(f"Dados após filtro - {len(dff)} registros")
    if "LOTACAO" in dff.columns:
        print(f"Valores únicos de LOTACAO: {dff['LOTACAO'].dropna().unique()[:10]}")
    
    fig_satisfacao = criar_grafico_satisfacao_geral(dff)
    fig_distribuicao = criar_grafico_distribuicao_unidades_institucional(dff)
    fig_treemap_unidades = criar_grafico_treemap_unidades_institucional(dff)
    
    return fig_satisfacao, fig_distribuicao, fig_treemap_unidades

if __name__ == "__main__":
    app.run(debug=True)