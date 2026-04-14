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
