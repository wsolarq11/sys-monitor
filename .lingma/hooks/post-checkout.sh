#!/usr/bin/env bash
# Git post-checkout hook - Spec触发器
# 
# 用途：在git checkout/switch后自动验证Spec状态
# 安装：复制此文件到 .git/hooks/post-checkout 并赋予执行权限

set -e

# 获取仓库根目录
REPO_ROOT=$(git rev-parse --show-toplevel)

# Python脚本路径
VALIDATOR_SCRIPT="$REPO_ROOT/.lingma/scripts/spec-validator.py"

# 检查Python是否可用
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "⚠️  警告: 未找到Python，跳过Spec验证"
        exit 0
    fi
    PYTHON=python
else
    PYTHON=python3
fi

# 检查验证脚本是否存在
if [ ! -f "$VALIDATOR_SCRIPT" ]; then
    echo "⚠️  警告: Spec验证脚本不存在，跳过验证"
    exit 0
fi

# 执行post-checkout验证
echo ""
$PYTHON "$VALIDATOR_SCRIPT" post-checkout --repo-root "$REPO_ROOT"
exit_code=$?

# post-checkout不阻止操作，始终返回0
exit 0
