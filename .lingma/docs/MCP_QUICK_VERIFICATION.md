# MCP 快速验证指南

## 🎯 目标

在 5 分钟内验证 Lingma MCP 配置是否正确生效。

---

## ✅ 前置检查

### 1. 确认全局配置已同步

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

如果失败，先运行：
```bash
python .lingma/scripts/sync-mcp-config.py
```

---

## 🧪 验证步骤

### Step 1: 重启 IDE（必须）

1. **完全关闭** Lingma IDE / VS Code / JetBrains
2. **重新启动** IDE
3. **等待插件加载**完成（约 10-30 秒）

---

### Step 2: 打开智能会话

1. 点击 Lingma 图标打开智能会话
2. **切换到智能体模式**（左下角切换按钮）
3. 确保使用的是 **qwen3** 模型

---

### Step 3: 测试 Filesystem MCP

在对话框中输入：

```
使用 filesystem MCP 列出当前目录的所有 Markdown 文件
```

**✅ 成功的标志**:
- Agent 识别需要使用 filesystem MCP
- 显示调用 MCP 工具的提示
- 返回 Markdown 文件列表，例如：
  ```
  找到以下 Markdown 文件:
  - README.md (2.3 KB)
  - CHANGELOG.md (1.5 KB)
  - docs/guide.md (5.7 KB)
  ```

**❌ 失败的标志**:
- Agent 说"未找到 MCP 服务"
- 报错 "failed to start command"
- 长时间无响应（> 60s）

---

### Step 4: 测试 Git MCP

在对话框中输入：

```
使用 git MCP 查看最近的 3 个 commits
```

**✅ 成功的标志**:
- Agent 调用 git MCP
- 返回 commit 列表，例如：
  ```
  最近的 commits:
  
  1. 39bc545 docs: Lingma MCP 深度调研完成
     Author: AI Assistant
     Date: 2024-01-15 18:00
  
  2. f9b5e05 fix: 同步 MCP 配置到 Lingma 全局位置
     ...
  ```

**❌ 失败的标志**:
- Agent 无法获取 Git 信息
- 报错或超时

---

### Step 5: 检查 IDE 日志（如果失败）

如果上述测试失败，查看日志：

**Windows 日志位置**:
```
%APPDATA%\Lingma\logs\
```

**查找关键词**:
- `MCP`
- `mcpServers`
- `server-filesystem`
- `failed to start`

**成功日志示例**:
```
[INFO] 2024-01-15 18:00:00 MCP server 'filesystem' started successfully
[INFO] 2024-01-15 18:00:01 MCP server 'git' started successfully
```

**失败日志示例**:
```
[ERROR] 2024-01-15 18:00:00 Failed to start MCP server 'filesystem'
[ERROR] Command not found: npx
```

---

## 🔍 故障排除

### 问题 1: MCP 服务未启动

**症状**: Agent 说找不到 MCP 服务

**解决方案**:
1. 确认全局配置文件存在：
   ```bash
   type C:\Users\Administrator\AppData\Roaming\Lingma\SharedClientCache\mcp.json
   ```

2. 重新同步配置：
   ```bash
   python .lingma/scripts/sync-mcp-config.py
   ```

3. **完全重启 IDE**（不是重新加载窗口）

---

### 问题 2: npx 命令找不到

**症状**: 日志显示 "Command not found: npx"

**解决方案**:
1. 确认 Node.js 已安装：
   ```bash
   node -v
   npx -v
   ```

2. 如果未安装，从 https://nodejs.org/ 下载 v18+

3. 重启 IDE

---

### 问题 3: 首次调用超时

**症状**: 第一次调用 MCP 时等待很久（> 60s）

**原因**: npx 需要下载 MCP 包

**解决方案**:
- **耐心等待**首次调用完成（可能需要 1-2 分钟）
- 后续调用会快很多（1-3s）
- 可以手动预下载：
  ```bash
  npx -y @modelcontextprotocol/server-filesystem --help
  npx -y @modelcontextprotocol/server-git --help
  ```

---

### 问题 4: Agent 不调用 MCP

**症状**: Agent 使用内置工具而非 MCP

**原因**: 
- Agent 认为内置工具足够
- MCP 描述不够清晰

**解决方案**:
- **明确指定**使用 MCP：
  ```
  使用 filesystem MCP 列出文件
  ```
  而非：
  ```
  列出文件
  ```

---

## 📊 验证结果记录

请填写以下表格：

| 测试项 | 状态 | 备注 |
|--------|------|------|
| 环境检查 | □ 通过 □ 失败 | |
| IDE 重启 | □ 完成 □ 未完成 | |
| Filesystem MCP | □ 成功 □ 失败 □ 未测试 | |
| Git MCP | □ 成功 □ 失败 □ 未测试 | |
| 日志检查 | □ 正常 □ 异常 □ 未检查 | |

**发现的问题**:
1. _______________
2. _______________

**截图/日志**:
- 粘贴相关截图或日志片段

---

## ✅ 验证完成标准

MCP 集成视为**成功**的条件：

- [ ] 环境检查通过（Node.js, npm, 配置）
- [ ] IDE 已重启
- [ ] Filesystem MCP 测试成功
- [ ] Git MCP 测试成功
- [ ] 日志无严重错误

---

## 💡 下一步

### 如果验证成功

✅ MCP 已正常工作！

**建议**:
1. 在日常开发中使用 MCP
2. 收集团队反馈
3. 根据需要调整配置

### 如果验证失败

❌ 需要进一步排查

**行动**:
1. 记录具体的错误信息
2. 查看完整日志
3. 创建 issue 报告问题
4. 考虑暂时禁用 MCP，使用内置工具

---

## 📞 获取帮助

如果遇到问题：

1. **查看完整文档**: `.lingma/docs/MCP_USAGE_GUIDE.md`
2. **查看调研报告**: `.lingma/reports/lingma-mcp-investigation.md`
3. **检查配置**: `.lingma/config/mcp-servers.json`
4. **查看日志**: `%APPDATA%\Lingma\logs\`

---

**验证人**: _______________  
**验证日期**: _______________  
**IDE 版本**: _______________  
**通义灵码版本**: _______________
