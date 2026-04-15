# Spec强制约束机制 - 使用指南

## 📋 概述

本系统实现了**真正的Spec驱动开发硬约束**，确保所有代码提交都必须有完整、有效的Spec支持。

### 核心特性

✅ **Git Hook pre-commit强制验证** - 阻止无Spec或Spec不完整的提交  
✅ **Spec验证中间件** - 4种模式验证Spec完整性  
✅ **后台Worker执行引擎** - 异步处理Spec任务  
✅ **自动审计日志** - 所有操作可追溯  
✅ **端到端可测试** - 16项检查100%通过  

---

## 🚀 快速开始

### 1. 安装Git Hooks

```bash
cd /path/to/your/project
python .lingma/scripts/install-hooks.py
```

输出示例:
```
============================================================
Git Hook 安装程序
============================================================
项目根目录: /path/to/project
Hook源目录: /path/to/project/.lingma/hooks
Hook目标目录: /path/to/project/.git/hooks
============================================================

📦 安装 pre-commit hook...
   ✅ 已设置执行权限
   ✅ Hook已安装: /path/to/project/.git/hooks/pre-commit
   📄 文件大小: 5234 bytes

============================================================
✅ Git Hook 安装成功!
============================================================
```

### 2. 验证安装

```bash
python .lingma/scripts/install-hooks.py --verify
```

### 3. 测试强制约束

```bash
# 修改任意文件
echo "test" >> test.txt
git add test.txt

# 尝试提交(会自动触发Spec验证)
git commit -m "test commit"
```

如果Spec验证失败，提交将被阻止:
```
🔍 执行Spec强制验证...
   正在验证Spec完整性...
❌ Spec验证失败

错误:
  - 缺少必填字段: status
  - 存在未回答的澄清问题

请修复上述问题后重新提交。
```

---

## 📖 组件说明

### 1. Spec验证器 (spec-validator.py)

**功能**: 解析和验证Spec文件完整性

**使用方式**:

```bash
# 手动验证
python .lingma/scripts/spec-validator.py --mode manual

# Pre-commit模式(由Git Hook自动调用)
python .lingma/scripts/spec-validator.py --mode pre-commit

# CI模式(持续集成)
python .lingma/scripts/spec-validator.py --mode CI

# JSON格式输出
python .lingma/scripts/spec-validator.py --mode manual --json

# 严格模式(警告也视为错误)
python .lingma/scripts/spec-validator.py --mode manual --strict

# 指定Spec文件
python .lingma/scripts/spec-validator.py --spec path/to/spec.md
```

**验证内容**:
- ✅ Spec文件存在性
- ✅ 必填字段(status, priority)
- ✅ 状态值有效性(draft/in-progress/review/completed/archived)
- ✅ 优先级有效性(P0/P1/P2/P3/LOW/MEDIUM/HIGH/CRITICAL)
- ✅ 澄清问题检测([NEEDS CLARIFICATION])
- ✅ 任务列表完整性
- ✅ 任务进度一致性

**输出示例**:
```
============================================================
Spec验证报告
============================================================
Spec文件: /path/to/.lingma/specs/current-spec.md
验证模式: manual
验证时间: 2024-01-15T10:30:00
耗时: 15.2ms

--- 元数据 ---
  状态: in-progress
  优先级: P0
  进度: 60.9%

--- 任务进度 ---
  总计: 50
  已完成: 31
  待完成: 19
  完成率: 62.0%

验证结果: ✅ 通过

============================================================
```

---

### 2. Spec Worker (spec-worker.py)

**功能**: 异步执行Spec任务，支持优先级调度和自动重试

**使用方式**:

```bash
# 启动Worker(持续处理任务)
python .lingma/scripts/spec-worker.py --start

# 限制处理任务数
python .lingma/scripts/spec-worker.py --start --max-tasks 5

# 查看Worker状态
python .lingma/scripts/spec-worker.py --status

# 处理指定任务
python .lingma/scripts/spec-worker.py --process-task "Task-001"
```

