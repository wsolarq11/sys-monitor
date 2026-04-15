# 📋 Spec-Driven Development Skill 安装与使用指南

## 🎉 恭喜！Spec-Driven Development Skill 已创建完成

这个 Skill 将帮助您在不同会话中自动维护 spec 文档，并基于 spec 进行自主开发。

---

## 📦 已创建的文件

```
.lingma/skills/spec-driven-development/
├── SKILL.md                    # ✅ 主 Skill 定义（578 行）
├── QUICK_REFERENCE.md          # ✅ 快速参考卡片
├── examples.md                 # ✅ 完整使用示例
├── templates/
│   └── feature-spec.md         # ✅ Feature Spec 模板
└── scripts/
    ├── init-spec.sh            # ✅ 初始化脚本
    └── check-spec-status.py    # ✅ 状态检查工具
```

---

## 🚀 立即开始（3 步）

### Step 1: 运行初始化脚本

```bash
cd d:\Users\Administrator\Desktop\PowerShell_Script_Repository\FolderSizeMonitor
bash .lingma/skills/spec-driven-development/scripts/init-spec.sh
```

这将：
- ✅ 创建目录结构（`.lingma/specs/`, `spec-history/`, `templates/`）
- ✅ 安装模板文件
- ✅ 安装工具脚本
- ✅ 配置 Git 忽略规则
- ✅ 创建使用说明

### Step 2: 验证安装

```bash
# 检查目录结构
ls -R .lingma/specs/

# 测试状态检查工具
python .lingma/scripts/check-spec-status.py
```

预期输出：
```
❌ 未找到活跃的 spec 文件

💡 提示: 开始新功能时，AI 会自动创建 spec
```

### Step 3: 创建第一个 Spec

在新的对话中，告诉 AI：

```
"我需要添加一个新功能：[描述你的需求]"
```

AI 会：
1. 自动识别需要使用 spec-driven-development skill
2. 引导您澄清需求
3. 创建 spec 草案
4. 请求您确认
5. 开始自主开发

---

## 🎯 核心功能

### 1. 跨会话持久化

**问题**: 每次新会话都要重新解释项目背景？

**解决**: 
- Spec 保存在 `.lingma/specs/current-spec.md`
- 新会话开始时，AI 自动检测并加载
- 继续未完成的工作，无需重复说明

### 2. 自主开发

**问题**: 需要不断指导 AI 下一步做什么？

**解决**:
- Spec 中包含完整的任务列表
- AI 按顺序自主执行
- 仅在需要澄清时与您交互

### 3. 进度追踪

**问题**: 不知道当前进展如何？

**解决**:
```bash
# 随时查看进度
python .lingma/scripts/check-spec-status.py
```

输出示例：
```
📋 Spec 状态报告
📝 名称: 文件夹阈值告警功能
⏳ 状态: in-progress
📊 任务进度: ████████░░░░░░░░░░░░ 40.0% (4/10)
💡 下一步: Task-005: 创建阈值配置 UI 组件
```

### 4. 需求变更管理

**问题**: 开发中途需求变了怎么办？

**解决**:
- AI 评估变更影响
- 更新 spec 并记录变更原因
- 调整任务列表和预估时间
- 继续开发或重新规划

---

## 💡 使用场景示例

### 场景 1: 新功能开发

```
用户: "我需要添加文件夹大小阈值告警功能"

AI 自动:
  1. 澄清需求（仅必要时）
  2. 创建 spec 草案
  3. 请求确认
  4. 开始开发
  5. 每完成任务更新进度
  6. 完成后生成验收报告
```

### 场景 2: 跨会话恢复

```
新会话开始:

AI 自动检测:
  "👋 欢迎回来！检测到进行中的开发任务:
   
   Spec: 文件夹阈值告警
   状态: 进行中 (40%)
   
   我可以继续执行剩余任务。"

用户: "继续"

AI: 从下一个任务继续...
```

### 场景 3: 代码重构

```
用户: "我想重构文件扫描模块，提升性能"

AI:
  1. 创建 refactor spec
  2. 分析当前实现
  3. 设计优化方案
  4. 列出重构步骤
  5. 逐步执行并验证
```

### 场景 4: Bug 修复

```
用户: "发现一个 bug：大文件夹扫描时会卡死"

AI:
  1. 创建 bugfix spec
  2. 复现问题
  3. 定位根因
  4. 设计修复方案
  5. 实施并测试
  6. 添加回归测试
```

---

## 🔧 高级用法

### 自定义 Spec 模板

在 `templates/` 目录下创建自己的模板：

```bash
# 例如：创建 API 开发专用模板
cp templates/feature-spec.md templates/api-spec.md
# 编辑 api-spec.md，添加 API 特定的章节
```

### 自动化报告

设置定时任务生成周报：

