from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "agent-knowledge"

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# Delete all points but keep collection & indexes
client.delete(
    collection_name=COLLECTION_NAME,
    points_selector=models.Filter(
        must=[]  # empty filter = match all
    )
)

print(f"All points deleted from collection '{COLLECTION_NAME}' (collection preserved)")
