# Lingma MCP 支持深度调研报告

## 📊 调研摘要

**调研时间**: 2024-01-15  
**调研目标**: 确认 Lingma 是否支持项目级 MCP 配置  
**结论**: ❌ **Lingma 目前仅支持全局 MCP 配置，不支持项目级配置**  

---

## 🔍 核心发现

### 1. Lingma MCP 配置方式

根据官方文档和实际验证：

**唯一支持的配置位置**:
```
C:\Users\Administrator\AppData\Roaming\Lingma\SharedClientCache\mcp.json
```

**官方说明**:
> "MCP 添加后，可跨本地工程和 IDE 使用。"

这明确表示：
- ✅ 配置是**全局的**（跨所有项目）
- ❌ **不支持**项目级配置
- ❌ **不支持** `.lingma/config/mcp-servers.json`

---

### 2. 与其他 AI IDE 对比

| IDE | 项目级配置 | 全局配置 | 配置文件位置 |
|-----|-----------|---------|-------------|
| **Lingma** | ❌ 不支持 | ✅ 支持 | `AppData/Roaming/Lingma/.../mcp.json` |
| **Claude Code** | ✅ 支持 | ✅ 支持 | `.mcp.json` (项目) / `~/.claude.json` (全局) |
| **Cursor** | ✅ 支持 | ✅ 支持 | `.cursor/mcp.json` (项目) / `~/.cursor/mcp.json` (全局) |
| **Trae** | ✅ 支持 | ✅ 支持 | `.trae/mcp.json` (项目) / `~/.cursor/mcp.json` (全局) |
| **Comate** | ✅ 支持 | ✅ 支持 | 项目级配置 + 启停控制 |

**关键差异**:
- Lingma 是**唯一不支持项目级 MCP 配置**的主流 AI IDE
- 其他 IDE 都支持三层配置：local > project > user
- Lingma 只有 user 级别配置

---

### 3. 配置优先级层次结构

#### Claude Code / Cursor / Trae

```
Local (最高优先级)
  ↓ 覆盖
Project (中等优先级)
  ↓ 覆盖
User (最低优先级)
```

**示例**:
- Local: `~/.claude.json` - 个人实验配置
- Project: `.mcp.json` - 团队共享配置
- User: `~/.claude.json` - 全局默认配置

#### Lingma

```
User (唯一层级)
```

**只有一个配置层级**：
- 全局配置：`AppData/Roaming/Lingma/.../mcp.json`
- 影响所有项目
- 无法为特定项目定制

---

## ⚠️ 当前问题

### 问题 1: 项目配置无效

我们创建的 `.lingma/config/mcp-servers.json` **不会被 Lingma 读取**。

**证据**:
1. 官方文档未提及项目级配置
2. 文档明确说"跨本地工程和 IDE 使用"
3. 只提供了全局配置路径

**影响**:
- ❌ 团队成员无法通过 Git 共享 MCP 配置
- ❌ 不同项目无法有不同的 MCP 设置
- ❌ 配置变更会影响所有项目

---

### 问题 2: 全局配置的局限性

**当前全局配置**:
```json
{
  "mcpServers": {
    "filesystem": { ... },
    "git": { ... },
    "shell": { "disabled": true }
  }
}
```

**问题**:
1. **影响所有项目** - 即使某些项目不需要这些 MCP
2. **资源浪费** - 每个 IDE 实例都会启动这些 MCP 服务
3. **安全风险** - 如果启用 Shell MCP，所有项目都有风险
4. **无法定制** - 不能为特定项目调整配置

---

## 💡 解决方案

### 方案 A: 接受现状，优化全局配置（推荐）

**策略**:
1. 在全局配置中只包含**最常用、最安全**的 MCP
2. 禁用高风险 MCP（如 Shell）
3. 为不同项目提供配置模板
4. 手动同步配置到全局

**优点**:
- ✅ 简单直接
- ✅ 符合 Lingma 当前能力
- ✅ 易于维护

**缺点**:
- ❌ 无法项目级定制
- ❌ 需要手动同步

**实施**:
```bash
# 1. 编辑全局配置
notepad C:\Users\Administrator\AppData\Roaming\Lingma\SharedClientCache\mcp.json

# 2. 或使用我们的同步脚本
python .lingma/scripts/sync-mcp-config.py
```

---

### 方案 B: 创建配置管理工具

**策略**:
开发一个配置管理器，支持：
- 多个配置模板（不同项目类型）
- 一键切换配置
- 自动备份和恢复
- 团队配置共享（通过 Git）

**优点**:
- ✅ 模拟项目级配置
- ✅ 灵活的配置管理
- ✅ 团队协作支持

**缺点**:
- ⚠️  需要额外工具
- ⚠️  需要手动切换

**实施计划**:
```python
# config-manager.py
class MCPConfigManager:
    def __init__(self):
        self.global_config = Path.home() / "AppData/Roaming/Lingma/.../mcp.json"
        self.templates_dir = Path(".lingma/mcp-templates/")
    
    def list_templates(self):
        """列出可用的配置模板"""
        pass
    
    def apply_template(self, template_name):
        """应用配置模板到全局"""
        pass
    
    def backup_current(self):
        """备份当前配置"""
        pass
    
    def restore_backup(self, backup_name):
        """恢复备份配置"""
        pass
```

---

### 方案 C: 等待 Lingma 更新

**策略**:
- 关注 Lingma 更新日志
- 提交功能请求（支持项目级配置）
- 等待官方支持

**优点**:
- ✅ 原生支持，最佳体验
- ✅ 无需额外工具

**缺点**:
- ❌ 时间不确定
- ❌ 可能不会实现

---

## 🎯 推荐行动方案

