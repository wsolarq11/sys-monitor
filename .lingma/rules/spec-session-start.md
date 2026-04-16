---
trigger: always_on
priority: P0
---
# Spec-Driven Development 会话启动规则

**角色**: 每次会话开始时自动检查 spec 状态并智能响应  
**职责**: 状态检查、意图分析、进度透明化、强制验证

## 🚨 强制执行规则

**此Rule为P0优先级，每次会话开始时必须执行**

### 强制检查项

如果检测到以下情况，**立即阻止并报错**（除非用户使用 `--force-bypass`）：

1. ❌ `.lingma/specs/current-spec.md` 不存在
2. ❌ Spec 状态为 `draft` 但存在未解决的 `[NEEDS CLARIFICATION]` 标记
3. ❌ 必需组件缺失（agents/skills/rules/config 目录）
4. ❌ 关键文件缺失（AGENTS.md, automation-policy.md, memory-usage.md）
5. ❌ `.lingma/` 根目录存在冗余文档（违反单一入口原则）

### 执行流程

```python
# 伪代码 - 实际由 session-middleware.py 执行
1. 运行 .lingma/scripts/session-middleware.py
2. 如果验证失败:
   - 输出详细错误报告
   - 阻止会话继续（除非 --force-bypass）
   - 提供修复指南
3. 如果验证通过:
   - 加载 Spec 上下文
   - 显示状态摘要
   - 继续正常会话
```

## 核心流程

1. **🔍 强制验证** - 运行 session-middleware.py 进行完整性检查
2. **📖 检查 spec 状态** - 读取 `.lingma/specs/current-spec.md`
3. **🎯 分析用户意图** - 识别新功能/继续开发/需求变更/查询状态
4. **💬 生成综合响应** - 结合 spec 状态和用户消息
5. **❓ 优先处理澄清问题** - 如有 `[NEEDS CLARIFICATION]` 标记
6. **📝 记录会话日志** - 添加到 spec 实施笔记

## 响应原则

- ✅ **始终包含**: spec 状态、进度百分比、下一步建议
- ✅ **优先处理**: 阻塞性澄清问题
- ✅ **透明化**: 明确告知当前上下文
- ✅ **主动预防**: 在问题发生前检测并警告
- ❌ **禁止假设**: 不要假设用户知道当前状态
- ❌ **禁止跳过**: 不得绕过验证步骤

## 集成说明

### 与 Session Middleware 的集成

本 Rule 依赖 `.lingma/scripts/session-middleware.py` 执行实际验证。

**调用方式**:
```bash
# 标准模式（推荐）
python .lingma/scripts/session-middleware.py

# 强制绕过模式（仅调试用）
python .lingma/scripts/session-middleware.py --force-bypass

# 保存报告
python .lingma/scripts/session-middleware.py --report-output .lingma/logs/session-start.json
```

**验证内容**:
- ✅ Spec 文件存在性和可读性
- ✅ 目录结构完整性
- ✅ 关键文件存在性
- ✅ 文档冗余检测
- ✅ 临时文件检测
- ✅ Spec 状态合法性

### 失败处理策略

| 错误类型 | 处理方式 | 用户操作 |
|---------|---------|----------|
| Spec 文件缺失 | 🔴 阻断会话 | 创建或恢复 current-spec.md |
| 组件目录缺失 | 🔴 阻断会话 | 运行系统初始化脚本 |
| 关键文件缺失 | 🔴 阻断会话 | 从备份恢复或重新创建 |
| 冗余文档 | 🟡 警告但继续 | 删除冗余文件 |
| 临时文件 | 🟡 警告但继续 | 清理临时文件 |

## 详细实现

完整响应模板和异常处理见：[spec-session-start-detailed.md](../docs/architecture/spec-session-start-detailed.md)

Session Middleware 实现见：[session-middleware.py](../scripts/session-middleware.py)

## 量化标准

- Rule 文件 ≤ 3KB
- 详细内容移至 docs/
- 仅保留核心指令和引用链接
- **验证覆盖率**: 100%（所有必需组件）
- **误报率**: < 1%
- **执行时间**: < 500ms
