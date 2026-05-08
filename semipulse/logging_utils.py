"""Logging helpers for SemiPulse."""

from __future__ import annotations

import logging

from semipulse.config import get_settings


def configure_logging(level: str | None = None) -> None:
    """Configure standard-library logging for CLI and app entrypoints."""

    log_level = (level or get_settings().log_level).upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
