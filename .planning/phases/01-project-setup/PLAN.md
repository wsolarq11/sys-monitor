# Phase 1 Plan: Project Setup

**Phase**: 1 - Project Setup  
**Goal**: Initialize Rust + Tauri v2 project structure  
**Status**: Ready for execution  
**Created**: 2026-04-13

---

## Success Criteria

Phase 1 is complete when:

1. ✅ Tauri v2 + React project created and builds successfully
2. ✅ SQLite integration configured with initial schema
3. ✅ System information library (sysinfo) integrated
4. ✅ Cross-platform build configuration in place
5. ✅ Development workflow established (dev, test, build)
6. ✅ Basic "Hello World" command working (Rust ↔ React communication)

---

## Implementation Plan

### Plan 1.1: Create Tauri v2 Project

**Goal**: Scaffold project with create-tauri-app

**Tasks**:
1. Run `pnpm create tauri-app@latest . --template react-ts` in current directory
2. Review generated structure
3. Verify development server starts: `pnpm tauri dev`
4. Verify production build works: `pnpm tauri build`

**Acceptance Criteria**:
- [ ] Project scaffolding completes without errors
- [ ] `pnpm tauri dev` opens window with React app
- [ ] `pnpm tauri build` produces executable
- [ ] Git repository initialized with proper .gitignore

**Estimated Time**: 30 minutes

---

### Plan 1.2: Add Rust Dependencies

**Goal**: Configure Rust dependencies in Cargo.toml

**Tasks**:
1. Navigate to `src-tauri/` directory
2. Add dependencies to `Cargo.toml`:
   ```toml
   [dependencies]
   tauri = { version = "2", features = [] }
   sysinfo = "0.30"
   rusqlite = { version = "0.31", features = ["bundled"] }
   serde = { version = "1.0", features = ["derive"] }
   serde_json = "1.0"
   thiserror = "1.0"
   tokio = { version = "1", features = ["full"] }
   ```
3. Run `cargo check` to verify dependencies resolve
4. Commit changes

**Acceptance Criteria**:
- [ ] All dependencies added to Cargo.toml
- [ ] `cargo check` passes without errors
- [ ] Dependencies download successfully

**Estimated Time**: 15 minutes

---

### Plan 1.3: Configure Tauri v2

**Goal**: Update tauri.conf.json for SysMonitor

**Tasks**:
1. Update `src-tauri/tauri.conf.json`:
   - Set `productName` to "SysMonitor"
   - Set `version` to "0.1.0"
   - Configure `identifier` (e.g., "com.sysmonitor.app")
   - Set window title and dimensions
   - Configure security settings (CSP)
2. Add app icons (use placeholder for now)
3. Configure build settings for all platforms

**Configuration**:
```json
{
  "productName": "SysMonitor",
  "version": "0.1.0",
  "identifier": "com.sysmonitor.app",
  "app": {
    "windows": [
      {
        "title": "SysMonitor - System Dashboard",
        "width": 1200,
        "height": 800,
        "resizable": true,
        "fullscreen": false
      }
    ],
    "security": {
      "csp": "default-src 'self'; img-src 'self' asset: https://asset.localhost"
    }
  },
  "bundle": {
    "active": true,
    "targets": ["msi", "appimage", "dmg"],
    "icon": ["icons/icon.ico", "icons/icon.icns", "icons/icon.png"]
  }
}
```

**Acceptance Criteria**:
- [ ] tauri.conf.json updated with SysMonitor configuration
- [ ] Window title displays correctly
- [ ] Build still works after configuration changes

**Estimated Time**: 20 minutes

---

### Plan 1.4: Setup SQLite Database

**Goal**: Create database schema and repository layer

**Tasks**:
1. Create `src-tauri/src/db/mod.rs` - Database module
2. Create `src-tauri/src/db/schema.rs` - Database schema
3. Create `src-tauri/src/db/repository.rs` - Data access layer
4. Implement database initialization in `src-tauri/src/main.rs`

