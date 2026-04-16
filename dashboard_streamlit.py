from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
REPORT_DIR = PROJECT_ROOT / "TCCPipeline" / "Result" / "relatorios_escolares"


def report_path(filename: str) -> Path:
    return REPORT_DIR / filename


@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def safe_read(filename: str) -> pd.DataFrame:
    path = report_path(filename)
    if not path.exists():
        st.error(
            f"Arquivo não encontrado: {path}. "
            "Rode a pipeline completa antes de abrir o dashboard."
        )
        st.stop()
    return load_csv(str(path))


def normalize_filters(
    df: pd.DataFrame,
    period_col: str = "NomePeriodo",
    series_col: str = "NomeSerie",
    key_prefix: str = "default",
) -> pd.DataFrame:
    filtered = df.copy()

    if period_col in filtered.columns:
        period_options = sorted(filtered[period_col].dropna().astype(str).unique().tolist())
        selected_periods = st.sidebar.multiselect(
            "Período",
            period_options,
            default=period_options,
            key=f"{key_prefix}_periodo",
        )
        if selected_periods:
            filtered = filtered[filtered[period_col].astype(str).isin(selected_periods)]

    if series_col in filtered.columns:
        series_options = sorted(filtered[series_col].dropna().astype(str).unique().tolist())
        selected_series = st.sidebar.multiselect(
            "Série",
            series_options,
            default=series_options,
            key=f"{key_prefix}_serie",
        )
        if selected_series:
            filtered = filtered[filtered[series_col].astype(str).isin(selected_series)]

    return filtered


def metric_row(items: list[tuple[str, str]]) -> None:
    columns = st.columns(len(items))
    for column, (label, value) in zip(columns, items):
        column.metric(label, value)


def plot_risk_distribution(integrated: pd.DataFrame) -> None:
    distribution = (
        integrated["nivel_risco"]
        .value_counts()
        .rename_axis("nivel_risco")
        .reset_index(name="quantidade")
    )
    fig = px.bar(
        distribution,
        x="nivel_risco",
        y="quantidade",
        color="nivel_risco",
        color_discrete_map={"alto": "#c0392b", "moderado": "#f39c12", "baixo": "#27ae60"},
        title="Distribuição de risco",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_overview() -> None:
    integrated = safe_read("relatorio_escolar_integrado.csv")
    ranking = safe_read("ranking_executivo_coordenacao.csv")
    filtered = normalize_filters(integrated, key_prefix="overview")
    ranking_filtered = ranking.copy()

    if "NomePeriodo" in ranking_filtered.columns and "NomePeriodo" in filtered.columns:
        periods = filtered["NomePeriodo"].astype(str).unique().tolist()
        ranking_filtered = ranking_filtered[ranking_filtered["NomePeriodo"].astype(str).isin(periods)]
    if "NomeSerie" in ranking_filtered.columns and "NomeSerie" in filtered.columns:
        series = filtered["NomeSerie"].astype(str).unique().tolist()
        ranking_filtered = ranking_filtered[ranking_filtered["NomeSerie"].astype(str).isin(series)]

    st.subheader("Visão geral")
    metric_row(
        [
            ("Registros avaliados", f"{len(filtered):,}".replace(",", ".")),
            ("Alunos únicos", f"{filtered['IDAluno'].nunique():,}".replace(",", ".")),
            ("Casos alto risco", f"{(filtered['nivel_risco'] == 'alto').sum():,}".replace(",", ".")),
            ("Casos moderados", f"{(filtered['nivel_risco'] == 'moderado').sum():,}".replace(",", ".")),
        ]
    )

    plot_risk_distribution(filtered)

    top_disciplines = (
        filtered.groupby("NomeDisciplina", dropna=False)["nivel_risco"]
        .apply(lambda s: (s == "alto").mean())
        .reset_index(name="taxa_alto_risco")
        .sort_values("taxa_alto_risco", ascending=False)
        .head(12)
    )
    fig_disc = px.bar(
        top_disciplines,
        x="taxa_alto_risco",
        y="NomeDisciplina",
        orientation="h",
        title="Disciplinas com maior taxa de alto risco",
        color="taxa_alto_risco",
        color_continuous_scale="Reds",
    )
    fig_disc.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_disc, use_container_width=True)

    scatter = px.scatter(
        filtered,
        x="ValorMedia",
        y="predicted_next_grade",
        color="nivel_risco",
        hover_data=["NomeAluno", "NomeSerie", "NomeDisciplina", "NomeEtapa"],
        title="Nota atual x nota prevista",
        color_discrete_map={"alto": "#c0392b", "moderado": "#f39c12", "baixo": "#27ae60"},
    )
    st.plotly_chart(scatter, use_container_width=True)

    st.subheader("Ranking executivo")
    st.dataframe(
        ranking_filtered[
            [
                "NomeAluno",
                "NomeSerie",
                "nivel_prioridade_executiva",
                "indice_prioridade",
                "casos_alto_risco",
                "casos_risco_moderado",
                "media_nota_prevista",
                "faltas_acumuladas_maximas",
                "pagamentos_pendentes_maximos",
                "motivos_prioridade",
            ]
        ].head(20),
        use_container_width=True,
        hide_index=True,
    )


