#!/bin/bash
# Spec-Driven Development 初始化工具
# 用法: ./init-spec.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Spec-Driven Development 初始化${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查是否在正确的目录
if [ ! -d ".lingma" ]; then
    echo -e "${RED}❌ 错误: 未找到 .lingma 目录${NC}"
    echo -e "${YELLOW}💡 提示: 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 创建目录结构
echo -e "${GREEN}📁 创建目录结构...${NC}"

SPEC_DIR=".lingma/specs"
HISTORY_DIR="$SPEC_DIR/spec-history"
TEMPLATES_DIR="$SPEC_DIR/templates"
SCRIPTS_DIR=".lingma/scripts"

mkdir -p "$HISTORY_DIR"
mkdir -p "$TEMPLATES_DIR"
mkdir -p "$SCRIPTS_DIR"

echo -e "  ✓ $SPEC_DIR"
echo -e "  ✓ $HISTORY_DIR"
echo -e "  ✓ $TEMPLATES_DIR"
echo -e "  ✓ $SCRIPTS_DIR"
echo ""

# 复制模板文件
echo -e "${GREEN}📄 安装模板文件...${NC}"

SKILL_DIR=".lingma/skills/spec-driven-development"

if [ -d "$SKILL_DIR/templates" ]; then
    cp "$SKILL_DIR/templates/"*.md "$TEMPLATES_DIR/" 2>/dev/null || true
    echo -e "  ✓ Feature spec 模板"
    echo -e "  ✓ Refactor spec 模板"
    echo -e "  ✓ Bugfix spec 模板"
else
    echo -e "${YELLOW}⚠️  模板目录不存在，跳过${NC}"
fi
echo ""

# 安装脚本
echo -e "${GREEN}🔧 安装工具脚本...${NC}"

if [ -f "$SKILL_DIR/scripts/check-spec-status.py" ]; then
    cp "$SKILL_DIR/scripts/check-spec-status.py" "$SCRIPTS_DIR/"
    chmod +x "$SCRIPTS_DIR/check-spec-status.py"
    echo -e "  ✓ Spec 状态检查器"
else
    echo -e "${YELLOW}⚠️  脚本文件不存在，跳过${NC}"
fi
echo ""

# 创建 .gitignore 条目
echo -e "${GREEN}📝 配置 Git 忽略规则...${NC}"

GITIGNORE=".gitignore"
if [ -f "$GITIGNORE" ]; then
    if ! grep -q "\.lingma/specs/current-spec\.md" "$GITIGNORE" 2>/dev/null; then
        echo "" >> "$GITIGNORE"
        echo "# Spec files (keep history, ignore current)" >> "$GITIGNORE"
        echo ".lingma/specs/current-spec.md" >> "$GITIGNORE"
        echo "!**.lingma/specs/spec-history/**" >> "$GITIGNORE"
        echo -e "  ✓ 已添加到 .gitignore"
    else
        echo -e "  ℹ️  Git 规则已存在"
    fi
else
    echo -e "${YELLOW}⚠️  未找到 .gitignore 文件${NC}"
fi
echo ""

# 创建 README
echo -e "${GREEN}📖 创建使用说明...${NC}"

cat > "$SPEC_DIR/README.md" << 'EOF'
# Spec 管理规范

## 目录结构

```
specs/
├── README.md                    # 本文件
├── current-spec.md              # 当前活跃的 spec (不提交到 Git)
├── spec-history/                # 历史 spec 归档
│   ├── 2024-01-15-feature-x.md
│   └── 2024-01-20-refactor-y.md
└── templates/                   # Spec 模板
    ├── feature-spec.md
    ├── refactor-spec.md
    └── bugfix-spec.md
```

## 工作流程

### 1. 创建新 Spec

与 AI 助手对话，描述你的需求。AI 会自动：
- 选择合适的模板
- 引导你填写必要信息
- 创建 `current-spec.md`

### 2. 开发过程

AI 会：
- 自动加载 `current-spec.md`
- 按照 spec 中的任务列表执行
- 实时更新进度和状态
- 添加实施笔记

### 3. 完成与归档

当 spec 状态变为 `completed` 后：
```bash
# 归档 spec
mv current-spec.md spec-history/$(date +%Y-%m-%d)-feature-name.md

# 查看历史
ls -la spec-history/
```

## 常用命令

### 检查当前 spec 状态
```bash
python .lingma/scripts/check-spec-status.py
```

### 生成摘要报告
```bash
python .lingma/scripts/check-spec-status.py --summary
```

### 查看所有历史 spec
```bash
ls -lt spec-history/
```

## Spec 状态说明

- **draft**: 草稿阶段，正在收集需求
- **approved**: 已批准，可以开始开发
- **in-progress**: 开发进行中
- **completed**: 已完成并验收
- **cancelled**: 已取消

## 最佳实践

1. **保持 spec 更新**: 每次重大变更后更新 spec
2. **详细的实施笔记**: 记录关键决策和问题
3. **及时归档**: 完成后立即归档，保持工作区整洁
4. **版本控制**: 重要的 spec 变更应该 commit 到 Git

## 注意事项

- `current-spec.md` 不会提交到 Git（避免冲突）
- 历史 spec 会被提交（保留完整的项目演进历史）
- 定期清理过期的草稿 spec
EOF

echo -e "  ✓ README.md 已创建"
echo ""

# 显示下一步指引
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ 初始化完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}📚 下一步:${NC}"
echo ""
echo -e "1. ${GREEN}查看使用说明:${NC}"
echo -e "   cat $SPEC_DIR/README.md"
echo ""
echo -e "2. ${GREEN}开始第一个 spec:${NC}"
echo -e "   告诉 AI: \"我需要创建一个新功能...\""
echo ""
echo -e "3. ${GREEN}检查 spec 状态:${NC}"
echo -e "   python $SCRIPTS_DIR/check-spec-status.py"
echo ""
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}🎉 准备好开始 Spec-Driven Development 了！${NC}"
