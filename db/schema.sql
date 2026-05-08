PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS machines (
    machine_id TEXT PRIMARY KEY,
    machine_type TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    facility_area TEXT NOT NULL,
    install_date TEXT NOT NULL,
    status TEXT NOT NULL,
    model TEXT,
    line_id TEXT,
    process_step TEXT,
    criticality TEXT,
    last_service_date TEXT,
    expected_lifetime_years INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    reading_id TEXT PRIMARY KEY,
    machine_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    temperature REAL NOT NULL,
    vibration REAL NOT NULL,
    pressure REAL NOT NULL,
    power_draw REAL NOT NULL,
    humidity REAL,
    cycle_count INTEGER,
    runtime_hours REAL,
    chamber_pressure REAL,
    gas_flow_rate REAL,
    error_code TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);

CREATE TABLE IF NOT EXISTS maintenance_records (
    maintenance_id TEXT PRIMARY KEY,
    machine_id TEXT NOT NULL,
    maintenance_date TEXT NOT NULL,
    maintenance_type TEXT NOT NULL,
    downtime_hours REAL NOT NULL,
    technician TEXT,
    parts_replaced TEXT,
    maintenance_cost REAL,
    severity TEXT,
    resolved INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);

CREATE TABLE IF NOT EXISTS defect_records (
    defect_id TEXT PRIMARY KEY,
    machine_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    defect_count INTEGER NOT NULL,
    batch_id TEXT NOT NULL,
    wafer_lot TEXT,
    defect_type TEXT,
    severity TEXT,
    yield_loss_pct REAL,
    process_step TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);

CREATE TABLE IF NOT EXISTS machine_features (
    machine_id TEXT PRIMARY KEY,
    feature_timestamp TEXT,
    avg_temperature REAL,
    max_temperature REAL,
    std_temperature REAL,
    avg_vibration REAL,
    max_vibration REAL,
    std_vibration REAL,
    avg_pressure REAL,
    var_pressure REAL,
    avg_power_draw REAL,
    var_power_draw REAL,
    rolling_7d_avg_temperature REAL,
    rolling_7d_avg_vibration REAL,
    rolling_7d_defect_count REAL,
    rolling_30d_maintenance_count REAL,
    recent_downtime_hours REAL,
    days_since_last_maintenance REAL,
    total_maintenance_events INTEGER,
    total_downtime_hours REAL,
    avg_downtime_per_event REAL,
    emergency_maintenance_count INTEGER,
    maintenance_frequency REAL,
    total_defect_count INTEGER,
    recent_defect_count INTEGER,
    avg_defects_per_batch REAL,
    defect_severity_score REAL,
    yield_loss_pct_avg REAL,
    machine_age_days INTEGER,
    machine_type TEXT,
    manufacturer TEXT,
    criticality TEXT,
    facility_area TEXT,
    target_failure_within_window INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);

CREATE TABLE IF NOT EXISTS model_runs (
    model_run_id TEXT PRIMARY KEY,
    model_type TEXT NOT NULL,
    training_timestamp TEXT NOT NULL,
    prediction_window_days INTEGER,
    random_seed INTEGER,
    metrics_json TEXT,
    feature_columns_json TEXT,
    artifact_path TEXT,
    metadata_path TEXT,
    simulated_data_warning TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS risk_predictions (
    prediction_id TEXT PRIMARY KEY,
    machine_id TEXT NOT NULL,
    model_run_id TEXT NOT NULL,
    risk_score REAL NOT NULL,
    predicted_failure_flag INTEGER NOT NULL,
    risk_level TEXT NOT NULL,
    prediction_timestamp TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id),
    FOREIGN KEY (model_run_id) REFERENCES model_runs(model_run_id)
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    pipeline_run_id TEXT PRIMARY KEY,
    run_type TEXT NOT NULL,
    status TEXT NOT NULL,
    run_started_at TEXT NOT NULL,
    run_finished_at TEXT,
    details_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_quality_issues (
    issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_run_id TEXT,
    dataset TEXT NOT NULL,
    severity TEXT NOT NULL,
    issue_type TEXT NOT NULL,
    message TEXT NOT NULL,
    row_count INTEGER,
    column_name TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_runs(pipeline_run_id)
);
