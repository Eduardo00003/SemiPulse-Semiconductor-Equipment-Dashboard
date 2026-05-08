Status: NOT_STARTED

# 14 Model Performance View

## Goal
Add a Model Performance dashboard page that displays simulated-data model metrics, confusion matrix, model metadata, and a recall-focused explanation suitable for predictive maintenance.

## Files to create/modify exact paths
- `app/pages/model_performance.py`
- `app/streamlit_app.py`
- `semipulse/metrics.py`
- `semipulse/plots.py`
- `README.md`
- `START_HERE.md`
- `CURRENT_STATE.md`

## Steps
1. Create `app/pages/model_performance.py` with `render()`.
2. Read from SQLite and model metadata:
   - `model_runs`
   - `risk_predictions`
   - `models/model_metadata.json`
3. Display latest model run metadata:
   - Model type.
   - Model run ID.
   - Training timestamp.
   - Prediction window.
   - Random seed.
   - Feature columns.
   - Simulated-data warning.
4. Display metrics:
   - Recall.
   - Precision.
   - F1.
   - Accuracy.
   - ROC-AUC when available.
5. Display confusion matrix:
   - Use values stored in `model_runs` or metadata.
   - Add a clear table or chart.
6. Add recall explanation:
   - Explain that recall measures how many true high-risk machines were caught.
   - State that recall is important for maintenance prioritization.
   - State that all metrics are simulated-data performance only.
7. Add model run selector if multiple runs exist.
8. Add a rerun training button that calls the pipeline/model functions.
9. Update docs.

## API or Function Contract
- `app.pages.model_performance.render() -> None`
- `semipulse.metrics.load_latest_model_metadata(model_dir: Path | str | None = None) -> dict`
- `semipulse.plots.prepare_confusion_matrix(metrics: dict) -> pandas.DataFrame`

## Acceptance criteria
- Model Performance page renders from sidebar.
- Latest model metrics display correctly.
- Confusion matrix is visible when available.
- Simulated-data limitation is visible next to metrics.
- Rerun training works if sample data/features exist.
- Missing metadata is handled with setup instructions.
- Tests pass.

## Tests what to test and how to run
- Run:
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  python - <<'PY'
  from semipulse.pipeline import run_demo_pipeline
  print(run_demo_pipeline(generate_data=True, reset_database=True, train_model=True))
  PY
  pytest
  streamlit run app/streamlit_app.py
  ```
- Expected results:
  - Pipeline creates model run metadata.
  - Tests pass.
  - Model Performance page displays metrics and confusion matrix.

## Stop and verify commands and expected results
Run:
```bash
python - <<'PY'
import json
from pathlib import Path
path = Path("models/model_metadata.json")
print(path.exists())
if path.exists():
    data = json.loads(path.read_text())
    print(data.get("metrics", {}).keys())
    print(data.get("simulated_data_warning"))
PY
pytest
streamlit run app/streamlit_app.py
```

Expected results:
- Metadata file exists after a pipeline run.
- Metrics keys are printed.
- Simulated-data warning is present.
- Tests pass and Streamlit page works.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

For this slice, smoke test the full pipeline and manually open the Model Performance page.
