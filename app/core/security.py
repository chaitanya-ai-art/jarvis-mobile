from __future__ import annotations

import secrets
from fastapi import Cookie, Header, HTTPException, Query, status

from app.core.config import settings

SESSION_COOKIE = "jarvis_session"


def is_valid_token(candidate: str | None) -> bool:
    """Compare access tokens without leaking timing information."""
    if not candidate:
        return False
    return secrets.compare_digest(candidate, settings.auth_token)


def extract_bearer_token(authorization: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


async def require_token(
    authorization: str | None = Header(default=None),
    token: str | None = Query(default=None),
    jarvis_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
) -> None:
    """Accept the same token from Bearer, query string, or secure session cookie."""
    bearer_token = extract_bearer_token(authorization)
    if any(is_valid_token(value) for value in (bearer_token, token, jarvis_session)):
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing Jarvis access token.",
    )
