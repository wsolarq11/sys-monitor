# MCP 使用指南

**版本**: v1.0  
**最后更新**: 2026-04-15

---

## 📋 概述

MCP（Model Context Protocol）是标准化协议，允许 AI 助手访问外部工具和数据源。

**当前配置**:
- ✅ **Filesystem MCP** - 文件系统操作
- ✅ **Git MCP** - Git 操作
- ⚠️ **Shell MCP** - Shell 命令（默认禁用）

---

## 🔧 快速开始

### 1. 验证环境

```bash
node -v   # 需要 v18+
npm -v    # 需要 v8+
```

### 2. 同步配置

Lingma IDE 读取**全局配置文件**，需同步项目配置：

```bash
python .lingma/scripts/sync-mcp-config.py
```

### 3. 验证安装

```bash
python .lingma/scripts/verify-mcp-setup.py
```

**预期输出**:
```
✅ Node.js: v24.14.1
✅ npm: 11.12.1
✅ MCP 配置文件存在
核心检查: 3/3 通过
```

---

## 🛠️ 可用工具

### Filesystem MCP

**用途**: 安全地读写文件、列出目录

**示例**:
```python
# 读取文件
content = mcp.filesystem.read_file("path/to/file.md")

# 写入文件
mcp.filesystem.write_file("path/to/file.md", "content")

# 列出目录
files = mcp.filesystem.list_directory("path/to/dir")
```

**限制**:
- 仅允许访问工作区目录
- 禁止访问系统敏感目录（/etc, /usr, C:\Windows 等）
- 文件大小限制: 10MB

---

### Git MCP

**用途**: 执行 Git 操作

**示例**:
```python
# 查看状态
status = mcp.git.status()

# 提交更改
mcp.git.commit("feat: add new feature")

# 推送代码
mcp.git.push()
```

**限制**:
- 仅在当前仓库内操作
- 禁止 force push
- 禁止修改 git config

---

## 📚 详细文档

- **配置管理**: guides/mcp-config.md
- **测试清单**: guides/mcp-test-checklist.md
- **故障排查**: guides/mcp-troubleshooting.md

---

## ⚠️ 常见问题

### Q1: MCP 工具不生效？

**检查步骤**:
1. 确认已同步配置到全局
2. 重启 Lingma IDE
3. 运行验证脚本

```bash
python .lingma/scripts/sync-mcp-config.py
python .lingma/scripts/verify-mcp-setup.py
```

### Q2: 权限被拒绝？

**原因**: MCP 配置限制了可访问目录

**解决**: 在 `.lingma/config/mcp.json` 中添加允许的目录

### Q3: 如何添加新的 MCP 服务？

**步骤**:
1. 创建模板: `cp .lingma/mcp-templates/example.json .lingma/config/mcp-new-service.json`
2. 编辑配置
3. 同步到全局: `python .lingma/scripts/sync-mcp-config.py`
4. 验证: `python .lingma/scripts/verify-mcp-setup.py`

---

## 🔗 相关资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [项目 MCP 配置](../config/mcp.json)
- [验证脚本](../scripts/verify-mcp-setup.py)
