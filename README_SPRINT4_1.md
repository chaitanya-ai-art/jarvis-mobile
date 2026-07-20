# Jarvis V7 Sprint 4.1 — Authentication & WebSocket Hotfix

Version: **7.3.1**

## Fixed

- REST dashboard `401 Unauthorized` loop.
- WebSocket `403 Forbidden` reconnect loop.
- REST and WebSocket now accept the same HttpOnly browser session.
- The exact PHONE APP URL creates or refreshes the mobile session.
- The token is removed from the visible URL after pairing.
- Stale token values in browser local storage are cleared.
- Invalid or expired links show a clear recovery message instead of looping.
- Mobile HTML is served with `Cache-Control: no-store` to prevent stale dashboard code.

## Install

1. Stop Jarvis with `Ctrl+C`.
2. Extract this ZIP.
3. Run `INSTALL_SPRINT4_1_HOTFIX.bat`.
4. Restart `D:\Jarvis\START_JARVIS_V7.bat`.
5. On the phone, close the old Jarvis tab and open the **new exact PHONE APP URL** printed by the PC.

The installer preserves your existing authentication token, database, memories, projects, goals, and reminders.
