# Spec触发器机制 - 硬约束自动化实施指南

## 📋 概述

本文档描述Spec-Driven Development系统的**硬约束自动化**实现，通过Git Hooks、验证中间件和后台Worker引擎，确保开发流程严格遵循Spec驱动原则。

### 核心特性

✅ **强制约束** - Git pre-commit钩子阻止无Spec的提交  
✅ **自动验证** - post-checkout钩子自动检查Spec状态  
✅ **异步处理** - Worker引擎后台执行Spec相关任务  
✅ **完整审计** - 所有操作记录到日志文件  
✅ **最小噪音** - 简洁的代码实现，less is more  

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────┐
│           Developer Workflow                 │
│  (git commit / git checkout / git switch)   │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│          Git Hooks Layer                     │
│  ┌──────────────┐  ┌──────────────────┐    │
│  │ pre-commit   │  │ post-checkout    │    │
│  │ (强制验证)   │  │ (状态检查)       │    │
│  └──────┬───────┘  └────────┬─────────┘    │
└─────────┼───────────────────┼──────────────┘
          │                   │
          ▼                   ▼
┌─────────────────────────────────────────────┐
│      Spec Validator Middleware              │
│  - 检查 current-spec.md 存在性              │
│  - 验证必需字段和元数据                      │
│  - 评估状态转换合法性                        │
│  - 生成验证报告                              │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│        Spec Worker Engine                    │
│  - 异步任务队列                              │
│  - 后台执行验证/更新/清理                    │
│  - 优先级调度                                │
│  - 错误重试机制                              │
└─────────────────────────────────────────────┘
```

---

## 📦 组件说明

### 1. Spec验证中间件 (`spec-validator.py`)

**职责**: 验证Spec文件的完整性和有效性

**验证规则**:
- ✅ `current-spec.md` 必须存在
- ✅ 必需字段: 元数据、背景与目标、需求规格、实施计划
- ✅ 元数据完整性: 创建日期、状态、优先级
- ✅ 状态转换合法性: draft → in-progress → review → completed
- ✅ 实施笔记: in-progress状态应有进度记录

**使用模式**:
```bash
# Pre-commit模式（严格，阻止提交）
python .lingma/scripts/spec-validator.py pre-commit

# Post-checkout模式（宽松，仅警告）
python .lingma/scripts/spec-validator.py post-checkout

# CI/CD模式（严格，用于流水线）
python .lingma/scripts/spec-validator.py ci

# 手动验证
python .lingma/scripts/spec-validator.py manual
```

**返回值**:
- `0`: 验证通过
- `1`: 验证失败（有错误）

---

### 2. Git Hooks

#### pre-commit Hook

**触发时机**: `git commit` 执行前

**行为**: 
- 调用 `spec-validator.py pre-commit`
- 如果验证失败，**阻止提交**
- 显示详细的错误信息和修复建议

**安装位置**: `.git/hooks/pre-commit`

#### post-checkout Hook

**触发时机**: `git checkout` 或 `git switch` 执行后

**行为**:
- 调用 `spec-validator.py post-checkout`
- 仅显示警告，**不阻止操作**
- 提醒开发者当前Spec状态

**安装位置**: `.git/hooks/post-checkout`

---

### 3. Spec Worker引擎 (`spec-worker.py`)

**职责**: 异步处理Spec相关后台任务

**任务类型**:
- `validate_spec`: 验证Spec状态
- `update_spec_status`: 更新Spec状态
- `generate_report`: 生成进度报告
- `cleanup_old_tasks`: 清理旧任务

**架构**:
```
.lingma/worker/tasks/
├── pending/      # 待处理任务（JSON文件）
├── running/      # 运行中任务
├── completed/    # 已完成任务（保留7天）
└── failed/       # 失败任务（保留7天）
```

**使用方式**:

```bash
# 启动Worker（后台运行）
python .lingma/scripts/spec-worker.py start

# 提交任务
python .lingma/scripts/spec-worker.py submit \
  --task-type validate_spec \
  --priority high

# 查看队列状态
python .lingma/scripts/spec-worker.py status
```

---

## 🚀 快速开始

### Step 1: 安装Git Hooks

```bash
# 进入项目根目录
cd d:\Users\Administrator\Desktop\PowerShell_Script_Repository\FolderSizeMonitor

# 运行安装脚本
python .lingma/scripts/install-hooks.py
```

**预期输出**:
```
🔧 开始安装Git Hooks...

✅ 已安装: pre-commit
✅ 已安装: post-checkout

🔍 验证安装:
  ✅ pre-commit
  ✅ post-checkout

📊 安装结果:
  成功: 2
  失败: 0

✅ 所有Hooks安装成功！

💡 提示:
  - pre-commit: 提交前强制验证Spec
  - post-checkout: 切换分支后检查Spec状态
  - 运行测试: git commit --allow-empty -m 'test'
