from __future__ import annotations

import socket

import uvicorn

from app.core.config import settings


def local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return str(sock.getsockname()[0])
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


if __name__ == "__main__":
    ip = local_ip()
    print("=" * 58)
    print("JARVIS V7 UNIFIED CORE")
    print("=" * 58)
    print(f"PC HEALTH : http://127.0.0.1:{settings.port}/health")
    print(f"API DOCS  : http://127.0.0.1:{settings.port}/docs")
    print(f"PHONE APP : http://{ip}:{settings.port}/mobile?token={settings.auth_token}")
    print(f"PHONE API : http://{ip}:{settings.port}")
    print(f"TOKEN     : {settings.auth_token}")
    print("Press Ctrl+C to stop Jarvis.")
    print("=" * 58)

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level=settings.log_level.lower(),
    )
