import os
import sys
from agno.knowledge.reader.website_reader import WebsiteReader
from agno.knowledge.chunking.semantic import SemanticChunking
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from knowledge.knowledge_base import get_knowledge

knowledge = get_knowledge()

def ingest_website(url: str, metadata: dict):
    knowledge.add_content(
    url=url,
    reader=WebsiteReader(chunking_strategy=SemanticChunking(
        chunk_size=600,
        similarity_threshold=0.5,
    )),
    metadata=metadata or {}
)

