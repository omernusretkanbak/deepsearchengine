import os
from fastapi import Header, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer()
_TOKEN  = os.environ.get("MICROSERVICE_BEARER_TOKEN", "")


async def require_bearer(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
) -> None:
    if not _TOKEN or credentials.credentials != _TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
