import pytest

@pytest.fixture(autouse=True)
def mock_env_development(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
