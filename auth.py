from fastapi import Security, HTTPException, status, Request
from fastapi.security import APIKeyHeader
from routers.public_utils import get_user, AUTH_STATUS


api_key_header = APIKeyHeader(name="X-API-KEY")

def auth_user(api_key_header: str = Security(api_key_header), request: Request):
    status = get_user(api_key_header, request.app.state.db)
    if status == AUTH_STATUS.GRANTED:
        return True

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API Key"
        )
