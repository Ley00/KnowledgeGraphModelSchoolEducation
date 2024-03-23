import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker


# Criar a string de conexão
database = "COLEGIO_TESTE"
server_name = "DESKTOP-ESQU4CF\\SQLEXPRESS"
username = "sa"
password = "10203040"

connection_string = f"mssql+pyodbc://{username}:{password}@{server_name}/{database}?driver=SQL+Server"

# Criar uma sessão do SQLAlchemy
engine = sa.create_engine(connection_string)
Session = sessionmaker(bind=engine)

def criar_sessao():
    return Session()
