#!/bin/bash
# 验证 Spec-Driven Development 配置
# 用法: bash .lingma/scripts/verify-setup.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Spec-Driven Development 配置验证${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

PASS=0
FAIL=0
WARN=0

# 检查函数
check_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $description"
        ((PASS++))
        return 0
    else
        echo -e "  ${RED}✗${NC} $description (文件不存在: $file)"
        ((FAIL++))
        return 1
    fi
}

check_dir() {
    local dir=$1
    local description=$2
    
    if [ -d "$dir" ]; then
        echo -e "  ${GREEN}✓${NC} $description"
        ((PASS++))
        return 0
    else
        echo -e "  ${RED}✗${NC} $description (目录不存在: $dir)"
        ((FAIL++))
        return 1
    fi
}

check_executable() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ] && [ -x "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $description"
        ((PASS++))
        return 0
    elif [ -f "$file" ]; then
        echo -e "  ${YELLOW}⚠${NC} $description (存在但不可执行)"
        ((WARN++))
        return 1
    else
        echo -e "  ${RED}✗${NC} $description (文件不存在)"
        ((FAIL++))
        return 1
    fi
}

echo -e "${BLUE}1. 检查 Skill 文件${NC}"
check_file ".lingma/skills/spec-driven-development/SKILL.md" "SKILL.md 主文件"
check_file ".lingma/skills/spec-driven-development/QUICK_REFERENCE.md" "快速参考文档"
check_file ".lingma/skills/spec-driven-development/examples.md" "使用示例文档"
check_file ".lingma/skills/spec-driven-development/INSTALLATION_GUIDE.md" "安装指南"
echo ""

echo -e "${BLUE}2. 检查模板文件${NC}"
check_dir ".lingma/skills/spec-driven-development/templates" "模板目录"
check_file ".lingma/skills/spec-driven-development/templates/feature-spec.md" "Feature Spec 模板"
echo ""

echo -e "${BLUE}3. 检查工具脚本${NC}"
check_file ".lingma/skills/spec-driven-development/scripts/init-spec.sh" "初始化脚本"
check_file ".lingma/skills/spec-driven-development/scripts/check-spec-status.py" "状态检查脚本"
echo ""

echo -e "${BLUE}4. 检查 Rules 配置${NC}"
check_file ".lingma/rules/spec-session-start.md" "会话启动规则"
check_file ".lingma/rules/README.md" "规则索引"
echo ""

echo -e "${BLUE}5. 检查目录结构${NC}"
check_dir ".lingma/specs" "Specs 目录"
if [ -d ".lingma/specs" ]; then
    check_dir ".lingma/specs/spec-history" "历史归档目录"
    check_dir ".lingma/specs/templates" "模板副本目录"
fi
check_dir ".lingma/scripts" "脚本目录"
echo ""

echo -e "${BLUE}6. 检查 Python 环境${NC}"
if command -v python &> /dev/null || command -v python3 &> /dev/null; then
    PYTHON_CMD=$(command -v python3 || command -v python)
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    echo -e "  ${GREEN}✓${NC} Python 已安装 (版本: $PYTHON_VERSION)"
    ((PASS++))
    
    # 检查是否可以运行状态检查脚本
    if [ -f ".lingma/scripts/check-spec-status.py" ]; then
        if $PYTHON_CMD .lingma/scripts/check-spec-status.py &> /dev/null; then
            echo -e "  ${GREEN}✓${NC} 状态检查脚本可运行"
            ((PASS++))
        else
            echo -e "  ${YELLOW}⚠${NC} 状态检查脚本运行失败（可能因为没有 current-spec）"
            ((WARN++))
        fi
    fi
else
    echo -e "  ${RED}✗${NC} Python 未安装"
    ((FAIL++))
fi
echo ""

echo -e "${BLUE}7. 检查 Git 配置${NC}"
if [ -f ".gitignore" ]; then
    if grep -q "\.lingma/specs/current-spec\.md" .gitignore 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} .gitignore 已配置 current-spec.md 忽略规则"
        ((PASS++))
    else
        echo -e "  ${YELLOW}⚠${NC} .gitignore 缺少 current-spec.md 忽略规则"
        ((WARN++))
    fi
else
    echo -e "  ${YELLOW}⚠${NC} 未找到 .gitignore 文件"
    ((WARN++))
fi
echo ""

echo -e "${BLUE}8. 文件权限检查${NC}"
check_executable ".lingma/skills/spec-driven-development/scripts/init-spec.sh" "初始化脚本可执行权限"
check_executable ".lingma/scripts/check-spec-status.py" "状态检查脚本可执行权限"
echo ""

# 总结
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  验证结果总结${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}通过: $PASS${NC}"
if [ $WARN -gt 0 ]; then
    echo -e "${YELLOW}警告: $WARN${NC}"
fi
if [ $FAIL -gt 0 ]; then
    echo -e "${RED}失败: $FAIL${NC}"
fi
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ 所有检查通过！Spec-Driven Development 已正确配置。${NC}"
    echo ""
    echo -e "${BLUE}下一步:${NC}"
    echo "  1. 运行初始化脚本: bash .lingma/skills/spec-driven-development/scripts/init-spec.sh"
    echo "  2. 开始第一个 spec: 告诉 AI 您的需求"
    echo "  3. 查看文档: cat .lingma/skills/spec-driven-development/INSTALLATION_GUIDE.md"
    exit 0
else
    echo -e "${RED}❌ 存在 $FAIL 个失败项，请修复后重试。${NC}"
    echo ""
    echo -e "${YELLOW}建议操作:${NC}"
    echo "  1. 重新运行初始化脚本"
    echo "  2. 检查文件路径是否正确"
    echo "  3. 查看 INSTALLATION_GUIDE.md 获取帮助"
    exit 1
fi
