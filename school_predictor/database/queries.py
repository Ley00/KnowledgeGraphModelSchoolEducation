import re

from sqlalchemy import text

from school_predictor.database.query_loader import load_private_query


def _extract_row_params(query: str, row) -> dict:
    placeholders = set(re.findall(r":(\w+)", query))
    return {column: row[column] for column in placeholders if column in row}


def _append_filters(base_query: str, filters: list[str]) -> str:
    query = base_query.strip()
    if not filters:
        return query
    return f"{query}\nWHERE 1=1\n    " + "\n    ".join(filters)


def get_student(has_where, student_name=None, academicperiod=None):
    """Carrega localmente a consulta privada de alunos e injeta filtros opcionais."""
    query = load_private_query("get_student")

    filters = []
    if has_where:
        if student_name:
            filters.append("AND Alunos.NomeAluno = :student_name")
        if academicperiod:
            filters.append("AND PeriodosLetivos.NomePeriodo = :academicperiod")

    query = _append_filters(query, filters)
    query += """
ORDER BY
    Unidades.NomeUnidade,
    Cursos.NomeCurso,
    PeriodosLetivos.NomePeriodo,
    Series.NomeSerie,
    Turmas.ApelidoTurma,
    Alunos.NomeAluno
"""
    return text(query)


def get_student_averages(row):
    query = load_private_query("get_student_averages")
    return text(query), _extract_row_params(query, row)


def get_paid_student(row):
    query = load_private_query("get_paid_student")
    return text(query), _extract_row_params(query, row)


def get_student_guardians(row):
    query = load_private_query("get_student_guardians")
    return text(query), _extract_row_params(query, row)


def get_student_absences(row):
    query = load_private_query("get_student_absences")
    return text(query), _extract_row_params(query, row)


def get_teacher_assignments(row):
    query = load_private_query("get_teacher_assignments")
    return text(query), _extract_row_params(query, row)
