from pathlib import Path

from semipulse.database import (
    get_connection,
    initialize_database,
    load_sample_csvs_to_sqlite,
    read_table,
    table_exists,
)
from semipulse.sample_data import generate_sample_data
from semipulse.schema import REQUIRED_TABLES


def test_initialize_database_creates_required_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "semipulse.db"
    initialize_database(db_path=db_path, reset=True)

    conn = get_connection(db_path)
    try:
        for table in REQUIRED_TABLES:
            assert table_exists(conn, table)
    finally:
        conn.close()


def test_load_sample_csvs_to_sqlite_writes_source_tables(tmp_path: Path) -> None:
    data_dir = tmp_path / "sample"
    db_path = tmp_path / "semipulse.db"
    generate_sample_data(data_dir, random_seed=42, num_machines=8, days=15)

    counts = load_sample_csvs_to_sqlite(data_dir=data_dir, db_path=db_path, reset=True)

    assert counts["machines"] == 8
    assert counts["sensor_readings"] > 0
    assert counts["maintenance_records"] > 0
    assert counts["defect_records"] > 0

    conn = get_connection(db_path)
    try:
        for table, expected in counts.items():
            assert len(read_table(conn, table)) == expected
        assert len(read_table(conn, "pipeline_runs")) == 1
    finally:
        conn.close()
