from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_voice_version() -> None:
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['version'] == '7.4.1'


def test_mobile_contains_voice_controls() -> None:
    from app.core.config import settings
    response = client.get(f'/mobile?token={settings.auth_token}', follow_redirects=True)
    assert response.status_code == 200
    text = response.text
    assert 'SpeechRecognition' in text
    assert 'speechSynthesis' in text
    assert 'voiceLang' in text
    assert 'autoSpeak' in text


def test_voice_uses_existing_chat_websocket() -> None:
    page = Path('app/web/index.html').read_text(encoding='utf-8')
    assert "type:'chat'" in page
    assert "source:'voice_or_text'" in page
