# MCP 使用指南

## 📋 概述

本指南介绍如何在本项目中使用 MCP（Model Context Protocol）服务。

**MCP 是什么**: MCP 是一种标准化协议，允许 AI 助手访问外部工具和数据源。

**我们的配置**: 
- ✅ Filesystem MCP - 文件系统操作
- ✅ Git MCP - Git 操作
- ⚠️  Shell MCP - Shell 命令（默认禁用）

---

## 🔧 前置条件

### 1. 确保依赖已安装

```bash
# 检查 Node.js 和 npm
node -v   # 需要 v18+
npm -v    # 需要 v8+

# 如果未安装，从 https://nodejs.org/ 下载
```

### 2. 验证 MCP 配置

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

### 3. 同步配置到全局（重要！）

Lingma IDE 读取的是**全局配置文件**，而非项目配置。

```bash
# 同步项目配置到全局
python .lingma/scripts/sync-mcp-config.py
```

**这会**:
- ✅ 将 `.lingma/config/mcp-servers.json` 复制到全局位置
- ✅ 备份现有全局配置
- ✅ 使 IDE 立即生效

**全局配置位置**:
```
C:\Users\Administrator\AppData\Roaming\Lingma\SharedClientCache\mcp.json
```

### 4. 重启 IDE

在 VS Code / JetBrains / Lingma IDE 中：
1. 重新加载窗口（Ctrl+Shift+P → "Reload Window"）
2. 确保通义灵码插件已更新到最新版本（v2.5.0+）

---

## 📦 可用的 MCP 服务

### 1. Filesystem MCP

**用途**: 文件系统操作  
**状态**: ✅ 启用  
**风险等级**: 🟢 低风险  

**功能**:
- 读取文件内容
- 写入文件
- 列出目录
- 搜索文件
- 文件元数据查询

**使用示例**:

```
👤 用户: 使用 filesystem MCP 列出当前目录的所有 Markdown 文件

🤖 Agent: [调用 filesystem MCP]
   找到以下 Markdown 文件:
   - README.md (2.3 KB)
   - CHANGELOG.md (1.5 KB)
   - docs/guide.md (5.7 KB)
   ...
```

```
👤 用户: 使用 filesystem MCP 读取 package.json 的内容

🤖 Agent: [调用 filesystem MCP]
   {
     "name": "folder-size-monitor",
     "version": "1.0.0",
     ...
   }
```

---

### 2. Git MCP

**用途**: Git 版本控制操作  
**状态**: ✅ 启用  
**风险等级**: 🟢 低风险  

**功能**:
- 查看 commit 历史
- 查看分支列表
- 查看文件 diff
- 查看 tags
- 查看远程仓库信息

**使用示例**:

```
👤 用户: 使用 git MCP 查看最近的 5 个 commits

🤖 Agent: [调用 git MCP]
   最近的 commits:
   
   1. ebc0fc4 (HEAD -> main) feat: Phase 2 Task-006 - MCP 服务器配置完成
      Author: AI Assistant
      Date: 2024-01-15 17:45
   
   2. 7020ee3 refactor: 移除冗余代码，改用 Lingma 原生能力
      Author: AI Assistant
      Date: 2024-01-15 17:30
   
   3. abc1234 fix: 修复验证脚本问题
      ...
```

```
👤 用户: 使用 git MCP 查看当前分支

🤖 Agent: [调用 git MCP]
   当前分支: main
   所有分支:
   - main (当前)
   - develop
   - feature/mcp-integration
```

---

### 3. Shell MCP

**用途**: Shell 命令执行  
**状态**: ⚠️  禁用（高风险）  
**风险等级**: 🔴 严重风险  

**⚠️  警告**: Shell MCP 可以执行任意命令，包括危险操作（如 `rm -rf /`）。仅在必要时启用，并谨慎使用。

**如何启用**:

编辑 `.lingma/config/mcp-servers.json`:

