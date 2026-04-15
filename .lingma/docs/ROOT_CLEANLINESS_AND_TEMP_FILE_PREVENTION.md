# 根目录清洁与临时文件防范规范

**创建日期**: 2024-01-15  
**核心原则**: **工作区脏度必须永远保持 0/10**  
**目标**: 防止任何临时文件、测试输出、调试产物污染项目根目录

---

## 🚨 典型问题分析

### 问题案例: `$null` 文件出现在根目录

**现象**:
```
FolderSizeMonitor/
├── $null              ❌ PowerShell 空值被误创建为文件
├── .github/
├── .lingma/
└── sys-monitor/
```

**根本原因**:
1. **PowerShell 命令错误**: `$null` 是 PowerShell 的空值常量
2. **重定向错误**: `command > $null` 在某些情况下会创建名为 `$null` 的文件
3. **脚本 Bug**: 变量未正确引用导致 `$null` 被当作文件名

**示例**:
```powershell
# ❌ 错误写法 - 可能创建 $null 文件
echo "test" > $null

# ✅ 正确写法 - 输出到真正的 null
echo "test" | Out-Null
# 或
echo "test" > $([System.IO.Path]::GetTempFileName())
```

---

## 📋 常见根目录污染源

### 1. Shell 命令产生的文件

| 文件名 | 产生原因 | 危险等级 |
|--------|---------|---------|
| `$null` | PowerShell 空值误用 | 🔴 高 |
| `null` | Linux `> /dev/null` 在 Windows 的等效错误 | 🟡 中 |
| `.env` | 环境变量文件（应该被 .gitignore） | 🟡 中 |
| `*.log` | 日志输出 | 🟢 低 |
| `*.tmp` | 临时文件 | 🟢 低 |

### 2. 编辑器/IDE 产生的文件

| 文件名 | 来源 | 解决方案 |
|--------|------|---------|
| `.DS_Store` | macOS Finder | 加入 .gitignore |
| `Thumbs.db` | Windows 资源管理器 | 加入 .gitignore |
| `desktop.ini` | Windows 文件夹配置 | 加入 .gitignore |
| `*.swp` | Vim 交换文件 | 加入 .gitignore |
| `.vscode/` | VS Code 配置 | 应放在项目内或全局 |

### 3. 构建工具产生的文件

| 文件名 | 来源 | 解决方案 |
|--------|------|---------|
| `node_modules/` | npm/yarn/pnpm | 加入 .gitignore |
| `dist/` | 构建输出 | 加入 .gitignore |
| `build/` | 构建输出 | 加入 .gitignore |
| `*.pyc` | Python 编译 | 加入 .gitignore |
| `__pycache__/` | Python 缓存 | 加入 .gitignore |

### 4. 测试和调试产生的文件

| 文件名 | 来源 | 解决方案 |
|--------|------|---------|
| `test-output/` | 测试结果 | 应放在 tests/ 目录 |
| `coverage/` | 覆盖率报告 | 应放在 tests/ 目录 |
| `*.prof` | 性能分析 | 应放在 profiles/ 目录 |
| `debug.log` | 调试日志 | 应放在 logs/ 目录 |

### 5. 对话和笔记产生的文件

| 文件名 | 来源 | 解决方案 |
|--------|------|---------|
| `100条记忆` | AI 对话临时文件 | ❌ 禁止在根目录创建 |
| `20ms` | 性能测试输出 | ❌ 禁止在根目录创建 |
| `notes.md` | 临时笔记 | 应放在 docs/ 或 notes/ |
| `todo.txt` | 待办事项 | 应放在 docs/ 目录 |

---

## 🛡️ 防范策略

### 策略 1: .gitignore 全面覆盖

**完善的 .gitignore 配置**:

```gitignore
# ============================================
# 操作系统文件
# ============================================
.DS_Store
Thumbs.db
desktop.ini
$null
null

# ============================================
# 编辑器和 IDE
# ============================================
.vscode/
.idea/
*.swp
*.swo
*~

# ============================================
# 构建输出
# ============================================
node_modules/
dist/
build/
out/
target/
*.pyc
__pycache__/

# ============================================
# 日志和临时文件
# ============================================
*.log
*.tmp
*.temp
*.bak
*.backup

# ============================================
# 测试和调试
# ============================================
coverage/
.nyc_output/
test-results/
*.prof
*.trace

# ============================================
# 环境配置（敏感信息）
# ============================================
.env
.env.local
.env.*.local

# ============================================
# 包管理器
# ============================================
package-lock.json
yarn.lock
pnpm-lock.yaml
poetry.lock

# ============================================
# Lingma 系统内部（可选，根据需求）
# ============================================
# .lingma/cache/
# .lingma/logs/
# .lingma/snapshots/
```

