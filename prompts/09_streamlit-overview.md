Status: COMPLETED

# 09 Streamlit Overview

## Goal
Create the Streamlit dashboard shell and overview page. The app must read from SQLite, show fleet KPIs, explain that all data and metrics are simulated, and remain responsive when the database or model artifacts are missing.

## Files to create/modify exact paths
- `app/streamlit_app.py`
- `app/pages/__init__.py`
- `app/pages/overview.py`
- `semipulse/plots.py`
- `README.md`
- `START_HERE.md`
- `CURRENT_STATE.md`

## Steps
1. Create `app/streamlit_app.py`:
   - Configure Streamlit page title and layout.
   - Add sidebar navigation for:
     - Overview
     - Data Upload / Load
     - Machine Health
     - Maintenance Risk
     - Defect Trends
     - Downtime Analysis
     - Model Performance
     - Data Explorer
   - For pages not implemented yet, show a compact placeholder that says the page is planned.
   - Keep heavy data processing out of the page file.
2. Create `app/pages/overview.py`:
   - Read tables from SQLite through `semipulse.database`.
   - Show fleet KPIs:
     - total machines
     - active machines
     - high-risk machines
     - average risk score
     - total downtime hours
     - total defect count
     - latest pipeline run
     - latest model run
   - Show a warning that the dataset and metrics are simulated.
   - Handle missing database/tables gracefully with a callout and the commands to initialize the demo.
3. Create `semipulse/plots.py` with lightweight chart helpers that return Matplotlib figures or prepared DataFrames for Streamlit charts.
4. Use Streamlit-native charts or Matplotlib. Do not introduce a complex backend.
5. Add minimal caching with `st.cache_data` only around read-only database queries.
6. Update docs with `streamlit run app/streamlit_app.py`.

## API or Function Contract
- `app.pages.overview.render() -> None`
- `semipulse.plots.prepare_risk_distribution(predictions: pandas.DataFrame) -> pandas.DataFrame`
- `semipulse.plots.prepare_downtime_summary(maintenance: pandas.DataFrame) -> pandas.DataFrame`

## Acceptance criteria
- `streamlit run app/streamlit_app.py` launches the app.
- The Overview page renders with generated sample data and predictions.
- If the database is missing, the app shows a clear setup message instead of crashing.
- Sidebar navigation exists for all planned pages.
- Simulated-data limitation is visible in the UI.
- Tests still pass.

## Tests what to test and how to run
- Run:
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  python -m semipulse.sample_data
  python - <<'PY'
  from semipulse.data_loader import rebuild_database_from_csvs
  rebuild_database_from_csvs(reset=True)
  PY
  python -m semipulse.features
  python -m semipulse.model
  pytest
  streamlit run app/streamlit_app.py
  ```
- Expected results:
  - Tests pass.
  - Streamlit starts locally.
  - Overview displays fleet KPIs and no traceback appears.
  - Stop Streamlit with `Ctrl-C` after the smoke check.

## Stop and verify commands and expected results
Run:
```bash
python -m compileall app semipulse
pytest
streamlit run app/streamlit_app.py
```

Expected results:
- Python files compile.
- Tests pass.
- Streamlit opens the Overview page at the local URL and shows KPIs when demo data exists.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

For this slice, smoke test the complete pipeline and then launch `streamlit run app/streamlit_app.py`.
