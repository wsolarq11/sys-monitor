#!/bin/bash
# Git Hooks安装脚本
# 
# 功能:
# 1. 备份现有hooks
# 2. 安装增强版hooks
# 3. 设置执行权限
# 4. 验证安装

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取项目根目录
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_SOURCE="$PROJECT_ROOT/.lingma/hooks"
HOOKS_TARGET="$PROJECT_ROOT/.git/hooks"

echo -e "${BLUE}🔧 Git Hooks 安装程序${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查是否在Git仓库中
if [ ! -d "$PROJECT_ROOT/.git" ]; then
    echo -e "${RED}❌ 错误: 当前目录不是Git仓库${NC}"
    exit 1
fi

# 步骤1: 备份现有hooks
echo -e "${YELLOW}步骤 1/4: 备份现有Hooks...${NC}"

BACKUP_DIR="$PROJECT_ROOT/.lingma/backups/git-hooks-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -d "$HOOKS_TARGET" ] && [ "$(ls -A $HOOKS_TARGET 2>/dev/null)" ]; then
    cp -r "$HOOKS_TARGET"/* "$BACKUP_DIR/" 2>/dev/null || true
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR" | wc -l)
    echo -e "${GREEN}   ✅ 已备份 $BACKUP_COUNT 个现有hooks${NC}"
    echo "   备份位置: $BACKUP_DIR"
else
    echo -e "${GREEN}   ✅ 无需备份（无现有hooks）${NC}"
fi

echo ""

# 步骤2: 安装hooks
echo -e "${YELLOW}步骤 2/4: 安装Hooks...${NC}"

INSTALLED_COUNT=0

# Hook映射: 源文件 -> 目标文件名
declare -A HOOK_MAP=(
    ["pre-commit-enhanced.sh"]="pre-commit"
    ["pre-push-enhanced.sh"]="pre-push"
    ["post-commit.sh"]="post-commit"
    ["post-checkout-enhanced.sh"]="post-checkout"
)

for source_file in "${!HOOK_MAP[@]}"; do
    target_name="${HOOK_MAP[$source_file]}"
    source_path="$HOOKS_SOURCE/$source_file"
    target_path="$HOOKS_TARGET/$target_name"
    
    if [ -f "$source_path" ]; then
        # 复制hook文件
        cp "$source_path" "$target_path"
        
        # 设置执行权限
        chmod +x "$target_path"
        
        echo -e "${GREEN}   ✅ 安装: $target_name${NC}"
        ((INSTALLED_COUNT++))
    else
        echo -e "${YELLOW}⚠️  跳过: $source_file (不存在)${NC}"
    fi
done

if [ $INSTALLED_COUNT -eq 0 ]; then
    echo -e "${RED}❌ 未安装任何hooks${NC}"
    exit 1
fi

echo ""

# 步骤3: 验证安装
echo -e "${YELLOW}步骤 3/4: 验证安装...${NC}"

VERIFICATION_PASSED=true

for source_file in "${!HOOK_MAP[@]}"; do
    target_name="${HOOK_MAP[$source_file]}"
    target_path="$HOOKS_TARGET/$target_name"
    
    if [ -f "$target_path" ]; then
        if [ -x "$target_path" ]; then
            echo -e "${GREEN}   ✓ $target_name (已安装, 可执行)${NC}"
        else
            echo -e "${RED}   ✗ $target_name (缺少执行权限)${NC}"
            VERIFICATION_PASSED=false
        fi
    else
        echo -e "${RED}   ✗ $target_name (未找到)${NC}"
        VERIFICATION_PASSED=false
    fi
done

echo ""

if [ "$VERIFICATION_PASSED" = false ]; then
    echo -e "${RED}❌ 验证失败，请检查上述错误${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 所有hooks验证通过${NC}"
echo ""

# 步骤4: 显示使用说明
echo -e "${YELLOW}步骤 4/4: 配置说明${NC}"
echo ""

echo -e "${BLUE}📋 已安装的Hooks:${NC}"
echo "  ┌─────────────────────┬──────────────────────────────────┐"
echo "  │ Hook名称            │ 触发时机                         │"
echo "  ├─────────────────────┼──────────────────────────────────┤"
echo "  │ pre-commit          │ git commit 前                    │"
echo "  │                     │ 验证Spec完整性、规则合规性       │"
echo "  ├─────────────────────┼──────────────────────────────────┤"
echo "  │ pre-push            │ git push 前                      │"
echo "  │                     │ 运行测试、构建、安全检查         │"
echo "  ├─────────────────────┼──────────────────────────────────┤"
echo "  │ post-commit         │ git commit 后                    │"
echo "  │                     │ 通知AI Agent、更新上下文         │"
echo "  ├─────────────────────┼──────────────────────────────────┤"
echo "  │ post-checkout       │ git checkout 后                  │"
echo "  │                     │ 加载Spec、恢复会话状态           │"
echo "  └─────────────────────┴──────────────────────────────────┘"
echo ""

echo -e "${BLUE}🔒 安全提示:${NC}"
echo "  • 所有hooks都会记录审计日志: .lingma/logs/audit.log"
echo "  • 紧急情况可使用 --no-verify 绕过验证（不推荐）"
echo "  • 定期查看日志以监控系统健康度"
echo ""

echo -e "${BLUE}💡 常用命令:${NC}"
echo "  # 查看审计日志"
echo "  cat .lingma/logs/audit.log"
echo ""
echo "  # 临时绕过pre-commit（紧急情况）"
echo "  git commit --no-verify -m \"emergency fix\""
echo ""
echo "  # 临时绕过pre-push（紧急情况）"
echo "  git push --no-verify"
echo ""
echo "  # 重新安装hooks"
echo "  bash .lingma/scripts/install-hooks.sh"
echo ""
echo "  # 卸载hooks（恢复到备份）"
echo "  rm .git/hooks/pre-commit .git/hooks/pre-push .git/hooks/post-commit .git/hooks/post-checkout"
echo ""

echo -e "${BLUE}📊 监控指标:${NC}"
echo "  # 运行度量收集器"
echo "  python3 .lingma/scripts/metrics-collector.py"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Git Hooks安装完成！${NC}"
echo ""
echo "下一步:"
echo "  1. 尝试提交一次代码，观察hooks执行情况"
echo "  2. 查看审计日志确认hooks正常工作"
echo "  3. 阅读文档: .lingma/docs/GIT_HOOKS_GUIDE.md"
echo ""

exit 0
