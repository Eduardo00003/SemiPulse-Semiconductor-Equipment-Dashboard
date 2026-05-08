# MasterPrompt.md — SemiPulse Predictive Maintenance Dashboard MVP

## MANDATORY DIRECTIVE
You are an expert Python data engineer, machine learning engineer, and dashboard developer.

**CRITICAL**: Build SemiPulse by following this implementation guide in the exact order.

**CRITICAL**: Use prompts in the `/prompts` directory, create them if missing, and execute them sequentially.

**CRITICAL**: Keep the project runnable after every step. This is a portfolio project, so every feature must be clean, understandable, reproducible, and interview-ready.

---

## PROJECT SUMMARY
SemiPulse is a predictive maintenance analytics dashboard for simulated semiconductor manufacturing equipment.

The app shall:
- Generate or load simulated semiconductor equipment datasets.
- Ingest sensor, maintenance, defect, and machine metadata CSV files.
- Clean, validate, merge, and store data in SQLite.
- Generate predictive maintenance features with Pandas.
- Train or run a scikit-learn model to score near-term machine service risk.
- Display fleet health, downtime, defect trends, model performance, and ranked maintenance risk in Streamlit.
- Export risk rankings and processed data.

The project must support this resume framing:

> Built a Python-based predictive maintenance analytics application that ingested and merged sensor, maintenance, defect, and machine metadata into a unified SQLite pipeline, engineered Pandas/scikit-learn feature-generation and risk-scoring workflows, and designed a Streamlit dashboard for machine health, downtime, defect trends, and ranked maintenance risk.

---

## CORE MVP CONSTRAINTS DO NOT VIOLATE

### Prototype baseline preservation
- Keep the existing demo runnable at all times.
- Do not delete the working baseline flow:
  - load sample data,
  - build or load SQLite database,
  - generate features,
  - train or load model,
  - produce risk scores,
  - launch Streamlit dashboard.
- Maintain a frozen reference point: tag or branch `prototype-v0`.
- Development must be incremental. Every prompt must end with a runnable, working state.

### Simulated data honesty
- The project must clearly state that the semiconductor equipment data is simulated.
- Do not claim real-world factory accuracy.
- Any metric such as 84 percent recall must be described as performance on simulated datasets only.

### No large AI model required
- Do not download or depend on a large language model.
- The ML component must use scikit-learn.
- Recommended baseline model: `RandomForestClassifier` with `class_weight="balanced"` and fixed `random_state`.
- Optional alternate models: Logistic Regression or Gradient Boosting.
- Model artifacts may be saved locally in `models/` using `joblib`.

### Storage constraints
- Use SQLite for MVP persistence.
- Do not rely only on in-memory DataFrames for app state.
- Keep raw sample CSVs under `data/raw/` or `data/sample/`.
- Store processed tables and predictions in SQLite.
- Store trained model artifacts under `models/`.

### Dashboard constraints
- Use Streamlit for the app UI.
- Keep dashboard code separate from ETL, feature engineering, model training, and database code.
- Use Matplotlib or Streamlit-native charts.
- Do not create a complex backend unless explicitly required.

---

## RECOMMENDED STACK
- Language: Python 3.11+
- Data processing: Pandas, NumPy
- Machine learning: scikit-learn, joblib
- Dashboard: Streamlit
- Database: SQLite
- Charts: Matplotlib and Streamlit-native charts
- Testing: pytest
- Containerization: Docker and docker-compose
- Config: `.env` plus environment variables

---

## RECOMMENDED REPOSITORY STRUCTURE
```text
semipulse-predictive-maintenance-dashboard/
  app/
    streamlit_app.py
    pages/
      overview.py
      data_upload.py
      machine_health.py
      maintenance_risk.py
      defect_trends.py
      downtime_analysis.py
      model_performance.py
      data_explorer.py

  semipulse/
    __init__.py
    config.py
    database.py
    schema.py
    validation.py
    data_loader.py
    sample_data.py
    features.py
    model.py
    predict.py
    metrics.py
    exports.py
    plots.py
    logging_utils.py

  data/
    raw/
    processed/
    sample/

  db/
    semipulse.db
    schema.sql

  models/
    risk_model.pkl
    model_metadata.json

  tests/
    test_validation.py
    test_features.py
    test_model.py
    test_database.py

  prompts/
    01_project-freeze-and-docs.md
    02_repo-structure-and-config.md
    03_sample-data-generator.md
    04_sqlite-schema-pipeline.md
    05_data-validation.md
    06_data-cleaning-and-merging.md
    07_feature-engineering.md
    08_model-training-risk-scoring.md
    09_streamlit-overview.md
    10_data-upload-dashboard.md
    11_machine-health-dashboard.md
    12_maintenance-risk-dashboard.md
    13_defect-downtime-analysis.md
    14_model-performance-view.md
    15_data-explorer-exports.md
    16_docker-and-deployment.md
    17_docs-qa-polish.md

  README.md
  TECHNICAL.md
  START_HERE.md
  CURRENT_STATE.md
  requirements.txt
  Dockerfile
  docker-compose.yml
  .env.example
  .gitignore
```