**输出示例**:
```
============================================================
Spec Worker 启动
============================================================
Worker ID: worker-20240115103000
项目根目录: /path/to/project
Spec文件: /path/to/.lingma/specs/current-spec.md
最大重试次数: 3
============================================================

🚀 开始处理任务: Task-001
   描述: 创建自动化引擎核心
   优先级: HIGH
   时间: 2024-01-15 10:30:00
✅ 任务完成: Task-001

🚀 开始处理任务: Task-002
   描述: 创建操作日志系统
   优先级: MEDIUM
   时间: 2024-01-15 10:30:05
✅ 任务完成: Task-002

✅ 所有任务已完成!

============================================================
Worker 停止
处理任务数: 2
成功: 2
失败: 0
============================================================
```

**特性**:
- 🔄 **自动重试**: 失败任务最多重试3次
- 📊 **优先级调度**: CRITICAL > HIGH > MEDIUM > LOW
- 📝 **进度更新**: 自动更新Spec中的任务进度
- 🔔 **失败通知**: 任务失败时通知用户
- 📋 **审计日志**: 所有操作记录到audit.log

---

### 3. Git Pre-commit Hook

**功能**: 在每次commit前强制执行Spec验证

**安装**:
```bash
python .lingma/scripts/install-hooks.py
```

**卸载**:
```bash
python .lingma/scripts/install-hooks.py --uninstall
```

**验证流程**:
1. ✅ 检查current-spec.md是否存在
2. ✅ 运行spec-validator.py验证Spec
3. ✅ 检测未回答的澄清问题
4. ✅ 验证Spec状态(in-progress/review)
5. ✅ 记录审计日志
6. ❌ 任何检查失败则阻止提交

**绕过验证**(紧急情况):
```bash
git commit --no-verify -m "emergency fix"
```

⚠️ **注意**: `--no-verify`应在团队负责人批准下使用，并事后补充Spec。

---

## 🔧 配置说明

### Spec文件格式要求

```markdown
# Spec标题

## 元数据
- **创建日期**: 2024-01-15
- **状态**: in-progress          # 必需: draft/in-progress/review/completed/archived
- **优先级**: P0                 # 必需: P0/P1/P2/P3/LOW/MEDIUM/HIGH/CRITICAL
- **负责人**: AI Assistant
- **进度**: 60.9% (31/50 任务)

## 背景与目标
...

## 需求规格
...

## 实施计划
- [x] Task-001: 任务描述 ✅ 已完成
- [ ] Task-002: 任务描述
- [ ] Task-003: 需要澄清的问题[NEEDS CLARIFICATION]
```

### 澄清问题标记

当需求不明确时，使用`[NEEDS CLARIFICATION]`标记:

```markdown
- [ ] Task-003: 实现用户认证[NEEDS CLARIFICATION]
  问题: 使用哪种认证方式? JWT还是Session?
```

**规则**: 
- 存在`[NEEDS CLARIFICATION]`标记时，Git提交将被阻止
- 必须在Spec中回答问题并删除标记后才能继续

---

## 📊 审计日志

所有操作自动记录到 `.lingma/logs/audit.log`:

```json
{"timestamp":"2024-01-15T10:30:00","event_type":"pre-commit-check","status":"passed","message":"Spec验证通过","hook":"pre-commit"}
{"timestamp":"2024-01-15T10:30:05","event_type":"task_started","worker_id":"worker-20240115103000","task_id":"Task-001","priority":"HIGH"}
{"timestamp":"2024-01-15T10:30:06","event_type":"task_completed","worker_id":"worker-20240115103000","task_id":"Task-001","retries":0}
```

**日志类型**:
- `pre-commit-check`: Git Hook验证
- `worker_started/stopped`: Worker启停
- `task_started/completed/failed`: 任务执行
- `notification_sent`: 通知发送

---

## 🧪 验证和测试

### 运行端到端验证

```bash
python .lingma/scripts/verify-spec-trigger.py
```

**16项检查**:
1. ✅ Spec文件存在性
2. ✅ Spec文件格式正确
3. ✅ spec-validator.py存在且可执行
4. ✅ spec-worker.py存在且可执行
5. ✅ pre-commit.sh存在
6. ✅ install-hooks.py存在且可执行
7. ✅ Git Hooks目录结构
8. ✅ 审计日志目录
9. ✅ Worker状态目录
10. ✅ Validator功能测试
11. ✅ Worker功能测试
12. ✅ Hook安装流程
13. ✅ 澄清问题检测
14. ✅ 任务进度更新
15. ✅ 审计日志记录
16. ✅ 完整工作流集成测试