```bash
# Linux/Mac crontab
0 9 * * 1 cd /path/to/project && \
  python .lingma/scripts/check-spec-status.py --summary \
  > weekly-report-$(date +\%Y\%m\%d).json

# Windows Task Scheduler
# 创建定时任务运行 PowerShell 脚本
```

### 团队协作

共享 spec 历史：

```bash
# 提交历史 spec 到 Git
git add .lingma/specs/spec-history/
git commit -m "docs: archive completed specs"

# 团队成员可以查看项目演进历史
git log --oneline .lingma/specs/spec-history/
```

---

## 📊 Spec 质量指标

定期审查以下指标：

| 指标 | 目标 | 检查方法 |
|------|------|----------|
| Spec 完成率 | > 90% | 统计 completed / total |
| 任务预估准确性 | ±20% | 对比预估 vs 实际时间 |
| 验收标准覆盖率 | 100% | 所有 AC 都有对应测试 |
| Spec 更新频率 | 每次重大变更 | 检查变更记录 |
| 实施笔记完整性 | 每个任务都有 | 检查笔记数量 |

---

## ⚠️ 注意事项

### Git 配置

`.gitignore` 已自动配置：

```gitignore
# Spec files (keep history, ignore current)
.lingma/specs/current-spec.md
!**/.lingma/specs/spec-history/**
```

**说明**:
- `current-spec.md` 不提交（避免多人编辑冲突）
- `spec-history/` 会提交（保留完整历史）

### 文件大小

- **推荐**: Spec < 500 行
- **如果超过**: 拆分成多个子 spec
- **原因**: 保持上下文窗口效率

### 多项目管理

如果您有多个项目：

```bash
# 每个项目独立维护自己的 spec
project-a/.lingma/specs/
project-b/.lingma/specs/

# AI 会根据当前工作目录自动加载对应的 spec
```

---

## 🆘 故障排除

### 问题 1: AI 没有自动使用 Spec

**症状**: 新会话中 AI 没有加载 current-spec.md

**解决**:
1. 检查文件是否存在: `ls .lingma/specs/current-spec.md`
2. 手动提醒 AI: "请检查当前的 spec 状态"
3. 确认 Skill 已正确安装

### 问题 2: 状态检查脚本失败

**症状**: `python check-spec-status.py` 报错

**解决**:
```bash
# 检查 Python 版本
python --version  # 需要 Python 3.6+

# 检查文件编码
file .lingma/specs/current-spec.md  # 应该是 UTF-8

# 手动修复编码
iconv -f gbk -t utf-8 current-spec.md > temp.md && mv temp.md current-spec.md
```

### 问题 3: Spec 与实际实现不同步

**症状**: 代码已经改了，但 spec 还是旧状态

**解决**:
1. 告诉 AI: "请同步 spec 与当前实现"
2. AI 会:
   - 检查 git diff
   - 更新任务状态
   - 添加实施笔记
   - 更新变更记录

---

## 📚 学习资源

### 必读文档

1. **[SKILL.md](SKILL.md)** - 完整的 Skill 定义和工作流程
2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 快速查阅手册
3. **[examples.md](examples.md)** - 详细的使用示例

### 实践建议

1. **第一周**: 尝试创建 1-2 个小功能的 spec
2. **第二周**: 体验跨会话恢复功能
3. **第三周**: 尝试需求变更处理
4. **第四周**: 回顾和改进流程

---

## 🎓 最佳实践总结

### ✅ Do's

- ✅ 从简单功能开始，逐步复杂化
- ✅ 保持 spec 简洁，关注 WHAT 和 WHY
- ✅ 及时更新实施笔记
- ✅ 完成后立即归档
- ✅ 定期回顾和改进流程

### ❌ Don'ts

- ❌ 不要过度设计 spec（不是技术文档）
- ❌ 不要跳过 spec（即使很小的功能）
- ❌ 不要害怕变更（spec 是活的）
- ❌ 不要忽略验收标准
- ❌ 不要让 spec 过时

---

## 🚀 下一步行动

1. **立即**: 运行初始化脚本
2. **今天**: 创建第一个 spec（选择一个简单功能）
3. **本周**: 体验完整的 spec 生命周期
4. **本月**: 建立团队规范和工作流

---

## 💬 反馈与改进

这个 Skill 会随着使用不断优化。如果您发现：

- 🐛 Bug 或问题
- 💡 改进建议
- ✨ 新的使用场景

请记录下来，我们可以一起改进这个工作流！

---

## 🎉 开始您的 Spec-Driven Development 之旅！

```bash
# 现在就运行
bash .lingma/skills/spec-driven-development/scripts/init-spec.sh

# 然后告诉 AI 您的需求
"我需要 [功能描述]..."
```

祝您开发愉快！🚀
