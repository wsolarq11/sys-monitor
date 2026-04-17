# Spec-Driven Development 快速参考

**版本**: 1.0.0  
**最后更新**: 2026-04-17

## 常用命令

### 验证和测试

```bash
# 验证系统设置
python .lingma/scripts/verify-setup.py

# 验证架构完整性
python .lingma/scripts/validate-architecture.py

# 验证 MCP 配置
python .lingma/scripts/verify-mcp-setup.py

# 运行性能优化器
python .lingma/scripts/performance-optimizer.py
```

### 会话管理

```bash
# 启动会话中间件（自动验证）
python .lingma/scripts/session-middleware.py

# 生成会话报告
python .lingma/scripts/session-middleware.py --report-output report.json

# 强制绕过验证（仅调试）
python .lingma/scripts/session-middleware.py --force-bypass
```

### Git Hooks

```bash
# 安装 Git Hooks
python .lingma/scripts/install-hooks.py

# 手动触发 pre-commit hook
.git/hooks/pre-commit

# 手动触发 pre-push hook
.git/hooks/pre-push
```

---

## 核心组件快速访问

### 脚本文件

| 文件 | 用途 |
|------|------|
| `session-middleware.py` | 会话验证和初始化 |
| `validate-architecture.py` | 架构完整性验证 |
| `performance-optimizer.py` | 性能分析和优化 |
| `decision_cache.py` | 决策缓存管理 |
| `batch_logger.py` | 批量日志写入 |
| `ux_improvements.py` | 用户体验改进 |
| `interactive_cli.py` | 交互式命令行 |

### 配置文件

| 文件 | 用途 |
|------|------|
| `.lingma/config/automation.json` | 自动化配置 |
| `.lingma/config/agent-config.json` | Agent 配置 |
| `.lingma/config/mcp-servers.json` | MCP 服务器配置 |

### 规则文件

| 文件 | 用途 |
|------|------|
| `automation-policy.md` | 自动化执行策略 |
| `memory-usage.md` | Memory 使用规范 |
| `spec-session-start.md` | 会话启动规则 |
| `subagent-file-creation.md` | 子代理文件创建规则 |

### 文档文件

| 文件 | 用途 |
|------|------|
| `USER_GUIDE.md` | 用户指南 |
| `DEVELOPER_GUIDE.md` | 开发者文档 |
| `BEST_PRACTICES.md` | 最佳实践 |
| `INSTALLATION_GUIDE.md` | 安装指南 |

---

## Python API 快速参考

### 决策缓存

```python
from decision_cache import get_decision_cache, cache_decision, get_cached_decision

# 获取缓存实例
cache = get_decision_cache()

# 缓存决策
operation = {"type": "file_read", "path": "/test.txt"}
result = {"strategy": "auto_execute"}
cache_decision(operation, result)

# 获取缓存
cached = get_cached_decision(operation)

# 查看统计
stats = cache.get_stats()
print(f"命中率: {stats['hit_rate_percent']}%")
```

### 批量日志

```python
from batch_logger import get_batch_logger, log_entry, flush_logs

# 记录日志
log_entry({
    'level': 'INFO',
    'message': 'Operation completed',
    'operation': 'file_read'
})

# 立即刷新
flush_logs()
```

### 进度显示

```python
from ux_improvements import create_progress

with create_progress(100, "Processing") as progress:
    for i in range(100):
        # 执行工作
        progress.update()
```

### 消息格式化

```python
from ux_improvements import get_message_formatter

formatter = get_message_formatter()

print(formatter.success("操作成功", "详细信息"))
print(formatter.warning("警告信息", "详细说明"))
print(formatter.error("错误信息", "错误详情"))
print(formatter.info("提示信息", "补充信息"))
```

### 撤销管理

```python
from ux_improvements import get_undo_manager

undo_mgr = get_undo_manager()

# 记录操作
def undo_func(details):
    print(f"撤销: {details}")

def redo_func(details):
    print(f"重做: {details}")

undo_mgr.record_action("modify", {"data": "value"}, undo_func, redo_func)

# 撤销
result = undo_mgr.undo()

# 重做
result = undo_mgr.redo()

# 查看历史
history = undo_mgr.get_history(limit=10)
```

---

## 自动化级别

### 保守模式 (Conservative)

