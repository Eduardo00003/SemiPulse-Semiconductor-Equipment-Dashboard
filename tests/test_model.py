from pathlib import Path

from semipulse.data_loader import rebuild_database_from_csvs
from semipulse.database import get_connection, read_table
from semipulse.features import build_features_from_database
from semipulse.metrics import calculate_classification_metrics
from semipulse.model import load_model, train_model
from semipulse.sample_data import generate_sample_data


def test_calculate_classification_metrics_has_required_keys() -> None:
    metrics = calculate_classification_metrics([0, 1, 1], [0, 0, 1], [0.1, 0.4, 0.8])

    assert {"recall", "precision", "f1", "accuracy", "roc_auc", "confusion_matrix"}.issubset(metrics)
    assert metrics["confusion_matrix"] == [[1, 0], [1, 1]]


def test_train_model_writes_artifacts_and_predictions(tmp_path: Path) -> None:
    data_dir = tmp_path / "sample"
    db_path = tmp_path / "semipulse.db"
    model_dir = tmp_path / "models"
    generate_sample_data(data_dir, random_seed=42, num_machines=30, days=100)
    rebuild_database_from_csvs(data_dir=data_dir, db_path=db_path, reset=True)
    build_features_from_database(db_path=db_path, write=True)

    metadata = train_model(db_path=db_path, model_dir=model_dir, random_seed=42)

    assert (model_dir / "risk_model.pkl").exists()
    assert (model_dir / "model_metadata.json").exists()
    assert "recall" in metadata["metrics"]
    assert metadata["simulated_data_warning"]

    model = load_model(model_dir / "risk_model.pkl")
    assert "pipeline" in model

    conn = get_connection(db_path)
    try:
        model_runs = read_table(conn, "model_runs")
        predictions = read_table(conn, "risk_predictions")
    finally:
        conn.close()

    assert len(model_runs) == 1
    assert len(predictions) == 30
    assert predictions["risk_score"].between(0, 1).all()
    assert {"high", "medium", "low"}.intersection(set(predictions["risk_level"]))
