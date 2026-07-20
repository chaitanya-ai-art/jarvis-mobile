JARVIS V7.2.1 - MOBILE DASHBOARD HOTFIX

What this fixes
- Old PHONE links ending in /?token=... now redirect to the dashboard.
- /mobile and /mobile/ both work.
- The dashboard, WebSocket chat, counters, CPU/RAM status, and microphone button are included.
- Existing D:\Jarvis\config\settings.json and D:\Jarvis\data\jarvis.db are preserved.

Install
1. Stop Jarvis with Ctrl+C.
2. Extract this ZIP.
3. Double-click INSTALL_SPRINT3_HOTFIX.bat.
4. Start D:\Jarvis\START_JARVIS_V7.bat.
5. Open the exact PHONE APP URL shown in the console.

Verification
- http://127.0.0.1:8765/health must show version 7.2.1
- http://127.0.0.1:8765/mobile?token=YOUR_TOKEN must show the dashboard
- The old root URL /?token=YOUR_TOKEN will also redirect to the dashboard
