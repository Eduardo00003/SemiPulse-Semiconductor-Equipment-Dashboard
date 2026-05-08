"""Feature engineering for SemiPulse machine risk modeling."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from semipulse.config import get_settings
from semipulse.database import get_connection, read_table
from semipulse.logging_utils import configure_logging

NUMERIC_FEATURE_COLUMNS = [
    "avg_temperature",
    "max_temperature",
    "std_temperature",
    "avg_vibration",
    "max_vibration",
    "std_vibration",
    "avg_pressure",
    "var_pressure",
    "avg_power_draw",
    "var_power_draw",
    "rolling_7d_avg_temperature",
    "rolling_7d_avg_vibration",
    "rolling_7d_defect_count",
    "rolling_30d_maintenance_count",
    "recent_downtime_hours",
    "days_since_last_maintenance",
    "total_maintenance_events",
    "total_downtime_hours",
    "avg_downtime_per_event",
    "emergency_maintenance_count",
    "maintenance_frequency",
    "total_defect_count",
    "recent_defect_count",
    "avg_defects_per_batch",
    "defect_severity_score",
    "yield_loss_pct_avg",
    "machine_age_days",
]

CATEGORICAL_FEATURE_COLUMNS = [
    "machine_type",
    "manufacturer",
    "criticality",
    "facility_area",
]

FEATURE_COLUMNS = NUMERIC_FEATURE_COLUMNS + CATEGORICAL_FEATURE_COLUMNS


def _prepare_dates(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    prepared = {name: dataframe.copy() for name, dataframe in datasets.items()}
    prepared["machines"]["install_date"] = pd.to_datetime(prepared["machines"]["install_date"], errors="coerce", format="mixed")
    prepared["sensor_readings"]["timestamp"] = pd.to_datetime(prepared["sensor_readings"]["timestamp"], errors="coerce", format="mixed")
    prepared["maintenance_records"]["maintenance_date"] = pd.to_datetime(
        prepared["maintenance_records"]["maintenance_date"],
        errors="coerce",
        format="mixed",
    )
    prepared["defect_records"]["timestamp"] = pd.to_datetime(prepared["defect_records"]["timestamp"], errors="coerce", format="mixed")
    return prepared


def _default_as_of_date(datasets: dict[str, pd.DataFrame], prediction_window_days: int) -> pd.Timestamp:
    sensors = datasets["sensor_readings"]
    max_timestamp = pd.to_datetime(sensors["timestamp"], errors="coerce", format="mixed").max()
    if pd.isna(max_timestamp):
        return pd.Timestamp.utcnow().tz_localize(None)
    return (max_timestamp - pd.Timedelta(days=prediction_window_days)).normalize()


def _severity_score(series: pd.Series) -> pd.Series:
    return series.astype("string").str.lower().map({"low": 1, "medium": 2, "high": 3}).fillna(1)


def _safe_merge(base: pd.DataFrame, right: pd.DataFrame, on: str = "machine_id") -> pd.DataFrame:
    if right.empty:
        return base
    return base.merge(right, on=on, how="left")


def build_machine_features(
    datasets: dict[str, pd.DataFrame],
    as_of_date: pd.Timestamp | None = None,
    prediction_window_days: int | None = None,
) -> pd.DataFrame:
    """Generate one model-ready feature row per machine."""

    settings = get_settings()
    window_days = prediction_window_days or settings.prediction_window_days
    prepared = _prepare_dates(datasets)
    resolved_as_of = as_of_date or _default_as_of_date(prepared, window_days)
    resolved_as_of = pd.Timestamp(resolved_as_of).tz_localize(None) if pd.Timestamp(resolved_as_of).tzinfo else pd.Timestamp(resolved_as_of)
    prediction_end = resolved_as_of + pd.Timedelta(days=window_days)

    machines = prepared["machines"].copy()
    sensors = prepared["sensor_readings"]
    maintenance = prepared["maintenance_records"]
    defects = prepared["defect_records"]

    sensors_history = sensors[sensors["timestamp"] <= resolved_as_of]
    maintenance_history = maintenance[maintenance["maintenance_date"] <= resolved_as_of]
    defects_history = defects[defects["timestamp"] <= resolved_as_of]

    features = machines[["machine_id", "machine_type", "manufacturer", "criticality", "facility_area", "install_date"]].copy()
    features["feature_timestamp"] = resolved_as_of.isoformat()
    features["machine_age_days"] = (resolved_as_of - features["install_date"]).dt.days.clip(lower=0)

    sensor_summary = sensors_history.groupby("machine_id", as_index=False).agg(
        avg_temperature=("temperature", "mean"),
        max_temperature=("temperature", "max"),
        std_temperature=("temperature", "std"),
        avg_vibration=("vibration", "mean"),
        max_vibration=("vibration", "max"),
        std_vibration=("vibration", "std"),
        avg_pressure=("pressure", "mean"),
        var_pressure=("pressure", "var"),
        avg_power_draw=("power_draw", "mean"),
        var_power_draw=("power_draw", "var"),
    )
    features = _safe_merge(features, sensor_summary)

    recent_7d_start = resolved_as_of - pd.Timedelta(days=7)
    recent_30d_start = resolved_as_of - pd.Timedelta(days=30)
    recent_sensors = sensors_history[sensors_history["timestamp"] >= recent_7d_start]
    rolling_sensor = recent_sensors.groupby("machine_id", as_index=False).agg(
        rolling_7d_avg_temperature=("temperature", "mean"),
        rolling_7d_avg_vibration=("vibration", "mean"),
    )
    features = _safe_merge(features, rolling_sensor)

    maintenance_summary = maintenance_history.groupby("machine_id", as_index=False).agg(
        total_maintenance_events=("maintenance_id", "count"),
        total_downtime_hours=("downtime_hours", "sum"),
        avg_downtime_per_event=("downtime_hours", "mean"),
        last_maintenance_date=("maintenance_date", "max"),
    )
    emergency_counts = (
        maintenance_history[maintenance_history["maintenance_type"].astype("string").str.lower() == "emergency"]
        .groupby("machine_id", as_index=False)
        .agg(emergency_maintenance_count=("maintenance_id", "count"))
    )
    recent_maintenance = maintenance_history[maintenance_history["maintenance_date"] >= recent_30d_start].groupby("machine_id", as_index=False).agg(
        rolling_30d_maintenance_count=("maintenance_id", "count"),
        recent_downtime_hours=("downtime_hours", "sum"),
    )
    features = _safe_merge(features, maintenance_summary)
    features = _safe_merge(features, emergency_counts)
    features = _safe_merge(features, recent_maintenance)
    if "total_maintenance_events" not in features:
        features["total_maintenance_events"] = 0
    last_maintenance = (
        pd.to_datetime(features["last_maintenance_date"], errors="coerce", format="mixed")
        if "last_maintenance_date" in features
        else pd.Series(pd.NaT, index=features.index)
    )
    features["days_since_last_maintenance"] = (
        resolved_as_of - last_maintenance
    ).dt.days
    features["maintenance_frequency"] = features["total_maintenance_events"] / np.maximum(features["machine_age_days"] / 365.0, 0.1)

    defect_work = defects_history.copy()
    if not defect_work.empty:
        defect_work["severity_numeric"] = _severity_score(defect_work.get("severity", pd.Series(index=defect_work.index)))
    defect_summary = defect_work.groupby("machine_id", as_index=False).agg(
        total_defect_count=("defect_count", "sum"),
        avg_defects_per_batch=("defect_count", "mean"),
        defect_severity_score=("severity_numeric", "mean"),
        yield_loss_pct_avg=("yield_loss_pct", "mean"),
    ) if not defect_work.empty else pd.DataFrame()
    recent_defects = defects_history[defects_history["timestamp"] >= recent_7d_start].groupby("machine_id", as_index=False).agg(
        rolling_7d_defect_count=("defect_count", "sum"),
        recent_defect_count=("defect_count", "sum"),
    )
    features = _safe_merge(features, defect_summary)
    features = _safe_merge(features, recent_defects)

    future_maintenance = maintenance[
        (maintenance["maintenance_date"] > resolved_as_of)
        & (maintenance["maintenance_date"] <= prediction_end)
        & (
            (maintenance["maintenance_type"].astype("string").str.lower() == "emergency")
            | (maintenance.get("severity", pd.Series(index=maintenance.index)).astype("string").str.lower() == "high")
        )
    ]
    future_defects = defects[
        (defects["timestamp"] > resolved_as_of)
        & (defects["timestamp"] <= prediction_end)
        & (pd.to_numeric(defects["defect_count"], errors="coerce") >= 7)
    ]
    target_machine_ids = set(future_maintenance["machine_id"]).union(set(future_defects["machine_id"]))
    features["target_failure_within_window"] = features["machine_id"].isin(target_machine_ids).astype(int)

    features = features.drop(columns=["install_date", "last_maintenance_date"], errors="ignore")
    for column in NUMERIC_FEATURE_COLUMNS:
        if column not in features:
            features[column] = 0
        features[column] = pd.to_numeric(features[column], errors="coerce")
    features["days_since_last_maintenance"] = features["days_since_last_maintenance"].fillna(9999)
    features[NUMERIC_FEATURE_COLUMNS] = features[NUMERIC_FEATURE_COLUMNS].fillna(0)
    for column in CATEGORICAL_FEATURE_COLUMNS:
        if column not in features:
            features[column] = "unknown"
        features[column] = features[column].fillna("unknown").astype(str)

    ordered_columns = ["machine_id", "feature_timestamp", *FEATURE_COLUMNS, "target_failure_within_window"]
    return features[ordered_columns].sort_values("machine_id").reset_index(drop=True)


def write_machine_features(
    connection: sqlite3.Connection,
    features: pd.DataFrame,
    if_exists: str = "replace",
) -> int:
    """Write machine features to SQLite."""

    if if_exists == "replace":
        connection.execute("DELETE FROM machine_features")
        features.to_sql("machine_features", connection, if_exists="append", index=False)
    else:
        features.to_sql("machine_features", connection, if_exists=if_exists, index=False)
    connection.commit()
    return len(features)


def build_features_from_database(
    db_path: Path | str | None = None,
    write: bool = True,
) -> pd.DataFrame:
    """Read cleaned SQLite tables, generate features, and optionally persist them."""

    with get_connection(db_path) as connection:
        datasets = {
            "machines": read_table(connection, "machines"),
            "sensor_readings": read_table(connection, "sensor_readings"),
            "maintenance_records": read_table(connection, "maintenance_records"),
            "defect_records": read_table(connection, "defect_records"),
        }
        features = build_machine_features(datasets)
        if write:
            write_machine_features(connection, features, if_exists="replace")
        return features


def main() -> None:
    configure_logging()
    features = build_features_from_database(write=True)
    print(f"Wrote {len(features)} machine feature rows")


if __name__ == "__main__":
    main()
