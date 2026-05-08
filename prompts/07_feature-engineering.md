Status: COMPLETED

# 07 Feature Engineering

## Goal
Generate a model-ready `machine_features` table from cleaned SQLite data. Include sensor aggregates, rolling-window signals, maintenance recency and downtime features, defect features, and metadata features.

## Files to create/modify exact paths
- `semipulse/features.py`
- `semipulse/database.py`
- `tests/test_features.py`
- `README.md`
- `START_HERE.md`
- `CURRENT_STATE.md`

## Steps
1. Implement `semipulse/features.py` so it can read cleaned tables from SQLite and write `machine_features`.
2. Include sensor features:
   - `avg_temperature`
   - `max_temperature`
   - `std_temperature`
   - `avg_vibration`
   - `max_vibration`
   - `std_vibration`
   - `avg_pressure`
   - `var_pressure`
   - `avg_power_draw`
   - `var_power_draw`
3. Include rolling-window features:
   - `rolling_7d_avg_temperature`
   - `rolling_7d_avg_vibration`
   - `rolling_7d_defect_count`
   - `rolling_30d_maintenance_count`
   - `recent_downtime_hours`
4. Include maintenance features:
   - `days_since_last_maintenance`
   - `total_maintenance_events`
   - `total_downtime_hours`
   - `avg_downtime_per_event`
   - `emergency_maintenance_count`
   - `maintenance_frequency`
5. Include defect features:
   - `total_defect_count`
   - `recent_defect_count`
   - `avg_defects_per_batch`
   - `defect_severity_score`
   - `yield_loss_pct_avg`
6. Include metadata features:
   - `machine_age_days`
   - `machine_type`
   - `manufacturer`
   - `criticality`
   - `facility_area`
7. Add a binary training target helper:
   - `target_failure_within_window`
   - Use maintenance/defect/degradation events within the configurable prediction window.
   - Keep the definition simple and documented because the dataset is simulated.
8. Store generated features in SQLite table `machine_features`.
9. Add tests for:
   - Expected feature columns.
   - One feature row per machine.
   - Rolling-window calculations on small controlled data.
   - Days since last maintenance.
   - No all-null numeric feature columns on generated sample data.
10. Add a CLI entrypoint so `python -m semipulse.features` rebuilds features from the configured SQLite database.
11. Update docs.

## API or Function Contract
- `build_machine_features(datasets: dict[str, pandas.DataFrame], as_of_date: pandas.Timestamp | None = None, prediction_window_days: int | None = None) -> pandas.DataFrame`
- `build_features_from_database(db_path: Path | str | None = None, write: bool = True) -> pandas.DataFrame`
- `write_machine_features(connection: sqlite3.Connection, features: pandas.DataFrame, if_exists: str = "replace") -> int`

## Acceptance criteria
- `machine_features` is generated and stored in SQLite.
- Feature columns cover all required feature groups.
- The target label exists for model training.
- The implementation uses Pandas and remains testable outside Streamlit.
- Tests pass.

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
  pytest tests/test_features.py
  ```
- Expected results:
  - `python -m semipulse.features` writes rows to `machine_features`.
  - Feature tests pass.

## Stop and verify commands and expected results
Run:
```bash
python - <<'PY'
from semipulse.database import get_connection, read_table
conn = get_connection()
features = read_table(conn, "machine_features")
print(features.shape)
print(features.columns.tolist())
print(features[["machine_id", "avg_temperature", "avg_vibration", "recent_defect_count", "target_failure_within_window"]].head())
conn.close()
PY
pytest
```

Expected results:
- `machine_features` has one row per machine.
- Required feature columns are present.
- `pytest` passes.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

For this slice, smoke test: generate sample data, rebuild SQLite, run `python -m semipulse.features`, and read `machine_features`.
