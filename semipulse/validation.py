"""Data validation for SemiPulse CSV and DataFrame inputs."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

import pandas as pd


REQUIRED_COLUMNS: dict[str, set[str]] = {
    "machines": {
        "machine_id",
        "machine_type",
        "manufacturer",
        "facility_area",
        "install_date",
        "status",
    },
    "sensor_readings": {
        "reading_id",
        "machine_id",
        "timestamp",
        "temperature",
        "vibration",
        "pressure",
        "power_draw",
    },
    "maintenance_records": {
        "maintenance_id",
        "machine_id",
        "maintenance_date",
        "maintenance_type",
        "downtime_hours",
    },
    "defect_records": {
        "defect_id",
        "machine_id",
        "timestamp",
        "defect_count",
        "batch_id",
    },
}

ID_COLUMNS = {
    "machines": "machine_id",
    "sensor_readings": "reading_id",
    "maintenance_records": "maintenance_id",
    "defect_records": "defect_id",
}

TIMESTAMP_COLUMNS = {
    "machines": ["install_date"],
    "sensor_readings": ["timestamp"],
    "maintenance_records": ["maintenance_date"],
    "defect_records": ["timestamp"],
}

NUMERIC_COLUMNS = {
    "sensor_readings": ["temperature", "vibration", "pressure", "power_draw"],
    "maintenance_records": ["downtime_hours", "maintenance_cost"],
    "defect_records": ["defect_count", "yield_loss_pct"],
}


@dataclass(frozen=True)
class ValidationIssue:
    dataset: str
    severity: str
    issue_type: str
    message: str
    row_count: int | None = None
    column: str | None = None


@dataclass(frozen=True)
class ValidationResult:
    issues: list[ValidationIssue]

    @property
    def is_valid(self) -> bool:
        return not self.errors

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def infos(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "info"]

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "dataset": issue.dataset,
                    "severity": issue.severity,
                    "issue_type": issue.issue_type,
                    "message": issue.message,
                    "row_count": issue.row_count,
                    "column": issue.column,
                }
                for issue in self.issues
            ],
            columns=["dataset", "severity", "issue_type", "message", "row_count", "column"],
        )


def _issue(
    dataset: str,
    severity: str,
    issue_type: str,
    message: str,
    row_count: int | None = None,
    column: str | None = None,
) -> ValidationIssue:
    return ValidationIssue(dataset, severity, issue_type, message, row_count, column)


def _missing_required_columns(name: str, dataframe: pd.DataFrame) -> list[ValidationIssue]:
    required = REQUIRED_COLUMNS.get(name)
    if required is None:
        return [_issue(name, "error", "unknown_dataset", f"Unknown dataset {name!r}")]
    missing = sorted(required.difference(dataframe.columns))
    if not missing:
        return []
    return [
        _issue(
            name,
            "error",
            "missing_required_columns",
            f"Missing required columns: {', '.join(missing)}",
            row_count=len(dataframe),
        )
    ]


def _duplicate_ids(name: str, dataframe: pd.DataFrame) -> list[ValidationIssue]:
    id_column = ID_COLUMNS.get(name)
    if id_column is None or id_column not in dataframe.columns:
        return []
    duplicate_count = int(dataframe[id_column].duplicated().sum())
    if duplicate_count == 0:
        return []
    return [
        _issue(
            name,
            "error",
            "duplicate_ids",
            f"Found {duplicate_count} duplicate values in {id_column}",
            duplicate_count,
            id_column,
        )
    ]


def _missing_required_values(name: str, dataframe: pd.DataFrame) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for column in sorted(REQUIRED_COLUMNS.get(name, set()).intersection(dataframe.columns)):
        missing = int(dataframe[column].isna().sum())
        if missing:
            issues.append(
                _issue(
                    name,
                    "error",
                    "missing_required_values",
                    f"Column {column} has {missing} missing required values",
                    missing,
                    column,
                )
            )
    return issues


def _timestamp_issues(name: str, dataframe: pd.DataFrame) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for column in TIMESTAMP_COLUMNS.get(name, []):
        if column not in dataframe.columns:
            continue
        parsed = pd.to_datetime(dataframe[column], errors="coerce", format="mixed")
        invalid = int(parsed.isna().sum() - dataframe[column].isna().sum())
        if invalid:
            issues.append(
                _issue(
                    name,
                    "error",
                    "invalid_timestamps",
                    f"Column {column} has {invalid} invalid timestamp/date values",
                    invalid,
                    column,
                )
            )
    return issues


def _numeric_issues(name: str, dataframe: pd.DataFrame) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for column in NUMERIC_COLUMNS.get(name, []):
        if column not in dataframe.columns:
            continue
        parsed = pd.to_numeric(dataframe[column], errors="coerce")
        invalid = int(parsed.isna().sum() - dataframe[column].isna().sum())
        if invalid:
            issues.append(
                _issue(
                    name,
                    "error",
                    "invalid_numeric_values",
                    f"Column {column} has {invalid} values that cannot be parsed as numbers",
                    invalid,
                    column,
                )
            )
        if column in {"temperature", "vibration", "pressure", "power_draw", "downtime_hours", "defect_count"}:
            negative = int((parsed < 0).sum())
            if negative:
                issues.append(
                    _issue(
                        name,
                        "error",
                        "negative_numeric_values",
                        f"Column {column} has {negative} negative values",
                        negative,
                        column,
                    )
                )
        if column == "yield_loss_pct":
            outside = int(((parsed < 0) | (parsed > 100)).sum())
            if outside:
                issues.append(
                    _issue(
                        name,
                        "warning",
                        "yield_loss_out_of_range",
                        f"Column {column} has {outside} values outside 0-100",
                        outside,
                        column,
                    )
                )
    return issues


def _orphan_machine_ids(
    name: str,
    dataframe: pd.DataFrame,
    machines: pd.DataFrame | None,
) -> list[ValidationIssue]:
    if name == "machines" or machines is None or "machine_id" not in dataframe.columns or "machine_id" not in machines.columns:
        return []
    machine_ids = set(machines["machine_id"].dropna().astype(str))
    references = dataframe["machine_id"].dropna().astype(str)
    orphan_count = int((~references.isin(machine_ids)).sum())
    if orphan_count == 0:
        return []
    return [
        _issue(
            name,
            "error",
            "orphan_machine_ids",
            f"Found {orphan_count} rows referencing unknown machine_id values",
            orphan_count,
            "machine_id",
        )
    ]


def validate_dataset(
    name: str,
    dataframe: pd.DataFrame,
    machines: pd.DataFrame | None = None,
) -> ValidationResult:
    """Validate one named dataset and return structured issues."""

    issues: list[ValidationIssue] = []
    issues.extend(_missing_required_columns(name, dataframe))
    issues.extend(_missing_required_values(name, dataframe))
    issues.extend(_duplicate_ids(name, dataframe))
    issues.extend(_timestamp_issues(name, dataframe))
    issues.extend(_numeric_issues(name, dataframe))
    issues.extend(_orphan_machine_ids(name, dataframe, machines))

    if not issues:
        issues.append(_issue(name, "info", "validation_passed", "Dataset passed validation", len(dataframe)))

    return ValidationResult(issues)


def validate_all_datasets(datasets: dict[str, pd.DataFrame]) -> ValidationResult:
    """Validate all core SemiPulse datasets together."""

    machines = datasets.get("machines")
    issues: list[ValidationIssue] = []

    for name in REQUIRED_COLUMNS:
        dataframe = datasets.get(name)
        if dataframe is None:
            issues.append(
                _issue(name, "error", "missing_dataset", f"Missing required dataset {name!r}")
            )
            continue
        issues.extend(validate_dataset(name, dataframe, machines=machines).issues)

    return ValidationResult(issues)


def persist_validation_issues(
    connection: sqlite3.Connection,
    issues: list[ValidationIssue],
    pipeline_run_id: str | None = None,
) -> int:
    """Persist validation issues into the SQLite data_quality_issues table."""

    rows = [
        (
            pipeline_run_id,
            issue.dataset,
            issue.severity,
            issue.issue_type,
            issue.message,
            issue.row_count,
            issue.column,
        )
        for issue in issues
        if issue.severity != "info"
    ]
    if not rows:
        return 0

    connection.executemany(
        """
        INSERT INTO data_quality_issues (
            pipeline_run_id, dataset, severity, issue_type, message, row_count, column_name
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    connection.commit()
    return len(rows)
