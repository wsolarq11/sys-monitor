# MCP配置未来规划

## 背景

本项目曾尝试配置MCP (Model Context Protocol)服务器以增强AI助手能力，但经过验证发现：

**Lingma目前不支持自定义MCP配置**

## 历史配置（已归档）

### 原配置文件
- `.lingma/config/mcp-servers.json` - 已删除
- `.lingma/mcp-templates/` - 已删除

### 原计划功能
1. **filesystem MCP**: 文件系统操作
2. **git MCP**: Git操作
3. **shell MCP**: Shell命令执行（高风险）

## 当前状态

所有MCP相关配置已清理，避免误导性内容。

## 未来展望

如果Lingma未来支持自定义MCP配置，可考虑增强的文件操作、Git工作流自动化等场景。

## 替代方案

当前通过Agent的Read/Write/Grep/Glob工具和Bash工具实现类似功能。

---

**归档日期**: 2026-04-16  
**原因**: Lingma不支持自定义MCP配置