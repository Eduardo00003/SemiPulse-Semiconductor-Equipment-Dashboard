# Current State

Last updated: 2026-05-08

## What Works Now

- Project requirements exist in `MasterPrompt.md`.
- Technical guidance exists in `TECHNICAL.md`.
- The full 17-file implementation prompt sequence exists in `prompts/`.
- Prompt 01 documentation files have been added.
- Final project directories exist for `app/`, `semipulse/`, `data/`, `db/`, `models/`, and `tests/`.
- `requirements.txt` exists with the MVP Python dependencies.
- `semipulse/config.py` loads environment-variable settings with defaults.
- `semipulse/logging_utils.py` provides a reusable logging setup helper.
- `semipulse/sample_data.py` generates simulated machine, sensor, maintenance, and defect CSVs.
- `db/schema.sql` defines the required SQLite MVP tables.
- `semipulse/database.py` can initialize SQLite and load sample CSVs.
- `semipulse/validation.py` validates CSV/DataFrame contracts and can persist data quality issues.
- `semipulse/data_loader.py` cleans CSV data, builds a machine-level analytical table, and rebuilds SQLite from CSVs.
- `semipulse/features.py` generates machine-level model features and stores `machine_features`.
- `semipulse/model.py`, `semipulse/predict.py`, and `semipulse/metrics.py` train a local scikit-learn model, save artifacts, and store risk predictions.
- `app/streamlit_app.py` and `app/pages/overview.py` provide the Streamlit shell and Overview dashboard.
- `semipulse/pipeline.py` orchestrates the demo pipeline for tests and UI actions.
- `app/pages/data_upload.py` provides sample loading, CSV upload, validation, previews, and pipeline rebuild actions.
- `app/pages/machine_health.py` shows sensor trends, fleet averages, machine details, and heuristic anomaly indicators.
- `app/pages/maintenance_risk.py` ranks machines by simulated maintenance risk and provides filters/detail context.
- `app/pages/defect_trends.py` and `app/pages/downtime_analysis.py` show simulated defect and downtime analysis.
- `app/pages/model_performance.py` displays simulated model metrics, confusion matrix, metadata, and recall context.

## What Is Missing

- Streamlit app under `app/`.
- Remaining dashboard page after Overview, Data Upload / Load, Machine Health, Maintenance Risk, Defect Trends, Downtime Analysis, and Model Performance.
- CSV/JSON export helpers.
- Docker support.

## Known Issues and Limitations

- There is no runnable dashboard yet.
- There is no sample dataset yet.
- There is no SQLite database yet.
- There are no tests yet.
- The baseline flow is documented but not implemented at this stage.

## Current Commands

Useful inspection commands:

```bash
ls -la
find prompts -maxdepth 1 -type f | sort
python3 --version
```

Planned commands after later prompts:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
python -m semipulse.sample_data
python -m semipulse.features
python -m semipulse.model
streamlit run app/streamlit_app.py
docker compose up --build
```

Local environment note: `python` is not available before virtual environment activation in this shell, but `python3` is available and was verified as Python 3.13.5.

## Current Dataset Assumptions

- All future data will be simulated semiconductor manufacturing equipment data.
- Required source datasets will be:
  - `machines.csv`
  - `sensor_readings.csv`
  - `maintenance_records.csv`
  - `defect_records.csv`
- Generated CSV files can be created under `data/sample/` with `python -m semipulse.sample_data`.

## Current Model Limitations

- A local scikit-learn baseline model has been implemented.
- Future model metrics must be labeled as simulated-data performance only.
- The project must use local scikit-learn modeling, not external LLMs or large downloaded AI models.

## Capability Status

| Capability | Status |
| --- | --- |
| Repo structure and config | Implemented |
| Sample data | Implemented |
| SQLite database | Implemented |
| Data validation | Implemented |
| Data cleaning and merging | Implemented |
| Feature engineering | Implemented |
| Model training | Implemented |
| Risk scoring | Implemented |
| Streamlit dashboard | Overview, Data Upload, Machine Health, Maintenance Risk, Defect Trends, Downtime Analysis, and Model Performance implemented |
| Exports | Not implemented |
| Docker | Not implemented |

## Baseline Freeze

The repository did not have Git initialized before prompt 01. Prompt 01 initialized Git, created the first baseline commit, and tagged the baseline as `prototype-v0`.
