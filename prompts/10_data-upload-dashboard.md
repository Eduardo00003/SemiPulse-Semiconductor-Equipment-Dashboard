Status: NOT_STARTED

# 10 Data Upload Dashboard

## Goal
Add a Streamlit Data Upload / Load page that can load generated sample CSVs, accept uploaded CSVs, preview datasets, validate schemas, and rebuild the SQLite pipeline. Keep upload and pipeline logic in reusable modules, not embedded in page code.

## Files to create/modify exact paths
- `app/pages/data_upload.py`
- `app/streamlit_app.py`
- `semipulse/data_loader.py`
- `semipulse/validation.py`
- `semipulse/pipeline.py`
- `tests/test_pipeline.py`
- `README.md`
- `START_HERE.md`
- `CURRENT_STATE.md`

## Steps
1. Add `semipulse/pipeline.py` as a thin orchestrator:
   - Generate sample data when requested.
   - Rebuild database from a data directory.
   - Generate features.
   - Train model and write predictions when requested.
   - Return a structured status summary for UI display.
2. Create `app/pages/data_upload.py`:
   - Let the user load existing sample data from `data/sample/`.
   - Let the user generate fresh sample data.
   - Provide upload widgets for:
     - `machines.csv`
     - `sensor_readings.csv`
     - `maintenance_records.csv`
     - `defect_records.csv`
   - Preview uploaded or sample datasets.
   - Validate datasets and show issue summaries.
   - Trigger database rebuild.
   - Trigger full pipeline rebuild: database, features, model, predictions.
3. Uploaded CSV handling:
   - Save temporary uploaded files under `data/raw/uploads/` or a clearly named local path.
   - Do not store secrets.
   - Do not crash on malformed CSVs; show validation errors.
4. Update `app/streamlit_app.py` to route to the implemented Data Upload / Load page.
5. Add tests for the pipeline orchestrator without requiring Streamlit.
6. Update docs with UI workflow and CLI equivalent commands.

## API or Function Contract
- `run_demo_pipeline(generate_data: bool = False, reset_database: bool = True, train_model: bool = True) -> dict`
- `validate_data_directory(data_dir: Path | str | None = None) -> ValidationResult`
- `save_uploaded_datasets(files: dict[str, BinaryIO], destination_dir: Path | str) -> dict[str, Path]`

## Acceptance criteria
- Data Upload / Load page renders in Streamlit.
- Users can generate or load sample data from the UI.
- Users can upload the four required CSVs and see previews.
- Validation issues are shown clearly.
- Full pipeline rebuild writes SQLite tables, features, model runs, and risk predictions.
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
  pytest tests/test_pipeline.py
  streamlit run app/streamlit_app.py
  ```
- Expected results:
  - The pipeline summary reports successful data, database, features, model, and prediction steps.
  - Tests pass.
  - Streamlit Data Upload / Load page can generate sample data and rebuild the pipeline without a traceback.

## Stop and verify commands and expected results
Run:
```bash
python - <<'PY'
from semipulse.pipeline import run_demo_pipeline
from semipulse.database import get_connection, read_table
print(run_demo_pipeline(generate_data=True, reset_database=True, train_model=True))
conn = get_connection()
for table in ["machines", "machine_features", "model_runs", "risk_predictions"]:
    print(table, len(read_table(conn, table)))
conn.close()
PY
pytest
streamlit run app/streamlit_app.py
```

Expected results:
- Required tables have rows.
- Tests pass.
- Streamlit page works manually.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

For this slice, smoke test both the CLI pipeline orchestrator and the Streamlit Data Upload / Load page.
