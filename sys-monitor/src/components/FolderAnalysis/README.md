# FolderAnalysis 模块

> 文件夹大小分析与监控功能模块

## 📁 文件结构

```
FolderAnalysis/
├── FolderAnalysisContainer.tsx    # Container 组件（状态管理 + 业务逻辑）
├── FolderAnalysisView.tsx         # Presentational 组件（纯 UI）
└── WatchedFoldersList.tsx         # 监控文件夹列表组件
```

## 🚀 快速开始

### 基本使用

```tsx
import { FolderAnalysisContainer } from './components/FolderAnalysis';

function App() {
  return <FolderAnalysisContainer />;
}
```

### 核心功能

1. **单次扫描** - 选择文件夹并执行深度扫描
2. **历史记录** - 查看和管理扫描历史
3. **持续监控** - 添加文件夹到监控列表

## 📚 详细文档

- [📘 快速入门指南](../../docs/FolderAnalysis-Quick-Start.md) - 5分钟上手
- [🏗️ 架构设计文档](../../docs/FolderAnalysis-Module-Architecture.md) - 深入理解
- [📖 API 参考手册](../../docs/FolderAnalysis-API-Reference.md) - 完整 API
- [📊 架构图解](../../docs/FolderAnalysis-Architecture-Diagrams.md) - 可视化图表
- [📑 文档索引](../../docs/FOLDER_ANALYSIS_DOCS_INDEX.md) - 导航入口

## 🎯 设计模式

采用 **Container-Presenter** 模式：

- **Container** (`FolderAnalysisContainer`): 管理状态、调用 API、处理业务逻辑
- **Presenter** (`FolderAnalysisView`): 纯 UI 组件，接收 props 并渲染

## 🔧 技术栈

- React 18 + TypeScript
- Zustand (状态管理)
- Tauri 2.x (桌面集成)
- TailwindCSS (样式)
- Sonner (通知系统)

## 📊 组件关系

```
FolderAnalysisContainer
├── WatchedFoldersList (监控列表)
└── FolderAnalysisView (扫描界面)
```

## ⚡ 关键概念

### 状态管理

- **本地状态** (`useState`): 扫描相关的临时状态
- **全局状态** (`Zustand`): 监控文件夹列表（跨组件共享）

### 数据流

```
用户操作 → Container → Tauri Backend → 更新状态 → Presenter 渲染
```

## 🐛 常见问题

**Q: 扫描按钮无响应？**  
A: 检查路径是否有效，查看控制台错误信息。

**Q: 监控列表为空？**  
A: 确认 `fetchFolders()` 在组件挂载时被调用。

更多问题请查看 [快速入门指南 - 排错部分](../../docs/FolderAnalysis-Quick-Start.md#-快速排错指南)

## 🤝 贡献

修改组件前请阅读：
1. [架构设计文档](../../docs/FolderAnalysis-Module-Architecture.md)
2. [技术债务清单](../../docs/FolderAnalysis-Module-Architecture.md#技术债务与问题)

## 📄 许可证

项目内部文档，仅供团队使用。

---

**维护者**: Development Team  
**最后更新**: 2026-04-16
