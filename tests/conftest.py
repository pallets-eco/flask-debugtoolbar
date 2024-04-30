from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def mock_env_development(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FLASK_ENV", "development")
