# Spec-Driven Development 开发者文档

**版本**: 1.0.0  
**最后更新**: 2026-04-17

## 目录

1. [架构概览](#架构概览)
2. [核心组件](#核心组件)
3. [开发指南](#开发指南)
4. [API 参考](#api-参考)
5. [测试指南](#测试指南)
6. [部署指南](#部署指南)
7. [扩展开发](#扩展开发)

---

## 架构概览

### 系统架构图

```
┌─────────────────────────────────────┐
│       User Interface Layer          │
│  (CLI / Chat / Dashboard)           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│    Intelligent Decision Engine      │
│  - Risk Assessment                  │
│  - Confidence Scoring               │
│  - Strategy Selection               │
│  - Decision Caching                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Automation Execution Layer      │
│  - Operation Queue                  │
│  - Snapshot Management              │
│  - Rollback System                  │
│  - Progress Tracking                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│        MCP Tool Layer               │
│  - Filesystem MCP                   │
│  - Git MCP                          │
│  - Shell MCP                        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Learning & Optimization        │
│  - Pattern Recognition              │
│  - Preference Learning              │
│  - Performance Tuning               │
└─────────────────────────────────────┘
```

### 目录结构

```
.lingma/
├── agents/                    # Agent 定义
│   ├── spec-driven-core-agent.md
│   └── README.md
├── config/                    # 配置文件
│   ├── automation.json
│   ├── agent-config.json
│   └── mcp-servers.json
├── docs/                      # 文档
│   ├── guides/               # 用户指南
│   ├── architecture/         # 架构文档
│   └── reports/              # 报告
├── hooks/                     # Git Hooks
├── logs/                      # 日志文件
├── reports/                   # 生成的报告
├── rules/                     # Rules 定义
│   ├── automation-policy.md
│   ├── memory-usage.md
│   └── spec-session-start.md
├── scripts/                   # Python 脚本
│   ├── automation-engine.py
│   ├── decision_cache.py
│   ├── batch_logger.py
│   ├── ux_improvements.py
│   ├── interactive_cli.py
│   ├── performance-optimizer.py
│   └── ...
├── skills/                    # Skills 定义
│   ├── spec-driven-development/
│   └── memory-management/
├── specs/                     # Spec 文件
│   ├── current-spec.md
│   └── constitution.md
└── worker/                    # Worker 进程
```

---

## 核心组件

### 1. 会话中间件 (Session Middleware)

**文件**: `.lingma/scripts/session-middleware.py`

**职责**:
- 验证 Spec 文件存在性
- 检查目录结构完整性
- 验证关键文件存在性
- 检测文档冗余
- 生成验证报告

**使用示例**:
```python
from session_middleware import SessionMiddleware

middleware = SessionMiddleware()
result = middleware.validate()

if result['status'] == 'PASSED':
    print("✅ 验证通过")
else:
    print(f"❌ 验证失败: {result['errors']}")
```

### 2. 决策缓存 (Decision Cache)

**文件**: `.lingma/scripts/decision_cache.py`

**职责**:
- 缓存决策结果
- LRU 淘汰策略
- TTL 过期机制
- 磁盘持久化

**API**:
```python
from decision_cache import get_decision_cache, cache_decision, get_cached_decision

# 获取缓存实例
cache = get_decision_cache()

# 缓存决策
operation = {"type": "file_read", "path": "/test.txt"}
result = {"strategy": "auto_execute", "risk": "low"}
cache_decision(operation, result)

# 获取缓存的决策
cached = get_cached_decision(operation)
if cached:
    print(f"缓存命中: {cached}")
```

### 3. 批量日志写入器 (Batch Logger)

**文件**: `.lingma/scripts/batch_logger.py`

**职责**:
- 批量收集日志
- 异步写入磁盘
- 减少 I/O 次数
- 线程安全

**API**:
```python
from batch_logger import get_batch_logger, log_entry, flush_logs

# 获取日志实例
logger = get_batch_logger()

# 记录日志
log_entry({
    'level': 'INFO',
    'message': 'Operation completed',
    'operation': 'file_read'
})

# 立即刷新
flush_logs()
```

### 4. 用户体验改进 (UX Improvements)

**文件**: `.lingma/scripts/ux_improvements.py`

**职责**:
- 进度显示
- 消息格式化
- 撤销/重做管理

**API**:
```python
from ux_improvements import (
    create_progress,
    get_message_formatter,
    get_undo_manager
)

# 进度显示
with create_progress(100, "Processing") as progress:
    for i in range(100):
        progress.update()

# 消息格式化
formatter = get_message_formatter()
print(formatter.success("Operation successful"))

# 撤销管理
undo_mgr = get_undo_manager()
undo_mgr.record_action("modify", data, undo_func, redo_func)
undo_mgr.undo()
```

### 5. 性能优化器 (Performance Optimizer)

**文件**: `.lingma/scripts/performance-optimizer.py`

**职责**:
- 性能基准测试
- 决策引擎优化
- 内存使用优化
- 日志写入优化

**使用示例**:
```bash
python .lingma/scripts/performance-optimizer.py
```

---

## 开发指南

### 环境设置

1. **安装依赖**
   ```bash
   pip install psutil
   ```

2. **配置 Git Hooks**
   ```bash
   python .lingma/scripts/install-hooks.py
   ```

3. **验证安装**
   ```bash
   python .lingma/scripts/verify-setup.py
   ```

### 代码规范

#### Python 代码风格

- 遵循 PEP 8
- 使用类型注解
- 编写文档字符串
- 保持函数简洁（< 50 行）

**示例**:
```python
def calculate_risk(operation: Dict[str, Any]) -> float:
    """
    计算操作风险分数
    
    Args:
        operation: 操作详情
        
    Returns:
        风险分数 (0.0 - 1.0)
    """
    # 实现逻辑
    pass
```

#### 文件组织

- 每个模块一个文件
- 相关文件放在同一目录
- 使用清晰的命名

### 添加新功能

1. **创建模块**
   ```python
   # .lingma/scripts/my_feature.py
   
   class MyFeature:
       def __init__(self):
           pass
       
       def execute(self):
           pass
   ```

2. **编写测试**
   ```python
   # .lingma/scripts/test_my_feature.py
   
   def test_my_feature():
       feature = MyFeature()
       result = feature.execute()
       assert result is not None
   ```

3. **更新文档**
   - 添加到用户指南
   - 添加到开发者文档
   - 更新 API 参考

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: add my feature"
   git push
   ```

---

## API 参考

### SessionMiddleware

```python
class SessionMiddleware:
    def validate(self) -> Dict[str, Any]:
        """验证会话环境"""
        pass
    
    def generate_report(self) -> str:
        """生成验证报告"""
        pass
```

### DecisionCache

```python
class DecisionCache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """初始化缓存"""
        pass
    
    def get(self, operation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """获取缓存的决策"""
        pass
    
    def set(self, operation: Dict[str, Any], result: Dict[str, Any]):
        """设置决策缓存"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        pass
```

### BatchLogger

```python
class BatchLogger:
    def __init__(self, log_file: str, batch_size: int = 10, 
                 flush_interval: float = 5.0):
        """初始化日志写入器"""
        pass
    
    def log(self, entry: Dict[str, Any]):
        """记录日志条目"""
        pass
    
    def flush(self):
        """立即刷新日志"""
        pass
    
    def stop(self):
        """停止日志写入器"""
        pass
```

### ProgressDisplay

```python
class ProgressDisplay:
    def __init__(self, total: int = 100, description: str = "处理中"):
        """初始化进度显示"""
        pass
    
    def update(self, current: Optional[int] = None, increment: int = 1):
        """更新进度"""
        pass
    
    def complete(self, message: str = "完成"):
        """完成任务"""
        pass
```

### UndoManager

```python
class UndoManager:
    def __init__(self, max_history: int = 50):
        """初始化撤销管理器"""
        pass
    
    def record_action(self, action_type: str, details: Dict[str, Any],
                     undo_func=None, redo_func=None):
        """记录操作"""
        pass
    
    def undo(self) -> Optional[Dict[str, Any]]:
        """撤销最后一个操作"""
        pass
    
    def redo(self) -> Optional[Dict[str, Any]]:
        """重做最后一个撤销的操作"""
        pass
```

---

## 测试指南

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_decision_cache.py

# 运行测试并生成覆盖率报告
python -m pytest --cov=.lingma/scripts tests/
```

### 编写测试

```python
import unittest
from decision_cache import DecisionCache

class TestDecisionCache(unittest.TestCase):
    
    def setUp(self):
        self.cache = DecisionCache(max_size=100, ttl=60)
    
    def test_cache_miss(self):
        """测试缓存未命中"""
        operation = {"type": "test"}
        result = self.cache.get(operation)
        self.assertIsNone(result)
    
    def test_cache_hit(self):
        """测试缓存命中"""
        operation = {"type": "test"}
        expected = {"strategy": "auto"}
        
        self.cache.set(operation, expected)
        result = self.cache.get(operation)
        
        self.assertEqual(result, expected)
    
    def test_cache_expiry(self):
        """测试缓存过期"""
        import time
        
        cache = DecisionCache(max_size=100, ttl=1)
        operation = {"type": "test"}
        
        cache.set(operation, {"strategy": "auto"})
        time.sleep(1.1)
        
        result = cache.get(operation)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
```

---

## 部署指南

### 开发环境

1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd FolderSizeMonitor
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件
   ```

4. **运行测试**
   ```bash
   python -m pytest tests/
   ```

### 生产环境

1. **备份数据**
   ```bash
   tar -czf backup.tar.gz .lingma/
   ```

2. **部署代码**
   ```bash
   git pull origin main
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行迁移**
   ```bash
   python .lingma/scripts/migrate.py
   ```

5. **重启服务**
   ```bash
   systemctl restart spec-driven
   ```

---

## 扩展开发

### 添加新的 MCP 服务器

1. **创建配置文件**
   ```json
   {
     "my_server": {
       "command": "npx",
       "args": ["-y", "@my-org/server"],
       "enabled": true
     }
   }
   ```

2. **更新验证脚本**
   ```python
   def verify_my_server():
       # 验证逻辑
       pass
   ```

3. **添加文档**
   - 更新用户指南
   - 添加配置示例

### 添加新的 Rule

1. **创建 Rule 文件**
   ```markdown
   ---
   trigger: always_on
   ---
   # My Custom Rule
   
   **角色**: ...
   **职责**: ...
   
   ## 规则内容
   ...
   ```

2. **放置到正确位置**
   ```
   .lingma/rules/my-custom-rule.md
   ```

3. **测试 Rule**
   - 触发相关操作
   - 验证 Rule 是否生效

### 添加新的 Skill

1. **创建 Skill 目录**
   ```
   .lingma/skills/my-skill/
   ├── SKILL.md
   └── examples/
   ```

2. **编写 Skill 文档**
   ```markdown
   # My Skill
   
   **用途**: ...
   
   ## 使用方法
   ...
   
   ## 示例
   ...
   ```

3. **注册 Skill**
   - 更新 agent 配置
   - 添加引用

---

## 性能调优

### 决策缓存调优

```python
# 调整缓存大小和 TTL
cache = DecisionCache(max_size=2000, ttl=7200)
```

### 日志批处理调优

```python
# 调整批量大小和刷新间隔
logger = BatchLogger(batch_size=20, flush_interval=3.0)
```

### 内存优化

```python
# 定期清理过期缓存
cache.clear_expired()

# 限制历史记录大小
undo_mgr = UndoManager(max_history=30)
```

---

## 监控与告警

### 关键指标

| 指标 | 阈值 | 告警级别 |
|------|------|----------|
| 决策延迟 | > 100ms | Warning |
| 错误率 | > 5% | Critical |
| 缓存命中率 | < 50% | Warning |
| 内存使用 | > 100MB | Warning |

### 日志分析

```bash
# 查看错误日志
grep "ERROR" .lingma/logs/automation.log

# 查看性能指标
cat .lingma/state/metrics.json
```

---

## 常见问题

### Q: 如何调试决策引擎？

A: 启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Q: 如何自定义风险评估算法？

A: 修改 `automation-engine.py` 中的 `assess_risk()` 方法。

### Q: 如何添加新的自动化级别？

A: 在 `automation.json` 中添加新级别，并更新相关逻辑。

---

## 贡献指南

欢迎贡献代码、文档或建议！

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

**许可证**: MIT  
**维护者**: AI Assistant  
**最后更新**: 2026-04-17
