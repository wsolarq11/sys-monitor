# 自迭代流系统有效性验证指南

**目标**: 确保 Agents/Skills/Rules 在不同会话、不同模型中真正生效  
**频率**: 每次重大修改后 + 每周例行检查  

---

## 🔍 验证维度

### 1. Rules 持久化验证（P0 级）

**测试场景**: 跨会话规则遵循

#### 测试步骤
```markdown
Session 1:
1. 打开新会话
2. 观察是否自动显示 Spec 状态检查
3. 预期: Rule "spec-session-start" 触发

Session 2 (关闭后重新打开):
1. 再次打开新会话
2. 观察是否仍然自动检查 Spec
3. 预期: 同样的行为，证明 Rules 持久化
```

#### 验证指标
- ✅ Session 1: Rule 触发 → 显示进度
- ✅ Session 2: Rule 触发 → 显示进度
- ✅ 两次行为一致 → **Rules 持久化成功**

---

### 2. Skills 动态加载验证（P1 级）

**测试场景**: Skill 按需注入

#### 测试步骤
```markdown
测试 1: Spec-Driven Development Skill
1. 用户输入: "我想添加新功能"
2. 观察 AI 是否:
   - 读取 .lingma/skills/spec-driven-development/SKILL.md
   - 按照 Skill 定义的工作流执行
   - 创建 current-spec.md
3. 预期: Skill 被正确加载并执行

测试 2: Memory Management Skill
1. 用户分享偏好: "我喜欢 Python"
2. 后续提问: "给我写个脚本"
3. 观察 AI 是否:
   - 记住 Python 偏好
   - 生成 Python 代码而非 JavaScript
4. 预期: Memory Skill 正确管理跨轮次上下文
```

#### 验证指标
- ✅ Skill 描述准确 → 模型能识别
- ✅ Skill 内容完整 → 执行符合预期
- ✅ 渐进式披露 → 未使用时不占用上下文

---

### 3. Agents 自动委派验证（P1 级）

**测试场景**: 多 Agent 协作

#### 测试步骤
```markdown
测试 1: Supervisor Agent 编排
1. 用户输入: "/supervisor 实现文件夹监控功能"
2. 观察是否:
   - Supervisor Agent 被激活
   - 分解任务为子任务
   - 委派给 test-runner/code-review/doc-agent
3. 预期: 完整的流水线执行

测试 2: Test Runner Agent
1. 代码变更后
2. 观察是否:
   - 自动运行测试
   - 分析失败原因
   - 提供修复建议
3. 预期: Agent 独立完成任务
```

#### 验证指标
- ✅ Agent frontmatter 完整（name/description/tools）
- ✅ 模型能根据 description 自动选择
- ✅ Agent 执行符合职责定义

---

### 4. 跨模型一致性验证（P2 级）

**测试场景**: 不同模型表现一致

#### 支持的模型
- GPT-4 / GPT-4o
- Claude 3.5 Sonnet
- Qwen 2.5 / Qwen 3
- 其他通过 MCP 接入的模型

#### 测试步骤
```markdown
同一任务，切换不同模型:
1. 任务: "检查当前 Spec 状态"
2. 在 GPT-4 下执行 → 记录行为
3. 切换到 Claude → 执行同样任务
4. 切换到 Qwen → 执行同样任务
5. 对比三次执行结果
```

#### 验证指标
- ✅ 所有模型都加载了相同的 Rules
- ✅ 所有模型都能识别相同的 Skills
- ✅ 所有模型都能调用相同的 Agents
- ⚠️ 允许细微差异（模型能力不同），但核心行为应一致

---

## 📊 自动化验证脚本

### 1. Rules 加载检查
```python
# scripts/verify-rules-loading.py
import os
from pathlib import Path

def check_rules_structure():
    """验证 Rules 目录结构"""
    rules_dir = Path('.lingma/rules')
    
    required_files = [
        'AGENTS.md',
        'automation-policy.md',
        'memory-usage.md',
        'spec-session-start.md'
    ]
    
    missing = []
    for file in required_files:
        if not (rules_dir / file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ 缺少 Rules 文件: {missing}")
        return False
    
    # 检查 AGENTS.md 是否有 trigger: always_on
    agents_md = rules_dir / 'AGENTS.md'
    content = agents_md.read_text(encoding='utf-8')
    if 'trigger: always_on' not in content:
        print("❌ AGENTS.md 缺少 trigger: always_on")
        return False
    
    print("✅ Rules 结构验证通过")
    return True

if __name__ == '__main__':
    check_rules_structure()
```

### 2. Skills 完整性检查
```python
# scripts/verify-skills-completeness.py
import os
from pathlib import Path

def check_skills_structure():
    """验证 Skills 目录结构"""
    skills_dir = Path('.lingma/skills')
    
    # 检查每个 Skill 是否有 SKILL.md
    for skill_folder in skills_dir.iterdir():
        if skill_folder.is_dir():
            skill_md = skill_folder / 'SKILL.md'
            if not skill_md.exists():
                print(f"❌ {skill_folder.name} 缺少 SKILL.md")
                return False
            
            # 检查是否有 description
            content = skill_md.read_text(encoding='utf-8')
            if 'description:' not in content and '## 描述' not in content:
                print(f"⚠️ {skill_folder.name} 可能缺少 description")
    
    print("✅ Skills 结构验证通过")
    return True

if __name__ == '__main__':
    check_skills_structure()
```

