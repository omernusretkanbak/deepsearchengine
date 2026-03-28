import os
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from core.orchestrator import run
from core.utils.schemas import DeepSearchOutput

router = APIRouter()

_KEY = os.environ.get("N8N_WEBHOOK_API_KEY", "")


def _auth(x_api_key: str = Header(default="")):
    if not _KEY or x_api_key != _KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


class WebhookPayload(BaseModel):
    query: str


@router.post("/webhook/trigger", response_model=DeepSearchOutput)
async def trigger(
    body: WebhookPayload,
    x_api_key: str = Header(default=""),
) -> DeepSearchOutput:
    _auth(x_api_key)
    if not body.query.strip():
        raise HTTPException(status_code=422, detail="query cannot be empty")
    return await run(body.query)
