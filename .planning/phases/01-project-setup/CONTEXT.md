# Phase 1 Context: Project Setup

**Phase**: 1 - Project Setup  
**Created**: 2026-04-13  
**Status**: Ready for planning

---

## Decisions from Prior Context

### Technology Stack (from PROJECT.md)
- **Backend**: Rust (latest stable)
- **Frontend**: Tauri v2 + React 18+
- **Database**: SQLite (rusqlite crate)
- **Platforms**: Windows, Linux, macOS

### Project Structure Decision
- Single Rust workspace with Tauri v2 application
- React frontend in `src-tauri/src` for Rust code, `src/` for React code
- SQLite database file stored in user data directory

### Development Workflow
- **Package Manager**: pnpm for frontend, cargo for Rust
- **Development Mode**: `pnpm tauri dev` for hot reload
- **Build**: `pnpm tauri build` for production builds
- **Testing**: cargo test for Rust, vitest/jest for React (TBD)

### Cross-platform Considerations
- Windows: Primary development platform (current working directory)
- Linux: Ubuntu/Debian focus for testing
- macOS: Intel and Apple Silicon support

---

## Phase 1 Scope (from ROADMAP.md)

**Goal**: Initialize Rust + Tauri v2 project structure

**Must deliver**:
1. Create Rust workspace with Tauri v2
2. Configure React frontend scaffold
3. Setup SQLite integration (rusqlite)
4. Configure cross-platform build settings
5. Establish development workflow

---

## Technical Decisions for Planning

### Tauri v2 Configuration
- Use `create-tauri-app` with React template as starting point
- Configure `tauri.conf.json` for cross-platform builds
- Enable system tray (optional, for future monitoring features)
- Configure CSP (Content Security Policy) for security

### Rust Dependencies (planned)
- `tauri` v2.x - Core framework
- `rusqlite` - SQLite bindings
- `sysinfo` - System information (CPU, memory, disk)
- `tokio` - Async runtime (if needed by Tauri)
- `serde` + `serde_json` - Serialization
- `thiserror` - Error handling

### React Dependencies (planned)
- `react` 18+ - UI framework
- `tauri-api` - Tauri frontend API
- UI library: TBD (recommend shadcn/ui or Mantine for modern look)
- State management: TBD (Zustand or Context API for simplicity)
- Charts: `recharts` for data visualization

### SQLite Schema (initial)
- Single database file in user data directory
- Tables for:
  - `system_metrics` - CPU, memory, disk usage over time
  - `network_metrics` - Network traffic data
  - `alerts` - Alert history
  - `settings` - User configuration

### Project Structure
```
SysMonitor/
├── src-tauri/
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   ├── src/
│   │   ├── main.rs
│   │   ├── lib.rs
│   │   ├── commands/
│   │   │   ├── system.rs
│   │   │   ├── disk.rs
│   │   │   ├── network.rs
│   │   │   └── mod.rs
│   │   ├── db/
│   │   │   ├── schema.rs
│   │   │   ├── repository.rs
│   │   │   └── mod.rs
│   │   └── error.rs
│   ├── icons/
│   │   └── icon.ico
│   └── build.rs
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── components/
│   │   ├── Dashboard/
│   │   ├── SystemMonitor/
│   │   └── common/
│   ├── hooks/
│   ├── stores/
│   └── styles/
├── package.json
├── tsconfig.json
└── .gitignore
```

---

## Open Questions for Planning Agent

1. **UI Library Choice**: Which React UI library provides best balance of looks/performance/size?
2. **State Management**: Simple enough for monitoring app - Context API or lightweight store?
3. **Database Location**: Platform-specific paths for SQLite file storage
4. **Permissions**: What system permissions needed for monitoring on each platform?

---

## Research Topics

1. Tauri v2 migration guide and best practices (vs v1)
2. System monitoring libraries for Rust (sysinfo vs alternatives)
3. SQLite performance optimization for time-series data
4. Cross-platform system API access patterns

---

*Last updated: 2026-04-13 after initialization*
