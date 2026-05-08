"""Data Upload / Load dashboard page."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from semipulse.config import get_settings
from semipulse.data_loader import load_csv_datasets
from semipulse.pipeline import run_demo_pipeline, save_uploaded_datasets, validate_data_directory
from semipulse.sample_data import DATASET_FILENAMES, generate_sample_data


def _preview_datasets(data_dir: Path) -> None:
    try:
        datasets = load_csv_datasets(data_dir)
    except Exception as exc:
        st.error(f"Could not load datasets: {exc}")
        return

    for name, dataframe in datasets.items():
        with st.expander(f"{name} ({len(dataframe):,} rows)", expanded=name == "machines"):
            st.dataframe(dataframe.head(50), use_container_width=True, hide_index=True)


def _show_validation(data_dir: Path) -> None:
    try:
        result = validate_data_directory(data_dir)
    except Exception as exc:
        st.error(f"Validation could not run: {exc}")
        return

    issues = result.to_dataframe()
    if result.is_valid:
        st.success("Datasets passed validation.")
    else:
        st.error(f"Validation found {len(result.errors)} blocking issue(s).")
    if not issues.empty:
        st.dataframe(issues, use_container_width=True, hide_index=True)


def render() -> None:
    """Render the Data Upload / Load page."""

    settings = get_settings()
    st.title("Data Upload / Load")
    st.warning(
        "Loaded datasets are treated as simulated demo data unless clearly replaced and documented. Model metrics remain simulated-data performance for this MVP."
    )

    st.subheader("Sample Data")
    sample_cols = st.columns(3)
    if sample_cols[0].button("Generate sample data", use_container_width=True):
        paths = generate_sample_data(settings.data_dir)
        st.success(f"Generated {len(paths)} sample CSV files in {settings.data_dir}.")
    if sample_cols[1].button("Validate sample data", use_container_width=True):
        _show_validation(settings.data_dir)
    if sample_cols[2].button("Run full demo pipeline", use_container_width=True):
        with st.spinner("Running demo pipeline"):
            summary = run_demo_pipeline(generate_data=True, reset_database=True, train_model=True)
        st.success("Demo pipeline completed.")
        st.json(summary)

    st.subheader("Upload CSVs")
    uploads = {
        "machines": st.file_uploader("machines.csv", type="csv", key="machines_upload"),
        "sensor_readings": st.file_uploader("sensor_readings.csv", type="csv", key="sensor_upload"),
        "maintenance_records": st.file_uploader("maintenance_records.csv", type="csv", key="maintenance_upload"),
        "defect_records": st.file_uploader("defect_records.csv", type="csv", key="defect_upload"),
    }
    uploaded_files = {name: file for name, file in uploads.items() if file is not None}
    upload_dir = Path("data/raw/uploads")
    if uploaded_files and st.button("Save uploaded CSVs", use_container_width=True):
        if set(uploaded_files) != set(DATASET_FILENAMES):
            st.error("Upload all four required CSV files before saving.")
        else:
            saved = save_uploaded_datasets(uploaded_files, upload_dir)
            st.success(f"Saved uploads to {upload_dir}.")
            st.json({name: str(path) for name, path in saved.items()})

    st.subheader("Preview")
    preview_source = st.radio("Preview source", ["Sample data", "Uploaded data"], horizontal=True)
    preview_dir = settings.data_dir if preview_source == "Sample data" else upload_dir
    _preview_datasets(preview_dir)

    st.subheader("Rebuild SQLite")
    rebuild_source = st.radio("Rebuild from", ["Sample data", "Uploaded data"], horizontal=True, key="rebuild_source")
    source_dir = settings.data_dir if rebuild_source == "Sample data" else upload_dir
    if st.button("Validate and rebuild database", type="primary", use_container_width=True):
        try:
            _show_validation(source_dir)
            from semipulse.data_loader import rebuild_database_from_csvs
            from semipulse.features import build_features_from_database
            from semipulse.model import train_model

            row_counts = rebuild_database_from_csvs(data_dir=source_dir, reset=True)
            features = build_features_from_database(write=True)
            metadata = train_model()
            st.success("Database, features, model, and predictions rebuilt.")
            st.json(
                {
                    "row_counts": row_counts,
                    "feature_rows": len(features),
                    "model_run_id": metadata["model_run_id"],
                    "metrics": metadata["metrics"],
                }
            )
        except Exception as exc:
            st.error(f"Pipeline rebuild failed: {exc}")
