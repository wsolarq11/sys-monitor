# 根目录清洁规范

**原则**: 工作区脏度必须为 **0/10**  
**目标**: 保持项目根目录绝对清洁，所有临时文件、测试文件、报告文件都必须放在合适的子目录中

---

## ✅ 允许的根目录内容

### 目录（4个）

1. **`.github/`** - GitHub CI/CD 配置
2. **`.lingma/`** - 自迭代流系统（Agents, Skills, Rules, MCP等）
3. **`sys-monitor/`** - 主项目代码
4. **`.git/`** - Git 版本控制（隐藏）

### 文件（1个）

1. **`sys-monitor打开GitHub仓库.url`** - 快捷方式（可选）

---

## ❌ 禁止的根目录内容

### 临时文件
- ❌ `100条记忆`
- ❌ `20ms`
- ❌ `30-50%`
- ❌ `50ms`
- ❌ `58.9%`
- ❌ `60.9%`
- ❌ `99%`
- ❌ `$null`
- ❌ 任何以数字开头的文件

### 备份目录
- ❌ `.backup/` （已迁移到 `.lingma/backups/`）

### 测试文件
- ❌ `test-*.py`
- ❌ `test-*.js`
- ❌ `*.test.*`

### 报告文件
- ❌ `*.md` （除了 README.md，如果有）
- ❌ `report-*.md`
- ❌ `analysis-*.md`

### 其他
- ❌ `*.log`
- ❌ `*.tmp`
- ❌ `*.bak`
- ❌ `__pycache__/`
- ❌ `node_modules/`
- ❌ `dist/`
- ❌ `build/`

---

## 📁 正确的文件存放位置

| 文件类型 | 应该放在 | 示例 |
|---------|---------|------|
| **临时文件** | 删除或 `.lingma/tmp/` | 对话中创建的临时文件 |
| **备份文件** | `.lingma/backups/` | MCP 配置备份、架构调整备份 |
| **测试脚本** | `.lingma/scripts/tests/` 或 `sys-monitor/tests/` | 验证脚本、测试用例 |
| **报告文档** | `.lingma/reports/` | 调研报告、实施报告 |
| **日志文件** | `.lingma/logs/` | 运行日志、审计日志 |
| **缓存文件** | `.lingma/cache/` | Spec 缓存、Memory 缓存 |
| **快照文件** | `.lingma/snapshots/` | 文件系统快照 |
| **配置文件** | `.lingma/config/` | MCP 配置、Agent 配置 |
| **技能文档** | `.lingma/skills/` | Skill 定义和指南 |
| **规则文档** | `.lingma/rules/` | Rule 定义和规范 |
| **Agent 配置** | `.lingma/agents/` | Agent 角色定义 |
| **Spec 文档** | `.lingma/specs/` | 开发规范文档 |

---

## 🧹 清洁检查清单

### 每次会话结束后

- [ ] 检查根目录是否有新文件
- [ ] 删除所有临时文件
- [ ] 移动报告到 `.lingma/reports/`
- [ ] 移动备份到 `.lingma/backups/`
- [ ] 确认工作区脏度为 0/10

### 每周清理

- [ ] 清理 `.lingma/cache/` 过期缓存
- [ ] 清理 `.lingma/logs/` 旧日志
- [ ] 审查 `.lingma/backups/` 是否需要保留
- [ ] 更新本规范文档（如有需要）

---

## 🔍 检查命令

### Windows CMD

```cmd
# 查看根目录所有内容
dir /b

# 查看非隐藏文件
dir /b /a:-d | findstr /V "^\."

# 查找数字开头的文件（临时文件）
dir /b | findstr /R "^[0-9]"

# 查找所有 .md 文件（应该在 .lingma/reports/ 中）
dir /b *.md
```

### PowerShell

```powershell
# 查看根目录所有内容
Get-ChildItem -Name

# 查找临时文件
Get-ChildItem | Where-Object { $_.Name -match '^\d' }

# 查找不应该在根目录的文件
Get-ChildItem -File | Where-Object { 
    $_.Name -notmatch '^\.|^sys-monitor' 
}
```

