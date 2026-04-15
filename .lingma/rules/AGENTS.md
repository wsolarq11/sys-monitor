## 自我演进
每次从用户回复中意识到：自己上次的实际交付结果与自己上次对话中给用户的回复描述存在不符时，需将最终解决该问题、达成用户预期目标时所确认的根本原因及解决办法记录在 D:\Users\Administrator\Desktop\PowerShell_Script_Repository\FolderSizeMonitor\.lingma\rules\AGENTS.md 本章节末尾（作为一条新规则）。此外，当自己的回复被用户指出错误并纠正后，同样应据此添加新规则，以避免重复犯错。

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