---

## START HERE CODE NAVIGATION REQUIRED DOCS
Create and maintain these docs early.

### `START_HERE.md`
Must point to:
- Streamlit entrypoint: `app/streamlit_app.py`
- Dashboard pages: `app/pages/`
- Config: `semipulse/config.py`
- SQLite connection and schema helpers: `semipulse/database.py`, `semipulse/schema.py`
- Data validation: `semipulse/validation.py`
- Data loading and merging: `semipulse/data_loader.py`
- Sample data generator: `semipulse/sample_data.py`
- Feature generation: `semipulse/features.py`
- Model training: `semipulse/model.py`
- Prediction/risk scoring: `semipulse/predict.py`
- Metrics: `semipulse/metrics.py`
- Exports: `semipulse/exports.py`
- Plot helpers: `semipulse/plots.py`
- SQLite schema: `db/schema.sql`
- Sample data: `data/sample/`
- Tests: `tests/`
- Local run: `requirements.txt`, `Dockerfile`, `docker-compose.yml`
- Technical overview: `TECHNICAL.md`

### `CURRENT_STATE.md`
Must document:
- What works now.
- What is missing.
- Known issues and limitations.
- Current commands.
- Current dataset assumptions.
- Current model limitations.
- Whether sample data, SQLite, features, model, dashboard, and exports work.

Goal: A new developer can locate the app, pipeline, model, and dashboard code within 30 minutes.

---

## IMPLEMENTATION EXECUTION ORDER PROMPTS
**CRITICAL**: Execute prompts in this exact sequence.

All prompts live in `/prompts` and must be small, testable increments.

1. `01_project-freeze-and-docs.md`
   - Create `prototype-v0` tag or branch.
   - Add or refresh `README.md`, `START_HERE.md`, `CURRENT_STATE.md`, `.env.example`.
   - Confirm baseline demo still runs.

2. `02_repo-structure-and-config.md`
   - Create final folder structure.
   - Add `semipulse/config.py`.
   - Add environment variable support.
   - Add basic logging setup.

3. `03_sample-data-generator.md`
   - Generate simulated semiconductor equipment datasets.
   - Output machine metadata, sensor readings, maintenance records, and defect records.
   - Use fixed random seed for reproducibility.

4. `04_sqlite-schema-pipeline.md`
   - Add SQLite schema.
   - Create tables: machines, sensor_readings, maintenance_records, defect_records, machine_features, risk_predictions, model_runs, data_quality_issues, pipeline_runs.
   - Add database create/reset/load helpers.

5. `05_data-validation.md`
   - Validate uploaded or sample CSVs.
   - Enforce required columns.
   - Report missing columns, invalid timestamps, duplicates, orphan machine IDs, and numeric issues.

6. `06_data-cleaning-and-merging.md`
   - Clean datasets.
   - Standardize machine IDs, timestamps, categorical fields, and numeric fields.
   - Merge data into machine-level analytical tables.
   - Store cleaned data in SQLite.

7. `07_feature-engineering.md`
   - Generate machine-level features.
   - Include sensor, maintenance, defect, rolling-window, and metadata features.
   - Store `machine_features` in SQLite.

8. `08_model-training-risk-scoring.md`
   - Create failure target label.
   - Train scikit-learn baseline model.
   - Evaluate recall, precision, F1, accuracy, ROC-AUC when available, and confusion matrix.
   - Save model artifact and metadata.
   - Store predictions in `risk_predictions`.

