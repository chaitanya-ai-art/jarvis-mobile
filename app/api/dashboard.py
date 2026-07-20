from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Cookie, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, Response

from app.core.config import settings
from app.core.security import SESSION_COOKIE, is_valid_token

WEB_DIR = Path(__file__).resolve().parents[1] / "web"
router = APIRouter(tags=["dashboard"])

_INVALID_LINK = """<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Jarvis Link</title>
<style>
body {
    background: #070b14;
    color: #eef4ff;
    font-family: Segoe UI, Arial, sans-serif;
    padding: 28px;
    line-height: 1.5;
}

.box {
    max-width: 620px;
    margin: auto;
    background: #101727;
    border: 1px solid #23304b;
    border-radius: 18px;
    padding: 22px;
}

code {
    color: #4dd7ff;
}
</style>
</head>

<body>
<div class="box">
    <h2>Jarvis mobile link is invalid</h2>
    <p>
        Open Jarvis using the correct mobile link containing your authentication token.
    </p>
    <p>
        Example:
        <code>/mobile?token=YOUR_AUTH_TOKEN</code>
    </p>
</div>
</body>
</html>
"""


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        samesite="strict",
        secure=settings.cloud_mode,
        max_age=60 * 60 * 24 * 30,
        path="/",
    )


@router.get("/mobile", include_in_schema=False)
@router.get("/mobile/", include_in_schema=False)
async def mobile_dashboard(
    request: Request,
    token: str | None = Query(default=None),
    jarvis_session: str | None = Cookie(
        default=None,
        alias=SESSION_COOKIE,
    ),
):
    """
    Serve the Jarvis mobile dashboard.

    A valid token in the URL creates or refreshes the browser session.
    After that, the browser can authenticate using the secure session cookie.
    """

    selected_token: str | None = None

    if is_valid_token(token):
        selected_token = token
    elif is_valid_token(jarvis_session):
        selected_token = jarvis_session

    if not is_valid_token(selected_token):
        return HTMLResponse(
            content=_INVALID_LINK,
            status_code=401,
        )

    index_file = WEB_DIR / "index.html"

    if not index_file.exists():
        return HTMLResponse(
            content="<h2>Jarvis mobile interface not found.</h2>",
            status_code=500,
        )

    response = FileResponse(
        index_file,
        media_type="text/html",
    )

    _set_session_cookie(
        response=response,
        token=selected_token,
    )

    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@router.post("/auth/logout", include_in_schema=False)
async def logout() -> Response:
    response = Response(status_code=204)

    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/",
        secure=settings.cloud_mode,
        samesite="strict",
    )

    return response


@router.get("/manifest.webmanifest", include_in_schema=False)
async def manifest() -> FileResponse:
    manifest_file = WEB_DIR / "manifest.webmanifest"

    return FileResponse(
        manifest_file,
        media_type="application/manifest+json",
    )