```json
{
  "mcpServers": {
    "shell": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-shell"],
      "env": {},
      "disabled": false  // ← 改为 false
    }
  }
}
```

然后重启 IDE。

**使用示例**（启用后）:

```
👤 用户: 使用 shell MCP 运行 npm test

🤖 Agent: ⚠️  高风险操作确认
   
   您请求执行 shell 命令: npm test
   
   这将在您的系统上执行命令。
   
   如需继续，请输入: APPROVE
```

---

## 🧪 测试 MCP

### 测试 1: Filesystem MCP

**步骤**:

1. 在 IDE 中打开智能会话
2. 切换到智能体模式
3. 输入：

```
使用 filesystem MCP 列出当前目录的文件
```

**预期结果**:
- Agent 应该调用 filesystem MCP
- 返回文件列表
- 显示在对话中

**如果失败**:
- 检查 MCP 配置是否正确
- 检查 Node.js/npm 是否安装
- 查看 IDE 日志中的错误信息

---

### 测试 2: Git MCP

**步骤**:

1. 在 IDE 中打开智能会话
2. 切换到智能体模式
3. 输入：

```
使用 git MCP 查看最近的 commit
```

**预期结果**:
- Agent 应该调用 git MCP
- 返回最近的 commit 信息
- 显示作者、日期、消息等

**如果失败**:
- 确保当前目录是 Git 仓库
- 检查 git 是否已安装
- 查看 IDE 日志

---

### 测试 3: Shell MCP（可选）

**前提**: 已启用 Shell MCP

**步骤**:

1. 在 IDE 中打开智能会话
2. 切换到智能体模式
3. 输入：

```
使用 shell MCP 运行 echo "Hello MCP"
```

**预期结果**:
- Agent 应该请求确认（高风险）
- 输入 "APPROVE" 后执行
- 返回命令输出: "Hello MCP"

**⚠️  注意**: 测试完成后，建议重新禁用 Shell MCP

---

## 🔍 故障排除

### 问题 1: MCP 服务无法启动

**症状**: Agent 尝试调用 MCP 时失败

**可能原因**:
1. Node.js 未安装或版本过低
2. npx 无法下载 MCP 包
3. 网络问题

**解决方案**:

```bash
# 1. 检查 Node.js 版本
node -v  # 需要 v18+

# 2. 手动安装 MCP 包
npx -y @modelcontextprotocol/server-filesystem --help
npx -y @modelcontextprotocol/server-git --help

# 3. 检查网络连接
ping registry.npmjs.org
```

---

### 问题 2: MCP 调用超时

**症状**: Agent 调用 MCP 后长时间无响应

**可能原因**:
1. 首次调用需要下载包（较慢）
2. MCP 服务器启动慢
3. 资源不足

**解决方案**:
- 等待首次调用完成（可能需要 10-30s）
- 后续调用会复用连接，速度较快
- 关闭其他占用资源的程序

---

### 问题 3: 权限错误

**症状**: MCP 无法访问某些文件或目录

**可能原因**:
1. 文件系统权限不足
2. MCP 配置的路径不正确

**解决方案**:

检查 `.lingma/config/mcp-servers.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "."  // ← 确保路径正确
      ]
    }
  }
}
```

---

### 问题 4: IDE 中看不到 MCP 选项

**症状**: Agent 不调用 MCP，或使用内置工具

**可能原因**:
1. IDE 插件版本过旧
2. MCP 配置未加载
3. 需要重启 IDE

**解决方案**:

1. 更新通义灵码插件到最新版本（v2.5.0+）
2. 重新加载窗口（Ctrl+Shift+P → "Reload Window"）
3. 检查 MCP 配置文件格式是否正确
4. 查看 IDE 日志中的错误信息

---

## 💡 最佳实践

### 1. 优先使用 Lingma 内置工具

**原则**: MCP 是补充，不是替代

**示例**:

