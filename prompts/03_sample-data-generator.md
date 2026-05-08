Status: NOT_STARTED

# 03 Sample Data Generator

## Goal
Build a reproducible simulated semiconductor equipment dataset generator. It must create machine metadata, sensor readings, maintenance records, and defect records with realistic simulated degradation patterns while clearly labeling the data as simulated.

## Files to create/modify exact paths
- `semipulse/sample_data.py`
- `tests/test_sample_data.py`
- `data/sample/.gitkeep`
- `README.md`
- `START_HERE.md`
- `CURRENT_STATE.md`

## Steps
1. Implement `semipulse/sample_data.py` with a CLI entrypoint:
   - Running `python -m semipulse.sample_data` writes CSVs to `SEMIPULSE_DATA_DIR`, defaulting to `data/sample/`.
   - Use `SEMIPULSE_RANDOM_SEED`, defaulting to `42`.
2. Generate `machines.csv` with required columns:
   - `machine_id`
   - `machine_type`
   - `manufacturer`
   - `facility_area`
   - `install_date`
   - `status`
   - Include useful optional columns such as `criticality`, `line_id`, `process_step`, `last_service_date`, and `expected_lifetime_years`.
3. Generate `sensor_readings.csv` with required columns:
   - `reading_id`
   - `machine_id`
   - `timestamp`
   - `temperature`
   - `vibration`
   - `pressure`
   - `power_draw`
   - Include optional columns if useful: `runtime_hours`, `cycle_count`, `error_code`, `chamber_pressure`, `gas_flow_rate`.
4. Generate `maintenance_records.csv` with required columns:
   - `maintenance_id`
   - `machine_id`
   - `maintenance_date`
   - `maintenance_type`
   - `downtime_hours`
   - Include optional fields such as `severity`, `resolved`, `maintenance_cost`, `parts_replaced`.
5. Generate `defect_records.csv` with required columns:
   - `defect_id`
   - `machine_id`
   - `timestamp`
   - `defect_count`
   - `batch_id`
   - Include optional fields such as `defect_type`, `severity`, `yield_loss_pct`, `process_step`, `wafer_lot`.
6. Simulate realistic but honest patterns:
   - Vibration trends upward before emergency maintenance or failure-like events.
   - Temperature anomalies appear before service events.
   - Defect counts increase near degraded machine periods.
   - Downtime appears after maintenance events.
   - Do not claim these patterns represent real semiconductor factory behavior.
7. Keep datasets small enough for a portfolio demo by default:
   - Default around 40 to 75 machines.
   - 90 to 180 days of daily or subdaily readings.
   - Configurable row counts through function parameters.
8. Add tests for:
   - Required CSV files are created.
   - Required columns exist.
   - Generation is reproducible with a fixed seed.
   - IDs in sensor, maintenance, and defect tables refer to generated machines.
9. Update docs with the sample data command and simulated-data caveat.

## API or Function Contract
- `generate_sample_data(output_dir: Path | str | None = None, random_seed: int | None = None, num_machines: int = 50, days: int = 120) -> dict[str, Path]`
  - Writes all four CSVs.
  - Returns a mapping from dataset name to written file path.
- `generate_machines(...) -> pandas.DataFrame`
- `generate_sensor_readings(...) -> pandas.DataFrame`
- `generate_maintenance_records(...) -> pandas.DataFrame`
- `generate_defect_records(...) -> pandas.DataFrame`

## Acceptance criteria
- `python -m semipulse.sample_data` creates:
  - `data/sample/machines.csv`
  - `data/sample/sensor_readings.csv`
  - `data/sample/maintenance_records.csv`
  - `data/sample/defect_records.csv`
- All required columns are present.
- Generated foreign keys reference valid `machine_id` values.
- Running with the same random seed produces repeatable data.
- The docs explicitly say the dataset is simulated.

## Tests what to test and how to run
- Run:
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  python -m semipulse.sample_data
  pytest tests/test_sample_data.py
  ```
- Expected results:
  - The four sample CSV files are written under `data/sample/`.
  - Tests pass.
  - No network access or large model downloads occur.

## Stop and verify commands and expected results
Run:
```bash
python -m semipulse.sample_data
python - <<'PY'
import pandas as pd
for name in ["machines", "sensor_readings", "maintenance_records", "defect_records"]:
    df = pd.read_csv(f"data/sample/{name}.csv")
    print(name, df.shape, list(df.columns))
PY
pytest
```

Expected results:
- Each CSV has rows and the required columns.
- `pytest` passes.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

For this slice, the smoke test path is `python -m semipulse.sample_data`; it must leave the project ready for the later SQLite, feature, model, and dashboard steps.
