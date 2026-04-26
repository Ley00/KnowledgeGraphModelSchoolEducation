from pathlib import Path

import numpy
import pandas

from school_predictor.project import ProjectPaths, ensure_parent_dir


REPORT_KEY_COLUMNS = [
    "IDAluno",
    "NomeAluno",
    "NomePeriodo",
    "NomeSerie",
    "NomeDisciplina",
    "NomeEtapa",
]

LANGUAGE_KEYWORDS = ("portugues", "redacao", "literatura", "gramatica", "ingles", "lingua")
EXACT_KEYWORDS = ("matematica", "fisica", "quimica", "biologia", "ciencias")
HUMANITIES_KEYWORDS = ("historia", "geografia", "filosofia", "sociologia")


def _load_mode_artifacts(project_root: str | Path, mode: str) -> tuple[pandas.DataFrame, pandas.DataFrame]:
    """Lê os dois artefatos-base de um modo: predições e dataset final."""
    project_paths = ProjectPaths.from_root(project_root)
    base_dir = project_paths.pipeline_artifacts_dir / mode
    predictions = pandas.read_csv(base_dir / "student_prediction_predictions.csv")
    dataset = pandas.read_csv(base_dir / "student_prediction_dataset.csv")
    return predictions, dataset


def _normalize_text(value: object) -> str:
    """Normaliza texto para facilitar regras simples por palavra-chave."""
    if pandas.isna(value):
        return ""
    return (
        str(value)
        .lower()
        .replace("á", "a")
        .replace("à", "a")
        .replace("ã", "a")
        .replace("â", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ô", "o")
        .replace("õ", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )


def _discipline_support_action(discipline: object) -> str:
    """Mapeia a disciplina para um tipo de recomendação pedagógica mais específica."""
    normalized = _normalize_text(discipline)
    if any(keyword in normalized for keyword in EXACT_KEYWORDS):
        return "Priorizar retomada de prerequisitos, resolucao guiada de exercicios e verificacao de lacunas conceituais."
    if any(keyword in normalized for keyword in LANGUAGE_KEYWORDS):
        return "Trabalhar leitura orientada, interpretacao, producao textual curta e devolutiva individual frequente."
    if any(keyword in normalized for keyword in HUMANITIES_KEYWORDS):
        return "Reforcar leitura de contexto, conexao entre conceitos e uso de resumos orientados com perguntas-chave."
    return "Aplicar reforco dirigido na habilidade central da disciplina e validar aprendizagem na etapa seguinte."


def _build_risk_reasons(row: pandas.Series) -> str:
    """Traduz sinais numéricos do registro em fatores de alerta legíveis."""
    reasons = []
    if float(row.get("predicted_next_grade", 10)) < 6.0:
        reasons.append("nota prevista abaixo da media de aprovacao")
    elif float(row.get("predicted_next_grade", 10)) < 7.0:
        reasons.append("nota prevista em faixa de atencao")
    if row.get("tendencia") == "queda":
        reasons.append("tendencia recente de queda")
    faltas_acumuladas = row.get("faltas_acumuladas")
    if not pandas.isna(faltas_acumuladas) and float(faltas_acumuladas) >= 8:
        reasons.append("faltas acumuladas elevadas")
    pagamentos_pendentes = row.get("pagamentos_pendentes_ano")
    if not pandas.isna(pagamentos_pendentes) and float(pagamentos_pendentes) >= 2:
        reasons.append("pendencias financeiras recorrentes")
    if float(row.get("ValorMedia", 10)) < 6.0:
        reasons.append("nota atual ja abaixo do esperado")
    if not reasons:
        reasons.append("desempenho dentro da normalidade com acompanhamento preventivo")
    return "; ".join(reasons)


def _build_teacher_recommendation(row: pandas.Series) -> str:
    """Gera a recomendação textual final do professor para um caso específico."""
    reasons = _build_risk_reasons(row)
    discipline_action = _discipline_support_action(row.get("NomeDisciplina"))
    if row["nivel_risco"] == "alto":
        return f"Intervencao imediata. Motivos: {reasons}. Acao pedagogica: {discipline_action}"
    if row["nivel_risco"] == "moderado":
        return f"Monitoramento reforcado. Motivos: {reasons}. Acao pedagogica: {discipline_action}"
    return f"Acompanhamento preventivo. Motivos: {reasons}. Acao pedagogica: {discipline_action}"


def _build_coordinator_recommendation(row: pandas.Series) -> str:
    """Gera o encaminhamento da coordenação para agrupamentos críticos."""
    if row["taxa_alto_risco"] >= 0.5:
        return "Planejar intervencao coletiva na disciplina, revisar estrategia docente e acompanhar turma em curto prazo."
    if row["casos_risco_moderado"] >= max(5, row["alunos_monitorados"] * 0.2):
        return "Monitorar a disciplina com professor e verificar se os casos estao concentrados em habilidades especificas."
    return "Manter acompanhamento de rotina e revisar novamente no proximo fechamento."


def _build_secretary_recommendation(row: pandas.Series) -> str:
    """Gera a ação administrativa sugerida para a secretaria."""
    actions = []
    if row["alerta_financeiro"] == 1:
        actions.append("validar historico financeiro e registrar contato preventivo")
    if row["alerta_frequencia"] == 1:
        actions.append("confirmar frequencia e alinhar comunicacao com a familia")
    if row["casos_alto_risco"] >= 3:
        actions.append("avisar coordenacao sobre volume de disciplinas em risco")
    if not actions:
        actions.append("manter acompanhamento administrativo regular")
    return "; ".join(actions).capitalize() + "."


def _calculate_risk_score(combined: pandas.DataFrame) -> pandas.Series:
    """Calcula uma pontuação composta de risco para priorização operacional.

    A pontuação combina:
    - risco previsto pelo classificador
    - nota prevista
    - nota atual
    - tendência de queda
    - faltas acumuladas
    - pendências financeiras
    """
    predicted_next_grade = combined["predicted_next_grade"].fillna(10)
    current_grade = combined["ValorMedia"].fillna(10)
    variation = combined["variacao_prevista"].fillna(0)
    absences = combined["faltas_acumuladas"].fillna(0)
    pending_payments = combined["pagamentos_pendentes_ano"].fillna(0)
    predicted_flag = combined["predicted_risk_flag"].fillna(0).astype(int)

    score = pandas.Series(0, index=combined.index, dtype="int64")
    score = score + numpy.where(predicted_flag == 1, 3, 0)
    score = score + numpy.where(
        predicted_next_grade < 5.0,
        3,
        numpy.where(predicted_next_grade < 6.0, 2, numpy.where(predicted_next_grade < 6.5, 1, 0)),
    )
    score = score + numpy.where(current_grade < 5.0, 2, numpy.where(current_grade < 6.0, 1, 0))
    score = score + numpy.where(variation <= -1.0, 2, numpy.where(variation <= -0.5, 1, 0))
    score = score + numpy.where(absences >= 10, 2, numpy.where(absences >= 8, 1, 0))
    score = score + numpy.where(pending_payments >= 3, 2, numpy.where(pending_payments >= 2, 1, 0))
    return score.astype(int)


def _build_executive_ranking_reason(row: pandas.Series) -> str:
    """Resume em texto por que o aluno entrou no ranking executivo."""
    reasons = []
    if row["casos_alto_risco"] >= 10:
        reasons.append("volume muito alto de disciplinas em alto risco")
    elif row["casos_alto_risco"] >= 5:
        reasons.append("multiplas disciplinas em alto risco")

    if row["pontuacao_risco_maxima"] >= 10:
        reasons.append("ha disciplinas com gravidade maxima muito elevada")
    elif row["pontuacao_risco_media"] >= 5:
        reasons.append("gravidade media elevada no conjunto das disciplinas")

    if row["faltas_acumuladas_maximas"] >= 10:
        reasons.append("faltas acumuladas em faixa critica")
    elif row["faltas_acumuladas_maximas"] >= 8:
        reasons.append("faltas acumuladas em faixa de alerta")

    if row["pagamentos_pendentes_maximos"] >= 3:
        reasons.append("pendencias financeiras recorrentes")
    elif row["pagamentos_pendentes_maximos"] >= 2:
        reasons.append("sinal financeiro que merece acompanhamento")

    if row["media_nota_prevista"] < 6:
        reasons.append("media prevista abaixo da linha de seguranca")

    if not reasons:
        reasons.append("caso relevante pelo conjunto de sinais moderados")

    return "; ".join(reasons)


def _build_executive_ranking_action(row: pandas.Series) -> str:
    """Define a ação sugerida da coordenação com base no índice de prioridade."""
    if row["indice_prioridade"] >= 18:
        return "Acionar coordenacao imediatamente, alinhar professores das disciplinas criticas e planejar contato com a familia nesta etapa."
    if row["indice_prioridade"] >= 12:
        return "Programar acompanhamento intensivo na coordenacao, revisar plano de apoio e monitorar fechamento da proxima etapa."
    return "Manter no radar da coordenacao com revisao breve e verificar se a situacao melhora no proximo fechamento."


def _prepare_combined_predictions(project_root: str | Path) -> pandas.DataFrame:
    """Cruza os resultados de previsao_nota e alerta_risco em uma única base operacional.

    Esse passo:
    - carrega as saídas dos dois modos
    - une as predições por chave escolar
    - reincorpora informações de faltas, pagamentos e professor
    - calcula pontuação de risco, nível de risco, tendência e recomendações
    """
    grade_predictions, _ = _load_mode_artifacts(project_root, "previsao_nota")
    risk_predictions, risk_dataset = _load_mode_artifacts(project_root, "alerta_risco")

    grade_predictions = grade_predictions.rename(
        columns={
            "predicted_next_grade": "predicted_next_grade_previsao",
            "predicted_risk_flag": "predicted_risk_flag_previsao",
            "absolute_error": "absolute_error_previsao",
            "signed_error": "signed_error_previsao",
            "risk_hit": "risk_hit_previsao",
            "selected_regression_candidate": "selected_regression_candidate_previsao",
            "selected_classification_candidate": "selected_classification_candidate_previsao",
        }
    )
    risk_predictions = risk_predictions.rename(
        columns={
            "predicted_next_grade": "predicted_next_grade_alerta",
            "predicted_risk_flag": "predicted_risk_flag_alerta",
            "absolute_error": "absolute_error_alerta",
            "signed_error": "signed_error_alerta",
            "risk_hit": "risk_hit_alerta",
            "selected_regression_candidate": "selected_regression_candidate_alerta",
            "selected_classification_candidate": "selected_classification_candidate_alerta",
        }
    )

    merge_columns = REPORT_KEY_COLUMNS + ["ValorMedia", "target_nota_proxima", "target_risco_proxima"]
    combined = risk_predictions.merge(
        grade_predictions,
        on=merge_columns,
        how="outer",
    )

    dataset_columns = [
        "IDAluno",
        "NomeCurso",
        "ApelidoTurma",
        "NomePeriodo",
        "NomeDisciplina",
        "NomeEtapa",
        "faltas_etapa",
        "faltas_acumuladas",
        "pagamentos_registrados_ano",
        "pagamentos_pendentes_ano",
        "proporcao_mensalidades_ano",
        "media_valor_pagamento_ano",
        "media_dias_ate_pagamento_ano",
        "NomeFuncionario",
        "quantidade_professores_disciplina",
        "professor_disponivel",
        "media_historica_disciplina",
        "media_historica_aluno_ano",
        "tendencia_ultima_nota",
    ]
    available_dataset_columns = [column for column in dataset_columns if column in risk_dataset.columns]
    combined = combined.merge(
        risk_dataset[available_dataset_columns].drop_duplicates(
            subset=["IDAluno", "NomePeriodo", "NomeDisciplina", "NomeEtapa"]
        ),
        on=["IDAluno", "NomePeriodo", "NomeDisciplina", "NomeEtapa"],
        how="left",
    )

    combined["predicted_next_grade"] = combined["predicted_next_grade_previsao"].fillna(combined["predicted_next_grade_alerta"])
    combined["predicted_risk_flag"] = (
        combined["predicted_risk_flag_alerta"]
        .fillna(combined["predicted_risk_flag_previsao"])
        .fillna(0)
        .astype(int)
    )
    combined["variacao_prevista"] = combined["predicted_next_grade"] - combined["ValorMedia"]
    combined["gap_para_meta_seis"] = 6.0 - combined["predicted_next_grade"]
    combined["NomeCurso"] = combined.get("NomeCurso", pandas.Series(dtype=str)).fillna("Curso não identificado")
    combined["ApelidoTurma"] = combined.get("ApelidoTurma", pandas.Series(dtype=str)).fillna("Turma não identificada")
    combined["professor_responsavel"] = (
        combined.get("NomeFuncionario", pandas.Series(dtype=str))
        .fillna("Professor não identificado ou não vinculado")
    )
    combined["professor_disponivel"] = (
        combined.get("professor_disponivel", pandas.Series(dtype="float64"))
        .fillna(0)
        .astype(int)
    )

    combined["pontuacao_risco"] = _calculate_risk_score(combined)
    high_risk_mask = combined["pontuacao_risco"] >= 7
    medium_risk_mask = (combined["pontuacao_risco"] >= 4) & (~high_risk_mask)
    combined["nivel_risco"] = numpy.select(
        [high_risk_mask, medium_risk_mask],
        ["alto", "moderado"],
        default="baixo",
    )

    combined["tendencia"] = numpy.select(
        [combined["variacao_prevista"] <= -0.5, combined["variacao_prevista"] >= 0.5],
        ["queda", "melhora"],
        default="estavel",
    )
    combined["alerta_frequencia"] = (combined["faltas_acumuladas"].fillna(0) >= 8).astype(int)
    combined["alerta_financeiro"] = (combined["pagamentos_pendentes_ano"].fillna(0) >= 2).astype(int)
    combined["fatores_alerta"] = combined.apply(_build_risk_reasons, axis=1)
    combined["recomendacao_professor"] = combined.apply(_build_teacher_recommendation, axis=1)
    combined["recomendacao_secretaria"] = numpy.select(
        [
            combined["alerta_financeiro"] == 1,
            combined["alerta_frequencia"] == 1,
        ],
        [
            "Verificar histórico financeiro e sinalizar coordenação para acompanhamento administrativo.",
            "Confirmar registros de frequência e apoiar contato preventivo com a família.",
        ],
        default="Sem ação administrativa imediata.",
    )

    risk_order = pandas.Categorical(combined["nivel_risco"], categories=["alto", "moderado", "baixo"], ordered=True)
    combined = combined.assign(_risk_order=risk_order).sort_values(
        ["_risk_order", "pontuacao_risco", "predicted_next_grade", "faltas_acumuladas"],
        ascending=[True, False, True, False],
        kind="stable",
    )
    return combined.drop(columns="_risk_order")


def _build_teacher_report(combined: pandas.DataFrame) -> pandas.DataFrame:
    """Extrai da base integrada apenas as colunas que interessam ao professor."""
    columns = [
        "NomePeriodo",
        "NomeSerie",
        "NomeDisciplina",
        "NomeEtapa",
        "professor_responsavel",
        "professor_disponivel",
        "NomeAluno",
        "ValorMedia",
        "predicted_next_grade",
        "variacao_prevista",
        "pontuacao_risco",
        "nivel_risco",
        "tendencia",
        "faltas_etapa",
        "faltas_acumuladas",
        "pagamentos_pendentes_ano",
        "fatores_alerta",
        "recomendacao_professor",
    ]
    teacher_report = combined[columns].copy()
    teacher_report = teacher_report.rename(
        columns={
            "ValorMedia": "nota_atual",
            "predicted_next_grade": "nota_prevista_proxima",
            "variacao_prevista": "variacao_prevista_nota",
        }
    )
    return teacher_report


def _build_coordinator_report(combined: pandas.DataFrame) -> pandas.DataFrame:
    """Agrupa a base integrada por série e disciplina para a coordenação."""
    student_group = (
        combined.groupby(["NomePeriodo", "NomeSerie", "NomeDisciplina", "IDAluno"], dropna=False)
        .agg(
            nivel_risco_aluno=("nivel_risco", lambda s: "alto" if (s == "alto").any() else ("moderado" if (s == "moderado").any() else "baixo")),
            nota_atual_media_aluno=("ValorMedia", "mean"),
            nota_prevista_media_aluno=("predicted_next_grade", "mean"),
            faltas_acumuladas_media_aluno=("faltas_acumuladas", "mean"),
            pendencias_financeiras_media_aluno=("pagamentos_pendentes_ano", "mean"),
            professores_disponiveis=("professor_disponivel", "max"),
        )
        .reset_index()
    )

    coordinator_report = (
        student_group.groupby(["NomePeriodo", "NomeSerie", "NomeDisciplina"], dropna=False)
        .agg(
            alunos_monitorados=("IDAluno", "nunique"),
            casos_alto_risco=("nivel_risco_aluno", lambda s: int((s == "alto").sum())),
            casos_risco_moderado=("nivel_risco_aluno", lambda s: int((s == "moderado").sum())),
            media_nota_atual=("nota_atual_media_aluno", "mean"),
            media_nota_prevista=("nota_prevista_media_aluno", "mean"),
            faltas_medias_acumuladas=("faltas_acumuladas_media_aluno", "mean"),
            pendencias_financeiras_medias=("pendencias_financeiras_media_aluno", "mean"),
            grupos_sem_professor_identificado=("professores_disponiveis", lambda s: int((s == 0).sum())),
        )
        .reset_index()
    )
    coordinator_report["taxa_alto_risco"] = coordinator_report["casos_alto_risco"] / coordinator_report["alunos_monitorados"]
    coordinator_report["recomendacao_coordenacao"] = coordinator_report.apply(_build_coordinator_recommendation, axis=1)
    coordinator_report = coordinator_report.sort_values(
        ["taxa_alto_risco", "casos_alto_risco", "faltas_medias_acumuladas"],
        ascending=[False, False, False],
        kind="stable",
    )
    return coordinator_report


def _build_teacher_risk_by_class_report(combined: pandas.DataFrame) -> pandas.DataFrame:
    """Resume risco por curso, série, turma e professor para uso da coordenação."""
    student_group = (
        combined.groupby(
            ["NomePeriodo", "NomeCurso", "NomeSerie", "ApelidoTurma", "professor_responsavel", "IDAluno"],
            dropna=False,
        )
        .agg(
            nivel_risco_aluno=("nivel_risco", lambda s: "alto" if (s == "alto").any() else ("moderado" if (s == "moderado").any() else "baixo")),
            professor_disponivel=("professor_disponivel", "max"),
        )
        .reset_index()
    )

    report = (
        student_group.groupby(
            ["NomePeriodo", "NomeCurso", "NomeSerie", "ApelidoTurma", "professor_responsavel"],
            dropna=False,
        )
        .agg(
            alunos_monitorados=("IDAluno", "nunique"),
            alunos_com_risco=("nivel_risco_aluno", lambda s: int(((s == "alto") | (s == "moderado")).sum())),
            casos_alto_risco=("nivel_risco_aluno", lambda s: int((s == "alto").sum())),
            casos_risco_moderado=("nivel_risco_aluno", lambda s: int((s == "moderado").sum())),
            casos_baixo_risco=("nivel_risco_aluno", lambda s: int((s == "baixo").sum())),
            professor_disponivel=("professor_disponivel", "max"),
        )
        .reset_index()
    )
    report["taxa_alunos_com_risco"] = report["alunos_com_risco"] / report["alunos_monitorados"]
    report = report.sort_values(
        ["alunos_com_risco", "casos_alto_risco", "casos_risco_moderado", "alunos_monitorados"],
        ascending=[False, False, False, False],
        kind="stable",
    )
    return report


def _build_teacher_risk_overall_report(combined: pandas.DataFrame) -> pandas.DataFrame:
    """Resume risco por professor independentemente da turma."""
    student_group = (
        combined.groupby(["NomePeriodo", "professor_responsavel", "IDAluno"], dropna=False)
        .agg(
            nivel_risco_aluno=("nivel_risco", lambda s: "alto" if (s == "alto").any() else ("moderado" if (s == "moderado").any() else "baixo")),
            professor_disponivel=("professor_disponivel", "max"),
        )
        .reset_index()
    )

    report = (
        student_group.groupby(["NomePeriodo", "professor_responsavel"], dropna=False)
        .agg(
            alunos_monitorados=("IDAluno", "nunique"),
            alunos_com_risco=("nivel_risco_aluno", lambda s: int(((s == "alto") | (s == "moderado")).sum())),
            casos_alto_risco=("nivel_risco_aluno", lambda s: int((s == "alto").sum())),
            casos_risco_moderado=("nivel_risco_aluno", lambda s: int((s == "moderado").sum())),
            casos_baixo_risco=("nivel_risco_aluno", lambda s: int((s == "baixo").sum())),
            professor_disponivel=("professor_disponivel", "max"),
        )
        .reset_index()
    )
    report["taxa_alunos_com_risco"] = report["alunos_com_risco"] / report["alunos_monitorados"]
    report = report.sort_values(
        ["alunos_com_risco", "casos_alto_risco", "casos_risco_moderado", "alunos_monitorados"],
        ascending=[False, False, False, False],
        kind="stable",
    )
    return report


def _build_secretary_report(combined: pandas.DataFrame) -> pandas.DataFrame:
    """Consolida sinais administrativos por aluno para a secretaria."""
    secretary_report = (
        combined.groupby(["IDAluno", "NomeAluno", "NomePeriodo", "NomeSerie"], dropna=False)
        .agg(
            disciplinas_monitoradas=("NomeDisciplina", "nunique"),
            casos_alto_risco=("nivel_risco", lambda s: int((s == "alto").sum())),
            faltas_acumuladas_maximas=("faltas_acumuladas", "max"),
            pagamentos_pendentes_maximos=("pagamentos_pendentes_ano", "max"),
            media_nota_prevista=("predicted_next_grade", "mean"),
            alerta_frequencia=("alerta_frequencia", "max"),
            alerta_financeiro=("alerta_financeiro", "max"),
        )
        .reset_index()
    )
    secretary_report["prioridade_secretaria"] = numpy.select(
        [
            (secretary_report["alerta_financeiro"] == 1) & (secretary_report["alerta_frequencia"] == 1),
            (secretary_report["alerta_financeiro"] == 1) | (secretary_report["alerta_frequencia"] == 1),
        ],
        ["alta", "media"],
        default="baixa",
    )
    secretary_report["recomendacao_secretaria"] = secretary_report.apply(_build_secretary_recommendation, axis=1)
    secretary_priority = pandas.Categorical(
        secretary_report["prioridade_secretaria"],
        categories=["alta", "media", "baixa"],
        ordered=True,
    )
    secretary_report = secretary_report.assign(_priority=secretary_priority)
    secretary_report = secretary_report.sort_values(
        ["_priority", "casos_alto_risco", "pagamentos_pendentes_maximos", "faltas_acumuladas_maximas"],
        ascending=[True, False, False, False],
        kind="stable",
    )
    return secretary_report.drop(columns="_priority")


def _build_executive_ranking(combined: pandas.DataFrame) -> pandas.DataFrame:
    """Monta o ranking executivo final da coordenação por aluno e período."""
    ranking = (
        combined.groupby(["IDAluno", "NomeAluno", "NomePeriodo", "NomeSerie"], dropna=False)
        .agg(
            disciplinas_monitoradas=("NomeDisciplina", "size"),
            disciplinas_distintas=("NomeDisciplina", "nunique"),
            casos_alto_risco=("nivel_risco", lambda s: int((s == "alto").sum())),
            casos_risco_moderado=("nivel_risco", lambda s: int((s == "moderado").sum())),
            pontuacao_risco_maxima=("pontuacao_risco", "max"),
            pontuacao_risco_media=("pontuacao_risco", "mean"),
            media_nota_atual=("ValorMedia", "mean"),
            media_nota_prevista=("predicted_next_grade", "mean"),
            pior_nota_prevista=("predicted_next_grade", "min"),
            faltas_acumuladas_maximas=("faltas_acumuladas", "max"),
            pagamentos_pendentes_maximos=("pagamentos_pendentes_ano", "max"),
            alerta_frequencia=("alerta_frequencia", "max"),
            alerta_financeiro=("alerta_financeiro", "max"),
        )
        .reset_index()
    )

    ranking["indice_prioridade"] = (
        ranking["casos_alto_risco"] * 3
        + ranking["casos_risco_moderado"] * 1
        + ranking["pontuacao_risco_maxima"]
        + numpy.where(ranking["media_nota_prevista"] < 5.0, 4, numpy.where(ranking["media_nota_prevista"] < 6.0, 2, 0))
        + numpy.where(ranking["faltas_acumuladas_maximas"].fillna(0) >= 10, 3, numpy.where(ranking["faltas_acumuladas_maximas"].fillna(0) >= 8, 2, 0))
        + numpy.where(ranking["pagamentos_pendentes_maximos"].fillna(0) >= 3, 3, numpy.where(ranking["pagamentos_pendentes_maximos"].fillna(0) >= 2, 2, 0))
    ).astype(int)

    ranking["nivel_prioridade_executiva"] = numpy.select(
        [
            ranking["indice_prioridade"] >= 18,
            ranking["indice_prioridade"] >= 12,
        ],
        ["critica", "alta"],
        default="moderada",
    )
    ranking["motivos_prioridade"] = ranking.apply(_build_executive_ranking_reason, axis=1)
    ranking["acao_executiva_sugerida"] = ranking.apply(_build_executive_ranking_action, axis=1)

    priority_order = pandas.Categorical(
        ranking["nivel_prioridade_executiva"],
        categories=["critica", "alta", "moderada"],
        ordered=True,
    )
    ranking = ranking.assign(_priority=priority_order).sort_values(
        ["_priority", "indice_prioridade", "casos_alto_risco", "pontuacao_risco_maxima", "faltas_acumuladas_maximas"],
        ascending=[True, False, False, False, False],
        kind="stable",
    )
    return ranking.drop(columns="_priority")


def _write_text_summaries(
    output_dir: Path,
    teacher_report: pandas.DataFrame,
    coordinator_report: pandas.DataFrame,
    teacher_risk_by_class_report: pandas.DataFrame,
    teacher_risk_overall_report: pandas.DataFrame,
    secretary_report: pandas.DataFrame,
    executive_ranking: pandas.DataFrame,
) -> None:
    """Gera versões .txt dos relatórios para leitura rápida e documentação."""
    teacher_lines = [
        "RELATORIO PARA PROFESSORES",
        "",
        "Objetivo: sinalizar alunos e disciplinas que exigem ajuste imediato de abordagem pedagógica.",
        "",
        "Casos prioritarios",
    ]
    for _, row in teacher_report.head(20).iterrows():
        teacher_lines.append(
            f"- {row['NomeAluno']} | {row['NomeSerie']} | {row['NomeDisciplina']} | etapa {row['NomeEtapa']} | nota atual={row['nota_atual']:.2f} | nota prevista={row['nota_prevista_proxima']:.2f} | risco={row['nivel_risco']} | pontuacao={int(row['pontuacao_risco'])} | tendencia={row['tendencia']} | faltas acumuladas={int(row['faltas_acumuladas']) if not pandas.isna(row['faltas_acumuladas']) else 0}"
        )
        teacher_lines.append(f"  Fatores de alerta: {row['fatores_alerta']}")
        teacher_lines.append(f"  Acao sugerida: {row['recomendacao_professor']}")

    coordinator_lines = [
        "RELATORIO PARA COORDENACAO",
        "",
        "Objetivo: identificar series e disciplinas que concentram maior risco pedagógico.",
        "",
        "Agrupamentos mais criticos",
    ]
    for _, row in coordinator_report.head(15).iterrows():
        coordinator_lines.append(
            f"- {row['NomePeriodo']} | {row['NomeSerie']} | {row['NomeDisciplina']} | alunos={int(row['alunos_monitorados'])} | alto risco={int(row['casos_alto_risco'])} | taxa alto risco={row['taxa_alto_risco']:.2%} | nota prevista media={row['media_nota_prevista']:.2f}"
        )
        coordinator_lines.append(f"  Encaminhamento: {row['recomendacao_coordenacao']}")

    coordinator_lines.extend([
        "",
        "Professores com mais alunos em risco por turma",
    ])
    for _, row in teacher_risk_by_class_report.head(15).iterrows():
        coordinator_lines.append(
            f"- {row['NomePeriodo']} | {row['NomeCurso']} | {row['NomeSerie']} | {row['ApelidoTurma']} | {row['professor_responsavel']} | alunos em risco={int(row['alunos_com_risco'])} | altos={int(row['casos_alto_risco'])} | moderados={int(row['casos_risco_moderado'])} | baixos={int(row['casos_baixo_risco'])}"
        )

    coordinator_lines.extend([
        "",
        "Professores com mais alunos em risco no periodo",
    ])
    for _, row in teacher_risk_overall_report.head(15).iterrows():
        coordinator_lines.append(
            f"- {row['NomePeriodo']} | {row['professor_responsavel']} | alunos em risco={int(row['alunos_com_risco'])} | altos={int(row['casos_alto_risco'])} | moderados={int(row['casos_risco_moderado'])} | baixos={int(row['casos_baixo_risco'])}"
        )

    secretary_lines = [
        "RELATORIO PARA SECRETARIA",
        "",
        "Objetivo: localizar alunos com sinais administrativos que podem exigir contato preventivo.",
        "",
        "Casos para acompanhamento",
    ]
    for _, row in secretary_report.head(20).iterrows():
        secretary_lines.append(
            f"- {row['NomeAluno']} | {row['NomeSerie']} | disciplinas={int(row['disciplinas_monitoradas'])} | prioridade={row['prioridade_secretaria']} | pendencias maximas={int(row['pagamentos_pendentes_maximos']) if not pandas.isna(row['pagamentos_pendentes_maximos']) else 0} | faltas maximas={int(row['faltas_acumuladas_maximas']) if not pandas.isna(row['faltas_acumuladas_maximas']) else 0} | nota prevista media={row['media_nota_prevista']:.2f}"
        )
        secretary_lines.append(f"  Encaminhamento: {row['recomendacao_secretaria']}")

    executive_lines = [
        "RANKING EXECUTIVO PARA COORDENACAO",
        "",
        "Objetivo: listar os alunos mais urgentes do periodo em uma unica visao priorizada.",
        "",
        "Casos mais urgentes",
    ]
    for _, row in executive_ranking.head(25).iterrows():
        executive_lines.append(
            f"- {row['NomeAluno']} | {row['NomeSerie']} | prioridade={row['nivel_prioridade_executiva']} | indice={int(row['indice_prioridade'])} | altos={int(row['casos_alto_risco'])} | moderados={int(row['casos_risco_moderado'])} | media prevista={row['media_nota_prevista']:.2f} | pior nota prevista={row['pior_nota_prevista']:.2f} | faltas maximas={int(row['faltas_acumuladas_maximas']) if not pandas.isna(row['faltas_acumuladas_maximas']) else 0} | pendencias maximas={int(row['pagamentos_pendentes_maximos']) if not pandas.isna(row['pagamentos_pendentes_maximos']) else 0}"
        )
        executive_lines.append(f"  Motivos: {row['motivos_prioridade']}")
        executive_lines.append(f"  Acao sugerida: {row['acao_executiva_sugerida']}")

    for filename, content in (
        ("relatorio_professor.txt", teacher_lines),
        ("relatorio_coordenacao.txt", coordinator_lines),
        ("relatorio_secretaria.txt", secretary_lines),
        ("ranking_executivo_coordenacao.txt", executive_lines),
    ):
        target = output_dir / filename
        ensure_parent_dir(target)
        target.write_text("\n".join(content), encoding="utf-8")


def build_school_reports(project_root: str | Path = ".") -> dict[str, Path]:
    """Gera toda a camada operacional de relatórios da escola.

    Saídas:
    - relatório do professor
    - relatório da coordenação
    - relatório da secretaria
    - ranking executivo
    - arquivo integrado que serve de base para dashboards e análises
    """
    project_paths = ProjectPaths.from_root(project_root)
    output_dir = project_paths.reports_artifacts_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    combined = _prepare_combined_predictions(project_paths.root)
    teacher_report = _build_teacher_report(combined)
    coordinator_report = _build_coordinator_report(combined)
    teacher_risk_by_class_report = _build_teacher_risk_by_class_report(combined)
    teacher_risk_overall_report = _build_teacher_risk_overall_report(combined)
    secretary_report = _build_secretary_report(combined)
    executive_ranking = _build_executive_ranking(combined)

    for filename, dataframe in (
        ("relatorio_escolar_integrado.csv", combined),
        ("relatorio_professor.csv", teacher_report),
        ("relatorio_coordenacao.csv", coordinator_report),
        ("relatorio_professores_por_turma.csv", teacher_risk_by_class_report),
        ("relatorio_professores_geral.csv", teacher_risk_overall_report),
        ("relatorio_secretaria.csv", secretary_report),
        ("ranking_executivo_coordenacao.csv", executive_ranking),
    ):
        dataframe.to_csv(output_dir / filename, index=False, encoding="utf-8")
    _write_text_summaries(
        output_dir,
        teacher_report,
        coordinator_report,
        teacher_risk_by_class_report,
        teacher_risk_overall_report,
        secretary_report,
        executive_ranking,
    )

    return {
        "integrado_csv": output_dir / "relatorio_escolar_integrado.csv",
        "professor_csv": output_dir / "relatorio_professor.csv",
        "professor_txt": output_dir / "relatorio_professor.txt",
        "coordenacao_csv": output_dir / "relatorio_coordenacao.csv",
        "coordenacao_txt": output_dir / "relatorio_coordenacao.txt",
        "professores_por_turma_csv": output_dir / "relatorio_professores_por_turma.csv",
        "professores_geral_csv": output_dir / "relatorio_professores_geral.csv",
        "secretaria_csv": output_dir / "relatorio_secretaria.csv",
        "secretaria_txt": output_dir / "relatorio_secretaria.txt",
        "ranking_executivo_csv": output_dir / "ranking_executivo_coordenacao.csv",
        "ranking_executivo_txt": output_dir / "ranking_executivo_coordenacao.txt",
    }
