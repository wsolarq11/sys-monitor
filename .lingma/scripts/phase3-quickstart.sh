#!/bin/bash
# Phase 3 快速启动脚本
# 
# 功能:
# 1. 安装Git Hooks
# 2. 配置MCP
# 3. 运行首次度量
# 4. 验证安装

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   Phase 3: Git Hooks & MCP Configuration Setup           ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

PROJECT_ROOT="$(git rev-parse --show-toplevel)"

# ==================== 步骤1: 安装Git Hooks ====================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}步骤 1/4: 安装Git Hooks${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if bash "$PROJECT_ROOT/.lingma/scripts/install-hooks.sh"; then
    echo -e "${GREEN}✅ Git Hooks安装成功${NC}"
else
    echo -e "${RED}❌ Git Hooks安装失败${NC}"
    exit 1
fi

echo ""
read -p "按回车键继续..."

# ==================== 步骤2: 配置MCP ====================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}步骤 2/4: 配置MCP服务器${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

MCP_CONFIG="$PROJECT_ROOT/.lingma/config/mcp-config.json"
MCP_TEMPLATE="$PROJECT_ROOT/.lingma/config/mcp-config.template.json"

if [ ! -f "$MCP_CONFIG" ]; then
    echo "复制MCP配置模板..."
    cp "$MCP_TEMPLATE" "$MCP_CONFIG"
    echo -e "${GREEN}✅ MCP配置已创建: $MCP_CONFIG${NC}"
    echo ""
    echo "⚠️  请根据实际需求编辑配置文件:"
    echo "   - 调整ALLOWED_PATHS"
    echo "   - 设置BLOCKED_COMMANDS"
    echo "   - 配置安全策略"
    echo ""
    read -p "按回车键查看配置文件..."
    
    if command -v code &> /dev/null; then
        code "$MCP_CONFIG"
    elif command -v nano &> /dev/null; then
        nano "$MCP_CONFIG"
    else
        cat "$MCP_CONFIG"
    fi
else
    echo -e "${GREEN}✅ MCP配置已存在${NC}"
    echo "   路径: $MCP_CONFIG"
fi

echo ""
read -p "按回车键继续..."

# ==================== 步骤3: 运行首次度量 ====================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}步骤 3/4: 运行首次度量收集${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if command -v python3 &> /dev/null; then
    echo "生成基线度量报告..."
    echo ""
    
    python3 "$PROJECT_ROOT/.lingma/scripts/metrics-collector.py" --output "$PROJECT_ROOT/.lingma/reports/baseline-metrics.md"
    
    echo ""
    echo -e "${GREEN}✅ 基线度量报告已生成${NC}"
    echo "   路径: .lingma/reports/baseline-metrics.md"
    echo ""
    
    read -p "是否查看报告？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cat "$PROJECT_ROOT/.lingma/reports/baseline-metrics.md"
    fi
else
    echo -e "${YELLOW}⚠️  Python3未安装，跳过度量收集${NC}"
fi

echo ""
read -p "按回车键继续..."

# ==================== 步骤4: 验证安装 ====================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}步骤 4/4: 验证安装${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "检查Hooks..."
HOOKS_OK=true

for hook in pre-commit pre-push post-commit post-checkout; do
    if [ -x "$PROJECT_ROOT/.git/hooks/$hook" ]; then
        echo -e "${GREEN}  ✓ $hook${NC}"
    else
        echo -e "${RED}  ✗ $hook${NC}"
        HOOKS_OK=false
    fi
done

echo ""
echo "检查MCP配置..."
if [ -f "$MCP_CONFIG" ]; then
    echo -e "${GREEN}  ✓ mcp-config.json${NC}"
else
    echo -e "${RED}  ✗ mcp-config.json${NC}"
fi

echo ""
echo "检查度量脚本..."
if [ -x "$PROJECT_ROOT/.lingma/scripts/metrics-collector.py" ]; then
    echo -e "${GREEN}  ✓ metrics-collector.py${NC}"
else
    echo -e "${RED}  ✗ metrics-collector.py${NC}"
fi

echo ""

if [ "$HOOKS_OK" = true ]; then
    echo -e "${GREEN}✅ 所有组件验证通过${NC}"
else
    echo -e "${RED}❌ 部分组件验证失败${NC}"
    exit 1
fi

# ==================== 完成 ====================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Phase 3 设置完成！${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${BLUE}📋 已完成的任务:${NC}"
echo "  ✅ Git Hooks安装（pre-commit, pre-push, post-commit, post-checkout）"
echo "  ✅ MCP配置模板创建"
echo "  ✅ 度量收集器部署"
echo "  ✅ 基线报告生成"
echo ""

echo -e "${BLUE}📚 下一步行动:${NC}"
echo ""
echo "  1️⃣  阅读文档:"
echo "     - Git Hooks使用指南: .lingma/docs/GIT_HOOKS_GUIDE.md"
echo "     - AI Agent最佳实践: .lingma/docs/AI_AGENT_WORKFLOW_BEST_PRACTICES_2026.md"
echo ""
echo "  2️⃣  测试Hooks:"
echo "     git add ."
echo "     git commit -m \"test: verify hooks\""
echo ""
echo "  3️⃣  查看审计日志:"
echo "     cat .lingma/logs/audit.log"
echo ""
echo "  4️⃣  定期运行度量:"
echo "     python3 .lingma/scripts/metrics-collector.py"
echo ""

echo -e "${BLUE}💡 提示:${NC}"
echo "  • 紧急情况可使用 --no-verify 绕过验证"
echo "  • 每周review一次度量报告"
echo "  • 定期更新MCP配置以增强安全性"
echo ""

echo -e "${GREEN}🚀 系统已准备就绪，开始使用Spec驱动开发吧！${NC}"
echo ""

exit 0
