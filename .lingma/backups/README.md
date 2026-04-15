# 自迭代流系统备份管理

**位置**: `.lingma/backups/`  
**目的**: 统一管理所有系统备份，保持项目根目录清洁

---

## 📁 备份目录结构

```
.lingma/backups/
├── README.md                   # 本文件
├── mcp/                        # MCP 配置备份
│   ├── mcp-20260415_175811.json
│   ├── mcp-20260415_175817.json
│   └── mcp-20260415_175823.json
└── architecture/               # 架构调整备份
    └── phase1-cleanup/         # Phase 1 架构精简备份
        ├── agent-config.json
        ├── automation-engine.py
        ├── operation-logger.py
        ├── snapshot-manager.py
        ├── spec-driven-agent.py
        ├── test-agent.py
        └── verify-automation.py
```

---

## 📋 备份分类

### 1. MCP 配置备份 (`mcp/`)

**备份内容**: MCP 服务器配置文件的历史版本  
**备份时机**: 每次修改 `mcp-servers.json` 前自动备份  
**备份工具**: `.lingma/scripts/sync-mcp-config.py`  
**保留策略**: 保留最近 10 个版本  

**恢复方法**:
```bash
# 查看可用备份
python .lingma/scripts/sync-mcp-config.py list-backups

# 恢复到指定版本
python .lingma/scripts/sync-mcp-config.py restore <backup-file>
```

---

### 2. 架构调整备份 (`architecture/`)

**备份内容**: 架构重构时删除的文件  
**备份时机**: 执行重大架构调整前手动备份  
**备份原因**: 防止需要回滚或参考旧实现  

#### Phase 1 架构精简备份 (`phase1-cleanup/`)

**备份时间**: 2024-01-15  
**备份原因**: Phase 1.5 架构精简，删除自定义实现，改用 Lingma 原生能力

**备份文件清单**:

| 文件 | 大小 | 原位置 | 删除原因 | 替代方案 |
|------|------|--------|---------|---------|
| `automation-engine.py` | 12.8KB | `.lingma/scripts/` | 冗余实现 | Rules: `automation-policy.md` |
| `operation-logger.py` | 11.9KB | `.lingma/scripts/` | 冗余实现 | Git + Spec 实施笔记 |
| `snapshot-manager.py` | 16.3KB | `.lingma/scripts/` | 冗余实现 | Git branch |
| `spec-driven-agent.py` | 18.9KB | `.lingma/scripts/` | 冗余实现 | Agent: `spec-driven-core-agent.md` |
| `agent-config.json` | 1.3KB | `.lingma/config/` | 配置迁移 | 集成到 Agent 配置 |
| `test-agent.py` | 10.3KB | `.lingma/scripts/` | 测试脚本 | 手动测试 |
| `verify-automation.py` | 8.1KB | `.lingma/scripts/` | 验证脚本 | 手动验证 |

**总计**: 7 个文件，~79.6KB

**恢复方法**:
```bash
# 如果需要恢复某个文件
copy .lingma/backups/architecture/phase1-cleanup/<filename> .lingma/scripts/

# 注意：恢复后需要重新评估是否真的需要该文件
# 建议：先阅读相关文件，理解为什么被删除
```

**重要提示**:
- ⚠️  这些文件被删除是因为与 Lingma 原生能力重复
- ⚠️  恢复前请确认是否真的需要
- ⚠️  恢复后可能需要调整其他组件以兼容

---

## 🔄 备份策略

### 自动备份

**MCP 配置**:
- 触发条件: 修改 `mcp-servers.json` 前
- 备份工具: `sync-mcp-config.py`
- 保留数量: 最近 10 个版本
- 清理策略: 自动删除最旧的备份

### 手动备份

**架构调整**:
- 触发条件: 执行重大架构变更前
- 备份方法: 手动复制到 `architecture/` 子目录
- 命名规范: `<变更名称>/` (例如: `phase1-cleanup/`)
- 保留策略: 永久保留（除非确认不再需要）

---

## 📊 备份统计

| 类别 | 备份数量 | 总大小 | 最后备份时间 |
|------|---------|--------|-------------|
| MCP 配置 | 3 个 | ~2.7KB | 2026-04-15 17:58 |
| 架构调整 | 1 个批次 | ~79.6KB | 2024-01-15 |
| **总计** | **4 个** | **~82.3KB** | - |

---

## 🧹 清理策略

### MCP 备份清理

