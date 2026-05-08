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
