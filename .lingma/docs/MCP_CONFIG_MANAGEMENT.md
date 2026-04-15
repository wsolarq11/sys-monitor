# MCP 配置管理快速参考

## 🚀 常用命令

### 1. 同步项目配置到全局

```bash
python .lingma/scripts/sync-mcp-config.py
```

**用途**: 将 `.lingma/config/mcp-servers.json` 同步到 Lingma 全局配置  
**何时使用**: 修改项目配置后

---

### 2. 列出可用模板

```bash
python .lingma/scripts/sync-mcp-config.py list-templates
```

**输出示例**:
```
📋 可用的配置模板 (2 个):

✅ basic
   文件: .lingma\mcp-templates\basic.json
   MCP 服务: filesystem, git

✅ minimal
   文件: .lingma\mcp-templates\minimal.json
   MCP 服务: 无
```

---

### 3. 应用配置模板

```bash
# 应用 basic 模板（推荐）
python .lingma/scripts/sync-mcp-config.py apply-template basic

# 应用 minimal 模板（禁用所有 MCP）
python .lingma/scripts/sync-mcp-config.py apply-template minimal
```

**流程**:
1. 自动备份当前配置
2. 应用新模板
3. 验证配置
4. 提示重启 IDE

---

### 4. 备份当前配置

```bash
python .lingma/scripts/sync-mcp-config.py backup
```

**备份位置**: `.lingma/backups/mcp/mcp-YYYYMMDD_HHMMSS.json`

---

### 5. 恢复备份

```bash
# 列出可用备份
dir .lingma\backups\mcp\

# 恢复指定备份
python .lingma/scripts/sync-mcp-config.py restore mcp-20260415_175811.json
```

---

## 📁 目录结构

```
.lingma/
├── config/
│   └── mcp-servers.json          # 项目配置（团队共享）
├── mcp-templates/
│   ├── basic.json                # 基础配置模板
│   └── minimal.json              # 最小配置模板
├── backups/
│   └── mcp/
│       ├── mcp-20260415_175811.json
│       └── mcp-20260415_175817.json
└── scripts/
    └── sync-mcp-config.py        # 配置管理工具
```

---

## 🎯 典型工作流

### 场景 1: 日常开发（使用基础配置）

```bash
# 1. 应用基础配置
python .lingma/scripts/sync-mcp-config.py apply-template basic

# 2. 重启 IDE

# 3. 开始开发，MCP 自动生效
```

---

### 场景 2: 切换项目（需要不同配置）

```bash
# 项目 A: 需要 filesystem + git
python .lingma/scripts/sync-mcp-config.py apply-template basic

# 切换到项目 B: 不需要 MCP
python .lingma/scripts/sync-mcp-config.py apply-template minimal

# 切换回项目 A
python .lingma/scripts/sync-mcp-config.py apply-template basic
```

---

### 场景 3: 配置出错（快速恢复）

```bash
# 1. 查看可用备份
dir .lingma\backups\mcp\

# 2. 恢复到最近的备份
python .lingma/scripts/sync-mcp-config.py restore mcp-20260415_175811.json

# 3. 重启 IDE
```

---

### 场景 4: 创建自定义模板

```bash
# 1. 复制现有模板
copy .lingma\mcp-templates\basic.json .lingma\mcp-templates\advanced.json

# 2. 编辑 advanced.json，添加更多 MCP 服务
notepad .lingma\mcp-templates\advanced.json

# 3. 应用新模板
python .lingma/scripts/sync-mcp-config.py apply-template advanced
```

---

## 🔧 配置文件格式

### 项目配置示例

`.lingma/config/mcp-servers.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "env": {},
      "disabled": false,
      "description": "文件系统操作 MCP"
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "env": {},
      "disabled": false,
      "description": "Git 操作 MCP"
    }
  }
}
```

### 关键字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `command` | string | ✅ | 启动命令（如 `npx`） |
| `args` | array | ✅ | 命令行参数 |
| `env` | object | ❌ | 环境变量 |
| `disabled` | boolean | ❌ | 是否禁用（默认 false） |
| `description` | string | ❌ | 服务描述 |

---

## ⚠️ 注意事项

### 1. 每次修改配置后必须重启 IDE

Lingma 只在启动时读取全局配置，运行时不会自动重载。

**正确做法**:
```bash
python .lingma/scripts/sync-mcp-config.py apply-template basic
# 完全关闭 IDE
# 重新启动 IDE
```

