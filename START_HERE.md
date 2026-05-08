# Start Here

This document is the navigation map for SemiPulse. At the prompt-01 baseline, most implementation paths are planned but not yet created. Later prompts update this file as modules become real.

## Current Entry Points

- Master requirements: `MasterPrompt.md`
- Technical guide: `TECHNICAL.md`
- Prompt generator spec: `promptForPrompt.txt`
- Implementation prompts: `prompts/`

## Implemented App and Pipeline Files

- Config: `semipulse/config.py`
- Logging helpers: `semipulse/logging_utils.py`
- Sample data generator: `semipulse/sample_data.py`
- SQLite connection helpers: `semipulse/database.py`
- SQLite schema helpers: `semipulse/schema.py`
- SQLite schema: `db/schema.sql`
- Data validation: `semipulse/validation.py`
- Data loading and merging: `semipulse/data_loader.py`
- Feature generation: `semipulse/features.py`

## Planned App and Pipeline Files

- Streamlit entrypoint: `app/streamlit_app.py`
- Dashboard pages: `app/pages/`
- Model training: `semipulse/model.py`
- Prediction/risk scoring: `semipulse/predict.py`
- Metrics: `semipulse/metrics.py`
- Exports: `semipulse/exports.py`
- Plot helpers: `semipulse/plots.py`
- Sample data: `data/sample/`
- Tests: `tests/`
- Local run dependencies: `requirements.txt`
- Docker runtime: `Dockerfile`, `docker-compose.yml`

## Read First

1. Read `MasterPrompt.md` for the product requirements and execution order.
2. Read `TECHNICAL.md` for architecture, data contracts, table contracts, and QA expectations.
3. Execute prompts in `prompts/` sequentially.
4. After each prompt, run its verification commands and keep the baseline flow runnable.

## Planned Local Commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
python -m semipulse.sample_data
python -m semipulse.model
streamlit run app/streamlit_app.py
docker compose up --build
```

These commands become available as the relevant prompts create the underlying files.

Local note: this environment has `python3` available on `PATH`; after virtual environment activation, use the venv's `python`.

## Non-Negotiable Constraints

- The data is simulated.
- Model metrics are simulated-data performance only.
- Use SQLite for MVP persistence.
- Use scikit-learn for modeling.
- Do not download large AI models or call external LLMs for the ML pipeline.
- Keep heavy processing out of Streamlit page code.
