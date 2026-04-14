pub const INIT_SQL: &str = r#"
-- Core system metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    cpu_usage REAL NOT NULL,
    memory_usage REAL NOT NULL,
    memory_total REAL,
    disk_usage REAL,
    disk_total REAL,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Per-core CPU usage
CREATE TABLE IF NOT EXISTS cpu_cores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_id INTEGER NOT NULL,
    core_name TEXT NOT NULL,
    usage_percent REAL NOT NULL,
    FOREIGN KEY (metric_id) REFERENCES system_metrics(id)
);

-- Per-disk usage statistics
CREATE TABLE IF NOT EXISTS disk_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_id INTEGER NOT NULL,
    mount_point TEXT NOT NULL,
    total_bytes INTEGER NOT NULL,
    available_bytes INTEGER NOT NULL,
    disk_type TEXT,
    FOREIGN KEY (metric_id) REFERENCES system_metrics(id)
);

-- Network interface statistics
CREATE TABLE IF NOT EXISTS network_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    interface_name TEXT NOT NULL,
    bytes_sent INTEGER NOT NULL,
    bytes_received INTEGER NOT NULL,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Alert system
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    metric_type TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    threshold_value REAL,
    actual_value REAL,
    acknowledged INTEGER DEFAULT 0,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Folder scan history
CREATE TABLE IF NOT EXISTS folder_scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL,
    scan_timestamp INTEGER NOT NULL,
    total_size INTEGER NOT NULL,
    file_count INTEGER NOT NULL,
    folder_count INTEGER NOT NULL,
    scan_duration_ms INTEGER,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Individual items in scan
CREATE TABLE IF NOT EXISTS folder_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    name TEXT NOT NULL,
    size INTEGER NOT NULL,
    type TEXT NOT NULL,
    extension TEXT,
    parent_path TEXT,
    FOREIGN KEY (scan_id) REFERENCES folder_scans(id)
);

-- File type statistics
CREATE TABLE IF NOT EXISTS file_type_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,
    file_type TEXT NOT NULL,
    count INTEGER NOT NULL,
    total_size INTEGER NOT NULL,
    FOREIGN KEY (scan_id) REFERENCES folder_scans(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_cpu_cores_metric ON cpu_cores(metric_id);
CREATE INDEX IF NOT EXISTS idx_disk_metrics_metric ON disk_metrics(metric_id);
CREATE INDEX IF NOT EXISTS idx_network_timestamp ON network_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_folder_scans_path ON folder_scans(path);
CREATE INDEX IF NOT EXISTS idx_folder_scans_timestamp ON folder_scans(scan_timestamp);
CREATE INDEX IF NOT EXISTS idx_folder_items_scan ON folder_items(scan_id);
CREATE INDEX IF NOT EXISTS idx_file_type_stats_scan ON file_type_stats(scan_id);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at INTEGER DEFAULT (strftime('%s', 'now'))
);
"#;
