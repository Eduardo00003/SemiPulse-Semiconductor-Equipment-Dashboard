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
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

These commands will become active once the repository structure and dependency file are created in prompt 02.

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

## Prompt Execution

Development is driven by the prompt files in `prompts/`, in numeric order from `01_project-freeze-and-docs.md` through `17_docs-qa-polish.md`.

Each prompt starts with a status marker:

```text
Status: NOT_STARTED | IN_PROGRESS | COMPLETED
```

Only mark a prompt `COMPLETED` after its acceptance criteria and verification commands pass, or after unavailable baseline behavior is documented honestly.
