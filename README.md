# SemiPulse: Predictive Maintenance Dashboard

SemiPulse is a portfolio-ready predictive maintenance dashboard for simulated semiconductor manufacturing equipment. It generates or loads equipment CSVs, validates and cleans them, persists the data in SQLite, engineers machine-level features, trains a local scikit-learn risk model, and presents operational views in Streamlit.

## Simulated Data Notice

All datasets in this project are simulated. Model metrics, including recall, precision, F1, accuracy, and ROC-AUC, are simulated-data performance only. SemiPulse does not claim real semiconductor factory accuracy.

## What It Includes

- Reproducible simulated datasets for machines, sensor readings, maintenance records, and defect records.
- CSV validation for required columns, timestamps, numeric values, duplicate IDs, and orphan machine references.
- SQLite persistence for raw/cleaned entities, machine features, model runs, predictions, pipeline runs, and data quality issues.
- Pandas feature engineering for sensors, rolling windows, maintenance history, downtime, defects, and machine metadata.
- Local `RandomForestClassifier` training with saved model and metadata artifacts.
- Streamlit dashboard pages for fleet overview, data loading, machine health, maintenance risk, defect trends, downtime analysis, model performance, and data exploration.
- CSV/JSON exports for risk rankings, machine features, model metrics, and selected SQLite tables.
- Docker Compose support for reproducible local execution.

## Architecture

```text
CSV / generated sample data
        -> validation + cleaning
        -> SQLite tables
        -> feature engineering
        -> scikit-learn model training / loading
        -> risk predictions + model metrics
        -> Streamlit dashboard + exports
```

Reusable data, model, database, plotting, and export logic lives in `semipulse/`. Streamlit UI code lives in `app/`.

## Project Structure

- `app/streamlit_app.py` launches the Streamlit dashboard.
- `app/pages/` contains Overview, Data Upload / Load, Machine Health, Maintenance Risk, Defect Trends, Downtime Analysis, Model Performance, and Data Explorer pages.
- `semipulse/sample_data.py` generates simulated sample CSVs.
- `semipulse/validation.py`, `semipulse/data_loader.py`, and `semipulse/database.py` validate, clean, and persist data.
- `semipulse/features.py` builds machine-level features.
- `semipulse/model.py`, `semipulse/predict.py`, and `semipulse/metrics.py` train and score the local model.
- `semipulse/pipeline.py` orchestrates the demo flow.
- `semipulse/exports.py` supports dashboard downloads.
- `db/schema.sql` defines the SQLite schema.
- `tests/` contains pytest coverage for validation, loading, features, model training, pipeline orchestration, database helpers, and exports.

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On this macOS environment, `python3` is available before virtual environment activation. After activation, use the venv `python`.

## Run the Pipeline

Generate sample data:

```bash
python -m semipulse.sample_data
```

Run the full demo pipeline:

```bash
python - <<'PY'
from semipulse.pipeline import run_demo_pipeline
print(run_demo_pipeline(generate_data=False, reset_database=True, train_model=True))
PY
```

The pipeline rebuilds SQLite, writes `machine_features`, trains a local model, writes `models/risk_model.pkl` and `models/model_metadata.json`, and stores risk predictions in SQLite.

Individual commands are also available:

```bash
python -m semipulse.features
python -m semipulse.model
```

## Launch Dashboard

```bash
streamlit run app/streamlit_app.py
```

The dashboard is available at `http://localhost:8501` by default.

## Dashboard Pages

- Overview: fleet KPIs, risk summary, downtime, defects, and setup status.
- Data Upload / Load: sample generation, CSV upload, validation, previews, and rebuild actions.
- Machine Health: sensor trends, fleet averages, machine details, and anomaly indicators.
- Maintenance Risk: ranked machine risk, filters, and detail context.
- Defect Trends: defect volume over time, by machine, by process step, and by severity.
- Downtime Analysis: downtime by machine, type, maintenance category, and risk band.
- Model Performance: simulated-data metrics, confusion matrix, metadata, and recall context.
- Data Explorer: SQLite table previews, text search, row limits, and exports.

## Exports

The Data Explorer page provides:

- ranked risk predictions CSV,
- machine features CSV,
- model metrics JSON,
- selected table CSV.

The same export logic is available in `semipulse/exports.py` for tests or scripts.

## Docker

```bash
docker compose up --build
```

The dashboard is available at `http://localhost:8501` by default. Override the host port with `SEMIPULSE_STREAMLIT_PORT`.

Compose uses Docker-managed volumes for `/app/data`, `/app/db`, and `/app/models` so generated sample data, SQLite state, and model artifacts persist without requiring host-directory mounts.

## Tests

```bash
pytest
```

The current test suite covers the local data pipeline, validation rules, SQLite helpers, feature generation, model training, pipeline orchestration, export helpers, and Streamlit app import/render behavior.

## Deployment Notes

For a portfolio demo, deploy the Streamlit app with the entrypoint `app/streamlit_app.py`. Streamlit Community Cloud, Render, Railway, and Fly.io can run this app as long as `requirements.txt` is installed and environment variables from `.env.example` are configured. Generate sample data from the UI or run the pipeline commands before demoing persisted results.

## Prompt Execution

Development is driven by the prompt files in `prompts/`, in numeric order from `01_project-freeze-and-docs.md` through `17_docs-qa-polish.md`. Each prompt includes acceptance criteria and verification commands, and should only be marked `COMPLETED` after those checks pass or a documented environment limitation is captured honestly.
