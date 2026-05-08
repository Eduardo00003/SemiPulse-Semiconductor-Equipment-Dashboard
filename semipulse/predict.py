"""Risk scoring helpers."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

import numpy as np
import pandas as pd


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def risk_level_from_score(score: float) -> str:
    if score >= 0.70:
        return "high"
    if score >= 0.40:
        return "medium"
    return "low"


def _positive_class_probability(pipeline, feature_frame: pd.DataFrame) -> np.ndarray:
    if not hasattr(pipeline, "predict_proba"):
        return pipeline.predict(feature_frame).astype(float)

    probabilities = pipeline.predict_proba(feature_frame)
    classes = list(getattr(pipeline, "classes_", []))
    if 1 in classes:
        return probabilities[:, classes.index(1)]
    if classes == [1]:
        return np.ones(len(feature_frame))
    return np.zeros(len(feature_frame))


def score_features(model: object, features: pd.DataFrame, model_run_id: str) -> pd.DataFrame:
    """Score machine feature rows with a trained model artifact."""

    artifact = model if isinstance(model, dict) else {"pipeline": model}
    pipeline = artifact["pipeline"]
    feature_columns = artifact.get(
        "feature_columns",
        [column for column in features.columns if column not in {"machine_id", "feature_timestamp", "target_failure_within_window", "created_at"}],
    )
    feature_frame = features[feature_columns].copy()
    risk_scores = _positive_class_probability(pipeline, feature_frame)
    timestamp = _utc_now()

    predictions = pd.DataFrame(
        {
            "prediction_id": [f"pred-{uuid4().hex}" for _ in range(len(features))],
            "machine_id": features["machine_id"].values,
            "model_run_id": model_run_id,
            "risk_score": risk_scores.astype(float),
            "predicted_failure_flag": (risk_scores >= 0.5).astype(int),
            "risk_level": [risk_level_from_score(float(score)) for score in risk_scores],
            "prediction_timestamp": timestamp,
        }
    )
    return predictions.sort_values(["risk_score", "machine_id"], ascending=[False, True]).reset_index(drop=True)


def write_predictions(
    connection: sqlite3.Connection,
    predictions: pd.DataFrame,
    if_exists: str = "replace",
) -> int:
    """Write risk predictions to SQLite."""

    if if_exists == "replace":
        connection.execute("DELETE FROM risk_predictions")
        predictions.to_sql("risk_predictions", connection, if_exists="append", index=False)
    else:
        predictions.to_sql("risk_predictions", connection, if_exists=if_exists, index=False)
    connection.commit()
    return len(predictions)


def build_ranked_risk_table(connection: sqlite3.Connection) -> pd.DataFrame:
    """Return a dashboard-ready ranked risk table."""

    query = """
        SELECT
            rp.machine_id,
            m.machine_type,
            m.facility_area,
            m.manufacturer,
            rp.risk_score,
            rp.risk_level,
            rp.predicted_failure_flag,
            mf.recent_downtime_hours,
            mf.recent_defect_count,
            mf.days_since_last_maintenance,
            mf.avg_vibration,
            mf.max_temperature,
            rp.model_run_id,
            rp.prediction_timestamp
        FROM risk_predictions rp
        LEFT JOIN machines m ON m.machine_id = rp.machine_id
        LEFT JOIN machine_features mf ON mf.machine_id = rp.machine_id
        ORDER BY rp.risk_score DESC, rp.machine_id ASC
    """
    ranked = pd.read_sql_query(query, connection)
    if ranked.empty:
        ranked.insert(0, "rank", [])
        return ranked
    ranked.insert(0, "rank", range(1, len(ranked) + 1))
    return ranked
