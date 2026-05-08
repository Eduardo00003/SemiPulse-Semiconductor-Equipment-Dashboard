Status: NOT_STARTED

# 17 Docs QA Polish

## Goal
Finalize SemiPulse as a portfolio-ready MVP. Refresh documentation, run the full QA checklist, verify local and Docker execution, confirm all required dashboard pages and exports work, and clearly document limitations.

## Files to create/modify exact paths
- `README.md`
- `TECHNICAL.md`
- `START_HERE.md`
- `CURRENT_STATE.md`
- `.env.example`
- Any tests that need small fixes:
  - `tests/test_validation.py`
  - `tests/test_features.py`
  - `tests/test_model.py`
  - `tests/test_database.py`
  - `tests/test_data_loader.py`
  - `tests/test_pipeline.py`
  - `tests/test_exports.py`

## Steps
1. Run the full local QA flow:
   - Create/activate virtual environment.
   - Install dependencies.
   - Generate sample data.
   - Rebuild SQLite.
   - Generate features.
   - Train model and predictions.
   - Run tests.
   - Launch Streamlit.
2. Run Docker QA:
   - `docker compose config`
   - `docker compose up --build`
3. Verify dashboard pages manually:
   - Overview.
   - Data Upload / Load.
   - Machine Health.
   - Maintenance Risk.
   - Defect Trends.
   - Downtime Analysis.
   - Model Performance.
   - Data Explorer.
4. Verify exports:
   - Risk ranking CSV.
   - Machine features CSV.
   - Model metrics CSV or JSON.
   - Selected table CSV.
5. Update `README.md`:
   - Strong project summary.
   - Screens/demo instructions if screenshots are available.
   - Setup commands.
   - Local run commands.
   - Docker commands.
   - Pipeline commands.
   - Dashboard page summary.
   - Export summary.
   - Simulated-data and model limitation section.
   - Portfolio/resume framing.
6. Update `TECHNICAL.md` to match the final code:
   - Architecture.
   - Data contracts.
   - SQLite tables.
   - Feature engineering.
   - Model training.
   - Streamlit pages.
   - Exports.
   - Known limitations.
7. Update `START_HERE.md`:
   - Confirm all listed paths exist.
   - Add recommended first files to inspect.
   - Add commands for local, tests, pipeline, and Docker.
8. Update `CURRENT_STATE.md`:
   - Mark completed pieces accurately.
   - Note known issues and limitations.
   - Include latest successful verification commands and date.
9. Fix small test/doc drift issues discovered during QA.
10. Do not add unrelated features.

## Acceptance criteria
- All tests pass.
- The app runs locally through Streamlit.
- The app runs through Docker.
- The sample-data pipeline works end-to-end.
- SQLite stores cleaned data, features, model runs, predictions, and data quality issues.
- The dashboard shows fleet KPIs, machine health, downtime, defect trends, ranked risk, model metrics, and data explorer views.
- Exports work.
- Documentation is accurate, concise, and honest about simulated data.

## Tests what to test and how to run
- Run:
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  python -m semipulse.sample_data
  python - <<'PY'
  from semipulse.pipeline import run_demo_pipeline
  print(run_demo_pipeline(generate_data=False, reset_database=True, train_model=True))
  PY
  pytest
  streamlit run app/streamlit_app.py
  docker compose config
  docker compose up --build
  ```
- Expected results:
  - Sample data is present.
  - Full pipeline completes.
  - Tests pass.
  - Streamlit works locally.
  - Docker Compose config validates and app launches.

## Stop and verify commands and expected results
Run:
```bash
python - <<'PY'
from pathlib import Path
required = [
    "app/streamlit_app.py",
    "semipulse/config.py",
    "semipulse/database.py",
    "semipulse/schema.py",
    "semipulse/validation.py",
    "semipulse/data_loader.py",
    "semipulse/sample_data.py",
    "semipulse/features.py",
    "semipulse/model.py",
    "semipulse/predict.py",
    "semipulse/metrics.py",
    "semipulse/exports.py",
    "semipulse/plots.py",
    "db/schema.sql",
    "Dockerfile",
    "docker-compose.yml",
]
missing = [p for p in required if not Path(p).exists()]
print("missing:", missing)
PY
pytest
```

Expected results:
- The missing list is empty.
- `pytest` passes.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

For this final slice, perform the full manual QA checklist and document the result in `CURRENT_STATE.md`.
