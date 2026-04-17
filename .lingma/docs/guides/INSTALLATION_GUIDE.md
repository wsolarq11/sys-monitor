# Spec-Driven Development 安装指南

**版本**: 1.0.0  
**最后更新**: 2026-04-17

## 系统要求

### 必需软件

- **Python**: 3.10 或更高版本
- **Node.js**: 18 或更高版本（用于 MCP 服务器）
- **Git**: 任意最新版本
- **操作系统**: Windows 10+, macOS 10.15+, Linux

### 推荐配置

- **内存**: 4GB RAM 最低，8GB 推荐
- **磁盘空间**: 500MB 可用空间
- **网络**: 稳定的互联网连接（用于 MCP 服务器）

---

## 快速安装

### 步骤 1: 克隆仓库

```bash
git clone <repository-url>
cd FolderSizeMonitor
```

### 步骤 2: 安装 Python 依赖

```bash
pip install psutil
```

### 步骤 3: 验证安装

```bash
python .lingma/scripts/verify-setup.py
```

预期输出：
```
✅ 所有检查通过
```

### 步骤 4: 配置 Git Hooks（可选但推荐）

```bash
python .lingma/scripts/install-hooks.py
```

这将安装：
- `pre-commit`: 提交前验证
- `pre-push`: 推送前验证

---

## 详细安装步骤

### Windows 安装

#### 1. 安装 Python

1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载 Python 3.10+ 安装包
3. 运行安装程序
4. **重要**: 勾选 "Add Python to PATH"
5. 点击 "Install Now"

验证安装：
```powershell
python --version
# 应显示: Python 3.10.x 或更高
```

#### 2. 安装 Node.js

1. 访问 [Node.js 官网](https://nodejs.org/)
2. 下载 LTS 版本（18+）
3. 运行安装程序
4. 使用默认设置

验证安装：
```powershell
node --version
# 应显示: v18.x.x 或更高

npm --version
# 应显示: 9.x.x 或更高
```

#### 3. 安装 Git

1. 访问 [Git 官网](https://git-scm.com/download/win)
2. 下载安装程序
3. 运行安装程序
4. 使用默认设置

验证安装：
```powershell
git --version
# 应显示: git version 2.x.x
```

#### 4. 克隆项目

```powershell
git clone <repository-url>
cd FolderSizeMonitor
```

#### 5. 安装依赖

```powershell
pip install psutil
```

#### 6. 验证安装

```powershell
python .lingma/scripts/verify-setup.py
```

---

### macOS 安装

#### 1. 使用 Homebrew 安装

```bash
# 安装 Homebrew（如果尚未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python
brew install python@3.10

# 安装 Node.js
brew install node

# 安装 Git
brew install git
```

#### 2. 克隆项目并安装依赖

```bash
git clone <repository-url>
cd FolderSizeMonitor
pip3 install psutil
python3 .lingma/scripts/verify-setup.py
```

---

### Linux 安装

#### Ubuntu/Debian

```bash
# 更新包列表
sudo apt update

# 安装 Python
sudo apt install python3 python3-pip

# 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装 Git
sudo apt install git

# 克隆项目并安装依赖
git clone <repository-url>
cd FolderSizeMonitor
pip3 install psutil
python3 .lingma/scripts/verify-setup.py
```

#### CentOS/RHEL

```bash
# 安装 EPEL 仓库
sudo yum install epel-release

# 安装 Python
sudo yum install python3 python3-pip

# 安装 Node.js
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# 安装 Git
sudo yum install git

# 克隆项目并安装依赖
git clone <repository-url>
cd FolderSizeMonitor
pip3 install psutil
python3 .lingma/scripts/verify-setup.py
```

---

## MCP 服务器配置

MCP (Model Context Protocol) 服务器提供额外的工具能力。

### 自动配置

运行验证脚本会自动检查 MCP 配置：

```bash
python .lingma/scripts/verify-mcp-setup.py
```

### 手动配置

编辑 `.lingma/config/mcp-servers.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "enabled": true
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "enabled": true
    },
    "shell": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-shell"],
      "enabled": false
    }
  }
}
```

**注意**: Shell MCP 默认禁用，因为它是高风险操作。

---

## 环境变量配置

创建 `.env` 文件（从 `.env.example` 复制）：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 自动化级别: conservative, balanced, aggressive, full_auto
AUTOMATION_LEVEL=balanced

# 启用学习功能
LEARNING_ENABLED=true

# 日志级别: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# 最大并发任务数
MAX_CONCURRENT_TASKS=3
```

---

## 验证安装

### 运行完整验证

```bash
python .lingma/scripts/verify-setup.py
```

这将检查：
- ✅ Python 版本
- ✅ Node.js 版本
- ✅ Git 配置
- ✅ 目录结构
- ✅ 关键文件
- ✅ MCP 配置
- ✅ 依赖安装

### 运行架构验证

```bash
python .lingma/scripts/validate-architecture.py
```

这将测试：
- ✅ 目录结构
- ✅ Rule 加载
- ✅ Agent 配置
- ✅ Skill 文件
- ✅ Spec 结构
- ✅ 决策缓存
- ✅ 批量日志
- ✅ UX 改进
- ✅ 会话中间件
- ✅ 性能指标

---

## 故障排除

### 问题 1: Python 版本过低

**症状**: `Python 3.10+ is required`

**解决方案**:
```bash
# 检查当前版本
python --version

# 升级到 Python 3.10+
# Windows: 从 python.org 下载新版本
# macOS: brew upgrade python
# Linux: sudo apt install python3.10
```

### 问题 2: Node.js 未找到

**症状**: `Node.js 18+ is required`

**解决方案**:
```bash
# 检查当前版本
node --version

# 安装 Node.js 18+
# 访问 nodejs.org 下载 LTS 版本
```

### 问题 3: pip 未找到

**症状**: `'pip' is not recognized`

**解决方案**:
```bash
# Windows
python -m pip install psutil

# macOS/Linux
python3 -m pip install psutil
```

### 问题 4: 权限错误

**症状**: `Permission denied`

**解决方案**:
```bash
# Windows: 以管理员身份运行 PowerShell
# macOS/Linux: 使用 sudo
sudo pip3 install psutil
```

### 问题 5: Git Hook 安装失败

**症状**: `Failed to install Git hooks`

**解决方案**:
```bash
# 手动安装
cp .lingma/hooks/pre-commit .git/hooks/
cp .lingma/hooks/pre-push .git/hooks/
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
```

---

## 下一步

安装完成后：

1. **阅读用户指南**: `.lingma/docs/guides/USER_GUIDE.md`
2. **查看快速参考**: `.lingma/docs/guides/BEST_PRACTICES.md`
3. **开始开发**: 查看 `.lingma/specs/current-spec.md` 了解当前任务

---

## 获取帮助

- **文档**: `.lingma/docs/` 目录
- **问题报告**: GitHub Issues
- **社区**: Discord / Slack

---

**许可证**: MIT  
**维护者**: AI Assistant  
**最后更新**: 2026-04-17
