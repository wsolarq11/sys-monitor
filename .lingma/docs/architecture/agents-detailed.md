# AGENTS.md 详细指南

**版本**: v1.0  
**最后更新**: 2026-04-15  
**关联 Rule**: `.lingma/rules/AGENTS.md`

---

## 📋 Rules 优先级详细说明

### P0 - 最高优先级（必须遵循）

1. **AGENTS.md** - 自我演进规则
   - 包含系统级约束和元规则
   - 任何情况下都必须遵循

2. **spec-session-start.md** - 会话启动规则
   - 定义每次会话的初始化流程
   - 确保 Spec 状态检查

### P1 - 高优先级（重要约束）

3. **automation-policy.md** - 自动化执行策略
   - 定义风险等级和执行策略
   - 决定操作的自动化程度

4. **memory-usage.md** - Memory 使用规范
   - 定义何时创建/更新/删除记忆
   - 规范 Memory 管理操作

### P2 - 中优先级（指导性规则）

5. **其他自定义 Rules**
   - 项目特定的规范
   - 团队约定的最佳实践

---

## 🔧 冲突解决原则

### 1. 高优先级覆盖低优先级
- 如果 P0 和 P1 冲突，遵循 P0
- 如果 P1 和 P2 冲突，遵循 P1

### 2. 同优先级取最严格
- 如果两个 P1 Rules 冲突，选择更严格的约束
- 示例：一个 Rule 说"可以自动执行"，另一个说"需要询问"，则选择"需要询问"

### 3. 特殊场景例外
- 如果用户明确要求违反某个 Rule，遵循用户意愿
- 但必须记录到 Memory 和 Spec 实施笔记

---

## 💻 编码与路径规则

### UTF-8 无 BOM
数据文件强制 UTF‑8 无 BOM。  
读：`[System.IO.File]::ReadAllText($Path, [System.Text.UTF8Encoding]::new($false))`  
写：`[System.IO.File]::WriteAllText($Path, $Content, [System.Text.UTF8Encoding]::new($false))`  
遇 BOM `EF BB BF` 即 `exit 96`。

### 路径解析
路径解析用 `$PSCmdlet.GetUnresolvedProviderPathFromPSPath($p)`，可处理不存在路径，交 .NET 前 `Convert-Path`。

### Git 配置
```
text=auto
*.bat text eol=crlf
```

---

## 🚪 退出码标准

| 范围 | 含义 | 示例 |
|------|------|------|
| 0 | 成功 | - |
| 32-63 | 环境错误 | 缺少依赖 |
| 64-95 | 执行错误 | 命令失败 |
| 96-127 | 数据错误 | BOM 检测 |
| 128+ | 信号中断 | Ctrl+C |

**要求**: 退出前须写 `.exit_code` 文件。

---

## 📝 审计与闭环

### 日志格式
日志为 JSON 行，字段：
- `timestamp` (ISO UTC)
- `level` (INFO/WARN/ERROR)
- `trace_id` (UUID v4)
- `action` (操作名称)
- `result` (结果)
- `exit_code` (失败必填)

### 任务启动
任务启动时若缺 `TRACE_ID` 则生成注入，并写 `INFO` 日志(`action=task_start`)。

### 阻断前落盘
阻断前落盘：ERROR 审计日志与 `.exit_code` 文件。致命错误另存 `error_<timestamp>.log`。证据完备方可退出。

---

## 🐚 Shell 约束

### Bash (.sh)
- 首行 `set -euo pipefail`
- 管道内显式启用 `set -e`（如 `set -e; cmd1 | cmd2`）
- 命令替换内显式捕获错误

### PowerShell (.ps1)
- 首行 `$ErrorActionPreference = 'Stop'`
- 每条外部命令后须 `if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }`

### 错误流
错误流保持独立，使用 `2>` 或 `2>>` 定向至日志。

### 跨平台
跨平台脚本引用用户目录优先使用 `$env:USERPROFILE`（Win）与 `$HOME`（Unix）。

---

## 🛠️ 策略与修复

### 环境错误修复
遇环境错误(32-63)执行根因修复，保持终端与步骤连续性。临时修复写入 `.known_issues.md` 并记 `WARN` 日志，触发后续工单。

### 关键文件落盘
落盘关键文件遵循：临时文件写入 → 绕过缓存刷盘 → 系统级原子重命名。

---

## 🔗 相关资源

- [精简版 Rule](../../rules/AGENTS.md)
- [使命宣言](../MISSION_STATEMENT.md)
- [验证指南](../guides/verification-guide.md)

---

**注意**: 此文档包含详细的实现指南和规范，不应放入 Rule 文件中。Rule 文件应保持简洁（≤5KB，作为核心Rule的特殊例外），仅包含核心指令和引用链接。
