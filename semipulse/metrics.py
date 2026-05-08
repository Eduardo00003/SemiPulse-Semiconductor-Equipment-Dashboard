"""Model metrics and metadata helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from semipulse.config import get_settings


def calculate_classification_metrics(y_true, y_pred, y_proba=None) -> dict[str, Any]:
    """Calculate robust binary classification metrics."""

    metrics: dict[str, Any] = {
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist(),
        "roc_auc": None,
    }
    if y_proba is not None and len(set(y_true)) > 1:
        try:
            metrics["roc_auc"] = float(roc_auc_score(y_true, y_proba))
        except ValueError:
            metrics["roc_auc"] = None
    return metrics


def load_latest_model_metadata(model_dir: Path | str | None = None) -> dict[str, Any]:
    """Load the latest local model metadata JSON."""

    resolved_dir = Path(model_dir) if model_dir is not None else get_settings().model_dir
    path = resolved_dir / "model_metadata.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