def render_teacher() -> None:
    teacher = safe_read("relatorio_professor.csv")
    teacher = normalize_filters(teacher, key_prefix="teacher")

    discipline_options = sorted(teacher["NomeDisciplina"].dropna().astype(str).unique().tolist())
    selected_disciplines = st.sidebar.multiselect(
        "Disciplina",
        discipline_options,
        default=discipline_options,
        key="teacher_disciplina",
    )
    if selected_disciplines:
        teacher = teacher[teacher["NomeDisciplina"].astype(str).isin(selected_disciplines)]

    risk_options = sorted(teacher["nivel_risco"].dropna().astype(str).unique().tolist())
    selected_risks = st.sidebar.multiselect(
        "Nível de risco",
        risk_options,
        default=risk_options,
        key="teacher_risco",
    )
    if selected_risks:
        teacher = teacher[teacher["nivel_risco"].astype(str).isin(selected_risks)]

    st.subheader("Painel do professor")
    metric_row(
        [
            ("Casos exibidos", f"{len(teacher):,}".replace(",", ".")),
            ("Alunos em alto risco", f"{(teacher['nivel_risco'] == 'alto').sum():,}".replace(",", ".")),
            ("Média nota atual", f"{teacher['nota_atual'].mean():.2f}" if not teacher.empty else "0.00"),
            ("Média nota prevista", f"{teacher['nota_prevista_proxima'].mean():.2f}" if not teacher.empty else "0.00"),
        ]
    )

    if not teacher.empty:
        top_students = (
            teacher.sort_values(["pontuacao_risco", "nota_prevista_proxima"], ascending=[False, True])
            .head(15)
        )
        fig_top = px.bar(
            top_students,
            x="pontuacao_risco",
            y="NomeAluno",
            color="nivel_risco",
            orientation="h",
            title="Alunos mais críticos no recorte atual",
            hover_data=["NomeDisciplina", "NomeEtapa", "nota_atual", "nota_prevista_proxima"],
            color_discrete_map={"alto": "#c0392b", "moderado": "#f39c12", "baixo": "#27ae60"},
        )
        fig_top.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_top, use_container_width=True)

        fig_scatter = px.scatter(
            teacher,
            x="nota_atual",
            y="nota_prevista_proxima",
            color="nivel_risco",
            size="pontuacao_risco",
            hover_data=["NomeAluno", "NomeDisciplina", "NomeEtapa", "fatores_alerta"],
            title="Relação entre nota atual, nota prevista e risco",
            color_discrete_map={"alto": "#c0392b", "moderado": "#f39c12", "baixo": "#27ae60"},
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.dataframe(
        teacher[
            [
                "NomeAluno",
                "NomeSerie",
                "NomeDisciplina",
                "NomeEtapa",
                "nota_atual",
                "nota_prevista_proxima",
                "pontuacao_risco",
                "nivel_risco",
                "fatores_alerta",
                "recomendacao_professor",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


def render_coordination() -> None:
    coord = safe_read("relatorio_coordenacao.csv")
    ranking = safe_read("ranking_executivo_coordenacao.csv")
    integrated = safe_read("relatorio_escolar_integrado.csv")

    coord = normalize_filters(coord, key_prefix="coord_coord")
    ranking = normalize_filters(ranking, key_prefix="coord_rank")
    integrated = normalize_filters(integrated, key_prefix="coord_integrated")

    st.subheader("Painel da coordenação")
    metric_row(
        [
            ("Agrupamentos críticos", f"{len(coord):,}".replace(",", ".")),
            ("Alunos no ranking", f"{len(ranking):,}".replace(",", ".")),
            ("Prioridade crítica", f"{(ranking['nivel_prioridade_executiva'] == 'critica').sum():,}".replace(",", ".")),
            ("Alto risco no recorte", f"{(integrated['nivel_risco'] == 'alto').sum():,}".replace(",", ".")),
        ]
    )

    top_groups = coord.sort_values("taxa_alto_risco", ascending=False).head(15)
    fig_groups = px.bar(
        top_groups,
        x="taxa_alto_risco",
        y="NomeDisciplina",
        color="NomeSerie",
        orientation="h",
        title="Disciplinas com maior taxa de alto risco",
        hover_data=["alunos_monitorados", "casos_alto_risco", "media_nota_prevista"],
    )
    fig_groups.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_groups, use_container_width=True)

    heat = (
        integrated.groupby(["NomeSerie", "NomeDisciplina"], dropna=False)["nivel_risco"]
        .apply(lambda s: (s == "alto").mean())
        .reset_index(name="taxa_alto_risco")
    )
    if not heat.empty:
        heatmap = heat.pivot(index="NomeSerie", columns="NomeDisciplina", values="taxa_alto_risco").fillna(0)
        fig_heat = px.imshow(
            heatmap,
            aspect="auto",
            color_continuous_scale="Reds",
            title="Mapa de calor de alto risco por série e disciplina",
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    st.subheader("Ranking executivo")
    st.dataframe(
        ranking[
            [
                "NomeAluno",
                "NomeSerie",
                "nivel_prioridade_executiva",
                "indice_prioridade",
                "casos_alto_risco",
                "casos_risco_moderado",
                "media_nota_prevista",
                "faltas_acumuladas_maximas",
                "pagamentos_pendentes_maximos",
                "motivos_prioridade",
                "acao_executiva_sugerida",
            ]
        ].head(30),
        use_container_width=True,
        hide_index=True,
    )


def render_secretary() -> None:
    secretary = safe_read("relatorio_secretaria.csv")
    secretary = normalize_filters(secretary, key_prefix="secretary")

    priority_options = sorted(secretary["prioridade_secretaria"].dropna().astype(str).unique().tolist())
    selected_priorities = st.sidebar.multiselect(
        "Prioridade da secretaria",
        priority_options,
        default=priority_options,
        key="secretary_prioridade",
    )
    if selected_priorities:
        secretary = secretary[secretary["prioridade_secretaria"].astype(str).isin(selected_priorities)]

    st.subheader("Painel da secretaria")
    metric_row(
        [
            ("Alunos monitorados", f"{len(secretary):,}".replace(",", ".")),
            ("Com alerta financeiro", f"{secretary['alerta_financeiro'].sum():,}".replace(",", ".")),
            ("Com alerta de frequência", f"{secretary['alerta_frequencia'].sum():,}".replace(",", ".")),
            ("Pendência média", f"{secretary['pagamentos_pendentes_maximos'].mean():.2f}" if not secretary.empty else "0.00"),
        ]
    )

    priority_distribution = (
        secretary["prioridade_secretaria"]
        .value_counts()
        .rename_axis("prioridade_secretaria")
        .reset_index(name="quantidade")
    )
    fig_priority = px.pie(
        priority_distribution,
        names="prioridade_secretaria",
        values="quantidade",
        title="Distribuição da prioridade administrativa",
    )
    st.plotly_chart(fig_priority, use_container_width=True)

    top_admin = secretary.sort_values(
        ["pagamentos_pendentes_maximos", "faltas_acumuladas_maximas", "casos_alto_risco"],
        ascending=[False, False, False],
    ).head(20)
    fig_admin = px.bar(
        top_admin,
        x="NomeAluno",
        y="pagamentos_pendentes_maximos",
        color="prioridade_secretaria",
        title="Casos com maior pendência financeira",
        hover_data=["NomeSerie", "faltas_acumuladas_maximas", "casos_alto_risco", "recomendacao_secretaria"],
    )
    st.plotly_chart(fig_admin, use_container_width=True)

    st.dataframe(
        secretary[
            [
                "NomeAluno",
                "NomeSerie",
                "disciplinas_monitoradas",
                "casos_alto_risco",
                "faltas_acumuladas_maximas",
                "pagamentos_pendentes_maximos",
                "prioridade_secretaria",
                "recomendacao_secretaria",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="Painel Escolar Preditivo",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("Painel Escolar Preditivo")
    st.caption(
        "Dashboard para professores, coordenação e secretaria a partir dos relatórios gerados pela pipeline."
    )

    profile = st.sidebar.selectbox(
        "Perfil",
        ["Visão geral", "Professor", "Coordenação", "Secretaria"],
    )

    if profile == "Visão geral":
        render_overview()
    elif profile == "Professor":
        render_teacher()
    elif profile == "Coordenação":
        render_coordination()
    else:
        render_secretary()


if __name__ == "__main__":
    main()
