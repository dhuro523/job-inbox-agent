from app.config.settings import load_settings


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    settings = load_settings()

    assert settings.app_env == "local"
    assert settings.log_level == "INFO"