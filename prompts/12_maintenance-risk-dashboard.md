Status: COMPLETED

# 12 Maintenance Risk Dashboard

## Goal
Add a ranked maintenance risk dashboard that helps users prioritize simulated machine service. Include risk filters, sorting, high/medium/low labels, and machine-level explanation fields from features and predictions.

## Files to create/modify exact paths
- `app/pages/maintenance_risk.py`
- `app/streamlit_app.py`
- `semipulse/plots.py`
- `semipulse/predict.py`
- `README.md`
- `START_HERE.md`
- `CURRENT_STATE.md`

## Steps
1. Create `app/pages/maintenance_risk.py` with `render()`.
2. Read from SQLite:
   - `risk_predictions`
   - `machine_features`
   - `machines`
   - `model_runs`
3. Build a ranked risk DataFrame with:
   - Rank.
   - Machine ID.
   - Machine type.
   - Facility area.
   - Manufacturer.
   - Risk score.
   - Risk level.
   - Predicted failure flag.
   - Recent downtime hours.
   - Recent defect count.
   - Days since last maintenance.
   - Key sensor indicators such as average vibration and max temperature.
   - Model run ID and prediction timestamp.
4. Add filters:
   - Risk level.
   - Machine type.
   - Facility area.
   - Manufacturer.
   - Predicted failure flag.
5. Add sorting:
   - Risk score descending by default.
   - Recent downtime.
   - Recent defect count.
   - Days since last maintenance.
6. Add machine detail context:
   - Select a machine from ranked table.
   - Show feature values and recent risk metadata.
   - Use plain-language labels without implying real factory accuracy.
7. Add risk distribution visual.
8. Add a button to rerun risk scoring if features and model are already present.
9. Update docs.

## API or Function Contract
- `app.pages.maintenance_risk.render() -> None`
- `semipulse.predict.build_ranked_risk_table(connection: sqlite3.Connection) -> pandas.DataFrame`
- `semipulse.plots.prepare_risk_level_counts(predictions: pandas.DataFrame) -> pandas.DataFrame`

## Acceptance criteria
- Maintenance Risk page renders from sidebar.
- Ranked table shows one row per latest prediction.
- Filters and sorting work.
- High/medium/low risk labels are visible.
- Machine detail panel gives context from feature columns.
- Page handles missing predictions with setup instructions.
- Tests pass.

## Tests what to test and how to run
- Run:
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  python - <<'PY'
  from semipulse.pipeline import run_demo_pipeline
  print(run_demo_pipeline(generate_data=True, reset_database=True, train_model=True))
  from semipulse.database import get_connection
  from semipulse.predict import build_ranked_risk_table
  conn = get_connection()
  print(build_ranked_risk_table(conn).head())
  conn.close()
  PY
  pytest
  streamlit run app/streamlit_app.py
  ```
- Expected results:
  - Ranked risk table prints with risk scores.
  - Tests pass.
  - Maintenance Risk page loads and filters work manually.

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
- The Maintenance Risk page displays ranked simulated maintenance risk.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

For this slice, smoke test the full pipeline and manually open the Maintenance Risk page.
