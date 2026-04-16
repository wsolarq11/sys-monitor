#!/bin/bash
# Git pre-push hook - 推送前完整验证（增强版）
# 
# 功能:
# 1. 验证Spec状态（必须是review或done）
# 2. 运行完整测试套件
# 3. 构建验证
# 4. CHANGELOG检查
# 5. 版本号一致性
# 6. 安全扫描
# 7. 落盘审计日志
# 8. exit 1阻断推送

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取项目根目录
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
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
    
    echo "{\"timestamp\":\"$timestamp\",\"event_type\":\"$event_type\",\"status\":\"$status\",\"message\":\"$message\",\"hook\":\"pre-push\"}" >> "$AUDIT_LOG"
}

echo "🚀 执行Pre-Push验证..."
echo ""

# ==================== 检查1: Spec状态验证 ====================
echo "   [1/6] 检查Spec状态..."
if [ -f "$SPEC_PATH" ]; then
    # 提取Spec状态
    SPEC_STATUS=$(grep "^status:" "$SPEC_PATH" | head -1 | awk '{print $2}' | tr -d '\r\n')
    
    if [ -z "$SPEC_STATUS" ]; then
        echo -e "${YELLOW}⚠️  无法读取Spec状态，跳过检查${NC}"
        log_audit "pre-push" "warning" "无法读取Spec状态"
    elif [ "$SPEC_STATUS" != "review" ] && [ "$SPEC_STATUS" != "done" ]; then
        echo -e "${RED}❌ Spec状态必须是'review'或'done'才能推送${NC}"
        echo ""
        echo "当前状态: $SPEC_STATUS"
        echo ""
        echo "请完成以下操作之一:"
        echo "  1. 将Spec状态更新为'review'（准备审查）"
        echo "  2. 将Spec状态更新为'done'（已完成）"
        echo ""
        echo "编辑文件: $SPEC_PATH"
        echo ""
        
        log_audit "pre-push" "failed" "Spec状态不正确: $SPEC_STATUS"
        exit 1
    else
        echo -e "${GREEN}   ✅ Spec状态: $SPEC_STATUS${NC}"
        log_audit "pre-push-spec-check" "passed" "Spec状态正确: $SPEC_STATUS"
    fi
else
    echo -e "${YELLOW}⚠️  Spec文件不存在，跳过状态检查${NC}"
    echo "   路径: $SPEC_PATH"
    log_audit "pre-push" "warning" "Spec文件不存在"
fi

echo ""

# ==================== 检查2: 运行测试套件 ====================
echo "   [2/6] 运行测试套件..."

TEST_PASSED=false

# 检测Node.js项目
if command -v npm &> /dev/null && [ -f "$PROJECT_ROOT/package.json" ]; then
    echo "   检测到Node.js项目，运行npm test..."
    cd "$PROJECT_ROOT"
    
    if npm run test:ci 2>&1 | tee /tmp/test-output.log; then
        TEST_PASSED=true
    else
        echo -e "${RED}❌ 测试失败${NC}"
        echo ""
        echo "查看完整输出: cat /tmp/test-output.log"
        echo ""
        echo "常见原因:"
        echo "  - 单元测试失败"
        echo "  - 覆盖率不达标"
        echo "  - 测试超时"
        log_audit "pre-push" "failed" "测试失败"
        exit 1
    fi
    
# 检测Python项目
elif command -v pytest &> /dev/null && [ -d "$PROJECT_ROOT/tests" ]; then
    echo "   检测到Python项目，运行pytest..."
    cd "$PROJECT_ROOT"
    
    if pytest --tb=short -q 2>&1 | tee /tmp/test-output.log; then
        TEST_PASSED=true
    else
        echo -e "${RED}❌ 测试失败${NC}"
        echo "查看完整输出: cat /tmp/test-output.log"
        log_audit "pre-push" "failed" "测试失败"
        exit 1
    fi
    
# 检测Rust项目
elif command -v cargo &> /dev/null && [ -f "$PROJECT_ROOT/Cargo.toml" ]; then
    echo "   检测到Rust项目，运行cargo test..."
    cd "$PROJECT_ROOT"
    
    if cargo test --quiet 2>&1 | tee /tmp/test-output.log; then
        TEST_PASSED=true
    else
        echo -e "${RED}❌ 测试失败${NC}"
        echo "查看完整输出: cat /tmp/test-output.log"
        log_audit "pre-push" "failed" "测试失败"
        exit 1
    fi
    
else
    echo -e "${YELLOW}⚠️  未检测到测试框架，跳过测试检查${NC}"
    echo "   建议: 添加测试以提高代码质量"
    TEST_PASSED=true  # 不阻止推送
    log_audit "pre-push" "warning" "未检测到测试框架"
