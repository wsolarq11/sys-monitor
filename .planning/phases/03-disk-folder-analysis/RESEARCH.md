# Phase 3 Research

**Phase**: 3 - Disk/Folder Analysis  
**Date**: 2026-04-14  
**Status**: Research Complete

---

## Research Questions

### 1. Directory Traversal Strategy

**Question**: What's the best approach for recursive folder scanning in Rust?

**Options**:
1. **`walkdir` crate** (Recommended)
   - Pros: Efficient, handles symlinks, cancellation support, streaming iterator
   - Cons: Additional dependency
   - Use case: Large directory trees, progress reporting

2. **`std::fs::read_dir` with recursion**
   - Pros: No dependencies, full control
   - Cons: Manual implementation, harder to handle edge cases
   - Use case: Simple scans, minimal dependencies

3. **`ignore` crate**
   - Pros: Respects `.gitignore`, efficient
   - Cons: Overkill for simple scans, additional dependency
   - Use case: If ignoring patterns is needed

**Decision**: Use `walkdir` crate for efficient directory traversal with progress reporting

**Evidence**:
- `walkdir` is widely used and well-maintained
- Provides `WalkDir` iterator with depth control
- Supports cancellation via `try_for_each`
- Handles symlinks and permission errors gracefully

---

### 2. Folder Size Calculation

**Question**: How to calculate folder sizes efficiently?

**Options**:
1. **Bottom-up aggregation**
   - Scan all files, sum sizes, aggregate to parent folders
   - Pros: Accurate, handles hard links
   - Cons: Requires two passes or complex data structures

2. **Top-down recursion**
   - Visit folder, sum files, recurse into subfolders
   - Pros: Simple, single pass
   - Cons: May double-count hard links

3. **Hybrid approach**
   - Cache file sizes, aggregate on demand
   - Pros: Flexible, supports incremental updates
   - Cons: More complex implementation

**Decision**: Use top-down recursion with caching for initial implementation

**Evidence**:
- Simpler to implement and maintain
- Hard links are rare in typical user scenarios
- Can be optimized later if needed

---

### 3. File Type Classification

**Question**: How to classify files by type?

**Options**:
1. **Extension-based** (Recommended)
   - Map extensions to categories (e.g., `.jpg` → Images)
   - Pros: Fast, simple, no content reading needed
   - Cons: May misclassify files without extensions

2. **MIME type detection**
   - Use `file` crate or similar
   - Pros: More accurate, content-based
   - Cons: Slower, requires reading file content

3. **Hybrid approach**
   - Check extension first, fallback to content if ambiguous
   - Pros: Balanced accuracy and performance
   - Cons: More complex

**Decision**: Use extension-based classification with common extensions

**Evidence**:
- Phase 2 shows user prefers performance over perfection
- Extension-based is sufficient for typical use cases
- Can be extended later with MIME detection

**Proposed Categories**:
- Images: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`, `.webp`
- Videos: `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`
- Audio: `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`
- Documents: `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.txt`
- Archives: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`
- Code: `.rs`, `.js`, `.ts`, `.py`, `.java`, `.cpp`, `.h`, `.c`
- Others: Everything else

---

### 4. Database Schema Extension

**Question**: How to extend existing schema for folder metrics?

**Current Schema** (from `schema.rs`):
```sql
CREATE TABLE IF NOT EXISTS system_metrics (...);
CREATE TABLE IF NOT EXISTS disk_metrics (...);
```

**Proposed Extension**:
```sql
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

CREATE TABLE IF NOT EXISTS folder_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    name TEXT NOT NULL,
    size INTEGER NOT NULL,
    type TEXT NOT NULL,  -- 'file' or 'folder'
    extension TEXT,
    parent_path TEXT,
    FOREIGN KEY (scan_id) REFERENCES folder_scans(id)
);

CREATE TABLE IF NOT EXISTS file_type_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,
    file_type TEXT NOT NULL,
    count INTEGER NOT NULL,
    total_size INTEGER NOT NULL,
    FOREIGN KEY (scan_id) REFERENCES folder_scans(id)
);

CREATE INDEX IF NOT EXISTS idx_folder_scans_path ON folder_scans(path);
CREATE INDEX IF NOT EXISTS idx_folder_scans_timestamp ON folder_scans(scan_timestamp);
CREATE INDEX IF NOT EXISTS idx_folder_items_scan ON folder_items(scan_id);
CREATE INDEX IF NOT EXISTS idx_file_type_stats_scan ON file_type_stats(scan_id);
```

