from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from school_predictor.database.access import create_session
from school_predictor.database.extraction import extract_school_data
from school_predictor.database.maintenance import prepare_updated_database
from school_predictor.pipeline.orchestration import run_full_reporting_pipeline, run_real_pipeline


def extract_school_data_from_database(
    user: str = "default",
    project_root: str | Path = ".",
    student_name: str | None = None,
    academic_period: str | None = None,
    specific: bool = False,
) -> None:
    """Extrai os CSVs base a partir do banco configurado no ambiente local."""
    session = create_session(user)
    if session is None:
        raise RuntimeError("Nao foi possivel criar a sessao com o banco de dados.")

    try:
        try:
            session.execute(text("SELECT 1"))
        except SQLAlchemyError as error:
            raise RuntimeError(
                "Nao foi possivel conectar ao SQL Server para iniciar a extração. "
                "Verifique se o banco esta online, se a porta configurada responde "
                "e se as credenciais do .env estao corretas."
            ) from error

        extract_school_data(
            session=session,
            project_root=project_root,
            student_name=student_name,
            academic_period=academic_period,
            specific=specific,
        )
    finally:
        session.close()


def run_default_workflow(project_root: str | Path = ".") -> dict:
    """Executa a pipeline principal do TCC com geração dos relatórios finais."""
    return run_full_reporting_pipeline(project_root=project_root)