### Git

```bash
# 查看未跟踪的文件
git status --short

# 查看所有变更
git status

# 清理未跟踪的文件（谨慎使用）
git clean -fdn  # 先预览
git clean -fd   # 再执行
```

---

## ⚠️ 常见错误

### 错误 1: 在根目录创建临时文件

**错误示例**:
```
根目录/
├── 100条记忆      ❌
├── 20ms           ❌
└── test-output.txt ❌
```

**正确做法**:
```
.lingma/tmp/
├── 100条记忆      ✅
├── 20ms           ✅
└── test-output.txt ✅
```

或直接删除（如果不需要保留）

---

### 错误 2: 在根目录创建备份目录

**错误示例**:
```
根目录/
└── .backup/       ❌
```

**正确做法**:
```
.lingma/backups/
└── architecture/  ✅
```

---

### 错误 3: 在根目录放置报告文件

**错误示例**:
```
根目录/
├── investigation-report.md  ❌
└── implementation-report.md ❌
```

**正确做法**:
```
.lingma/reports/
├── investigation-report.md  ✅
└── implementation-report.md ✅
```

---

## 🎯 工作区脏度评分标准

### 评分规则

| 违规项 | 扣分 | 示例 |
|--------|------|------|
| 每个临时文件 | -1 | `100条记忆`, `20ms` |
| 每个未授权目录 | -2 | `.backup/`, `tmp/` |
| 每个报告文件 | -1 | `report.md` 在根目录 |
| 每个测试文件 | -1 | `test.py` 在根目录 |
| 每个日志文件 | -0.5 | `app.log` 在根目录 |

### 评分示例

**脏度 10/10** (完美):
```
根目录/
├── .github/
├── .lingma/
├── sys-monitor/
└── README.md (如果有)
```

**脏度 5/10** (中等):
```
根目录/
├── .github/
├── .lingma/
├── sys-monitor/
├── 100条记忆      (-1)
├── 20ms           (-1)
├── test.py        (-1)
├── report.md      (-1)
└── .backup/       (-2)
```

**脏度 0/10** (不可接受):
```
根目录/
├── 10+ 个临时文件
├── 多个备份目录
├── 散落的报告文件
└── 各种测试输出
```

---

## 🚀 自动化清洁工具

### 创建清洁检查脚本

```python
# .lingma/scripts/check_root_cleanliness.py

import os
from pathlib import Path

def check_root_cleanliness(root_dir: Path) -> dict:
    """检查根目录清洁度"""
    
    allowed_items = {
        '.github', '.lingma', 'sys-monitor', '.git',
        'sys-monitor打开GitHub仓库.url'
    }
    
    violations = []
    score = 10
    
    for item in root_dir.iterdir():
        if item.name not in allowed_items:
            violations.append(item.name)
            if item.is_file():
                score -= 1
            else:
                score -= 2
    
    return {
        'score': max(0, score),
        'violations': violations,
        'is_clean': score == 10
    }

if __name__ == "__main__":
    root = Path(".")
    result = check_root_cleanliness(root)
    
    print(f"工作区脏度: {result['score']}/10")
    
    if result['violations']:
        print("\n违规项:")
        for v in result['violations']:
            print(f"  - {v}")
    else:
        print("\n✅ 根目录完美清洁！")
```

### 使用方法

```bash
# 检查根目录清洁度
python .lingma/scripts/check_root_cleanliness.py

# 输出示例:
# 工作区脏度: 10/10
# ✅ 根目录完美清洁！
```

---

## 📝 维护日志

| 日期 | 操作 | 执行人 | 备注 |
|------|------|--------|------|
| 2024-01-15 | 创建规范文档 | AI Assistant | 定义根目录清洁标准 |
| 2024-01-15 | 清理临时文件 | AI Assistant | 删除 10+ 个临时文件 |
| 2024-01-15 | 迁移 .backup | AI Assistant | 移到 .lingma/backups/ |

---

**最后更新**: 2024-01-15  
**维护者**: AI Assistant  
**当前状态**: ✅ 工作区脏度 0/10（完美清洁）
