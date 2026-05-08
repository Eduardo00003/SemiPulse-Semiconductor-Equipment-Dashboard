from pathlib import Path

import pandas as pd

from semipulse.database import get_connection, initialize_database, read_table
from semipulse.sample_data import generate_sample_data
from semipulse.validation import (
    persist_validation_issues,
    validate_all_datasets,
    validate_dataset,
)


def _load_sample(tmp_path: Path) -> dict[str, pd.DataFrame]:
    paths = generate_sample_data(tmp_path, random_seed=42, num_machines=8, days=20)
    return {name: pd.read_csv(path) for name, path in paths.items()}


def test_generated_sample_data_has_no_validation_errors(tmp_path: Path) -> None:
    result = validate_all_datasets(_load_sample(tmp_path))

    assert result.is_valid
    assert not result.errors


def test_missing_required_columns_are_reported() -> None:
    df = pd.DataFrame({"machine_id": ["M-1"]})

    result = validate_dataset("machines", df)

    assert not result.is_valid
    assert any(issue.issue_type == "missing_required_columns" for issue in result.errors)


def test_duplicate_ids_invalid_timestamps_and_numeric_issues_are_reported() -> None:
    df = pd.DataFrame(
        {
            "reading_id": ["R-1", "R-1"],
            "machine_id": ["M-1", "M-1"],
            "timestamp": ["not-a-date", "2025-01-01"],
            "temperature": ["bad", 70],
            "vibration": [0.2, -1],
            "pressure": [100, 101],
            "power_draw": [20, 21],
        }
    )
    machines = pd.DataFrame({"machine_id": ["M-1"]})

    result = validate_dataset("sensor_readings", df, machines=machines)
    issue_types = {issue.issue_type for issue in result.errors}

    assert "duplicate_ids" in issue_types
    assert "invalid_timestamps" in issue_types
    assert "invalid_numeric_values" in issue_types
    assert "negative_numeric_values" in issue_types


def test_orphan_machine_ids_are_reported() -> None:
    df = pd.DataFrame(
        {
            "defect_id": ["D-1"],
            "machine_id": ["UNKNOWN"],
            "timestamp": ["2025-01-01"],
            "defect_count": [1],
            "batch_id": ["B-1"],
        }
    )
    machines = pd.DataFrame({"machine_id": ["M-1"]})

    result = validate_dataset("defect_records", df, machines=machines)

    assert not result.is_valid
    assert any(issue.issue_type == "orphan_machine_ids" for issue in result.errors)


def test_validation_issues_can_be_persisted(tmp_path: Path) -> None:
    db_path = tmp_path / "semipulse.db"
    initialize_database(db_path=db_path, reset=True)
    conn = get_connection(db_path)
    try:
        result = validate_dataset("machines", pd.DataFrame({"machine_id": ["M-1"]}))
        count = persist_validation_issues(conn, result.issues, pipeline_run_id=None)
        issues = read_table(conn, "data_quality_issues")
    finally:
        conn.close()

    assert count > 0
    assert len(issues) == count
