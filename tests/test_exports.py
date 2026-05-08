from pathlib import Path

from semipulse.data_loader import rebuild_database_from_csvs
from semipulse.database import get_connection, list_tables, read_table_view
from semipulse.exports import (
    export_machine_features,
    export_model_metrics,
    export_risk_rankings,
    export_table_csv,
)
from semipulse.features import build_features_from_database
from semipulse.model import train_model
from semipulse.sample_data import generate_sample_data


def _build_pipeline(tmp_path: Path):
    data_dir = tmp_path / "sample"
    db_path = tmp_path / "semipulse.db"
    model_dir = tmp_path / "models"
    generate_sample_data(data_dir, random_seed=42, num_machines=12, days=80)
    rebuild_database_from_csvs(data_dir=data_dir, db_path=db_path, reset=True)
    build_features_from_database(db_path=db_path, write=True)
    train_model(db_path=db_path, model_dir=model_dir, random_seed=42)
    return db_path, model_dir


def test_list_and_read_table_view(tmp_path: Path) -> None:
    db_path, _ = _build_pipeline(tmp_path)
    conn = get_connection(db_path)
    try:
        tables = list_tables(conn)
        machines = read_table_view(conn, "machines", limit=5)
    finally:
        conn.close()

    assert "machines" in tables
    assert 0 < len(machines) <= 5


def test_export_helpers_return_content(tmp_path: Path) -> None:
    db_path, model_dir = _build_pipeline(tmp_path)
    conn = get_connection(db_path)
    try:
        risk_csv = export_risk_rankings(conn)
        features_csv = export_machine_features(conn)
        metrics_json = export_model_metrics(conn, model_dir=model_dir)
        table_csv = export_table_csv(conn, "machines", limit=5)
    finally:
        conn.close()

    assert "machine_id" in risk_csv
    assert "risk_score" in risk_csv
    assert "avg_temperature" in features_csv
    assert "simulated_data_warning" in metrics_json
    assert "machine_type" in table_csv
