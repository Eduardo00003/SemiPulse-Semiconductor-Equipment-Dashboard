"""SQLite helpers for SemiPulse."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd

from semipulse.config import ensure_runtime_dirs, get_settings
from semipulse.schema import REQUIRED_TABLES, SOURCE_TABLES, load_schema_sql
from semipulse.validation import persist_validation_issues, validate_all_datasets


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Open a SQLite connection with foreign keys enabled."""

    settings = get_settings()
    ensure_runtime_dirs(settings)
    resolved = Path(db_path) if db_path is not None else settings.db_path
    resolved.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(resolved)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(db_path: Path | str | None = None, reset: bool = False) -> Path:
    """Create the SQLite database and all required tables."""

    settings = get_settings()
    ensure_runtime_dirs(settings)
    resolved = Path(db_path) if db_path is not None else settings.db_path
    if reset and resolved.exists():
        resolved.unlink()

    with get_connection(resolved) as connection:
        connection.executescript(load_schema_sql())
        connection.commit()

    return resolved


def table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    """Return whether a table exists in the database."""

    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def write_dataframe(
    connection: sqlite3.Connection,
    table_name: str,
    dataframe: pd.DataFrame,
    if_exists: str = "append",
) -> None:
    """Write a DataFrame to SQLite."""

    dataframe.to_sql(table_name, connection, if_exists=if_exists, index=False)


def read_table(
    connection: sqlite3.Connection,
    table_name: str,
    limit: int | None = None,
) -> pd.DataFrame:
    """Read a full SQLite table or a limited subset."""

    if table_name not in REQUIRED_TABLES:
        raise ValueError(f"Unsupported table: {table_name}")

    query = f'SELECT * FROM "{table_name}"'
    if limit is not None:
        query += " LIMIT ?"
        return pd.read_sql_query(query, connection, params=(limit,))
    return pd.read_sql_query(query, connection)


def list_tables(connection: sqlite3.Connection) -> list[str]:
    """List whitelisted SemiPulse tables that exist in SQLite."""

    rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    existing = {row[0] for row in rows}
    return [table for table in REQUIRED_TABLES if table in existing]


def read_table_view(
    connection: sqlite3.Connection,
    table_name: str,
    limit: int | None = 500,
) -> pd.DataFrame:
    """Read a whitelisted table for dashboard exploration."""

    return read_table(connection, table_name, limit=limit)


def _read_sample_csvs(data_dir: Path) -> dict[str, pd.DataFrame]:
    datasets: dict[str, pd.DataFrame] = {}
    for table in SOURCE_TABLES:
        path = data_dir / f"{table}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing required sample file: {path}")
        datasets[table] = pd.read_csv(path)
    return datasets


def _clear_tables(connection: sqlite3.Connection, table_names: list[str]) -> None:
    for table in table_names:
        connection.execute(f'DELETE FROM "{table}"')


def _insert_pipeline_run(
    connection: sqlite3.Connection,
    pipeline_run_id: str,
    run_type: str,
    status: str,
    started_at: str,
    finished_at: str,
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
            run_type,
            status,
            started_at,
            finished_at,
            json.dumps(details, sort_keys=True),
        ),
    )


def load_sample_csvs_to_sqlite(
    data_dir: Path | str | None = None,
    db_path: Path | str | None = None,
    reset: bool = False,
    validate: bool = True,
) -> dict[str, int]:
    """Load generated sample CSVs into SQLite and record a pipeline run."""

    settings = get_settings()
    resolved_data_dir = Path(data_dir) if data_dir is not None else settings.data_dir
    initialize_database(db_path=db_path, reset=reset)
    started_at = _utc_now()
    pipeline_run_id = f"pipeline-{uuid4().hex}"

    with get_connection(db_path) as connection:
        try:
            datasets = _read_sample_csvs(resolved_data_dir)
            validation_result = validate_all_datasets(datasets) if validate else None
            if validation_result is not None and validation_result.errors:
                persist_validation_issues(connection, validation_result.issues, pipeline_run_id=None)
                raise ValueError(
                    f"Sample CSV validation failed with {len(validation_result.errors)} error(s)"
                )
            _clear_tables(
                connection,
                [
                    "risk_predictions",
                    "machine_features",
                    "defect_records",
                    "maintenance_records",
                    "sensor_readings",
                    "machines",
                ],
            )

            row_counts: dict[str, int] = {}
            for table in SOURCE_TABLES:
                write_dataframe(connection, table, datasets[table], if_exists="append")
                row_counts[table] = len(datasets[table])

            _insert_pipeline_run(
                connection=connection,
                pipeline_run_id=pipeline_run_id,
                run_type="sample_csv_load",
                status="success",
                started_at=started_at,
                finished_at=_utc_now(),
                details={"data_dir": str(resolved_data_dir), "row_counts": row_counts},
            )
            connection.commit()
            return row_counts
        except Exception as exc:
            _insert_pipeline_run(
                connection=connection,
                pipeline_run_id=pipeline_run_id,
                run_type="sample_csv_load",
                status="failed",
                started_at=started_at,
                finished_at=_utc_now(),
                details={"data_dir": str(resolved_data_dir), "error": str(exc)},
            )
            connection.commit()
            raise
