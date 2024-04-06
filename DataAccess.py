import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

def create_session():
    try:
        # Connection parameters
        database = "COLEGIO_TESTE"
        server_name = "DESKTOP-ESQU4CF\\SQLEXPRESS"
        username = "sa"
        password = "10203040"

        # Create connection string
        connection_string = f"mssql+pyodbc://{username}:{password}@{server_name}/{database}?driver=SQL+Server"

        # Create an SQLAlchemy engine
        engine = sa.create_engine(connection_string)

        # Create a session class
        Session = sessionmaker(bind=engine)

        return Session()
    except Exception as e:
        print("Error occurred while creating session:", e)
        return None

session = create_session()
if session:
    print("Session created successfully.")
else:
    print("Failed to create session.")