**Schema Design** (`schema.rs`):
```rust
pub const INIT_SQL: &str = r#"
CREATE TABLE IF NOT EXISTS system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    cpu_usage REAL NOT NULL,
    memory_usage REAL NOT NULL,
    disk_usage REAL,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

CREATE TABLE IF NOT EXISTS network_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    interface_name TEXT NOT NULL,
    bytes_sent INTEGER,
    bytes_received INTEGER,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

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

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at INTEGER DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp 
ON system_metrics(timestamp);

CREATE INDEX IF NOT EXISTS idx_network_metrics_timestamp 
ON network_metrics(timestamp);
"#;
```

**Repository Implementation** (`repository.rs`):
```rust
use rusqlite::{Connection, Result};
use crate::models::metrics::SystemMetric;

pub struct DatabaseRepository {
    conn: Connection,
}

impl DatabaseRepository {
    pub fn new(path: &str) -> Result<Self> {
        let conn = Connection::open(path)?;
        Ok(Self { conn })
    }

    pub fn insert_system_metric(&self, metric: &SystemMetric) -> Result<()> {
        self.conn.execute(
            "INSERT INTO system_metrics (timestamp, cpu_usage, memory_usage, disk_usage)
             VALUES (?1, ?2, ?3, ?4)",
            [metric.timestamp, metric.cpu_usage, metric.memory_usage, metric.disk_usage],
        )?;
        Ok(())
    }

    pub fn get_recent_metrics(&self, limit: u32) -> Result<Vec<SystemMetric>> {
        let mut stmt = self.conn.prepare(
            "SELECT * FROM system_metrics ORDER BY timestamp DESC LIMIT ?1"
        )?;
        let metrics = stmt.query_map([limit], |row| {
            Ok(SystemMetric {
                id: row.get(0)?,
                timestamp: row.get(1)?,
                cpu_usage: row.get(2)?,
                memory_usage: row.get(3)?,
                disk_usage: row.get(4)?,
            })
        })?;
        
        metrics.collect::<Result<Vec<_>, _>>()
    }
}
```

**Database Location**:
- Windows: `%APPDATA%\SysMonitor\sysmonitor.db`
- Linux: `~/.config/sysmonitor/sysmonitor.db`
- macOS: `~/Library/Application Support/com.sysmonitor.app/sysmonitor.db`

**Acceptance Criteria**:
- [ ] Database module created with schema
- [ ] Repository layer implemented
- [ ] Database initializes on app startup
- [ ] Can insert and query test data

**Estimated Time**: 60 minutes

---

### Plan 1.5: Create Data Models

**Goal**: Define Rust data models for metrics

**Tasks**:
1. Create `src-tauri/src/models/mod.rs`
2. Create `src-tauri/src/models/metrics.rs`
3. Create `src-tauri/src/models/config.rs`

**Metrics Model** (`models/metrics.rs`):
```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemMetric {
    pub id: Option<i64>,
    pub timestamp: i64,
    pub cpu_usage: f64,
    pub memory_usage: f64,
    pub disk_usage: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkMetric {
    pub id: Option<i64>,
    pub timestamp: i64,
    pub interface_name: String,
    pub bytes_sent: u64,
    pub bytes_received: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Alert {
    pub id: Option<i64>,
    pub timestamp: i64,
    pub metric_type: String,
    pub metric_name: String,
    pub threshold_value: f64,
    pub actual_value: f64,
    pub acknowledged: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Setting {
    pub key: String,
    pub value: String,
    pub updated_at: i64,
}
```

**Acceptance Criteria**:
- [ ] All models defined with proper types
- [ ] Serialize/Deserialize traits implemented
- [ ] Models compile without warnings

**Estimated Time**: 30 minutes

---

### Plan 1.6: Implement Tauri Commands

**Goal**: Create Rust commands callable from React frontend

**Tasks**:
1. Create `src-tauri/src/commands/mod.rs`
2. Create `src-tauri/src/commands/system.rs` - System metrics commands
3. Create `src-tauri/src/commands/database.rs` - Database commands
4. Register commands in `src-tauri/src/lib.rs`

