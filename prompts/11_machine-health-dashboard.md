Status: COMPLETED

# 11 Machine Health Dashboard

## Goal
Add the Machine Health dashboard page with sensor trends, machine filters, detail panels, and fleet averages. The page must read from SQLite and avoid doing expensive ETL directly in Streamlit.

## Files to create/modify exact paths
- `app/pages/machine_health.py`
- `app/streamlit_app.py`
- `semipulse/plots.py`
- `semipulse/database.py`
- `README.md`
- `START_HERE.md`
- `CURRENT_STATE.md`

## Steps
1. Create `app/pages/machine_health.py` with `render()`.
2. Load required tables:
   - `machines`
   - `sensor_readings`
   - `machine_features`
   - `risk_predictions`
3. Add filters:
   - Machine ID.
   - Machine type.
   - Facility area.
   - Manufacturer.
   - Date range for sensor readings.
4. Show machine detail context:
   - Machine metadata.
   - Current risk score and risk level if predictions exist.
   - Days since last maintenance if features exist.
   - Recent defect count and recent downtime if features exist.
5. Show sensor trends:
   - Temperature over time.
   - Vibration over time.
   - Pressure over time.
   - Power draw over time.
   - Fleet average comparison where practical.
6. Add simple anomaly indicators:
   - Highlight readings above selected percentile thresholds.
   - Clearly label these as heuristic indicators on simulated data.
7. Add `semipulse.plots` helpers for preparing time-series chart data.
8. Update routing in `app/streamlit_app.py`.
9. Handle missing data gracefully with setup instructions.
10. Update docs.

## API or Function Contract
- `app.pages.machine_health.render() -> None`
- `semipulse.plots.prepare_sensor_timeseries(sensor_readings: pandas.DataFrame, machine_id: str | None = None) -> pandas.DataFrame`
- `semipulse.plots.prepare_fleet_sensor_averages(sensor_readings: pandas.DataFrame) -> pandas.DataFrame`

## Acceptance criteria
- Machine Health page renders from the sidebar.
- User can filter by machine and see sensor trends.
- Detail panel shows machine metadata plus risk/feature context when available.
- Missing database or missing predictions do not crash the page.
- Simulated-data caveat remains visible.
- Tests still pass.

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
  - Machine Health page loads and charts update when filters change.

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
- Machine Health page works manually with sample data.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

For this slice, smoke test the full pipeline and manually open the Machine Health page.
