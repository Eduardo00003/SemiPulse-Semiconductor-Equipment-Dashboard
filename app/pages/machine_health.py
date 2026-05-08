"""Machine Health dashboard page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from semipulse.database import get_connection, read_table
from semipulse.plots import prepare_fleet_sensor_averages, prepare_sensor_timeseries


def _read(table_name: str) -> pd.DataFrame:
    try:
        with get_connection() as connection:
            return read_table(connection, table_name)
    except Exception:
        return pd.DataFrame()


def _filter_options(dataframe: pd.DataFrame, column: str) -> list[str]:
    if dataframe.empty or column not in dataframe:
        return []
    return sorted(dataframe[column].dropna().astype(str).unique().tolist())


def _apply_machine_filters(
    machines: pd.DataFrame,
    machine_type: list[str],
    area: list[str],
    manufacturer: list[str],
) -> pd.DataFrame:
    filtered = machines.copy()
    if machine_type:
        filtered = filtered[filtered["machine_type"].astype(str).isin(machine_type)]
    if area:
        filtered = filtered[filtered["facility_area"].astype(str).isin(area)]
    if manufacturer:
        filtered = filtered[filtered["manufacturer"].astype(str).isin(manufacturer)]
    return filtered


def render() -> None:
    """Render the Machine Health page."""

    st.title("Machine Health")
    st.caption("Sensor trends and equipment context for simulated machines")

    machines = _read("machines")
    sensors = _read("sensor_readings")
    features = _read("machine_features")
    predictions = _read("risk_predictions")

    if machines.empty or sensors.empty:
        st.info("Machine health data is not available yet. Run the demo pipeline from the Data Upload / Load page.")
        return

    filter_cols = st.columns(3)
    selected_types = filter_cols[0].multiselect("Machine type", _filter_options(machines, "machine_type"))
    selected_areas = filter_cols[1].multiselect("Facility area", _filter_options(machines, "facility_area"))
    selected_manufacturers = filter_cols[2].multiselect("Manufacturer", _filter_options(machines, "manufacturer"))
    filtered_machines = _apply_machine_filters(machines, selected_types, selected_areas, selected_manufacturers)

    machine_ids = filtered_machines["machine_id"].astype(str).tolist()
    if not machine_ids:
        st.warning("No machines match the selected filters.")
        return

    selected_machine = st.selectbox("Machine", machine_ids)
    sensor_frame = prepare_sensor_timeseries(sensors, selected_machine)
    if sensor_frame.empty:
        st.info("No sensor readings are available for this machine.")
        return

    date_min = sensor_frame["timestamp"].min().date()
    date_max = sensor_frame["timestamp"].max().date()
    date_range = st.date_input("Date range", value=(date_min, date_max), min_value=date_min, max_value=date_max)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
        sensor_frame = sensor_frame[(sensor_frame["timestamp"] >= start) & (sensor_frame["timestamp"] < end)]

    st.subheader("Machine Detail")
    machine_row = machines[machines["machine_id"] == selected_machine].head(1)
    feature_row = features[features["machine_id"] == selected_machine].head(1) if not features.empty else pd.DataFrame()
    prediction_row = predictions[predictions["machine_id"] == selected_machine].head(1) if not predictions.empty else pd.DataFrame()

    detail_cols = st.columns(4)
    detail_cols[0].metric("Type", machine_row.iloc[0].get("machine_type", "Unknown"))
    detail_cols[1].metric("Area", machine_row.iloc[0].get("facility_area", "Unknown"))
    detail_cols[2].metric(
        "Risk score",
        f"{float(prediction_row.iloc[0]['risk_score']):.2f}" if not prediction_row.empty else "N/A",
    )
    detail_cols[3].metric(
        "Days since service",
        f"{float(feature_row.iloc[0]['days_since_last_maintenance']):.0f}" if not feature_row.empty else "N/A",
    )

    st.subheader("Sensor Trends")
    chart_cols = st.columns(2)
    chart_cols[0].line_chart(sensor_frame, x="timestamp", y=["temperature", "vibration"])
    chart_cols[1].line_chart(sensor_frame, x="timestamp", y=["pressure", "power_draw"])

    st.subheader("Fleet Averages")
    fleet_averages = prepare_fleet_sensor_averages(sensors)
    if not fleet_averages.empty:
        st.line_chart(fleet_averages, x="timestamp", y=["temperature", "vibration", "pressure", "power_draw"])

    st.subheader("Heuristic Anomaly Indicators")
    thresholds = sensors[["temperature", "vibration", "pressure", "power_draw"]].quantile(0.95)
    latest = sensor_frame.sort_values("timestamp").tail(1).iloc[0]
    anomaly_cols = st.columns(4)
    for idx, metric in enumerate(["temperature", "vibration", "pressure", "power_draw"]):
        value = float(latest[metric])
        threshold = float(thresholds[metric])
        anomaly_cols[idx].metric(metric.replace("_", " ").title(), f"{value:.2f}", delta="above p95" if value > threshold else "normal")

    st.caption("Anomaly indicators are simple simulated-data heuristics, not validated factory alarms.")