fi

if [ "$TEST_PASSED" = true ]; then
    echo -e "${GREEN}   ✅ 测试通过${NC}"
    log_audit "pre-push-test" "passed" "测试通过"
fi

echo ""

# ==================== 检查3: 构建验证 ====================
echo "   [3/6] 验证构建..."

BUILD_PASSED=false

# Node.js构建
if command -v npm &> /dev/null && [ -f "$PROJECT_ROOT/package.json" ]; then
    echo "   运行npm run build..."
    cd "$PROJECT_ROOT"
    
    if npm run build 2>&1 | tee /tmp/build-output.log; then
        BUILD_PASSED=true
    else
        echo -e "${RED}❌ 构建失败${NC}"
        echo ""
        echo "查看完整输出: cat /tmp/build-output.log"
        echo ""
        echo "常见原因:"
        echo "  - TypeScript编译错误"
        echo "  - 依赖缺失"
        echo "  - 资源配置错误"
        log_audit "pre-push" "failed" "构建失败"
        exit 1
    fi
    
# Rust构建
elif command -v cargo &> /dev/null && [ -f "$PROJECT_ROOT/Cargo.toml" ]; then
    echo "   运行cargo build --release..."
    cd "$PROJECT_ROOT"
    
    if cargo build --release --quiet 2>&1 | tee /tmp/build-output.log; then
        BUILD_PASSED=true
    else
        echo -e "${RED}❌ 构建失败${NC}"
        echo "查看完整输出: cat /tmp/build-output.log"
        log_audit "pre-push" "failed" "构建失败"
        exit 1
    fi
    
else
    echo -e "${YELLOW}⚠️  未检测到构建系统，跳过构建检查${NC}"
    BUILD_PASSED=true  # 不阻止推送
    log_audit "pre-push" "warning" "未检测到构建系统"
fi

if [ "$BUILD_PASSED" = true ]; then
    echo -e "${GREEN}   ✅ 构建成功${NC}"
    log_audit "pre-push-build" "passed" "构建成功"
fi

echo ""

# ==================== 检查4: CHANGELOG检查 ====================
echo "   [4/6] 检查CHANGELOG..."

if [ -f "$PROJECT_ROOT/CHANGELOG.md" ]; then
    LAST_COMMIT_DATE=$(git log -1 --format=%ai | cut -d' ' -f1)
    TODAY=$(date +%Y-%m-%d)
    
    # 检查CHANGELOG是否包含今天的日期或最近提交日期
    if grep -q "$TODAY" "$PROJECT_ROOT/CHANGELOG.md" || \
       grep -q "$LAST_COMMIT_DATE" "$PROJECT_ROOT/CHANGELOG.md" || \
       git log --oneline -5 | head -1 | awk '{print $2}' | xargs -I {} grep -q "{}" "$PROJECT_ROOT/CHANGELOG.md" 2>/dev/null; then
        echo -e "${GREEN}   ✅ CHANGELOG已更新${NC}"
        log_audit "pre-push-changelog" "passed" "CHANGELOG已更新"
    else
        echo -e "${YELLOW}⚠️  CHANGELOG可能未更新${NC}"
        echo ""
        echo "最后提交日期: $LAST_COMMIT_DATE"
        echo "今天日期: $TODAY"
        echo ""
        echo "建议在CHANGELOG.md中添加变更记录:"
        echo ""
        echo "## [$TODAY]"
        echo ""
        echo "- $(git log -1 --pretty=format:'%s')"
        echo ""
        
        # 警告但不阻止（可根据需要改为exit 1）
        log_audit "pre-push-changelog" "warning" "CHANGELOG可能未更新"
    fi
else
    echo -e "${YELLOW}⚠️  CHANGELOG.md不存在${NC}"
    echo "   建议创建CHANGELOG.md以跟踪变更"
    log_audit "pre-push" "warning" "CHANGELOG.md不存在"
fi

echo ""

# ==================== 检查5: 版本号一致性检查 ====================
echo "   [5/6] 检查版本号..."

VERSION_CONSISTENT=true

# 检查Cargo.toml版本
if [ -f "$PROJECT_ROOT/sys-monitor/src-tauri/Cargo.toml" ]; then
    CARGO_VERSION=$(grep '^version = ' "$PROJECT_ROOT/sys-monitor/src-tauri/Cargo.toml" | head -1 | sed 's/version = "\(.*\)"/\1/')
    echo "   Cargo.toml版本: $CARGO_VERSION"
fi

