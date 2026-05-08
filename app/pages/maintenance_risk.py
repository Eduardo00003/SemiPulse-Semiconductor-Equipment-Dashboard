"""Maintenance Risk dashboard page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from semipulse.database import get_connection, read_table
from semipulse.model import train_model
from semipulse.plots import prepare_risk_level_counts
from semipulse.predict import build_ranked_risk_table


def _load_ranked_table() -> pd.DataFrame:
    try:
        with get_connection() as connection:
            return build_ranked_risk_table(connection)
    except Exception:
        return pd.DataFrame()


def _options(dataframe: pd.DataFrame, column: str) -> list[str]:
    if dataframe.empty or column not in dataframe:
        return []
    return sorted(dataframe[column].dropna().astype(str).unique().tolist())


def render() -> None:
    """Render the Maintenance Risk page."""

    st.title("Maintenance Risk")
    st.caption("Ranked simulated maintenance risk for machine prioritization")
    st.warning("Risk scores and model metrics are simulated-data outputs only.")

    ranked = _load_ranked_table()
    if ranked.empty:
        st.info("Risk predictions are not available. Run the full demo pipeline from Data Upload / Load.")
        return

    filters = st.columns(4)
    risk_levels = filters[0].multiselect("Risk level", _options(ranked, "risk_level"), default=_options(ranked, "risk_level"))
    machine_types = filters[1].multiselect("Machine type", _options(ranked, "machine_type"))
    areas = filters[2].multiselect("Facility area", _options(ranked, "facility_area"))
    manufacturers = filters[3].multiselect("Manufacturer", _options(ranked, "manufacturer"))

    filtered = ranked.copy()
    if risk_levels:
        filtered = filtered[filtered["risk_level"].astype(str).isin(risk_levels)]
    if machine_types:
        filtered = filtered[filtered["machine_type"].astype(str).isin(machine_types)]
    if areas:
        filtered = filtered[filtered["facility_area"].astype(str).isin(areas)]
    if manufacturers:
        filtered = filtered[filtered["manufacturer"].astype(str).isin(manufacturers)]
    if filtered.empty:
        st.warning("No machines match the selected risk filters.")
        return

    sort_map = {
        "Risk score": "risk_score",
        "Recent downtime": "recent_downtime_hours",
        "Recent defects": "recent_defect_count",
        "Days since maintenance": "days_since_last_maintenance",
    }
    sort_label = st.selectbox("Sort by", list(sort_map), index=0)
    filtered = filtered.sort_values(sort_map[sort_label], ascending=False).reset_index(drop=True)
    filtered["rank"] = range(1, len(filtered) + 1)

    metric_cols = st.columns(4)
    metric_cols[0].metric("Machines shown", f"{len(filtered):,}")
    metric_cols[1].metric("High risk", f"{(filtered['risk_level'] == 'high').sum():,}")
    metric_cols[2].metric("Medium risk", f"{(filtered['risk_level'] == 'medium').sum():,}")
    metric_cols[3].metric("Average score", f"{filtered['risk_score'].mean():.2f}" if not filtered.empty else "0.00")

    risk_counts = prepare_risk_level_counts(filtered)
    if not risk_counts.empty:
        st.bar_chart(risk_counts, x="risk_level", y="machine_count")

    st.subheader("Ranked Machines")
    display_columns = [
        "rank",
        "machine_id",
        "machine_type",
        "facility_area",
        "manufacturer",
        "risk_score",
        "risk_level",
        "predicted_failure_flag",
        "recent_downtime_hours",
        "recent_defect_count",
        "days_since_last_maintenance",
        "avg_vibration",
        "max_temperature",
        "model_run_id",
        "prediction_timestamp",
    ]
    st.dataframe(filtered[display_columns], use_container_width=True, hide_index=True)

    st.subheader("Machine Detail")
    selected_machine = st.selectbox("Inspect machine", filtered["machine_id"].tolist())
    selected = filtered[filtered["machine_id"] == selected_machine].head(1)
    if not selected.empty:
        row = selected.iloc[0]
        detail_cols = st.columns(4)
        detail_cols[0].metric("Risk score", f"{float(row['risk_score']):.2f}")
        detail_cols[1].metric("Risk level", str(row["risk_level"]).title())
        detail_cols[2].metric("Recent defects", f"{float(row['recent_defect_count']):.0f}")
        detail_cols[3].metric("Recent downtime", f"{float(row['recent_downtime_hours']):.1f} h")
        st.write(
            {
                "machine_id": row["machine_id"],
                "machine_type": row["machine_type"],
                "facility_area": row["facility_area"],
                "manufacturer": row["manufacturer"],
                "days_since_last_maintenance": row["days_since_last_maintenance"],
                "avg_vibration": row["avg_vibration"],
                "max_temperature": row["max_temperature"],
            }
        )

    if st.button("Retrain model and refresh risk scores", use_container_width=True):
        with st.spinner("Training model and updating predictions"):
            metadata = train_model()
        st.success(f"Updated predictions with model run {metadata['model_run_id']}.")
        st.rerun()
