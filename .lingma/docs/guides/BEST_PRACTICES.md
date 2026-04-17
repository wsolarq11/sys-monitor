# Spec-Driven Development 最佳实践

**版本**: 1.0.0  
**最后更新**: 2026-04-17

## 目录

1. [编码最佳实践](#编码最佳实践)
2. [Spec 编写最佳实践](#spec-编写最佳实践)
3. [自动化策略最佳实践](#自动化策略最佳实践)
4. [性能优化最佳实践](#性能优化最佳实践)
5. [用户体验最佳实践](#用户体验最佳实践)
6. [测试最佳实践](#测试最佳实践)
7. [文档最佳实践](#文档最佳实践)
8. [安全最佳实践](#安全最佳实践)

---

## 编码最佳实践

### 1. 遵循单一职责原则

每个模块、类、函数应该只有一个职责。

**✅ 好的做法**:
```python
class DecisionCache:
    """只负责缓存管理"""
    def get(self, operation):
        pass
    
    def set(self, operation, result):
        pass

class RiskAssessor:
    """只负责风险评估"""
    def assess(self, operation):
        pass
```

**❌ 不好的做法**:
```python
class Everything:
    """做了太多事情"""
    def cache_decision(self):
        pass
    
    def assess_risk(self):
        pass
    
    def log_operation(self):
        pass
    
    def send_notification(self):
        pass
```

### 2. 使用类型注解

**✅ 好的做法**:
```python
def calculate_risk(operation: Dict[str, Any]) -> float:
    """计算风险分数"""
    pass
```

**❌ 不好的做法**:
```python
def calculate_risk(operation):
    """计算风险分数"""
    pass
```

### 3. 编写文档字符串

**✅ 好的做法**:
```python
def process_data(data: List[Dict], batch_size: int = 100) -> Dict[str, Any]:
    """
    批量处理数据
    
    Args:
        data: 待处理的数据列表
        batch_size: 批处理大小，默认 100
        
    Returns:
        处理结果统计
        
    Raises:
        ValueError: 当数据为空时
    """
    if not data:
        raise ValueError("数据不能为空")
    
    # 处理逻辑
    pass
```

### 4. 错误处理

**✅ 好的做法**:
```python
try:
    result = perform_operation()
except SpecificError as e:
    logger.error(f"操作失败: {e}")
    handle_error(e)
except Exception as e:
    logger.critical(f"未知错误: {e}")
    raise
```

**❌ 不好的做法**:
```python
try:
    result = perform_operation()
except:
    pass  # 静默忽略所有错误
```

### 5. 避免硬编码

**✅ 好的做法**:
```python
# 从配置读取
config = load_config()
max_retries = config.get('max_retries', 3)
```

**❌ 不好的做法**:
```python
# 硬编码
max_retries = 3
```

---

## Spec 编写最佳实践

### 1. 明确验收标准

每个需求都应该有可量化的验收标准。

**✅ 好的做法**:
```markdown
#### FR-001: 智能环境自检

**验收标准**:
- [ ] AC-001-01: 自动检测缺失的目录和文件
- [ ] AC-001-02: 自动创建或修复损坏的结构
- [ ] AC-001-03: 验证工具链可用性
- [ ] AC-001-04: 检查并应用配置更新
- [ ] AC-001-05: 生成清晰的自检报告
```

**❌ 不好的做法**:
```markdown
#### FR-001: 智能环境自检

**描述**: 系统应该能够检查环境
```

### 2. 任务分解要合理

任务应该足够小，可以在 2-4 小时内完成。

**✅ 好的做法**:
```markdown
- [x] Task-001: 创建自动化引擎核心 (预计: 2h)
  - ✅ 实现风险评估算法
  - ✅ 实现置信度计算
  - ✅ 实现策略选择逻辑
```

**❌ 不好的做法**:
```markdown
- [ ] Task-001: 实现整个系统 (预计: 40h)
```

### 3. 记录实施笔记

每次完成任务后，添加详细的实施笔记。

**✅ 好的做法**:
```markdown
### [2026-04-17 21:05:00] Phase 4 Task-013 完成 - 性能优化

**完成时间**: 2026-04-17 21:05  
**状态**: ✅ 已完成  
**总耗时**: ~30分钟

**关键成果**:
1. ✅ 决策缓存模块 (198 lines)
2. ✅ 批量日志写入器 (220 lines)
3. ✅ 性能优化器 (332 lines)

**性能指标**:
- 文件写入性能：提升 30%
- 文件读取性能：提升 9.1%
```

### 4. 保持 Spec 更新

- 及时更新任务状态
- 记录进度百分比
- 更新实施笔记
- 标记完成的任务

---

## 自动化策略最佳实践

### 1. 选择合适的自动化级别

根据环境选择自动化级别：

| 环境 | 推荐级别 | 原因 |
|------|---------|------|
| 生产环境 | Conservative | 安全性优先 |
| 开发环境 | Balanced | 平衡效率和安全 |
| 测试环境 | Aggressive | 快速迭代 |
| 实验环境 | Full Auto | 完全自动化 |

### 2. 逐步提高自动化程度

不要一开始就启用最高自动化级别：

1. **第一阶段**: Conservative - 观察系统行为
2. **第二阶段**: Balanced - 提高自动化程度
3. **第三阶段**: Aggressive - 最大化效率
4. **第四阶段**: Full Auto - 完全自动化（如需要）

### 3. 监控自动化效果

定期检查以下指标：

- 自动化执行率
- 错误率
- 用户覆盖次数
- 回滚次数

**示例**:
```python
from automation_engine import get_stats

stats = get_stats()
print(f"自动化执行率: {stats['automation_rate']}%")
print(f"错误率: {stats['error_rate']}%")
print(f"用户覆盖次数: {stats['user_overrides']}")
```

### 4. 保留人工干预能力

即使在高自动化级别下，也要确保：

- 可以随时暂停自动化
- 可以手动撤销操作
- 可以查看操作历史
- 可以调整风险阈值

---

## 性能优化最佳实践

### 1. 使用决策缓存

对于重复的决策，使用缓存避免重复计算。

**✅ 好的做法**:
```python
from decision_cache import get_cached_decision, cache_decision

# 尝试从缓存获取
result = get_cached_decision(operation)
if result:
    return result

# 计算新决策
result = evaluate_operation(operation)

# 缓存结果
cache_decision(operation, result)
```

### 2. 批量处理日志

避免每次操作都写入磁盘。

**✅ 好的做法**:
```python
from batch_logger import log_entry

# 批量记录日志
for operation in operations:
    log_entry({
        'level': 'INFO',
        'message': f'Processed {operation}'
    })

# 在适当时机刷新
flush_logs()
```

### 3. 限制历史记录大小

避免内存泄漏。

**✅ 好的做法**:
```python
# 限制撤销历史为 50 条
undo_mgr = UndoManager(max_history=50)

# 定期清理过期缓存
cache.clear_expired()
```

### 4. 性能监控

定期运行性能分析：

```bash
python .lingma/scripts/performance-optimizer.py
```

关注以下指标：
- 决策延迟 < 100ms
- 缓存命中率 > 80%
- 内存使用 < 100MB

---

## 用户体验最佳实践

### 1. 提供清晰的进度反馈

**✅ 好的做法**:
```python
with create_progress(100, "处理数据") as progress:
    for i, item in enumerate(items):
        process(item)
        progress.update(current=i+1)
```

**输出**:
```
处理数据: [██████████████████████████████] 100.0% (100/100) | 耗时: 5.2s
✅ 完成 (总耗时: 5.23s)
```

### 2. 使用统一的消息格式

**✅ 好的做法**:
```python
formatter = get_message_formatter()

print(formatter.success("文件保存成功", "路径: /path/to/file"))
print(formatter.warning("配置警告", "使用默认值"))
print(formatter.error("连接失败", "请检查网络"))
```

### 3. 提供撤销功能

对于重要操作，始终提供撤销能力。

**✅ 好的做法**:
```python
def modify_file(path, content):
    # 记录操作
    undo_mgr.record_action(
        "modify_file",
        {"path": path, "content": content},
        undo_func=lambda d: restore_file(d['path']),
        redo_func=lambda d: modify_file(d['path'], d['content'])
    )
    
    # 执行修改
    write_file(path, content)
```

### 4. 友好的错误提示

**✅ 好的做法**:
```
❌ 连接失败
   无法连接到服务器，请检查网络连接
   建议: ping server.example.com
```

**❌ 不好的做法**:
```
Error: Connection refused
```

---

## 测试最佳实践

### 1. 编写单元测试

为每个模块编写单元测试。

**示例**:
```python
import unittest
from decision_cache import DecisionCache

class TestDecisionCache(unittest.TestCase):
    
    def test_cache_hit(self):
        cache = DecisionCache()
        operation = {"type": "test"}
        expected = {"strategy": "auto"}
        
        cache.set(operation, expected)
        result = cache.get(operation)
        
        self.assertEqual(result, expected)
```

### 2. 保持测试独立

每个测试应该独立运行，不依赖其他测试的状态。

**✅ 好的做法**:
```python
def setUp(self):
    # 每个测试前重置状态
    self.cache = DecisionCache()
```

### 3. 测试边界情况

**示例**:
```python
def test_empty_cache(self):
    """测试空缓存"""
    cache = DecisionCache()
    result = cache.get({"type": "test"})
    self.assertIsNone(result)

def test_cache_full(self):
    """测试缓存已满"""
    cache = DecisionCache(max_size=2)
    cache.set({"type": "1"}, {"result": "1"})
    cache.set({"type": "2"}, {"result": "2"})
    cache.set({"type": "3"}, {"result": "3"})  # 应该淘汰第一个
    
    self.assertIsNone(cache.get({"type": "1"}))
```

### 4. 自动化测试

在 CI/CD 中自动运行测试：

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: python -m pytest tests/
```

---

## 文档最佳实践

### 1. 保持文档更新

代码变更后，立即更新相关文档。

**检查清单**:
- [ ] 用户指南已更新
- [ ] 开发者文档已更新
- [ ] API 参考已更新
- [ ] 变更日志已更新

### 2. 提供实际示例

**✅ 好的做法**:
```python
# 示例：使用决策缓存
from decision_cache import get_decision_cache

cache = get_decision_cache()
result = cache.get(operation)
```

**❌ 不好的做法**:
```python
# 使用缓存
cache.get(operation)
```

### 3. 使用清晰的标题层次

```markdown
# 一级标题
## 二级标题
### 三级标题
#### 四级标题
```

### 4. 包含故障排除部分

为常见问题提供解决方案。

**示例**:
```markdown
## 故障排除

### 问题: 模块导入错误

**症状**: `ModuleNotFoundError`

**解决方案**:
1. 检查 Python 路径
2. 安装依赖: `pip install psutil`
3. 验证安装: `python verify-setup.py`
```

---

## 安全最佳实践

### 1. 验证用户输入

**✅ 好的做法**:
```python
def execute_command(command: str):
    # 白名单验证
    allowed_commands = ['status', 'help', 'version']
    if command not in allowed_commands:
        raise ValueError(f"不允许的命令: {command}")
    
    # 执行命令
    pass
```

### 2. 限制文件访问

**✅ 好的做法**:
```python
def read_file(path: str):
    # 确保路径在允许的目录内
    allowed_dirs = ['.lingma/', 'scripts/']
    if not any(path.startswith(d) for d in allowed_dirs):
        raise PermissionError(f"不允许访问: {path}")
    
    # 读取文件
    pass
```

### 3. 记录审计日志

**✅ 好的做法**:
```python
def perform_sensitive_operation(operation):
    # 记录审计日志
    audit_log({
        'timestamp': datetime.now().isoformat(),
        'operation': operation,
        'user': current_user,
        'result': 'success'
    })
    
    # 执行操作
    pass
```

### 4. 定期审查权限

- 检查 MCP 服务器权限
- 审查 Git Hook 权限
- 验证文件访问权限

---

## 总结

遵循这些最佳实践可以：

- ✅ 提高代码质量
- ✅ 减少错误率
- ✅ 提升开发效率
- ✅ 改善用户体验
- ✅ 增强系统安全性

记住：**最佳实践不是规则，而是指导原则**。根据实际情况灵活应用。

---

**许可证**: MIT  
**维护者**: AI Assistant  
**最后更新**: 2026-04-17
