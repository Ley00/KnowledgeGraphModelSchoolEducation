import re
from typing import Any

import pandas


STAGE_PATTERN = re.compile(r"(\d+)")


def parse_stage_order(stage_name: Any) -> float:
    """Extrai a ordem numérica da etapa a partir do texto.

    Exemplos:
    - "1º BIMESTRE" -> 1
    - "3 ETAPA" -> 3
    """
    if pandas.isna(stage_name):
        return pandas.NA

    match = STAGE_PATTERN.search(str(stage_name))
    return int(match.group(1)) if match else pandas.NA


def coerce_bool(series: pandas.Series) -> pandas.Series:
    """Converte colunas booleanas heterogêneas para o tipo boolean do pandas."""
    normalized = (
        series.astype(str)
        .str.strip()
        .str.lower()
        .replace(
            {
                "true": True,
                "false": False,
                "1": True,
                "0": False,
                "sim": True,
                "nao": False,
                "não": False,
                "nan": pandas.NA,
                "none": pandas.NA,
                "null": pandas.NA,
            }
        )
    )
    return normalized.astype("boolean")


def read_csv(path) -> pandas.DataFrame:
    """Leitura padronizada de CSV para toda a pipeline."""
    return pandas.read_csv(path, encoding="utf-8", low_memory=False)


def load_source_tables(paths) -> dict[str, pandas.DataFrame]:
    """Carrega as tabelas-base que alimentam a pipeline.

    O arquivo de professor é opcional porque a base atual pode não ter sido
    extraída com esse vínculo preservado.
    """
    teachers = read_csv(paths.teachers_csv) if paths.teachers_csv.exists() else pandas.DataFrame()
    return {
        "grades": read_csv(paths.grades_csv),
        "absences": read_csv(paths.absences_csv),
        "payments": read_csv(paths.payments_csv),
        "teachers": teachers,
    }


def prepare_grades(df: pandas.DataFrame) -> pandas.DataFrame:
    """Normaliza e ordena a base de notas.

    Esse passo garante que o histórico do aluno fique em ordem temporal
    por ano, disciplina e etapa antes da construção dos atributos.
    """
    grades = df.copy()
    grades["ValorMedia"] = pandas.to_numeric(grades["ValorMedia"], errors="coerce")
    grades["NomePeriodo"] = pandas.to_numeric(grades["NomePeriodo"], errors="coerce")
    grades["stage_order"] = grades["NomeEtapa"].apply(parse_stage_order)
    grades = grades.dropna(subset=["IDAluno", "NomeDisciplina", "NomePeriodo", "stage_order", "ValorMedia"])
    grades["NomePeriodo"] = grades["NomePeriodo"].astype(int)
    grades["stage_order"] = grades["stage_order"].astype(int)
    grades = grades.sort_values(
        by=["IDAluno", "NomePeriodo", "NomeDisciplina", "stage_order", "NomeEtapa"],
        kind="stable",
    ).reset_index(drop=True)
    return grades


def prepare_absences(df: pandas.DataFrame) -> pandas.DataFrame:
    """Normaliza a base de faltas para integração com as notas."""
    absences = df.copy()
    absences["NomePeriodo"] = pandas.to_numeric(absences["NomePeriodo"], errors="coerce")
    absences["stage_order"] = absences["NomeEtapa"].apply(parse_stage_order)
    absences["DataFalta"] = pandas.to_datetime(absences["DataFalta"], errors="coerce")
    absences = absences.dropna(subset=["IDAluno", "NomeDisciplina", "NomePeriodo", "stage_order"])
    absences["NomePeriodo"] = absences["NomePeriodo"].astype(int)
    absences["stage_order"] = absences["stage_order"].astype(int)
    return absences


def prepare_payments(df: pandas.DataFrame) -> pandas.DataFrame:
    """Normaliza a base financeira e calcula o atraso/antecipação do pagamento."""
    payments = df.copy()
    payments["NomePeriodo"] = pandas.to_numeric(payments["NomePeriodo"], errors="coerce")
    payments["DataAntecipadoMovimento"] = pandas.to_datetime(payments["DataAntecipadoMovimento"], errors="coerce")
    payments["DataVencimentoMovimento"] = pandas.to_datetime(payments["DataVencimentoMovimento"], errors="coerce")
    payments["ValorMovimento"] = pandas.to_numeric(payments["ValorMovimento"], errors="coerce")
    payments["ValorPagoMovimento"] = pandas.to_numeric(payments["ValorPagoMovimento"], errors="coerce")
    payments["PagoMovimento"] = coerce_bool(payments["PagoMovimento"])
    payments["EhMensalidadeMovimento"] = coerce_bool(payments["EhMensalidadeMovimento"])
    payments = payments.dropna(subset=["IDAluno", "NomePeriodo"])
    payments["NomePeriodo"] = payments["NomePeriodo"].astype(int)

    delay = (payments["DataAntecipadoMovimento"] - payments["DataVencimentoMovimento"]).dt.days
    payments["dias_ate_pagamento"] = delay
    return payments


def prepare_teachers(df: pandas.DataFrame) -> pandas.DataFrame:
    """Resume os vínculos de professor por unidade, período, curso e disciplina.

    Quando há mais de um professor na mesma disciplina, os nomes são consolidados
    em uma única string e também é criada a quantidade de professores envolvidos.
    """
    if df is None or df.empty:
        return pandas.DataFrame(
            columns=[
                "IDUnidade", "IDPeriodo", "IDCurso", "IDDisciplina", "NomeFuncionario", "quantidade_professores_disciplina"
            ]
        )

    teachers = df.copy()
    teachers["IDUnidade"] = teachers["IDUnidade"].astype(str)
    teachers["IDPeriodo"] = teachers["IDPeriodo"].astype(str)
    teachers["IDCurso"] = teachers["IDCurso"].astype(str)
    teachers["IDDisciplina"] = teachers["IDDisciplina"].astype(str)

    grouped = (
        teachers.groupby(["IDUnidade", "IDPeriodo", "IDCurso", "IDDisciplina"], dropna=False)
        .agg(
            NomeFuncionario=("NomeFuncionario", lambda s: " | ".join(sorted(set(str(value) for value in s if pandas.notna(value))))),
            quantidade_professores_disciplina=("IDFuncionario", "nunique"),
        )
        .reset_index()
    )
    return grouped
