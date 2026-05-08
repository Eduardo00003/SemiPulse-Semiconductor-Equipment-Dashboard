"""Model Performance dashboard page."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from semipulse.database import get_connection, read_table
from semipulse.metrics import load_latest_model_metadata
from semipulse.model import train_model
from semipulse.plots import prepare_confusion_matrix


def _read(table_name: str) -> pd.DataFrame:
    try:
        with get_connection() as connection:
            return read_table(connection, table_name)
    except Exception:
        return pd.DataFrame()


def _latest_model_run(model_runs: pd.DataFrame) -> dict:
    if model_runs.empty:
        return {}
    latest = model_runs.sort_values("training_timestamp").tail(1).iloc[0].to_dict()
    metrics_raw = latest.get("metrics_json")
    feature_raw = latest.get("feature_columns_json")
    latest["metrics"] = json.loads(metrics_raw) if isinstance(metrics_raw, str) and metrics_raw else {}
    latest["feature_columns"] = json.loads(feature_raw) if isinstance(feature_raw, str) and feature_raw else []
    return latest


def render() -> None:
    st.title("Model Performance")
    st.caption("Simulated-data metrics for the local scikit-learn risk model")
    st.warning("All metrics shown here are simulated-data performance only.")

    model_runs = _read("model_runs")
    predictions = _read("risk_predictions")
    metadata = load_latest_model_metadata()
    latest_run = _latest_model_run(model_runs)
    if not latest_run and not metadata:
        st.info("Model metadata is not available. Run the full demo pipeline first.")
        return

    metrics = metadata.get("metrics") or latest_run.get("metrics", {})
    metric_cols = st.columns(5)
    metric_cols[0].metric("Recall", f"{metrics.get('recall', 0):.2f}")
    metric_cols[1].metric("Precision", f"{metrics.get('precision', 0):.2f}")
    metric_cols[2].metric("F1", f"{metrics.get('f1', 0):.2f}")
    metric_cols[3].metric("Accuracy", f"{metrics.get('accuracy', 0):.2f}")
    roc_auc = metrics.get("roc_auc")
    metric_cols[4].metric("ROC-AUC", "N/A" if roc_auc is None else f"{roc_auc:.2f}")

    st.subheader("Confusion Matrix")
    confusion = prepare_confusion_matrix(metrics)
    if confusion.empty:
        st.info("Confusion matrix is not available for this run.")
    else:
        st.dataframe(confusion, use_container_width=True)

    st.subheader("Why Recall Matters")
    st.write(
        "Recall measures how many truly high-risk simulated machines were caught by the model. "
        "For predictive maintenance prioritization, missed high-risk machines can be more costly than false alarms, "
        "so recall is more informative than accuracy alone. These results are generated from simulated data only."
    )

    st.subheader("Model Metadata")
    display_metadata = {
        "model_run_id": metadata.get("model_run_id") or latest_run.get("model_run_id"),
        "model_type": metadata.get("model_type") or latest_run.get("model_type"),
        "training_timestamp": metadata.get("training_timestamp") or latest_run.get("training_timestamp"),
        "prediction_window_days": metadata.get("prediction_window_days") or latest_run.get("prediction_window_days"),
        "random_seed": metadata.get("random_seed") or latest_run.get("random_seed"),
        "artifact_path": metadata.get("artifact_path") or latest_run.get("artifact_path"),
        "simulated_data_warning": metadata.get("simulated_data_warning") or latest_run.get("simulated_data_warning"),
    }
    st.json(display_metadata)

    with st.expander("Feature Columns"):
        st.write(metadata.get("feature_columns") or latest_run.get("feature_columns", []))

    st.subheader("Prediction Summary")
    if predictions.empty:
        st.info("No predictions are stored yet.")
    else:
        st.dataframe(
            predictions.groupby("risk_level", as_index=False)
            .agg(machine_count=("machine_id", "count"), avg_risk_score=("risk_score", "mean"))
            .sort_values("avg_risk_score", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

    if st.button("Retrain model", use_container_width=True):
        with st.spinner("Training model and updating predictions"):
            updated = train_model()
        st.success(f"Trained model run {updated['model_run_id']}.")
        st.rerun()
