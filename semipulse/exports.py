"""CSV and JSON export helpers."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from semipulse.database import read_table_view
from semipulse.metrics import load_latest_model_metadata
from semipulse.predict import build_ranked_risk_table


def export_risk_rankings(connection: sqlite3.Connection) -> str:
    """Export ranked risk predictions as CSV."""

    ranked = build_ranked_risk_table(connection)
    return ranked.to_csv(index=False)


def export_machine_features(connection: sqlite3.Connection) -> str:
    """Export the machine feature table as CSV."""

    features = read_table_view(connection, "machine_features", limit=None)
    return features.to_csv(index=False)


def export_model_metrics(
    connection: sqlite3.Connection,
    model_dir: Path | str | None = None,
) -> str:
    """Export latest model metrics and metadata as JSON."""

    metadata = load_latest_model_metadata(model_dir)
    if metadata:
        return json.dumps(metadata, indent=2, sort_keys=True)
    model_runs = read_table_view(connection, "model_runs", limit=1)
    return model_runs.to_json(orient="records", indent=2)


def export_table_csv(
    connection: sqlite3.Connection,
    table_name: str,
    limit: int | None = None,
) -> str:
    """Export a whitelisted SQLite table as CSV."""

    table = read_table_view(connection, table_name, limit=limit)
    return table.to_csv(index=False)