**System Commands** (`commands/system.rs`):
```rust
use sysinfo::{System, SystemExt};
use tauri::command;
use crate::models::metrics::SystemMetric;

#[command]
pub fn get_system_metrics() -> Result<SystemMetric, String> {
    let mut sys = System::new_all();
    sys.refresh_all();

    Ok(SystemMetric {
        id: None,
        timestamp: chrono::Utc::now().timestamp(),
        cpu_usage: sys.global_cpu_usage() as f64,
        memory_usage: sys.used_memory() as f64,
        disk_usage: None, // TODO: Implement disk monitoring
    })
}

#[command]
pub fn get_cpu_info() -> Result<serde_json::Value, String> {
    let mut sys = System::new();
    sys.refresh_cpu();

    let cores: Vec<serde_json::Value> = sys.cpus().iter().map(|cpu| {
        serde_json::json!({
            "name": cpu.name(),
            "brand": cpu.brand(),
            "frequency": cpu.frequency(),
            "usage": cpu.cpu_usage()
        })
    }).collect();

    Ok(serde_json::json!({
        "cores": cores,
        "global_usage": sys.global_cpu_usage()
    }))
}

#[command]
pub fn get_memory_info() -> Result<serde_json::Value, String> {
    let mut sys = System::new_all();
    sys.refresh_memory();

    Ok(serde_json::json!({
        "total": sys.total_memory(),
        "used": sys.used_memory(),
        "free": sys.free_memory(),
        "available": sys.available_memory(),
        "usage_percent": (sys.used_memory() as f64 / sys.total_memory() as f64) * 100.0
    }))
}
```

**Database Commands** (`commands/database.rs`):
```rust
use tauri::command;
use crate::db::repository::DatabaseRepository;
use crate::models::metrics::SystemMetric;

#[command]
pub fn save_system_metric(metric: SystemMetric) -> Result<(), String> {
    // TODO: Get repository from app state
    // For now, create new connection each time
    let repo = DatabaseRepository::new("sysmonitor.db")
        .map_err(|e| e.to_string())?;
    
    repo.insert_system_metric(&metric)
        .map_err(|e| e.to_string())?;
    
    Ok(())
}

#[command]
pub fn get_recent_metrics(limit: u32) -> Result<Vec<SystemMetric>, String> {
    let repo = DatabaseRepository::new("sysmonitor.db")
        .map_err(|e| e.to_string())?;
    
    repo.get_recent_metrics(limit)
        .map_err(|e| e.to_string())
}
```

**Register Commands** (`lib.rs`):
```rust
mod commands;
mod db;
mod models;
mod error;

use commands::system::{get_system_metrics, get_cpu_info, get_memory_info};
use commands::database::{save_system_metric, get_recent_metrics};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            get_system_metrics,
            get_cpu_info,
            get_memory_info,
            save_system_metric,
            get_recent_metrics
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**Acceptance Criteria**:
- [ ] All commands compile without errors
- [ ] Commands can be invoked from frontend
- [ ] Error handling implemented

**Estimated Time**: 60 minutes

---

### Plan 1.7: Setup React Frontend Structure

**Goal**: Create React component structure and styling

**Tasks**:
1. Install additional dependencies:
   ```bash
   pnpm add recharts zustand clsx tailwind-merge
   pnpm add -D tailwindcss postcss autoprefixer
   ```
2. Initialize Tailwind CSS:
   ```bash
   pnpm tailwindcss init -p
   ```
3. Configure `tailwind.config.js`
4. Add Tailwind directives to `src/index.css`
5. Create component structure

**Tailwind Config** (`tailwind.config.js`):
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        },
      },
    },
  },
  plugins: [],
}
```

**Component Structure**:
```
src/
├── components/
│   ├── Dashboard/
│   │   ├── Dashboard.tsx
│   │   └── Dashboard.css
│   ├── SystemMonitor/
│   │   ├── CPUMonitor.tsx
│   │   ├── MemoryMonitor.tsx
│   │   └── DiskMonitor.tsx
│   └── common/
│       ├── Card.tsx
│       ├── Loading.tsx
│       └── ErrorBoundary.tsx
├── hooks/
│   └── useSystemMetrics.ts
├── stores/
│   └── metricsStore.ts
└── utils/
    └── format.ts
```

**Acceptance Criteria**:
- [ ] Tailwind CSS configured and working
- [ ] Component directories created
- [ ] Basic layout component renders

