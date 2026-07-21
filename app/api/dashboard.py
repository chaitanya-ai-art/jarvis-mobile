from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Cookie, Query
from fastapi.responses import FileResponse, HTMLResponse, Response

from app.core.config import settings
from app.core.security import SESSION_COOKIE, is_valid_token

WEB_DIR = Path(__file__).resolve().parents[1] / "web"
router = APIRouter(tags=["dashboard"])

_INVALID_LINK = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Jarvis Login</title>
<style>
body{margin:0;background:#050a13;color:#eef4ff;font-family:Segoe UI,Arial,sans-serif}
.box{max-width:620px;margin:12vh auto;background:#101827;border:1px solid #263451;border-radius:20px;padding:26px}
code{color:#51d8ff}
</style>
</head>
<body>
<div class="box">
<h2>Jarvis login required</h2>
<p>Open Jarvis once using the secure link containing your authentication token.</p>
<p><code>/mobile?token=YOUR_AUTH_TOKEN</code></p>
</div>
</body>
</html>"""


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


def _authenticated_file(
    token: str | None,
    jarvis_session: str | None,
    filename: str,
) -> Response:
    selected = token if is_valid_token(token) else jarvis_session

    if not is_valid_token(selected):
        return HTMLResponse(_INVALID_LINK, status_code=401)

    page = WEB_DIR / filename
    if not page.exists():
        return HTMLResponse(
            f"<h2>Jarvis page missing: {filename}</h2>",
            status_code=500,
        )

    response = FileResponse(page, media_type="text/html")
    _set_session_cookie(response, selected)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@router.get("/mobile", include_in_schema=False)
@router.get("/mobile/", include_in_schema=False)
async def mobile_dashboard(
    token: str | None = Query(default=None),
    jarvis_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
):
    """
    Mobile-first Jarvis home.

    In cloud mode, /mobile is the conversational assistant.
    The legacy Windows dashboard remains available at /control.
    """
    filename = "assistant.html" if settings.cloud_mode else "index.html"
    return _authenticated_file(token, jarvis_session, filename)


@router.get("/assistant", include_in_schema=False)
@router.get("/assistant/", include_in_schema=False)
async def assistant_dashboard(
    token: str | None = Query(default=None),
    jarvis_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
):
    return _authenticated_file(token, jarvis_session, "assistant.html")


@router.get("/control", include_in_schema=False)
@router.get("/control/", include_in_schema=False)
async def legacy_control_dashboard(
    token: str | None = Query(default=None),
    jarvis_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
):
    return _authenticated_file(token, jarvis_session, "index.html")


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
    return FileResponse(
        WEB_DIR / "manifest.webmanifest",
        media_type="application/manifest+json",
    )