```json
{
  "automation_level": "conservative",
  "risk_thresholds": {
    "low": 0.1,
    "medium": 0.3,
    "high": 0.6
  }
}
```

**适用场景**: 生产环境、关键操作

### 平衡模式 (Balanced) - 默认

```json
{
  "automation_level": "balanced",
  "risk_thresholds": {
    "low": 0.2,
    "medium": 0.5,
    "high": 0.8
  }
}
```

**适用场景**: 开发环境

### 激进模式 (Aggressive)

```json
{
  "automation_level": "aggressive",
  "risk_thresholds": {
    "low": 0.3,
    "medium": 0.7,
    "high": 0.9
  }
}
```

**适用场景**: 测试环境

### 完全自动 (Full Auto)

```json
{
  "automation_level": "full_auto",
  "risk_thresholds": {
    "low": 1.0,
    "medium": 1.0,
    "high": 1.0
  }
}
```

**适用场景**: 实验环境

---

## 执行策略

| 风险等级 | 策略 | 说明 |
|---------|------|------|
| 🟢 低风险 (< 0.2) | 自动执行 | 无需确认，直接执行 |
| 🟡 中风险 (0.2-0.5) | 快照后执行 | 创建 Git 快照后执行 |
| 🟠 高风险 (0.5-0.8) | 询问用户 | 需要用户确认 |
| 🔴 极高风险 (> 0.8) | 明确批准 | 需要明确同意 |

---

## 目录结构

```
.lingma/
├── agents/              # Agent 定义
├── config/              # 配置文件
├── docs/                # 文档
│   └── guides/         # 用户指南
├── hooks/               # Git Hooks
├── logs/                # 日志文件
├── reports/             # 生成的报告
├── rules/               # Rules 定义
├── scripts/             # Python 脚本
├── skills/              # Skills 定义
├── specs/               # Spec 文件
└── worker/              # Worker 进程
```

---

## 常见问题速查

### Q: 如何更改自动化级别？

编辑 `.lingma/config/automation.json`:
```json
{
  "automation_level": "conservative"
}
```

### Q: 如何清除缓存？

```bash
rm -rf .lingma/cache/
```

### Q: 如何查看操作历史？

```python
from ux_improvements import get_undo_manager
undo_mgr = get_undo_manager()
history = undo_mgr.get_history(limit=10)
```

### Q: 如何禁用学习功能？

编辑 `.lingma/config/automation.json`:
```json
{
  "learning": {
    "enabled": false
  }
}
```

### Q: 如何查看性能报告？

```bash
ls .lingma/reports/performance_report_*.json
cat .lingma/reports/performance_report_<timestamp>.json
```

### Q: Git Hook 失败怎么办？

```bash
# 重新安装
python .lingma/scripts/install-hooks.py

# 或手动修复
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
```

---

## 键盘快捷键（CLI）

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+C` | 中断当前操作 |
| `help` / `h` / `?` | 显示帮助 |
| `quit` / `exit` / `q` | 退出 CLI |
| `clear` / `cls` | 清屏 |

---

## 日志位置

| 日志类型 | 文件路径 |
|---------|---------|
| 自动化日志 | `.lingma/logs/automation.log` |
| 审计日志 | `.lingma/logs/audit.log` |
| MCP 日志 | `.lingma/logs/mcp.log` |
| 性能指标 | `.lingma/state/metrics.json` |

---

## 报告位置

| 报告类型 | 文件路径 |
|---------|---------|
| 性能报告 | `.lingma/reports/performance_report_*.json` |
| 验证报告 | `.lingma/reports/architecture-validation-*.json` |
| 完成报告 | `.lingma/reports/phase*-task*-completion.md` |

---

## 有用的链接

- **Spec 文件**: `.lingma/specs/current-spec.md`
- **Constitution**: `.lingma/specs/constitution.md`
- **用户指南**: `.lingma/docs/guides/USER_GUIDE.md`
- **开发者文档**: `.lingma/docs/guides/DEVELOPER_GUIDE.md`
- **最佳实践**: `.lingma/docs/guides/BEST_PRACTICES.md`
- **安装指南**: `.lingma/docs/guides/INSTALLATION_GUIDE.md`

---

**提示**: 将此文档加入书签，方便快速查阅！

---

**许可证**: MIT  
**维护者**: AI Assistant  
**最后更新**: 2026-04-17
