"""CSV loading, cleaning, merging, and SQLite rebuild helpers."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd

from semipulse.config import get_settings
from semipulse.database import get_connection, initialize_database, write_dataframe
from semipulse.schema import SOURCE_TABLES
from semipulse.validation import persist_validation_issues, validate_all_datasets


CSV_FILENAMES = {
    "machines": "machines.csv",
    "sensor_readings": "sensor_readings.csv",
    "maintenance_records": "maintenance_records.csv",
    "defect_records": "defect_records.csv",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    cleaned = dataframe.copy()
    cleaned.columns = [
        str(column).strip().lower().replace(" ", "_").replace("-", "_")
        for column in cleaned.columns
    ]
    return cleaned


def _clean_machine_id(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.upper()


def _clean_category(series: pd.Series, *, lower: bool = True) -> pd.Series:
    cleaned = series.astype("string").str.strip()
    return cleaned.str.lower() if lower else cleaned


def _parse_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", format="mixed").dt.strftime("%Y-%m-%dT%H:%M:%S")


def _parse_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", format="mixed").dt.strftime("%Y-%m-%d")


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _optional_column(dataframe: pd.DataFrame, column: str, default: object = pd.NA) -> pd.Series:
    if column in dataframe.columns:
        return dataframe[column]
    return pd.Series([default] * len(dataframe), index=dataframe.index)


def load_csv_datasets(data_dir: Path | str | None = None) -> dict[str, pd.DataFrame]:
    """Load the four SemiPulse CSV datasets from a directory."""

    resolved = Path(data_dir) if data_dir is not None else get_settings().data_dir
    datasets: dict[str, pd.DataFrame] = {}
    for name, filename in CSV_FILENAMES.items():
        path = resolved / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing required dataset: {path}")
        datasets[name] = pd.read_csv(path)
    return datasets


def clean_machines(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = _clean_columns(df)
    if "machine_id" in cleaned:
        cleaned["machine_id"] = _clean_machine_id(cleaned["machine_id"])
    for column in ["machine_type", "manufacturer", "facility_area", "model", "line_id", "process_step"]:
        if column in cleaned:
            cleaned[column] = _clean_category(cleaned[column], lower=False)
    for column in ["status", "criticality"]:
        if column in cleaned:
            cleaned[column] = _clean_category(cleaned[column], lower=True)
    for column in ["install_date", "last_service_date"]:
        if column in cleaned:
            cleaned[column] = _parse_date(cleaned[column])
    if "expected_lifetime_years" in cleaned:
        cleaned["expected_lifetime_years"] = _numeric(cleaned["expected_lifetime_years"]).astype("Int64")
    return cleaned


def clean_sensor_readings(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = _clean_columns(df)
    if "machine_id" in cleaned:
        cleaned["machine_id"] = _clean_machine_id(cleaned["machine_id"])
    if "reading_id" in cleaned:
        cleaned["reading_id"] = _clean_category(cleaned["reading_id"], lower=False)
    if "timestamp" in cleaned:
        cleaned["timestamp"] = _parse_datetime(cleaned["timestamp"])
    for column in [
        "temperature",
        "vibration",
        "pressure",
        "power_draw",
        "humidity",
        "runtime_hours",
        "chamber_pressure",
        "gas_flow_rate",
    ]:
        if column in cleaned:
            cleaned[column] = _numeric(cleaned[column])
    if "cycle_count" in cleaned:
        cleaned["cycle_count"] = _numeric(cleaned["cycle_count"]).astype("Int64")
    if "error_code" in cleaned:
        cleaned["error_code"] = cleaned["error_code"].fillna("").astype("string").str.strip()
    return cleaned


def clean_maintenance_records(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = _clean_columns(df)
    if "machine_id" in cleaned:
        cleaned["machine_id"] = _clean_machine_id(cleaned["machine_id"])
    if "maintenance_id" in cleaned:
        cleaned["maintenance_id"] = _clean_category(cleaned["maintenance_id"], lower=False)
    if "maintenance_date" in cleaned:
        cleaned["maintenance_date"] = _parse_date(cleaned["maintenance_date"])
    for column in ["maintenance_type", "severity", "parts_replaced", "technician"]:
        if column in cleaned:
            cleaned[column] = _clean_category(cleaned[column], lower=column in {"maintenance_type", "severity"})
    for column in ["downtime_hours", "maintenance_cost"]:
        if column in cleaned:
            cleaned[column] = _numeric(cleaned[column])
    if "resolved" in cleaned:
        cleaned["resolved"] = cleaned["resolved"].astype("string").str.lower().isin(["true", "1", "yes", "resolved"]).astype(int)
    return cleaned


def clean_defect_records(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = _clean_columns(df)
    if "machine_id" in cleaned:
        cleaned["machine_id"] = _clean_machine_id(cleaned["machine_id"])
    if "defect_id" in cleaned:
        cleaned["defect_id"] = _clean_category(cleaned["defect_id"], lower=False)
    if "timestamp" in cleaned:
        cleaned["timestamp"] = _parse_datetime(cleaned["timestamp"])
    for column in ["defect_type", "severity", "process_step", "wafer_lot", "batch_id"]:
        if column in cleaned:
            cleaned[column] = _clean_category(cleaned[column], lower=column in {"defect_type", "severity", "process_step"})
    for column in ["defect_count", "yield_loss_pct"]:
        if column in cleaned:
            cleaned[column] = _numeric(cleaned[column])
    if "defect_count" in cleaned:
        cleaned["defect_count"] = cleaned["defect_count"].astype("Int64")
    return cleaned


def clean_all_datasets(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Clean all core SemiPulse datasets."""

    return {
        "machines": clean_machines(datasets["machines"]),
        "sensor_readings": clean_sensor_readings(datasets["sensor_readings"]),
        "maintenance_records": clean_maintenance_records(datasets["maintenance_records"]),
        "defect_records": clean_defect_records(datasets["defect_records"]),
    }


