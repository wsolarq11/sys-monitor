# Phase 3 Plan

**Phase**: 3 - Disk/Folder Analysis  
**Date**: 2026-04-14  
**Status**: Plan Ready for Execution

---

## Overview

Implement folder size analysis and disk space tracking with recursive scanning, file type classification, and GUI visualization.

**Goal**: As a user, I want to analyze folder sizes and understand disk usage patterns to identify large files and optimize storage.

**Success Criteria**:
- Recursive folder scanning with progress reporting
- File type distribution analysis
- Historical tracking of folder sizes
- Interactive GUI visualization (treemap + list view)
- All tests passing

---

## Scope

### In Scope
- Recursive folder size calculation
- File type classification and distribution
- SQLite storage for scan history
- Tauri backend commands with async scanning
- React frontend with treemap visualization
- Progress reporting and cancellation
- Basic error handling (permissions, large folders)

### Out of Scope
- Network folder scanning (UNC paths)
- Real-time folder monitoring (Phase 9)
- Cloud storage integration
- Advanced file filtering (Phase 9)
- Duplicate file detection

---

## Implementation Tasks

### Backend (Rust)

#### 1. Add Dependencies
**File**: `sys-monitor/src-tauri/Cargo.toml`

```toml
[dependencies]
walkdir = "2"
tokio = { version = "1", features = ["full"] }
```

#### 2. Create Data Models
**File**: `sys-monitor/src-tauri/src/models/folder.rs` (new)

```rust
use serde::{Deserialize, Serialize};

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

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileTypeStat {
    pub id: Option<i64>,
    pub scan_id: i64,
    pub file_type: String,
    pub count: u64,
    pub total_size: u64,
}
```

#### 3. Extend Database Schema
**File**: `sys-monitor/src-tauri/src/db/schema.rs` (modify)

Add new tables:
- `folder_scans`
- `folder_items`
- `file_type_stats`

#### 4. Create Repository Methods
**File**: `sys-monitor/src-tauri/src/db/repository.rs` (modify)

```rust
pub fn create_folder_scan(scan: &FolderScan) -> Result<i64>;
pub fn get_folder_scans(path: &str, limit: i64) -> Result<Vec<FolderScan>>;
pub fn get_folder_items(scan_id: i64) -> Result<Vec<FolderItem>>;
pub fn get_file_type_stats(scan_id: i64) -> Result<Vec<FileTypeStat>>;
pub fn delete_folder_scan(scan_id: i64) -> Result<usize>;
```

#### 5. Implement File Type Classification
**File**: `sys-monitor/src-tauri/src/utils/file_types.rs` (new)

```rust
pub fn classify_file(path: &str) -> String;
pub fn get_extension(path: &str) -> Option<String>;
pub fn get_file_type_category(extension: &str) -> String;
```

#### 6. Implement Folder Scanning
**File**: `sys-monitor/src-tauri/src/commands/folder.rs` (new)

```rust
#[command]
pub fn scan_folder(path: String) -> Result<serde_json::Value, AppError>;

#[command]
pub fn cancel_scan(scan_id: i64) -> Result<(), AppError>;
```

Use `walkdir` for directory traversal with progress reporting via Tauri events.

#### 7. Update Main Library
**File**: `sys-monitor/src-tauri/src/lib.rs` (modify)

```rust
mod commands::folder;
mod models::folder;
mod utils::file_types;

// Add to invoke_handler
scan_folder,
cancel_scan,
```

---

### Frontend (React)

#### 1. Create Folder Scan Component
**File**: `sys-monitor/src/components/FolderAnalysis/FolderScan.tsx` (new)

Features:
- File picker for folder selection
- Progress bar during scan
- Cancellation button
- Scan history dropdown

#### 2. Create Treemap Visualization
**File**: `sys-monitor/src/components/FolderAnalysis/Treemap.tsx` (new)

Features:
- Recursive folder structure
- Size-based coloring
- Hover tooltips with details
- Click to drill down

#### 3. Create File Type Distribution Chart
**File**: `sys-monitor/src/components/FolderAnalysis/FileTypeDistribution.tsx` (new)

Features:
- Pie chart or bar chart
- Top 10 categories
- Percentage and absolute sizes

#### 4. Create Scan History View
**File**: `sys-monitor/src/components/FolderAnalysis/ScanHistory.tsx` (new)

Features:
- List of previous scans
- Comparison between scans
- Delete individual scans
- Export functionality

#### 5. Create Folder Analysis Dashboard
**File**: `sys-monitor/src/components/FolderAnalysis/FolderAnalysis.tsx` (new)

Features:
- Main dashboard layout
- Navigation between views
- Integration with existing layout

#### 6. Add to App Router
**File**: `sys-monitor/src/App.tsx` (modify)

Add route for folder analysis page.

---

### Database

#### 1. Create Migration
**File**: `sys-monitor/src-tauri/src/db/migrations/003_folder_analysis.sql` (new)

```sql
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
```

#### 2. Update Repository
**File**: `sys-monitor/src-tauri/src/db/repository.rs` (modify)

Add methods for folder scan operations.

---

## Testing Strategy

### Unit Tests
- File type classification
- Size calculation
- Path handling (cross-platform)

### Integration Tests
- Full folder scan
- Progress reporting
- Database persistence
- Cancellation

### E2E Tests
- User workflow: Select folder → Scan → View results
- History management
- Error handling (permissions, large folders)

---

## Verification Checklist

- [ ] Backend compiles without errors
- [ ] All Tauri commands tested
- [ ] Database schema applied successfully
- [ ] Frontend builds without errors
- [ ] Treemap visualization renders correctly
- [ ] Progress reporting works
- [ ] Cancellation works
- [ ] Error handling for permissions
- [ ] Scan history stored in SQLite
- [ ] File type classification accurate
- [ ] Cross-platform path handling
- [ ] Documentation updated

---

## Known Issues & Tradeoffs

1. **Performance**: Large folder trees may take time to scan
   - Mitigation: Progress reporting, async scanning

2. **Permissions**: May fail on system folders
   - Mitigation: Graceful error handling, user notifications

3. **Storage**: Scan history grows over time
   - Mitigation: Implement cleanup in Phase 9

4. **Accuracy**: May double-count hard links
   - Mitigation: Accept for v0.1.0, optimize later

---

## Dependencies

### Backend
- `walkdir = "2"` - Directory traversal
- `tokio = "1"` - Async runtime

### Frontend
- `@visx/hierarchy` - Treemap visualization
- `recharts` - File type distribution chart

---

## Timeline Estimate

- Backend implementation: 4-6 hours
- Frontend implementation: 6-8 hours
- Testing: 2-3 hours
- Documentation: 1 hour

**Total**: 13-18 hours

---

## Next Steps

1. Execute Phase 3 plan
2. Verify all acceptance criteria
3. Update ROADMAP.md
4. Create Phase 4 plan (Network Monitor)
