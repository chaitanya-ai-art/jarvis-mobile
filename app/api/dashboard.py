from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Cookie, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response

from app.core.security import SESSION_COOKIE, is_valid_token

WEB_DIR = Path(__file__).resolve().parents[1] / "web"
router = APIRouter(tags=["dashboard"])

_INVALID_LINK = """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Jarvis Link</title><style>body{background:#070b14;color:#eef4ff;font-family:Segoe UI,Arial;padding:28px;line-height:1.5}.box{max-width:620px;margin:auto;background:#101727;border:1px solid #23304b;border-radius:18px;padding:22px}code{color:#4dd7ff}</style></head>
<body><div class='box'><h2>Jarvis mobile link is invalid</h2><p>Close this tab and open the exact <code>PHONE APP</code> URL currently shown in the Jarvis PC window.</p><p>The server may have restarted or this browser may be using an old token.</p></div></body></html>"""


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        samesite="strict",
        secure=False,  # Local HTTP LAN connection. Change to True when HTTPS is introduced.
        max_age=60 * 60 * 24 * 30,
        path="/",
    )


@router.get("/mobile", include_in_schema=False)
@router.get("/mobile/", include_in_schema=False)
async def mobile_dashboard(
    request: Request,
    token: str | None = Query(default=None),
    jarvis_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
):
    # A valid URL token starts/refreshes the browser session. Afterwards the
    # page and WebSocket can authenticate through the HttpOnly cookie.
    selected = token if is_valid_token(token) else jarvis_session
    if not is_valid_token(selected):
        return HTMLResponse(_INVALID_LINK, status_code=401)

    response = FileResponse(WEB_DIR / "index.html", media_type="text/html")
    _set_session_cookie(response, selected)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@router.post("/auth/logout", include_in_schema=False)
async def logout() -> Response:
    response = Response(status_code=204)
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response


@router.get("/manifest.webmanifest", include_in_schema=False)
async def manifest() -> FileResponse:
    return FileResponse(
        WEB_DIR / "manifest.webmanifest",
        media_type="application/manifest+json",
    )
