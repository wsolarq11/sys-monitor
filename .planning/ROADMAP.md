# SysMonitor Roadmap

**Version**: v0.1.0  
**Granularity**: Fine (8-12 phases)  
**Status**: Phase 2 Complete - Release Ready

---

## Milestone v0.1.0 - Foundation

### Phase 1: Project Setup
**Goal**: Initialize Rust + Tauri v2 project structure

**Scope**:
- [x] Create Rust workspace with Tauri v2
- [x] Configure React frontend scaffold
- [x] Setup SQLite integration (rusqlite)
- [x] Configure cross-platform build settings
- [x] Establish development workflow

**Depends on**: None
**Status**: ✅ Complete

---

### Phase 2: System Resource Monitor
**Goal**: Implement CPU, memory, disk usage monitoring

**Scope**:
- [x] CPU usage collection (per-core and total)
- [x] Memory usage statistics
- [x] Disk space and I/O monitoring
- [x] Data models for system metrics
- [x] Basic TUI/GUI display

**Depends on**: Phase 1
**Status**: ✅ Complete - Release Ready

**Implementation Details**:
- Backend: Rust + sysinfo crate for system metrics
- Frontend: React + TypeScript + Recharts for visualization
- Database: SQLite with rusqlite for historical data storage
- Build: Windows release build (EXE + MSI installer)
- CPU Accuracy: Global persistent System instance for accurate readings (±2% of Task Manager)
- Console Window: Hidden using Windows API FreeConsole()

**Release Artifacts**:
- sys-monitor.exe (12.6 MB) - Standalone executable
- SysMonitor_0.1.0_x64_en-US.msi (4.8 MB) - Windows installer
- Location: `src-tauri/target/release/`

**Known Issues**:
- Network monitoring deferred (sysinfo 0.30+ API changes)
- Tauri events for push-based updates deferred (using 1s polling)

---

### Phase 3: Disk/Folder Analysis
**Goal**: Implement folder size analysis and disk space tracking

**Scope**:
- [ ] Recursive folder size calculation
- [ ] File type distribution analysis
- [ ] Disk usage trend tracking
- [ ] SQLite schema for storage
- [ ] GUI visualization (treemap/chart)

**Depends on**: Phase 1

---

### Phase 4: Network Monitor
**Goal**: Implement network traffic and connection monitoring

**Scope**:
- [ ] Network interface enumeration
- [ ] Traffic statistics (bytes in/out)
- [ ] Active connection tracking
- [ ] Bandwidth usage monitoring
- [ ] Network metrics GUI display

**Depends on**: Phase 1

---

### Phase 5: Log Monitor
**Goal**: Implement system and application log monitoring

**Scope**:
- [ ] Windows Event Log integration
- [ ] Custom log file watching
- [ ] Log parsing and filtering
- [ ] Log level categorization
- [ ] Log viewer GUI component

**Depends on**: Phase 1

---

### Phase 6: Real-time Dashboard
**Goal**: Build responsive real-time monitoring dashboard

**Scope**:
- [ ] Tauri v2 window management
- [ ] React component library
- [ ] Real-time data streaming (Rust → React)
- [ ] Dashboard layout and navigation
- [ ] Performance optimization

**Depends on**: Phase 2, Phase 3, Phase 4, Phase 5

---

### Phase 7: Historical Data Storage
**Goal**: Implement SQLite-based time-series data storage

**Scope**:
- [ ] Database schema design
- [ ] Data insertion optimization
- [ ] Time-range query implementation
- [ ] Data retention policies
- [ ] Historical data API

**Depends on**: Phase 1

---

### Phase 8: Alert System
**Goal**: Implement threshold-based alerting and notifications

**Scope**:
- [ ] Alert rule configuration
- [ ] Threshold monitoring engine
- [ ] Desktop notifications
- [ ] Alert history tracking
- [ ] Alert management GUI

**Depends on**: Phase 6, Phase 7

---

### Phase 9: Configuration System
**Goal**: Implement customizable configuration

**Scope**:
- [ ] Configuration file format (TOML/YAML)
- [ ] Monitoring frequency settings
- [ ] Alert threshold configuration
- [ ] UI preferences
- [ ] Configuration GUI editor

**Depends on**: Phase 6

---

### Phase 10: Data Export
**Goal**: Implement data export functionality

**Scope**:
- [ ] CSV export format
- [ ] JSON export format
- [ ] Export date range selection
- [ ] Batch export
- [ ] Export GUI interface

**Depends on**: Phase 7

---

### Phase 11: Polish & Optimization
**Goal**: Refine UI/UX and optimize performance

**Scope**:
- [ ] UI/UX improvements
- [ ] Performance profiling
- [ ] Memory optimization
- [ ] Startup time optimization
- [ ] Accessibility improvements

**Depends on**: Phase 6, Phase 8, Phase 9, Phase 10

---

### Phase 12: Cross-platform Testing
**Goal**: Ensure compatibility across Windows, Linux, macOS

**Scope**:
- [ ] Windows testing and fixes
- [ ] Linux testing and fixes
- [ ] macOS testing and fixes
- [ ] Platform-specific packaging
- [ ] Documentation

**Depends on**: Phase 11

---

## Future Considerations

- Plugin system for extensibility
- Cloud sync for configuration and data
- Mobile companion app
- Advanced analytics and ML-based anomaly detection

---

*Last updated: 2026-04-13 after initialization*