def build_machine_analytics_table(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build a compact one-row-per-machine analytical table."""

    machines = datasets["machines"].copy()
    sensors = datasets["sensor_readings"].copy()
    maintenance = datasets["maintenance_records"].copy()
    defects = datasets["defect_records"].copy()

    sensor_summary = sensors.groupby("machine_id", as_index=False).agg(
        avg_temperature=("temperature", "mean"),
        avg_vibration=("vibration", "mean"),
        avg_pressure=("pressure", "mean"),
        avg_power_draw=("power_draw", "mean"),
        latest_sensor_timestamp=("timestamp", "max"),
    )
    maintenance_summary = maintenance.groupby("machine_id", as_index=False).agg(
        total_maintenance_events=("maintenance_id", "count"),
        total_downtime_hours=("downtime_hours", "sum"),
        latest_maintenance_date=("maintenance_date", "max"),
    )
    defect_summary = defects.groupby("machine_id", as_index=False).agg(
        total_defect_count=("defect_count", "sum"),
        defect_batches=("batch_id", "nunique"),
        latest_defect_timestamp=("timestamp", "max"),
    )

    analytics = machines.merge(sensor_summary, on="machine_id", how="left")
    analytics = analytics.merge(maintenance_summary, on="machine_id", how="left")
    analytics = analytics.merge(defect_summary, on="machine_id", how="left")

    for column in [
        "avg_temperature",
        "avg_vibration",
        "avg_pressure",
        "avg_power_draw",
        "total_downtime_hours",
        "total_defect_count",
    ]:
        if column in analytics:
            analytics[column] = analytics[column].fillna(0)
    for column in ["total_maintenance_events", "defect_batches"]:
        if column in analytics:
            analytics[column] = analytics[column].fillna(0).astype(int)

    return analytics


def _clear_source_tables(connection: sqlite3.Connection) -> None:
    for table in [
        "risk_predictions",
        "machine_features",
        "defect_records",
        "maintenance_records",
        "sensor_readings",
        "machines",
        "data_quality_issues",
    ]:
        connection.execute(f'DELETE FROM "{table}"')


def _record_pipeline_run(
    connection: sqlite3.Connection,
    pipeline_run_id: str,
    status: str,
    started_at: str,
    details: dict[str, object],
) -> None:
    connection.execute(
        """
        INSERT INTO pipeline_runs (
            pipeline_run_id, run_type, status, run_started_at, run_finished_at, details_json
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            pipeline_run_id,
            "csv_rebuild",
            status,
            started_at,
            _utc_now(),
            json.dumps(details, sort_keys=True),
        ),
    )


def rebuild_database_from_csvs(
    data_dir: Path | str | None = None,
    db_path: Path | str | None = None,
    reset: bool = True,
) -> dict[str, int]:
    """Clean, validate, and write source CSV datasets into SQLite."""

    started_at = _utc_now()
    pipeline_run_id = f"pipeline-{uuid4().hex}"
    raw_datasets = load_csv_datasets(data_dir)
    cleaned = clean_all_datasets(raw_datasets)
    validation_result = validate_all_datasets(cleaned)

    initialize_database(db_path=db_path, reset=reset)
    with get_connection(db_path) as connection:
        if validation_result.errors:
            _record_pipeline_run(
                connection,
                pipeline_run_id,
                "failed",
                started_at,
                {"error_count": len(validation_result.errors), "warning_count": len(validation_result.warnings)},
            )
            persist_validation_issues(connection, validation_result.issues, pipeline_run_id)
            connection.commit()
            raise ValueError(f"Cleaned CSV validation failed with {len(validation_result.errors)} error(s)")

        _clear_source_tables(connection)
        row_counts: dict[str, int] = {}
        for table in SOURCE_TABLES:
            write_dataframe(connection, table, cleaned[table], if_exists="append")
            row_counts[table] = len(cleaned[table])

        if validation_result.warnings:
            persist_validation_issues(connection, validation_result.issues, pipeline_run_id)
        _record_pipeline_run(
            connection,
            pipeline_run_id,
            "success",
            started_at,
            {"row_counts": row_counts, "data_dir": str(Path(data_dir) if data_dir else get_settings().data_dir)},
        )
        connection.commit()
        return row_counts