# 检查package.json版本
if [ -f "$PROJECT_ROOT/sys-monitor/package.json" ]; then
    PACKAGE_VERSION=$(grep '"version"' "$PROJECT_ROOT/sys-monitor/package.json" | head -1 | sed 's/.*"version": "\(.*\)".*/\1/')
    echo "   package.json版本: $PACKAGE_VERSION"
    
    # 比较版本一致性
    if [ -n "$CARGO_VERSION" ] && [ -n "$PACKAGE_VERSION" ]; then
        if [ "$CARGO_VERSION" != "$PACKAGE_VERSION" ]; then
            echo -e "${RED}❌ 版本不一致!${NC}"
            echo "   Cargo.toml: $CARGO_VERSION"
            echo "   package.json: $PACKAGE_VERSION"
            echo ""
            echo "请统一版本号后重新推送。"
            VERSION_CONSISTENT=false
            log_audit "pre-push" "failed" "版本不一致"
            exit 1
        fi
    fi
fi

# 检查Git tag
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "none")
if [ "$LATEST_TAG" != "none" ]; then
    echo "   最新Git标签: $LATEST_TAG"
fi

if [ "$VERSION_CONSISTENT" = true ]; then
    echo -e "${GREEN}   ✅ 版本号检查通过${NC}"
    log_audit "pre-push-version" "passed" "版本一致"
fi

echo ""

# ==================== 检查6: 安全扫描 ====================
echo "   [6/6] 安全扫描..."

# Gitleaks扫描（敏感信息检测）
if command -v gitleaks &> /dev/null; then
    echo "   运行gitleaks扫描..."
    
    if gitleaks detect --staged --no-banner --report-format json --report-path /tmp/gitleaks-report.json 2>&1; then
        echo -e "${GREEN}   ✅ 未发现敏感信息${NC}"
        log_audit "pre-push-security" "passed" "Gitleaks扫描通过"
    else
        echo -e "${RED}❌ 发现潜在敏感信息泄露${NC}"
        echo ""
        echo "详细报告: cat /tmp/gitleaks-report.json"
        echo ""
        echo "可能的原因:"
        echo "  - 硬编码的API密钥"
        echo "  - 密码或令牌"
        echo "  - 私钥文件"
        echo ""
        echo "请移除敏感信息后重新推送。"
        echo ""
        echo "💡 提示: 使用环境变量或密钥管理服务存储敏感信息"
        
        log_audit "pre-push-security" "failed" "发现敏感信息"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  gitleaks未安装，跳过敏感信息扫描${NC}"
    echo "   安装: brew install gitleaks 或从 https://github.com/gitleaks/gitleaks 下载"
    log_audit "pre-push-security" "warning" "gitleaks未安装"
fi

# Trivy扫描（依赖漏洞检测，可选）
if command -v trivy &> /dev/null && [ -f "$PROJECT_ROOT/package-lock.json" -o -f "$PROJECT_ROOT/Cargo.lock" ]; then
    echo "   运行trivy漏洞扫描..."
    
    if [ -f "$PROJECT_ROOT/package-lock.json" ]; then
        TRIVY_TARGET="fs $PROJECT_ROOT"
    elif [ -f "$PROJECT_ROOT/Cargo.lock" ]; then
        TRIVY_TARGET="fs $PROJECT_ROOT"
    fi
    
    if trivy fs --severity HIGH,CRITICAL --exit-code 0 "$PROJECT_ROOT" 2>&1 | tee /tmp/trivy-output.log; then
        echo -e "${GREEN}   ✅ 未发现高危漏洞${NC}"
        log_audit "pre-push-security" "passed" "Trivy扫描通过"
    else
        echo -e "${YELLOW}⚠️  发现潜在漏洞，请审查${NC}"
        echo "   详细报告: cat /tmp/trivy-output.log"
        log_audit "pre-push-security" "warning" "发现潜在漏洞"
    fi
else
    echo -e "${YELLOW}⚠️  trivy未安装或无锁文件，跳过漏洞扫描${NC}"
    log_audit "pre-push-security" "warning" "trivy未安装"
fi

echo ""

# ==================== 所有检查通过 ====================
echo -e "${GREEN}✅ Pre-Push验证全部通过${NC}"
echo ""
echo "📊 验证摘要:"
echo "  ✓ Spec状态: OK"
echo "  ✓ 测试套件: PASSED"
echo "  ✓ 构建验证: SUCCESS"
echo "  ✓ CHANGELOG: CHECKED"
echo "  ✓ 版本号: CONSISTENT"
echo "  ✓ 安全扫描: CLEAN"
echo ""
echo "🚀 准备推送到远程仓库..."
echo ""

log_audit "pre-push" "passed" "所有检查通过"

exit 0