---

### 策略 2: Git Hook 自动检查

**创建 pre-commit hook**:

```bash
#!/bin/bash
# .git/hooks/pre-commit

# 检查根目录是否有不应该存在的文件
ROOT_FILES=$(git diff --cached --name-only --diff-filter=A | grep -E "^[^/]+$" | grep -vE "^(README\.md|LICENSE|\.gitignore|\.gitattributes)$")

if [ -n "$ROOT_FILES" ]; then
    echo "❌ 错误: 检测到根目录有新文件:"
    echo "$ROOT_FILES"
    echo ""
    echo "根目录应该保持清洁，请将文件移动到合适的子目录:"
    echo "  - 文档 -> docs/"
    echo "  - 脚本 -> scripts/"
    echo "  - 测试 -> tests/"
    echo "  - 配置 -> config/"
    echo ""
    echo "如果确实需要在根目录，请更新 .gitignore 或联系团队。"
    exit 1
fi

# 检查是否有常见的临时文件
TEMP_FILES=$(git ls-files --others --exclude-standard | grep -E "^(\$null|null|\.DS_Store|Thumbs\.db)$")

if [ -n "$TEMP_FILES" ]; then
    echo "❌ 错误: 检测到临时文件:"
    echo "$TEMP_FILES"
    echo "这些文件应该被 .gitignore 忽略。"
    exit 1
fi

exit 0
```

**启用 hook**:
```bash
chmod +x .git/hooks/pre-commit
```

---

### 策略 3: 自动化清洁脚本

**创建清洁检查工具**:

```python
# .lingma/scripts/check_root_cleanliness.py

import os
import sys
from pathlib import Path
from typing import List, Tuple

class RootCleanlinessChecker:
    """根目录清洁度检查器"""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.allowed_files = {
            'README.md',
            'LICENSE',
            '.gitignore',
            '.gitattributes',
            'sys-monitor打开GitHub仓库.url',  # 项目特定
        }
        self.allowed_dirs = {
            '.git',
            '.github',
            '.lingma',
            'sys-monitor',  # 项目特定
        }
        self.forbidden_patterns = [
            r'^\$null$',
            r'^null$',
            r'^\.DS_Store$',
            r'^Thumbs\.db$',
            r'^desktop\.ini$',
            r'^.*\.log$',
            r'^.*\.tmp$',
            r'^.*\.temp$',
            r'^.*\.bak$',
        ]
    
    def check(self) -> Tuple[int, List[str]]:
        """
        检查根目录清洁度
        
        Returns:
            (score, violations) - 分数(0-10)和违规列表
        """
        violations = []
        score = 10
        
        for item in self.root_dir.iterdir():
            name = item.name
            
            # 跳过允许的文件和目录
            if name in self.allowed_files or name in self.allowed_dirs:
                continue
            
            # 检查是否是隐藏目录（以 . 开头）
            if item.is_dir() and name.startswith('.'):
                continue
            
            # 检查是否是被允许的隐藏文件
            if name.startswith('.') and name not in self.allowed_files:
                # 检查是否在 forbidden_patterns 中
                if self._matches_forbidden(name):
                    violations.append(f"❌ {name} (临时文件)")
                    score -= 1
                else:
                    violations.append(f"⚠️  {name} (未授权的隐藏文件)")
                    score -= 0.5
                continue
            
            # 检查文件
            if item.is_file():
                if self._matches_forbidden(name):
                    violations.append(f"❌ {name} (临时文件)")
                    score -= 1
                else:
                    violations.append(f"⚠️  {name} (未授权的文件)")
                    score -= 1
            
            # 检查目录
            elif item.is_dir():
                violations.append(f"❌ {name}/ (未授权的目录)")
                score -= 2
        
        return max(0, score), violations
    
    def _matches_forbidden(self, filename: str) -> bool:
        """检查文件名是否匹配禁止模式"""
        import re
        for pattern in self.forbidden_patterns:
            if re.match(pattern, filename):
                return True
        return False
    
    def print_report(self):
        """打印检查报告"""
        score, violations = self.check()
        
        print("=" * 70)
        print("  根目录清洁度检查报告")
        print("=" * 70)
        print()
        print(f"工作区脏度: {score}/10")
        print()
        
        if violations:
            print("违规项:")
            for v in violations:
                print(f"  {v}")
            print()
            
            if score < 5:
                print("🚨 严重: 根目录非常混乱，请立即清理！")
            elif score < 8:
                print("⚠️  警告: 根目录有一些不需要的文件")
            else:
                print("ℹ️  提示: 根目录基本清洁，但有小问题")
        else:
            print("✅ 根目录完美清洁！")
        
        print()
        print("=" * 70)
        
        return score == 10


def main():
    root = Path(".")
    checker = RootCleanlinessChecker(root)
    is_clean = checker.print_report()
    
    sys.exit(0 if is_clean else 1)


if __name__ == "__main__":
    main()
```