**Evidence**:
- Maintains consistency with existing schema patterns
- Supports historical tracking of folder changes
- Allows efficient queries for trends and analysis

---

### 5. Frontend Visualization

**Question**: How to visualize folder structure and size distribution?

**Options**:
1. **Treemap** (Recommended)
   - Pros: Shows hierarchical structure and size proportions
   - Cons: Can become cluttered with many files
   - Library: `react-treemap` or `@visx/hierarchy`

2. **Sunburst Chart**
   - Pros: Good for hierarchical data
   - Cons: Less intuitive for size comparison
   - Library: `recharts` (already integrated)

3. **List/Table with Expandable Folders**
   - Pros: Easy to understand, good for detailed view
   - Cons: Takes more space
   - Library: `@tanstack/react-table`

4. **Hybrid Approach**
   - Treemap for overview, list for details
   - Pros: Best of both worlds
   - Cons: More complex implementation

**Decision**: Start with treemap for overview, add list view for details

**Evidence**:
- `recharts` already integrated (Phase 2), supports sunburst
- Treemap provides intuitive size comparison
- Can be extended later with detailed views

---

### 6. Async Scanning Strategy

**Question**: How to handle long-running scans without blocking UI?

**Options**:
1. **Tauri Command with Tokio**
   - Pros: Native Tauri integration, easy to use
   - Cons: Command timeout limits scan duration

2. **Tauri Event Stream**
   - Pros: Real-time progress updates, no timeout issues
   - Cons: More complex implementation

3. **Hybrid Approach**
   - Start scan via command, emit events for progress
   - Pros: Best of both worlds
   - Cons: Most complex

**Decision**: Use hybrid approach with command + event stream

**Evidence**:
- Phase 2 uses polling for metrics (1s interval)
- Events already used for real-time updates in Phase 2
- Allows cancellation and progress reporting

---

## Implementation Plan

### Backend (Rust)

1. **Add `walkdir` dependency** to `Cargo.toml`
2. **Create new models** for folder scans and items
3. **Create database schema** extension (folder_scans, folder_items, file_type_stats)
4. **Implement scan command** with progress events
5. **Add file type classification** logic
6. **Create disk analysis API** (extend existing `get_disk_info`)

### Frontend (React)

1. **Create folder scan component**
   - Tree view with expandable folders
   - Size display and visualization
2. **Add treemap visualization**
   - Use `recharts` or `@visx/hierarchy`
3. **Implement progress reporting**
   - Show scan progress and estimated time
4. **Add file type distribution chart**
   - Pie chart or bar chart by type
5. **Create scan history view**
   - List of previous scans with comparison

### Database

1. **Create migration** for new schema
2. **Add repository methods** for folder scans
3. **Implement historical queries** for trends

---

## Dependencies to Add

### Backend
```toml
walkdir = "2"
tokio = { version = "1", features = ["full"] }
```

### Frontend
```json
{
  "@visx/hierarchy": "^3.0.0",
  "react-treemap": "^3.3.0"
}
```

---

## Open Questions

1. **Scan scope**: Should we scan entire system or user-selected folders?
   - **Decision**: User-selected folders (more flexible, respects privacy)

2. **Scan frequency**: Manual only or scheduled?
   - **Decision**: Manual for v0.1.0, scheduled in Phase 9

3. **Storage location**: Where to store scan results?
   - **Decision**: SQLite database (consistent with Phase 2)

4. **Cancellation**: Should scans be cancellable?
   - **Decision**: Yes, important for large directories

---

## References

- [walkdir crate docs](https://docs.rs/walkdir/)
- [Recharts documentation](https://recharts.org/)
- [Tauri Commands guide](https://tauri.app/guides/command/)
- [Tauri Events guide](https://tauri.app/guides/event/)
