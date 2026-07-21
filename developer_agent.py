from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "self_developer_config.json"
LOG_DIR = PROJECT_ROOT / "logs" / "self_developer"

DEFAULT_CONFIG: dict[str, Any] = {
    "model": "gpt-5",
    "test_command": [sys.executable, "-m", "pytest", "-q"],
    "allowed_extensions": [
        ".py", ".html", ".css", ".js", ".json", ".md", ".txt",
        ".yml", ".yaml", ".bat"
    ],
    "ignored_directories": [
        ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
        "data", "logs", "certs", "node_modules"
    ],
    "protected_paths": [
        ".env", "config/settings.json", "data/", "logs/", "certs/",
        ".git/"
    ],
    "max_context_chars": 120000,
    "max_patch_chars": 70000,
    "auto_commit": True,
    "auto_push": False,
    "auto_deploy": False
}


def run(command: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(
            json.dumps(DEFAULT_CONFIG, indent=2),
            encoding="utf-8",
        )
        return dict(DEFAULT_CONFIG)

    loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    merged = dict(DEFAULT_CONFIG)
    merged.update(loaded)
    return merged


def ensure_git_repo() -> None:
    result = run(["git", "rev-parse", "--is-inside-work-tree"], check=False)
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise RuntimeError("Run this inside the Jarvis Git repository.")


def ensure_clean_worktree() -> None:
    result = run(["git", "status", "--porcelain"])
    if result.stdout.strip():
        raise RuntimeError(
            "Git working tree is not clean. Commit or discard current changes first."
        )


def current_branch() -> str:
    return run(["git", "branch", "--show-current"]).stdout.strip()


def create_work_branch() -> str:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    branch = f"jarvis-ai/{stamp}"
    run(["git", "switch", "-c", branch])
    return branch


def is_ignored(path: Path, ignored: list[str]) -> bool:
    return any(part in ignored for part in path.parts)


def collect_context(config: dict[str, Any]) -> str:
    allowed = set(config["allowed_extensions"])
    ignored = set(config["ignored_directories"])
    max_chars = int(config["max_context_chars"])

    candidates: list[Path] = []
    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(PROJECT_ROOT)
        if is_ignored(rel, list(ignored)):
            continue
        if path.suffix.lower() not in allowed:
            continue
        candidates.append(path)

    # Prioritize active application code.
    candidates.sort(
        key=lambda p: (
            0 if str(p.relative_to(PROJECT_ROOT)).startswith("app") else 1,
            len(p.parts),
            str(p),
        )
    )

    chunks: list[str] = []
    used = 0
    for path in candidates:
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        block = f"\n===== FILE: {rel} =====\n{content}\n"
        if used + len(block) > max_chars:
            continue
        chunks.append(block)
        used += len(block)

    tree = run(["git", "ls-files"]).stdout
    return f"===== TRACKED FILES =====\n{tree}\n" + "".join(chunks)


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise RuntimeError("The AI did not return valid JSON.")
        return json.loads(match.group(0))


def validate_patch(patch: str, config: dict[str, Any]) -> None:
    if not patch.strip():
        raise RuntimeError("The AI returned an empty patch.")
    if len(patch) > int(config["max_patch_chars"]):
        raise RuntimeError("Patch is larger than the configured safety limit.")

    protected = [p.replace("\\", "/") for p in config["protected_paths"]]
    touched = re.findall(r"^\+\+\+ b/(.+)$", patch, flags=re.MULTILINE)
    touched += re.findall(r"^--- a/(.+)$", patch, flags=re.MULTILINE)

    for raw in touched:
        path = raw.strip().replace("\\", "/")
        if path == "/dev/null":
            continue
        if path.startswith("/") or ".." in Path(path).parts:
            raise RuntimeError(f"Unsafe patch path: {path}")
        for protected_path in protected:
            if protected_path.endswith("/"):
                if path.startswith(protected_path):
                    raise RuntimeError(f"Protected path cannot be changed: {path}")
            elif path == protected_path:
                raise RuntimeError(f"Protected path cannot be changed: {path}")


def request_patch(requirement: str, context: str, config: dict[str, Any]) -> dict[str, Any]:
    client = OpenAI()
    prompt = f"""
You are Jarvis Developer Agent, a cautious senior software engineer.

USER REQUIREMENT:
{requirement}

PROJECT CONTEXT:
{context}

Return JSON only with this exact shape:
{{
  "summary": "short explanation",
  "risk": "low|medium|high",
  "patch": "a valid unified git diff",
  "test_notes": ["test note 1"]
}}

Rules:
- Modify the smallest number of files necessary.
- Do not edit secrets, .env, config/settings.json, data, logs, certs, or .git.
- Do not remove authentication or safety checks.
- Do not add destructive commands, arbitrary shell execution, credential collection,
  surveillance, or silent deployment.
- Preserve existing APIs unless the requirement explicitly needs a change.
- The patch must be applicable with `git apply`.
- Include tests for meaningful behavior changes.
- Do not wrap JSON in markdown fences.
"""
    response = client.responses.create(
        model=str(config["model"]),
        input=prompt,
    )
    return extract_json(response.output_text)


def apply_patch(patch: str) -> None:
    patch_file = PROJECT_ROOT / ".jarvis_ai_patch.diff"
    patch_file.write_text(patch, encoding="utf-8", newline="\n")
    try:
        check = run(["git", "apply", "--check", str(patch_file)], check=False)
        if check.returncode != 0:
            raise RuntimeError(
                "Patch validation failed:\n" + check.stderr.strip()
            )
        apply_result = run(["git", "apply", str(patch_file)], check=False)
        if apply_result.returncode != 0:
            raise RuntimeError(
                "Patch application failed:\n" + apply_result.stderr.strip()
            )
    finally:
        patch_file.unlink(missing_ok=True)


def run_tests(config: dict[str, Any]) -> tuple[bool, str]:
    command = [str(part) for part in config["test_command"]]
    result = run(command, check=False)
    output = (result.stdout + "\n" + result.stderr).strip()
    return result.returncode == 0, output


def rollback_changes() -> None:
    run(["git", "reset", "--hard", "HEAD"], check=False)
    run(["git", "clean", "-fd"], check=False)


def write_log(payload: dict[str, Any]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Safely ask Jarvis to improve its own Git repository."
    )
    parser.add_argument(
        "requirement",
        nargs="?",
        help='Example: "Hide PC controls in cloud mode"',
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Apply a low/medium-risk patch without interactive confirmation.",
    )
    args = parser.parse_args()

    requirement = args.requirement or input("What should Jarvis develop? ").strip()
    if not requirement:
        print("No requirement provided.")
        return 2

    if not os.getenv("OPENAI_API_KEY", "").strip():
        print("OPENAI_API_KEY is not configured.")
        return 2

    config = load_config()
    ensure_git_repo()
    ensure_clean_worktree()

    original_branch = current_branch()
    branch = create_work_branch()
    print(f"Created safe work branch: {branch}")

    try:
        context = collect_context(config)
        proposal = request_patch(requirement, context, config)
        patch = str(proposal.get("patch", ""))
        validate_patch(patch, config)

        print("\nPROPOSAL")
        print("Summary:", proposal.get("summary", ""))
        print("Risk:", proposal.get("risk", "unknown"))
        print("\nPATCH PREVIEW\n")
        print(patch[:12000])
        if len(patch) > 12000:
            print("\n...patch preview truncated...")

        risk = str(proposal.get("risk", "")).lower()
        approved = args.auto_approve and risk in {"low", "medium"}
        if not approved:
            answer = input("\nApply this patch? Type YES: ").strip()
            approved = answer == "YES"

        if not approved:
            run(["git", "switch", original_branch], check=False)
            run(["git", "branch", "-D", branch], check=False)
            print("Cancelled. No files were changed.")
            return 0

        apply_patch(patch)
        ok, test_output = run_tests(config)
        print("\nTEST OUTPUT\n")
        print(test_output)

        log_payload = {
            "requirement": requirement,
            "branch": branch,
            "proposal": proposal,
            "tests_passed": ok,
            "test_output": test_output[-20000:],
        }
        log_path = write_log(log_payload)

        if not ok:
            rollback_changes()
            print(f"Tests failed. Changes rolled back. Log: {log_path}")
            return 1

        if config.get("auto_commit", True):
            run(["git", "add", "."])
            commit_message = f"Jarvis AI: {proposal.get('summary', requirement)[:70]}"
            result = run(["git", "commit", "-m", commit_message], check=False)
            if result.returncode != 0:
                raise RuntimeError(result.stderr or result.stdout)

        print("\nSUCCESS")
        print(f"Changes are committed on branch: {branch}")
        print(f"Review with: git diff {original_branch}..{branch}")
        print(f"Return to main with: git switch {original_branch}")
        print(f"Merge when satisfied: git merge {branch}")
        print(f"Log: {log_path}")

        if config.get("auto_push", False):
            run(["git", "push", "-u", "origin", branch])
            print("Branch pushed to GitHub.")

        return 0

    except Exception as exc:
        rollback_changes()
        print(f"\nDeveloper Agent failed safely: {exc}")
        print(f"Current branch: {branch}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
