"""Defect Trends dashboard page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from semipulse.database import get_connection, read_table
from semipulse.plots import prepare_defect_trends, prepare_risk_relationship


def _read(table_name: str) -> pd.DataFrame:
    try:
        with get_connection() as connection:
            return read_table(connection, table_name)
    except Exception:
        return pd.DataFrame()


def render() -> None:
    st.title("Defect Trends")
    st.caption("Simulated production defect patterns by machine, process, and risk")

    defects = _read("defect_records")
    machines = _read("machines")
    features = _read("machine_features")
    predictions = _read("risk_predictions")
    if defects.empty:
        st.info("Defect records are not available. Run the demo pipeline from Data Upload / Load.")
        return

    defects = defects.copy()
    defects["timestamp"] = pd.to_datetime(defects["timestamp"], errors="coerce", format="mixed")
    if not machines.empty:
        defects = defects.merge(
            machines[["machine_id", "machine_type", "facility_area", "process_step"]],
            on="machine_id",
            how="left",
            suffixes=("", "_machine"),
        )

    filter_cols = st.columns(3)
    machine_options = sorted(defects["machine_id"].dropna().astype(str).unique().tolist())
    selected_machines = filter_cols[0].multiselect("Machine", machine_options)
    area_options = sorted(defects.get("facility_area", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())
    selected_areas = filter_cols[1].multiselect("Facility area", area_options)
    type_options = sorted(defects.get("defect_type", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())
    selected_types = filter_cols[2].multiselect("Defect type", type_options)

    filtered = defects.copy()
    if selected_machines:
        filtered = filtered[filtered["machine_id"].astype(str).isin(selected_machines)]
    if selected_areas and "facility_area" in filtered:
        filtered = filtered[filtered["facility_area"].astype(str).isin(selected_areas)]
    if selected_types and "defect_type" in filtered:
        filtered = filtered[filtered["defect_type"].astype(str).isin(selected_types)]

    metric_cols = st.columns(4)
    metric_cols[0].metric("Defect records", f"{len(filtered):,}")
    metric_cols[1].metric("Total defects", f"{int(filtered['defect_count'].sum()):,}")
    metric_cols[2].metric("Machines affected", f"{filtered['machine_id'].nunique():,}")
    metric_cols[3].metric("Avg defects/batch", f"{filtered['defect_count'].mean():.2f}")

    trends = prepare_defect_trends(filtered, machines=None)
    if not trends.empty:
        st.subheader("Defects Over Time")
        st.line_chart(trends, x="timestamp", y="defect_count")

    st.subheader("Defects by Machine")
    by_machine = (
        filtered.groupby("machine_id", as_index=False)
        .agg(defect_count=("defect_count", "sum"))
        .sort_values("defect_count", ascending=False)
        .head(20)
    )
    st.bar_chart(by_machine, x="machine_id", y="defect_count")

    optional_cols = [column for column in ["defect_type", "facility_area", "process_step", "batch_id", "wafer_lot"] if column in filtered]
    for column in optional_cols[:4]:
        grouped = (
            filtered.groupby(column, as_index=False)
            .agg(defect_count=("defect_count", "sum"))
            .sort_values("defect_count", ascending=False)
            .head(20)
        )
        with st.expander(f"Defects by {column.replace('_', ' ')}"):
            st.dataframe(grouped, use_container_width=True, hide_index=True)

    if not features.empty and not predictions.empty:
        st.subheader("Defects and Risk")
        risk_context = prepare_risk_relationship(
            features.merge(predictions[["machine_id", "risk_score", "risk_level"]], on="machine_id", how="left")
        )
        if not risk_context.empty:
            st.dataframe(
                risk_context[["machine_id", "recent_defect_count", "total_defect_count", "risk_score", "risk_level"]]
                .sort_values("risk_score", ascending=False)
                .head(25),
                use_container_width=True,
                hide_index=True,
            )
