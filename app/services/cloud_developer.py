from __future__ import annotations

import base64
import json
import os
import re
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import httpx
from openai import OpenAI


@dataclass
class DeveloperJob:
    id: str
    instruction: str
    status: str = "queued"
    message: str = "Queued"
    branch: str | None = None
    changed_files: list[str] = field(default_factory=list)
    pull_request_number: int | None = None
    pull_request_url: str | None = None
    merge_commit_sha: str | None = None
    error: str | None = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "instruction": self.instruction,
            "status": self.status,
            "message": self.message,
            "branch": self.branch,
            "changed_files": self.changed_files,
            "pull_request_number": self.pull_request_number,
            "pull_request_url": self.pull_request_url,
            "merge_commit_sha": self.merge_commit_sha,
            "error": self.error,
            "created_at": self.created_at,
        }


class DeveloperJobs:
    def __init__(self) -> None:
        self._jobs: dict[str, DeveloperJob] = {}
        self._lock = threading.Lock()

    def create(self, instruction: str) -> DeveloperJob:
        job = DeveloperJob(
            id=uuid.uuid4().hex,
            instruction=instruction.strip(),
        )
        with self._lock:
            self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> DeveloperJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def _update(self, job: DeveloperJob, **values: Any) -> None:
        with self._lock:
            for key, value in values.items():
                setattr(job, key, value)

    @staticmethod
    def _environment() -> tuple[str, str, str]:
        github_token = os.getenv("GITHUB_TOKEN", "").strip()
        github_repo = os.getenv("GITHUB_REPO", "").strip()
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()

        if not github_token:
            raise RuntimeError("GITHUB_TOKEN is not configured")
        if "/" not in github_repo:
            raise RuntimeError("GITHUB_REPO must be owner/repository")
        if not openai_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        return github_token, github_repo, openai_key

    def run(self, job_id: str) -> None:
        job = self.get(job_id)
        if job is None:
            return

        try:
            self._update(
                job,
                status="working",
                message="Reading the Jarvis GitHub project",
            )
            github_token, github_repo, openai_key = self._environment()
            owner, repo = github_repo.split("/", 1)
            api = GitHubRepo(owner, repo, github_token)

            main_sha = api.branch_sha("main")
            branch = (
                "jarvis-ai/"
                + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
                + "-"
                + job.id[:6]
            )
            api.create_branch(branch, main_sha)
            self._update(
                job,
                branch=branch,
                message="Analyzing the active Jarvis source",
            )

            files = api.read_context_files(
                branch="main",
                preferred=[
                    "app/main.py",
                    "app/web/assistant.html",
                    "app/web/index.html",
                    "app/api/developer.py",
                    "app/api/chat.py",
                    "app/api/dashboard.py",
                    "app/services/cloud_developer.py",
                    "app/services/chat_service.py",
                    "app/core/config.py",
                    "app/core/security.py",
                    "requirements.txt",
                ],
                limit=20,
                max_chars=100000,
            )

            changes = generate_changes(
                instruction=job.instruction,
                files=files,
                api_key=openai_key,
            )
            if not changes:
                raise RuntimeError("AI returned no file changes")

            changed: list[str] = []
            for item in changes:
                path = validate_path(str(item["path"]))
                content = str(item["content"])

                api.write_file(
                    branch=branch,
                    path=path,
                    content=content,
                    message=f"Jarvis AI: {job.instruction[:60]}",
                )
                changed.append(path)
                self._update(
                    job,
                    changed_files=list(changed),
                    message=f"Updated {len(changed)} file(s)",
                )

            pull_request = api.create_pull_request(
                title=f"Jarvis AI: {job.instruction[:70]}",
                body=(
                    "Created by Jarvis Mobile Self Developer.\n\n"
                    f"Request: {job.instruction}\n\n"
                    "Review the changed files before approving from the Jarvis app."
                ),
                head=branch,
                base="main",
            )

            self._update(
                job,
                status="ready",
                message=(
                    "Development completed. Review the pull request, "
                    "then approve it from Jarvis."
                ),
                changed_files=changed,
                pull_request_number=int(pull_request["number"]),
                pull_request_url=str(pull_request["html_url"]),
            )

        except Exception as exc:
            self._update(
                job,
                status="failed",
                message="Development failed safely",
                error=str(exc),
            )

    def approve(self, job_id: str) -> None:
        job = self.get(job_id)
        if job is None:
            return

        if job.status != "ready" or job.pull_request_number is None:
            self._update(
                job,
                status="failed",
                message="Approval failed safely",
                error="The job is not ready for merge",
            )
            return

        try:
            self._update(
                job,
                status="merging",
                message="Merging the approved pull request",
            )
            github_token, github_repo, _ = self._environment()
            owner, repo = github_repo.split("/", 1)
            api = GitHubRepo(owner, repo, github_token)

            result = api.merge_pull_request(
                pull_number=job.pull_request_number,
                commit_title=f"Jarvis AI: {job.instruction[:70]}",
            )

            if not result.get("merged"):
                raise RuntimeError(
                    str(result.get("message", "GitHub did not merge the pull request"))
                )

            self._update(
                job,
                status="merged",
                message=(
                    "Approved update merged into main. "
                    "Render should deploy it automatically."
                ),
                merge_commit_sha=str(result.get("sha", "")),
            )

        except Exception as exc:
            self._update(
                job,
                status="failed",
                message="Merge failed safely",
                error=str(exc),
            )


