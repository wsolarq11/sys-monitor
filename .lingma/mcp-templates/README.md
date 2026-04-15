# MCP Servers Registry

本目录包含 Model Context Protocol (MCP) 服务器配置模板，遵循 [Anthropic MCP](https://modelcontextprotocol.io) 标准。

## 🔌 MCP 服务器列表

### 1. [basic.json](basic.json) - 基础 MCP 配置
- **类型**: Template（模板）
- **用途**: 
  - 文件系统访问
  - 基础工具集成
- **状态**: ✅ Available

### 2. [minimal.json](minimal.json) - 最小化配置
- **类型**: Template（模板）
- **用途**: 
  - 轻量级部署
  - 快速原型验证
- **状态**: ✅ Available

## 🏗️ 架构设计

### MCP 在自迭代流中的角色
```
Agent (决策层)
    ↓
Skills (能力层)
    ↓
MCP Servers (工具层) ← 本目录
    ↓
External Systems (外部系统)
```

### 加载策略
- **渐进式披露**: 仅在需要时连接 MCP 服务器
- **按需激活**: 根据任务类型选择对应的服务器
- **连接池管理**: 复用已建立的连接

## 📝 MCP 配置规范

### 文件命名
- 使用描述性名称 + `.json` 扩展名
- 示例: `filesystem.json`, `github.json`, `database.json`

### 必需字段
```json
{
  "mcpServers": {
    "server-name": {
      "command": "执行命令",
      "args": ["参数列表"],
      "env": {
        "环境变量": "值"
      }
    }
  }
}
```

### 最佳实践
- ✅ 每个服务器专注单一职责
- ✅ 提供清晰的文档说明
- ✅ 包含错误处理策略
- ❌ 避免过度复杂的配置
- ❌ 不要硬编码敏感信息（使用环境变量）

## 🔧 创建新 MCP 服务器

### 步骤 1: 确定需求
- 需要访问什么外部系统？
- 提供哪些工具/资源？
- 是否有现有的 MCP 服务器可用？

### 步骤 2: 选择基础
- 从现有模板复制
- 或从头创建

### 步骤 3: 配置服务器
```bash
# 复制模板
cp .lingma/mcp-templates/basic.json .lingma/config/mcp-custom.json

# 编辑配置
# 添加服务器定义
```

### 步骤 4: 测试连接
```bash
# 验证配置格式
python -m json.tool .lingma/config/mcp-custom.json

# 测试服务器连接
# （具体命令取决于 MCP 客户端）
```

### 步骤 5: 注册
- 更新本 README.md
- 添加到相关文档的引用

## 📊 服务器统计

| 类型 | 数量 | 状态 |
|------|------|------|
| Templates | 2 | ✅ Available |
| Active Configs | 0 | ⏳ Not Configured |
| **总计** | **2** | **✅ Ready** |

## 🔗 相关资源

- [Model Context Protocol 官方文档](https://modelcontextprotocol.io)
- [Anthropic MCP 指南](https://docs.anthropic.com/en/docs/agents-and-tools/mcp)
- [MCP Servers 社区仓库](https://github.com/modelcontextprotocol/servers)
- [Spec-Driven Development Skill](../skills/spec-driven-development/SKILL.md)

## 🚀 未来规划

### Phase 1: 基础服务器（已完成）
- [x] Filesystem MCP（文件系统访问）
- [x] GitHub MCP（代码仓库操作）

### Phase 2: 专业服务器（计划中）
- [ ] Database MCP（数据库查询）
- [ ] Docker MCP（容器管理）
- [ ] Testing MCP（测试执行）

### Phase 3: 高级集成（远期）
- [ ] Custom MCP Servers（自定义服务器）
- [ ] MCP Orchestration（服务器编排）

## 📅 更新历史

- **2026-04-15**: 创建 MCP Servers Registry，统一管理 MCP 配置
- 遵循渐进式披露原则，支持动态连接