```

### Step 2: 验证安装

```bash
# 测试pre-commit hook
git commit --allow-empty -m "测试Spec验证"
```

**如果Spec有效**:
```
🔍 执行Spec预提交检查...
✅ Spec验证通过
[main abc1234] 测试Spec验证
```

**如果Spec无效**:
```
🔍 执行Spec预提交检查...

❌ Spec验证失败:
  ❌ Spec文件不存在: .../current-spec.md
     必须先创建Spec才能进行开发

💡 修复建议:
  1. 确保 current-spec.md 存在且格式正确
  2. 参考模板: .lingma/specs/templates/spec-template.md
  3. 运行验证脚本: python .lingma/scripts/validate-spec.py

🚫 Commit被阻止：Spec验证失败
   修复问题后重新commit
```

### Step 3: 启动Worker引擎（可选）

```bash
# 在新终端启动Worker
python .lingma/scripts/spec-worker.py start

# 或使用后台运行（Linux/Mac）
nohup python .lingma/scripts/spec-worker.py start > /dev/null 2>&1 &

# Windows后台运行
start /B python .lingma/scripts/spec-worker.py start
```

---

## 📖 使用示例

### 场景1: 正常开发流程

```bash
# 1. 切换到功能分支
git checkout feature/new-feature

# post-checkout hook自动执行
🔍 执行Spec切换后检查...
✅ Spec状态正常

# 2. 修改代码
echo "print('hello')" >> test.py
git add test.py

# 3. 提交（Spec有效则通过）
git commit -m "添加测试代码"

# pre-commit hook自动执行
🔍 执行Spec预提交检查...
✅ Spec验证通过
[feature/new-feature xyz789] 添加测试代码
```

### 场景2: Spec缺失时尝试提交

```bash
# 删除Spec文件（模拟错误）
mv .lingma/specs/current-spec.md .lingma/specs/current-spec.md.bak

# 尝试提交
git commit -m "测试提交"

# 被阻止
🔍 执行Spec预提交检查...

❌ Spec验证失败:
  ❌ Spec文件不存在: .../current-spec.md
     必须先创建Spec才能进行开发

🚫 Commit被阻止：Spec验证失败
```

### 场景3: 手动验证Spec

```bash
# 手动运行验证
python .lingma/scripts/spec-validator.py manual

# 输出
验证结果: ✅ 通过

警告 (1):
  ⚠️  in-progress状态的Spec应该有实施笔记记录进度
```

### 场景4: 提交Worker任务

```bash
# 提交验证任务
python .lingma/scripts/spec-worker.py submit \
  --task-type validate_spec \
  --priority medium

# 提交状态更新任务
python .lingma/scripts/spec-worker.py submit \
  --task-type update_spec_status \
  --payload '{"status": "review"}' \
  --priority high

# 查看队列状态
python .lingma/scripts/spec-worker.py status

# 输出
📊 Worker队列状态:
  待处理: 2
  运行中: 0
  已完成: 5
  失败:   0
```

---

## 🔧 配置选项

### 验证器配置

编辑 `.lingma/config/automation.json`:

```json
{
  "spec_validation": {
    "strict_mode": true,
    "required_fields": [
      "元数据",
      "背景与目标",
      "需求规格",
      "实施计划"
    ],
    "valid_statuses": [
      "draft",
      "in-progress",
      "review",
      "completed",
      "archived"
    ]
  }
}
```

### Worker配置

编辑 `.lingma/config/worker.json` (需创建):

```json
{
  "worker": {
    "poll_interval": 2.0,
    "max_retries": 3,
    "retention_days": 7,
    "log_level": "INFO"
  }
}
```

---

## 🧪 测试方法

### 端到端测试

```bash
# 1. 验证Hook安装
python .lingma/scripts/install-hooks.py

# 2. 测试pre-commit（应通过）
git commit --allow-empty -m "测试1: 正常提交"

# 3. 临时禁用Hook测试失败场景
mv .git/hooks/pre-commit .git/hooks/pre-commit.bak
git commit --allow-empty -m "测试2: 绕过Hook"
mv .git/hooks/pre-commit.bak .git/hooks/pre-commit

# 4. 测试post-checkout
git checkout main
git checkout feature/test

# 5. 测试Worker
python .lingma/scripts/spec-worker.py submit --task-type validate_spec
python .lingma/scripts/spec-worker.py status
```

### 单元测试

```bash
# 运行验证器测试
python -c "
from pathlib import Path
from .lingma.scripts.spec_validator import SpecValidator

validator = SpecValidator(Path('.'))
is_valid, errors, warnings = validator.validate()
print(f'Valid: {is_valid}')
print(f'Errors: {len(errors)}')
print(f'Warnings: {len(warnings)}')
"
```

---

## 🛠️ 故障排除

### 问题1: Hook未执行

**症状**: `git commit` 时没有看到验证信息

**原因**: Hook未安装或无执行权限

**解决**:
```bash
# 重新安装
python .lingma/scripts/install-hooks.py