9. `09_streamlit-overview.md`
   - Create Streamlit app shell.
   - Add sidebar navigation.
   - Add overview dashboard with fleet KPIs.

10. `10_data-upload-dashboard.md`
    - Add data upload/load page.
    - Upload or load sample CSVs.
    - Preview and validate datasets.
    - Trigger pipeline rebuild.

11. `11_machine-health-dashboard.md`
    - Add machine health visualizations.
    - Show sensor trends and machine detail view.

12. `12_maintenance-risk-dashboard.md`
    - Add ranked maintenance risk view.
    - Filter and sort machines.
    - Show high/medium/low risk categories and machine detail context.

13. `13_defect-downtime-analysis.md`
    - Add defect trends page.
    - Add downtime analysis page.
    - Connect defects/downtime to machine risk.

14. `14_model-performance-view.md`
    - Add model performance page.
    - Show metrics, confusion matrix, model run metadata, and recall explanation.

15. `15_data-explorer-exports.md`
    - Add Data Explorer.
    - Add CSV exports for risk ranking, features, model metrics, and selected table views.

16. `16_docker-and-deployment.md`
    - Add Dockerfile and docker-compose.
    - Make Streamlit port configurable.
    - Document optional deployment to Streamlit Community Cloud, Render, Railway, or Fly.io.

17. `17_docs-qa-polish.md`
    - Final README, TECHNICAL.md, START_HERE.md, CURRENT_STATE.md updates.
    - Add final QA checklist.
    - Confirm project is portfolio-ready.

---

## MANDATORY VERIFICATION BETWEEN STEPS
After every prompt:
1. Fix build/import/test errors before proceeding.
2. Run unit tests with `pytest`.
3. Run or smoke test the pipeline.
4. Launch Streamlit locally.
5. Confirm baseline flow still works:
   - load sample data,
   - build SQLite database,
   - generate features,
   - produce risk scores,
   - show dashboard.
6. If schema or function contracts changed, update docs and tests.

