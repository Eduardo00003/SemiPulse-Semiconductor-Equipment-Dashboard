from pathlib import Path

import pandas as pd

from semipulse.data_loader import (
    build_machine_analytics_table,
    clean_all_datasets,
    clean_machines,
    clean_sensor_readings,
    load_csv_datasets,
    rebuild_database_from_csvs,
)
from semipulse.database import get_connection, read_table
from semipulse.sample_data import generate_sample_data


def test_clean_machines_standardizes_machine_ids_and_dates() -> None:
    raw = pd.DataFrame(
        {
            "Machine ID": [" m-0001 "],
            "Machine Type": [" Etcher "],
            "Manufacturer": [" TEL "],
            "Facility Area": [" Fab A "],
            "Install Date": ["2024/01/02"],
            "Status": [" Active "],
        }
    )

    cleaned = clean_machines(raw)

    assert cleaned.loc[0, "machine_id"] == "M-0001"
    assert cleaned.loc[0, "install_date"] == "2024-01-02"
    assert cleaned.loc[0, "status"] == "active"


def test_clean_sensor_readings_parses_timestamps_and_numeric_values() -> None:
    raw = pd.DataFrame(
        {
            "reading_id": ["R-1"],
            "machine_id": ["m-1"],
            "timestamp": ["2025-01-01 12:30:00"],
            "temperature": ["70.5"],
            "vibration": ["0.3"],
            "pressure": ["101"],
            "power_draw": ["20"],
        }
    )

    cleaned = clean_sensor_readings(raw)

    assert cleaned.loc[0, "machine_id"] == "M-1"
    assert cleaned.loc[0, "timestamp"] == "2025-01-01T12:30:00"
    assert cleaned.loc[0, "temperature"] == 70.5


def test_build_machine_analytics_table_has_one_row_per_machine(tmp_path: Path) -> None:
    paths = generate_sample_data(tmp_path, random_seed=42, num_machines=6, days=20)
    datasets = {name: pd.read_csv(path) for name, path in paths.items()}
    cleaned = clean_all_datasets(datasets)

    analytics = build_machine_analytics_table(cleaned)

    assert len(analytics) == len(cleaned["machines"])
    assert analytics["machine_id"].is_unique
    assert {"avg_temperature", "total_downtime_hours", "total_defect_count"}.issubset(analytics.columns)


def test_rebuild_database_from_csvs_writes_cleaned_tables(tmp_path: Path) -> None:
    data_dir = tmp_path / "sample"
    db_path = tmp_path / "semipulse.db"
    generate_sample_data(data_dir, random_seed=42, num_machines=7, days=18)

    counts = rebuild_database_from_csvs(data_dir=data_dir, db_path=db_path, reset=True)

    conn = get_connection(db_path)
    try:
        assert counts["machines"] == 7
        assert len(read_table(conn, "machines")) == 7
        assert len(read_table(conn, "sensor_readings")) == counts["sensor_readings"]
        assert len(read_table(conn, "pipeline_runs")) == 1
    finally:
        conn.close()


def test_load_csv_datasets_reads_expected_files(tmp_path: Path) -> None:
    generate_sample_data(tmp_path, random_seed=42, num_machines=4, days=10)

    datasets = load_csv_datasets(tmp_path)

    assert set(datasets) == {"machines", "sensor_readings", "maintenance_records", "defect_records"}
