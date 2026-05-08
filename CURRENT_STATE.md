# Current State

Last updated: 2026-05-08

## What Works Now

- Project requirements exist in `MasterPrompt.md`.
- Technical guidance exists in `TECHNICAL.md`.
- The full 17-file implementation prompt sequence exists in `prompts/`.
- Prompt 01 documentation files have been added.

## What Is Missing

- Python package structure under `semipulse/`.
- Streamlit app under `app/`.
- Dependency file `requirements.txt`.
- Sample data generator.
- SQLite schema and database helpers.
- Validation and cleaning pipeline.
- Feature engineering pipeline.
- scikit-learn model training and risk scoring.
- Dashboard pages.
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
```

Planned commands after later prompts:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
python -m semipulse.sample_data
python -m semipulse.features
python -m semipulse.model
streamlit run app/streamlit_app.py
docker compose up --build
```

## Current Dataset Assumptions

- All future data will be simulated semiconductor manufacturing equipment data.
- Required source datasets will be:
  - `machines.csv`
  - `sensor_readings.csv`
  - `maintenance_records.csv`
  - `defect_records.csv`
- No generated CSV files exist yet.

## Current Model Limitations

- No model has been implemented yet.
- Future model metrics must be labeled as simulated-data performance only.
- The project must use local scikit-learn modeling, not external LLMs or large downloaded AI models.

## Capability Status

| Capability | Status |
| --- | --- |
| Sample data | Not implemented |
| SQLite database | Not implemented |
| Data validation | Not implemented |
| Data cleaning and merging | Not implemented |
| Feature engineering | Not implemented |
| Model training | Not implemented |
| Risk scoring | Not implemented |
| Streamlit dashboard | Not implemented |
| Exports | Not implemented |
| Docker | Not implemented |

## Baseline Freeze

The repository did not have Git initialized before prompt 01. Prompt 01 initialized Git, created the first baseline commit, and tagged the baseline as `prototype-v0`.