```
✅ 好: 直接让 Agent 读取文件（使用内置工具）
   "读取 package.json 的内容"

✅ 好: 批量操作时使用 MCP
   "使用 filesystem MCP 列出所有 .md 文件"

❌ 不好: 简单操作用 MCP
   "使用 filesystem MCP 读取单个文件"
```

---

### 2. 谨慎使用 Shell MCP

**原则**: 最小权限，明确授权

**建议**:
- 默认禁用 Shell MCP
- 仅在必要时启用
- 使用后重新禁用
- 始终审查要执行的命令

---

### 3. 监控 MCP 使用情况

**方法**:
- 查看 IDE 日志
- 观察 Agent 的调用行为
- 记录性能问题

**工具**:
```bash
# 查看 MCP 配置
cat .lingma/config/mcp-servers.json

# 验证配置
python .lingma/scripts/verify-mcp-setup.py
```

---

### 4. 定期更新 MCP 包

**方法**:

```bash
# 清除 npx 缓存
npx clear-npx-cache

# 重新调用 MCP（会自动下载最新版本）
```

---

## 📊 MCP vs 内置工具对比

| 场景 | 推荐方式 | 原因 |
|------|---------|------|
| 读取单个文件 | 内置工具 | 更快，无需额外调用 |
| 批量文件操作 | Filesystem MCP | 更高效，支持复杂查询 |
| 查看 Git 历史 | Git MCP | 结构化数据，易解析 |
| 简单 Git 命令 | 内置终端 | 更直接 |
| 执行构建命令 | 内置终端 | 更安全，可控 |
| 复杂 Shell 脚本 | Shell MCP | （谨慎使用） |

---

## 🔗 相关资源

### 官方文档

- [Lingma MCP 使用指南](https://help.aliyun.com/zh/lingma/user-guide/guide-for-using-mcp)
- [MCP 官方网站](https://modelcontextprotocol.io/)
- [MCP GitHub](https://github.com/modelcontextprotocol)

### MCP 市场

- [魔搭社区 MCP 市场](https://modelscope.cn/mcp)
- [Higress MCP 市场](https://higress.cn/mcp)

### 本项目文档

- [MCP 配置](../config/mcp-servers.json)
- [验证脚本](../scripts/verify-mcp-setup.py)
- [Phase 2 计划](../specs/phase2-mcp-plan.md)
- [Task-006 完成报告](../reports/phase2-task006-completion.md)

---

## ❓ 常见问题

### Q1: MCP 会影响性能吗？

**A**: 
- 首次调用较慢（需要下载包，10-30s）
- 后续调用较快（复用连接，1-2s）
- 对于简单操作，优先使用内置工具

### Q2: MCP 安全吗？

**A**:
- Filesystem 和 Git MCP 相对安全（只读操作为主）
- Shell MCP 风险高（可执行任意命令）
- 遵循最小权限原则
- 定期审查 MCP 配置

### Q3: 可以自定义 MCP 服务器吗？

**A**:
- 可以！您可以开发自己的 MCP 服务器
- 参考 [MCP 开发者文档](https://modelcontextprotocol.io/development)
- 在配置文件中添加自定义服务器

### Q4: MCP 配置可以团队共享吗？

**A**:
- 可以！将 `.lingma/config/mcp-servers.json` 提交到 Git
- 团队成员拉取后即可使用相同配置
- 注意：不要包含敏感信息（如 API keys）

---

## 🎯 总结

**MCP 的价值**:
- ✅ 扩展 AI 助手的能力边界
- ✅ 标准化外部工具接入
- ✅ 丰富的生态系统

**使用原则**:
- 🎯 优先使用内置工具
- 🔒 谨慎使用高风险 MCP
- 📊 监控性能和安全性
- 🔄 定期更新和维护

**现在就试试吧！**

在 IDE 中输入：
```
使用 filesystem MCP 列出当前目录的文件
```
