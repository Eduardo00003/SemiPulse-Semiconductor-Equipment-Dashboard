Status: NOT_STARTED

# 05 Data Validation

## Goal
Add reusable CSV and DataFrame validation for SemiPulse datasets. The validator must enforce the required dataset contracts, report bad rows and schema issues clearly, and store data quality issues in SQLite when a database connection is available.

## Files to create/modify exact paths
- `semipulse/validation.py`
- `semipulse/database.py`
- `tests/test_validation.py`
- `README.md`
- `START_HERE.md`
- `CURRENT_STATE.md`

## Steps
1. Implement `semipulse/validation.py` with required-column contracts for:
   - `machines`
   - `sensor_readings`
   - `maintenance_records`
   - `defect_records`
2. Validate:
   - Missing required columns.
   - Invalid timestamps and dates.
   - Duplicate IDs:
     - `machine_id`
     - `reading_id`
     - `maintenance_id`
     - `defect_id`
   - Orphan `machine_id` references in sensor, maintenance, and defect data.
   - Numeric parsing/range issues for sensor values, defect counts, downtime hours, and yield loss if present.
   - Missing values in required fields.
3. Return structured validation results instead of raising for normal data issues.
4. Add severity levels:
   - `error`
   - `warning`
   - `info`
5. Add a helper to persist validation issues into `data_quality_issues`.
6. Update `load_sample_csvs_to_sqlite` or add a wrapper so validation can run before loading without breaking existing database behavior.
7. Tests should cover valid generated data and intentionally invalid DataFrames.
8. Update docs with validation behavior and how issues are stored.

## API or Function Contract
- `ValidationIssue`
  - Fields:
    - `dataset: str`
    - `severity: str`
    - `issue_type: str`
    - `message: str`
    - `row_count: int | None`
    - `column: str | None`
- `ValidationResult`
  - Fields:
    - `is_valid: bool`
    - `issues: list[ValidationIssue]`
  - Convenience properties or methods for `errors`, `warnings`, and `to_dataframe()`.
- `validate_dataset(name: str, dataframe: pandas.DataFrame, machines: pandas.DataFrame | None = None) -> ValidationResult`
- `validate_all_datasets(datasets: dict[str, pandas.DataFrame]) -> ValidationResult`
- `persist_validation_issues(connection: sqlite3.Connection, issues: list[ValidationIssue], pipeline_run_id: str | None = None) -> int`

## Acceptance criteria
- Generated sample CSVs validate successfully or only produce documented non-blocking warnings.
- Invalid CSVs/DataFrames return useful validation issues.
- Missing columns are reported by dataset name.
- Orphan machine IDs are detected.
- Data quality issues can be stored in SQLite.
- Tests pass.

## Tests what to test and how to run
- Run:
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  python -m semipulse.sample_data
  python - <<'PY'
  import pandas as pd
  from pathlib import Path
  from semipulse.validation import validate_all_datasets
  base = Path("data/sample")
  datasets = {name: pd.read_csv(base / f"{name}.csv") for name in ["machines", "sensor_readings", "maintenance_records", "defect_records"]}
  result = validate_all_datasets(datasets)
  print("valid=", result.is_valid)
  print(result.to_dataframe().head())
  PY
  pytest tests/test_validation.py
  ```
- Expected results:
  - Validation completes without crashing.
  - Valid generated sample data has no blocking errors.
  - Validation tests pass.

## Stop and verify commands and expected results
Run:
```bash
pytest
python - <<'PY'
from semipulse.database import get_connection, read_table
conn = get_connection()
print(read_table(conn, "data_quality_issues", limit=5))
conn.close()
PY
```

Expected results:
- `pytest` passes.
- `data_quality_issues` can be read even when it is empty.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

For this slice, smoke test generated sample data validation before database loading. Validation must not prevent a clean generated dataset from loading into SQLite.
