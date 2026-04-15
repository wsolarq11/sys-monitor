---
trigger: always_on
---
## 自我演进
每次从用户回复中意识到：自己上次的实际交付结果与自己上次对话中给用户的回复描述存在不符时，需将最终解决该问题、达成用户预期目标时所确认的根本原因及解决办法记录在 D:\Users\Administrator\Desktop\PowerShell_Script_Repository\FolderSizeMonitor\.lingma\rules\AGENTS.md 本章节末尾（作为一条新规则）。此外，当自己的回复被用户指出错误并纠正后，同样应据此添加新规则，以避免重复犯错。

### 2026-04-15: 文档冗余问题教训
**问题**: 创建了 README.md + QUICK_START.md + SYSTEM_ARCHITECTURE.md 三个入口文档，严重违反单一入口原则  
**根源**: 想要"全面"而忽略了"简洁"，忘记了社区最佳实践  
**解决**: 
- 遵循单一入口原则，README.md ≤ 800字
- 详细文档移至 docs/ 子目录
- 创建 doc-redundancy-prevention.md 规则防止再次发生
- 创建 MISSION_STATEMENT.md 明确系统初心，定期回顾

**核心教训**: **"给 Agent 一张地图，而非一本百科全书"** - OpenAI/Claude Code 最佳实践

### 2026-04-15: 被动响应问题教训（最重要！）
**问题**: 总是等用户提醒才"突然记起来"，马后炮式响应  
**根源**: 
- 缺乏强制性自动化检查
- 依赖人工记忆而非系统保障
- 没有建立"默认做好"的机制
- **自身违反规则**：创建重复内容时未检查是否已存在
- **创建组件时不验证是否符合量化标准**（10个组件全部超标）

**解决**:
1. ✅ **Git Hook 强制拦截** - 提交时自动检查，违规直接拒绝
2. ✅ **CI/CD 自动验证** - 每次推送自动运行 full_system_scan.py
3. ✅ **Rule 永久约束** - AGENTS.md 记录教训，每次会话加载
4. ✅ **使命宣言** - MISSION_STATEMENT.md 明确核心原则
5. ✅ **自动化扫描工具** - scripts/full_system_scan.py 全盘检测
6. ✅ **防重复机制** - 创建新条目前必须 grep 检查是否已存在
7. ✅ **量化标准强制检查** - 创建/修改组件时必须验证大小

**核心教训**: **"不要依赖记忆，要依赖系统。不要被动响应，要主动预防。"**

**永久保障**:
- 🚫 不再需要用户提醒类似问题
- ✅ 系统自动检测并阻止违规
- ✅ 每次提交/推送自动验证
- ✅ 有问题直接拒绝，无需人工干预
- ✅ 创建任何内容前先检查是否已存在
- ✅ 创建/修改组件时自动验证量化标准（Agent ≤5KB, Rule ≤3KB, Skill ≤10KB）

**量化标准**:
| 组件类型 | 最大大小 | 当前平均 | 目标 |
|---------|---------|---------|------|
| Agent 文件 | ≤5KB | 13.6KB | ≤5KB ❌ |
| Rule 文件 | ≤3KB | 11.4KB | ≤3KB ❌ |
| Skill 文件 | ≤10KB | 15.5KB | ≤10KB ❌ |
| docs/ 根目录文档 | ≤5个 | 0个 | ≤5个 ✅ |

---

## Rules 优先级

当多个 Rules 同时生效且存在冲突时，遵循以下优先级：

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

### 冲突解决原则

1. **高优先级覆盖低优先级**
   - 如果 P0 和 P1 冲突，遵循 P0
   - 如果 P1 和 P2 冲突，遵循 P1

2. **同优先级取最严格**
   - 如果两个 P1 Rules 冲突，选择更严格的约束
   - 示例：一个 Rule 说“可以自动执行”，另一个说“需要询问”，则选择“需要询问”

