"""Data Explorer dashboard page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from semipulse.database import get_connection, list_tables, read_table_view
from semipulse.exports import (
    export_machine_features,
    export_model_metrics,
    export_risk_rankings,
    export_table_csv,
)


def _filter_table(dataframe: pd.DataFrame, search_text: str) -> pd.DataFrame:
    if dataframe.empty or not search_text:
        return dataframe
    text_columns = dataframe.select_dtypes(include=["object", "string"]).columns
    if len(text_columns) == 0:
        return dataframe
    mask = dataframe[text_columns].astype(str).apply(
        lambda column: column.str.contains(search_text, case=False, na=False)
    ).any(axis=1)
    return dataframe[mask]


def render() -> None:
    st.title("Data Explorer")
    st.caption("Explore processed SQLite tables and export dashboard data")

    try:
        connection = get_connection()
        tables = list_tables(connection)
    except Exception as exc:
        st.error(f"Could not open SQLite database: {exc}")
        return

    if not tables:
        st.info("No SemiPulse tables are available yet. Run the demo pipeline first.")
        connection.close()
        return

    table_name = st.selectbox("Table", tables)
    row_limit = st.number_input("Row limit", min_value=10, max_value=10000, value=500, step=50)
    search_text = st.text_input("Search text columns")
    table = read_table_view(connection, table_name, limit=int(row_limit))
    filtered = _filter_table(table, search_text)

    st.metric("Rows shown", f"{len(filtered):,}")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.download_button(
        "Download selected table CSV",
        data=filtered.to_csv(index=False),
        file_name=f"{table_name}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.subheader("Dedicated Exports")
    export_cols = st.columns(3)
    export_cols[0].download_button(
        "Risk rankings CSV",
        data=export_risk_rankings(connection),
        file_name="semipulse_risk_rankings.csv",
        mime="text/csv",
        use_container_width=True,
    )
    export_cols[1].download_button(
        "Machine features CSV",
        data=export_machine_features(connection),
        file_name="semipulse_machine_features.csv",
        mime="text/csv",
        use_container_width=True,
    )
    export_cols[2].download_button(
        "Model metrics JSON",
        data=export_model_metrics(connection),
        file_name="semipulse_model_metrics.json",
        mime="application/json",
        use_container_width=True,
    )

    with st.expander("Raw selected table export"):
        st.code(export_table_csv(connection, table_name, limit=int(row_limit))[:2000], language="csv")

    connection.close()
