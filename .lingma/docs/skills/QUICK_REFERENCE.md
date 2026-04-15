# Spec-Driven Development 快速参考

## 🚀 快速开始

```bash
# 1. 初始化
bash .lingma/skills/spec-driven-development/scripts/init-spec.sh

# 2. 创建 spec（与 AI 对话）
"我需要添加 [功能描述]"

# 3. 检查状态
python .lingma/scripts/check-spec-status.py
```

---

## 📋 Spec 生命周期

```
draft → approved → in-progress → completed
   ↓                    ↓
cancelled          (归档到 spec-history/)
```

---

## 🎯 核心原则

| 原则 | 说明 |
|------|------|
| **Spec 即真相** | 所有开发基于 spec |
| **跨会话持久化** | Spec 在会话间保持 |
| **自主开发** | AI 独立执行任务 |
| **最小交互** | 仅在需要澄清时询问 |

---

## 📝 Spec 关键部分

### 必须包含
- ✅ 成功标准（可衡量）
- ✅ 验收标准（AC-001, AC-002...）
- ✅ 任务分解（< 4h 每个）
- ✅ 技术方案概要

### 可选但推荐
- ⭐ 风险评估
- ⭐ 性能要求
- ⭐ 测试策略

---

## 🔧 常用命令

```bash
# 检查 spec 状态
python .lingma/scripts/check-spec-status.py

# 生成 JSON 报告
python .lingma/scripts/check-spec-status.py --summary

# 归档完成的 spec
mv .lingma/specs/current-spec.md \
   .lingma/specs/spec-history/$(date +%Y-%m-%d)-feature-name.md

# 查看所有历史 spec
ls -lt .lingma/specs/spec-history/
```

---

## 💬 与 AI 交互模式

### 模式 1: 创建新 Spec
```
用户: "我需要 [功能描述]"
AI: 澄清需求 → 创建 spec 草案 → 请求确认
```

### 模式 2: 继续开发
```
用户: "继续" 或 "下一步"
AI: 加载 spec → 执行下一个任务 → 更新进度
```

### 模式 3: 查询进度
```
用户: "进度如何？" 或 "当前状态"
AI: 显示 spec 状态报告
```

### 模式 4: 需求变更
```
用户: "我想修改..."
AI: 评估影响 → 更新 spec → 继续或重新规划
```

---

## ⚠️ 何时需要用户确认

AI 会在以下情况暂停并询问：

- ❓ Spec 中有 `[NEEDS CLARIFICATION]`
- ❓ 需求相互矛盾
- ❓ 技术实现超出预期 (> 2x 时间)
- ❓ 发现重大安全风险
- ❓ 需要改变已批准的架构

其他情况：**AI 自主决策并记录**

---

## 📊 任务状态标记

```markdown
- [ ] Task-001: 未开始
- [~] Task-002: 进行中（可选）
- [x] Task-003: 已完成
```

---

## 🎨 实施笔记模板

```markdown
### 实施笔记 - YYYY-MM-DD HH:mm

**完成**: [任务描述]

**关键决策**:
- [决策]: [理由]

**遇到的问题**:
- 问题: [描述]
- 解决: [方案]

**测试结果**:
- 单元测试: X/Y 通过

**下一步**: [计划]
```

---

## 🔍 Spec 质量检查清单

开始前确认：
- [ ] 成功标准可衡量
- [ ] 验收标准具体且可测试
- [ ] 任务粒度合理（2-4h）
- [ ] 技术方案可行
- [ ] 风险已识别

---

## 📁 文件结构

```
.lingma/
├── specs/
│   ├── current-spec.md          # 当前活跃（不提交 Git）
│   ├── spec-history/            # 历史记录（提交 Git）
│   └── templates/               # 模板
├── scripts/
│   └── check-spec-status.py     # 状态检查工具
└── skills/
    └── spec-driven-development/
        ├── SKILL.md             # Skill 定义
        ├── examples.md          # 使用示例
        └── scripts/
            └── init-spec.sh     # 初始化脚本
```

---

## 🎯 Git Commit 规范

```bash
# Spec 相关
docs: create spec for [feature]
docs: update spec for [feature] - [change]

# 代码实现（引用 spec）
feat: implement [feature] (ref: spec#FR-001)
fix: resolve [issue] (ref: spec#FR-002)

# 任务完成
chore: complete Task-003 from spec
```

---

## 💡 最佳实践

### ✅ 推荐
- 保持 spec 简洁（< 500 行）
- 及时更新实施笔记
- 完成后立即归档
- 定期回顾和改进

### ❌ 避免
- Spec 过于详细（逐行代码）
- 实现偏离 spec 但不更新
- 每个小决策都问用户
- 忽略验收标准

---

## 🔗 相关链接

- [完整文档](SKILL.md)
- [使用示例](examples.md)
- [Feature 模板](templates/feature-spec.md)

---

## 🆘 常见问题

**Q: Spec 太长怎么办？**  
A: 拆分成多个小 spec 或使用子任务

**Q: 实现时发现 spec 有误？**  
A: 更新 spec，记录原因，必要时询问用户

**Q: 可以并行多个 spec 吗？**  
A: 可以，但建议专注一个，其他的标记为 paused

**Q: 如何追踪团队效率？**  
A: 分析 spec-history 中的完成时间和偏差

---

**记住**: Spec 是活的文档，保持准确性比严格遵守更重要！