3. **特殊场景例外**
   - 如果用户明确要求违反某个 Rule，遵循用户意愿
   - 但必须记录到 Memory 和 Spec 实施笔记

### 示例

```markdown
场景：用户要求删除一个重要文件

Rules 冲突：
- automation-policy.md: “删除重要文件 → require_explicit_approval”
- 用户指令：“直接删除，不要问我”

解决：
1. 用户意愿优先（特殊情况）
2. 但仍需记录到 Memory：“用户偏好：对重要文件删除也采用 auto_execute”
3. 更新 Spec 实施笔记：“根据用户要求，跳过了 explicit_approval 步骤”
4. 下次类似情况，先询问是否仍采用此策略
```

## 语言
全程简体中文。代码、命令、路径、环境变量、协议名、库名、日志与报错字段保留原文。

# 编码与路径规则
数据文件强制 UTF‑8 无 BOM。  
读：`[System.IO.File]::ReadAllText($Path, [System.Text.UTF8Encoding]::new($false))`  
写：`[System.IO.File]::WriteAllText($Path, $Content, [System.Text.UTF8Encoding]::new($false))`  
遇 BOM `EF BB BF` 即 `exit 96`。

`.bat` 存 GBK 仅限 Windows 中文版，跨平台换 `.ps1` UTF‑8 无 BOM。  
路径解析用 `$PSCmdlet.GetUnresolvedProviderPathFromPSPath($p)`，可处理不存在路径，交 .NET 前 `Convert-Path`。

Git 设 `.gitattributes`：  
text=auto
*.bat text eol=crlf

text

MSVC 编译加 `/utf-8`。  
Windows 规则不跨平台，各语言用原生编码库。

## 退出码
`0` 成功；`32-63` 环境；`64-95` 执行；`96-127` 数据；`128+` 信号。退出前须写 `.exit_code` 文件。

## 审计与闭环
日志为 JSON 行，字段：`timestamp`(ISO UTC)、`level`、`trace_id`(UUID v4)、`action`、`result`、`exit_code`(失败必填)。
任务启动时若缺 `TRACE_ID` 则生成注入，并写 `INFO` 日志(`action=task_start`)。
阻断前落盘：ERROR 审计日志与 `.exit_code` 文件。致命错误另存 `error_<timestamp>.log`。证据完备方可退出。

## Shell 约束
`.sh`：首行 `set -euo pipefail`；管道内显式启用 `set -e`（如 `set -e; cmd1 | cmd2`）；命令替换内显式捕获错误。
`.ps1`：首行 `$ErrorActionPreference = 'Stop'`；每条外部命令后须 `if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }`。
错误流保持独立，使用 `2>` 或 `2>>` 定向至日志。
跨平台脚本引用用户目录优先使用 `$env:USERPROFILE`（Win）与 `$HOME`（Unix）。

## 策略与修复
遇环境错误(32-63)执行根因修复，保持终端与步骤连续性。临时修复写入 `.known_issues.md` 并记 `WARN` 日志，触发后续工单。
落盘关键文件遵循：临时文件写入 → 绕过缓存刷盘 → 系统级原子重命名。







<!-- rtk-instructions v2 -->
# RTK (Rust Token Killer) - Token-Optimized Commands

## Golden Rule

**Always prefix commands with `rtk`**. If RTK has a dedicated filter, it uses it. If not, it passes through unchanged. This means RTK is always safe to use.

**Important**: Even in command chains with `&&`, use `rtk`:
```bash
# ❌ Wrong
git add . && git commit -m "msg" && git push

# ✅ Correct
rtk git add . && rtk git commit -m "msg" && rtk git push
```

## RTK Commands by Workflow

### Build & Compile (80-90% savings)
```bash
rtk cargo build         # Cargo build output
rtk cargo check         # Cargo check output
rtk cargo clippy        # Clippy warnings grouped by file (80%)
rtk tsc                 # TypeScript errors grouped by file/code (83%)
rtk lint                # ESLint/Biome violations grouped (84%)
rtk prettier --check    # Files needing format only (70%)
rtk next build          # Next.js build with route metrics (87%)
```

