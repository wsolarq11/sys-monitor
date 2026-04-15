# 📚 远程构建状态监控系统 - 文档中心

欢迎使用远程构建状态监控系统！本文档中心提供了完整的使用指南、API 参考和架构说明。

---

## 🚀 快速开始

### 我是新手，想快速上手
👉 [快速参考卡片](./src/components/BuildStatus/QUICK_REFERENCE.md) - 5分钟上手指南

### 我想了解完整功能
👉 [完整使用指南](./docs/guides/BUILD_MONITOR_GUIDE.md) - 从入门到精通

### 我想看代码示例
👉 [使用示例](./docs/examples/BuildStatusExample.tsx) - 5个实际场景

---

## 📖 文档分类

### 📘 入门文档

| 文档 | 适合人群 | 阅读时间 |
|------|---------|---------|
| [快速参考](./src/components/BuildStatus/QUICK_REFERENCE.md) | 所有用户 | 5分钟 |
| [.env.example](./.env.example) | 配置环境 | 2分钟 |
| [组件 README](./src/components/BuildStatus/README.md) | 开发者 | 15分钟 |

### 📗 进阶文档

| 文档 | 适合人群 | 阅读时间 |
|------|---------|---------|
| [完整指南](./docs/guides/BUILD_MONITOR_GUIDE.md) | 开发者、架构师 | 30分钟 |
| [使用示例](./docs/examples/BuildStatusExample.tsx) | 开发者 | 10分钟 |
| [实现总结](./docs/guides/IMPLEMENTATION_SUMMARY.md) | 技术负责人 | 20分钟 |

### 📙 专业文档

| 文档 | 适合人群 | 阅读时间 |
|------|---------|---------|
| [架构详解](./docs/architecture/ARCHITECTURE.md) | 架构师、高级开发者 | 45分钟 |
| [项目完成报告](./docs/guides/PROJECT_COMPLETION_REPORT.md) | 项目经理、技术负责人 | 15分钟 |

---

## 📂 文档目录结构

```
docs/
├── 📄 DOCUMENTATION_INDEX.md          # 本文档（导航索引）
│
├── guides/                             # 使用指南
│   ├── BUILD_MONITOR_GUIDE.md         # 完整使用指南
│   ├── IMPLEMENTATION_SUMMARY.md      # 实现总结
│   └── PROJECT_COMPLETION_REPORT.md   # 项目完成报告
│
├── architecture/                       # 架构文档
│   └── ARCHITECTURE.md                # 系统架构详解
│
├── api/                                # API 文档（预留）
│   └── (未来添加 API 参考文档)
│
└── examples/                           # 代码示例
    └── BuildStatusExample.tsx         # 使用示例代码
```

---

## 🔍 按主题查找

