from pathlib import Path

import pandas as pd

from semipulse.data_loader import rebuild_database_from_csvs
from semipulse.database import get_connection, read_table
from semipulse.features import (
    CATEGORICAL_FEATURE_COLUMNS,
    NUMERIC_FEATURE_COLUMNS,
    build_features_from_database,
    build_machine_features,
)
from semipulse.sample_data import generate_sample_data


def test_build_machine_features_has_required_columns(tmp_path: Path) -> None:
    data_dir = tmp_path / "sample"
    db_path = tmp_path / "semipulse.db"
    generate_sample_data(data_dir, random_seed=42, num_machines=8, days=45)
    rebuild_database_from_csvs(data_dir=data_dir, db_path=db_path, reset=True)

    features = build_features_from_database(db_path=db_path, write=True)

    assert len(features) == 8
    assert {"machine_id", "feature_timestamp", "target_failure_within_window"}.issubset(features.columns)
    assert set(NUMERIC_FEATURE_COLUMNS).issubset(features.columns)
    assert set(CATEGORICAL_FEATURE_COLUMNS).issubset(features.columns)


def test_feature_rows_are_stored_in_sqlite(tmp_path: Path) -> None:
    data_dir = tmp_path / "sample"
    db_path = tmp_path / "semipulse.db"
    generate_sample_data(data_dir, random_seed=7, num_machines=6, days=40)
    rebuild_database_from_csvs(data_dir=data_dir, db_path=db_path, reset=True)

    features = build_features_from_database(db_path=db_path, write=True)

    conn = get_connection(db_path)
    try:
        stored = read_table(conn, "machine_features")
    finally:
        conn.close()
    assert len(stored) == len(features)
    assert stored["machine_id"].is_unique


def test_rolling_and_recency_features_on_controlled_data() -> None:
    datasets = {
        "machines": pd.DataFrame(
            {
                "machine_id": ["M-1"],
                "machine_type": ["Etcher"],
                "manufacturer": ["TEL"],
                "facility_area": ["Fab A"],
                "install_date": ["2024-01-01"],
                "status": ["active"],
                "criticality": ["high"],
            }
        ),
        "sensor_readings": pd.DataFrame(
            {
                "reading_id": ["R-1", "R-2", "R-3"],
                "machine_id": ["M-1", "M-1", "M-1"],
                "timestamp": ["2025-01-01", "2025-01-08", "2025-01-10"],
                "temperature": [60.0, 70.0, 80.0],
                "vibration": [0.1, 0.3, 0.5],
                "pressure": [100.0, 101.0, 102.0],
                "power_draw": [10.0, 20.0, 30.0],
            }
        ),
        "maintenance_records": pd.DataFrame(
            {
                "maintenance_id": ["MT-1"],
                "machine_id": ["M-1"],
                "maintenance_date": ["2025-01-05"],
                "maintenance_type": ["scheduled"],
                "downtime_hours": [4.0],
                "severity": ["low"],
            }
        ),
        "defect_records": pd.DataFrame(
            {
                "defect_id": ["D-1", "D-2"],
                "machine_id": ["M-1", "M-1"],
                "timestamp": ["2025-01-07", "2025-01-09"],
                "defect_count": [2, 4],
                "batch_id": ["B-1", "B-2"],
                "severity": ["low", "medium"],
                "yield_loss_pct": [1.0, 3.0],
            }
        ),
    }

    features = build_machine_features(datasets, as_of_date=pd.Timestamp("2025-01-10"), prediction_window_days=14)
    row = features.iloc[0]

    assert row["rolling_7d_avg_temperature"] == 75.0
    assert row["rolling_7d_defect_count"] == 6
    assert row["days_since_last_maintenance"] == 5


def test_generated_numeric_features_are_not_all_null(tmp_path: Path) -> None:
    data_dir = tmp_path / "sample"
    db_path = tmp_path / "semipulse.db"
    generate_sample_data(data_dir, random_seed=99, num_machines=12, days=75)
    rebuild_database_from_csvs(data_dir=data_dir, db_path=db_path, reset=True)

    features = build_features_from_database(db_path=db_path, write=False)

    assert features[NUMERIC_FEATURE_COLUMNS].notna().all().all()
    assert len(features["target_failure_within_window"].unique()) >= 1
