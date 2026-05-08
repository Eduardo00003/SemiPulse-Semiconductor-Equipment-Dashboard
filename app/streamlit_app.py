"""SemiPulse Streamlit application entrypoint."""

from __future__ import annotations

import streamlit as st

from app.pages import (
    data_upload,
    data_explorer,
    defect_trends,
    downtime_analysis,
    machine_health,
    maintenance_risk,
    model_performance,
    overview,
)


PAGE_NAMES = [
    "Overview",
    "Data Upload / Load",
    "Machine Health",
    "Maintenance Risk",
    "Defect Trends",
    "Downtime Analysis",
    "Model Performance",
    "Data Explorer",
]


def _render_placeholder(page_name: str) -> None:
    st.title(page_name)
    st.info("This page is planned in the next implementation prompts.")


def main() -> None:
    st.set_page_config(
        page_title="SemiPulse",
        page_icon="SP",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.sidebar.title("SemiPulse")
    selected_page = st.sidebar.radio("Navigate", PAGE_NAMES, label_visibility="collapsed")

    if selected_page == "Overview":
        overview.render()
    elif selected_page == "Data Upload / Load":
        data_upload.render()
    elif selected_page == "Machine Health":
        machine_health.render()
    elif selected_page == "Maintenance Risk":
        maintenance_risk.render()
    elif selected_page == "Defect Trends":
        defect_trends.render()
    elif selected_page == "Downtime Analysis":
        downtime_analysis.render()
    elif selected_page == "Model Performance":
        model_performance.render()
    elif selected_page == "Data Explorer":
        data_explorer.render()
    else:
        _render_placeholder(selected_page)


if __name__ == "__main__":
    main()
