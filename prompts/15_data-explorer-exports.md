Status: NOT_STARTED

# 15 Data Explorer Exports

## Goal
Add a Data Explorer page and CSV/JSON export helpers for risk rankings, feature tables, model metrics, and selected SQLite table views.

## Files to create/modify exact paths
- `app/pages/data_explorer.py`
- `app/streamlit_app.py`
- `semipulse/exports.py`
- `semipulse/database.py`
- `tests/test_exports.py`
- `README.md`
- `START_HERE.md`
- `CURRENT_STATE.md`

## Steps
1. Implement `semipulse/exports.py`:
   - Export ranked risk predictions as CSV.
   - Export machine features as CSV.
   - Export model metrics as JSON or CSV.
   - Export any selected database table view as CSV.
2. Export files should include clear headers and either timestamps or model run IDs.
3. Create `app/pages/data_explorer.py` with `render()`:
   - Select a database table.
   - Preview rows with a row limit.
   - Search/filter simple text columns where practical.
   - Download the selected table view as CSV.
   - Provide dedicated downloads for:
     - Ranked risk predictions.
     - Machine features.
     - Model metrics.
4. Add safe table listing in `semipulse.database.py`:
   - Do not allow arbitrary SQL from UI input.
   - Only read whitelisted SQLite tables.
5. Update `app/streamlit_app.py` routing.
6. Add tests for export helper functions:
   - CSV output is non-empty.
   - Expected columns are present.
   - Export functions work with generated sample pipeline output.
7. Update docs.

## API or Function Contract
- `list_tables(connection: sqlite3.Connection) -> list[str]`
- `read_table_view(connection: sqlite3.Connection, table_name: str, limit: int | None = 500) -> pandas.DataFrame`
- `export_risk_rankings(connection: sqlite3.Connection) -> str`
- `export_machine_features(connection: sqlite3.Connection) -> str`
- `export_model_metrics(connection: sqlite3.Connection, model_dir: Path | str | None = None) -> str`
- `export_table_csv(connection: sqlite3.Connection, table_name: str, limit: int | None = None) -> str`
- `app.pages.data_explorer.render() -> None`

## Acceptance criteria
- Data Explorer page renders from sidebar.
- User can preview whitelisted SQLite tables.
- User can download selected table views.
- Dedicated exports exist for risk ranking, features, and model metrics.
- Exported risk ranking includes clear columns such as `machine_id`, `risk_score`, `risk_level`, `model_run_id`, and `prediction_timestamp`.
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
  from semipulse.exports import export_risk_rankings, export_machine_features, export_model_metrics
  conn = get_connection()
  print(export_risk_rankings(conn)[:200])
  print(export_machine_features(conn)[:200])
  print(export_model_metrics(conn)[:200])
  conn.close()
  PY
  pytest tests/test_exports.py
  streamlit run app/streamlit_app.py
  ```
- Expected results:
  - Export strings print CSV/JSON-like content.
  - Export tests pass.
  - Data Explorer page previews and downloads table views.

## Stop and verify commands and expected results
Run:
```bash
pytest
streamlit run app/streamlit_app.py
```

Expected results:
- Tests pass.
- Data Explorer and downloads work manually.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

For this slice, smoke test the full pipeline, the Data Explorer page, and at least one CSV download.
