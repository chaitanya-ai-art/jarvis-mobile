from __future__ import annotations

from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.assistant import router as assistant_router
from app.api.chat import router as chat_router
from app.api.conversations import router as conversations_router
from app.api.dashboard import router as dashboard_router
from app.api.developer import router as developer_router
from app.api.goals import router as goals_router
from app.api.health import router as health_router
from app.api.memory import router as memory_router
from app.api.projects import router as projects_router
from app.api.reminders import router as reminders_router
from app.api.status import router as status_router
from app.api.summary import router as summary_router
from app.api.websocket import router as websocket_router
from app.api.windows import router as windows_router
from app.core.config import settings
from app.core.logging_config import logger
from app.services.database import initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    logger.info("Jarvis %s starting", settings.version)
    yield
    logger.info("Jarvis shutting down")


app = FastAPI(
    title="Jarvis Unified Core",
    version=settings.version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    started = perf_counter()
    response = await call_next(request)
    elapsed_ms = (perf_counter() - started) * 1000
    logger.info(
        "%s %s -> %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


app.include_router(health_router)
app.include_router(dashboard_router)
app.include_router(assistant_router)
app.include_router(developer_router)
app.include_router(summary_router)
app.include_router(websocket_router)
app.include_router(status_router)
app.include_router(chat_router)
app.include_router(memory_router)
app.include_router(conversations_router)
app.include_router(projects_router)
app.include_router(goals_router)
app.include_router(reminders_router)
app.include_router(windows_router)


@app.get("/", include_in_schema=False)
async def root(request: Request) -> RedirectResponse:
    token = request.query_params.get("token", "")
    target = "/assistant"
    if token:
        target += f"?token={token}"
    return RedirectResponse(url=target, status_code=307)
