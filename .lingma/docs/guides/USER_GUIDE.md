# Spec-Driven Development 用户指南

**版本**: 1.0.0  
**最后更新**: 2026-04-17

## 目录

1. [简介](#简介)
2. [快速开始](#快速开始)
3. [核心概念](#核心概念)
4. [使用工作流](#使用工作流)
5. [命令参考](#命令参考)
6. [配置说明](#配置说明)
7. [常见问题](#常见问题)
8. [故障排除](#故障排除)

---

## 简介

Spec-Driven Development (SDD) 是一个基于规格说明的自动化开发系统，旨在提高开发效率、减少人工干预、降低出错率。

### 主要特性

- ✅ **自动化决策**: 智能风险评估，自动选择执行策略
- ✅ **进度跟踪**: 实时显示任务进度和预计完成时间
- ✅ **撤销/重做**: 完整的操作历史管理
- ✅ **性能优化**: 决策缓存、批量日志写入
- ✅ **友好交互**: 统一的命令行界面和消息格式化

### 系统架构

```
用户界面层
    ↓
智能决策引擎
    ↓
自动化执行层
    ↓
MCP 工具层
    ↓
学习与优化
```

---

## 快速开始

### 前置条件

- Python 3.10+
- Node.js 18+ (用于 MCP)
- Git 已配置

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd FolderSizeMonitor
   ```

2. **安装依赖**
   ```bash
   pip install psutil
   ```

3. **验证安装**
   ```bash
   python .lingma/scripts/verify-setup.py
   ```

### 首次使用

1. **检查 Spec 状态**
   ```bash
   python .lingma/scripts/session-middleware.py
   ```

2. **查看当前进度**
   ```bash
   cat .lingma/specs/current-spec.md
   ```

3. **开始开发**
   - 系统会自动加载 Spec 并继续下一个任务
   - 如需手动干预，使用交互式 CLI

---

## 核心概念

### Spec (规格说明)

Spec 是项目的核心文档，定义了：
- 背景与目标
- 功能性需求
- 非功能性需求
- 技术方案
- 实施计划
- 测试策略

文件位置: `.lingma/specs/current-spec.md`

### 任务 (Tasks)

任务是 Spec 中的具体工作单元，每个任务包括：
- 任务描述
- 验收标准
- 预计时间
- 完成状态

### 自动化级别

系统支持四种自动化级别：

| 级别 | 风险阈值 | 适用场景 |
|------|---------|---------|
| 保守 (Conservative) | 0.1 / 0.3 / 0.6 | 生产环境、关键操作 |
| 平衡 (Balanced) | 0.2 / 0.5 / 0.8 | 开发环境（默认） |
| 激进 (Aggressive) | 0.3 / 0.7 / 0.9 | 实验环境 |
| 完全自动 (Full Auto) | 1.0 / 1.0 / 1.0 | 测试环境 |

### 执行策略

根据风险评估，系统会选择不同的执行策略：

- 🟢 **自动执行**: 低风险操作，无需确认
- 🟡 **快照后执行**: 中风险操作，创建 Git 快照
- 🟠 **询问用户**: 高风险操作，需要用户确认
- 🔴 **明确批准**: 极高风险操作，需要明确同意

---

## 使用工作流

### 标准开发流程

1. **会话启动**
   - 系统自动检查 Spec 状态
   - 验证环境完整性
   - 加载上下文和配置

2. **任务执行**
   - 评估操作风险
   - 选择执行策略
   - 执行任务
   - 记录操作日志

3. **进度更新**
   - 更新 Spec 中的任务状态
   - 添加实施笔记
   - 生成进度报告

4. **验证与提交**
   - 运行测试
   - 验证功能
   - 提交代码

### 示例：创建新功能

```bash
# 1. 查看当前 Spec 状态
python .lingma/scripts/session-middleware.py

# 2. 系统会自动识别下一个任务并开始执行
# 如果需要手动控制，使用交互式 CLI
python .lingma/scripts/interactive_cli.py

# 3. 在 CLI 中执行命令
spec-driven> status
spec-driven> help
spec-driven> quit
```

### 示例：撤销操作

```python
from ux_improvements import get_undo_manager

undo_mgr = get_undo_manager()

# 撤销最后一个操作
result = undo_mgr.undo()
if result:
    print(f"已撤销: {result['action_type']}")

# 重做
result = undo_mgr.redo()
if result:
    print(f"已重做: {result['action_type']}")
```

### 示例：显示进度

```python
from ux_improvements import create_progress
import time

with create_progress(100, "处理数据") as progress:
    for i in range(100):
        # 执行实际工作
        time.sleep(0.01)
        progress.update()
```

---

## 命令参考

### 会话中间件

```bash
# 基本用法
python .lingma/scripts/session-middleware.py

# 生成报告
python .lingma/scripts/session-middleware.py --report-output report.json

# 强制绕过验证（仅调试用）
python .lingma/scripts/session-middleware.py --force-bypass
```

### 性能优化器

```bash
# 运行性能优化
python .lingma/scripts/performance-optimizer.py

# 查看性能报告
cat .lingma/reports/performance_report_*.json
```

### UX 演示

```bash
# 运行 UX 功能演示
python .lingma/scripts/ux_demo.py
```

### 验证脚本

```bash
# 验证系统设置
python .lingma/scripts/verify-setup.py

# 验证 MCP 配置
python .lingma/scripts/verify-mcp-setup.py
```

---

## 配置说明

### 自动化配置

文件: `.lingma/config/automation.json`

```json
{
  "automation_level": "balanced",
  "risk_thresholds": {
    "low": 0.2,
    "medium": 0.5,
    "high": 0.8
  },
  "learning": {
    "enabled": true,
    "learning_rate": 0.1
  }
}
```

### MCP 服务器配置

文件: `.lingma/config/mcp-servers.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "enabled": true
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "enabled": true
    },
    "shell": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-shell"],
      "enabled": false
    }
  }
}
```

### Agent 配置

文件: `.lingma/config/agent-config.json`

```json
{
  "agent_name": "SpecDrivenAgent",
  "version": "1.0.0",
  "skills": ["spec-driven-development", "memory-management"],
  "rules": ["automation-policy", "memory-usage", "subagent-file-creation"]
}
```

---

## 常见问题

### Q1: 如何更改自动化级别？

编辑 `.lingma/config/automation.json` 文件，修改 `automation_level` 字段：

```json
{
  "automation_level": "conservative"  // 或 "balanced", "aggressive", "full_auto"
}
```

### Q2: 如何查看操作历史？

```python
from ux_improvements import get_undo_manager

undo_mgr = get_undo_manager()
history = undo_mgr.get_history(limit=10)
for entry in history:
    print(f"{entry['timestamp']}: {entry['action_type']}")
```

### Q3: 如何清除缓存？

```bash
# 删除缓存目录
rm -rf .lingma/cache/

# 或使用 Python
from decision_cache import get_decision_cache
cache = get_decision_cache()
cache.clear_expired()
```

### Q4: 系统提示 "Spec 文件缺失" 怎么办？

1. 检查 `.lingma/specs/current-spec.md` 是否存在
2. 如果不存在，从备份恢复或创建新的 Spec
3. 运行验证脚本: `python .lingma/scripts/verify-setup.py`

### Q5: 如何禁用学习功能？

编辑 `.lingma/config/automation.json`:

```json
{
  "learning": {
    "enabled": false
  }
}
```

---

## 故障排除

### 问题 1: 模块导入错误

**症状**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:
```bash
# 确保在正确的目录
cd d:\Users\Administrator\Desktop\PowerShell_Script_Repository\FolderSizeMonitor

# 安装依赖
pip install psutil

# 检查 Python 路径
python -c "import sys; print(sys.path)"
```

### 问题 2: 性能下降

**症状**: 决策延迟超过 100ms

**解决方案**:
1. 运行性能分析: `python .lingma/scripts/performance-optimizer.py`
2. 检查缓存是否正常工作
3. 清理过期缓存: `rm -rf .lingma/cache/`
4. 重启系统

### 问题 3: 日志文件过大

**症状**: `.lingma/logs/automation.log` 文件过大

**解决方案**:
```bash
# 归档旧日志
mv .lingma/logs/automation.log .lingma/logs/automation.log.bak

# 系统会自动创建新日志文件
```

### 问题 4: Git Hook 失败

**症状**: Git 提交时 Hook 报错

**解决方案**:
```bash
# 重新安装 Hook
python .lingma/scripts/install-hooks.py

# 或手动修复
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
```

### 问题 5: MCP 服务器无法启动

**症状**: MCP 连接失败

**解决方案**:
1. 检查 Node.js 版本: `node --version` (需要 18+)
2. 检查 npm 版本: `npm --version`
3. 验证配置: `python .lingma/scripts/verify-mcp-setup.py`
4. 查看日志: `cat .lingma/logs/mcp.log`

---

## 获取帮助

- **文档**: `.lingma/docs/` 目录
- **报告**: `.lingma/reports/` 目录
- **日志**: `.lingma/logs/` 目录
- **Spec**: `.lingma/specs/current-spec.md`

## 贡献指南

欢迎贡献代码、文档或建议！

1. Fork 仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

---

**许可证**: MIT  
**维护者**: AI Assistant  
**最后更新**: 2026-04-17
