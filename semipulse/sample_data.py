"""Generate reproducible simulated semiconductor equipment data."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from semipulse.config import ensure_runtime_dirs, get_settings
from semipulse.logging_utils import configure_logging

DATASET_FILENAMES = {
    "machines": "machines.csv",
    "sensor_readings": "sensor_readings.csv",
    "maintenance_records": "maintenance_records.csv",
    "defect_records": "defect_records.csv",
}

SIMULATION_START = pd.Timestamp("2025-01-01")


def _rng(random_seed: int | None = None) -> np.random.Generator:
    seed = get_settings().random_seed if random_seed is None else random_seed
    return np.random.default_rng(seed)


def generate_machines(
    num_machines: int = 50,
    random_seed: int | None = None,
    start_date: pd.Timestamp = SIMULATION_START,
) -> pd.DataFrame:
    """Generate simulated machine metadata."""

    rng = _rng(random_seed)
    machine_types = np.array(["Etcher", "Lithography", "CMP", "Deposition", "Inspection"])
    manufacturers = np.array(["Nikon", "TEL", "Applied Materials", "Lam Research", "KLA"])
    areas = np.array(["Fab A", "Fab B", "Cleanroom North", "Cleanroom South"])
    statuses = np.array(["active", "active", "active", "maintenance", "standby"])
    process_steps = np.array(["etch", "lithography", "planarization", "deposition", "inspection"])
    criticality = np.array(["low", "medium", "high"])

    rows: list[dict[str, object]] = []
    for idx in range(num_machines):
        install_age_days = int(rng.integers(240, 2500))
        machine_type = str(rng.choice(machine_types))
        rows.append(
            {
                "machine_id": f"M-{idx + 1:04d}",
                "machine_type": machine_type,
                "manufacturer": str(rng.choice(manufacturers)),
                "facility_area": str(rng.choice(areas)),
                "install_date": (start_date - pd.Timedelta(days=install_age_days)).date().isoformat(),
                "status": str(rng.choice(statuses)),
                "model": f"{machine_type[:3].upper()}-{int(rng.integers(100, 999))}",
                "line_id": f"L{int(rng.integers(1, 7))}",
                "process_step": str(rng.choice(process_steps)),
                "criticality": str(rng.choice(criticality, p=[0.25, 0.45, 0.30])),
                "last_service_date": (
                    start_date - pd.Timedelta(days=int(rng.integers(5, 120)))
                ).date().isoformat(),
                "expected_lifetime_years": int(rng.integers(6, 14)),
            }
        )

    return pd.DataFrame(rows)


def _build_event_plan(
    machines: pd.DataFrame,
    days: int,
    random_seed: int | None = None,
    start_date: pd.Timestamp = SIMULATION_START,
) -> pd.DataFrame:
    rng = _rng(random_seed)
    rows: list[dict[str, object]] = []

    for _, machine in machines.iterrows():
        criticality = str(machine.get("criticality", "medium"))
        high_risk_probability = {"low": 0.20, "medium": 0.35, "high": 0.55}.get(criticality, 0.35)
        has_degradation = bool(rng.random() < high_risk_probability)
        event_day = int(rng.integers(max(20, days // 3), max(21, days - 7))) if has_degradation else None

        rows.append(
            {
                "machine_id": machine["machine_id"],
                "has_degradation": has_degradation,
                "event_day": event_day,
                "event_date": (
                    start_date + pd.Timedelta(days=event_day)
                ).normalize()
                if event_day is not None
                else pd.NaT,
                "severity": str(rng.choice(["low", "medium", "high"], p=[0.25, 0.45, 0.30])),
            }
        )

    return pd.DataFrame(rows)


def generate_sensor_readings(
    machines: pd.DataFrame,
    days: int = 120,
    random_seed: int | None = None,
    event_plan: pd.DataFrame | None = None,
    start_date: pd.Timestamp = SIMULATION_START,
) -> pd.DataFrame:
    """Generate simulated machine sensor readings with degradation patterns."""

    rng = _rng(random_seed)
    events = (
        event_plan.set_index("machine_id").to_dict("index")
        if event_plan is not None and not event_plan.empty
        else _build_event_plan(machines, days, random_seed, start_date).set_index("machine_id").to_dict("index")
    )
    rows: list[dict[str, object]] = []
    reading_id = 1

    type_temperature_offset = {
        "Etcher": 5.0,
        "Lithography": -2.0,
        "CMP": 0.0,
        "Deposition": 4.0,
        "Inspection": -4.0,
    }

    for _, machine in machines.iterrows():
        machine_id = machine["machine_id"]
        machine_type = str(machine["machine_type"])
        event = events.get(machine_id, {})
        event_day = event.get("event_day")
        has_degradation = bool(event.get("has_degradation", False))
        base_temp = 66 + type_temperature_offset.get(machine_type, 0.0) + rng.normal(0, 1.2)
        base_vibration = 0.38 + rng.normal(0, 0.04)
        base_pressure = 101 + rng.normal(0, 2)
        base_power = 18 + rng.normal(0, 2)

        for day in range(days):
            timestamp = start_date + pd.Timedelta(days=day)
            degradation_factor = 0.0
            if has_degradation and event_day is not None:
                days_to_event = event_day - day
                if 0 <= days_to_event <= 21:
                    degradation_factor = (21 - days_to_event) / 21
                elif day > event_day:
                    degradation_factor = 0.25

            rows.append(
                {
                    "reading_id": f"R-{reading_id:07d}",
                    "machine_id": machine_id,
                    "timestamp": timestamp.isoformat(),
                    "temperature": round(base_temp + rng.normal(0, 1.8) + degradation_factor * 12, 3),
                    "vibration": round(max(0.05, base_vibration + rng.normal(0, 0.04) + degradation_factor * 0.45), 4),
                    "pressure": round(base_pressure + rng.normal(0, 2.5) - degradation_factor * 4, 3),
                    "power_draw": round(base_power + rng.normal(0, 1.6) + degradation_factor * 5, 3),
                    "humidity": round(float(rng.uniform(35, 48)), 2),
                    "cycle_count": int(day * rng.integers(70, 130)),
                    "runtime_hours": round(float(rng.uniform(12, 24)), 2),
                    "chamber_pressure": round(base_pressure / 10 + rng.normal(0, 0.3), 3),
                    "gas_flow_rate": round(float(rng.uniform(80, 130)), 3),
                    "error_code": "E-DEGRADE" if degradation_factor > 0.75 and rng.random() < 0.18 else "",
                }
            )
            reading_id += 1

    return pd.DataFrame(rows)


def generate_maintenance_records(
    machines: pd.DataFrame,
    days: int = 120,
    random_seed: int | None = None,
    event_plan: pd.DataFrame | None = None,
    start_date: pd.Timestamp = SIMULATION_START,
) -> pd.DataFrame:
    """Generate simulated maintenance events and downtime."""

    rng = _rng(random_seed)
    events = event_plan if event_plan is not None else _build_event_plan(machines, days, random_seed, start_date)
    events_by_machine = events.set_index("machine_id").to_dict("index")
    rows: list[dict[str, object]] = []
    maintenance_id = 1

    for _, machine in machines.iterrows():
        machine_id = machine["machine_id"]
        scheduled_interval = int(rng.integers(28, 55))
        first_service = int(rng.integers(10, 28))
        for service_day in range(first_service, days, scheduled_interval):
            rows.append(
                {
                    "maintenance_id": f"MT-{maintenance_id:06d}",
                    "machine_id": machine_id,
                    "maintenance_date": (start_date + pd.Timedelta(days=service_day)).date().isoformat(),
                    "maintenance_type": "scheduled",
                    "downtime_hours": round(float(rng.uniform(1.0, 5.0)), 2),
                    "technician": f"Tech-{int(rng.integers(1, 12)):02d}",
                    "parts_replaced": str(rng.choice(["filter", "seal", "sensor", "none"], p=[0.30, 0.20, 0.20, 0.30])),
                    "maintenance_cost": round(float(rng.uniform(500, 4000)), 2),
                    "severity": "low",
                    "resolved": True,
                }
            )
            maintenance_id += 1

        event = events_by_machine.get(machine_id, {})
        if bool(event.get("has_degradation", False)) and pd.notna(event.get("event_date")):
            downtime = float(rng.uniform(6, 24))
            severity = str(event.get("severity", "high"))
            rows.append(
                {
                    "maintenance_id": f"MT-{maintenance_id:06d}",
                    "machine_id": machine_id,
                    "maintenance_date": pd.Timestamp(event["event_date"]).date().isoformat(),
                    "maintenance_type": "emergency",
                    "downtime_hours": round(downtime, 2),
                    "technician": f"Tech-{int(rng.integers(1, 12)):02d}",
                    "parts_replaced": str(rng.choice(["pump", "bearing", "controller", "chamber kit"])),
                    "maintenance_cost": round(downtime * float(rng.uniform(900, 1800)), 2),
                    "severity": severity,
                    "resolved": True,
                }
            )
            maintenance_id += 1

    return pd.DataFrame(rows)


def generate_defect_records(
    machines: pd.DataFrame,
    days: int = 120,
    random_seed: int | None = None,
    event_plan: pd.DataFrame | None = None,
    start_date: pd.Timestamp = SIMULATION_START,
) -> pd.DataFrame:
    """Generate simulated production defect records."""

    rng = _rng(random_seed)
    events = (
        event_plan.set_index("machine_id").to_dict("index")
        if event_plan is not None and not event_plan.empty
        else _build_event_plan(machines, days, random_seed, start_date).set_index("machine_id").to_dict("index")
    )
    defect_types = np.array(["particle", "alignment", "etch_depth", "film_uniformity", "scratch"])
    rows: list[dict[str, object]] = []
    defect_id = 1

    for _, machine in machines.iterrows():
        machine_id = machine["machine_id"]
        event = events.get(machine_id, {})
        event_day = event.get("event_day")
        has_degradation = bool(event.get("has_degradation", False))

        for day in range(0, days, 3):
            degradation_factor = 0.0
            if has_degradation and event_day is not None:
                days_to_event = event_day - day
                if 0 <= days_to_event <= 21:
                    degradation_factor = (21 - days_to_event) / 21
                elif day > event_day:
                    degradation_factor = 0.20

            defect_count = int(rng.poisson(1.4 + degradation_factor * 7))
            severity = "high" if defect_count >= 7 else "medium" if defect_count >= 3 else "low"
            rows.append(
                {
                    "defect_id": f"D-{defect_id:07d}",
                    "machine_id": machine_id,
                    "timestamp": (start_date + pd.Timedelta(days=day)).isoformat(),
                    "defect_count": defect_count,
                    "batch_id": f"B-{day:03d}-{machine_id}",
                    "wafer_lot": f"WL-{int(rng.integers(1000, 9999))}",
                    "defect_type": str(rng.choice(defect_types)),
                    "severity": severity,
                    "yield_loss_pct": round(float(min(35, defect_count * rng.uniform(0.25, 0.9))), 3),
                    "process_step": str(machine.get("process_step", "")),
                }
            )
            defect_id += 1

    return pd.DataFrame(rows)


def generate_sample_data(
    output_dir: Path | str | None = None,
    random_seed: int | None = None,
    num_machines: int = 50,
    days: int = 120,
) -> dict[str, Path]:
    """Write all simulated sample CSV files and return their paths."""

    settings = get_settings()
    ensure_runtime_dirs(settings)
    resolved_output = Path(output_dir) if output_dir is not None else settings.data_dir
    resolved_output.mkdir(parents=True, exist_ok=True)
    seed = settings.random_seed if random_seed is None else random_seed

    machines = generate_machines(num_machines=num_machines, random_seed=seed)
    event_plan = _build_event_plan(machines, days=days, random_seed=seed + 1)
    datasets = {
        "machines": machines,
        "sensor_readings": generate_sensor_readings(
            machines,
            days=days,
            random_seed=seed + 2,
            event_plan=event_plan,
        ),
        "maintenance_records": generate_maintenance_records(
            machines,
            days=days,
            random_seed=seed + 3,
            event_plan=event_plan,
        ),
        "defect_records": generate_defect_records(
            machines,
            days=days,
            random_seed=seed + 4,
            event_plan=event_plan,
        ),
    }

    paths: dict[str, Path] = {}
    for name, dataframe in datasets.items():
        path = resolved_output / DATASET_FILENAMES[name]
        dataframe.to_csv(path, index=False)
        paths[name] = path

    return paths


def main() -> None:
    configure_logging()
    paths = generate_sample_data()
    print("Generated simulated sample data:")
    for name, path in paths.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
