from __future__ import annotations

import socket
import uvicorn

from app.core.config import settings
from generate_https_cert import ensure_certificates


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
    cert, key, ca = ensure_certificates()
    ip = local_ip()
    print("=" * 66)
    print("JARVIS V7.4.2 - SECURE VOICE")
    print("=" * 66)
    print(f"PHONE APP : https://{ip}:{settings.port}/mobile?token={settings.auth_token}")
    print(f"PC HEALTH : https://127.0.0.1:{settings.port}/health")
    print(f"PHONE CA  : {ca}")
    print("Install jarvis-ca.crt on the phone once, then open PHONE APP in Chrome.")
    print("Press Ctrl+C to stop Jarvis.")
    print("=" * 66)
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level=settings.log_level.lower(),
        ssl_certfile=str(cert),
        ssl_keyfile=str(key),
    )
