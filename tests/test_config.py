from semipulse.config import Settings, ensure_runtime_dirs, get_settings


def test_default_settings_load_and_dirs_exist() -> None:
    settings = get_settings()

    assert isinstance(settings, Settings)
    assert settings.db_path.name == "semipulse.db"
    assert settings.random_seed == 42
    assert settings.prediction_window_days == 14

    ensure_runtime_dirs(settings)

    assert settings.db_path.parent.exists()
    assert settings.data_dir.exists()
    assert settings.model_dir.exists()
