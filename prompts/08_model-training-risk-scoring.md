Status: NOT_STARTED

# 08 Model Training Risk Scoring

## Goal
Train a local scikit-learn predictive maintenance model on simulated features, generate machine risk scores, save model artifacts, and persist model run metadata and predictions in SQLite. Do not use external LLMs or download large AI models.

## Files to create/modify exact paths
- `semipulse/model.py`
- `semipulse/predict.py`
- `semipulse/metrics.py`
- `semipulse/features.py`
- `tests/test_model.py`
- `models/.gitkeep`
- `README.md`
- `START_HERE.md`
- `CURRENT_STATE.md`

## Steps
1. Implement `semipulse/metrics.py`:
   - Calculate recall, precision, F1, accuracy, ROC-AUC when possible, and confusion matrix.
   - Handle single-class edge cases without crashing.
2. Implement `semipulse/model.py`:
   - Read `machine_features` from SQLite.
   - Split train/test data with fixed random seed.
   - Use a scikit-learn pipeline with:
     - numeric feature passthrough or imputation.
     - categorical encoding via `OneHotEncoder`.
     - `RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")` or a configurable fixed-seed equivalent.
   - Train the model.
   - Evaluate metrics.
   - Save `models/risk_model.pkl` using `joblib`.
   - Save `models/model_metadata.json`.
   - Insert a row into `model_runs`.
3. Implement `semipulse/predict.py`:
   - Load saved model artifact.
   - Score `machine_features`.
   - Produce `risk_score`, `predicted_failure_flag`, `risk_level`, `model_run_id`, and `prediction_timestamp`.
   - Persist rows in `risk_predictions`.
4. Include risk levels:
   - `high` for scores >= 0.70.
   - `medium` for scores >= 0.40 and < 0.70.
   - `low` for scores < 0.40.
5. Add a CLI entrypoint:
   - `python -m semipulse.model` trains, saves artifacts, stores a model run, and writes predictions.
6. Ensure all metadata and docs state metrics are simulated-data performance only.
7. Add tests for:
   - Model trains on generated sample data.
   - Metrics keys exist.
   - Predictions include risk scores between 0 and 1.
   - Model artifacts are written.
   - `risk_predictions` and `model_runs` receive rows.

## API or Function Contract
- `train_model(db_path: Path | str | None = None, model_dir: Path | str | None = None, random_seed: int | None = None) -> dict`
- `load_model(model_path: Path | str | None = None) -> Any`
- `score_features(model: Any, features: pandas.DataFrame, model_run_id: str) -> pandas.DataFrame`
- `write_predictions(connection: sqlite3.Connection, predictions: pandas.DataFrame, if_exists: str = "replace") -> int`
- `calculate_classification_metrics(y_true, y_pred, y_proba=None) -> dict`

## Acceptance criteria
- `python -m semipulse.model` trains without network access.
- `models/risk_model.pkl` and `models/model_metadata.json` are created.
- `model_runs` stores metrics and simulated-data warning text.
- `risk_predictions` stores one prediction per machine feature row.
- Metrics include recall, precision, F1, accuracy, confusion matrix, and ROC-AUC when possible.
- Tests pass.

## Tests what to test and how to run
- Run:
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  python -m semipulse.sample_data
  python - <<'PY'
  from semipulse.data_loader import rebuild_database_from_csvs
  rebuild_database_from_csvs(reset=True)
  PY
  python -m semipulse.features
  python -m semipulse.model
  pytest tests/test_model.py
  ```
- Expected results:
  - Model artifacts are written under `models/`.
  - Predictions are written to SQLite.
  - Tests pass.

## Stop and verify commands and expected results
Run:
```bash
python - <<'PY'
from semipulse.database import get_connection, read_table
conn = get_connection()
print(read_table(conn, "model_runs", limit=5))
print(read_table(conn, "risk_predictions", limit=5))
conn.close()
PY
pytest
```

Expected results:
- `model_runs` shows at least one simulated-data model run.
- `risk_predictions` shows risk scores and risk levels.
- `pytest` passes.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

For this slice, smoke test the full non-UI flow: sample data generation, database rebuild, feature generation, model training, and risk prediction storage.
