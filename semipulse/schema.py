"""SQLite schema helpers."""

from __future__ import annotations

from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "db" / "schema.sql"

SOURCE_TABLES = [
    "machines",
    "sensor_readings",
    "maintenance_records",
    "defect_records",
]

REQUIRED_TABLES = [
    *SOURCE_TABLES,
    "machine_features",
    "risk_predictions",
    "model_runs",
    "pipeline_runs",
    "data_quality_issues",
]


def get_schema_path() -> Path:
    """Return the project schema path."""

    return SCHEMA_PATH


def load_schema_sql(schema_path: Path | str | None = None) -> str:
    """Load the SQLite schema SQL text."""

    path = Path(schema_path) if schema_path is not None else get_schema_path()
    return path.read_text(encoding="utf-8")