**自动清理**:
```bash
# 保留最近 10 个备份，删除更旧的
python .lingma/scripts/sync-mcp-config.py cleanup --keep 10
```

**手动清理**:
```bash
# 删除特定备份
rm .lingma/backups/mcp/mcp-YYYYMMDD_HHMMSS.json
```

### 架构备份清理

**清理原则**:
- ✅ 永久保留重要的架构调整备份
- ✅ 如果确认不再需要，可以删除
- ✅ 删除前必须记录到 Spec 实施笔记

**清理命令**:
```bash
# 删除整个架构备份批次
rm -rf .lingma/backups/architecture/<batch-name>/
```

---

## 🔍 查找备份

### 按类型查找

```bash
# 查看所有 MCP 备份
ls .lingma/backups/mcp/

# 查看所有架构备份
ls .lingma/backups/architecture/
```

### 按时间查找

```bash
# 查看最近的 MCP 备份
ls -lt .lingma/backups/mcp/ | head -5
```

### 按内容查找

```bash
# 搜索包含特定内容的备份
grep -r "filesystem" .lingma/backups/mcp/
```

---

## 📝 最佳实践

### 1. 备份前检查

在执行重大变更前：
- [ ] 确认当前状态已提交到 Git
- [ ] 记录变更原因和预期效果
- [ ] 创建备份并验证完整性

### 2. 备份命名规范

**MCP 备份**: 自动生成时间戳
```
mcp-YYYYMMDD_HHMMSS.json
```

**架构备份**: 使用描述性名称
```
architecture/<变更描述>/
示例: phase1-cleanup/, mcp-refactor/, agent-upgrade/
```

### 3. 备份验证

创建备份后：
- [ ] 检查文件大小是否合理
- [ ] 尝试读取备份文件
- [ ] 记录备份到实施笔记

### 4. 定期清理

每季度执行一次：
- [ ] 审查 MCP 备份，删除过旧的
- [ ] 审查架构备份，确认是否仍需保留
- [ ] 更新本 README 的统计信息

---

## 🚨 紧急情况处理

### 场景 1: 误删重要文件

**恢复步骤**:
1. 检查 `.lingma/backups/architecture/` 是否有备份
2. 如果有，复制回原位置
3. 如果没有，从 Git 历史恢复
   ```bash
   git log --all --full-history -- <filepath>
   git checkout <commit-hash> -- <filepath>
   ```

### 场景 2: MCP 配置损坏

**恢复步骤**:
1. 查看最近的备份
   ```bash
   ls -lt .lingma/backups/mcp/ | head -5
   ```
2. 恢复到最近的正常版本
   ```bash
   cp .lingma/backups/mcp/mcp-YYYYMMDD_HHMMSS.json .lingma/config/mcp-servers.json
   ```
3. 重启 Lingma IDE

### 场景 3: 需要回滚架构调整

**恢复步骤**:
1. 确认要回滚的变更批次
   ```bash
   ls .lingma/backups/architecture/
   ```
2. 查看备份内容
   ```bash
   ls .lingma/backups/architecture/<batch-name>/
   ```
3. 恢复文件到原位置
   ```bash
   cp .lingma/backups/architecture/<batch-name>/* .lingma/scripts/
   ```
4. **重要**: 重新评估是否真的需要回滚
   - 阅读相关报告理解为什么删除
   - 考虑是否有更好的解决方案
   - 更新 Spec 实施笔记

---

## 📚 相关文档

- **MCP 配置管理**: `.lingma/docs/MCP_CONFIG_MANAGEMENT.md`
- **架构精简报告**: `.lingma/reports/lingma-native-architecture-refactor.md`
- **Phase 1.5 完成报告**: `.lingma/reports/phase1.5-completion-report.md`
- **自迭代流调研**: `.lingma/reports/self-iterating-flow-investigation.md`

---

## 📅 维护日志

| 日期 | 操作 | 执行人 | 备注 |
|------|------|--------|------|
| 2024-01-15 | 创建备份目录结构 | AI Assistant | 迁移 `.backup` 到 `.lingma/backups/architecture/` |
| 2024-01-15 | 添加 Phase 1 备份 | AI Assistant | 备份 7 个删除的文件 |
| 2026-04-15 | MCP 自动备份 | sync-mcp-config.py | 3 个备份文件 |

---

**最后更新**: 2024-01-15  
**维护者**: AI Assistant  
**版本**: 1.0
