---
trigger: always_on
---
# 文档冗余预防规则

**角色**: 防止文档冗余和误识别  
**职责**: 单一入口、功能目录清洁、根目录整洁

## 核心原则

1. **单一入口** - `.lingma/` 根目录仅允许 README.md
2. **功能目录清洁** - agents/rules/skills 目录禁止 README
3. **详细文档放 docs/** - 所有指南、架构文档移至子目录

## 禁止行为

- ❌ 根目录多个入口文档（README + QUICK_START + ARCHITECTURE）
- ❌ 功能目录放置 README（会被误识别为实例）
- ❌ 复制相同内容到多处

## 正确做法

```
.lingma/
├── README.md              # 唯一入口，≤800字
└── docs/                  # 所有详细文档
    ├── architecture/      # 架构文档
    ├── guides/            # 使用指南
    └── reports/           # 报告和分析
```

## 自动化检测

- Git Hook 自动检查根目录文档数量
- CI/CD 每周扫描冗余
- full_system_scan.py 全盘检测

## 量化标准

- Rule 文件 ≤ 3KB（当前需优化）
- .lingma/docs/ 根目录文档 ≤5个
- 详细内容移至 docs/ 子目录