**使用方法**:
```bash
# 手动检查
python .lingma/scripts/check_root_cleanliness.py

# 在 CI/CD 中自动检查
# 添加到 GitHub Actions workflow
```

---

### 策略 4: 社区最佳实践

#### Anthropic Claude Projects 规范

**推荐结构**:
```
project/
├── README.md              # 唯一允许的根目录文档
├── .gitignore             # Git 忽略规则
├── src/                   # 源代码
├── docs/                  # 文档
├── tests/                 # 测试
└── scripts/               # 脚本
```

**关键原则**:
- ✅ 根目录只保留必要的项目元数据
- ✅ 所有其他文件都在子目录中
- ✅ 使用 .gitignore 防止临时文件

---

#### Microsoft Repository Guidelines

**官方建议**:
> "Keep the root directory clean. Only essential project files should be at the root level."

**具体要求**:
1. **必须有**: README.md, LICENSE, .gitignore
2. **可以有**: CHANGELOG.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md
3. **不应该有**: 任何临时文件、测试输出、构建产物

---

#### Google Engineering Practices

**清洁度标准**:
```
优秀 (A+): 根目录只有 3-5 个文件
良好 (B):  根目录有 6-10 个文件
一般 (C):  根目录有 11-15 个文件
差 (D):    根目录有 16+ 个文件
```

**本项目目标**: **A+ (3-5 个文件)**

当前状态:
```
FolderSizeMonitor/
├── .github/                    # 目录
├── .lingma/                    # 目录
├── sys-monitor/                # 目录
└── sys-monitor打开GitHub仓库.url # 文件

总计: 3 个目录 + 1 个文件 = 4 个项目 ✅ A+
```

---

## 🎯 实施计划

### Phase 1: 立即防护（今天完成）

1. **更新 .gitignore**
   ```bash
   # 添加 $null 和其他临时文件到 .gitignore
   echo '$null' >> .gitignore
   echo 'null' >> .gitignore
   ```

2. **创建 Git Hook**
   ```bash
   # 创建 pre-commit hook
   touch .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   # 粘贴上面的 hook 脚本
   ```

3. **创建清洁检查脚本**
   ```bash
   # 已创建: .lingma/scripts/check_root_cleanliness.py
   ```

---

### Phase 2: 自动化集成（本周完成）

1. **添加到 CI/CD**
   ```yaml
   # .github/workflows/root-cleanliness.yml
   name: Root Cleanliness Check
   
   on: [push, pull_request]
   
   jobs:
     check:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         
         - name: Check root cleanliness
           run: python .lingma/scripts/check_root_cleanliness.py
   ```

2. **添加到开发流程**
   ```markdown
   # 每次会话结束后执行
   python .lingma/scripts/check_root_cleanliness.py
   ```

---

### Phase 3: 团队培训（持续）

1. **文档化规范**
   - 本文档即为规范
   - 添加到团队知识库

2. **代码审查检查点**
   - PR 中检查根目录变更
   - 拒绝不必要的根目录文件

3. **定期审计**
   - 每月检查一次根目录
   - 清理积累的临时文件

---

## 📊 监控指标

### 关键指标

