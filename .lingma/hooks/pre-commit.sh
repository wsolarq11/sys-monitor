#!/bin/bash
# Git pre-commit hook - Spec强制验证
# 
# 功能:
# 1. 检查current-spec.md是否存在且状态为in-progress
# 2. 检查是否有未回答的澄清问题[NEEDS CLARIFICATION]
# 3. 阻止无Spec提交或Spec不完整的提交
# 4. 落盘审计日志到.lingma/logs/audit.log
# 5. exit 1阻断提交
#
# 安装: 复制此文件到 .git/hooks/pre-commit 并赋予执行权限
# 绕过: git commit --no-verify (仅紧急情况使用)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取项目根目录
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
SPEC_PATH="$PROJECT_ROOT/.lingma/specs/current-spec.md"
VALIDATOR_SCRIPT="$PROJECT_ROOT/.lingma/scripts/spec-validator.py"
AUDIT_LOG="$PROJECT_ROOT/.lingma/logs/audit.log"

# 确保日志目录存在
mkdir -p "$(dirname "$AUDIT_LOG")"

# 审计日志函数
log_audit() {
    local event_type="$1"
    local status="$2"
    local message="$3"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    echo "{\"timestamp\":\"$timestamp\",\"event_type\":\"$event_type\",\"status\":\"$status\",\"message\":\"$message\",\"hook\":\"pre-commit\"}" >> "$AUDIT_LOG"
}

echo "🔍 执行Spec强制验证..."

# 🚨 根目录清洁度检查（P0优先级）
echo "   正在检查根目录清洁度..."
ROOT_CHECK_SCRIPT="$PROJECT_ROOT/scripts/check_root_cleanliness.py"

if [ -f "$ROOT_CHECK_SCRIPT" ]; then
    ROOT_CHECK_OUTPUT=$(python3 "$ROOT_CHECK_SCRIPT" 2>&1) || ROOT_CHECK_EXIT=$?
    
    if echo "$ROOT_CHECK_OUTPUT" | grep -q "工作区脏度: 10/10"; then
        echo -e "${GREEN}   ✅ 根目录清洁度检查通过${NC}"
    else
        echo -e "${RED}❌ 根目录清洁度检查失败${NC}"
        echo ""
        echo "$ROOT_CHECK_OUTPUT"
        echo ""
        echo "🚫 禁止以下文件出现在根目录："
        echo "  - mypy-errors*.txt (临时调试文件)"
        echo "  - docs/ (应使用 .lingma/docs/)"
        echo "  - scripts/ 外的任何脚本文件"
        echo "  - 任何数字/大小标记开头的文件"
        echo "  - 任何 temp_/tmp_ 前缀的文件"
        echo ""
        echo "请立即删除这些文件后重新提交。"
        
        log_audit "root-cleanliness-check" "failed" "根目录存在违规文件"
        exit 1
    fi
else
    echo -e "${YELLOW}   ⚠️  警告: check_root_cleanliness.py不存在，跳过根目录检查${NC}"
fi

echo ""

# 检查1: Spec文件是否存在
if [ ! -f "$SPEC_PATH" ]; then
    echo -e "${RED}❌ 错误: current-spec.md不存在${NC}"
    echo ""
    echo "Spec驱动开发要求每个提交都必须有对应的Spec。"
    echo "请先创建Spec文件:"
    echo "  $SPEC_PATH"
    echo ""
    echo "或使用 --no-verify 跳过验证(不推荐):"
    echo "  git commit --no-verify -m \"your message\""
    
    log_audit "pre-commit-check" "failed" "Spec文件不存在"
    exit 1
fi

# 检查2: 验证器脚本是否存在
if [ ! -f "$VALIDATOR_SCRIPT" ]; then
    echo -e "${YELLOW}⚠️  警告: spec-validator.py不存在，跳过详细验证${NC}"
    log_audit "pre-commit-check" "warning" "验证器脚本不存在"
    exit 0
fi

# 检查3: 运行Spec验证器
echo "   正在验证Spec完整性..."

