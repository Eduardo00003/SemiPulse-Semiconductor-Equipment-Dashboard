"""Train and persist a local scikit-learn machine risk model."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from semipulse.config import ensure_runtime_dirs, get_settings
from semipulse.database import get_connection, read_table
from semipulse.features import CATEGORICAL_FEATURE_COLUMNS, NUMERIC_FEATURE_COLUMNS, build_features_from_database
from semipulse.logging_utils import configure_logging
from semipulse.metrics import calculate_classification_metrics
from semipulse.predict import score_features, write_predictions

SIMULATED_DATA_WARNING = (
    "Model metrics are simulated-data performance only and do not represent real semiconductor factory accuracy."
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _feature_columns(features: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    numeric = [column for column in NUMERIC_FEATURE_COLUMNS if column in features.columns]
    categorical = [column for column in CATEGORICAL_FEATURE_COLUMNS if column in features.columns]
    return numeric, categorical, [*numeric, *categorical]


def _train_test_split(X: pd.DataFrame, y: pd.Series, random_seed: int):
    class_counts = y.value_counts()
    stratify = y if len(class_counts) > 1 and class_counts.min() >= 2 else None
    if len(X) < 4:
        return X, X, y, y
    return train_test_split(X, y, test_size=0.25, random_state=random_seed, stratify=stratify)


def _build_pipeline(numeric_columns: list[str], categorical_columns: list[str], random_seed: int) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", SimpleImputer(strategy="median"), numeric_columns),
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical_columns,
            ),
        ],
        remainder="drop",
    )
    classifier = RandomForestClassifier(
        n_estimators=200,
        random_state=random_seed,
        class_weight="balanced",
    )
    return Pipeline([("preprocessor", preprocessor), ("classifier", classifier)])


def _positive_probabilities(pipeline: Pipeline, X: pd.DataFrame):
    probabilities = pipeline.predict_proba(X)
    classes = list(pipeline.classes_)
    if 1 in classes:
        return probabilities[:, classes.index(1)]
    if classes == [1]:
        return [1.0] * len(X)
    return [0.0] * len(X)


def load_model(model_path: Path | str | None = None):
    """Load a saved model artifact."""

    settings = get_settings()
    path = Path(model_path) if model_path is not None else settings.model_dir / "risk_model.pkl"
    return joblib.load(path)


def _insert_model_run(connection, metadata: dict) -> None:
    connection.execute(
        """
        INSERT INTO model_runs (
            model_run_id, model_type, training_timestamp, prediction_window_days,
            random_seed, metrics_json, feature_columns_json, artifact_path,
            metadata_path, simulated_data_warning
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            metadata["model_run_id"],
            metadata["model_type"],
            metadata["training_timestamp"],
            metadata["prediction_window_days"],
            metadata["random_seed"],
            json.dumps(metadata["metrics"], sort_keys=True),
            json.dumps(metadata["feature_columns"]),
            metadata["artifact_path"],
            metadata["metadata_path"],
            metadata["simulated_data_warning"],
        ),
    )


def train_model(
    db_path: Path | str | None = None,
    model_dir: Path | str | None = None,
    random_seed: int | None = None,
) -> dict:
    """Train the baseline model, persist metadata, and write predictions."""

    settings = get_settings()
    ensure_runtime_dirs(settings)
    seed = settings.random_seed if random_seed is None else random_seed
    resolved_model_dir = Path(model_dir) if model_dir is not None else settings.model_dir
    resolved_model_dir.mkdir(parents=True, exist_ok=True)

    with get_connection(db_path) as connection:
        features = read_table(connection, "machine_features")
        if features.empty:
            features = build_features_from_database(db_path=db_path, write=True)

        numeric_columns, categorical_columns, feature_columns = _feature_columns(features)
        X = features[feature_columns].copy()
        y = pd.to_numeric(features["target_failure_within_window"], errors="coerce").fillna(0).astype(int)
        X_train, X_test, y_train, y_test = _train_test_split(X, y, seed)

        pipeline = _build_pipeline(numeric_columns, categorical_columns, seed)
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_proba = _positive_probabilities(pipeline, X_test)
        metrics = calculate_classification_metrics(y_test, y_pred, y_proba)

        model_run_id = f"model-{uuid4().hex}"
        artifact_path = resolved_model_dir / "risk_model.pkl"
        metadata_path = resolved_model_dir / "model_metadata.json"
        artifact = {
            "pipeline": pipeline,
            "feature_columns": feature_columns,
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "model_run_id": model_run_id,
        }
        joblib.dump(artifact, artifact_path)

        metadata = {
            "model_run_id": model_run_id,
            "model_type": "RandomForestClassifier",
            "training_timestamp": _utc_now(),
            "prediction_window_days": settings.prediction_window_days,
            "random_seed": seed,
            "feature_columns": feature_columns,
            "metrics": metrics,
            "artifact_path": str(artifact_path),
            "metadata_path": str(metadata_path),
            "simulated_data_warning": SIMULATED_DATA_WARNING,
        }
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")

        _insert_model_run(connection, metadata)
        predictions = score_features(artifact, features, model_run_id)
        write_predictions(connection, predictions, if_exists="replace")
        connection.commit()

    return metadata


def main() -> None:
    configure_logging()
    metadata = train_model()
    print("Trained simulated-data risk model")
    print(f"model_run_id={metadata['model_run_id']}")
    print(f"metrics={metadata['metrics']}")


if __name__ == "__main__":
    main()