**错误做法**:
```bash
python .lingma/scripts/sync-mcp-config.py apply-template basic
# 仅重新加载窗口（❌ 不会生效）
```

---

### 2. 首次调用 MCP 可能较慢

**原因**: npx 需要下载 MCP 包

**解决方案**:
- 耐心等待首次调用完成（1-2 分钟）
- 后续调用会快很多（1-3s）
- 可以手动预下载：
  ```bash
  npx -y @modelcontextprotocol/server-filesystem --help
  npx -y @modelcontextprotocol/server-git --help
  ```

---

### 3. Shell MCP 默认禁用

**原因**: 安全风险（可执行任意命令）

**如需启用**:
1. 编辑配置文件，设置 `"disabled": false`
2. 同步配置
3. 重启 IDE
4. **谨慎使用**

---

### 4. 备份策略

**建议**:
- 每次应用模板前自动备份 ✅
- 定期手动备份重要配置
- 保留最近 5-10 个备份
- 清理旧备份以节省空间

**清理旧备份**:
```bash
# 查看备份大小
dir .lingma\backups\mcp\ /s

# 手动删除旧备份（保留最近 5 个）
# 使用文件管理器或 PowerShell
```

---

## 🐛 故障排除

### 问题 1: 模板不存在

**错误**: `❌ 模板不存在: xxx`

**解决**:
```bash
# 列出可用模板
python .lingma/scripts/sync-mcp-config.py list-templates

# 检查模板目录
dir .lingma\mcp-templates\
```

---

### 问题 2: 备份失败

**错误**: `❌ 备份失败: [Errno 13] Permission denied`

**原因**: 文件被占用或权限不足

**解决**:
1. 关闭 IDE
2. 重试备份
3. 如果仍然失败，手动复制文件

---

### 问题 3: 配置未生效

**症状**: 重启 IDE 后 MCP 仍不可用

**排查步骤**:
```bash
# 1. 确认全局配置已更新
type C:\Users\Administrator\AppData\Roaming\Lingma\SharedClientCache\mcp.json

# 2. 验证 JSON 格式
python -c "import json; json.load(open('C:/Users/Administrator/AppData/Roaming/Lingma/SharedClientCache/mcp.json'))"

# 3. 查看 IDE 日志
dir %APPDATA%\Lingma\logs\
```

---

## 💡 最佳实践

### 1. 为每个项目类型创建模板

```
.lingma/mcp-templates/
├── basic.json          # 通用开发
├── frontend.json       # 前端项目（添加 browser-devtools）
├── backend.json        # 后端项目（添加 database）
└── minimal.json        # 轻量级项目
```

---

### 2. 在 Git 中跟踪模板和配置

```bash
# 添加到 .gitignore（不跟踪全局配置）
echo "AppData/" >> .gitignore

# 但跟踪项目配置和模板
git add .lingma/config/mcp-servers.json
git add .lingma/mcp-templates/
git commit -m "chore: 添加 MCP 配置和模板"
```

---

### 3. 团队共享配置

**方式 1**: Git 共享模板
```bash
# 团队成员拉取最新配置
git pull

# 应用标准配置
python .lingma/scripts/sync-mcp-config.py apply-template basic
```

**方式 2**: 文档说明
在 `README.md` 中添加：
```markdown
## MCP 配置

本项目推荐使用以下 MCP 配置：

```bash
python .lingma/scripts/sync-mcp-config.py apply-template basic
```

然后重启 IDE。
```

---

### 4. 定期审查和更新

**每月检查**:
- [ ] 是否有新的 MCP 服务可用
- [ ] 现有配置是否需要调整
- [ ] 清理旧备份
- [ ] 收集团队反馈

---

## 📊 配置对比

| 模板 | Filesystem | Git | Shell | 适用场景 |
|------|-----------|-----|-------|---------|
| **basic** | ✅ | ✅ | ❌ | 大多数项目（推荐） |
| **minimal** | ❌ | ❌ | ❌ | 不需要 MCP 的项目 |
| **advanced** | ✅ | ✅ | ✅ | 需要执行复杂命令 |

---

## 🔗 相关文档

- [MCP 使用指南](MCP_USAGE_GUIDE.md)
- [MCP 测试清单](MCP_TEST_CHECKLIST.md)
- [MCP 快速验证](MCP_QUICK_VERIFICATION.md)
- [Lingma MCP 调研报告](../reports/lingma-mcp-investigation.md)

---

**最后更新**: 2024-01-15  
**维护者**: AI Assistant
