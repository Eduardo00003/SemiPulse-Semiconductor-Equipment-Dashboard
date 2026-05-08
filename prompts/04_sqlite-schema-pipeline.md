Status: COMPLETED

# 04 SQLite Schema Pipeline

## Goal
Add SQLite persistence for the MVP. Create schema definitions, database helpers, and a pipeline entrypoint that creates or resets the database and loads the generated sample CSVs into the required tables.

## Files to create/modify exact paths
- `db/schema.sql`
- `semipulse/schema.py`
- `semipulse/database.py`
- `tests/test_database.py`
- `README.md`
- `START_HERE.md`
- `CURRENT_STATE.md`

## Steps
1. Create `db/schema.sql` with these minimum tables:
   - `machines`
   - `sensor_readings`
   - `maintenance_records`
   - `defect_records`
   - `machine_features`
   - `risk_predictions`
   - `model_runs`
   - `pipeline_runs`
   - `data_quality_issues`
2. Use clear primary keys and foreign keys where practical:
   - `machine_id` links sensor, maintenance, defect, features, and predictions.
   - `model_run_id` links predictions and model runs.
   - Add timestamps such as `created_at`, `run_started_at`, and `run_finished_at`.
3. Implement `semipulse/schema.py`:
   - Load `db/schema.sql`.
   - Expose table names and schema path helpers.
4. Implement `semipulse/database.py`:
   - `get_connection(db_path=None)`.
   - `initialize_database(db_path=None, reset=False)`.
   - `table_exists(connection, table_name)`.
   - `write_dataframe(connection, table_name, dataframe, if_exists="append")`.
   - `read_table(connection, table_name, limit=None)`.
   - `load_sample_csvs_to_sqlite(data_dir=None, db_path=None, reset=False)`.
   - Insert a `pipeline_runs` row for each load attempt.
5. Ensure SQLite paths come from `semipulse.config.get_settings()`.
6. Do not make the app rely only on in-memory DataFrames. This slice should persist raw or cleaned sample data into SQLite.
7. Add tests for:
   - Schema creation.
   - Required tables exist.
   - Sample CSVs load into the four source tables.
   - Row counts are greater than zero after loading generated data.
8. Update docs with database commands and current state.

## API or Function Contract
- `get_connection(db_path: Path | str | None = None) -> sqlite3.Connection`
- `initialize_database(db_path: Path | str | None = None, reset: bool = False) -> Path`
- `table_exists(connection: sqlite3.Connection, table_name: str) -> bool`
- `write_dataframe(connection: sqlite3.Connection, table_name: str, dataframe: pandas.DataFrame, if_exists: str = "append") -> None`
- `read_table(connection: sqlite3.Connection, table_name: str, limit: int | None = None) -> pandas.DataFrame`
- `load_sample_csvs_to_sqlite(data_dir: Path | str | None = None, db_path: Path | str | None = None, reset: bool = False) -> dict[str, int]`

## Acceptance criteria
- `db/schema.sql` creates all required tables.
- `python -m semipulse.sample_data` followed by the database load helper creates `db/semipulse.db`.
- Source tables contain sample rows after loading.
- `pipeline_runs` records the database load.
- Tests pass without requiring Streamlit to run.

## Tests what to test and how to run
- Run:
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  python -m semipulse.sample_data
  python - <<'PY'
  from semipulse.database import initialize_database, load_sample_csvs_to_sqlite
  initialize_database(reset=True)
  print(load_sample_csvs_to_sqlite(reset=False))
  PY
  pytest tests/test_database.py
  ```
- Expected results:
  - The database file exists at `db/semipulse.db`.
  - Row counts are printed for machines, sensor readings, maintenance records, and defect records.
  - Database tests pass.

## Stop and verify commands and expected results
Run:
```bash
python - <<'PY'
from semipulse.database import get_connection, read_table
conn = get_connection()
for table in ["machines", "sensor_readings", "maintenance_records", "defect_records", "pipeline_runs"]:
    print(table, len(read_table(conn, table)))
conn.close()
PY
pytest
```

Expected results:
- Each source table prints a row count greater than zero.
- `pipeline_runs` has at least one row.
- `pytest` passes.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

For this slice, explicitly smoke test: generate sample data, initialize SQLite, load CSVs, and read back the four source tables.
