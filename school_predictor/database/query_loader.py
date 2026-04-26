import os
from pathlib import Path

from school_predictor.database.access import load_project_env


load_project_env()


PRIVATE_SQL_ENV = "SCHOOL_PREDICTOR_SQL_DIR"
DEFAULT_PRIVATE_SQL_DIR = Path(__file__).resolve().parent / "private_sql"

QUERY_FILE_MAP = {
    "get_student": "get_student.sql",
    "get_student_averages": "get_student_averages.sql",
    "get_paid_student": "get_paid_student.sql",
    "get_student_guardians": "get_student_guardians.sql",
    "get_student_absences": "get_student_absences.sql",
    "get_teacher_assignments": "get_teacher_assignments.sql",
    "database_preparation": "database_preparation.sql",
}


def get_private_sql_dir() -> Path:
    override = os.getenv(PRIVATE_SQL_ENV)
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_PRIVATE_SQL_DIR


def load_private_query(query_name: str) -> str:
    if query_name not in QUERY_FILE_MAP:
        raise KeyError(f"Consulta privada desconhecida: {query_name}")

    sql_dir = get_private_sql_dir()
    sql_path = sql_dir / QUERY_FILE_MAP[query_name]
    if not sql_path.exists():
        raise FileNotFoundError(
            "Consulta SQL privada nao encontrada em "
            f"{sql_path}. Mantenha as consultas locais fora do Git e siga a "
            "documentacao publica de contrato em docs/ENTRADA_DE_DADOS_E_CONTRATOS.md."
        )

    query = sql_path.read_text(encoding="utf-8").strip()
    if not query:
        raise ValueError(f"Consulta SQL privada vazia: {sql_path}")

    return query
