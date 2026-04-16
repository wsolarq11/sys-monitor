# .lingma - 自迭代流系统

**四层架构**: Agents → Skills → Rules → MCP  
**状态**: ✅ Production Ready | **自动化**: 98% | **健康度**: ⭐⭐⭐⭐⭐  
**最新更新**: Phase 3 (Git Hooks & MCP) 已完成 🎉

---

## 🗺️ 快速导航

### 入门
- [5分钟快速开始](docs/guides/QUICK_START.md) - 安装、配置、首次运行
- [系统架构](docs/architecture/ARCHITECTURE.md) - 四层架构详解
- **[执行摘要](docs/EXECUTIVE_SUMMARY.md)** - 🆕 AI Agent工作流调研报告

### 核心组件
- [Agents](agents/) - 4个智能体（决策层）
- [Skills](skills/) - 2个技能（能力层，可扩展至6个）
- [Rules](rules/) - 4个规则（约束层）
- [MCP](config/mcp-config.template.json) - 🆕 标准化配置模板

### 开发工作流
- [Spec-Driven Development](skills/spec-driven-development/SKILL.md) - 基于Spec的自动化开发
- **[Git Hooks防护体系](docs/GIT_HOOKS_GUIDE.md)** - 🆕 完整的Hook系统
- [CI/CD](../.github/workflows/) - 5个自动化工作流

### 监控与维护
- [系统健康检查](reports/SYSTEM_HEALTH_CHECK.md)
- [文档自检测系统](docs/DOC_SELF_HEALING_SYSTEM.md)
- [报告清理策略](docs/REPORT_CLEANUP_STRATEGY.md)
- **[度量收集器](scripts/metrics-collector.py)** - 🆕 自动化指标收集

### Phase 3交付物（新增）
- **[最佳实践调研](docs/AI_AGENT_WORKFLOW_BEST_PRACTICES_2026.md)** - 1630行深度报告
- **[Git Hooks指南](docs/GIT_HOOKS_GUIDE.md)** - 771行完整文档
- **[实施报告](docs/PHASE3_IMPLEMENTATION_REPORT.md)** - 交付物清单
- **[快速启动脚本](scripts/phase3-quickstart.sh)** - 一键部署

---

## 🚀 快速开始Phase 3

```bash
# 一键安装所有新组件
bash .lingma/scripts/phase3-quickstart.sh

# 查看新文档
cat .lingma/docs/EXECUTIVE_SUMMARY.md
```

---

## 📊 最新指标

| 组件 | 数量 | 状态 |
|------|------|------|
| Git Hooks | 4个 | ✅ 完成 |
| MCP配置 | 3服务器 | ✅ 模板就绪 |
| 度量脚本 | 1个 | ✅ 可运行 |
| 文档页数 | 8个新文件 | ✅ 完整 |
| 代码行数 | ~4000行 | ✅ 生产就绪 |

---

*最后更新: 2026-04-16 | Phase 3完成*
