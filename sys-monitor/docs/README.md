# 📚 文档中心

本文档目录包含了远程构建状态监控系统的完整文档。

---

## 📂 目录结构

```
docs/
├── DOCUMENTATION_INDEX.md          # 🗂️ 文档导航索引（从这里开始）
│
├── guides/                         # 📘 使用指南
│   ├── BUILD_MONITOR_GUIDE.md     # 完整使用指南
│   ├── IMPLEMENTATION_SUMMARY.md  # 实现总结
│   └── PROJECT_COMPLETION_REPORT.md # 项目完成报告
│
├── architecture/                   # 🏗️ 架构文档
│   └── ARCHITECTURE.md            # 系统架构详解
│
├── api/                            # 🔌 API 文档
│   └── (预留，未来添加)
│
└── examples/                       # 💻 代码示例
    └── BuildStatusExample.tsx     # 5个使用场景示例
```

---

## 🚀 快速导航

### 我是新手
👉 [快速参考](../src/components/BuildStatus/QUICK_REFERENCE.md) - 5分钟上手

### 我想全面了解
👉 [文档索引](./DOCUMENTATION_INDEX.md) - 所有文档的导航中心

### 我想看架构设计
👉 [架构详解](./architecture/ARCHITECTURE.md) - 系统设计原理

### 我想看代码示例
👉 [使用示例](./examples/BuildStatusExample.tsx) - 实际场景代码

---

## 📖 文档分类说明

### guides/ - 使用指南
面向开发者和用户的实用文档，包含：
- 安装和配置指南
- API 使用说明
- 最佳实践
- 故障排查

### architecture/ - 架构文档
面向架构师和高级开发者的技术文档，包含：
- 系统架构图
- 数据流设计
- 技术选型说明
- 设计决策记录

### api/ - API 文档
API 参考文档（预留），将包含：
- API 端点说明
- 请求/响应格式
- 认证方式
- 错误码说明

### examples/ - 代码示例
可运行的代码示例，展示：
- 基本用法
- 高级功能
- 集成场景
- 自定义配置

---

## 🎯 推荐阅读路径

### 路径 1: 快速上手（15分钟）
1. [快速参考](../src/components/BuildStatus/QUICK_REFERENCE.md) - 5分钟
2. [组件文档](../src/components/BuildStatus/README.md) - 10分钟

### 路径 2: 深入学习（1小时）
1. [快速参考](../src/components/BuildStatus/QUICK_REFERENCE.md) - 5分钟
2. [完整指南](./guides/BUILD_MONITOR_GUIDE.md) - 30分钟
3. [使用示例](./examples/BuildStatusExample.tsx) - 10分钟
4. [实现总结](./guides/IMPLEMENTATION_SUMMARY.md) - 15分钟

### 路径 3: 掌握架构（2小时）
1. [完整指南](./guides/BUILD_MONITOR_GUIDE.md) - 30分钟
2. [架构详解](./architecture/ARCHITECTURE.md) - 45分钟
3. [源代码阅读](../src/services/githubBuildMonitor.ts) - 30分钟
4. [项目报告](./guides/PROJECT_COMPLETION_REPORT.md) - 15分钟

---

## 📊 文档统计

| 类别 | 文件数 | 总行数 | 说明 |
|------|--------|--------|------|
| 使用指南 | 3 | ~1,285 | 完整的用户和开发者指南 |
| 架构文档 | 1 | ~571 | 系统设计和架构说明 |
| 代码示例 | 1 | ~190 | 实际使用场景示例 |
| 导航索引 | 1 | ~270 | 文档导航和检索 |
| **总计** | **6** | **~2,316** | **完整的文档体系** |

---

## 🔍 如何查找文档

### 方法 1: 使用文档索引
打开 [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md)，按主题或角色查找。

### 方法 2: 浏览器搜索
在文档目录中使用浏览器的搜索功能 (Ctrl+F / Cmd+F)。

### 方法 3: 按文件类型
- 想看教程 → `guides/` 目录
- 想了解设计 → `architecture/` 目录
- 想看代码 → `examples/` 目录

---

## 💡 文档使用技巧

### 离线阅读
使用浏览器的打印功能 (Ctrl+P / Cmd+P) 将文档保存为 PDF。

### 快速定位
使用 Markdown 大纲视图（VS Code、Typora 等编辑器支持）。

### 加入书签
将常用文档加入书签，方便快速访问。

---

## 🤝 贡献文档

欢迎改进文档！您可以：

1. **修正错误** - 发现拼写错误或过时信息
2. **补充内容** - 添加缺失的说明或示例
3. **改进结构** - 优化文档组织和导航
4. **翻译文档** - 翻译成其他语言

### 文档规范

- 使用清晰的标题层级
- 包含代码示例
- 添加相关的链接
- 保持语言简洁明了
- 使用图表辅助说明

---

## 📞 需要帮助？

如果文档无法解决您的问题：

1. 检查 [故障排查章节](./guides/BUILD_MONITOR_GUIDE.md#故障排查)
2. 查看 [GitHub Issues](https://github.com/your-repo/issues)
3. 联系维护团队

---

**📖 从 [文档索引](./DOCUMENTATION_INDEX.md) 开始探索！**

*最后更新: 2026-04-15*
