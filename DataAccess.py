import os
import platform
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

#Link para baixar o banco de dados COLEGIO_TESTE.bak no tipo SQL Server
#https://1drv.ms/u/c/b0edc5d73af501e3/EfjFh-3O1gZJnL9n7upjOoABLV5-rbsM2ozDXGGE7k_U8A?e=juhoPe

# Configurações de conexão com o banco de dados
connections = {
    "Warley": {
        "driver": "ODBC Driver 18 for SQL Server",
        "database": "COLEGIO_TESTE",
        "server_name": "127.0.0.1",
        "port": "1433",
        "username": os.getenv("DB_USER_WARLEY", "sa"),
        "password": os.getenv("DB_PASS_WARLEY", "Prism@1020")
    }
}


def get_connection_params(user):
    connection_params = connections.get(user)
    if not connection_params:
        raise ValueError(f"Usuário '{user}' não encontrado nas configurações.")
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

# Cria sessão com o banco de dados SQL Server
def create_session(user):
    try:
        engine = create_engine(user)
        Session = sessionmaker(bind=engine)
        return Session()

    except Exception as e:
        print(f"Erro ao criar a sessão para o usuário {user}: {e}")
        return None
