"""
Arquivo de referência para a camada privada local.

Copie este arquivo para:
    school_predictor/database/private_runtime.py

Esse arquivo local deve permanecer fora do Git e concentrar:
1. a preparação física do banco restaurado
2. a extração dos CSVs com qualquer tratamento sensível necessário

O repositório público mantém apenas os wrappers e o contrato das entradas.
"""


def prepare_private_database(user: str = "Warley", source_database: str | None = None) -> str:
    raise NotImplementedError(
        "Implemente aqui a rotina local de renomeação, limpeza, anonimização e otimização do banco."
    )


def extract_private_school_data(
    session,
    project_root=".",
    student_name=None,
    academic_period=None,
    specific=False,
):
    raise NotImplementedError(
        "Implemente aqui a extração local de CSVs e os tratamentos necessários dos dados sensíveis."
    )
