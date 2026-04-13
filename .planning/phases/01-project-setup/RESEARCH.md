# Phase 1 Research: Tauri v2 + Rust Project Setup

**Phase**: 1 - Project Setup  
**Research Date**: 2026-04-13  
**Status**: Complete

---

## Tauri v2 Overview

### What's New in Tauri v2

Tauri v2 represents a major evolution with:

1. **Multiwindow Support** - Native multiwindow capabilities
2. **Mobile Support** - iOS and Android (beta)
3. **Improved Permissions** - Granular capability-based security
4. **Better TypeScript Types** - Enhanced type safety
5. **Plugin System 2.0** - More modular architecture
6. **Performance Improvements** - Smaller binaries, faster startup

### Migration Considerations (v1 → v2)

Key breaking changes:
- `tauri.conf.json` structure updated
- Plugin registration syntax changed
- IPC layer improvements
- New permission system (capabilities)

**Recommendation**: Start fresh with v2 template rather than migrating.

---

## Project Initialization Options

### Option 1: create-tauri-app (Recommended)

```bash
pnpm create tauri-app@latest
# or
npm create tauri-app@latest
# or
cargo install create-tauri-app
```

**Pros**:
- Official scaffolding tool
- Latest best practices baked in
- Choice of frontend framework (React, Vue, Svelte, etc.)
- TypeScript support out of the box

**Cons**:
- Basic setup only, need to add domain-specific code

### Option 2: Manual Setup

```bash
cargo init
cargo add tauri
```

**Pros**:
- Full control over structure
- Learn the internals

**Cons**:
- More error-prone
- Need to configure everything manually

**Decision**: Use `create-tauri-app` with React + TypeScript template.

---

## System Information Libraries for Rust

### sysinfo (Recommended)

**Repository**: https://github.com/GuillaumeGomez/sysinfo

**Features**:
- CPU usage (total and per-core)
- Memory usage
- Process information
- Disk usage
- Network interfaces
- Component temperatures

**API Example**:
```rust
use sysinfo::{System, SystemExt};

let mut sys = System::new_all();
sys.refresh_all();

println!("CPU usage: {}%", sys.global_cpu_usage());
println!("Memory: {} / {}", sys.used_memory(), sys.total_memory());
```

**Pros**:
- Cross-platform (Windows, Linux, macOS)
- Actively maintained
- Good performance
- Comprehensive API

**Cons**:
- Some platform-specific limitations
- Network monitoring limited to interface list (not traffic)

### Alternative: heim

**Repository**: https://github.com/heim-rs/heim

**Features**: Similar to sysinfo, with async-first design

**Decision**: Use `sysinfo` for simplicity and maturity. Add `heim` only if async needed.

---

## SQLite Integration

### rusqlite (Recommended)

**Repository**: https://github.com/rusqlite/rusqlite

**Features**:
- Bindings to SQLite3
- Optional bundled SQLite (bundled feature)
- Async support via tokio
- Connection pooling via r2d2

**API Example**:
```rust
use rusqlite::{Connection, Result};

fn create_table(conn: &Connection) -> Result<()> {
    conn.execute(
        "CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY,
            timestamp INTEGER NOT NULL,
            cpu_usage REAL,
            memory_usage REAL,
            disk_usage REAL
        )",
        [],
    )?;
    Ok(())
}
```

**Pros**:
- Mature and stable
- Well-documented
- Good performance
- Optional bundled SQLite simplifies cross-platform builds

**Cons**:
- Synchronous by default (async requires extra work)

### Alternative: sqlx with SQLite

**Decision**: Use `rusqlite` with `bundled` feature for simplicity. Can migrate to `sqlx` if async becomes critical.

---

## Cross-platform Build Configuration

### Windows

**Requirements**:
- Visual Studio Build Tools 2019+ or Visual Studio 2019+
- WebView2 (included in Windows 10 1803+)

**Build Command**:
```bash
pnpm tauri build
```

**Output**: MSI installer or portable executable

### Linux

**Requirements**:
- GCC/Clang
- libwebkit2gtk-4.0-dev (or -4.1-dev)
- libgtk-3-dev
- libayatana-appindicator3-dev (for system tray)

**Debian/Ubuntu**:
```bash
sudo apt install libwebkit2gtk-4.0-dev build-essential libssl-dev \
  libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev
```

**Build Command**:
```bash
pnpm tauri build
```

**Output**: AppImage, Debian package, or RPM

### macOS

**Requirements**:
- Xcode Command Line Tools
- macOS 10.15+

