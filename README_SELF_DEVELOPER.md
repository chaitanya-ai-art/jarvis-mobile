# Jarvis Self Developer V1

This package gives Jarvis a safe software-development agent inside the existing
`D:\Jarvis` Git repository.

## What it can do

You can ask:

```text
Hide PC controls when Jarvis is running in cloud mode
Add a mobile notes page
Fix the reminder validation bug
Improve the voice error message
```

The agent will:

1. Check that Git is clean.
2. Create a separate `jarvis-ai/...` branch.
3. Read the active project source.
4. Ask the AI model for a unified code patch.
5. Block changes to secrets, databases, logs, certificates, and Git metadata.
6. Show the proposed changes.
7. Apply the patch only after approval.
8. Run the complete test suite.
9. Roll back automatically if tests fail.
10. Commit successful changes on the safe branch.

It does **not** silently merge, push, or deploy by default. That prevents one bad
instruction from destroying the working Jarvis service.

## Install

Copy these files into the root of `D:\Jarvis`:

```text
developer_agent.py
self_developer_config.json
INSTALL_SELF_DEVELOPER.bat
RUN_SELF_DEVELOPER.bat
```

Run:

```text
INSTALL_SELF_DEVELOPER.bat
```

## API key

Create an OpenAI API key and store it as a Windows environment variable named
`OPENAI_API_KEY`. Never put it in GitHub, screenshots, or `config/settings.json`.

Open a new Command Prompt after setting the variable.

## Use

Double-click:

```text
RUN_SELF_DEVELOPER.bat
```

Or run:

```bat
cd /d D:\Jarvis
.venv\Scripts\python.exe developer_agent.py "Hide PC controls in cloud mode"
```

The agent creates a branch, proposes code, asks for approval, runs tests, and
commits when successful.

## Review and merge

After a successful run:

```bat
git diff main..jarvis-ai/BRANCH_NAME
git switch main
git merge jarvis-ai/BRANCH_NAME
git push
```

Render then auto-deploys the merged update.

## Optional automation

In `self_developer_config.json`:

```json
"auto_push": false,
"auto_deploy": false
```

Keep both `false` until the agent has completed several successful updates.
Automatic deployment without review is intentionally disabled.

## Important limitation

This is an autonomous coding agent, not an unlimited self-improving intelligence.
It can modify the code it can see, run tests, and create commits. It cannot safely
decide every product requirement or guarantee that every generated change is good.
Git branches, tests, protected paths, and rollback are required safeguards.