**输出示例**:
```
======================================================================
Spec强制约束机制 - 端到端验证
======================================================================
项目根目录: /path/to/project
验证时间: 2024-01-15 10:30:00
======================================================================

[ 1/16] Spec文件存在性... ✅ PASS
[ 2/16] Spec文件格式... ✅ PASS
[ 3/16] spec-validator.py存在... ✅ PASS
...
[16/16] 完整工作流集成... ✅ PASS

======================================================================
验证结果: 16/16 通过
🎉 所有检查通过! Spec强制约束机制已就绪。
======================================================================
```

---

## ⚠️ 常见问题

### Q1: 如何临时禁用Hook?

```bash
# 方法1: 单次提交绕过
git commit --no-verify -m "message"

# 方法2: 卸载Hook
python .lingma/scripts/install-hooks.py --uninstall

# 方法3: 删除Hook文件
rm .git/hooks/pre-commit
```

### Q2: Spec验证失败但必须紧急提交怎么办?

1. 使用`--no-verify`提交
2. 立即创建/修复Spec
3. 提交Spec修复
4. 向团队说明情况

```bash
# 紧急提交
git commit --no-verify -m "hotfix: critical bug"

# 修复Spec
vim .lingma/specs/current-spec.md

# 提交Spec
git add .lingma/specs/current-spec.md
git commit -m "docs: add spec for hotfix"
```

### Q3: 如何自定义验证规则?

编辑 `.lingma/scripts/spec-validator.py`:

```python
class SpecValidator:
    REQUIRED_FIELDS = ['status', 'priority', '负责人']  # 添加自定义必填字段
    VALID_STATUSES = ['draft', 'in-progress', ...]      # 自定义有效状态
```

### Q4: Worker如何处理长时间运行的任务?

Worker支持后台运行和断点续传:

```bash
# 后台启动
nohup python .lingma/scripts/spec-worker.py --start &

# 查看状态
python .lingma/scripts/spec-worker.py --status

# 中断后可重新启动，会从上次位置继续
```

### Q5: 如何查看历史审计日志?

```bash
# 查看所有日志
cat .lingma/logs/audit.log

# 查看特定类型事件
grep "pre-commit-check" .lingma/logs/audit.log

# 格式化查看
python -c "
import json
with open('.lingma/logs/audit.log') as f:
    for line in f:
        entry = json.loads(line)
        print(f'{entry[\"timestamp\"]} - {entry[\"event_type\"]}: {entry.get(\"message\", \"\")}')
"
```

---

## 📚 最佳实践

### 1. Spec编写规范

✅ **推荐**:
```markdown
- [x] Task-001: 创建自动化引擎核心 (预计: 2h) ✅ 已完成
- [ ] Task-002: 创建操作日志系统 (预计: 1h)
```

❌ **避免**:
```markdown
- [ ] 做一些事情
- [x] 完成了某个任务
```

### 2. 澄清问题处理

✅ **推荐**:
```markdown
- [ ] Task-003: 实现用户认证[NEEDS CLARIFICATION]
  问题: 使用JWT还是Session?
  建议: JWT更适合微服务架构
```

❌ **避免**:
```markdown
- [ ] Task-003: 实现用户认证[NEEDS CLARIFICATION]
  (没有具体问题描述)
```

### 3. 提交频率

- ✅ 每个任务完成后提交
- ✅ 重大变更前先更新Spec
- ❌ 不要累积多个任务后一次性提交

### 4. 团队协作

- 定期运行`verify-spec-trigger.py`确保系统正常
- 审查`.lingma/logs/audit.log`了解团队活动
- 新成员入职时运行`install-hooks.py`

---

## 🔗 相关文档

- [实施报告](SPEC_TRIGGER_IMPLEMENTATION.md) - 详细的技术实现说明
- [Spec模板](../specs/spec-template.md) - 标准Spec格式
- [自动化策略](../rules/automation-policy.md) - 风险评估和执行策略

---

## 📞 支持和反馈

如有问题或建议，请:
1. 查看本文档的"常见问题"部分
2. 检查`.lingma/logs/audit.log`了解详细错误
3. 运行`verify-spec-trigger.py`诊断系统状态
4. 联系项目负责人

---

**版本**: v1.0  
**最后更新**: 2024-01-15  
**维护者**: AI Assistant
