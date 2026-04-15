# Spec自动化基础设施使用指南

## 概述

本系统实现了真正的Spec自动化基础设施，包括：
- **文件监听守护进程** - 实时监控Spec变化并触发重新评估
- **规则解析引擎** - 解析和执行规则约束
- **增强的Worker** - 集成规则验证和自动启动watcher
- **Windows计划任务** - 开机自启守护进程
- **增强的Git Hooks** - pre-commit和post-checkout钩子
- **E2E测试套件** - 端到端测试验证

## 快速开始

### 1. 安装依赖

```bash
pip install watchdog
```

### 2. 运行E2E测试验证安装

```bash
python .lingma/scripts/test-e2e-automation.py --all
```

### 3. 启动Spec Worker（带规则验证）

```bash
python .lingma/scripts/spec-worker-enhanced.py --start
```

### 4. 启动Spec Watcher守护进程

```bash
python .lingma/scripts/spec-watcher.py --start
```

或在后台启动：

```bash
python .lingma/scripts/spec-worker-enhanced.py --start-watcher
```

## 组件详细说明

### 1. Spec Watcher (spec-watcher.py)

**功能**: 实时监控`.lingma/specs/current-spec.md`文件变化

**使用方式**:

```bash
# 启动监听器
python .lingma/scripts/spec-watcher.py --start

# 查看状态
python .lingma/scripts/spec-watcher.py --status

# 停止监听器
python .lingma/scripts/spec-watcher.py --stop

# 重新加载配置
python .lingma/scripts/spec-watcher.py --reload
```

**配置文件**: `.lingma/config/watcher-config.json`

```json
{
  "debounce_delay": 1.0,
  "auto_trigger_evaluation": true,
  "log_level": "INFO",
  "watch_patterns": ["*.md"],
  "exclude_patterns": ["*~", "*.tmp"]
}
```

**日志文件**: `.lingma/logs/watcher.log`

### 2. Rule Engine (rule-engine.py)

**功能**: 解析和执行`.lingma/rules/`下的所有Rule文件

**使用方式**:

```bash
# 验证Spec合规性
python .lingma/scripts/rule-engine.py --validate-spec

# 列出所有规则
python .lingma/scripts/rule-engine.py --list-rules

# 检查特定规则
python .lingma/scripts/rule-engine.py --check-rule spec-session-start

# JSON格式输出
python .lingma/scripts/rule-engine.py --validate-spec --json
```

**规则优先级**:
- **P0**: 关键，必须遵守
- **P1**: 重要，应该遵守
- **P2**: 建议，最好遵守

**触发器类型**:
- `always_on`: 始终启用
- `on_change`: 变更时触发
- `on_commit`: 提交时触发
- `on_spec_update`: Spec更新时触发
- `manual`: 手动触发

### 3. Spec Worker Enhanced (spec-worker-enhanced.py)

**功能**: 增强版Worker，集成规则验证和watcher管理

**新增功能**:
- 启动前自动验证Spec合规性
- 可自动启动spec-watcher守护进程
- 失败时阻止任务执行

**使用方式**:

```bash
# 启动Worker（默认启用规则验证）
python .lingma/scripts/spec-worker-enhanced.py --start

# 跳过规则验证
python .lingma/scripts/spec-worker-enhanced.py --start --skip-validation

# 启动Watcher守护进程
python .lingma/scripts/spec-worker-enhanced.py --start-watcher

# 处理指定任务（先验证规则）
python .lingma/scripts/spec-worker-enhanced.py --process-task "Task-001"
```

### 4. Windows计划任务 (install-windows-task.ps1)

**功能**: 自动注册Windows Task Scheduler任务，实现开机自启

**使用方式**（需要管理员权限）:

```powershell
# 安装计划任务
.\.lingma\scripts\install-windows-task.ps1 -Install

# 卸载计划任务
.\.lingma\scripts\install-windows-task.ps1 -Uninstall

# 查看状态
.\.lingma\scripts\install-windows-task.ps1 -Status
```

**任务特性**:
- 用户登录时自动启动
- 失败后自动重启（最多3次）
- 允许电池供电时运行
- 无执行时间限制

### 5. Git Hooks增强

#### Pre-commit Hook (pre-commit-enhanced.sh)

**功能**: 在commit前验证Spec和规则合规性

**安装**:

```bash
# 复制hook到.git/hooks目录
cp .lingma/hooks/pre-commit-enhanced.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**检查内容**:
1. Spec文件是否存在
2. Spec完整性验证
3. 未回答的澄清问题
4. Spec状态检查
5. **规则合规性验证**（新增）

**绕过验证**（紧急情况）:

```bash
git commit --no-verify -m "your message"
```

#### Post-checkout Hook (post-checkout-enhanced.sh)

**功能**: 在checkout/switch后检查Spec状态

**安装**:

```bash
# 复制hook到.git/hooks目录
cp .lingma/hooks/post-checkout-enhanced.sh .git/hooks/post-checkout
chmod +x .git/hooks/post-checkout
```

**检查内容**:
1. Spec状态验证
2. **规则合规性检查**（新增）
3. 审计日志记录

### 6. E2E测试套件 (test-e2e-automation.py)

**功能**: 端到端测试验证整个自动化基础设施

**使用方式**:

```bash
# 运行所有测试
python .lingma/scripts/test-e2e-automation.py --all

