# Start Here

This document is the navigation map for the completed SemiPulse MVP.

## Read First

1. `README.md` for setup, runtime commands, dashboard pages, exports, and deployment notes.
2. `TECHNICAL.md` for architecture, data contracts, SQLite tables, features, modeling, and QA expectations.
3. `CURRENT_STATE.md` for the latest implementation status and verification notes.
4. `MasterPrompt.md` and `prompts/` for the prompt-driven build history.

## Entry Points

- Streamlit app: `app/streamlit_app.py`
- Demo pipeline: `semipulse/pipeline.py`
- Sample data generator: `semipulse/sample_data.py`
- SQLite schema: `db/schema.sql`
- Docker runtime: `Dockerfile`, `docker-compose.yml`
- Tests: `tests/`

## Implemented Files To Inspect

- Dashboard pages: `app/pages/overview.py`, `app/pages/data_upload.py`, `app/pages/machine_health.py`, `app/pages/maintenance_risk.py`, `app/pages/defect_trends.py`, `app/pages/downtime_analysis.py`, `app/pages/model_performance.py`, `app/pages/data_explorer.py`
- Config and logging: `semipulse/config.py`, `semipulse/logging_utils.py`
- Data pipeline: `semipulse/validation.py`, `semipulse/data_loader.py`, `semipulse/database.py`, `semipulse/schema.py`
- Feature/model pipeline: `semipulse/features.py`, `semipulse/model.py`, `semipulse/predict.py`, `semipulse/metrics.py`
- UI helpers and exports: `semipulse/plots.py`, `semipulse/exports.py`

## Local Commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m semipulse.sample_data
python - <<'PY'
from semipulse.pipeline import run_demo_pipeline
print(run_demo_pipeline(generate_data=False, reset_database=True, train_model=True))
PY
pytest
streamlit run app/streamlit_app.py
```

Local note: this environment has `python3` available on `PATH`; after virtual environment activation, use the venv's `python`.

## Docker Command

```bash
docker compose up --build
```

The Docker command serves the dashboard on `http://localhost:8501` by default and uses named volumes for generated data, the SQLite database, and model artifacts.

## Non-Negotiable Constraints

- The data is simulated.
- Model metrics are simulated-data performance only.
- Use SQLite for MVP persistence.
- Use scikit-learn for modeling.
- Do not download large AI models or call external LLMs for the ML pipeline.
- Keep heavy processing out of Streamlit page code.
