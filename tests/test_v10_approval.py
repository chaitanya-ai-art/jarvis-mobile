from pathlib import Path


def test_v10_approval_api_exists():
    root = Path(__file__).resolve().parents[1]
    source = (root / "app" / "api" / "developer.py").read_text(encoding="utf-8")
    assert '"/approve/{job_id}"' in source
    assert "DEVELOPER_APPROVAL_PIN" in source


def test_v10_pull_request_workflow_exists():
    root = Path(__file__).resolve().parents[1]
    source = (
        root / "app" / "services" / "cloud_developer.py"
    ).read_text(encoding="utf-8")
    assert "create_pull_request" in source
    assert "merge_pull_request" in source
    assert "pull_request_url" in source


def test_v10_mobile_has_approval_ui():
    root = Path(__file__).resolve().parents[1]
    source = (root / "app" / "web" / "assistant.html").read_text(encoding="utf-8")
    assert "Approve & Deploy" in source
    assert "/developer/approve/" in source
