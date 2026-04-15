# Spec 性能优化指南

## 问题描述

随着项目进展，`current-spec.md` 文件会变得非常大（可能超过 1000 lines），导致：
- 每次会话启动时读取时间长
- Agent 解析 Spec 变慢
- 响应延迟增加

## 优化策略

### 策略 1: 增量读取

**原理**: 只读取未完成的任务部分，跳过已完成的任务。

**实现**:

```markdown
# Spec 读取优化流程

1. **快速扫描**
   - 读取 Spec 前 100 行（元数据和任务列表）
   - 提取未完成的任务 ID 列表

2. **精准定位**
   - 使用 grep 搜索未完成任务的标记
   - 示例: `grep -n "^\- \[ \] Task-" current-spec.md`

3. **按需加载**
   - 只读取未完成任务的详细内容
   - 跳过已完成任务的详细描述

4. **缓存结果**
   - 缓存解析后的任务列表
   - 下次会话直接使用缓存
```

**代码示例**:

```python
# 伪代码 - Spec 增量读取

def load_spec_efficient(spec_path: str) -> dict:
    """高效加载 Spec"""
    
    # 1. 读取元数据（前 100 行）
    with open(spec_path, 'r') as f:
        lines = f.readlines()[:100]
    
    metadata = parse_metadata(lines)
    
    # 2. 查找未完成任务
    incomplete_tasks = []
    for i, line in enumerate(lines):
        if line.startswith('- [ ] Task-'):
            task_id = extract_task_id(line)
            incomplete_tasks.append(task_id)
    
    # 3. 按需加载未完成任务详情
    task_details = {}
    for task_id in incomplete_tasks:
        detail = find_task_detail(spec_path, task_id)
        task_details[task_id] = detail
    
    return {
        'metadata': metadata,
        'incomplete_tasks': incomplete_tasks,
        'task_details': task_details
    }
```

---

### 策略 2: 归档旧任务

**原理**: 将已完成的任务移动到历史文件，保持 current-spec.md 精简。

**实现**:

```markdown
# Spec 归档流程

1. **检测已完成任务**
   - 扫描 current-spec.md
   - 找出所有标记为 `- [x]` 的任务

2. **移动到历史文件**
   - 创建归档文件: `.lingma/specs/spec-history/YYYY-MM-DD-completed-tasks.md`
   - 移动已完成任务的详细内容

3. **保留摘要**
   - 在 current-spec.md 中保留任务摘要
   - 示例:
     ```markdown
     ### 已完成任务（详见 spec-history）
     
     - [x] Task-001: 创建基础框架 ✅ (2024-01-10)
     - [x] Task-002: 实现 MCP 集成 ✅ (2024-01-12)
     - [x] Task-010: 上下文管理器 ✅ (2024-01-15)
     ```

4. **更新进度**
   - 重新计算完成百分比
   - 更新元数据
```

**归档文件结构**:

```
.lingma/specs/
├── current-spec.md          # 只包含未完成任务和摘要
├── spec-index.md            # 轻量级索引（可选）
└── spec-history/
    ├── 2024-01-10-task-001-005.md
    ├── 2024-01-12-task-006-009.md
    └── 2024-01-15-task-010.md
```

---

### 策略 3: 创建 Spec 索引

**原理**: 创建轻量级的 `spec-index.md`，只包含元数据和任务列表。

**实现**:

```markdown
# spec-index.md 结构

## 元数据
- **项目名称**: FolderSizeMonitor
- **当前 Spec**: current-spec.md
- **状态**: in-progress
- **进度**: 60.9% (31/50)
- **最后更新**: 2024-01-15

## 任务概览

### 已完成 (31/50)
- Task-001 ~ Task-005: Phase 1 基础框架 ✅
- Task-006, 009: Phase 2 MCP 集成 ✅
- Task-010: Phase 3 上下文管理器 ✅
- ...

### 进行中 (1/50)
- Task-011: 偏好学习 🔄

### 待执行 (18/50)
- Task-012: 学习效果评估 ⏳
- Task-013 ~ Task-015: Phase 4 优化和完善 ⏳
- ...

## 最近实施笔记
- 2024-01-15: Task-010 完成（改用 Lingma Memory）
- 2024-01-15: Task-009 完成（MCP 集成测试）
```

**使用方式**:

```markdown
# 会话启动时

1. 先读取 spec-index.md（快速，~100 lines）
2. 获取当前状态和待办任务
3. 如果需要详细信息，再读取 current-spec.md 的相关部分
```

---

### 策略 4: 缓存机制

