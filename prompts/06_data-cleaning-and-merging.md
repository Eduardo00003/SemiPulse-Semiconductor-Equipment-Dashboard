Status: COMPLETED

# 06 Data Cleaning and Merging

## Goal
Add deterministic cleaning and merging utilities that standardize uploaded or generated datasets, preserve data-quality feedback, and store cleaned source tables in SQLite. Keep heavy data processing in `semipulse/`, not in Streamlit.

## Files to create/modify exact paths
- `semipulse/data_loader.py`
- `semipulse/database.py`
- `semipulse/validation.py`
- `tests/test_data_loader.py`
- `README.md`
- `START_HERE.md`
- `CURRENT_STATE.md`

## Steps
1. Implement `semipulse/data_loader.py` with functions to:
   - Read the four dataset CSVs from a directory.
   - Clean column names.
   - Standardize `machine_id` values.
   - Parse date and timestamp columns.
   - Convert numeric fields safely.
   - Normalize categorical fields such as machine type, manufacturer, facility area, status, maintenance type, defect type, and severity.
   - Handle missing optional columns gracefully.
2. Cleaning should not silently discard bad rows:
   - Keep usable rows.
   - Record issues through the validation/data quality issue structure.
   - Make row drops explicit and counted.
3. Add a merged analytical dataset helper:
   - One machine-level row per machine.
   - Include latest metadata, sensor aggregates, maintenance summary, and defect summary.
   - This merged table is an intermediate helper; the model-ready feature table is created in prompt 07.
4. Add `rebuild_database_from_csvs(data_dir=None, db_path=None, reset=True)`:
   - Read CSVs.
   - Clean them.
   - Validate cleaned data.
   - Initialize SQLite.
   - Store cleaned source tables.
   - Store data quality issues.
   - Record `pipeline_runs`.
5. Keep compatibility with the existing sample generator and database helpers.
6. Add tests for:
   - Machine ID normalization.
   - Timestamp parsing.
   - Numeric conversion.
   - Merged machine-level output.
   - Database rebuild from generated sample CSVs.
7. Update docs with the rebuild command and current state.

## API or Function Contract
- `load_csv_datasets(data_dir: Path | str | None = None) -> dict[str, pandas.DataFrame]`
- `clean_machines(df: pandas.DataFrame) -> pandas.DataFrame`
- `clean_sensor_readings(df: pandas.DataFrame) -> pandas.DataFrame`
- `clean_maintenance_records(df: pandas.DataFrame) -> pandas.DataFrame`
- `clean_defect_records(df: pandas.DataFrame) -> pandas.DataFrame`
- `clean_all_datasets(datasets: dict[str, pandas.DataFrame]) -> dict[str, pandas.DataFrame]`
- `build_machine_analytics_table(datasets: dict[str, pandas.DataFrame]) -> pandas.DataFrame`
- `rebuild_database_from_csvs(data_dir: Path | str | None = None, db_path: Path | str | None = None, reset: bool = True) -> dict[str, int]`

## Acceptance criteria
- Generated sample CSVs can be read, cleaned, validated, and stored in SQLite.
- Cleaned source tables retain required columns and valid machine references.
- The machine-level analytical table has one row per machine.
- Data quality issues are persisted when validation/cleaning detects problems.
- Tests pass.

## Tests what to test and how to run
- Run:
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  python -m semipulse.sample_data
  python - <<'PY'
  from semipulse.data_loader import rebuild_database_from_csvs, load_csv_datasets, clean_all_datasets, build_machine_analytics_table
  raw = load_csv_datasets()
  clean = clean_all_datasets(raw)
  analytics = build_machine_analytics_table(clean)
  print(analytics.head())
  print(rebuild_database_from_csvs(reset=True))
  PY
  pytest tests/test_data_loader.py
  ```
- Expected results:
  - The analytics table prints with one row per machine.
  - Database rebuild prints source-table row counts.
  - Tests pass.

## Stop and verify commands and expected results
Run:
```bash
python -m semipulse.sample_data
python - <<'PY'
from semipulse.data_loader import rebuild_database_from_csvs
from semipulse.database import get_connection, read_table
print(rebuild_database_from_csvs(reset=True))
conn = get_connection()
for table in ["machines", "sensor_readings", "maintenance_records", "defect_records", "pipeline_runs", "data_quality_issues"]:
    print(table, len(read_table(conn, table)))
conn.close()
PY
pytest
```

Expected results:
- Cleaned source tables have rows.
- `pipeline_runs` records the rebuild.
- `pytest` passes.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

For this slice, smoke test `python -m semipulse.sample_data` followed by `rebuild_database_from_csvs(reset=True)`.