class GitHubRepo:
    def __init__(self, owner: str, repo: str, token: str) -> None:
        self.owner = owner
        self.repo = repo
        self.base = f"https://api.github.com/repos/{owner}/{repo}"
        self.client = httpx.Client(
            timeout=45,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

    def _request(self, method: str, url: str, **kwargs: Any) -> Any:
        response = self.client.request(method, url, **kwargs)

        if response.status_code >= 400:
            permissions = response.headers.get(
                "X-Accepted-GitHub-Permissions",
                "",
            )
            detail = response.text[:800]
            if permissions:
                detail += f" | Required permissions: {permissions}"
            raise RuntimeError(
                f"GitHub API {response.status_code}: {detail}"
            )

        if not response.content:
            return None

        return response.json()

    def branch_sha(self, branch: str) -> str:
        data = self._request(
            "GET",
            f"{self.base}/git/ref/heads/{branch}",
        )
        return str(data["object"]["sha"])

    def create_branch(self, branch: str, sha: str) -> None:
        self._request(
            "POST",
            f"{self.base}/git/refs",
            json={
                "ref": f"refs/heads/{branch}",
                "sha": sha,
            },
        )

    def get_file(
        self,
        path: str,
        branch: str,
    ) -> tuple[str, str] | None:
        response = self.client.get(
            f"{self.base}/contents/{path}",
            params={"ref": branch},
        )

        if response.status_code == 404:
            return None

        if response.status_code >= 400:
            raise RuntimeError(
                f"GitHub API {response.status_code}: {response.text[:500]}"
            )

        data = response.json()
        if data.get("type") != "file":
            return None

        decoded = base64.b64decode(data["content"]).decode("utf-8")
        return decoded, str(data["sha"])

    def write_file(
        self,
        branch: str,
        path: str,
        content: str,
        message: str,
    ) -> None:
        existing = self.get_file(path, branch)
        payload: dict[str, Any] = {
            "message": message,
            "content": base64.b64encode(
                content.encode("utf-8")
            ).decode("ascii"),
            "branch": branch,
        }

        if existing:
            payload["sha"] = existing[1]

        self._request(
            "PUT",
            f"{self.base}/contents/{path}",
            json=payload,
        )

    def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"{self.base}/pulls",
            json={
                "title": title,
                "body": body,
                "head": head,
                "base": base,
                "draft": False,
                "maintainer_can_modify": True,
            },
        )

    def merge_pull_request(
        self,
        pull_number: int,
        commit_title: str,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"{self.base}/pulls/{pull_number}/merge",
            json={
                "commit_title": commit_title,
                "merge_method": "squash",
            },
        )

    def read_context_files(
        self,
        branch: str,
        preferred: list[str],
        limit: int,
        max_chars: int,
    ) -> dict[str, str]:
        result: dict[str, str] = {}
        used = 0

        for path in preferred[:limit]:
            item = self.get_file(path, branch)
            if not item:
                continue

            content = item[0]
            if used + len(content) > max_chars:
                continue

            result[path] = content
            used += len(content)

        return result


def validate_path(path: str) -> str:
    clean = path.strip().replace("\\", "/").lstrip("/")

    protected_exact = {
        ".env",
        "config/settings.json",
        "render.yaml",
    }
    protected_prefixes = (
        "data/",
        "logs/",
        "certs/",
        ".git/",
        ".github/workflows/",
    )

    if not clean or ".." in clean.split("/"):
        raise RuntimeError(f"Unsafe path: {path}")

    if clean in protected_exact:
        raise RuntimeError(f"Protected path: {clean}")

    if any(clean.startswith(prefix) for prefix in protected_prefixes):
        raise RuntimeError(f"Protected path: {clean}")

    if not re.search(
        r"\.(py|html|css|js|json|md|txt|yml|yaml|bat)$",
        clean,
    ):
        raise RuntimeError(f"Unsupported file type: {clean}")

    return clean


def extract_json(text: str) -> Any:
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", text, flags=re.DOTALL)
        if not match:
            raise RuntimeError("AI response was not valid JSON")
        return json.loads(match.group(0))


def generate_changes(
    instruction: str,
    files: dict[str, str],
    api_key: str,
) -> list[dict[str, str]]:
    context = "\n\n".join(
        f"===== {path} =====\n{content}"
        for path, content in files.items()
    )

    prompt = f"""
You are the safe cloud developer for Chinna's Jarvis mobile-first assistant.

USER REQUEST:
{instruction}

CURRENT ACTIVE FILES:
{context}

Return JSON only as an array:
[
  {{"path":"relative/file/path.py","content":"complete replacement file content"}}
]

Rules:
- Make the smallest useful change.
- Keep Jarvis mobile-first; PC control is optional.
- Never expose or edit secrets.
- Never weaken authentication.
- Never edit Render configuration or GitHub workflows.
- Never add arbitrary shell execution, credential collection, surveillance,
  destructive actions, or hidden network behavior.
- Return complete content for every changed file.
- Preserve existing APIs unless the request requires a compatible extension.
- Keep the response below 60,000 characters.
"""

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5"),
        input=prompt,
    )

    parsed = extract_json(response.output_text)
    if not isinstance(parsed, list):
        raise RuntimeError("AI response must be a list")

    return [
        {
            "path": str(item["path"]),
            "content": str(item["content"]),
        }
        for item in parsed
        if isinstance(item, dict)
        and "path" in item
        and "content" in item
    ]


developer_jobs = DeveloperJobs()
