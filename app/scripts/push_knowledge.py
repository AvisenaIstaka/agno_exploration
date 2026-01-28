import os
from dotenv import load_dotenv
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.qdrant import Qdrant
from agno.knowledge.reader.website_reader import WebsiteReader
from agno.knowledge.reader.text_reader import TextReader
from agno.knowledge.chunking.semantic import SemanticChunking
from agno.knowledge.embedder.openai import OpenAIEmbedder

load_dotenv()

# Config
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")

# Initialize vector DB
vector_db = Qdrant(
    collection=COLLECTION_NAME,
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    embedder=OpenAIEmbedder(
        id="text-embedding-3-small",
        dimensions=1536
    ),
)

# Create knowledge base
knowledge = Knowledge(vector_db=vector_db)

# Semantic chunking config (reusable)
semantic_chunker = SemanticChunking(
    chunk_size=600,
    similarity_threshold=0.6,
)

# Add website content
try:
    print("📥 Adding website content...")
    knowledge.add_content(
        url="https://houpe.id/",
        reader=WebsiteReader(chunking_strategy=semantic_chunker),
        metadata={
            "source": "web",
            "title": "houpe_homepage",
            "category": "company_info",
        }
    )
    print("✅ Website content added")
except Exception as e:
    print(f"❌ Error adding website: {e}")

# Add text file content
try:
    print("📥 Adding text file content...")
    knowledge.add_content(
        path="docs/info_houpe.txt",
        reader=TextReader(chunking_strategy=semantic_chunker),
        metadata={
            "source": "text",
            "title": "houpe_info",
            "category": "documentation",
        }
    )
    print("✅ Text file content added")
except Exception as e:
    print(f"❌ Error adding text file: {e}")

# IMPORTANT: Load/index to Qdrant
try:
    print("🚀 Loading knowledge to Qdrant...")
    knowledge.load(recreate=False)  # set True untuk hapus data lama
    print("✅ Knowledge base loaded successfully!")
except Exception as e:
    print(f"❌ Error loading knowledge: {e}")