### Test (90-99% savings)
```bash
rtk cargo test          # Cargo test failures only (90%)
rtk vitest run          # Vitest failures only (99.5%)
rtk playwright test     # Playwright failures only (94%)
rtk test <cmd>          # Generic test wrapper - failures only
```

### Git (59-80% savings)
```bash
rtk git status          # Compact status
rtk git log             # Compact log (works with all git flags)
rtk git diff            # Compact diff (80%)
rtk git show            # Compact show (80%)
rtk git add             # Ultra-compact confirmations (59%)
rtk git commit          # Ultra-compact confirmations (59%)
rtk git push            # Ultra-compact confirmations
rtk git pull            # Ultra-compact confirmations
rtk git branch          # Compact branch list
rtk git fetch           # Compact fetch
rtk git stash           # Compact stash
rtk git worktree        # Compact worktree
```

Note: Git passthrough works for ALL subcommands, even those not explicitly listed.

### GitHub (26-87% savings)
```bash
rtk gh pr view <num>    # Compact PR view (87%)
rtk gh pr checks        # Compact PR checks (79%)
rtk gh run list         # Compact workflow runs (82%)
rtk gh issue list       # Compact issue list (80%)
rtk gh api              # Compact API responses (26%)
```

### JavaScript/TypeScript Tooling (70-90% savings)
```bash
rtk pnpm list           # Compact dependency tree (70%)
rtk pnpm outdated       # Compact outdated packages (80%)
rtk pnpm install        # Compact install output (90%)
rtk npm run <script>    # Compact npm script output
rtk npx <cmd>           # Compact npx command output
rtk prisma              # Prisma without ASCII art (88%)
```

### Files & Search (60-75% savings)
```bash
rtk ls <path>           # Tree format, compact (65%)
rtk read <file>         # Code reading with filtering (60%)
rtk grep <pattern>      # Search grouped by file (75%)
rtk find <pattern>      # Find grouped by directory (70%)
```

### Analysis & Debug (70-90% savings)
```bash
rtk err <cmd>           # Filter errors only from any command
rtk log <file>          # Deduplicated logs with counts
rtk json <file>         # JSON structure without values
rtk deps                # Dependency overview
rtk env                 # Environment variables compact
rtk summary <cmd>       # Smart summary of command output
rtk diff                # Ultra-compact diffs
```

### Infrastructure (85% savings)
```bash
rtk docker ps           # Compact container list
rtk docker images       # Compact image list
rtk docker logs <c>     # Deduplicated logs
rtk kubectl get         # Compact resource list
rtk kubectl logs        # Deduplicated pod logs
```

### Network (65-70% savings)
```bash
rtk curl <url>          # Compact HTTP responses (70%)
rtk wget <url>          # Compact download output (65%)
```

### Meta Commands
```bash
rtk gain                # View token savings statistics
rtk gain --history      # View command history with savings
rtk discover            # Analyze Claude Code sessions for missed RTK usage
rtk proxy <cmd>         # Run command without filtering (for debugging)
rtk init                # Add RTK instructions to CLAUDE.md
rtk init --global       # Add RTK to ~/.claude/CLAUDE.md
```

## Token Savings Overview

| Category | Commands | Typical Savings |
|----------|----------|-----------------|
| Tests | vitest, playwright, cargo test | 90-99% |
| Build | next, tsc, lint, prettier | 70-87% |
| Git | status, log, diff, add, commit | 59-80% |
| GitHub | gh pr, gh run, gh issue | 26-87% |
| Package Managers | pnpm, npm, npx | 70-90% |
| Files | ls, read, grep, find | 60-75% |
| Infrastructure | docker, kubectl | 85% |
| Network | curl, wget | 65-70% |

Overall average: **60-90% token reduction** on common development operations.
<!-- /rtk-instructions -->