**原理**: 缓存 Spec 解析结果，避免重复解析。

**实现**:

```python
# 伪代码 - Spec 缓存

import json
import hashlib
from pathlib import Path

class SpecCache:
    def __init__(self, cache_dir: Path = Path(".lingma/cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cache_key(self, spec_path: str) -> str:
        """生成缓存键（基于文件内容和修改时间）"""
        path = Path(spec_path)
        content_hash = hashlib.md5(path.read_text().encode()).hexdigest()
        mtime = path.stat().st_mtime
        return f"{content_hash}_{mtime}"
    
    def get_cached_spec(self, spec_path: str) -> dict:
        """从缓存获取 Spec"""
        cache_key = self.get_cache_key(spec_path)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        return None
    
    def cache_spec(self, spec_path: str, parsed_data: dict):
        """缓存 Spec 解析结果"""
        cache_key = self.get_cache_key(spec_path)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        with open(cache_file, 'w') as f:
            json.dump(parsed_data, f)
        
        # 清理旧缓存（保留最近 10 个）
        self.cleanup_old_cache()
    
    def cleanup_old_cache(self, keep: int = 10):
        """清理旧缓存"""
        cache_files = sorted(
            self.cache_dir.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        for old_file in cache_files[keep:]:
            old_file.unlink()
```

**使用流程**:

```markdown
Spec 读取流程（带缓存）:

1. 检查缓存
   IF 缓存存在 AND 未过期:
      → 使用缓存数据
   ELSE:
      → 重新解析 Spec
      → 更新缓存

2. 缓存有效期
   - 默认: 1 小时
   - 如果 Spec 文件被修改，立即失效
   - 手动清除: "请清除 Spec 缓存"
```

---

## 性能对比

### 优化前

| 操作 | 耗时 |
|------|------|
| 读取完整 Spec (1000 lines) | ~500ms |
| 解析 Spec | ~200ms |
| 总计 | ~700ms |

### 优化后

| 操作 | 耗时 | 优化幅度 |
|------|------|----------|
| 读取 spec-index (100 lines) | ~50ms | -90% |
| 增量读取未完成任务 | ~100ms | -80% |
| 使用缓存 | ~10ms | -98% |
| 总计（缓存命中） | ~10ms | **-98%** |
| 总计（缓存未命中） | ~150ms | **-78%** |

---

## 实施建议

### 短期（立即实施）

1. **创建 spec-index.md**
   - 手动创建初始版本
   - 后续由 Agent 自动维护

2. **实现缓存机制**
   - 添加简单的文件缓存
   - 设置 1 小时过期时间

### 中期（1-2 周）

3. **实现增量读取**
   - 修改 Agent 的 Spec 加载逻辑
   - 只读取未完成任务

4. **自动化归档**
   - 当任务完成后，自动移动到 spec-history
   - 在 current-spec.md 中保留摘要

### 长期（1 个月+）

5. **智能预加载**
   - 根据用户行为预测下一个任务
   - 提前加载相关 Spec 内容

6. **分布式缓存**
   - 跨会话共享缓存
   - 团队级别的 Spec 缓存

---

## 注意事项

### 1. 缓存一致性

**问题**: 缓存可能与实际文件不同步

**解决**:
- 每次读取前检查文件修改时间
- 如果文件被修改，立即清除缓存
- 提供手动清除缓存的命令

---

### 2. 归档完整性

**问题**: 归档后丢失重要信息

**解决**:
- 归档时保留完整的任务详情
- 在 current-spec.md 中保留足够的摘要
- 提供快速查看历史任务的命令

---

### 3. 向后兼容

**问题**: 旧工具可能依赖完整的 current-spec.md

**解决**:
- 保持 current-spec.md 格式不变
- 新增的文件作为补充，不替代原有文件
- 提供降级方案（如果优化失败，回退到完整读取）

---

## 监控指标

### 性能指标

- **Spec 加载时间**: 目标 < 100ms
- **缓存命中率**: 目标 > 80%
- **内存占用**: 目标 < 10MB

### 质量指标

- **归档完整性**: 100% 的任务都有归档
- **缓存一致性**: 0 次不一致事件
- **用户满意度**: > 90%

---

## 总结

通过以下四个策略的组合使用，可以显著提升 Spec 读取性能：

1. ✅ **增量读取**: 只加载需要的部分
2. ✅ **归档旧任务**: 保持 current-spec.md 精简
3. ✅ **创建索引**: 快速获取元数据
4. ✅ **缓存机制**: 避免重复解析

**预期效果**: 性能提升 78-98%，用户体验显著改善。
