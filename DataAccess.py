import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

def create_session():
    try:
        # Connection parameters
        #Warley
        database = "COLEGIO_TESTE"
        #server_name = "DESKTOP-ESQU4CF\\SQLEXPRESS"
        server_name = "WARLEY\\PRISMA"
        username = "sa"
        password = "10203040"
        # server_name = "localhost"
        # password = "dockerPwd123"

        # Create connection string
        connection_string = f"mssql+pyodbc://{username}:{password}@{server_name}/{database}?driver=SQL+Server"
        # connection_string = f"mssql+pyodbc://{username}:{password}@{server_name}/{database}?driver=ODBC Driver 18 for SQL Server&TrustServerCertificate=yes"

        # Create an SQLAlchemy engine
        engine = sa.create_engine(connection_string)

        # Create a session class
        session = sessionmaker(bind=engine)

        return session()
    except Exception as e:
        print("Error occurred while creating session:", e)
        return None

session = create_session()
if not session:
    print("Failed to create session.")