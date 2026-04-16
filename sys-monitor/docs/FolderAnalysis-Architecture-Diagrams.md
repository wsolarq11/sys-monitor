# FolderAnalysis 模块 - 架构总览图

## 📊 组件层级关系

```mermaid
graph TB
    subgraph "FolderAnalysis Module"
        A[FolderAnalysisContainer] --> B[WatchedFoldersList]
        A --> C[FolderAnalysisView]
        
        B --> D[Zustand Store<br/>watchedFoldersStore]
        
        C --> E[Utils: format.ts]
        C --> F[Utils: time.ts]
        
        A --> G[Utils: validation.ts]
        
        D --> H[Tauri Backend<br/>Rust Commands]
        A --> H
        B --> H
    end
    
    style A fill:#4F46E5,color:#fff
    style B fill:#10B981,color:#fff
    style C fill:#F59E0B,color:#fff
    style D fill:#EC4899,color:#fff
    style H fill:#6B7280,color:#fff
```

## 🔄 数据流向图

```mermaid
sequenceDiagram
    participant U as User
    participant C as Container
    participant V as View
    participant S as Store
    participant T as Tauri Backend
    
    Note over U,T: 扫描流程
    U->>C: 点击"扫描文件夹"
    C->>C: 验证路径
    C->>T: invoke('scan_folder')
    T-->>C: 返回 ScanResultData
    C->>C: 更新 scanResult
    C->>T: invoke('get_folder_scans')
    T-->>C: 返回历史记录
    C->>V: 传递 props
    V->>U: 渲染结果
    
    Note over U,T: 添加监控文件夹
    U->>B: 点击"添加监控文件夹"
    B->>T: invoke('select_folder')
    T-->>B: 返回路径
    B->>S: addFolder(path)
    S->>T: invoke('add_watched_folder')
    T-->>S: 成功
    S->>S: fetchFolders()
    S->>T: invoke('list_watched_folders')
    T-->>S: 返回列表
    S->>B: 更新 folders
    B->>U: Toast 通知
```

## 🗂️ 状态管理架构

```mermaid
graph LR
    subgraph "Local State (useState)"
        A[selectedPath]
        B[scans]
        C[isScanning]
        D[scanResult]
        E[dbPath]
        F[error]
        G[scanProgress]
    end
    
    subgraph "Global State (Zustand)"
        H[folders]
        I[loading]
        J[error]
        K[fetchFolders]
        L[addFolder]
        M[removeFolder]
        N[toggleActive]
    end
    
    A -.-> O[FolderAnalysisContainer]
    B -.-> O
    C -.-> O
    D -.-> O
    E -.-> O
    F -.-> O
    G -.-> O
    
    H -.-> P[WatchedFoldersList]
    I -.-> P
    J -.-> P
    K -.-> P
    L -.-> P
    M -.-> P
    N -.-> P
    
    style O fill:#4F46E5,color:#fff
    style P fill:#10B981,color:#fff
```

## 🔌 API 调用关系

```mermaid
graph TB
    subgraph "Frontend Components"
        A[FolderAnalysisContainer]
        B[WatchedFoldersList]
        C[watchedFoldersStore]
    end
    
    subgraph "Tauri Commands"
        D[get_db_path]
        E[select_folder]
        F[scan_folder]
        G[get_folder_scans]
        H[list_watched_folders]
        I[add_watched_folder]
        J[remove_watched_folder]
        K[toggle_watched_folder_active]
    end
    
    A --> D
    A --> E
    A --> F
    A --> G
    
    B --> E
    B --> C
    
    C --> D
    C --> H
    C --> I
    C --> J
    C --> K
    
    style A fill:#4F46E5,color:#fff
    style B fill:#10B981,color:#fff
    style C fill:#EC4899,color:#fff
```

## 🎯 组件职责矩阵

| 组件 | 状态管理 | UI 渲染 | 业务逻辑 | Tauri 调用 | Store 集成 |
|------|---------|---------|---------|-----------|-----------|
| **FolderAnalysisContainer** | ✅ | ❌ | ✅ | ✅ | ❌ |
| **FolderAnalysisView** | ❌ | ✅ | ❌ | ❌ | ❌ |
| **WatchedFoldersList** | ⚠️ 部分 | ✅ | ✅ | ✅ | ✅ |
| **watchedFoldersStore** | ✅ | ❌ | ✅ | ✅ | N/A |

✅ = 主要职责  ⚠️ = 部分涉及  ❌ = 不涉及

## 📈 性能优化建议

```mermaid
graph TD
    A[性能瓶颈识别] --> B{优化策略}
    
    B --> C[组件重渲染]
    B --> D[网络请求]
    B --> E[状态更新]
    
    C --> C1[React.memo]
    C --> C2[useMemo]
    C --> C3[useCallback]
    
    D --> D1[请求缓存]
    D --> D2[防抖/节流]
    D --> D3[并发请求]
    
    E --> E1[细粒度订阅]
    E --> E2[批量更新]
    E --> E3[乐观更新]
    
    style A fill:#EF4444,color:#fff
    style B fill:#F59E0B,color:#fff
    style C1 fill:#10B981,color:#fff
    style D1 fill:#10B981,color:#fff
    style E1 fill:#10B981,color:#fff
```

## 🔐 错误处理流程

```mermaid
flowchart TD
    A[用户操作] --> B{执行异步操作}
    
    B -->|成功| C[更新状态]
    B -->|失败| D{错误类型}
    
    D -->|用户取消| E[静默处理]
    D -->|网络错误| F[显示 Toast]
    D -->|验证失败| G[显示内联错误]
    D -->|未知错误| H[记录日志 + Toast]
    
    C --> I[正常渲染]
    E --> I
    F --> J[用户关闭通知]
    G --> K[用户修正输入]
    H --> J
    
    style A fill:#4F46E5,color:#fff
    style C fill:#10B981,color:#fff
    style D fill:#F59E0B,color:#fff
    style F fill:#EF4444,color:#fff
    style G fill:#EF4444,color:#fff
```

## 📝 技术债务优先级

```mermaid
quadrantChart
    title "技术债务优先级矩阵"
    x-axis "低影响" --> "高影响"
    y-axis "易修复" --> "难修复"
    
    "乐观更新缺少回滚": [0.85, 0.3]
    "错误处理不一致": [0.7, 0.4]
    "硬编码限制值": [0.4, 0.8]
    "类型安全性不足": [0.6, 0.7]
    "过多 Console 日志": [0.3, 0.9]
    "缺少加载动画": [0.5, 0.8]
    "魔法字符串": [0.2, 0.9]
    "重复获取 dbPath": [0.5, 0.6]
    "缺少路径历史": [0.4, 0.7]
    "组件耦合度高": [0.6, 0.5]
```

---

**图表说明**:
- 使用 Mermaid 语法绘制，可在支持 Mermaid 的 Markdown 编辑器中查看
- 推荐工具: GitHub、GitLab、VS Code (Mermaid 插件)、Notion