### 🏗️ 系统架构
- [架构详解 - 系统总览](./docs/architecture/ARCHITECTURE.md#系统架构总览)
- [架构详解 - 组件层次](./docs/architecture/ARCHITECTURE.md#组件层次结构)
- [架构详解 - 数据流](./docs/architecture/ARCHITECTURE.md#数据流图)

### 💻 代码实现
- [核心服务层](./src/services/githubBuildMonitor.ts)
- [UI 组件](./src/components/BuildStatus/BuildStatusCard.tsx)
- [单元测试](./src/services/githubBuildMonitor.test.ts)

### 📊 API 使用
- [GitHub API 端点](./docs/guides/BUILD_MONITOR_GUIDE.md#github-api-端点)
- [API 速率限制](./docs/guides/BUILD_MONITOR_GUIDE.md#api-速率限制)
- [认证流程](./docs/architecture/ARCHITECTURE.md#认证流程图)

### ⚙️ 配置说明
- [环境变量配置](./.env.example)
- [组件属性](./src/components/BuildStatus/README.md#配置选项)
- [刷新频率设置](./src/components/BuildStatus/QUICK_REFERENCE.md#常用配置)

### 🐛 问题排查
- [常见问题](./docs/guides/BUILD_MONITOR_GUIDE.md#故障排查)
- [403 错误解决](./docs/guides/BUILD_MONITOR_GUIDE.md#问题-1-403-forbidden---api-rate-limit-exceeded)
- [401 错误解决](./docs/guides/BUILD_MONITOR_GUIDE.md#问题-2-401-unauthorized)

### 🎨 UI 定制
- [自定义样式](./docs/examples/BuildStatusExample.tsx#示例-5-自定义样式)
- [状态颜色映射](./docs/guides/BUILD_MONITOR_GUIDE.md#状态可视化)
- [响应式设计](./docs/architecture/ARCHITECTURE.md#ui-状态机)

### 🧪 测试相关
- [运行测试](./docs/guides/IMPLEMENTATION_SUMMARY.md#测试覆盖)
- [测试用例](./src/services/githubBuildMonitor.test.ts)
- [Mock 策略](./docs/architecture/ARCHITECTURE.md#依赖关系图)

### 🔒 安全实践
- [Token 管理](./docs/guides/BUILD_MONITOR_GUIDE.md#安全管理-token)
- [环境变量](./docs/guides/BUILD_MONITOR_GUIDE.md#配置环境变量)
- [API 认证](./docs/architecture/ARCHITECTURE.md#认证流程图)

### 📈 性能优化
- [优化策略](./docs/architecture/ARCHITECTURE.md#性能优化策略)
- [性能指标](./docs/guides/PROJECT_COMPLETION_REPORT.md#性能指标)
- [最佳实践](./docs/guides/BUILD_MONITOR_GUIDE.md#最佳实践)

---

## 🎯 按角色查找

### 👨‍💻 前端开发者
**推荐阅读顺序：**
1. [快速参考](./src/components/BuildStatus/QUICK_REFERENCE.md) - 了解基本用法
2. [组件 README](./src/components/BuildStatus/README.md) - 学习组件 API
3. [使用示例](./docs/examples/BuildStatusExample.tsx) - 查看实际代码
4. [完整指南](./docs/guides/BUILD_MONITOR_GUIDE.md) - 深入理解

### 🏗️ 系统架构师
**推荐阅读顺序：**
1. [架构详解](./docs/architecture/ARCHITECTURE.md) - 理解系统设计
2. [实现总结](./docs/guides/IMPLEMENTATION_SUMMARY.md) - 了解技术选型
3. [核心服务层](./src/services/githubBuildMonitor.ts) - 审查代码质量

### 👔 技术负责人/项目经理
**推荐阅读顺序：**
1. [项目完成报告](./docs/guides/PROJECT_COMPLETION_REPORT.md) - 全面了解项目
2. [实现总结](./docs/guides/IMPLEMENTATION_SUMMARY.md) - 评估技术方案
3. [完整指南](./docs/guides/BUILD_MONITOR_GUIDE.md) - 了解功能特性

### 🎓 学习者
**推荐阅读顺序：**
1. [快速参考](./src/components/BuildStatus/QUICK_REFERENCE.md) - 快速体验
2. [使用示例](./docs/examples/BuildStatusExample.tsx) - 动手实践
3. [完整指南](./docs/guides/BUILD_MONITOR_GUIDE.md) - 系统学习
4. [架构详解](./docs/architecture/ARCHITECTURE.md) - 深入理解

---

## 🔗 外部资源

### GitHub 官方文档
- [GitHub Actions API](https://docs.github.com/en/rest/actions)
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [API 速率限制](https://docs.github.com/en/rest/overview/rate-limits)

### 技术文档
- [React 官方文档](https://react.dev/)
- [TypeScript 手册](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Vitest 测试框架](https://vitest.dev/)

---

## 💡 使用技巧

### 搜索文档
使用浏览器的搜索功能 (Ctrl+F / Cmd+F) 快速定位关键词：
- "token" - 查找 Token 相关配置
- "error" - 查找错误处理
- "example" - 查找代码示例
- "performance" - 查找性能优化

### 打印文档
需要离线阅读？使用浏览器的打印功能 (Ctrl+P / Cmd+P) 保存为 PDF。

### 加入书签
将常用文档加入书签，方便快速访问。

---

## ❓ 常见问题

### Q: 我应该从哪个文档开始阅读？
**A:** 如果您是新手，从 [快速参考](./src/components/BuildStatus/QUICK_REFERENCE.md) 开始；如果您想了解全面信息，阅读 [完整指南](./docs/guides/BUILD_MONITOR_GUIDE.md)。

### Q: 如何快速找到某个功能的说明？
**A:** 使用上面的"按主题查找"部分，或使用浏览器搜索功能。

### Q: 文档之间有重复内容吗？
**A:** 是的，为了便于查阅，某些重要概念会在多个文档中出现。每个文档侧重点不同：
- 快速参考：简洁明了
- 完整指南：详细全面
- 架构详解：深度解析

### Q: 发现文档错误或遗漏怎么办？
**A:** 欢迎提出改进建议！可以创建 Issue 或直接提交 Pull Request。

---

## 📊 文档统计

```
文档总数:        8 个
总行数:          ~3,500 行
总字数:          ~50,000 字
图表数量:        15+ 个
代码示例:        20+ 个
```

---

## 🎯 下一步行动

根据您的角色，选择下一步：

### 立即开始使用
1. ✅ 阅读 [快速参考](./src/components/BuildStatus/QUICK_REFERENCE.md)
2. ✅ 复制 `.env.example` 为 `.env`
3. ✅ 获取 GitHub Token
4. ✅ 在应用中集成组件

### 深入学习
1. ✅ 阅读 [完整指南](./docs/guides/BUILD_MONITOR_GUIDE.md)
2. ✅ 研究 [架构详解](./docs/architecture/ARCHITECTURE.md)
3. ✅ 查看 [源代码](./src/services/githubBuildMonitor.ts)
4. ✅ 运行 [单元测试](./src/services/githubBuildMonitor.test.ts)

### 贡献改进
1. ✅ 阅读 [实现总结](./docs/guides/IMPLEMENTATION_SUMMARY.md)
2. ✅ 了解 [未来规划](./docs/guides/PROJECT_COMPLETION_REPORT.md#未来扩展方向)
3. ✅ 提出改进建议
4. ✅ 提交 Pull Request

---

## 🌟 文档特色

- ✅ **渐进式**: 从入门到精通
- ✅ **实例驱动**: 每个概念都有代码示例
- ✅ **图文并茂**: 包含流程图、架构图、时序图
- ✅ **问题导向**: 针对实际问题提供解决方案
- ✅ **易于检索**: 清晰的分类和索引
- ✅ **持续更新**: 随项目发展不断完善

---

## 📞 获取帮助

如果文档无法解决您的问题：

1. 🔍 检查 [故障排查章节](./docs/guides/BUILD_MONITOR_GUIDE.md#故障排查)
2. 💬 查看 [GitHub Issues](https://github.com/your-repo/issues)
3. 📧 联系维护团队
4. 🤝 加入社区讨论

---

**祝您使用愉快！** 🎉

*最后更新: 2026-04-15*
