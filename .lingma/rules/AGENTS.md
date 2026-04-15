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

### 2026-04-15: .lingma目录结构冗余教训
**问题**: .lingma/ 根目录存在多个冗余子目录和文件，违反单一入口原则
**根源**: 
- 创建了 .lingma/reports/ (36个报告) 而非使用 .lingma/docs/reports/
- 创建了 .lingma/scripts/ (6个脚本) 而非使用项目根目录 scripts/
- 创建了 .lingma/hooks/ (冗余pre-commit) 而非仅使用 .git/hooks/
- .lingma/ 根目录放置 MISSION_STATEMENT.md
- .lingma/skills/ 根目录放置3个.md文件而非子目录结构
- skills子目录包含额外文档(INSTALLATION_GUIDE.md等)

**解决**: 
1. ✅ .lingma/reports/ → .lingma/docs/reports/archive/
2. ✅ .lingma/scripts/ → scripts/
3. ✅ .lingma/hooks/ → 删除（Git Hook仅在.git/hooks/生效）
4. ✅ .lingma/MISSION_STATEMENT.md → .lingma/docs/guides/
5. ✅ .lingma/backups/README.md → .lingma/docs/reports/archive/
6. ✅ .lingma/skills/*.md → .lingma/docs/skills/
7. ✅ skills子目录额外文档 → docs/skills/

**核心教训**: **".lingma/ 仅保留核心组件(agents/rules/skills/config)，所有文档移至docs/，所有脚本移至scripts/"**

**永久保障**:
- ✅ full_system_scan.py 自动检测.lingma/目录结构
- ✅ Git Hook 阻止不规范的文件放置
- ✅ CI/CD 每周扫描冗余
- ✅ 创建任何新目录前先检查是否已存在类似目录

### 2026-04-15: 双docs目录冗余教训
**问题**: 同时存在 `docs/` (项目根目录) 和 `.lingma/docs/`，造成混淆
**根源**: 
- 创建了 `docs/architecture/agent-system/` 等.lingma系统文档
- 应该在 `.lingma/docs/architecture/` 中
- 违反了目录职责分离原则

**解决**: 
1. ✅ 删除 `docs/` (仅包含空占位文件)
2. ✅ 保留 `.lingma/docs/` (完整的.lingma文档)
3. ✅ 明确职责：项目根目录docs/用于应用代码，.lingma/docs/用于AI系统

**核心教训**: **"项目根目录docs/存放应用代码文档(sys-monitor/)，.lingma/docs/存放.lingma系统文档，绝不混用"**

**永久保障**:
- ✅ full_system_scan.py 检测双docs目录
- ✅ 创建目录时明确归属

### 2026-04-15: scripts目录临时脚本冗余教训
**问题**: scripts/ 目录包含多个一次性临时脚本，造成混乱
**根源**: 
- 创建了 urgent_fix_rules.py、final_fix_all.py 等临时脚本
- 任务完成后未删除
- verify-setup.sh 和 verify-setup.py 功能重复

**解决**: 
1. ✅ 删除 urgent_fix_rules.py (临时脚本)
2. ✅ 删除 final_fix_all.py (临时脚本)
3. ✅ 删除 verify-setup.sh (与Python版本重复)
4. ✅ 保留9个核心可复用脚本

**核心教训**: **"scripts/ 仅保留可复用的工具脚本，一次性临时脚本用完即删，避免同一功能的多个版本"**

**永久保障**:
- ✅ 创建脚本时明确是否为临时脚本
- ✅ 任务完成后立即清理临时脚本
- ✅ 定期审查scripts/目录，删除过时脚本

### 2026-04-15: 项目根目录临时文件冗余教训（严重！）
**问题**: 项目根目录出现4个临时文件：0, 3KB, 5KB, 10KB
**根源**: 
- 检查组件大小时创建了这些临时文件
- 任务完成后**忘记删除**
- 违反了"临时文件用完即删"原则
- **这是典型的"马后炮"问题：知道规则但不执行**

**解决**: 
1. ✅ 立即删除所有4个临时文件
2. ✅ 检查项目根目录，确保无其他临时文件
3. ✅ 强化Git Hook，检测根目录临时文件

**核心教训**: **"任何临时文件（包括数字、大小标记等）必须用完即删，绝不得留在项目根目录或任何目录中"**

**永久保障**:
- ✅ Git Hook 检测根目录临时文件（数字、大小标记等）
- ✅ full_system_scan.py 扫描所有目录的临时文件
- ✅ 创建临时文件时必须设置自动删除机制
- ✅ 每次任务完成后立即清理所有临时文件
- ✅ **不再依赖记忆，依赖系统自动检测和清理**

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