Recommended commands:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
python -m semipulse.sample_data
python -m semipulse.model
streamlit run app/streamlit_app.py
```

---

## REQUIRED DATASET CONTRACT

### Machine metadata required columns
- `machine_id`
- `machine_type`
- `manufacturer`
- `facility_area`
- `install_date`
- `status`

Optional columns:
- `model`
- `line_id`
- `process_step`
- `criticality`
- `last_service_date`
- `expected_lifetime_years`

### Sensor readings required columns
- `reading_id`
- `machine_id`
- `timestamp`
- `temperature`
- `vibration`
- `pressure`
- `power_draw`

Optional columns:
- `humidity`
- `cycle_count`
- `error_code`
- `runtime_hours`
- `chamber_pressure`
- `gas_flow_rate`

### Maintenance records required columns
- `maintenance_id`
- `machine_id`
- `maintenance_date`
- `maintenance_type`
- `downtime_hours`

Optional columns:
- `technician`
- `parts_replaced`
- `maintenance_cost`
- `notes`
- `severity`
- `resolved`

### Defect records required columns
- `defect_id`
- `machine_id`
- `timestamp`
- `defect_count`
- `batch_id`

Optional columns:
- `wafer_lot`
- `defect_type`
- `severity`
- `yield_loss_pct`
- `process_step`

---

## REQUIRED SQLITE TABLES
Minimum tables:
- `machines`
- `sensor_readings`
- `maintenance_records`
- `defect_records`
- `machine_features`
- `risk_predictions`
- `model_runs`
- `pipeline_runs`
- `data_quality_issues`

---

## FEATURE ENGINEERING CONTRACT
The system must generate a model-ready `machine_features` table.

Required feature groups:

### Sensor features
- average temperature
- max temperature
- temperature standard deviation
- average vibration
- max vibration
- vibration standard deviation
- average pressure
- pressure variance
- average power draw
- power draw variance

### Rolling-window features
- 7-day rolling average temperature
- 7-day rolling average vibration
- 7-day rolling defect count
- 30-day maintenance count
- recent downtime hours

### Maintenance features
- days since last maintenance
- total maintenance events
- total downtime hours
- average downtime per event
- emergency maintenance count
- maintenance frequency

### Defect features
- total defect count
- recent defect count
- average defects per batch
- defect severity score
- yield loss percentage if available

### Metadata features
- machine age
- machine type
- manufacturer
- criticality
- facility area

---

## MACHINE LEARNING CONTRACT
- Use scikit-learn.
- Do not use or download a large AI model.
- Define a binary target label: machine is high risk for maintenance/failure within a future prediction window.
- Default prediction window: 14 days, configurable.
- Recommended model: `RandomForestClassifier`.
- Use fixed random seed.
- Use train/test split.
- Calculate:
  - recall,
  - precision,
  - F1,
  - accuracy,
  - ROC-AUC when applicable,
  - confusion matrix.
- Store:
  - risk score,
  - predicted failure flag,
  - model run ID,
  - prediction timestamp.
- Save:
  - `models/risk_model.pkl`,
  - `models/model_metadata.json`.

Important honesty rule:
- Any reported recall, including 84 percent, must be labeled as simulated-data performance.

---

## REQUIRED DASHBOARD PAGES

### Overview
- Fleet KPIs.
- Dataset status.
- High-risk machine count.
- Latest model run.
- Latest pipeline run.

### Data Upload / Load
- Load sample data.
- Upload CSVs.
- Preview datasets.
- Validate schemas.
- Rebuild SQLite database.

### Machine Health
- Sensor trends.
- Machine filter.
- Machine detail panel.
- Fleet averages.

### Maintenance Risk
- Ranked machines by risk score.
- Filters by machine type, area, manufacturer, risk level.
- High/medium/low labels.
- Machine-level explanation fields.

### Defect Trends
- Defect counts over time.
- Defects by machine, type, area, process step, batch/lot if present.

### Downtime Analysis
- Downtime by machine.
- Downtime by maintenance type.
- Top downtime machines.
- Downtime versus risk.

### Model Performance
- Metrics.
- Confusion matrix.
- Recall explanation.
- Model metadata.

### Data Explorer
- View processed tables.
- Filter/search.
- Export selected table views.

---

## EXPORT CONTRACT
The app must support CSV exports for:
- ranked risk predictions,
- machine features,
- model metrics,
- selected database table views.

Export files must include clear headers and timestamps or model run IDs.

---

## CROSS-CUTTING REQUIREMENTS
- Use clear logging.
- Handle errors safely.
- Record data quality issues.
- Avoid hard-coded local paths.
- Use environment variables for database path, data path, model path, and log level.
- Keep data processing testable outside Streamlit.
- Keep the app portfolio-friendly and easy to demo.

---

## FINAL MANUAL QA CHECKLIST

### Setup
- `pip install -r requirements.txt` works.
- `.env.example` documents required variables.
- SQLite database can be created from scratch.
- Sample data can be regenerated.
- Docker build succeeds.

### Pipeline
- Sample data loads.
- Uploaded CSVs validate.
- Invalid CSVs show clear errors.
- SQLite tables are created.
- Data quality report is generated.

### Features
- Machine-level features are generated.
- Rolling-window features calculate correctly.
- Feature table is stored in SQLite.
- Feature tests pass.

### ML
- Model trains successfully.
- Risk scores are generated.
- Failure flags are generated.
- Metrics are displayed.
- Model artifact and metadata are saved.
- Results are reproducible with fixed seed.

### Dashboard
- Overview loads.
- Data Upload page works.
- Maintenance Risk ranks machines correctly.
- Machine Health shows sensor trends.
- Downtime page shows downtime patterns.
- Defect Trends page shows defect patterns.
- Model Performance page shows metrics.
- Data Explorer shows processed tables.

### Exports
- Risk ranking CSV downloads.
- Feature CSV downloads.
- Exported files have clear columns.

### Docs
- README is complete.
- TECHNICAL.md is complete.
- START_HERE.md is complete.
- CURRENT_STATE.md is complete.
- Simulated-data limitations are stated clearly.

---

## SUCCESS CRITERIA
SemiPulse MVP is complete when:
- All tests pass.
- The app runs locally through Streamlit.
- The app runs through Docker.
- The sample-data pipeline works end-to-end.
- SQLite stores cleaned data, features, model runs, predictions, and data quality issues.
- The dashboard shows fleet KPIs, machine health, downtime, defect trends, ranked risk, and model metrics.
- Exports work.
- Documentation is strong enough for GitHub and resume review.
- The project honestly presents its ML results as simulated-data results.

---
# END OF MASTER PROMPT
