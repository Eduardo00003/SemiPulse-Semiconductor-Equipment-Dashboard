"""SemiPulse Streamlit application entrypoint."""

from __future__ import annotations

import streamlit as st

from app.pages import overview


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
    else:
        _render_placeholder(selected_page)


if __name__ == "__main__":
    main()
