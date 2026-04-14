use serde::{Deserialize, Serialize};

/// Folder scan record
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FolderScan {
    pub id: Option<i64>,
    pub path: String,
    pub scan_timestamp: i64,
    pub total_size: u64,
    pub file_count: u64,
    pub folder_count: u64,
    pub scan_duration_ms: Option<u64>,
}

/// Individual item in a folder scan
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FolderItem {
    pub id: Option<i64>,
    pub scan_id: i64,
    pub path: String,
    pub name: String,
    pub size: u64,
    pub item_type: String,  // 'file' or 'folder'
    pub extension: Option<String>,
    pub parent_path: Option<String>,
}

/// File type statistics for a scan
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileTypeStat {
    pub id: Option<i64>,
    pub scan_id: i64,
    pub file_type: String,
    pub count: u64,
    pub total_size: u64,
}

/// Watched folder configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WatchedFolder {
    pub id: i64,
    pub path: String,
    pub alias: Option<String>,
    pub is_active: bool,
    pub recursive: bool,
    pub debounce_ms: u64,
    pub size_threshold_bytes: Option<u64>,
    pub file_count_threshold: Option<u64>,
    pub notify_on_create: bool,
    pub notify_on_delete: bool,
    pub notify_on_modify: bool,
    pub last_scan_timestamp: Option<i64>,
    pub last_event_timestamp: Option<i64>,
    pub total_events_count: u64,
}

/// Folder change event
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FolderEvent {
    pub id: i64,
    pub watched_folder_id: i64,
    pub event_type: String,
    pub file_path: String,
    pub file_size: Option<u64>,
    pub timestamp: i64,
}
