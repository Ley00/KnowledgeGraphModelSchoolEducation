import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import os

# Criar a string de conexão
database = "COLEGIO_TESTE"
#Usuário
#Warley
server_name = "DESKTOP-ESQU4CF\\SQLEXPRESS"
username = "sa"
password = "10203040"

#Lucas
#server_name = "DESKTOP-ESQU4CF\\SQLEXPRESS"
#username = "sa"
#password = "10203040"

connection_string = f"mssql+pyodbc://{username}:{password}@{server_name}/{database}?driver=ODBC+Driver+19+for+SQL+Server"


# Criar uma sessão do SQLAlchemy
engine = sa.create_engine(connection_string)
session = sessionmaker(bind=engine)()