# SemiPulse: Predictive Maintenance Dashboard

SemiPulse is a portfolio-focused predictive maintenance analytics dashboard for simulated semiconductor manufacturing equipment.

The finished MVP will generate or load simulated equipment datasets, validate and clean CSV inputs, persist data in SQLite, engineer Pandas features, train a local scikit-learn risk model, and display machine health, downtime, defect trends, model performance, and ranked maintenance risk in Streamlit.

## Simulated Data Notice

All datasets in this project are simulated. Model metrics, including recall, precision, F1, accuracy, and ROC-AUC, must be described as simulated-data performance only. SemiPulse does not claim real semiconductor factory accuracy.

## Planned Stack

- Python 3.11+
- Pandas and NumPy
- scikit-learn and joblib
- SQLite
- Streamlit
- Matplotlib
- pytest
- python-dotenv
- Docker and Docker Compose

## Planned Architecture

```text
CSV / generated sample data
        -> validation + cleaning
        -> SQLite tables
        -> feature engineering
        -> scikit-learn model training / loading
        -> risk predictions + model metrics
        -> Streamlit dashboard + exports
```

Reusable data, model, database, and export logic will live in `semipulse/`. Streamlit UI code will live in `app/`.

## Current Structure

- `semipulse/config.py` loads environment-driven runtime settings.
- `semipulse/logging_utils.py` configures standard-library logging.
- `semipulse/sample_data.py` generates reproducible simulated sample CSVs.
- `semipulse/database.py` and `semipulse/schema.py` initialize SQLite and load sample CSVs.
- `semipulse/validation.py` validates required columns, timestamps, duplicates, numeric fields, and machine references.
- `semipulse/data_loader.py` loads, cleans, validates, merges, and rebuilds SQLite from CSVs.
- `semipulse/features.py` generates model-ready machine features and writes `machine_features`.
- `semipulse/model.py`, `semipulse/predict.py`, and `semipulse/metrics.py` train a local scikit-learn model, score risk, and store predictions.
- `app/streamlit_app.py` launches the Streamlit shell and Overview page.
- `app/`, `app/pages/`, `data/`, `db/`, `models/`, and `tests/` exist as the implementation skeleton.

## Baseline Flow

The intended runnable flow is:

1. Generate or load sample data.
2. Build or open the SQLite database.
3. Generate machine-level features.
4. Train or load the local scikit-learn model.
5. Produce risk scores.
6. Launch the Streamlit dashboard.

The implementation prompts in `prompts/` build this flow incrementally while keeping the project runnable after each slice.

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Planned Runtime Commands

```bash
python -m semipulse.sample_data
python -m semipulse.features
python -m semipulse.model
pytest
streamlit run app/streamlit_app.py
docker compose up --build
```

At the prompt-01 baseline, these commands are documented targets. The implementation modules are created in later prompts.

On this local macOS environment, use `python3` for creating the virtual environment. After activation, `.venv/bin/python` provides the `python` command used by later project commands.

## Generate Sample Data

```bash
source .venv/bin/activate
python -m semipulse.sample_data
```

This writes simulated CSVs to `data/sample/`.

## Build SQLite Database

```bash
source .venv/bin/activate
python - <<'PY'
from semipulse.data_loader import rebuild_database_from_csvs
print(rebuild_database_from_csvs(reset=True))
PY
```

Validation runs before writing cleaned sample CSV data and stores blocking data quality issues in SQLite when issues are detected.

## Generate Features

```bash
source .venv/bin/activate
python -m semipulse.features
```

Feature generation reads cleaned SQLite tables and writes one row per machine to `machine_features`.

## Train Model and Score Risk

```bash
source .venv/bin/activate
python -m semipulse.model
```

This trains a local `RandomForestClassifier` on simulated features, writes `models/risk_model.pkl` and `models/model_metadata.json`, and stores risk scores in SQLite. Metrics are simulated-data performance only.

## Launch Dashboard

```bash
source .venv/bin/activate
streamlit run app/streamlit_app.py
```

## Prompt Execution

Development is driven by the prompt files in `prompts/`, in numeric order from `01_project-freeze-and-docs.md` through `17_docs-qa-polish.md`.

Each prompt starts with a status marker:

```text
Status: NOT_STARTED | IN_PROGRESS | COMPLETED
```

Only mark a prompt `COMPLETED` after its acceptance criteria and verification commands pass, or after unavailable baseline behavior is documented honestly.
