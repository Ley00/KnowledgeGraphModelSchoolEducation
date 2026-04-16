from pathlib import Path

from TCCPipeline.config import PipelinePaths
from TCCPipeline.data import load_source_tables
from TCCPipeline.dataset import build_prediction_dataset, select_model_columns
from TCCPipeline.modeling import save_artifacts, train_and_evaluate, write_report
from TCCPipeline.reporting import build_school_reports


MODE_DEFAULTS = {
    "previsao_nota": {
        "min_history": 1,
    },
    "alerta_risco": {
        "min_history": 2,
    },
}


def resolve_mode_settings(mode: str, min_history: int | None) -> tuple[str, int]:
    """Resolve o modo solicitado e define o histórico mínimo padrão quando ele não é informado."""
    if mode not in MODE_DEFAULTS:
        raise ValueError(f"Modo inválido: {mode}. Use 'previsao_nota' ou 'alerta_risco'.")

    resolved_history = MODE_DEFAULTS[mode]["min_history"] if min_history is None else min_history
    return mode, resolved_history


def run_real_pipeline(project_root: str | Path = ".", min_history: int | None = None, mode: str = "previsao_nota") -> dict:
    """Executa uma pipeline completa para um único objetivo.

    Fluxo:
    1. resolve o modo e o min_history
    2. carrega os CSVs de origem
    3. constrói o dataset temporal de modelagem
    4. seleciona as colunas que entram no modelo
    5. treina, valida e testa os candidatos
    6. salva artefatos e relatório técnico do modo
    """
    mode, min_history = resolve_mode_settings(mode, min_history)
    paths = PipelinePaths.from_project_root(project_root, min_history=min_history, mode=mode)
    source_tables = load_source_tables(paths)
    dataset = build_prediction_dataset(source_tables, min_history=min_history)
    feature_columns, categorical_columns = select_model_columns(dataset)
    training_output = train_and_evaluate(dataset, feature_columns, categorical_columns)

    save_artifacts(paths, dataset, training_output)
    write_report(paths, dataset, training_output)

    return {
        "paths": paths,
        "mode": mode,
        "dataset": dataset,
        "metrics": training_output["metrics"],
        "predictions": training_output["predictions"],
    }


def run_full_reporting_pipeline(project_root: str | Path = ".") -> dict:
    """Função é a principal porta de entrada do projeto.
    Ela roda os dois modos técnicos da pipeline e, ao final,
    consolida os resultados em relatórios operacionais para a escola.
    """
    grade_output = run_real_pipeline(project_root=project_root, mode="previsao_nota")
    risk_output = run_real_pipeline(project_root=project_root, mode="alerta_risco")
    school_reports = build_school_reports(project_root=project_root)
    return {
        "previsao_nota": grade_output,
        "alerta_risco": risk_output,
        "school_reports": school_reports,
    }
