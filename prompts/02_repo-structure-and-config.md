Status: COMPLETED

# 02 Repo Structure and Config

## Goal
Create the final SemiPulse folder structure, Python package skeleton, dependency file, environment-variable configuration, and logging helpers. Keep this as a small infrastructure slice with no heavy data processing or dashboard logic yet.

## Files to create/modify exact paths
- `requirements.txt`
- `semipulse/__init__.py`
- `semipulse/config.py`
- `semipulse/logging_utils.py`
- `app/.gitkeep`
- `app/pages/.gitkeep`
- `data/raw/.gitkeep`
- `data/processed/.gitkeep`
- `data/sample/.gitkeep`
- `db/.gitkeep`
- `models/.gitkeep`
- `tests/.gitkeep`
- `README.md`
- `START_HERE.md`
- `CURRENT_STATE.md`

## Steps
1. Create these directories if missing:
   - `app/`
   - `app/pages/`
   - `semipulse/`
   - `data/raw/`
   - `data/processed/`
   - `data/sample/`
   - `db/`
   - `models/`
   - `tests/`
2. Add `requirements.txt` with the MVP dependencies:
   - `pandas`
   - `numpy`
   - `scikit-learn`
   - `streamlit`
   - `matplotlib`
   - `joblib`
   - `pytest`
   - `python-dotenv`
3. Add `semipulse/__init__.py` with a small package docstring and `__version__`.
4. Implement `semipulse/config.py`:
   - Define a `Settings` dataclass.
   - Load `.env` using `python-dotenv` when available.
   - Read environment variables:
     - `SEMIPULSE_DB_PATH`
     - `SEMIPULSE_DATA_DIR`
     - `SEMIPULSE_MODEL_DIR`
     - `SEMIPULSE_LOG_LEVEL`
     - `SEMIPULSE_RANDOM_SEED`
     - `SEMIPULSE_PREDICTION_WINDOW_DAYS`
   - Provide defaults matching `.env.example`.
   - Convert numeric values to `int`.
   - Expose `get_settings()`.
   - Include `ensure_runtime_dirs(settings=None)` to create parent/runtime directories.
5. Implement `semipulse/logging_utils.py`:
   - Provide `configure_logging(level: str | None = None) -> None`.
   - Use standard library `logging`.
   - Respect `SEMIPULSE_LOG_LEVEL`.
6. Update docs:
   - `START_HERE.md` should mark `semipulse/config.py` and `semipulse/logging_utils.py` as implemented.
   - `CURRENT_STATE.md` should state that structure and config exist, but sample data, database, features, model, dashboard, and exports are not complete yet.

## API or Function Contract
- `semipulse.config.Settings`
  - Fields:
    - `db_path: Path`
    - `data_dir: Path`
    - `model_dir: Path`
    - `log_level: str`
    - `random_seed: int`
    - `prediction_window_days: int`
- `semipulse.config.get_settings() -> Settings`
- `semipulse.config.ensure_runtime_dirs(settings: Settings | None = None) -> None`
- `semipulse.logging_utils.configure_logging(level: str | None = None) -> None`

## Acceptance criteria
- All recommended top-level directories exist.
- `requirements.txt` installs the planned MVP stack.
- `get_settings()` returns sane defaults without requiring a local `.env`.
- Runtime paths are configurable through environment variables.
- Importing `semipulse` and `semipulse.config` works.
- Docs reflect the current implementation state honestly.

## Tests what to test and how to run
- Run:
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  python - <<'PY'
  from semipulse.config import get_settings, ensure_runtime_dirs
  settings = get_settings()
  ensure_runtime_dirs(settings)
  print(settings)
  PY
  pytest
  ```
- Expected results:
  - Dependencies install.
  - The config import script prints a `Settings` instance.
  - Runtime directories exist.
  - `pytest` runs. It may report no tests collected at this stage, but it must not fail due to import errors.

## Stop and verify commands and expected results
Run:
```bash
find app semipulse data db models tests -maxdepth 2 -type d | sort
python -c "from semipulse.config import get_settings; print(get_settings().db_path)"
```

Expected results:
- The final project directories are listed.
- The config command prints `db/semipulse.db` or the value configured by environment variables.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

If the baseline flow is not implemented yet, keep the project importable and document the missing pieces in `CURRENT_STATE.md`.
