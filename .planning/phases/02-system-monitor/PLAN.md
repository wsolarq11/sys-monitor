# Phase 2 Plan

**Phase**: 2 - System Resource Monitor  
**Created**: 2026-04-13  
**Estimated Complexity**: Medium

---

## Implementation Plans

### Plan 2.1: Extend Database Schema
**Goal**: Add tables for disk and network metrics

**Tasks**:
1. Update `db/schema.rs` with new tables:
   - `cpu_cores` - Per-core CPU usage
   - `disk_metrics` - Per-disk statistics
   - `network_metrics` - Network interface stats
2. Add migration function to create tables if not exists
3. Update repository methods

**Verification**:
- [ ] Database tables created successfully
- [ ] Foreign key relationships working
- [ ] Indexes created for performance

---

### Plan 2.2: Enhance Rust Backend Commands
**Goal**: Add comprehensive system monitoring commands

**Tasks**:
1. Update `commands/system.rs`:
   - Enhance `get_system_metrics()` with disk/network data
   - Add `get_disk_usage()` command
   - Add `get_network_stats()` command
   - Add `get_cpu_cores()` command
2. Update `models/metrics.rs`:
   - Add `DiskMetric` struct
   - Add `NetworkMetric` struct
   - Add `CpuCoreMetric` struct
3. Update `commands/database.rs`:
   - Add save methods for new metric types
   - Add query methods for historical data

**Verification**:
- [ ] All commands compile without errors
- [ ] Commands return correct data types
- [ ] Database operations work correctly

---

### Plan 2.3: Add Real-time Data Collection
**Goal**: Implement background metric collection

**Tasks**:
1. Create `commands/monitor.rs`:
   - `start_monitoring()` - Start background collection
   - `stop_monitoring()` - Stop collection
   - `is_monitoring()` - Check status
2. Use `tokio::spawn` for async background task
3. Store metrics every 60 seconds
4. Update in-memory cache every 1 second

**Verification**:
- [ ] Monitoring starts/stops correctly
- [ ] Metrics collected at correct intervals
- [ ] No memory leaks or performance issues

---

### Plan 2.4: Add Recharts for Visualization
**Goal**: Install and configure chart library

**Tasks**:
1. Install dependency: `pnpm add recharts`
2. Create base chart component: `components/common/BaseChart.tsx`
3. Configure TypeScript types for chart data

**Verification**:
- [ ] Recharts installed successfully
- [ ] Base component renders correctly
- [ ] TypeScript types defined

---

### Plan 2.5: Create CPU Monitoring Component
**Goal**: Real-time CPU usage visualization

**Tasks**:
1. Create `components/SystemMonitor/CPUGraph.tsx`:
   - Line chart showing CPU usage over time
   - Per-core usage display
   - Global usage percentage
2. Update `stores/metricsStore.ts`:
   - Add historical data array
   - Add methods to append new data points
3. Implement polling mechanism (1 second interval)

**Verification**:
- [ ] CPU graph displays correctly
- [ ] Real-time updates working
- [ ] Performance is smooth (60fps)

---

### Plan 2.6: Create Memory Monitoring Component
**Goal**: Memory usage visualization

**Tasks**:
1. Create `components/SystemMonitor/MemoryGraph.tsx`:
   - Area chart for memory usage
   - Show used/available/total
   - Percentage display
2. Add memory trend over time (last 60 seconds)

**Verification**:
- [ ] Memory graph displays correctly
- [ ] Colors differentiate used vs available
- [ ] Real-time updates working

---

### Plan 2.7: Create Disk Usage Component
**Goal**: Disk space visualization

**Tasks**:
1. Create `components/SystemMonitor/DiskUsageCard.tsx`:
   - Bar chart for each disk
   - Show used/free space
   - Display disk type (SSD/HDD)
2. Create `components/SystemMonitor/DiskList.tsx`:
   - Table view of all disks
   - Mount point, total, used, free, type

**Verification**:
- [ ] All disks displayed correctly
- [ ] Space calculations accurate
- [ ] UI is responsive

---

### Plan 2.8: Create Network Stats Component
**Goal**: Network traffic monitoring

**Tasks**:
1. Create `components/SystemMonitor/NetworkStats.tsx`:
   - Show upload/download speeds
   - Total bytes transferred
   - Per-interface statistics
2. Add real-time speed calculation (bytes/second)

**Verification**:
- [ ] Network interfaces listed
- [ ] Speeds calculated correctly
- [ ] Totals displayed accurately

---

### Plan 2.9: Update Dashboard Layout
**Goal**: Integrate all new components

**Tasks**:
1. Update `App.tsx`:
   - Add tabs or sections for different metrics
   - Improve navigation
2. Update `components/Dashboard/Dashboard.tsx`:
   - Grid layout for all components
   - Responsive design
3. Add loading states and error handling

**Verification**:
- [ ] Dashboard displays all metrics
- [ ] Layout is responsive
- [ ] Loading states work correctly

---

### Plan 2.10: Testing and Documentation
**Goal**: Ensure quality and maintainability

**Tasks**:
1. Test all Tauri commands manually
2. Create `PHASE2_TESTS.md` with test cases
3. Update README.md with Phase 2 features
4. Document API endpoints and data models

**Verification**:
- [ ] All test cases pass
- [ ] Documentation is complete
- [ ] Code is committed to git

---

## Execution Strategy

**Wave 1**: Backend Foundation (Plans 2.1-2.3)
- Database schema
- Backend commands
- Data collection

**Wave 2**: Frontend Components (Plans 2.4-2.8)
- Recharts setup
- Individual metric components

**Wave 3**: Integration (Plans 2.9-2.10)
- Dashboard layout
- Testing and documentation

---

## Dependencies

- Phase 1: ✅ Complete
- External packages:
  - `recharts` (npm)
  - `sysinfo` (Rust) - already installed

---

## Success Criteria

1. ✅ All system metrics collected and displayed
2. ✅ Real-time updates working smoothly
3. ✅ Historical data stored in SQLite
4. ✅ Application builds without errors
5. ✅ All components documented and tested
