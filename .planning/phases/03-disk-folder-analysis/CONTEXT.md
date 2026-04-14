# Phase 3 Context

**Phase**: 3 - Disk/Folder Analysis  
**Created**: 2026-04-14  
**Status**: Ready for Planning

---

## Phase Overview

**Goal**: Implement folder size analysis and disk space tracking

**Scope**:
- Recursive folder size calculation
- File type distribution analysis
- Disk usage trend tracking
- SQLite schema for storage
- GUI visualization (treemap/chart)

**Domain**: File system scanning and analysis - user-facing feature where visual presentation and user interaction patterns matter significantly

---

## Decisions & Constraints

### Technology Choices
- **sysinfo crate**: Already integrated (Phase 1), provides disk information but NOT recursive folder scanning
- **SQLite**: Already configured (Phase 1), will store folder size history
- **React + Recharts**: Already used for metrics visualization (Phase 2), will extend for folder analysis
- **Rust file system API**: Standard library `std::fs` for recursive scanning, `walkdir` crate for efficient directory traversal

### Architecture Decisions
1. **Data Flow**: Rust backend scans folders → SQLite for persistence → Frontend displays analysis results
2. **Scan Strategy**: Background async scanning (non-blocking UI), progress reporting
3. **Caching**: Scan results cached in SQLite to avoid redundant full scans
4. **Update Frequency**: Manual trigger or scheduled (configurable via Phase 9 settings)

### Integration Points
- Phase 1: Database schema needs extension for folder metrics
- Phase 2: Existing disk info API can be extended to include folder analysis
- Phase 2: Recharts already integrated, will add treemap visualization

### Known Constraints
- **Performance**: Full disk scans can be expensive - need progress reporting and cancellation
- **Permissions**: May need elevated permissions for system folders
- **Cross-platform**: Path handling differs between Windows/Linux/macOS

---

## Success Criteria

1. ✅ Rust backend recursively scans folders and calculates sizes
2. ✅ File type distribution analysis implemented
3. ✅ Scan results stored in SQLite with timestamps
4. ✅ Frontend displays folder tree with size visualization
5. ✅ Progress reporting during long scans
6. ✅ Application builds and runs without errors
7. ✅ All Tauri commands tested and documented

---

## Dependencies

- **Phase 1**: ✅ Complete - Project structure, database setup, basic UI
- **Phase 2**: ✅ Complete - Recharts already integrated, existing disk info infrastructure
- **External**: `walkdir` crate for efficient directory traversal

---

## Risk Assessment

**Low Risk**: Rust file system API is stable and well-documented
**Medium Risk**: Large folder scans may block UI without proper async handling
**High Risk**: Permission issues on system folders may cause partial failures
**Mitigation**: 
- Use `tokio` for async scanning
- Implement progress reporting and cancellation
- Gracefully handle permission errors with user notifications

---

## Canonical refs:

- ROADMAP.md: Phase 3 description (line 58-68)
- PROJECT.md: Core value and requirements (line 1-87)
- sys-monitor/src-tauri/src/db/schema.rs: Existing database schema
- sys-monitor/src-tauri/src/commands/system.rs: Existing disk info implementation