**Estimated Time**: 45 minutes

---

### Plan 1.8: Create State Management

**Goal**: Setup Zustand store for metrics state

**Tasks**:
1. Create `src/stores/metricsStore.ts`
2. Implement store with metrics state
3. Add actions for updating metrics

**Store Implementation** (`metricsStore.ts`):
```typescript
import { create } from 'zustand';
import { invoke } from '@tauri-apps/api/core';

interface SystemMetric {
  id?: number;
  timestamp: number;
  cpu_usage: number;
  memory_usage: number;
  disk_usage?: number;
}

interface MetricsState {
  currentMetrics: SystemMetric | null;
  historicalMetrics: SystemMetric[];
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchCurrentMetrics: () => Promise<void>;
  startPolling: (intervalMs: number) => void;
  stopPolling: () => void;
}

export const useMetricsStore = create<MetricsState>((set, get) => ({
  currentMetrics: null,
  historicalMetrics: [],
  loading: false,
  error: null,
  
  fetchCurrentMetrics: async () => {
    set({ loading: true, error: null });
    try {
      const metrics = await invoke<SystemMetric>('get_system_metrics');
      set({ currentMetrics: metrics, loading: false });
      
      // Add to historical
      const historical = get().historicalMetrics;
      set({ historicalMetrics: [metrics, ...historical].slice(0, 100) });
    } catch (err) {
      set({ error: String(err), loading: false });
    }
  },
  
  startPolling: (intervalMs: number) => {
    const { fetchCurrentMetrics } = get();
    fetchCurrentMetrics();
    
    const intervalId = setInterval(fetchCurrentMetrics, intervalMs);
    (get() as any)._pollingInterval = intervalId;
  },
  
  stopPolling: () => {
    const intervalId = (get() as any)._pollingInterval;
    if (intervalId) {
      clearInterval(intervalId);
    }
  },
}));
```

**Acceptance Criteria**:
- [ ] Store created with proper types
- [ ] Can fetch metrics from Rust backend
- [ ] Polling mechanism works

**Estimated Time**: 30 minutes

---

### Plan 1.9: Create Basic UI Components

**Goal**: Build initial dashboard UI

**Tasks**:
1. Create `src/components/common/Card.tsx` - Reusable card component
2. Create `src/components/SystemMonitor/CPUMonitor.tsx`
3. Create `src/components/SystemMonitor/MemoryMonitor.tsx`
4. Create `src/components/Dashboard/Dashboard.tsx`
5. Update `src/App.tsx` to use Dashboard

**Card Component** (`Card.tsx`):
```typescript
import React from 'react';

interface CardProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

export function Card({ title, children, className = '' }: CardProps) {
  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
      {children}
    </div>
  );
}
```

**CPU Monitor** (`CPUMonitor.tsx`):
```typescript
import React from 'react';
import { useMetricsStore } from '../../stores/metricsStore';
import { Card } from '../common/Card';

export function CPUMonitor() {
  const currentMetrics = useMetricsStore((state) => state.currentMetrics);
  
  return (
    <Card title="CPU Usage">
      <div className="text-4xl font-bold text-blue-600">
        {currentMetrics?.cpu_usage.toFixed(1) || 0}%
      </div>
      <div className="mt-2 text-sm text-gray-500">
        Current usage across all cores
      </div>
    </Card>
  );
}
```

**Memory Monitor** (`MemoryMonitor.tsx`):
```typescript
import React from 'react';
import { useMetricsStore } from '../../stores/metricsStore';
import { Card } from '../common/Card';

function formatBytes(bytes: number): string {
  const gb = bytes / (1024 * 1024 * 1024);
  return `${gb.toFixed(2)} GB`;
}

export function MemoryMonitor() {
  const currentMetrics = useMetricsStore((state) => state.currentMetrics);
  
  return (
    <Card title="Memory Usage">
      <div className="text-4xl font-bold text-green-600">
        {currentMetrics ? formatBytes(currentMetrics.memory_usage) : '0 GB'}
      </div>
      <div className="mt-2 text-sm text-gray-500">
        System memory in use
      </div>
    </Card>
  );
}
```

