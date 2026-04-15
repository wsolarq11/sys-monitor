# Phase 2: MCP 集成计划（基于 Lingma 原生能力）

## 📋 任务概述

**目标**: 利用 Lingma 原生的 MCP 支持，配置外部工具接入  
**预计时间**: 4h（从原计划 8h 减少 50%）  
**策略**: 使用 Lingma 原生 MCP 配置，而非自定义实现  

---

## 🎯 核心洞察

根据 Lingma 官方文档和我们的架构精简原则：

### ❌ 不需要做的事情

1. **不需要实现 MCP 管理器** - Lingma 已提供
2. **不需要迁移工具到 MCP** - Lingma 内置工具已足够
3. **不需要复杂的测试框架** - 通过实际使用验证

### ✅ 需要做的事情

1. **配置 MCP Servers** - 通过 JSON 配置文件
2. **选择合适的 MCP 服务** - filesystem, git, shell
3. **测试 MCP 工具调用** - 验证集成效果
4. **更新文档** - 记录配置和使用方法

---

## 📝 实施计划（简化版）

### Task-006: 配置 MCP 服务器 (2h)

#### Step 1: 创建 MCP 配置文件

创建 `.lingma/config/mcp-servers.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/workspace"
      ],
      "env": {}
    },
    "git": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-git"
      ],
      "env": {}
    },
    "shell": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-shell"
      ],
      "env": {}
    }
  }
}
```

#### Step 2: 安装依赖

```bash
# 检查 Node.js 版本
node -v  # 需要 v18+
npm -v   # 需要 v8+

# 如果未安装，安装 Node.js
# Windows: 从 nodejs.org 下载
# Mac: brew install node
```

#### Step 3: 验证配置

```bash
# 运行验证脚本
python .lingma/scripts/verify-mcp-setup.py
```

---

### Task-007: 测试 MCP 工具调用 (1h)

#### 测试 1: Filesystem MCP

```
使用 filesystem MCP 列出当前目录的文件
```

**预期结果**:
- Agent 调用 filesystem MCP
- 返回文件列表
- 显示在对话中

#### 测试 2: Git MCP

```
使用 git MCP 查看最近的 commits
```

**预期结果**:
- Agent 调用 git MCP
- 返回 commit 历史
- 格式化显示

#### 测试 3: Shell MCP

```
使用 shell MCP 运行一个简单的命令
```

**预期结果**:
- Agent 调用 shell MCP
- 执行命令
- 返回输出

---

### Task-008: 优化配置 (0.5h)

#### 优化 1: 调整权限

根据 `automation-policy.md` Rule，配置 MCP 工具的权限：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "env": {},
      "permissions": {
        "read": true,
        "write": true,
        "delete": false
      }
    }
  }
}
```

#### 优化 2: 添加环境变量

如果需要 API keys 或其他配置：

```json
{
  "mcpServers": {
    "example": {
      "command": "npx",
      "args": ["-y", "@example/mcp-server"],
      "env": {
        "API_KEY": "${API_KEY}",
        "BASE_URL": "https://api.example.com"
      }
    }
  }
}
```

---

### Task-009: 文档和最佳实践 (0.5h)

#### 创建 MCP 使用指南

文件: `.lingma/docs/MCP_USAGE_GUIDE.md`

内容包括：
- MCP 配置说明
- 可用的 MCP 服务列表
- 使用示例
- 故障排除

#### 更新 Spec

在 `current-spec.md` 中添加 MCP 集成笔记。

---

## 🔍 推荐的 MCP 服务

### 1. Filesystem MCP

**用途**: 文件系统操作  
**命令**: `npx -y @modelcontextprotocol/server-filesystem <path>`  
**功能**:
- 读取文件
- 写入文件
- 列出目录
- 搜索文件

**适用场景**:
- 批量文件操作
- 复杂文件搜索
- 跨目录操作

### 2. Git MCP

**用途**: Git 操作  
**命令**: `npx -y @modelcontextprotocol/server-git`  
**功能**:
- 查看 commit 历史
- 查看分支
- 查看 diff
- 管理 tags

**适用场景**:
- 代码审查
- 历史追溯
- 分支管理

### 3. Shell MCP

**用途**: Shell 命令执行  
**命令**: `npx -y @modelcontextprotocol/server-shell`  
**功能**:
- 执行任意 shell 命令
- 获取命令输出
- 后台运行

**适用场景**:
- 构建项目
- 运行测试
- 部署操作

**注意**: 此 MCP 风险较高，应谨慎使用

### 4. 其他有用的 MCP 服务

| 服务 | 用途 | 命令 |
|------|------|------|
| **Fetch MCP** | 网页抓取 | SSE URL |
| **Database MCP** | 数据库操作 | 自定义 |
| **Weather MCP** | 天气查询 | `npx -y @h1deya/mcp-server-weather` |
| **GitHub MCP** | GitHub API | 自定义 |

---

## ⚙️ 配置示例

### 完整配置文件

`.lingma/config/mcp-servers.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "."
      ],
      "env": {},
      "disabled": false
    },
    "git": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-git"
      ],
      "env": {},
      "disabled": false
    },
    "shell": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-shell"
      ],
      "env": {},
      "disabled": true
    }
  }
}
```

**注意**: 
- `shell` MCP 默认禁用（高风险）
- 需要时手动启用

---

## 🧪 验证脚本

创建 `.lingma/scripts/verify-mcp-setup.py`:

```python
#!/usr/bin/env python3
"""
MCP 配置验证脚本
"""

