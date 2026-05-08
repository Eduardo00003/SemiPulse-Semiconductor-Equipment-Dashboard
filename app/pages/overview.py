"""Overview dashboard page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from semipulse.database import get_connection, read_table
from semipulse.plots import prepare_downtime_summary, prepare_risk_distribution


def _safe_read_table(table_name: str) -> pd.DataFrame:
    try:
        with get_connection() as connection:
            return read_table(connection, table_name)
    except Exception:
        return pd.DataFrame()


def _latest_value(dataframe: pd.DataFrame, sort_column: str, value_column: str) -> str:
    if dataframe.empty or sort_column not in dataframe or value_column not in dataframe:
        return "Not available"
    latest = dataframe.sort_values(sort_column).tail(1)
    return str(latest.iloc[0][value_column])


def _render_setup_message() -> None:
    st.info(
        "No SQLite demo data is available yet. Run the sample data, database, feature, and model commands to populate the dashboard."
    )
    st.code(
        "\n".join(
            [
                "python -m semipulse.sample_data",
                "python - <<'PY'",
                "from semipulse.data_loader import rebuild_database_from_csvs",
                "rebuild_database_from_csvs(reset=True)",
                "PY",
                "python -m semipulse.features",
                "python -m semipulse.model",
            ]
        ),
        language="bash",
    )


def render() -> None:
    """Render the Overview page."""

    st.title("SemiPulse")
    st.caption("Predictive maintenance dashboard for simulated semiconductor equipment")
    st.warning(
        "All data and model metrics shown here are simulated-data results only. They do not represent real semiconductor factory performance.",
    )

    machines = _safe_read_table("machines")
    maintenance = _safe_read_table("maintenance_records")
    defects = _safe_read_table("defect_records")
    predictions = _safe_read_table("risk_predictions")
    model_runs = _safe_read_table("model_runs")
    pipeline_runs = _safe_read_table("pipeline_runs")

    if machines.empty:
        _render_setup_message()
        return

    total_machines = len(machines)
    active_machines = int((machines.get("status", pd.Series(dtype=str)).astype(str).str.lower() == "active").sum())
    high_risk_machines = int((predictions.get("risk_level", pd.Series(dtype=str)).astype(str).str.lower() == "high").sum())
    average_risk = float(predictions["risk_score"].mean()) if not predictions.empty and "risk_score" in predictions else 0.0
    total_downtime = float(maintenance["downtime_hours"].sum()) if not maintenance.empty and "downtime_hours" in maintenance else 0.0
    total_defects = int(defects["defect_count"].sum()) if not defects.empty and "defect_count" in defects else 0

    cols = st.columns(4)
    cols[0].metric("Total machines", f"{total_machines:,}")
    cols[1].metric("Active machines", f"{active_machines:,}")
    cols[2].metric("High risk", f"{high_risk_machines:,}")
    cols[3].metric("Average risk", f"{average_risk:.2f}")

    cols = st.columns(4)
    cols[0].metric("Downtime hours", f"{total_downtime:,.1f}")
    cols[1].metric("Defect count", f"{total_defects:,}")
    cols[2].metric("Latest pipeline", _latest_value(pipeline_runs, "run_started_at", "status"))
    cols[3].metric("Latest model", _latest_value(model_runs, "training_timestamp", "model_type"))

    chart_cols = st.columns(2)
    risk_distribution = prepare_risk_distribution(predictions)
    if not risk_distribution.empty:
        chart_cols[0].subheader("Risk Distribution")
        chart_cols[0].bar_chart(risk_distribution, x="risk_level", y="machine_count")

    downtime_summary = prepare_downtime_summary(maintenance)
    if not downtime_summary.empty:
        chart_cols[1].subheader("Downtime by Maintenance Type")
        chart_cols[1].bar_chart(downtime_summary, x="maintenance_type", y="downtime_hours")

    st.subheader("Recent Risk Predictions")
    if predictions.empty:
        st.info("Risk predictions are not available yet. Run `python -m semipulse.model`.")
    else:
        st.dataframe(
            predictions.sort_values("risk_score", ascending=False).head(10),
            use_container_width=True,
            hide_index=True,
        )
