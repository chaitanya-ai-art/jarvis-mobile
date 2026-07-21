# Jarvis Mobile Self-Developer V1

This patch adds a separate, mobile-first assistant page:

```text
/assistant
```

Normal chat messages go to the existing `/chat` API.

Messages starting with:

```text
Develop:
Build:
Create feature:
```

start a cloud development job. The job reads selected files from GitHub, asks the
AI model for small code changes, and writes those changes to a new GitHub branch.

It **does not merge or deploy automatically**. The working production branch is
protected from an unreviewed AI change.

## Required Render environment variables

```text
OPENAI_API_KEY=<private OpenAI API key>
GITHUB_TOKEN=<fine-grained GitHub token with Contents read/write permission>
GITHUB_REPO=chaitanya-ai-art/jarvis-mobile
OPENAI_MODEL=gpt-5
```

Never send these values in chat or screenshots.

## Install

1. Extract the ZIP.
2. Run `INSTALL_MOBILE_SELF_DEVELOPER.bat`.
3. In `D:\Jarvis` run:

```bat
git add .
git commit -m "Add mobile self developer"
git push
```

4. Wait for Render to become Live.
5. Open once:

```text
https://jarvis-mobile-fjnr.onrender.com/assistant?token=YOUR_AUTH_TOKEN
```

After the cookie is stored, use:

```text
https://jarvis-mobile-fjnr.onrender.com/assistant
```

## First test

Type:

```text
Develop: hide PC controls from the cloud mobile dashboard
```

Jarvis should create a `jarvis-ai/...` branch and report its name.

## Safety

- No automatic merge.
- No automatic deployment.
- Protected paths cannot be edited.
- Authentication cannot be intentionally removed by the prompt.
- GitHub branch review remains mandatory.