**Build Command**:
```bash
pnpm tauri build
```

**Output**: .app bundle or DMG

**Code Signing**: Required for distribution outside App Store

---

## Recommended Project Structure

Based on analysis of production Tauri apps:

```
SysMonitor/
├── .gitignore
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── src-tauri/
│   ├── Cargo.toml
│   ├── Cargo.lock
│   ├── tauri.conf.json
│   ├── tauri.windows.conf.json (optional overrides)
│   ├── tauri.linux.conf.json (optional overrides)
│   ├── tauri.macos.conf.json (optional overrides)
│   ├── build.rs
│   ├── icons/
│   │   ├── icon.ico
│   │   ├── icon.icns
│   │   └── icon.png
│   └── src/
│       ├── main.rs - Application entry point
│       ├── lib.rs - Tauri commands
│       ├── app.rs - Tauri app configuration
│       ├── commands/
│       │   ├── mod.rs
│       │   ├── system.rs - System monitoring commands
│       │   ├── disk.rs - Disk monitoring commands
│       │   ├── network.rs - Network monitoring commands
│       │   └── database.rs - Database commands
│       ├── db/
│       │   ├── mod.rs
│       │   ├── schema.rs - Database schema
│       │   ├── repository.rs - Data access layer
│       │   └── migrations.rs - Schema migrations
│       ├── models/
│       │   ├── mod.rs
│       │   ├── metrics.rs - Data models
│       │   └── config.rs - Configuration models
│       └── error.rs - Error types
└── src/
    ├── main.tsx - React entry point
    ├── App.tsx - Root component
    ├── index.css - Global styles
    ├── vite-env.d.ts
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
    │       ├── Chart.tsx
    │       └── Layout.tsx
    ├── hooks/
    │   ├── useSystemMetrics.ts
    │   └── useDatabase.ts
    ├── stores/
    │   └── metricsStore.ts
    └── utils/
        └── format.ts
```

---

## Development Workflow

### Initial Setup

```bash
# Create Tauri app
pnpm create tauri-app@latest sys-monitor --template react-ts

cd sys-monitor

# Install dependencies
pnpm install

# Add Rust dependencies
cd src-tauri
cargo add sysinfo rusqlite --features bundled
cargo add serde serde_json thiserror tokio
```

### Development

```bash
# Start development server (hot reload)
pnpm tauri dev

# Run tests
cd src-tauri && cargo test
pnpm test
```

### Production Build

```bash
pnpm tauri build
```

---

## Potential Gotchas

### 1. WebView2 on Windows

Windows 10 1803+ includes WebView2. For older Windows, need to bundle or prompt for installation.

**Mitigation**: Use Tauri's WebView2 bootstrapper or require Windows 10 1803+.

### 2. Linux Dependencies

Linux builds fail without proper dependencies installed.

**Mitigation**: Document dependencies clearly. Consider providing Docker build environment.

### 3. macOS Code Signing

Required for distribution outside App Store.

**Mitigation**: Can skip for development. Purchase Apple Developer account ($99/year) for distribution.

### 4. SQLite Performance

Time-series data can grow quickly.

**Mitigation**: 
- Implement data retention policies from day one
- Use indexed queries
- Consider data aggregation (hourly/daily summaries)

### 5. System Permission Requirements

Monitoring apps may need elevated permissions on some platforms.

**Mitigation**: 
- Test on all platforms early
- Document permission requirements
- Gracefully degrade when permissions unavailable

---

## Recommendations Summary

### Dependencies

**Rust** (`src-tauri/Cargo.toml`):
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

**React** (`package.json`):
```json
{
  "dependencies": {
    "react": "^18",
    "react-dom": "^18",
    "@tauri-apps/api": "^2"
  },
  "devDependencies": {
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "typescript": "^5",
    "vite": "^5",
    "tailwindcss": "^3",
    "recharts": "^2"
  }
}
```

### UI Library

**Recommendation**: Start with Tailwind CSS + shadcn/ui for modern, performant UI.

**Rationale**:
- Small bundle size
- Good performance
- Modern design
- Easy customization

### State Management

**Recommendation**: Zustand for simplicity.

**Rationale**:
- Minimal boilerplate
- Good TypeScript support
- Devtools support
- Works well with Tauri

---

## Next Steps

1. Create project with `create-tauri-app`
2. Add Rust dependencies
3. Configure SQLite schema
4. Setup basic system monitoring commands
5. Create React component structure
6. Implement data flow (Rust → React)

---

*Research completed: 2026-04-13*
