from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    QDRANT_API_KEY: str
    QDRANT_URL: str
    QDRANT_COLLECTION_NAME: str = "agent-knowledge"

    RUNPOD_MODEL_NAME: str | None = None
    RUNPOD_BASE_URL: str | None = None
    RUNPOD_API_KEY: str | None = None

    POSTGRES_URL: str = "postgresql://agno_user:admin@localhost:5432/agno_db"
    POSTGRES_URL_DUMMY_DATA: str = "postgresql://agno_user:admin@localhost:5432/dummy_data"

settings = Settings()
