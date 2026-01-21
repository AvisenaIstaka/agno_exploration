import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.qdrant import Qdrant
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.reader.website_reader import WebsiteReader
from agno.knowledge.chunking.fixed import FixedSizeChunking
from agno.knowledge.chunking.semantic import SemanticChunking
from qdrant_client import QdrantClient
from qdrant_client.http import models
from agno.knowledge.embedder.openai import OpenAIEmbedder


load_dotenv()

api_key = os.getenv("QDRANT_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
COLLECTION_NAME = "agent-knowledge"

vector_db = Qdrant(
    collection=COLLECTION_NAME,
    url=qdrant_url,
    embedder=OpenAIEmbedder(
        id="text-embedding-3-small",
        dimensions=1536  # Explicitly set
    ),
    api_key=api_key, # (optional)
)

# Create a knowledge base with Qdrant
knowledge = Knowledge(
    vector_db=vector_db,
    max_results=4
)

# client = QdrantClient(
#     url=qdrant_url,
#     api_key=api_key
# )

# client.create_payload_index(
#     collection_name="agent-knowledge",
#     field_name="content_hash",
#     field_schema=models.PayloadSchemaType.KEYWORD
# )

# print("content_hash index created")

# Add content to the knowledge base
# knowledge.add_content(
#     url="https://www.ds-inovasi.com/",
#     reader=WebsiteReader(
#         chunking_strategy=SemanticChunking(
#             chunk_size=600,
#             similarity_threshold=0.6,
#         )
#     ),
#     metadata={
#         "source": "web",
#         "title": "dutasaranainovasi"
#     }
# )