# 运行特定测试
python .lingma/scripts/test-e2e-automation.py --test watcher
python .lingma/scripts/test-e2e-automation.py --test rule-engine
python .lingma/scripts/test-e2e-automation.py --test integration
python .lingma/scripts/test-e2e-automation.py --test git-hooks
```

**测试内容**:
1. **Spec Watcher测试**: 启动/停止、状态查询、配置重载
2. **Rule Engine测试**: 规则加载、Spec验证、特定规则检查
3. **Integration测试**: Worker启动、规则验证集成
4. **Git Hooks测试**: hook存在性、可执行性、rule-engine集成

**测试结果**: 保存到`.lingma/logs/e2e-test-results.json`

## 工作流程示例

### 场景1: 正常开发流程

```bash
# 1. 修改Spec文件
echo "- [ ] Task-001: 新功能开发" >> .lingma/specs/current-spec.md

# 2. Spec Watcher自动检测到变化并触发评估
# （如果watcher正在运行）

# 3. 手动验证规则合规性
python .lingma/scripts/rule-engine.py --validate-spec

# 4. 启动Worker处理任务
python .lingma/scripts/spec-worker-enhanced.py --start

# 5. 提交代码（pre-commit hook自动验证）
git add .
git commit -m "完成Task-001"
```

### 场景2: Windows开机自启

```powershell
# 1. 以管理员身份运行PowerShell
# 2. 安装计划任务
.\.lingma\scripts\install-windows-task.ps1 -Install

# 3. 重启计算机后，Spec Watcher会自动启动
# 4. 查看状态
.\.lingma\scripts\install-windows-task.ps1 -Status
```

### 场景3: CI/CD集成

```yaml
# .github/workflows/spec-validation.yml
name: Spec Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install watchdog
      
      - name: Validate Spec
        run: python .lingma/scripts/rule-engine.py --validate-spec
      
      - name: Run E2E Tests
        run: python .lingma/scripts/test-e2e-automation.py --all
```

## 审计日志

所有操作都会记录到`.lingma/logs/audit.log`，包括：

- Spec验证事件
- 规则检查事件
- Worker启动/停止
- 任务执行记录
- Git hook触发

**日志格式**（JSON）:

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "event_type": "spec_validation_passed",
  "worker_id": "worker-20240115103000",
  "violations_count": 0
}
```

## 故障排除

### 问题1: Watchdog未安装

**症状**: `ModuleNotFoundError: No module named 'watchdog'`

**解决**:
```bash
pip install watchdog
```

### 问题2: 权限不足（Windows计划任务）

**症状**: `Access is denied`

**解决**: 以管理员身份运行PowerShell

### 问题3: Hook不可执行

**症状**: `Permission denied`

**解决**:
```bash
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/post-checkout
```

### 问题4: Python路径问题

**症状**: `python: command not found`

**解决**:
```bash
# 检查Python是否安装
which python3
which python

# 更新PATH或创建符号链接
ln -s /usr/bin/python3 /usr/local/bin/python
```

### 问题5: 规则验证失败

**症状**: `❌ 规则验证失败：存在严重违规`

**解决**:
```bash
# 查看详细违规信息
python .lingma/scripts/rule-engine.py --validate-spec

# 根据建议修复Spec
# 重新验证
python .lingma/scripts/rule-engine.py --validate-spec
```

## 最佳实践

1. **始终运行E2E测试**: 在部署前运行完整测试套件
2. **启用Git Hooks**: 确保每次提交都经过验证
3. **定期检查审计日志**: 监控系统运行状态
4. **配置Windows计划任务**: 实现真正的自动化
5. **自定义规则**: 根据项目需求添加新的Rule文件
6. **监控Watcher状态**: 定期检查watcher是否正常运行

## 扩展开发

### 添加新规则

1. 在`.lingma/rules/`下创建新的`.md`文件
2. 添加YAML front matter元数据
3. 在`rule-engine.py`的`_apply_rule`方法中添加检查逻辑

**示例**:

```markdown
---
trigger: always_on
priority: P1
---
# 新规则名称

规则描述...
```

### 自定义Watch行为

编辑`.lingma/config/watcher-config.json`:

```json
{
  "debounce_delay": 2.0,
  "auto_trigger_evaluation": false,
  "watch_patterns": ["*.md", "*.json"],
  "exclude_patterns": ["*~", "*.tmp", "*.bak"]
}
```

### 扩展Worker功能

在`spec-worker-enhanced.py`中添加新的任务执行器：

```python
def _execute_custom_task(self, task: Dict) -> bool:
    """自定义任务执行逻辑"""
    # 实现具体逻辑
    return True
```

## 技术支持

如有问题，请查看：
- 审计日志: `.lingma/logs/audit.log`
- Watcher日志: `.lingma/logs/watcher.log`
- E2E测试结果: `.lingma/logs/e2e-test-results.json`

## 版本历史

- **v1.0** (2024-01-15): 初始版本
  - 实现spec-watcher.py
  - 实现rule-engine.py
  - 增强spec-worker.py
  - 创建Windows计划任务脚本
  - 增强Git Hooks
  - 创建E2E测试套件
