#!/bin/bash
# Git post-commit hook - 通知AI Agent新提交
# 
# 功能:
# 1. 异步通知Agent有新的commit
# 2. 传递commit元数据
# 3. 触发Agent上下文更新
# 4. 不阻塞commit流程（后台执行）

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B | head -1)
COMMIT_AUTHOR=$(git log -1 --pretty='%an <%ae>')
COMMIT_DATE=$(git log -1 --format=%ai)
SPEC_PATH="$PROJECT_ROOT/.lingma/specs/current-spec.md"
AUDIT_LOG="$PROJECT_ROOT/.lingma/logs/audit.log"

# 确保日志目录存在
mkdir -p "$(dirname "$AUDIT_LOG")"

# 审计日志函数
log_audit() {
    local event_type="$1"
    local status="$2"
    local message="$3"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    echo "{\"timestamp\":\"$timestamp\",\"event_type\":\"$event_type\",\"status\":\"$status\",\"message\":\"$message\",\"hook\":\"post-commit\"}" >> "$AUDIT_LOG"
}

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}📤 Post-Commit: 准备通知AI Agent...${NC}"

# 构建通知payload
PAYLOAD=$(cat <<EOF
{
  "event": "commit",
  "hash": "$COMMIT_HASH",
  "short_hash": "${COMMIT_HASH:0:8}",
  "message": "$COMMIT_MSG",
  "author": "$COMMIT_AUTHOR",
  "timestamp": "$COMMIT_DATE",
  "spec_path": "$SPEC_PATH",
  "project_root": "$PROJECT_ROOT"
}
EOF
)

# 方案1: HTTP通知（如果Agent服务运行）
AGENT_ENDPOINT="http://localhost:3000/api/agent/notify"

if curl -s --connect-timeout 2 --max-time 5 -o /dev/null -w "%{http_code}" "$AGENT_ENDPOINT" 2>/dev/null | grep -q "200\|404"; then
    # Agent服务可用，发送通知
    (
        curl -s -X POST "$AGENT_ENDPOINT" \
          -H "Content-Type: application/json" \
          -d "$PAYLOAD" > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}   ✅ 已成功通知AI Agent${NC}"
            log_audit "post-commit-notification" "passed" "Agent通知成功"
        else
            echo -e "${YELLOW}⚠️  Agent通知失败（非阻塞）${NC}"
            log_audit "post-commit-notification" "warning" "Agent通知失败"
        fi
    ) &
else
    # 方案2: 文件队列（Agent离线时的降级方案）
    QUEUE_DIR="$PROJECT_ROOT/.lingma/worker/queue"
    mkdir -p "$QUEUE_DIR"
    
    NOTIFICATION_FILE="$QUEUE_DIR/commit-${COMMIT_HASH:0:8}.json"
    echo "$PAYLOAD" > "$NOTIFICATION_FILE"
    
    echo -e "${YELLOW}⚠️  Agent服务未运行，已写入通知队列${NC}"
    echo "   队列文件: $NOTIFICATION_FILE"
    echo "   Agent启动后将自动处理"
    
    log_audit "post-commit-notification" "warning" "Agent离线，已入队"
fi

# 方案3: 更新最后提交记录（供Agent下次启动时读取）
LAST_COMMIT_FILE="$PROJECT_ROOT/.lingma/worker/state/last-commit.json"
mkdir -p "$(dirname "$LAST_COMMIT_FILE")"

cat > "$LAST_COMMIT_FILE" <<EOF
{
  "hash": "$COMMIT_HASH",
  "message": "$COMMIT_MSG",
  "author": "$COMMIT_AUTHOR",
  "timestamp": "$COMMIT_DATE",
  "spec_path": "$SPEC_PATH"
}
EOF

echo -e "${GREEN}   ✅ 已更新最后提交记录${NC}"
log_audit "post-commit-state-update" "passed" "状态更新成功"

# 可选: 显示Spec摘要（如果存在）
if [ -f "$SPEC_PATH" ]; then
    SPEC_STATUS=$(grep "^status:" "$SPEC_PATH" | head -1 | awk '{print $2}' | tr -d '\r\n')
    if [ -n "$SPEC_STATUS" ]; then
        echo -e "${GREEN}   ℹ️  当前Spec状态: $SPEC_STATUS${NC}"
    fi
fi

echo ""

exit 0