# 检查权限（Unix）
ls -la .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### 问题2: Python找不到

**症状**: `command not found: python3`

**解决**:
```bash
# Windows: 确保Python在PATH中
where python

# Linux/Mac: 检查Python安装
which python3

# 或者修改Hook脚本，指定Python路径
# 编辑 .git/hooks/pre-commit，第一行改为:
#!/usr/bin/env python
```

### 问题3: Spec验证误报

**症状**: Spec实际有效但验证失败

**原因**: 格式不符合预期

**解决**:
```bash
# 查看详细错误
python .lingma/scripts/spec-validator.py manual

# 参考模板修正
cat .lingma/specs/templates/spec-template.md
```

### 问题4: Worker不处理任务

**症状**: 提交任务后队列一直pending

**原因**: Worker未启动

**解决**:
```bash
# 检查Worker是否运行
ps aux | grep spec-worker

# 启动Worker
python .lingma/scripts/spec-worker.py start

# 查看日志
tail -f .lingma/logs/worker.log
```

---

## 📝 最佳实践

### 1. 始终先创建Spec

```bash
# 开始新功能前
cp .lingma/specs/templates/spec-template.md .lingma/specs/current-spec.md
# 编辑Spec
# 然后开始编码
```

### 2. 定期更新实施笔记

```markdown
## 实施笔记

### 2024-01-15 10:00
**完成**: Task-001 - 实现核心功能
**进度**: 30% (15/50 任务)
**问题**: 无
```

### 3. 使用Worker处理耗时任务

```bash
# 不要阻塞主流程
python .lingma/scripts/spec-worker.py submit \
  --task-type generate_report \
  --priority low
```

### 4. 监控验证日志

```bash
# 查看最近的验证记录
tail -n 20 .lingma/logs/spec-validation.log

# 查看Worker日志
tail -f .lingma/logs/worker.log
```

---

## 🔒 安全考虑

### 1. Hook不可绕过

⚠️ **注意**: 用户可以通过 `--no-verify` 绕过pre-commit hook

```bash
# 危险！不推荐
git commit --no-verify -m "绕过验证"
```

**缓解措施**:
- CI/CD流水线也集成验证（双重保障）
- Code Review检查Spec合规性
- 团队约定禁止使用 `--no-verify`

### 2. 日志审计

所有验证结果记录到:
- `.lingma/logs/spec-validation.log`
- `.lingma/logs/worker.log`

**不可篡改**: 建议使用Git追踪日志文件变更

### 3. 权限控制

Worker任务处理器应避免:
- ❌ 执行任意shell命令
- ❌ 访问敏感文件
- ✅ 仅操作Spec相关文件
- ✅ 完整的错误处理

---

## 📊 监控指标

### 关键指标

| 指标 | 阈值 | 告警 |
|------|------|------|
| Spec验证通过率 | > 95% | Warning |
| Worker任务失败率 | < 5% | Critical |
| 平均验证时间 | < 100ms | Warning |
| Hook执行失败次数 | 0 | Critical |

### 查看统计

```bash
# 验证统计
python -c "
import json
from pathlib import Path

log_file = Path('.lingma/logs/spec-validation.log')
if log_file.exists():
    lines = log_file.read_text().strip().split('\n')
    total = len(lines)
    success = sum(1 for line in lines if json.loads(line)['success'])
    print(f'总验证次数: {total}')
    print(f'成功率: {success/total*100:.1f}%')
"

# Worker统计
python .lingma/scripts/spec-worker.py status
```

---

## 🔄 卸载

如需移除Spec触发器机制：

```bash
# 卸载Hooks
python .lingma/scripts/install-hooks.py --uninstall

# 删除脚本（可选）
rm .lingma/scripts/spec-validator.py
rm .lingma/scripts/spec-worker.py
rm .lingma/scripts/install-hooks.py

# 删除Worker数据（可选）
rm -rf .lingma/worker

# 删除日志（可选）
rm .lingma/logs/spec-validation.log
rm .lingma/logs/worker.log
```

---

## 📚 相关文档

- [Spec模板](../specs/templates/spec-template.md)
- [自动化策略](../rules/automation-policy.md)
- [Spec-Driven Core Agent](../agents/spec-driven-core-agent.md)
- [架构设计](../../docs/architecture/ARCHITECTURE.md)

---

## 🎯 总结

Spec触发器机制通过**三层防护**确保Spec-Driven流程严格执行：

1. **Pre-commit Hook** - 阻止无Spec的提交（硬约束）
2. **Post-checkout Hook** - 提醒Spec状态变化（软提示）
3. **Worker Engine** - 异步处理Spec任务（自动化）

**核心价值**:
- ✅ 强制执行Spec驱动开发
- ✅ 减少人为疏漏
- ✅ 提升代码质量
- ✅ 完整审计追溯

**Less is More**: 最小化代码噪音，最大化约束效果。
