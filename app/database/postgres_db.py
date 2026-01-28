from agno.db.postgres import PostgresDb
from app.config.settings import settings

def get_postgres_db():
    return PostgresDb(
        id="my_agent_db",
        db_url=settings.POSTGRES_URL,
    )

def get_postgres_db_dummy_data():
    return PostgresDb(
        id="my_agent_db",
        db_url=settings.POSTGRES_URL_DUMMY_DATA,
    )