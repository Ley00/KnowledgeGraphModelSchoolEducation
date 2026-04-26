from pathlib import Path


def _load_private_runtime():
    try:
        from school_predictor.database.private_runtime import extract_private_school_data
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "Camada privada de extração não encontrada. Crie o arquivo local "
            "`school_predictor/database/private_runtime.py` a partir do contrato "
            "documentado em docs/ENTRADA_DE_DADOS_E_CONTRATOS.md."
        ) from error

    return extract_private_school_data


def extract_school_data(
    session,
    project_root: str | Path = ".",
    student_name: str | None = None,
    academic_period: str | None = None,
    specific: bool = False,
):
    """Wrapper público para a extração privada local de CSVs."""
    runner = _load_private_runtime()
    return runner(
        session=session,
        project_root=project_root,
        student_name=student_name,
        academic_period=academic_period,
        specific=specific,
    )


def process_data(session, manager, student_name, academicperiod, specific):
    """Compatibilidade mínima com fluxos antigos, delegando à camada privada local."""
    return extract_school_data(
        session=session,
        project_root=".",
        student_name=student_name,
        academic_period=academicperiod,
        specific=specific,
    )
