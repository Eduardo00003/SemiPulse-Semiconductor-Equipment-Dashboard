"""Chart preparation helpers for Streamlit pages."""

from __future__ import annotations

import pandas as pd


def prepare_risk_distribution(predictions: pd.DataFrame) -> pd.DataFrame:
    """Prepare risk-level counts for a bar chart."""

    if predictions.empty or "risk_level" not in predictions:
        return pd.DataFrame(columns=["risk_level", "machine_count"])
    order = ["high", "medium", "low"]
    counts = (
        predictions.assign(risk_level=predictions["risk_level"].astype(str).str.lower())
        .groupby("risk_level", as_index=False)
        .agg(machine_count=("machine_id", "count"))
    )
    counts["sort_order"] = counts["risk_level"].map({level: idx for idx, level in enumerate(order)}).fillna(99)
    return counts.sort_values("sort_order").drop(columns=["sort_order"]).reset_index(drop=True)


def prepare_downtime_summary(maintenance: pd.DataFrame) -> pd.DataFrame:
    """Prepare downtime totals by maintenance type."""

    if maintenance.empty or not {"maintenance_type", "downtime_hours"}.issubset(maintenance.columns):
        return pd.DataFrame(columns=["maintenance_type", "downtime_hours"])
    summary = (
        maintenance.assign(maintenance_type=maintenance["maintenance_type"].astype(str).str.lower())
        .groupby("maintenance_type", as_index=False)
        .agg(downtime_hours=("downtime_hours", "sum"))
        .sort_values("downtime_hours", ascending=False)
    )
    return summary.reset_index(drop=True)


def prepare_sensor_timeseries(sensor_readings: pd.DataFrame, machine_id: str | None = None) -> pd.DataFrame:
    """Prepare sensor readings for time-series charts."""

    if sensor_readings.empty:
        return pd.DataFrame(columns=["timestamp", "temperature", "vibration", "pressure", "power_draw"])
    frame = sensor_readings.copy()
    if machine_id is not None and "machine_id" in frame:
        frame = frame[frame["machine_id"].astype(str) == str(machine_id)]
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce", format="mixed")
    return frame.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)


def prepare_fleet_sensor_averages(sensor_readings: pd.DataFrame) -> pd.DataFrame:
    """Prepare daily fleet-average sensor values."""

    if sensor_readings.empty:
        return pd.DataFrame(columns=["timestamp", "temperature", "vibration", "pressure", "power_draw"])
    frame = prepare_sensor_timeseries(sensor_readings)
    if frame.empty:
        return frame
    frame["timestamp"] = frame["timestamp"].dt.floor("D")
    return (
        frame.groupby("timestamp", as_index=False)
        .agg(
            temperature=("temperature", "mean"),
            vibration=("vibration", "mean"),
            pressure=("pressure", "mean"),
            power_draw=("power_draw", "mean"),
        )
        .sort_values("timestamp")
        .reset_index(drop=True)
    )


def prepare_risk_level_counts(predictions: pd.DataFrame) -> pd.DataFrame:
    """Prepare risk-level counts in high, medium, low order."""

    return prepare_risk_distribution(predictions)