import json
import subprocess
from pathlib import Path


def check_nodejs():
    """检查 Node.js 是否安装"""
    try:
        result = subprocess.run(
            ["node", "-v"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print(f"✅ Node.js: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js 未安装或版本过低")
        return False


def check_npm():
    """检查 npm 是否安装"""
    try:
        result = subprocess.run(
            ["npm", "-v"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print(f"✅ npm: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm 未安装")
        return False


def check_mcp_config():
    """检查 MCP 配置文件"""
    config_file = Path(".lingma/config/mcp-servers.json")
    
    if not config_file.exists():
        print("❌ MCP 配置文件不存在")
        return False
    
    try:
        with open(config_file) as f:
            config = json.load(f)
        
        servers = config.get("mcpServers", {})
        print(f"✅ MCP 配置文件存在")
        print(f"   配置了 {len(servers)} 个服务器:")
        
        for name, server_config in servers.items():
            disabled = server_config.get("disabled", False)
            status = "⚠️  禁用" if disabled else "✅ 启用"
            print(f"   - {name}: {status}")
        
        return True
    except json.JSONDecodeError as e:
        print(f"❌ MCP 配置文件格式错误: {e}")
        return False


def verify_setup():
    """验证 MCP 设置"""
    print("=" * 60)
    print("  MCP 配置验证")
    print("=" * 60)
    print()
    
    checks = [
        ("Node.js", check_nodejs),
        ("npm", check_npm),
        ("MCP 配置", check_mcp_config),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n检查 {name}:")
        result = check_func()
        results.append(result)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n✅ MCP 配置正确！")
        print("\n下一步:")
        print("  1. 在 IDE 中重启通义灵码插件")
        print("  2. 测试 MCP 工具调用")
        print("  3. 根据需要启用/禁用 MCP 服务")
        return True
    else:
        print(f"\n❌ {total - passed} 个检查失败")
        print("\n建议:")
        print("  1. 安装 Node.js v18+")
        print("  2. 检查 MCP 配置文件格式")
        print("  3. 查看 MCP_USAGE_GUIDE.md")
        return False


if __name__ == "__main__":
    import sys
    success = verify_setup()
    sys.exit(0 if success else 1)
```

---

## 📊 预期收益

### 能力提升

| 能力 | 之前 | 之后 | 提升 |
|------|------|------|------|
| **文件操作** | Lingma 内置工具 | + MCP Filesystem | +20% |
| **Git 操作** | Lingma 内置工具 | + MCP Git | +15% |
| **Shell 执行** | Lingma 终端 | + MCP Shell | +10% |
| **外部集成** | 无 | MCP 生态 | ∞ |

### 代码量

| 项目 | 原计划 | 新计划 | 减少 |
|------|--------|--------|------|
| **实现代码** | ~1000 lines | ~100 lines | -90% |
| **配置文件** | ~200 lines | ~50 lines | -75% |
| **测试代码** | ~500 lines | ~100 lines | -80% |
| **文档** | ~300 lines | ~200 lines | -33% |
| **总计** | **~2000 lines** | **~450 lines** | **-78%** |

---

## ⚠️ 注意事项

### 1. 安全性

- **Filesystem MCP**: 限制访问路径，避免访问敏感目录
- **Git MCP**: 只读操作安全，写操作需谨慎
- **Shell MCP**: **高风险**，默认禁用，仅在必要时启用

### 2. 性能

- MCP 服务器启动有延迟（首次调用约 1-2s）
- 后续调用会复用连接，速度较快
- 避免频繁调用 MCP，优先使用 Lingma 内置工具

### 3. 兼容性

- 需要 Node.js v18+
- 某些 MCP 服务可能需要额外的环境变量
- 不同平台的命令可能略有差异

---

## 🚀 执行步骤

### Step 1: 创建配置文件 (现在)
- [ ] 创建 `.lingma/config/mcp-servers.json`
- [ ] 配置 filesystem, git, shell MCP
- [ ] 默认禁用 shell MCP

### Step 2: 创建验证脚本 (现在)
- [ ] 创建 `verify-mcp-setup.py`
- [ ] 测试验证逻辑

### Step 3: 运行验证 (现在)
- [ ] 检查 Node.js/npm
- [ ] 验证配置文件
- [ ] 修复问题

### Step 4: 测试 MCP 调用 (今天)
- [ ] 测试 filesystem MCP
- [ ] 测试 git MCP
- [ ] （可选）启用并测试 shell MCP

### Step 5: 文档化 (今天)
- [ ] 创建 MCP_USAGE_GUIDE.md
- [ ] 更新 current-spec.md
- [ ] 提交 Git

---

## 💡 总结

**Phase 2 的核心思想**:

> **利用 Lingma 原生的 MCP 支持，通过配置文件而非代码实现来集成外部工具。**

**优势**:
- ✅ 更少的代码（-78%）
- ✅ 更易维护（纯配置）
- ✅ 更强的能力（MCP 生态）
- ✅ 更安全（Lingma 管理权限）

**现在就开始了！** 🚀
