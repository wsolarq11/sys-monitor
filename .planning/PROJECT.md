# SysMonitor / SystemWatch

## What This Is

一个基于 Rust + Tauri v2 构建的跨平台桌面系统监控应用，提供实时监控、历史记录、告警通知和数据导出功能。通过现代化的 GUI 界面展示系统资源、磁盘使用、网络状态和日志信息。

**当前版本**: v0.1.0 ✅ (已发布)

---

## Core Value

为用户提供直观、可靠的系统健康状态全景视图，在问题发生前及时发现异常趋势。

---

## Requirements

### Validated (v0.1.0)

- [x] 系统资源监控 - CPU、内存、磁盘使用率实时采集和展示
- [x] 磁盘/文件夹大小监控 - 文件夹大小分析、磁盘空间趋势追踪
- [x] 实时监控界面 - Tauri v2 + React 构建的响应式 GUI
- [x] 历史数据存储 - SQLite 数据库存储时间序列监控数据

### Active (v0.2.0)

- [ ] 网络监控 - 网络流量、连接状态、带宽使用监控
- [ ] 告警通知系统 - 阈值配置和超限通知
- [ ] 数据导出功能 - 支持 CSV/JSON 格式导出监控数据
- [ ] 可配置性 - 监控项、采集频率、告警阈值的自定义配置

### Out of Scope

- 移动端支持 — 专注于桌面平台
- 云端同步 — 本地单机应用
- 远程控制 — 仅监控，无控制功能
- 日志监控 — 延期至 v0.3.0

---

## Context

**技术栈选择：**
- 后端：Rust (系统监控、数据采集)
- 前端：Tauri v2 + React (GUI 界面)
- 数据库：SQLite (rusqlite) - 成熟稳定，支持复杂查询和历史数据分析
- 跨平台：Windows、Linux、macOS

**架构决策：**
- 使用 Tauri v2 而非 Electron：更小的二进制体积、更好的性能、原生系统 API 访问
- 使用 SQLite 而非纯 Rust 数据库：需要 SQL 查询能力进行历史数据分析和报表生成
- 监控频率可配置：用户可根据需求平衡性能和实时性

**设计原则：**
- 用户体验优先：界面美观、响应流畅
- 功能可靠性：数据准确、监控可靠、告警及时
- 代码质量：架构清晰、易于扩展

---

## Constraints

- **技术栈**: Rust + Tauri v2 + React — 用户明确选择
- **数据库**: SQLite — 需要复杂查询和历史数据分析能力
- **跨平台**: Windows、Linux、macOS — Tauri v2 原生支持
- **性能**: 监控采集不应显著影响系统性能

---

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 使用 Tauri v2 构建 GUI | 纯 Rust 生态、小体积、高性能、原生 API 访问 | ✅ 成功 - v0.1.0 已发布 |
| 使用 SQLite 存储历史数据 | 成熟稳定、SQL 查询能力、适合数据分析场景 | ✅ 成功 - 已集成 |
| 全功能监控（系统/磁盘/网络/日志） | 提供系统健康全景视图，而非单一功能 | ⚠️ 部分实现 - 网络监控延期至 v0.2.0 |
| 可配置监控频率 | 适应不同使用场景和性能需求 | ✅ 已实现 - 1秒轮询 |

---

## Current State (v0.1.0)

**已发布功能**:
- ✅ 系统资源监控 (CPU、内存、磁盘)
- ✅ 文件夹分析 (扫描、文件类型统计、历史记录)
- ✅ 实时仪表板 (React + Tauri)
- ✅ SQLite 数据持久化
- ✅ 36个测试 (100% 通过率)
- ✅ Windows 构建 (EXE + MSI)

**已知限制**:
- 网络监控未实现 (sysinfo 0.30+ API 变更)
- 告警系统未实现
- 日志监控未实现
- 仅支持 Windows (Linux/macOS 构建未测试)

---

## Next Milestone Goals (v0.2.0)

1. **网络监控** - 重写以适配 sysinfo 0.30+
2. **告警系统** - 阈值配置和桌面通知
3. **数据导出** - CSV/JSON 导出功能
4. **配置界面** - 用户可配置监控参数

---

## Evolution

This document evolves at phase transitions and milestone boundaries.

**v0.1.0 里程碑完成更新 (2026-04-14)**:
- 将已验证需求移至 Validated 区域
- 更新技术决策 outcomes
- 添加 Current State 章节
- 定义 Next Milestone Goals

---

*Last updated: 2026-04-14 after v0.1.0 milestone completion*