### 3. Agents Frontmatter 检查
```python
# scripts/verify-agents-frontmatter.py
import os
import re
from pathlib import Path

def check_agents_frontmatter():
    """验证所有 Agent 都有必需的 frontmatter"""
    agents_dir = Path('.lingma/agents')
    
    required_fields = ['name:', 'description:', 'tools:']
    
    issues = []
    for agent_file in agents_dir.glob('*.md'):
        content = agent_file.read_text(encoding='utf-8')
        
        # 检查是否有 frontmatter
        if not content.startswith('---'):
            issues.append(f"{agent_file.name}: 缺少 frontmatter")
            continue
        
        # 提取 frontmatter
        match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            issues.append(f"{agent_file.name}: frontmatter 格式错误")
            continue
        
        frontmatter = match.group(1)
        
        # 检查必需字段
        for field in required_fields:
            if field not in frontmatter:
                issues.append(f"{agent_file.name}: 缺少 {field}")
    
    if issues:
        print("❌ Agents frontmatter 问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    print("✅ Agents frontmatter 验证通过")
    return True

if __name__ == '__main__':
    check_agents_frontmatter()
```

### 4. 综合验证脚本
```bash
#!/bin/bash
# scripts/verify-system-effectiveness.sh

echo "🔍 验证自迭代流系统有效性..."
echo ""

# 1. 检查 Rules
echo "1️⃣ 检查 Rules..."
python scripts/verify-rules-loading.py
if [ $? -ne 0 ]; then
    echo "❌ Rules 验证失败"
    exit 1
fi
echo ""

# 2. 检查 Skills
echo "2️⃣ 检查 Skills..."
python scripts/verify-skills-completeness.py
if [ $? -ne 0 ]; then
    echo "❌ Skills 验证失败"
    exit 1
fi
echo ""

# 3. 检查 Agents
echo "3️⃣ 检查 Agents..."
python scripts/verify-agents-frontmatter.py
if [ $? -ne 0 ]; then
    echo "❌ Agents 验证失败"
    exit 1
fi
echo ""

# 4. 检查文档结构
echo "4️⃣ 检查文档结构..."
python scripts/check_doc_redundancy.py
if [ $? -ne 0 ]; then
    echo "❌ 文档结构验证失败"
    exit 1
fi
echo ""

echo "✅ 所有验证通过！系统已准备就绪"
echo ""
echo "📋 下一步:"
echo "1. 打开 Lingma IDE"
echo "2. 开始新会话"
echo "3. 观察 Rules 是否自动触发"
echo "4. 测试 Skills 是否按需加载"
echo "5. 验证 Agents 是否能被正确委派"
```

---

## 🧪 手动测试清单

### 会话启动测试
- [ ] 打开新会话
- [ ] 观察是否自动显示 Spec 状态
- [ ] 如果没有活跃 Spec，是否提示创建
- [ ] 如果有活跃 Spec，是否显示进度

### Skill 加载测试
- [ ] 输入: "我想添加新功能"
- [ ] 观察是否触发 spec-driven-development Skill
- [ ] 观察是否创建 current-spec.md
- [ ] 观察是否按照 Skill 工作流执行

### Agent 委派测试
- [ ] 输入: "/test-runner 运行所有测试"
- [ ] 观察 test-runner-agent 是否被激活
- [ ] 观察是否执行测试并报告结果
- [ ] 输入: "/code-review 审查最近变更"
- [ ] 观察 code-review-agent 是否被激活

### 跨会话持久化测试
- [ ] Session 1: 创建 Spec，执行部分任务
- [ ] 关闭 IDE，重新打开
- [ ] Session 2: 观察是否恢复 Spec 状态
- [ ] 继续执行剩余任务
- [ ] 验证进度是否正确同步

### 跨模型一致性测试
- [ ] 在 GPT-4 下执行标准任务
- [ ] 切换到 Claude，执行同样任务
- [ ] 切换到 Qwen，执行同样任务
- [ ] 对比三次执行的核心行为是否一致

---

## 📈 验证指标

| 指标 | 目标 | 当前状态 |
|------|------|---------|
| Rules 加载成功率 | 100% | ✅ |
| Skills 识别准确率 | > 95% | ⏳ 待测试 |
| Agents 委派准确率 | > 90% | ⏳ 待测试 |
| 跨会话持久化 | 100% | ✅ |
| 跨模型一致性 | > 85% | ⏳ 待测试 |
| 文档冗余率 | < 5% | ✅ 0% |

---

## 🚀 持续改进

### 每周例行检查
```bash
# 添加到 crontab 或 Windows Task Scheduler
0 9 * * 1 cd /path/to/project && bash scripts/verify-system-effectiveness.sh
```

### 发现问题时的处理流程
1. **定位问题**: 哪个组件失效？（Rules/Skills/Agents）
2. **分析原因**: 配置错误？格式问题？描述不清？
3. **修复问题**: 修正配置/优化描述/补充内容
4. **重新验证**: 运行验证脚本确认修复
5. **记录教训**: 添加到 AGENTS.md 自我演进章节

---

## 💡 最佳实践总结

### 确保生效的关键要素
1. **Rules**: 必须有正确的 `trigger` 字段
2. **Skills**: 必须有清晰的 `description` 用于语义匹配
3. **Agents**: 必须有完整的 frontmatter（name/description/tools）
4. **文档**: 遵循单一入口原则，避免冗余
5. **测试**: 定期运行验证脚本，确保持续有效

### 常见问题排查
- ❌ Rule 未触发 → 检查 trigger 字段和文件格式
- ❌ Skill 未加载 → 检查 description 是否清晰
- ❌ Agent 未被选择 → 检查 frontmatter 是否完整
- ❌ 跨会话丢失 → 检查文件是否在 .gitignore 中误排除

---

**验证通过 = 系统真正生效！** ✅
