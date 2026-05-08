"""Pipeline orchestration helpers for CLI, tests, and Streamlit."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from semipulse.config import get_settings
from semipulse.data_loader import clean_all_datasets, load_csv_datasets, rebuild_database_from_csvs
from semipulse.features import build_features_from_database
from semipulse.model import train_model as train_risk_model
from semipulse.sample_data import DATASET_FILENAMES, generate_sample_data
from semipulse.validation import ValidationResult, validate_all_datasets


def validate_data_directory(data_dir: Path | str | None = None) -> ValidationResult:
    """Load and validate a directory containing the four expected CSVs."""

    raw = load_csv_datasets(data_dir)
    cleaned = clean_all_datasets(raw)
    return validate_all_datasets(cleaned)


def save_uploaded_datasets(files: dict[str, BinaryIO], destination_dir: Path | str) -> dict[str, Path]:
    """Save uploaded CSV file-like objects using the expected dataset filenames."""

    resolved = Path(destination_dir)
    resolved.mkdir(parents=True, exist_ok=True)
    saved: dict[str, Path] = {}
    for dataset_name, file_obj in files.items():
        if dataset_name not in DATASET_FILENAMES:
            raise ValueError(f"Unsupported dataset upload: {dataset_name}")
        path = resolved / DATASET_FILENAMES[dataset_name]
        content = file_obj.read()
        path.write_bytes(content)
        saved[dataset_name] = path
    return saved


def run_demo_pipeline(
    generate_data: bool = False,
    reset_database: bool = True,
    train_model: bool = True,
) -> dict[str, object]:
    """Run the local demo pipeline and return a status summary."""

    settings = get_settings()
    summary: dict[str, object] = {
        "generated_data": False,
        "database_rebuilt": False,
        "features_generated": False,
        "model_trained": False,
        "row_counts": {},
        "feature_rows": 0,
        "model_run_id": None,
    }

    if generate_data:
        paths = generate_sample_data(settings.data_dir)
        summary["generated_data"] = True
        summary["sample_files"] = {name: str(path) for name, path in paths.items()}

    row_counts = rebuild_database_from_csvs(data_dir=settings.data_dir, reset=reset_database)
    summary["database_rebuilt"] = True
    summary["row_counts"] = row_counts

    features = build_features_from_database(write=True)
    summary["features_generated"] = True
    summary["feature_rows"] = len(features)

    if train_model:
        metadata = train_risk_model()
        summary["model_trained"] = True
        summary["model_run_id"] = metadata["model_run_id"]
        summary["metrics"] = metadata["metrics"]

    return summary
