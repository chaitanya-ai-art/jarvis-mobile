# Jarvis V9 Mobile-First Activation

This patch changes the active cloud experience from the Windows-control dashboard
to a mobile-first assistant.

## What changes

- `/mobile` opens the conversational assistant in cloud mode.
- `/assistant` opens the same mobile-first assistant.
- The old Windows dashboard remains available at `/control`.
- The assistant has four tabs:
  - Chat
  - Develop
  - Today
  - Memory
- Developer requests are sent to the existing `/developer/request` API.
- Voice input and spoken replies remain available.
- A regression test confirms the cloud routing.

## Install

1. Extract this ZIP.
2. Run:

```text
INSTALL_V9_MOBILE_FIRST.bat
```

3. In Command Prompt:

```bat
cd /d D:\Jarvis
.venv\Scripts\python.exe -m pytest -q
git add app\api\dashboard.py app\web\assistant.html tests\test_v9_mobile_first.py
git commit -m "Activate Jarvis V9 mobile first"
git push
```

4. Wait for Render to become Live.
5. On the phone, refresh:

```text
https://jarvis-mobile-fjnr.onrender.com/mobile
```

The old dashboard is still available at:

```text
https://jarvis-mobile-fjnr.onrender.com/control
```

## Required for Developer mode

Render must contain:

```text
OPENAI_API_KEY
GITHUB_TOKEN
GITHUB_REPO=chaitanya-ai-art/jarvis-mobile
```

Developer mode creates a GitHub review branch. It does not merge or deploy
automatically.
