Status: COMPLETED

# 16 Docker and Deployment

## Goal
Add Docker support and deployment documentation for running the SemiPulse Streamlit MVP reproducibly. Keep configuration environment-driven and do not bake local machine paths into the image.

## Files to create/modify exact paths
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
- `README.md`
- `TECHNICAL.md`
- `START_HERE.md`
- `CURRENT_STATE.md`

## Steps
1. Create `Dockerfile`:
   - Use a Python 3.11+ slim base image.
   - Set a working directory.
   - Install dependencies from `requirements.txt`.
   - Copy project files.
   - Expose Streamlit port `8501`.
   - Use a command equivalent to `streamlit run app/streamlit_app.py --server.address=0.0.0.0`.
2. Create `docker-compose.yml`:
   - Define a `semipulse` service.
   - Build from the local Dockerfile.
   - Map `${SEMIPULSE_STREAMLIT_PORT:-8501}:8501`.
   - Pass environment variables:
     - `SEMIPULSE_DB_PATH`
     - `SEMIPULSE_DATA_DIR`
     - `SEMIPULSE_MODEL_DIR`
     - `SEMIPULSE_LOG_LEVEL`
     - `SEMIPULSE_RANDOM_SEED`
     - `SEMIPULSE_PREDICTION_WINDOW_DAYS`
   - Mount or persist data/db/models only if appropriate for local development.
3. Create `.dockerignore`:
   - Ignore `.venv`, `__pycache__`, `.pytest_cache`, `.git`, local database files if regenerated, and local OS/editor files.
4. Ensure the app can initialize missing runtime directories inside the container.
5. Update docs:
   - Local Docker run command: `docker compose up --build`.
   - Optional deployment notes for Streamlit Community Cloud, Render, Railway, or Fly.io.
   - State that sample data can be generated from the UI or CLI.
6. Do not introduce any external LLM or large model dependency.

## Acceptance criteria
- Docker build succeeds.
- `docker compose up --build` starts Streamlit.
- The containerized app uses environment variables for paths and configuration.
- Documentation explains local and Docker execution.
- Tests pass outside Docker before build.

## Tests what to test and how to run
- Run:
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  pytest
  docker compose up --build
  ```
- Expected results:
  - Tests pass locally.
  - Docker image builds.
  - Streamlit starts and is reachable at `http://localhost:8501` unless `SEMIPULSE_STREAMLIT_PORT` is set.
  - Stop Docker with `Ctrl-C`.

## Stop and verify commands and expected results
Run:
```bash
docker compose config
docker compose up --build
```

Expected results:
- Compose config validates.
- App starts without import errors.
- The dashboard opens at the configured local port.

## Do not break existing behavior
After completing this prompt, confirm the original demo flow still works:
- load sample data
- build or open SQLite database
- generate features
- produce risk scores
- launch Streamlit dashboard

For this slice, smoke test the local Python flow first, then the Docker Streamlit launch.
