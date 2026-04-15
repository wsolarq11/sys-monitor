#!/usr/bin/env bash
# Git pre-commit hook - Spec强制约束
# 
# 用途：在commit前强制验证Spec状态
# 安装：复制此文件到 .git/hooks/pre-commit 并赋予执行权限

set -e

# 获取仓库根目录
REPO_ROOT=$(git rev-parse --show-toplevel)

# Python脚本路径
VALIDATOR_SCRIPT="$REPO_ROOT/.lingma/scripts/spec-validator.py"

# 检查Python是否可用
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ 错误: 未找到Python，无法执行Spec验证"
        echo "   请安装Python 3.6+或禁用pre-commit钩子"
        exit 1
    fi
    PYTHON=python
else
    PYTHON=python3
fi

# 检查验证脚本是否存在
if [ ! -f "$VALIDATOR_SCRIPT" ]; then
    echo "❌ 错误: Spec验证脚本不存在"
    echo "   路径: $VALIDATOR_SCRIPT"
    echo "   请先完成Spec-Driven系统初始化"
    exit 1
fi

# 执行pre-commit验证（严格模式）
echo ""
$PYTHON "$VALIDATOR_SCRIPT" pre-commit --repo-root "$REPO_ROOT"
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "🚫 Commit被阻止：Spec验证失败"
    echo "   修复问题后重新commit"
    exit 1
fi

exit 0
