import os
import platform
from urllib.parse import quote_plus

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from school_predictor.project import DEFAULT_PATHS



def load_project_env():
    """Carrega variaveis de ambiente do arquivo .env sem depender de bibliotecas externas."""
    env_path = DEFAULT_PATHS.env_file
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_project_env()

def get_connection_params(user):
    connection_params = {
        "driver": os.getenv("DB_DRIVER"),
        "database": os.getenv("DB_NAME"),
        "server_name": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "username": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
    }

    env_names = {
        "driver": "DB_DRIVER",
        "database": "DB_NAME",
        "server_name": "DB_HOST",
        "port": "DB_PORT",
        "username": "DB_USER",
        "password": "DB_PASS",
    }
    missing_fields = [field for field, value in connection_params.items() if not value]
    if missing_fields:
        missing_variables = [env_names[field] for field in missing_fields]
        raise ValueError(
            "Configuracao do banco nao encontrada. Defina as variaveis de ambiente "
            f"{', '.join(missing_variables)} em um arquivo .env local ou no sistema."
        )

    return connection_params


def build_connection_string(user, database_override=None):
    connection_params = get_connection_params(user)

    driver = connection_params["driver"]
    database = database_override or connection_params["database"]
    server_name = connection_params["server_name"]
    port = connection_params["port"]
    username = connection_params["username"]
    password = connection_params["password"]
    password_escaped = quote_plus(password)

    if platform.system() == "Darwin":
        return (
            f"mssql+pyodbc://{username}:{password_escaped}@{server_name},{port}/{database}"
            f"?driver={quote_plus(driver)}&TrustServerCertificate=yes&Encrypt=no"
        )
    if platform.system() == "Windows":
        return (
            f"mssql+pyodbc://{username}:{password_escaped}@{server_name},{port}/{database}"
            f"?driver={quote_plus(driver)}&TrustServerCertificate=yes"
        )
    raise OSError("Sistema operacional não suportado para esta conexão.")


def create_engine(user, database_override=None, echo=False):
    connection_string = build_connection_string(user, database_override=database_override)
    return sa.create_engine(connection_string, echo=echo)


def create_session(user):
    """Cria uma sessao SQLAlchemy usando as credenciais carregadas do ambiente local."""
    try:
        engine = create_engine(user)
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        print(f"Erro ao criar a sessão para o usuário {user}: {e}")
        return None