VALIDATION_OUTPUT=$(python3 "$VALIDATOR_SCRIPT" --mode pre-commit --json 2>&1) || VALIDATION_EXIT=$?

if [ "${VALIDATION_EXIT:-0}" -ne 0 ]; then
    echo -e "${RED}❌ Spec验证失败${NC}"
    echo ""
    
    # 尝试解析JSON输出
    if command -v python3 &> /dev/null; then
        python3 -c "
import json, sys
try:
    result = json.loads('''$VALIDATION_OUTPUT''')
    if 'errors' in result:
        print('错误:')
        for error in result['errors']:
            print(f'  - {error}')
    if 'clarifications' in result and result['clarifications']:
        print('\n未回答的澄清问题:')
        for i, c in enumerate(result['clarifications'], 1):
            print(f'  {i}. {c[\"context\"]}')
except:
    print('$VALIDATION_OUTPUT')
" 2>/dev/null || echo "$VALIDATION_OUTPUT"
    else
        echo "$VALIDATION_OUTPUT"
    fi
    
    echo ""
    echo "请修复上述问题后重新提交。"
    echo ""
    echo "如需紧急提交，可使用 --no-verify (需团队负责人批准):"
    echo "  git commit --no-verify -m \"your message\""
    
    log_audit "pre-commit-check" "failed" "Spec验证失败"
    exit 1
fi

# 检查4: 解析验证结果，检查澄清问题
HAS_CLARIFICATIONS=$(python3 -c "
import json
result = json.loads('''$VALIDATION_OUTPUT''')
print('yes' if result.get('has_unanswered_questions', False) else 'no')
" 2>/dev/null || echo "no")

if [ "$HAS_CLARIFICATIONS" = "yes" ]; then
    echo -e "${RED}❌ 存在未回答的澄清问题${NC}"
    echo ""
    echo "Spec中包含[NEEDS CLARIFICATION]标记，必须先回答这些问题才能提交。"
    echo ""
    
    # 显示澄清问题
    python3 -c "
import json
result = json.loads('''$VALIDATION_OUTPUT''')
if 'clarifications' in result:
    for i, c in enumerate(result['clarifications'], 1):
        print(f'{i}. {c[\"context\"]}')
" 2>/dev/null
    
    echo ""
    echo "请在Spec中回答所有澄清问题(删除[NEEDS CLARIFICATION]标记)后重新提交。"
    
    log_audit "pre-commit-check" "failed" "存在未回答的澄清问题"
    exit 1
fi

# 检查5: 验证Spec状态
SPEC_STATUS=$(python3 -c "
import json
result = json.loads('''$VALIDATION_OUTPUT''')
print(result.get('metadata', {}).get('status', 'unknown'))
" 2>/dev/null || echo "unknown")

if [ "$SPEC_STATUS" != "in-progress" ] && [ "$SPEC_STATUS" != "review" ]; then
    echo -e "${YELLOW}⚠️  警告: Spec状态不是'in-progress'或'review' (当前: $SPEC_STATUS)${NC}"
    echo ""
    echo "建议将Spec状态设置为'in-progress'以表示正在积极开发。"
    echo ""
    
    # 警告但不阻止(可根据需要改为exit 1)
    log_audit "pre-commit-check" "warning" "Spec状态异常: $SPEC_STATUS"
fi

# 所有检查通过
echo -e "${GREEN}✅ Spec验证通过${NC}"
echo ""

# 显示Spec摘要
python3 -c "
import json
result = json.loads('''$VALIDATION_OUTPUT''')
metadata = result.get('metadata', {})
tasks = result.get('tasks', {})

print('Spec摘要:')
if metadata.get('status'):
    print(f'  状态: {metadata[\"status\"]}')
if metadata.get('priority'):
    print(f'  优先级: {metadata[\"priority\"]}')
if tasks:
    print(f'  任务进度: {tasks[\"completed\"]}/{tasks[\"total\"]} ({tasks[\"completion_rate\"]}%)')
" 2>/dev/null

echo ""

log_audit "pre-commit-check" "passed" "Spec验证通过"

exit 0
