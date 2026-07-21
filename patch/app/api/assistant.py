from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Cookie, Query
from fastapi.responses import FileResponse, HTMLResponse, Response

from app.core.config import settings
from app.core.security import SESSION_COOKIE, is_valid_token

WEB_DIR = Path(__file__).resolve().parents[1] / "web"
router = APIRouter(tags=["assistant"])

_INVALID = """<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Jarvis Login</title><style>body{background:#070b14;color:#eef4ff;font-family:Arial;padding:24px}
.box{max-width:620px;margin:10vh auto;background:#101827;border:1px solid #263451;border-radius:18px;padding:24px}
code{color:#50d8ff}</style></head><body><div class="box"><h2>Jarvis login required</h2>
<p>Open the assistant once using <code>/assistant?token=YOUR_AUTH_TOKEN</code>.</p></div></body></html>"""


def _set_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        secure=settings.cloud_mode,
        samesite="strict",
        max_age=60 * 60 * 24 * 30,
        path="/",
    )


@router.get("/assistant", include_in_schema=False)
@router.get("/assistant/", include_in_schema=False)
async def assistant_page(
    token: str | None = Query(default=None),
    jarvis_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
):
    selected = token if is_valid_token(token) else jarvis_session
    if not is_valid_token(selected):
        return HTMLResponse(_INVALID, status_code=401)

    page = WEB_DIR / "assistant.html"
    if not page.exists():
        return HTMLResponse("<h2>Assistant interface missing.</h2>", status_code=500)

    response = FileResponse(page, media_type="text/html")
    _set_cookie(response, selected)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response
