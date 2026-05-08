"""Downtime Analysis dashboard page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from semipulse.database import get_connection, read_table
from semipulse.plots import prepare_downtime_by_machine, prepare_risk_relationship


def _read(table_name: str) -> pd.DataFrame:
    try:
        with get_connection() as connection:
            return read_table(connection, table_name)
    except Exception:
        return pd.DataFrame()


def render() -> None:
    st.title("Downtime Analysis")
    st.caption("Simulated maintenance downtime patterns and risk context")

    maintenance = _read("maintenance_records")
    machines = _read("machines")
    features = _read("machine_features")
    predictions = _read("risk_predictions")
    if maintenance.empty:
        st.info("Maintenance records are not available. Run the demo pipeline from Data Upload / Load.")
        return

    maintenance = maintenance.copy()
    maintenance["maintenance_date"] = pd.to_datetime(maintenance["maintenance_date"], errors="coerce", format="mixed")
    if not machines.empty:
        maintenance = maintenance.merge(
            machines[["machine_id", "machine_type", "facility_area", "manufacturer"]],
            on="machine_id",
            how="left",
        )

    filter_cols = st.columns(3)
    selected_types = filter_cols[0].multiselect(
        "Machine type",
        sorted(maintenance.get("machine_type", pd.Series(dtype=str)).dropna().astype(str).unique().tolist()),
    )
    selected_areas = filter_cols[1].multiselect(
        "Facility area",
        sorted(maintenance.get("facility_area", pd.Series(dtype=str)).dropna().astype(str).unique().tolist()),
    )
    selected_maintenance = filter_cols[2].multiselect(
        "Maintenance type",
        sorted(maintenance.get("maintenance_type", pd.Series(dtype=str)).dropna().astype(str).unique().tolist()),
    )

    filtered = maintenance.copy()
    if selected_types:
        filtered = filtered[filtered["machine_type"].astype(str).isin(selected_types)]
    if selected_areas:
        filtered = filtered[filtered["facility_area"].astype(str).isin(selected_areas)]
    if selected_maintenance:
        filtered = filtered[filtered["maintenance_type"].astype(str).isin(selected_maintenance)]

    metric_cols = st.columns(4)
    metric_cols[0].metric("Maintenance events", f"{len(filtered):,}")
    metric_cols[1].metric("Downtime hours", f"{filtered['downtime_hours'].sum():,.1f}")
    metric_cols[2].metric("Machines serviced", f"{filtered['machine_id'].nunique():,}")
    metric_cols[3].metric("Avg downtime", f"{filtered['downtime_hours'].mean():.2f} h")

    st.subheader("Downtime by Machine")
    by_machine = prepare_downtime_by_machine(filtered, machines=None)
    if not by_machine.empty:
        st.bar_chart(by_machine.head(20), x="machine_id", y="downtime_hours")

    st.subheader("Downtime by Maintenance Type")
    by_type = (
        filtered.groupby("maintenance_type", as_index=False)
        .agg(downtime_hours=("downtime_hours", "sum"), events=("maintenance_id", "count"))
        .sort_values("downtime_hours", ascending=False)
    )
    st.dataframe(by_type, use_container_width=True, hide_index=True)

    if "machine_type" in filtered:
        st.subheader("Downtime by Machine Type")
        by_machine_type = (
            filtered.groupby("machine_type", as_index=False)
            .agg(downtime_hours=("downtime_hours", "sum"))
            .sort_values("downtime_hours", ascending=False)
        )
        st.bar_chart(by_machine_type, x="machine_type", y="downtime_hours")

    if not features.empty and not predictions.empty:
        st.subheader("Downtime and Risk")
        risk_context = prepare_risk_relationship(
            features.merge(predictions[["machine_id", "risk_score", "risk_level"]], on="machine_id", how="left")
        )
        if not risk_context.empty:
            st.dataframe(
                risk_context[
                    [
                        "machine_id",
                        "recent_downtime_hours",
                        "total_downtime_hours",
                        "days_since_last_maintenance",
                        "risk_score",
                        "risk_level",
                    ]
                ]
                .sort_values("total_downtime_hours", ascending=False)
                .head(25),
                use_container_width=True,
                hide_index=True,
            )
