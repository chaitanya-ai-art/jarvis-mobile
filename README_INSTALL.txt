JARVIS V8.1 VOICE AI PATCH

Adds:
- OpenAI Responses API brain
- recent conversation and saved-memory context
- spoken AI replies
- optional "Hey Jarvis" listening while the dashboard remains open
- safe cloud response for PC-only commands

INSTALL
1. Stop local Jarvis with Ctrl+C.
2. Extract this ZIP.
3. Run INSTALL_V8_1.bat.
4. In D:\Jarvis run:
   git add app/core/config.py app/services/chat_service.py app/web/index.html
   git commit -m "Add Jarvis V8.1 voice AI"
   git push
5. Wait for Render to become Live.
6. In Render Environment add OPENAI_API_KEY and optionally OPENAI_MODEL.
7. Open Jarvis mobile and test typed chat first, then microphone.

NOTE
- "Hey Jarvis" mode works only while the browser/PWA page is open and Android allows microphone activity.
- Do not commit the OpenAI API key to GitHub.
