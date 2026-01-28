import os
import sys
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pipelines.ingestion_pipeline import ingest_website

router = APIRouter()

class IngestRequest(BaseModel):
    url: str
    metadata: Optional[Dict[str, str]] = {}

@router.post("/insert_knowledge_by_website_url")
def ingest_knowledge(payload: IngestRequest):
    try:
        ingest_website(payload.url, payload.metadata)
        return {"status": "success", "url": payload.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
