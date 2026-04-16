# Git Hooks 使用指南

**版本**: 1.0  
**更新日期**: 2026-04-16  
**状态**: ✅ Production Ready

---

## 📋 目录

- [概述](#概述)
- [已安装的Hooks](#已安装的hooks)
- [安装与配置](#安装与配置)
- [详细功能说明](#详细功能说明)
- [故障排查](#故障排查)
- [最佳实践](#最佳实践)
- [高级用法](#高级用法)

---

## 概述

本系统实现了完整的Git Hook防护体系，确保Spec驱动开发流程的严格执行。所有提交和推送都会经过自动化验证，防止不完整的Spec、未通过的测试或不安全的代码进入仓库。

### 核心目标

1. **强制Spec完整性** - 每个提交必须有对应的有效Spec
2. **自动化质量检查** - 测试、构建、安全扫描自动执行
3. **双向Agent同步** - Commit后自动通知AI Agent更新上下文
4. **审计追踪** - 所有操作记录到审计日志

### 架构概览

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Developer   │─────▶│  Git Hooks   │─────▶│  Validation  │
│  (commit/    │      │  (pre-commit,│      │  & Blocking  │
│   push)      │      │   pre-push,  │      │              │
└──────────────┘      │   post-      │      └──────────────┘
                      │   commit)    │             │
                      └──────────────┘             │
                             │                     │
                             ▼                     ▼
                      ┌──────────────┐      ┌──────────────┐
                      │  AI Agent    │◀─────│  Audit Log   │
                      │  (context    │      │  (.lingma/   │
                      │   update)    │      │   logs/)     │
                      └──────────────┘      └──────────────┘
```

---

## 已安装的Hooks

### 1. Pre-Commit Hook

**触发时机**: `git commit` 执行时（在commit消息编辑器打开之前）

**文件位置**: `.git/hooks/pre-commit` (由 `.lingma/hooks/pre-commit-enhanced.sh` 安装)

**检查项**:
1. ✅ Spec文件存在性检查
2. ✅ Spec状态验证（必须是in-progress或review）
3. ✅ 未回答的澄清问题检测
4. ✅ Rule合规性验证
5. ✅ 代码质量检查（eslint/black等）
6. ✅ 敏感信息扫描（gitleaks）

**阻止条件**:
- Spec文件不存在
- Spec状态不是in-progress或review
- 存在[NEEDS CLARIFICATION]标记
- 规则验证出现ERROR级别违规

**绕过方式**:
```bash
git commit --no-verify -m "emergency fix"
```

**示例输出**:
```
🔍 执行Spec强制验证...
   正在验证Spec完整性...
   正在验证规则合规性...
✅ 规则验证通过
✅ Spec验证通过

Spec摘要:
  状态: in-progress
  优先级: high
  任务进度: 3/5 (60%)
```

---

### 2. Pre-Push Hook

**触发时机**: `git push` 执行时（在实际推送之前）

**文件位置**: `.git/hooks/pre-push` (由 `.lingma/hooks/pre-push-enhanced.sh` 安装)

**检查项**:
1. ✅ Spec状态验证（必须是review或done）
2. ✅ 完整测试套件运行
3. ✅ 构建验证
4. ✅ CHANGELOG更新检查
5. ✅ 版本号一致性检查
6. ✅ 安全扫描（gitleaks + trivy）

**阻止条件**:
- Spec状态不是review或done
- 测试失败
- 构建失败
- 发现高危安全漏洞
- 版本号不一致

**绕过方式**:
```bash
git push --no-verify
```

**示例输出**:
```
🚀 执行Pre-Push验证...

   [1/6] 检查Spec状态...
   ✅ Spec状态: review

   [2/6] 运行测试套件...
   ✅ 测试通过

   [3/6] 验证构建...
   ✅ 构建成功

   [4/6] 检查CHANGELOG...
   ✅ CHANGELOG已更新

   [5/6] 检查版本号...
   Cargo.toml版本: 2.0.0
   package.json版本: 2.0.0
   ✅ 版本号检查通过

   [6/6] 安全扫描...
   ✅ 未发现敏感信息

✅ Pre-Push验证全部通过

📊 验证摘要:
  ✓ Spec状态: OK
  ✓ 测试套件: PASSED
  ✓ 构建验证: SUCCESS
  ✓ CHANGELOG: CHECKED
  ✓ 版本号: CONSISTENT
  ✓ 安全扫描: CLEAN

🚀 准备推送到远程仓库...
```

---

### 3. Post-Commit Hook

**触发时机**: `git commit` 成功后

**文件位置**: `.git/hooks/post-commit` (由 `.lingma/hooks/post-commit.sh` 安装)

**功能**:
1. 📤 异步通知AI Agent新commit
2. 💾 更新最后提交状态文件
3. 📝 记录审计日志
4. ℹ️ 显示当前Spec状态

**特点**:
- ⚡ 非阻塞式执行（后台运行）
- 🔄 支持离线队列（Agent离线时）
- 📋 多种通知方式（HTTP / 文件队列）

**示例输出**:
```
📤 Post-Commit: 准备通知AI Agent...
   ✅ 已成功通知AI Agent
   ✅ 已更新最后提交记录
   ℹ️  当前Spec状态: in-progress
```

---

### 4. Post-Checkout Hook

**触发时机**: `git checkout` 或 `git switch` 后

**文件位置**: `.git/hooks/post-checkout` (由 `.lingma/hooks/post-checkout-enhanced.sh` 安装)

**功能**:
1. 📂 检测分支切换
2. 💾 保存当前会话状态
3. 🔄 加载目标分支的Spec
4. 🔔 提示用户当前状态

**示例输出**:
```
🔄 检测到分支切换: main → feature/new-ui
   ✅ 已保存当前会话状态
   📂 已加载目标分支Spec
   ℹ️  当前Spec: UI重构 v2.0 (状态: in-progress)
```

---

## 安装与配置

### 快速安装

```bash
# 一键安装所有hooks
bash .lingma/scripts/install-hooks.sh
```

**安装过程**:
1. 备份现有hooks（如果有）
2. 复制增强版hooks到 `.git/hooks/`
3. 设置执行权限
4. 验证安装完整性

### 手动安装

如果自动安装失败，可以手动安装：

```bash
# 1. 复制hook文件
cp .lingma/hooks/pre-commit-enhanced.sh .git/hooks/pre-commit
cp .lingma/hooks/pre-push-enhanced.sh .git/hooks/pre-push
cp .lingma/hooks/post-commit.sh .git/hooks/post-commit
cp .lingma/hooks/post-checkout-enhanced.sh .git/hooks/post-checkout

# 2. 设置执行权限
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
chmod +x .git/hooks/post-commit
chmod +x .git/hooks/post-checkout

# 3. 验证
ls -la .git/hooks/ | grep -E "pre-commit|pre-push|post-commit|post-checkout"
```

### 验证安装

```bash
# 检查hooks是否存在且可执行
test -x .git/hooks/pre-commit && echo "✅ pre-commit OK" || echo "❌ pre-commit FAILED"
test -x .git/hooks/pre-push && echo "✅ pre-push OK" || echo "❌ pre-push FAILED"
test -x .git/hooks/post-commit && echo "✅ post-commit OK" || echo "❌ post-commit FAILED"
test -x .git/hooks/post-checkout && echo "✅ post-checkout OK" || echo "❌ post-checkout FAILED"
```

### 卸载Hooks

```bash
# 方法1: 删除hooks
rm .git/hooks/pre-commit
rm .git/hooks/pre-push
rm .git/hooks/post-commit
rm .git/hooks/post-checkout

# 方法2: 恢复备份（如果安装时有备份）
BACKUP_DIR=".lingma/backups/git-hooks-YYYYMMDD-HHMMSS"
cp $BACKUP_DIR/* .git/hooks/
```

---

## 详细功能说明

### Pre-Commit 验证流程

```
开始
  ↓
检查Spec文件是否存在？
  ├─ 否 → ❌ 阻止提交
  └─ 是 ↓
检查Spec状态是否为in-progress/review？
  ├─ 否 → ❌ 阻止提交
  └─ 是 ↓
运行spec-validator.py
  ├─ 失败 → ❌ 阻止提交
  └─ 成功 ↓
检查是否有未回答的澄清问题？
  ├─ 是 → ❌ 阻止提交
  └─ 否 ↓
调用rule-engine验证规则
  ├─ ERROR级别违规 → ❌ 阻止提交
  ├─ WARNING级别违规 → ⚠️ 警告但允许
  └─ 无违规 ↓
✅ 允许提交
```

### Pre-Push 验证流程

```
开始
  ↓
检查Spec状态是否为review/done？
  ├─ 否 → ❌ 阻止推送
  └─ 是 ↓
运行测试套件（npm test / pytest / cargo test）
  ├─ 失败 → ❌ 阻止推送
  └─ 通过 ↓
运行构建（npm run build / cargo build）
  ├─ 失败 → ❌ 阻止推送
  └─ 成功 ↓
检查CHANGELOG是否更新？
  ├─ 否 → ⚠️ 警告但允许
  └─ 是 ↓
检查版本号一致性
  ├─ 不一致 → ❌ 阻止推送
  └─ 一致 ↓
运行安全扫描（gitleaks + trivy）
  ├─ 发现高危问题 → ❌ 阻止推送
  ├─ 发现低危问题 → ⚠️ 警告但允许
  └─ 无问题 ↓
✅ 允许推送
```

### Post-Commit 通知流程

```
Commit成功
  ↓
构建通知payload
  ↓
Agent服务是否可用？
  ├─ 是 → HTTP POST通知（异步）
  │        ↓
  │      记录成功日志
  └─ 否 → 写入文件队列
           ↓
         记录队列日志
  ↓
更新last-commit.json
  ↓
显示Spec状态摘要
  ↓
完成（不阻塞）
```

---

## 故障排查

### 常见问题

#### 问题1: Hook未执行

**症状**: 提交或推送时没有看到验证输出

**可能原因**:
1. Hook文件不存在
2. Hook文件没有执行权限
3. Hook文件有语法错误

**解决方案**:
```bash
# 1. 检查文件存在性
ls -la .git/hooks/pre-commit

# 2. 检查执行权限
chmod +x .git/hooks/pre-commit

# 3. 测试hook脚本
bash .git/hooks/pre-commit

# 4. 重新安装
bash .lingma/scripts/install-hooks.sh
```

---

#### 问题2: Pre-Commit误报

**症状**: Spec明明正确但被阻止

**可能原因**:
1. spec-validator.py脚本bug
2. Spec格式不符合预期
3. 编码问题

**解决方案**:
```bash
# 1. 查看详细错误信息
cat .lingma/logs/audit.log | tail -20

# 2. 手动运行验证器
python3 .lingma/scripts/spec-validator.py --mode pre-commit

# 3. 临时绕过（紧急情况）
git commit --no-verify -m "emergency fix"

# 4. 修复Spec后重新提交
```

---

#### 问题3: Pre-Push测试超时

**症状**: 推送时测试运行时间过长

**可能原因**:
1. 测试用例过多
2. 测试中有死循环
3. 资源不足

**解决方案**:
```bash
# 1. 本地先运行测试，确认问题
npm run test:ci

# 2. 优化测试用例
#    - 减少E2E测试数量
#    - 使用mock替代外部依赖
#    - 并行执行测试

# 3. 临时增加超时时间（修改hook脚本）
#    在pre-push-enhanced.sh中修改:
#    TIMEOUT_SECONDS=60  # 从30改为60

# 4. 紧急推送（不推荐）
git push --no-verify
```

---

#### 问题4: Post-Commit通知失败

**症状**: 看到"Agent通知失败"警告

**可能原因**:
1. Agent服务未启动
2. 端口3000被占用
3. 网络问题

**解决方案**:
```bash
# 1. 检查Agent服务状态
curl http://localhost:3000/api/health

# 2. 启动Agent服务
#    （根据你的Agent实现方式）

# 3. 查看队列文件
ls -la .lingma/worker/queue/

# 4. 手动处理队列
for file in .lingma/worker/queue/*.json; do
    curl -X POST http://localhost:3000/api/agent/notify \
         -H "Content-Type: application/json" \
         -d @$file
    rm $file
done
```

---

#### 问题5: 审计日志过大

**症状**: `.lingma/logs/audit.log` 文件超过100MB

**解决方案**:
```bash
# 1. 查看日志大小
du -h .lingma/logs/audit.log

# 2. 清理旧日志（保留最近30天）
python3 -c "
from datetime import datetime, timedelta
import json

cutoff = datetime.utcnow() - timedelta(days=30)
with open('.lingma/logs/audit.log', 'r') as f:
    lines = f.readlines()

recent_lines = []
for line in lines:
    try:
        log = json.loads(line)
        timestamp = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00')).replace(tzinfo=None)
        if timestamp >= cutoff:
            recent_lines.append(line)
    except:
        pass

with open('.lingma/logs/audit.log', 'w') as f:
    f.writelines(recent_lines)

print(f'清理完成: {len(lines)} -> {len(recent_lines)} 条记录')
"

# 3. 设置日志轮转（cron job）
#    添加到crontab:
#    0 0 * * 0 find /path/to/.lingma/logs -name "audit.log.*" -mtime +90 -delete
```

---

### 调试技巧

#### 启用详细日志

```bash
# 在hook脚本开头添加
set -x  # 开启调试模式

# 或在运行时
bash -x .git/hooks/pre-commit
```

#### 查看实时日志

```bash
# 监控审计日志
tail -f .lingma/logs/audit.log

# 过滤特定事件
grep "pre-commit" .lingma/logs/audit.log | tail -20
```

#### 模拟Hook执行

```bash
# 测试pre-commit
echo "test content" > .lingma/specs/current-spec.md
bash .git/hooks/pre-commit

# 测试pre-push
bash .git/hooks/pre-push origin main
```

---

## 最佳实践

### 1. 定期审查审计日志

```bash
# 每周生成一次报告
python3 .lingma/scripts/metrics-collector.py --output weekly-report.md

# 查看关键指标
cat weekly-report.md | grep -A 10 "质量评估"
```

### 2. 保持Spec更新

```bash
# 每次会话结束前
git add .lingma/specs/current-spec.md
git commit -m "chore(spec): update progress [skip ci]"
```

### 3. 合理使用--no-verify

```bash
# ✅ 适用场景
git commit --no-verify -m "fix: critical hotfix for production"

# ❌ 不适用场景
git commit --no-verify -m "feat: add new feature"  # 应该走正常流程
```

### 4. 团队协作规范

```markdown
团队约定:
- 禁止force-push到main分支
- 所有PR必须通过pre-push验证
- 紧急修复后必须补全Spec
- 每周review审计日志
```

### 5. 性能优化

```bash
# 缓存测试结果（如果支持）
export TEST_CACHE_ENABLED=true

# 并行执行检查
# 修改hook脚本，使用&后台运行独立检查
```

---

## 高级用法

### 自定义验证规则

编辑 `.lingma/rules/custom-rules.yaml`:

```yaml
custom_rules:
  - id: REQUIRE_TESTS_FOR_FEATURE
    description: "新功能必须包含测试"
    condition: "spec.type == 'feature' and tests.count == 0"
    severity: ERROR
    message: "新功能必须编写单元测试"
    
  - id: MAX_SPEC_AGE
    description: "Spec不能超过7天未更新"
    condition: "spec.last_updated < now() - 7.days"
    severity: WARNING
    message: "Spec已超过7天未更新，请刷新状态"
```

### 集成CI/CD

`.github/workflows/hook-validation.yml`:

```yaml
name: Hook Validation
on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Hooks
        run: bash .lingma/scripts/install-hooks.sh
      
      - name: Run Pre-Commit
        run: bash .git/hooks/pre-commit
      
      - name: Run Pre-Push
        run: bash .git/hooks/pre-push origin main
```

### 编程方式调用

Python示例:

```python
import subprocess
import json

def trigger_pre_commit():
    """以编程方式触发pre-commit验证"""
    result = subprocess.run(
        ['bash', '.git/hooks/pre-commit'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ 验证通过")
        return True
    else:
        print("❌ 验证失败")
        print(result.stderr)
        return False

def get_audit_logs(last_n=10):
    """获取最近的审计日志"""
    with open('.lingma/logs/audit.log', 'r') as f:
        lines = f.readlines()
    
    logs = []
    for line in lines[-last_n:]:
        logs.append(json.loads(line))
    
    return logs
```

### 自定义通知渠道

修改 `post-commit.sh`:

```bash
# Slack通知
curl -X POST "$SLACK_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"New commit: $COMMIT_MSG\",
    \"attachments\": [{
      \"color\": \"#36a64f\",
      \"fields\": [
        {\"title\": \"Author\", \"value\": \"$COMMIT_AUTHOR\", \"short\": true},
        {\"title\": \"Hash\", \"value\": \"${COMMIT_HASH:0:8}\", \"short\": true}
      ]
    }]
  }"

# Discord通知
# ...

# 企业微信通知
# ...
```

---

## 📊 度量与监控

### 运行度量收集器

```bash
# 生成文本报告
python3 .lingma/scripts/metrics-collector.py

# 生成JSON数据
python3 .lingma/scripts/metrics-collector.py --json

# 保存到文件
python3 .lingma/scripts/metrics-collector.py --output metrics.md
```

### 关键指标

| 指标 | 健康范围 | 说明 |
|------|---------|------|
| Pre-Commit阻止率 | 5-15% | 过低可能验证不严，过高可能模板复杂 |
| Pre-Push阻止率 | 2-10% | 应该低于pre-commit |
| Spec完成率 | >70% | 反映任务分解合理性 |
| 平均澄清问题数 | <3 | 反映Spec质量 |
| 质量评分 | >80 | 综合评估 |

---

## 🔗 相关资源

- [Spec驱动开发指南](../skills/spec-driven-development/SKILL.md)
- [AI Agent工作流最佳实践](./AI_AGENT_WORKFLOW_BEST_PRACTICES_2026.md)
- [MCP配置安全指南](./MCP_SECURITY_GUIDE.md)
- [系统架构文档](./architecture/ARCHITECTURE.md)

---

## ❓ FAQ

**Q: 可以在CI环境中禁用hooks吗？**  
A: 可以，设置环境变量 `SKIP_HOOKS=true`，或在CI中使用 `--no-verify`。

**Q: 如何为不同分支设置不同的验证规则？**  
A: 在hook脚本中添加分支判断逻辑：
```bash
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" = "main" ]; then
    # 严格验证
else
    # 宽松验证
fi
```

**Q: Hook执行速度慢怎么办？**  
A: 
1. 优化验证脚本性能
2. 使用缓存机制
3. 并行执行独立检查
4. 考虑增量验证

**Q: 团队成员不使用hooks怎么办？**  
A: 
1. 在README中明确说明
2. CI中重复验证
3. Code Review时检查
4. 团队培训

---

*最后更新: 2026-04-16*  
*维护者: AI Agent Team*
