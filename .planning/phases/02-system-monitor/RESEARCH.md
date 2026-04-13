# Phase 2 Research

**Phase**: 2 - System Resource Monitor  
**Created**: 2026-04-13

---

## sysinfo Crate Capabilities

### CPU Monitoring
```rust
use sysinfo::System;

let mut sys = System::new_all();
sys.refresh_cpu();

// Per-core usage
for cpu in sys.cpus() {
    println!("{}: {}%", cpu.name(), cpu.cpu_usage());
}

// Global usage (manual calculation in sysinfo 0.30+)
let global = sys.cpus().iter().map(|c| c.cpu_usage()).sum::<f32>() / sys.cpus().len() as f32;
```

**Key APIs**:
- `System::cpus()` - Returns list of CPU cores
- `Cpu::cpu_usage()` - Returns usage percentage (0-100)
- `System::refresh_cpu()` - Updates CPU data
- `System::global_cpu_usage()` - **Removed in 0.30+**, must calculate manually

### Memory Monitoring
```rust
sys.refresh_memory();
let total = sys.total_memory();
let used = sys.used_memory();
let available = sys.available_memory();
let usage_percent = (used as f32 / total as f32) * 100.0;
```

**Key APIs**:
- `System::total_memory()` - Total physical RAM in bytes
- `System::used_memory()` - Used RAM in bytes
- `System::available_memory()` - Available RAM in bytes
- `System::free_memory()` - Free RAM in bytes

### Disk Monitoring
```rust
sys.refresh_disks();
for disk in sys.disks() {
    println!("{}: {} / {} bytes", 
        disk.mount_point().display(),
        disk.available_space(),
        disk.total_space()
    );
}
```

**Key APIs**:
- `System::disks()` - Returns list of mounted disks
- `Disk::total_space()` - Total disk size in bytes
- `Disk::available_space()` - Available space in bytes
- `Disk::kind()` - SSD or HDD
- `Disk::mount_point()` - Mount path

### Network Monitoring
```rust
sys.refresh_networks();
for (name, network) in sys.networks() {
    let received = network.total_received();
    let transmitted = network.total_transmitted();
}
```

**Key APIs**:
- `System::networks()` - Returns network interfaces
- `NetworkData::total_received()` - Total bytes received
- `NetworkData::total_transmitted()` - Total bytes transmitted
- `NetworkData::received()` - Current received rate
- `NetworkData::transmitted()` - Current transmitted rate

---

## Database Schema Design

### Extended system_metrics Table
```sql
CREATE TABLE IF NOT EXISTS system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    cpu_usage REAL NOT NULL,
    memory_usage REAL NOT NULL,
    memory_total REAL,
    disk_usage REAL,
    disk_total REAL,
    network_received INTEGER,
    network_transmitted INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_timestamp ON system_metrics(timestamp);
```

### New Tables for Detailed Tracking
```sql
-- Per-core CPU usage
CREATE TABLE IF NOT EXISTS cpu_cores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_id INTEGER NOT NULL,
    core_name TEXT NOT NULL,
    usage_percent REAL NOT NULL,
    FOREIGN KEY (metric_id) REFERENCES system_metrics(id)
);

-- Per-disk usage
CREATE TABLE IF NOT EXISTS disk_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_id INTEGER NOT NULL,
    mount_point TEXT NOT NULL,
    total_bytes INTEGER NOT NULL,
    available_bytes INTEGER NOT NULL,
    disk_type TEXT,
    FOREIGN KEY (metric_id) REFERENCES system_metrics(id)
);

-- Network interface stats
CREATE TABLE IF NOT EXISTS network_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_id INTEGER NOT NULL,
    interface_name TEXT NOT NULL,
    bytes_received INTEGER NOT NULL,
    bytes_transmitted INTEGER NOT NULL,
    FOREIGN KEY (metric_id) REFERENCES system_metrics(id)
);
```

---

## Frontend Visualization

### Recharts Library
```tsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

<ResponsiveContainer width="100%" height={200}>
  <LineChart data={data}>
    <XAxis dataKey="time" />
    <YAxis domain={[0, 100]} />
    <Tooltip />
    <Line type="monotone" dataKey="cpu" stroke="#8884d8" />
    <Line type="monotone" dataKey="memory" stroke="#82ca9d" />
  </LineChart>
</ResponsiveContainer>
```

**Components to Add**:
- `pnpm add recharts`

### Real-time Updates Strategy

**Option 1: Polling (Simple)**
```tsx
useEffect(() => {
  const interval = setInterval(async () => {
    const metrics = await get_system_metrics();
    setMetrics(metrics);
  }, 1000);
  return () => clearInterval(interval);
}, []);
```

**Option 2: Tauri Events (Advanced)**
```rust
// Backend
app_handle.emit("metrics-update", metrics)?;

// Frontend
listen('metrics-update', (event) => {
  setMetrics(event.payload);
});
```

**Decision**: Start with polling for simplicity, can upgrade to events later.

---

## Implementation Plan

### Backend (Rust)
1. Extend `get_system_metrics()` to include disk and network data
2. Add new commands:
   - `get_disk_usage()` - Per-disk statistics
   - `get_network_stats()` - Per-interface statistics
   - `start_monitoring()` - Start background collection
   - `stop_monitoring()` - Stop background collection
3. Update database schema and repository methods

### Frontend (React)
1. Add Recharts dependency
2. Create chart components:
   - `CPUGraph.tsx` - Real-time CPU usage
   - `MemoryGraph.tsx` - Memory usage over time
   - `DiskUsageCard.tsx` - Disk space visualization
   - `NetworkStats.tsx` - Network traffic display
3. Implement polling mechanism
4. Update Zustand store with historical data

---

## References

- [sysinfo documentation](https://docs.rs/sysinfo/latest/sysinfo/)
- [Recharts documentation](https://recharts.org/en-US/)
- [Tauri Events](https://v2.tauri.app/reference/javascript/api/namespaceevent/)
