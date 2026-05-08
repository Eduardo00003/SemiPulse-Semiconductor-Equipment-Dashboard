"""Runtime configuration for SemiPulse."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    db_path: Path
    data_dir: Path
    model_dir: Path
    log_level: str
    random_seed: int
    prediction_window_days: int


def _as_int(value: str | None, default: int) -> int:
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Expected integer environment value, got {value!r}") from exc


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings loaded from `.env` and process environment."""

    load_dotenv()

    return Settings(
        db_path=Path(os.getenv("SEMIPULSE_DB_PATH", "db/semipulse.db")),
        data_dir=Path(os.getenv("SEMIPULSE_DATA_DIR", "data/sample")),
        model_dir=Path(os.getenv("SEMIPULSE_MODEL_DIR", "models")),
        log_level=os.getenv("SEMIPULSE_LOG_LEVEL", "INFO").upper(),
        random_seed=_as_int(os.getenv("SEMIPULSE_RANDOM_SEED"), 42),
        prediction_window_days=_as_int(
            os.getenv("SEMIPULSE_PREDICTION_WINDOW_DAYS"),
            14,
        ),
    )


def ensure_runtime_dirs(settings: Settings | None = None) -> None:
    """Create runtime directories needed by the local MVP."""

    resolved = settings or get_settings()
    resolved.db_path.parent.mkdir(parents=True, exist_ok=True)
    resolved.data_dir.mkdir(parents=True, exist_ok=True)
    resolved.model_dir.mkdir(parents=True, exist_ok=True)
