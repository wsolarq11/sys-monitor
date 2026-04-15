# 根目录清洁规范

**版本**: v1.0  
**最后更新**: 2026-04-15  
**核心原则**: **工作区脏度必须永远保持 0/10**

---

## ✅ 允许的根目录内容

### 目录（4个）

1. **`.github/`** - GitHub CI/CD 配置
2. **`.lingma/`** - 自迭代流系统
3. **`sys-monitor/`** - 主项目代码
4. **`.git/`** - Git 版本控制（隐藏）

### 文件（1个）

1. **`sys-monitor打开GitHub仓库.url`** - 快捷方式（可选）

---

## ❌ 禁止的根目录内容

### 临时文件
- ❌ `$null` - PowerShell 空值误创建
- ❌ `*.log` - 日志文件
- ❌ `*.tmp` - 临时文件
- ❌ `test_*`, `*_test` - 测试文件
- ❌ `debug_*` - 调试文件

### 报告和分析文件
- ❌ `*.md` (除 README.md 外) - 所有文档应放在子目录
- ❌ `report_*` - 报告文件
- ❌ `analysis_*` - 分析文件

### 构建产物
- ❌ `dist/`, `build/` - 构建输出
- ❌ `node_modules/` - 依赖目录
- ❌ `*.exe`, `*.dll` - 编译产物

---

## 🚨 典型问题案例

### 问题 1: `$null` 文件出现在根目录

**现象**:
```
FolderSizeMonitor/
├── $null              ❌ PowerShell 空值被误创建为文件
├── .github/
└── sys-monitor/
```

**根本原因**:
```powershell
# ❌ 错误写法 - 可能创建 $null 文件
echo "test" > $null

# ✅ 正确写法 - 重定向到空设备
echo "test" > $null  # PowerShell 中 $null 是特殊变量
# 或
echo "test" | Out-Null
```

**预防措施**:
1. 使用 `Out-Null` 而非 `$null` 重定向
2. Git Hook 自动检测异常文件
3. CI/CD 每周扫描根目录

---

### 问题 2: 文档过多污染根目录

**现象**:
```
.lingma/docs/
├── MCP_USAGE_GUIDE.md
├── MCP_CONFIG_MANAGEMENT.md
├── MCP_QUICK_VERIFICATION.md
├── MCP_TEST_CHECKLIST.md
├── ROOT_CLEANLINESS_AND_TEMP_FILE_PREVENTION.md
├── ROOT_DIRECTORY_CLEANLINESS.md
└── ... (共 17 个文档)
```

**解决**:
1. 合并重复主题文档
2. 使用子目录组织（guides/, reports/, architecture/）
3. 单一入口原则：根目录 ≤5 个核心文档

**目标结构**:
```
.lingma/docs/
├── guides/          # 使用指南
│   ├── mcp-guide.md
│   ├── root-cleanliness.md
│   └── rules-index.md
├── architecture/    # 架构文档
├── reports/         # 报告和分析
└── QUICK_START.md   # 唯一根目录文档
```

---

## 🛡️ 自动化防护

### 1. Git Hook 检查

提交时自动检测根目录异常文件：

```bash
# .git/hooks/pre-commit
git diff --cached --name-only | grep -E '^\$null|\.tmp$|\.log$' && {
    echo "❌ 检测到临时文件，禁止提交"
    exit 1
}
```

### 2. CI/CD 定期扫描

每周一自动运行全盘扫描：

```yaml
# .github/workflows/system-health-check.yml
schedule:
  - cron: '0 9 * * 1'  # 每周一上午9点
```

### 3. 自动化清理脚本

```bash
# 手动触发清理
python scripts/full_system_scan.py
```

---

## 📊 监控指标

| 指标 | 目标 | 当前状态 |
|------|------|----------|
| 根目录文档数 | ≤5 | 17 ❌ |
| 临时文件数 | 0 | 待检查 |
| 重复主题文档 | 0 | 4组 ❌ |

---

## 🔧 修复流程

发现根目录污染时：

1. **识别问题**: 运行 `python scripts/full_system_scan.py`
2. **分类处理**:
   - 临时文件 → 删除
   - 文档 → 移动到子目录或合并
   - 报告 → 归档到 reports/
3. **验证修复**: 再次运行扫描
4. **提交更改**: Git Hook 会自动检查

---

## 💡 最佳实践

### 1. 创建文件前先思考

- 这个文件应该放在哪里？
- 是否已有类似文档可以合并？
- 是否符合单一入口原则？

### 2. 定期检查

```bash
# 每周检查
git status --short
ls -la | grep -v '^\.' | wc -l  # 非隐藏文件数量
```

### 3. 及时清理

- 测试完成后立即删除测试文件
- 报告生成后移动到 reports/
- 临时脚本用完后删除或移至 scripts/

---

## 🔗 相关资源

- [完整扫描工具](../../scripts/full_system_scan.py)
- [CI/CD 工作流](../../.github/workflows/system-health-check.yml)
- [使命宣言](../MISSION_STATEMENT.md)
