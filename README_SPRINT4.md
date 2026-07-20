# Jarvis V7 Sprint 4 — Safe Windows Automation

Version 7.3.0 adds approved Windows actions available from REST, WebSocket chat, and the mobile dashboard.

## Voice/text commands

- `open Excel`
- `open Chrome`
- `open Downloads`
- `open Notepad`
- `open Calculator`
- `open VS Code`
- `find DTH_COMPLETE.xlsx`
- `system info`
- `recent actions`
- `lock PC`

## Safety

The agent uses a fixed allow-list. It does not execute arbitrary shell commands, scripts, deletion, registry edits, installations, passwords, or OTP operations. Every attempted action is recorded at `logs/actions/actions.jsonl`.

## API

- `GET /windows/capabilities`
- `POST /windows/action`
- `POST /windows/command`
- `GET /windows/actions`

All endpoints require the existing bearer token.
