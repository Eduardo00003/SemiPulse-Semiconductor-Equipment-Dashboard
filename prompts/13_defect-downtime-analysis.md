Status: COMPLETED

# 13 Defect Downtime Analysis

## Goal
Add Defect Trends and Downtime Analysis dashboard pages. These pages must help connect simulated defects, maintenance downtime, and machine risk without overstating real-world accuracy.

## Files to create/modify exact paths
- `app/pages/defect_trends.py`
- `app/pages/downtime_analysis.py`
- `app/streamlit_app.py`
- `semipulse/plots.py`
- `README.md`
- `START_HERE.md`
- `CURRENT_STATE.md`

## Steps
1. Create `app/pages/defect_trends.py` with `render()`.
2. Defect Trends page should read:
   - `defect_records`
   - `machines`
   - `machine_features`
   - `risk_predictions`
3. Add Defect Trends views:
   - Defect counts over time.
   - Defects by machine.
   - Defects by defect type if present.
   - Defects by facility area and process step if present.
   - Defects by batch or lot if present.
   - Defect count versus risk score table or chart.
4. Create `app/pages/downtime_analysis.py` with `render()`.
5. Downtime page should read:
   - `maintenance_records`
   - `machines`
   - `machine_features`
   - `risk_predictions`
6. Add Downtime Analysis views:
   - Downtime by machine.
   - Downtime by machine type.
   - Downtime by maintenance type.
   - Top downtime machines.
   - Downtime versus risk score.
7. Add filters shared across pages where useful:
   - Date range.
   - Facility area.
   - Machine type.
   - Machine ID.
8. Add chart prep helpers in `semipulse/plots.py`.
9. Update `app/streamlit_app.py` routing.
10. Handle missing optional columns gracefully.
11. Update docs.

## API or Function Contract
- `app.pages.defect_trends.render() -> None`
- `app.pages.downtime_analysis.render() -> None`
- `semipulse.plots.prepare_defect_trends(defects: pandas.DataFrame, machines: pandas.DataFrame | None = None) -> pandas.DataFrame`
- `semipulse.plots.prepare_downtime_by_machine(maintenance: pandas.DataFrame, machines: pandas.DataFrame | None = None) -> pandas.DataFrame`
- `semipulse.plots.prepare_risk_relationship(features_or_predictions: pandas.DataFrame) -> pandas.DataFrame`

## Acceptance criteria
- Defect Trends and Downtime Analysis pages render from sidebar.
- Charts/tables update with filters.
- Pages show useful results with generated sample data.
- Optional fields are used when present and ignored when missing.
- Simulated-data caveat remains visible.
- Tests pass.

## Tests what to test and how to run
- Run:
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  python - <<'PY'
  from semipulse.pipeline import run_demo_pipeline
  print(run_demo_pipeline(generate_data=True, reset_database=True, train_model=True))
  PY
  pytest
  streamlit run app/streamlit_app.py
  ```
- Expected results:
  - Pipeline completes.
  - Tests pass.
  - Defect Trends and Downtime Analysis pages render without tracebacks.

## Stop and verify commands and expected results
Run:
```bash
python -m compileall app semipulse
pytest
streamlit run app/streamlit_app.py
```

Expected results:
- Compile succeeds.
- Tests pass.
- Defect and downtime pages work manually with sample data.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

For this slice, smoke test the full pipeline and manually open both Defect Trends and Downtime Analysis pages.
