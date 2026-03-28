"""
Unified entry point.

Usage:
  python run.py              → start API server (port 8000)
  python run.py --test       → run a test query and print JSON
"""

import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from microservice_api.routes import router as api_router
from n8n_webhook.routes import router as n8n_router

app = FastAPI(
    title="Child-Safe Search Ecosystem",
    description="Full-spectrum YouTube Shorts market intelligence for 4-12yo.",
    version="1.0.0",
)

app.include_router(api_router)
app.include_router(n8n_router)


if __name__ == "__main__":
    if "--test" in sys.argv:
        from core.orchestrator import run
        query = " ".join(sys.argv[2:]) or "viral YouTube Shorts kids 2025"
        print(f"\n[TEST] Query: {query}\n")
        result = asyncio.run(run(query))
        print(result.model_dump_json(indent=2))
    else:
        import os
        import uvicorn
        port = int(os.getenv("PORT", "8080"))

        print(f"[START] Listening on http://0.0.0.0:{port}")
        uvicorn.run("run:app", host="0.0.0.0", port=port, reload=False)
