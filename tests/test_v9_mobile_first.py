from pathlib import Path


def test_mobile_first_files_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "app" / "web" / "assistant.html").exists()
    assert (root / "app" / "api" / "dashboard.py").exists()


def test_dashboard_has_mobile_first_routes():
    root = Path(__file__).resolve().parents[1]
    source = (root / "app" / "api" / "dashboard.py").read_text(encoding="utf-8")
    assert '"/mobile"' in source
    assert '"assistant.html" if settings.cloud_mode else "index.html"' in source
    assert '"/control"' in source

