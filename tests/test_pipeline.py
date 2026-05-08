from io import BytesIO
from pathlib import Path

from semipulse.config import get_settings
from semipulse.pipeline import run_demo_pipeline, save_uploaded_datasets, validate_data_directory
from semipulse.sample_data import DATASET_FILENAMES, generate_sample_data


def test_validate_data_directory_returns_valid_result(tmp_path: Path) -> None:
    generate_sample_data(tmp_path, random_seed=42, num_machines=6, days=20)

    result = validate_data_directory(tmp_path)

    assert result.is_valid


def test_save_uploaded_datasets_writes_expected_filenames(tmp_path: Path) -> None:
    files = {name: BytesIO(b"col\nvalue\n") for name in DATASET_FILENAMES}

    saved = save_uploaded_datasets(files, tmp_path)

    assert set(saved) == set(DATASET_FILENAMES)
    for name, path in saved.items():
        assert path.name == DATASET_FILENAMES[name]
        assert path.exists()


def test_run_demo_pipeline_completes_with_configured_paths(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("SEMIPULSE_DATA_DIR", str(tmp_path / "sample"))
    monkeypatch.setenv("SEMIPULSE_DB_PATH", str(tmp_path / "semipulse.db"))
    monkeypatch.setenv("SEMIPULSE_MODEL_DIR", str(tmp_path / "models"))
    get_settings.cache_clear()

    try:
        summary = run_demo_pipeline(generate_data=True, reset_database=True, train_model=True)
    finally:
        get_settings.cache_clear()

    assert summary["generated_data"] is True
    assert summary["database_rebuilt"] is True
    assert summary["features_generated"] is True
    assert summary["model_trained"] is True
    assert summary["feature_rows"] > 0
