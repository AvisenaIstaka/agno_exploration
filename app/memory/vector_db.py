from agno.vectordb.qdrant import Qdrant
from agno.knowledge.embedder.openai import OpenAIEmbedder
from app.config.settings import settings


def get_vector_db():
    return Qdrant(
        collection=settings.QDRANT_COLLECTION_NAME,
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        embedder=OpenAIEmbedder(
            id="text-embedding-3-small",
            dimensions=1536,
        ),
    )