**Dashboard** (`Dashboard.tsx`):
```typescript
import React, { useEffect } from 'react';
import { useMetricsStore } from '../stores/metricsStore';
import { CPUMonitor } from '../SystemMonitor/CPUMonitor';
import { MemoryMonitor } from '../SystemMonitor/MemoryMonitor';

export function Dashboard() {
  const { startPolling, stopPolling } = useMetricsStore();
  
  useEffect(() => {
    startPolling(2000); // Poll every 2 seconds
    
    return () => {
      stopPolling();
    };
  }, []);
  
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        SysMonitor Dashboard
      </h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <CPUMonitor />
        <MemoryMonitor />
      </div>
    </div>
  );
}
```

**Update App.tsx**:
```typescript
import { Dashboard } from './components/Dashboard/Dashboard';

function App() {
  return <Dashboard />;
}

export default App;
```

**Acceptance Criteria**:
- [ ] Dashboard renders without errors
- [ ] Metrics display updates in real-time
- [ ] UI is responsive and looks professional

**Estimated Time**: 60 minutes

---

### Plan 1.10: Test Cross-platform Build

**Goal**: Verify builds work on current platform

**Tasks**:
1. Run development build: `pnpm tauri dev`
2. Run production build: `pnpm tauri build`
3. Test installed application
4. Document any platform-specific issues

**Acceptance Criteria**:
- [ ] Development build starts successfully
- [ ] Production build completes without errors
- [ ] Application launches and displays metrics
- [ ] No console errors in developer tools

**Estimated Time**: 30 minutes

---

### Plan 1.11: Documentation

**Goal**: Create initial documentation

**Tasks**:
1. Create `README.md` with:
   - Project overview
   - Prerequisites
   - Setup instructions
   - Development commands
   - Build instructions
2. Create `CONTRIBUTING.md` (optional)
3. Update `.gitignore` if needed

**README.md Template**:
```markdown
# SysMonitor

A cross-platform system monitoring dashboard built with Rust and Tauri v2.

## Prerequisites

- Node.js 18+
- pnpm
- Rust 1.70+
- Platform-specific requirements (see below)

## Development

```bash
# Install dependencies
pnpm install

# Start development server
pnpm tauri dev

# Run tests
cd src-tauri && cargo test
```

## Build

```bash
pnpm tauri build
```

## Platform Requirements

### Windows
- WebView2 (included in Windows 10 1803+)

### Linux
```bash
sudo apt install libwebkit2gtk-4.0-dev build-essential libssl-dev \
  libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev
```

### macOS
- Xcode Command Line Tools
```

**Acceptance Criteria**:
- [ ] README.md created with clear instructions
- [ ] Documentation is accurate and complete

**Estimated Time**: 20 minutes

---

## Verification

After completing all plans, verify:

1. **Build Verification**:
   ```bash
   pnpm tauri dev
   # Should open window with dashboard
   # Metrics should update every 2 seconds
   # No console errors
   ```

2. **Production Build**:
   ```bash
   pnpm tauri build
   # Should complete without errors
   # Executable should be in src-tauri/target/release/
   ```

3. **Functionality Verification**:
   - [ ] Dashboard displays CPU usage
   - [ ] Dashboard displays memory usage
   - [ ] Values update in real-time
   - [ ] No memory leaks after 5 minutes
   - [ ] Application closes cleanly

4. **Code Quality**:
   ```bash
   cd src-tauri && cargo clippy
   pnpm lint
   # Should have no warnings
   ```

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tauri v2 breaking changes | Medium | High | Use latest stable version, check changelog |
| SQLite performance issues | Low | Medium | Implement indexing, limit query results |
| Cross-platform build failures | Medium | Medium | Test on each platform early |
| WebView2 missing on old Windows | Low | Low | Document minimum requirements |

---

## Dependencies

- **Rust**: 1.70+
- **Node.js**: 18+
- **pnpm**: 8+
- **Tauri**: 2.x
- **React**: 18+
- **SQLite**: 3.x (bundled)

---

## Estimated Total Time

**4-6 hours** (excluding research and planning)

---

*Plan created: 2026-04-13*  
*Ready for execution*
