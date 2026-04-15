# 文档冗余检测规则

**目标**: 防止在 `.lingma/` 根目录创建多个入口文档  
**触发**: Git pre-commit hook + 手动检查  

---

## ❌ 禁止行为

### 1. 根目录禁止放置多个入口文档
```
.lingma/
├── README.md          ✅ 允许（唯一入口）
├── QUICK_START.md     ❌ 禁止 → 移至 docs/guides/
├── SYSTEM_ARCHITECTURE.md  ❌ 禁止 → 移至 docs/architecture/
├── GUIDE.md           ❌ 禁止 → 移至 docs/guides/
└── ARCHITECTURE.md    ❌ 禁止 → 移至 docs/architecture/
```

### 2. 功能目录禁止放置 README
```
.lingma/agents/README.md       ❌ 禁止
.lingma/rules/README.md        ❌ 禁止  
.lingma/skills/README.md       ❌ 禁止
.lingma/mcp-templates/README.md ❌ 禁止
```

**原因**: 会被系统误识别为 Agent/Rule/Skill 实例

---

## ✅ 正确做法

### 单一入口地图模式
```
.lingma/
├── README.md              # 唯一入口，精简地图（≤800字）
│                          # 仅包含：
│                          # - 项目简介（1-2句）
│                          # - 快速导航链接
│                          # - 核心组件列表
│                          # - 状态徽章
└── docs/                  # 所有详细文档
    ├── architecture/      # 架构文档
    │   └── ARCHITECTURE.md
    ├── guides/            # 使用指南
    │   └── QUICK_START.md
    └── api/               # API文档
```

### 功能目录只放定义文件
```
.lingma/agents/
├── spec-driven-core-agent.md   ✅ Agent定义
├── test-runner-agent.md        ✅ Agent定义
└── (无 README.md)              ✅ 正确

.lingma/rules/
├── AGENTS.md                   ✅ Rule定义
├── automation-policy.md        ✅ Rule定义
└── (无 README.md)              ✅ 正确
```

---

## 🔧 自动检测脚本

```python
# scripts/check_doc_redundancy.py
import os
import sys
from pathlib import Path

def check_root_docs(lingma_dir: str) -> list[str]:
    """检查根目录是否有冗余入口文档"""
    root = Path(lingma_dir)
    
    # 允许的根目录文档
    allowed_docs = {'README.md'}
    
    # 禁止的入口文档模式
    forbidden_patterns = [
        'QUICK_START*',
        'GUIDE*',
        'ARCHITECTURE*',
        'SYSTEM_*',
        'INTRO*',
        'OVERVIEW*'
    ]
    
    violations = []
    
    for file in root.glob('*.md'):
        if file.name not in allowed_docs:
            # 检查是否匹配禁止模式
            for pattern in forbidden_patterns:
                if file.name.upper().startswith(pattern.replace('*', '')):
                    violations.append(f"❌ {file.name} - 应移至 docs/guides/ 或 docs/architecture/")
                    break
    
    return violations

def check_functional_readmes(lingma_dir: str) -> list[str]:
    """检查功能目录是否有 README"""
    functional_dirs = ['agents', 'rules', 'skills', 'mcp-templates']
    violations = []
    
    for dir_name in functional_dirs:
        readme_path = Path(lingma_dir) / dir_name / 'README.md'
        if readme_path.exists():
            violations.append(f"❌ {dir_name}/README.md - 功能目录禁止放置 README")
    
    return violations

def main():
    lingma_dir = '.lingma'
    
    print("🔍 检查文档冗余...")
    
    root_violations = check_root_docs(lingma_dir)
    functional_violations = check_functional_readmes(lingma_dir)
    
    all_violations = root_violations + functional_violations
    
    if all_violations:
        print("\n发现文档冗余问题:\n")
        for v in all_violations:
            print(v)
        print("\n💡 修复建议:")
        print("- 根目录多余文档 → 移至 docs/guides/ 或 docs/architecture/")
        print("- 功能目录 README → 删除或移至 docs/")
        sys.exit(1)
    else:
        print("✅ 文档结构符合规范")
        sys.exit(0)

if __name__ == '__main__':
    main()
```

---

## 🚫 Git Hook 集成

```bash
# .lingma/hooks/pre-commit-doc-check
#!/bin/bash

echo "🔍 检查文档冗余..."

python .lingma/scripts/check_doc_redundancy.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 提交被拒绝：存在文档冗余问题"
    echo "请修复后再提交"
    exit 1
fi

echo "✅ 文档检查通过"
exit 0
```

---

## 📊 检测指标

| 检查项 | 规则 | 违规示例 |
|--------|------|---------|
| 根目录入口文档 | 仅允许 README.md | QUICK_START.md, ARCHITECTURE.md |
| 功能目录 README | 禁止 | agents/README.md, rules/README.md |
| 文档大小 | README.md ≤ 800字 | 超过则拆分到 docs/ |
| 文档位置 | 详细文档在 docs/ | 根目录放置长篇文档 |

---

## 💡 最佳实践总结

### 核心原则
1. **单一入口**: `.lingma/README.md` 是唯一地图
2. **渐进式披露**: 详情放在 `docs/` 子目录
3. **功能纯净**: agents/rules/skills 只放定义文件
4. **自动化检测**: Git Hook 自动拦截违规

### 记忆要点
> **"根目录一张地图，docs 目录全部细节，功能目录零 README"**

---

**此规则已集成到自迭代流，下次自动执行检测！** ✅
