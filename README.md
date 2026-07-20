# Jarvis V7 Unified Core — Sprint 2 (v7.1.0)

Sprint 2 adds one shared SQLite database for the PC, mobile client, voice system, and future Android app.

## New working features

- Persistent SQLite database: `data/jarvis.db`
- Personal memories API
- Conversation history API
- Projects API
- Goals API
- Reminders API
- Every `/chat` exchange is stored automatically
- Existing authentication token is preserved during upgrade

## Upgrade your existing `D:\Jarvis`

1. Stop Jarvis with `Ctrl+C`.
2. Back up `D:\Jarvis` once.
3. Extract this ZIP.
4. Copy its contents into `D:\Jarvis` and choose **Replace files in the destination**.
5. Start `START_JARVIS_V7.bat` again.
6. Open `http://127.0.0.1:8765/health` and confirm version `7.1.0`.

The update package does not include `config/settings.json`, so your current token is not overwritten.

## API endpoints

All endpoints below require the same bearer token except `/health`.

- `GET /memory`
- `POST /memory`
- `DELETE /memory/{id}`
- `GET /conversations`
- `GET /projects`
- `POST /projects`
- `DELETE /projects/{id}`
- `GET /goals`
- `POST /goals`
- `DELETE /goals/{id}`
- `GET /reminders`
- `POST /reminders`
- `DELETE /reminders/{id}`
- `POST /chat` (now stores user and assistant messages)

Use `http://127.0.0.1:8765/docs` to test them interactively.

## Run tests

```powershell
python -m pytest -q
```

## Next milestone

Sprint 3 will add WebSocket live updates and reconnect the mobile dashboard to this shared database.
