from pathlib import Path

import pandas as pd

from semipulse.sample_data import generate_sample_data


REQUIRED_COLUMNS = {
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


def _load(paths: dict[str, Path]) -> dict[str, pd.DataFrame]:
    return {name: pd.read_csv(path) for name, path in paths.items()}


def test_generate_sample_data_writes_required_files(tmp_path: Path) -> None:
    paths = generate_sample_data(tmp_path, random_seed=42, num_machines=8, days=20)

    assert set(paths) == set(REQUIRED_COLUMNS)
    for path in paths.values():
        assert path.exists()

    datasets = _load(paths)
    for name, required in REQUIRED_COLUMNS.items():
        assert required.issubset(datasets[name].columns)
        assert not datasets[name].empty


def test_generate_sample_data_is_reproducible(tmp_path: Path) -> None:
    first = _load(generate_sample_data(tmp_path / "first", random_seed=7, num_machines=5, days=12))
    second = _load(generate_sample_data(tmp_path / "second", random_seed=7, num_machines=5, days=12))

    for name in REQUIRED_COLUMNS:
        pd.testing.assert_frame_equal(first[name], second[name])


def test_generated_foreign_keys_reference_machines(tmp_path: Path) -> None:
    datasets = _load(generate_sample_data(tmp_path, random_seed=13, num_machines=10, days=25))
    machine_ids = set(datasets["machines"]["machine_id"])

    for name in ["sensor_readings", "maintenance_records", "defect_records"]:
        assert set(datasets[name]["machine_id"]).issubset(machine_ids)


def test_degradation_patterns_exist_in_simulated_data(tmp_path: Path) -> None:
    datasets = _load(generate_sample_data(tmp_path, random_seed=21, num_machines=25, days=90))
    sensors = datasets["sensor_readings"]
    defects = datasets["defect_records"]
    maintenance = datasets["maintenance_records"]

    assert (maintenance["maintenance_type"] == "emergency").any()
    assert sensors["vibration"].max() > sensors["vibration"].median()
    assert defects["defect_count"].max() > defects["defect_count"].median()