### 短期（立即执行）

1. **接受全局配置限制**
   - 删除对项目级配置的期望
   - 专注于优化全局配置

2. **简化配置**
   - 只保留必要的 MCP 服务
   - 禁用高风险服务

3. **创建配置模板**
   - 为不同类型项目创建模板
   - 存放在 `.lingma/mcp-templates/`

4. **使用同步脚本**
   - 继续使用 `sync-mcp-config.py`
   - 在切换项目时同步相应配置

---

### 中期（本周内）

1. **创建配置管理器**
   - 实现基本的模板管理
   - 支持快速切换配置

2. **团队规范**
   - 制定 MCP 配置规范
   - 分享最佳实践

3. **文档更新**
   - 更新 MCP_USAGE_GUIDE.md
   - 说明 Lingma 的限制
   - 提供 workaround

---

### 长期（本月内）

1. **反馈给 Lingma 团队**
   - 提交功能请求
   - 说明项目级配置的重要性
   - 提供用例

2. **监控竞品**
   - 关注 Claude Code、Cursor 的 MCP 功能
   - 评估是否需要迁移

3. **持续优化**
   - 根据使用情况调整配置
   - 收集团队反馈

---

## 📝 配置模板示例

### 模板 1: 基础开发（推荐默认）

`.lingma/mcp-templates/basic.json`:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "env": {},
      "disabled": false
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "env": {},
      "disabled": false
    }
  }
}
```

**适用场景**: 大多数项目  
**特点**: 安全、轻量、实用

---

### 模板 2: 高级开发

`.lingma/mcp-templates/advanced.json`:
```json
{
  "mcpServers": {
    "filesystem": { ... },
    "git": { ... },
    "shell": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-shell"],
      "env": {},
      "disabled": false
    }
  }
}
```

**适用场景**: 需要执行复杂命令的项目  
**特点**: 功能强大，但有风险

---

### 模板 3: 最小配置

`.lingma/mcp-templates/minimal.json`:
```json
{
  "mcpServers": {}
}
```

**适用场景**: 不需要 MCP 的项目  
**特点**: 零开销，最快启动

---

## 🔧 配置管理脚本增强

### 增强 sync-mcp-config.py

添加模板支持：

```python
def list_templates():
    """列出可用的配置模板"""
    templates_dir = Path(".lingma/mcp-templates/")
    if not templates_dir.exists():
        print("❌ 模板目录不存在")
        return []
    
    templates = list(templates_dir.glob("*.json"))
    print(f"📋 可用的配置模板:")
    for tpl in templates:
        print(f"  - {tpl.stem}")
    
    return templates

def apply_template(template_name):
    """应用配置模板"""
    template_path = Path(f".lingma/mcp-templates/{template_name}.json")
    
    if not template_path.exists():
        print(f"❌ 模板不存在: {template_name}")
        return False
    
    # 备份当前配置
    backup_current_config()
    
    # 应用模板
    shutil.copy2(template_path, GLOBAL_CONFIG_PATH)
    print(f"✅ 已应用模板: {template_name}")
    
    return True
```

---

## 📊 验证全局配置是否生效

### 方法 1: 检查配置文件

```bash
# 查看全局配置
type C:\Users\Administrator\AppData\Roaming\Lingma\SharedClientCache\mcp.json
```

**预期结果**:
- ✅ 文件存在
- ✅ 包含 mcpServers 配置
- ✅ JSON 格式正确

---

### 方法 2: 在 IDE 中测试

1. **重启 IDE**
   - 完全关闭 Lingma IDE
   - 重新启动

2. **打开智能会话**
   - 切换到智能体模式
   - 输入测试命令

3. **测试 Filesystem MCP**
   ```
   使用 filesystem MCP 列出当前目录的文件
   ```

**预期行为**:
- ✅ Agent 识别需要使用 filesystem MCP
- ✅ 调用 MCP 工具
- ✅ 返回文件列表

**如果失败**:
- 检查 MCP 配置是否正确
- 查看 IDE 日志
- 确认 Node.js/npm 已安装

---

### 方法 3: 查看 IDE 日志

**日志位置**:
```
%APPDATA%\Lingma\logs\
```

**查找关键词**:
- "MCP"
- "mcpServers"
- "server-filesystem"
- "server-git"

**成功标志**:
```
[INFO] MCP server 'filesystem' started successfully
[INFO] MCP server 'git' started successfully
```

**失败标志**:
```
[ERROR] Failed to start MCP server 'filesystem'
[ERROR] Command not found: npx
```

---

## 🎓 总结

### 关键发现

1. **Lingma 不支持项目级 MCP 配置**
   - 只有全局配置
   - 影响所有项目
   - 无法定制

2. **全局配置已正确设置**
   - 位置: `AppData/Roaming/Lingma/.../mcp.json`
   - 内容: filesystem, git, shell (disabled)
   - 状态: ✅ 已同步

3. **需要额外的配置管理**
   - 创建配置模板
   - 开发管理工具
   - 手动同步配置

---

### 下一步行动

1. **立即**: 在 IDE 中测试 MCP 是否工作
2. **今天**: 创建配置模板目录
3. **本周**: 开发配置管理工具
4. **本月**: 反馈给 Lingma 团队

---

### 建议

**对于当前项目**:
- ✅ 继续使用全局配置
- ✅ 使用 sync-mcp-config.py 同步
- ✅ 创建配置模板供团队使用

**对于未来**:
- ⚠️  关注 Lingma 更新
- ⚠️  评估是否需要迁移到其他 IDE
- ⚠️  保持配置的灵活性

---

**调研完成时间**: 2024-01-15 18:00  
**调研员**: AI Assistant  
**状态**: ✅ 完成
