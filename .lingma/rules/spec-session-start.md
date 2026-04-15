---
trigger: always_on
---
# Spec-Driven Development 会话启动规则

**角色**: 每次会话开始时自动检查 spec 状态并智能响应  
**职责**: 状态检查、意图分析、进度透明化

## 核心流程

1. **检查 spec 状态** - 读取 `.lingma/specs/current-spec.md`
2. **分析用户意图** - 识别新功能/继续开发/需求变更/查询状态
3. **生成综合响应** - 结合 spec 状态和用户消息
4. **优先处理澄清问题** - 如有 `[NEEDS CLARIFICATION]` 标记
5. **记录会话日志** - 添加到 spec 实施笔记

## 响应原则

- ✅ **始终包含**: spec 状态、进度百分比、下一步建议
- ✅ **优先处理**: 阻塞性澄清问题
- ✅ **透明化**: 明确告知当前上下文
- ❌ **禁止假设**: 不要假设用户知道当前状态

## 详细实现

完整响应模板和异常处理见：[spec-session-start-detailed.md](../docs/architecture/spec-session-start-detailed.md)

## 量化标准

- Rule 文件 ≤ 3KB（当前需优化）
- 详细内容移至 docs/
- 仅保留核心指令和引用链接
