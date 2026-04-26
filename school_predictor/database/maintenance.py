def prepare_updated_database(user: str = "Warley", source_database: str | None = None) -> str:
    """Wrapper público para a preparação física privada do banco local."""
    try:
        from school_predictor.database.private_runtime import prepare_private_database
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "Camada privada de manutenção do banco não encontrada. Crie o arquivo local "
            "`school_predictor/database/private_runtime.py` antes de executar `prepare-db`."
        ) from error

    return prepare_private_database(user=user, source_database=source_database)
