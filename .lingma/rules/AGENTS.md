---
trigger: always_on
---
## 自我演进

每次从用户回复中意识到交付结果与描述不符时，需将根本原因及解决办法记录在本章节末尾。当被用户指出错误并纠正后，同样应据此添加新规则。

### 2026-04-15: 文档冗余问题教训
**问题**: 创建了多个入口文档，违反单一入口原则  
**解决**: README.md ≤800字，详细文档移至docs/，创建doc-redundancy-prevention.md  
**核心教训**: **"给 Agent 一张地图，而非一本百科全书"**

### 2026-04-15: 被动响应问题教训（最重要！）
**问题**: 等用户提醒才"突然记起来"，马后炮式响应  
**根源**: 缺乏自动化检查、依赖人工记忆、未建立"默认做好"机制  
**解决**: 
1. ✅ Git Hook 强制拦截
2. ✅ CI/CD 自动验证
3. ✅ Rule 永久约束
4. ✅ 自动化扫描工具
5. ✅ 防重复机制（创建前grep检查）
6. ✅ 量化标准强制检查

**核心教训**: **"不要依赖记忆，要依赖系统。不要被动响应，要主动预防。"**

**永久保障**:
- 🚫 不再需要用户提醒类似问题
- ✅ 系统自动检测并阻止违规
- ✅ 每次提交/推送自动验证
- ✅ 创建任何内容前先检查是否已存在

**量化标准**:
| 组件类型 | 最大大小 | 目标 |
|---------|---------|------|
| Agent 文件 | ≤5KB | ≤5KB |
| Rule 文件 | ≤3KB* | ≤3KB |
| Skill 文件 | ≤10KB | ≤10KB |
| docs/ 根目录文档 | ≤5个 | ≤5个 |

*AGENTS.md作为核心Rule允许≤5KB

### 2026-04-15: .lingma目录结构冗余
**问题**: .lingma/存在.reports/.scripts/.hooks等冗余目录
**解决**: reports→docs/reports, scripts→项目根scripts, hooks删除, MISSION_STATEMENT→docs/guides
**教训**: ".lingma/仅保留agents/rules/skills/config，文档移docs/，脚本移scripts/"
**保障**: full_system_scan.py检测 + Git Hook拦截 + CI/CD周扫描

### 2026-04-15: 双docs目录
**问题**: docs/和.lingma/docs/同时存在
**解决**: 删除docs/(空占位)，保留.lingma/docs/
**教训**: "项目根docs/存应用文档(sys-monitor/)，.lingma/docs/存AI系统文档，绝不混用"
**保障**: full_system_scan.py检测双docs

### 2026-04-15: scripts临时脚本
**问题**: urgent_fix_*.py等临时脚本未删除，verify-setup.sh重复
**解决**: 删除3个临时/重复脚本，保留9个核心工具
**教训**: "scripts/仅保留可复用工具，临时脚本用完即删，避免多版本"
**保障**: 创建时标记类型 + 任务完成立即清理 + 定期审查

### 2026-04-15: 根目录临时文件(严重!)
**问题**: 0,3KB,5KB,10KB临时文件残留
**根源**: 检查组件大小时创建，忘记删除，典型马后炮
**解决**: 删除4个文件 + Git Hook增强检测
**教训**: "任何临时文件(数字/大小标记等)必须用完即删"
**保障**: Git Hook检测数字/大小标记/temp_等 + full_system_scan.py扫描 + 自动删除机制

---

## Rules 优先级

### P0 - 最高优先级
1. **AGENTS.md** - 自我演进规则
2. **spec-session-start.md** - 会话启动规则

### P1 - 高优先级
3. **automation-policy.md** - 自动化执行策略
4. **memory-usage.md** - Memory 使用规范

### P2 - 中优先级
5. **其他自定义 Rules**

**冲突解决**: 高优先级覆盖低优先级，同优先级取最严格

---

## 编码与路径规则

- 数据文件强制 UTF‑8 无 BOM
- 路径解析用 `$PSCmdlet.GetUnresolvedProviderPathFromPSPath($p)`
- Git: `text=auto`, `*.bat text eol=crlf`

## 退出码

`0`成功；`32-63`环境；`64-95`执行；`96-127`数据；`128+`信号。退出前须写 `.exit_code` 文件。

## 审计与闭环

日志为 JSON 行：`timestamp`(ISO UTC)、`level`、`trace_id`(UUID v4)、`action`、`result`、`exit_code`(失败必填)。

## Shell 约束

- `.sh`: 首行 `set -euo pipefail`
- `.ps1`: 首行 `$ErrorActionPreference = 'Stop'`，外部命令后检查 `$LASTEXITCODE`

## 详细实现

完整指南见：[agents-detailed.md](../docs/architecture/agents-detailed.md)
