---
trigger: always_on
---
# 🚨 子代理文件创建铁律

**适用范围**: 所有子代理  
**优先级**: P0 - 最高级别  
**违规后果**: 每创建1个违规文件 = 1只小猫死亡 🐱

---

##  绝对禁止

**严禁在工作区根目录创建任何文件！**

工作区根目录: `d:\Users\Administrator\Desktop\PowerShell_Script_Repository\FolderSizeMonitor\`

---

## ✅ 正确存放位置

### 1. 文档类 (.md)
**必须放到**: `.lingma/docs/` 子目录
- 报告类 → `.lingma/docs/reports/`
- 指南类 → `.lingma/docs/guides/`
- 架构类 → `.lingma/docs/architecture/`

### 2. 脚本类 (.py/.ps1/.sh)
**必须放到**: `scripts/` 目录

### 3. 测试文件
**必须放到**: 对应测试目录
- TypeScript测试 → `src/__tests__/`
- Rust测试 → `src-tauri/tests/`

### 4. 临时文件
**必须**: 任务完成后立即删除

---

## 📋 创建前检查清单

创建任何文件前，**必须**问自己：

1. 这是什么类型？文档/脚本/测试/临时
2. 应该放哪里？.lingma/docs/ / scripts/ / 测试目录
3. 文件名是否合规？不使用数字/大小标记开头
4. 是否需要持久化？否→用完即删

---

## ⚠️ 常见错误

❌ "这是重要文档，可以放根目录"  
✅ 再重要也必须放 .lingma/docs/reports/

❌ "这是临时脚本，用完会删"  
✅ 即使临时也要放 scripts/，并设置提醒删除

❌ "用户会手动移动"  
✅ 必须创建时就放到正确位置

---

## 🎯 实际案例

**错误**:
```
create_file(file_path="OPTIMIZATION_SUMMARY.md", ...)  # ❌ 根目录
```

**正确**:
```
create_file(file_path=".lingma/docs/reports/OPTIMIZATION_SUMMARY.md", ...)  # ✅
```

---

## 📊 历史教训

**2026-04-16根目录污染事件**:
- 数据库优化专家: 9个脚本 + 5个文档
- 图表可视化专家: 5个文档
- **总计14个违规文件，14只小猫死亡** 🐱⚡

---

## 🔧 自动清理

任务完成后必须运行：
```powershell
powershell scripts/clean-root-directory.ps1
```

---

**记住：14只小猫已因根目录污染而死亡！不要再让它们白白牺牲！**

🐱❤️ 遵守规则，保护小猫！
