from fastapi.testclient import TestClient

from app.main import app
from app.services.command_service import ParsedCommand, parse_windows_command

client = TestClient(app)


def test_command_router_version():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['version'] == '8.0.0-cloud'


def test_open_excel_variants():
    assert parse_windows_command('Open Excel') == ParsedCommand('open_app', 'excel')
    assert parse_windows_command('Jarvis, please open Excel') == ParsedCommand('open_app', 'excel')
    assert parse_windows_command('Could you launch Microsoft Excel for me?') == ParsedCommand('open_app', 'excel')


def test_folder_and_file_commands():
    assert parse_windows_command('open the downloads folder') == ParsedCommand('open_folder', 'downloads')
    assert parse_windows_command('Hey Jarvis, find file DTH_COMPLETE.xlsx') == ParsedCommand('find_file', 'dth_complete.xlsx')


def test_non_approved_text_is_not_a_command():
    assert parse_windows_command('delete all files') is None
    assert parse_windows_command('run powershell format c') is None
    assert parse_windows_command('tell me a story') is None