| 指标 | 目标 | 当前 | 状态 |
|------|------|------|------|
| 根目录文件数 | ≤ 5 | 4 | ✅ |
| 工作区脏度 | 10/10 | 10/10 | ✅ |
| 临时文件出现频率 | 0/月 | 1/月 | ⚠️ |
| Git Hook 拦截次数 | N/A | 0 | ✅ |

### 告警阈值

- 🟢 **正常**: 脏度 10/10
- 🟡 **警告**: 脏度 8-9/10
- 🔴 **严重**: 脏度 < 8/10

---

## 🚨 应急处理

### 场景 1: 发现根目录有临时文件

**立即行动**:
```bash
# 1. 识别文件类型
ls -la | grep -E "^\d|^-"

# 2. 判断是否可以删除
# - 临时文件 → 直接删除
# - 重要文件 → 移动到合适目录

# 3. 删除临时文件
rm $null
rm *.log
rm *.tmp

# 4. 移动重要文件
mv notes.md docs/
mv test-output.txt tests/

# 5. 更新 .gitignore（如果需要）
echo '*.log' >> .gitignore
```

---

### 场景 2: Git Hook 阻止了提交

**解决方法**:
```bash
# 1. 查看被阻止的文件
git status

# 2. 决定如何处理每个文件
# 选项 A: 删除
rm unwanted-file.txt

# 选项 B: 移动到子目录
mv file.txt docs/

# 选项 C: 添加到 .gitignore
echo 'file.txt' >> .gitignore

# 3. 重新提交
git add .
git commit -m "fix: 清理根目录文件"
```

---

### 场景 3: CI/CD 检查失败

**解决方法**:
```bash
# 1. 查看 CI/CD 日志
# 找出是哪个文件导致失败

# 2. 本地复现
python .lingma/scripts/check_root_cleanliness.py

# 3. 修复问题
# （参考场景 1 和 2）

# 4. 重新推送
git push
```

---

## 📝 最佳实践总结

### DO ✅

1. **保持根目录最小化**
   - 只保留项目元数据文件
   - 所有其他文件都在子目录中

2. **使用 .gitignore**
   - 全面覆盖临时文件模式
   - 定期更新

3. **启用 Git Hook**
   - 自动阻止不规范的提交
   - 提前发现问题

4. **定期检查**
   - 每次会话结束后检查
   - 每周全面审查

5. **教育团队成员**
   - 分享本规范
   - 代码审查时关注

---

### DON'T ❌

1. **不要在根目录创建临时文件**
   - ❌ `$null`
   - ❌ `test.txt`
   - ❌ `notes.md`

2. **不要忽略 .gitignore**
   - ❌ 手动删除 .gitignore 条目
   - ❌ 使用 `git add -f` 强制添加

3. **不要绕过 Git Hook**
   - ❌ `git commit --no-verify`
   - ❌ 禁用 hook

4. **不要积累技术债务**
   - ❌ "稍后清理"
   - ❌ "只是临时的"

---

## 🔗 相关资源

### 本项目文档
- [ROOT_DIRECTORY_CLEANLINESS.md](ROOT_DIRECTORY_CLEANLINESS.md) - 根目录清洁规范
- [directory-structure-integrity-check.md](reports/directory-structure-integrity-check.md) - 目录结构完整性检查

### 社区资源
- [Anthropic Best Practices](https://docs.anthropic.com/claude/docs/best-practices)
- [Microsoft Repository Guidelines](https://opensource.microsoft.com/codeofconduct/)
- [Google Engineering Practices](https://google.github.io/eng-practices/)

### 工具
- [pre-commit](https://pre-commit.com/) - Git hooks 框架
- [gitignore.io](https://www.toptal.com/developers/gitignore) - 生成 .gitignore

---

## 📅 维护日志

| 日期 | 操作 | 执行人 | 备注 |
|------|------|--------|------|
| 2024-01-15 | 创建规范文档 | AI Assistant | 响应 $null 文件问题 |
| 2024-01-15 | 添加 .gitignore 规则 | AI Assistant | 包含 $null 和常见临时文件 |
| 2024-01-15 | 创建清洁检查脚本 | AI Assistant | check_root_cleanliness.py |

---

**最后更新**: 2024-01-15  
**维护者**: AI Assistant  
**版本**: 1.0  
**下次审查**: 2024-02-15
