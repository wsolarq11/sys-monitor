-- Phase 3: Folder Analysis Schema
-- Migration: 003_folder_analysis.sql

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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_folder_scans_path ON folder_scans(path);
CREATE INDEX IF NOT EXISTS idx_folder_scans_timestamp ON folder_scans(scan_timestamp);
CREATE INDEX IF NOT EXISTS idx_folder_items_scan ON folder_items(scan_id);
CREATE INDEX IF NOT EXISTS idx_file_type_stats_scan ON file_type_stats(scan_id);
