import os
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from core.orchestrator import run
from core.utils.schemas import DeepSearchOutput
from microservice_api.auth import require_bearer

router = APIRouter()


class SearchRequest(BaseModel):
    query:       str
    max_results: int = 15


@router.post("/search", response_model=DeepSearchOutput, dependencies=[Depends(require_bearer)])
async def search(body: SearchRequest) -> DeepSearchOutput:
    if not body.query.strip():
        raise HTTPException(status_code=422, detail="query cannot be empty")
    return await run(body.query)
