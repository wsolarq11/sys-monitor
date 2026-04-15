#!/usr/bin/env bash
# Git post-checkout hook - Spec触发器（增强版）
# 
# 用途：在git checkout/switch后自动验证Spec状态并触发评估
# 安装：复制此文件到 .git/hooks/post-checkout 并赋予执行权限

set -e

# 获取仓库根目录
REPO_ROOT=$(git rev-parse --show-toplevel)

# Python脚本路径
VALIDATOR_SCRIPT="$REPO_ROOT/.lingma/scripts/spec-validator.py"
RULE_ENGINE_SCRIPT="$REPO_ROOT/.lingma/scripts/rule-engine.py"
AUDIT_LOG="$REPO_ROOT/.lingma/logs/audit.log"

# 确保日志目录存在
mkdir -p "$(dirname "$AUDIT_LOG")"

# 审计日志函数
log_audit() {
    local event_type="$1"
    local message="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    echo "{\"timestamp\":\"$timestamp\",\"event_type\":\"$event_type\",\"message\":\"$message\",\"hook\":\"post-checkout\"}" >> "$AUDIT_LOG"
}

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

echo ""
echo "🔍 执行Spec状态检查..."

# 执行post-checkout验证
$PYTHON "$VALIDATOR_SCRIPT" post-checkout --repo-root "$REPO_ROOT"
exit_code=$?

# 调用rule-engine进行规则验证（如果存在）
if [ -f "$RULE_ENGINE_SCRIPT" ]; then
    echo "   正在验证规则合规性..."
    
    RULE_OUTPUT=$($PYTHON "$RULE_ENGINE_SCRIPT" --validate-spec --json 2>&1) || true
    
    # 检查是否有ERROR级别的违规
    HAS_ERRORS=$($PYTHON -c "
import json
try:
    violations = json.loads('''$RULE_OUTPUT''')
    has_error = any(v.get('severity') == 'ERROR' for v in violations)
    print('yes' if has_error else 'no')
except:
    print('no')
" 2>/dev/null || echo "no")
    
    if [ "$HAS_ERRORS" = "yes" ]; then
        echo "⚠️  检测到规则违规，建议修复"
        
        # 显示违规信息
        $PYTHON -c "
import json
try:
    violations = json.loads('''$RULE_OUTPUT''')
    for v in violations:
        if v.get('severity') == 'ERROR':
            print(f\"  [{v['severity']}] {v['message']}\")
            if v.get('suggestion'):
                print(f\"    建议: {v['suggestion']}\")
except:
    pass
" 2>/dev/null
        
        log_audit "post-checkout-rule-validation" "warning" "检测到规则违规"
    else
        echo "✅ 规则验证通过"
        log_audit "post-checkout-rule-validation" "passed" "规则验证通过"
    fi
fi

# post-checkout不阻止操作，始终返回0
log_audit "post-checkout" "completed" "Spec状态检查完成"
exit 0
