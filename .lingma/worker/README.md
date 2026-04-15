# 多Agent编排系统使用指南

## 📖 概述

这是一个真正的多Agent编排系统，实现了任务队列管理、Agent通信、质量门禁和决策日志等核心功能。

## 🚀 快速开始

### 1. 提交任务

```bash
# 基本用法
python .lingma/scripts/orchestrator.py --request "实现用户认证功能"

# 指定优先级
python .lingma/scripts/orchestrator.py --request "修复登录bug" --priority HIGH

# 非交互模式（不等待执行结果）
echo "n" | python .lingma/scripts/orchestrator.py --request "添加单元测试"
```

### 2. 查询任务状态

```bash
# 查询特定任务
python .lingma/scripts/orchestrator.py --status <task_id>

# 列出所有任务
python .lingma/scripts/orchestrator.py --list

# 列出待处理任务
python .lingma/scripts/orchestrator.py --list --filter pending

# 查看队列统计
python .lingma/scripts/orchestrator.py --stats
```

### 3. 运行测试

```bash
# 任务队列单元测试
python .lingma/worker/task_queue.py --test

# Agent客户端单元测试
python .lingma/worker/agent_client.py --test

# 端到端测试
python .lingma/scripts/test-orchestration.py
```

## 📚 核心组件

### 1. TaskQueue (任务队列)

**位置**: `.lingma/worker/task_queue.py`

**功能**:
- 任务的enqueue/dequeue/update_status
- pending/running/completed/failed状态管理
- UUID生成和任务文件持久化
- 优先级调度

**示例**:
```python
from .lingma.worker.task_queue import TaskQueue, Task, TaskPriority, TaskStatus

queue = TaskQueue()

# 创建任务
task = Task(
    task_type="code_implementation",
    payload={"feature": "user_auth", "language": "python"},
    priority=TaskPriority.HIGH,
    assigned_agent="spec-driven-core-agent"
)
task_id = queue.enqueue(task)

# 获取任务
task = queue.dequeue(agent_filter="spec-driven-core-agent")

# 更新状态
queue.update_status(
    task_id,
    TaskStatus.COMPLETED,
    result={"lines_added": 150}
)
```

### 2. AgentClient (Agent通信客户端)

**位置**: `.lingma/worker/agent_client.py`

**功能**:
- 通过stdio调用目标Agent
- JSON-RPC 2.0协议封装
- Session管理和超时控制

**示例**:
```python
from .lingma.worker.agent_client import AgentClient

client = AgentClient()

# 调用Agent
response = client.call_agent(
    agent_name="spec-driven-core-agent",
    method="implement_feature",
    params={"feature": "user_auth"},
    timeout=120
)

if response.error:
    print(f"错误: {response.error['message']}")
else:
    print(f"结果: {response.result}")
```

### 3. Orchestrator (编排器)

**位置**: `.lingma/scripts/orchestrator.py`

**功能**:
- 接收用户请求
- 创建任务并委派给Supervisor
- 轮询检查完成状态
- 聚合结果并返回

**示例**:
```python
from .lingma.scripts.orchestrator import Orchestrator

orchestrator = Orchestrator()

# 提交请求
task_id = orchestrator.submit_request(
    "实现用户认证功能",
    priority="HIGH"
)

# 等待执行
result = orchestrator.execute_and_wait(task_id, timeout=600)

# 查询状态
status = orchestrator.get_task_status(task_id)

# 列出任务
tasks = orchestrator.list_tasks(limit=10)
```

## 🎯 质量门禁（硬约束）

系统强制执行5层质量门禁，任何一层失败都会导致任务终止：

1. **Gate 1**: 执行Agent自检
   - 检查输出格式
   - 验证关键指标
   - 确保无错误日志

2. **Gate 2**: Test Runner验证
   - 执行自动化测试
   - 所有测试必须通过

3. **Gate 3**: Code Review审查
   - 代码风格检查
   - 安全性审查
   - 性能分析
   - 质量分数 ≥ 80

4. **Gate 4**: Documentation检查
   - 文档完整性
   - API文档
   - 使用示例

5. **Gate 5**: Supervisor最终验收
   - 综合评分 ≥ 85
   - 所有前置门禁通过

## 📊 决策日志

所有关键决策都记录在 `.lingma/logs/decision-log.json` 中：

```json
[
  {
    "timestamp": "2026-04-16T00:58:45.357519",
    "agent": "orchestrator",
    "action": "REQUEST_SUBMITTED",
    "metadata": {
      "task_id": "3af88781-ec0c-4731-9847-aca63c4bec93",
      "user_request": "测试功能实现",
      "priority": "MEDIUM"
    }
  }
]
```

## 🔧 高级用法

### 自定义任务处理器

```python
from .lingma.worker.task_queue import TaskQueue, Task

queue = TaskQueue()

# 注册自定义处理器
def my_custom_handler(task):
    # 处理逻辑
    result = {"status": "success"}
    return result

# 在Supervisor Agent中使用
response = client.call_agent(
    agent_name="custom-agent",
    method="my_custom_handler",
    params=task.payload
)
```

### 批量任务提交

```python
from .lingma.scripts.orchestrator import Orchestrator

orchestrator = Orchestrator()

tasks = [
    "实现用户登录",
    "实现用户注册",
    "实现密码重置"
]

task_ids = []
for request in tasks:
    task_id = orchestrator.submit_request(request, priority="HIGH")
    task_ids.append(task_id)

print(f"已提交 {len(task_ids)} 个任务")
```

### 监控任务进度

```python
import time
from .lingma.scripts.orchestrator import Orchestrator

orchestrator = Orchestrator()
task_id = orchestrator.submit_request("实现复杂功能")

# 轮询监控
while True:
    status = orchestrator.get_task_status(task_id)
    print(f"状态: {status['status']}")
    
    if status['status'] in ['completed', 'failed']:
        break
    
    time.sleep(2)
```

## 📁 目录结构

```
.lingma/
├── worker/
│   ├── task_queue.py          # 任务队列管理器
│   ├── agent_client.py        # Agent通信客户端
│   └── tasks/                 # 任务文件存储
│       ├── pending/           # 待处理任务
│       ├── running/           # 运行中任务
│       ├── completed/         # 已完成任务
│       └── failed/            # 失败任务
├── scripts/
│   ├── orchestrator.py        # 编排器入口
│   └── test-orchestration.py  # 端到端测试
├── agents/
│   └── supervisor-agent.md    # Supervisor Agent定义
├── logs/
│   └── decision-log.json      # 决策日志
└── reports/
    └── orchestration-implementation-report.md  # 实施报告
```

## 🐛 故障排除

### 问题1: 任务一直处于pending状态

**原因**: Supervisor Agent未启动或未处理任务

**解决**:
```bash
# 检查队列状态
python .lingma/scripts/orchestrator.py --stats

# 手动触发Supervisor处理
# （需要实现Supervisor的后台运行逻辑）
```

### 问题2: Agent调用超时

**原因**: Agent执行时间过长或死锁

**解决**:
```python
# 增加超时时间
response = client.call_agent(
    agent_name="spec-driven-core-agent",
    method="implement_feature",
    params=params,
    timeout=300  # 5分钟
)
```

### 问题3: Windows文件锁定问题

**原因**: 多个进程同时访问任务文件

**解决**:
- 避免同时运行多个Orchestrator实例
- 使用较长的清理保留期

### 问题4: 决策日志文件损坏

**原因**: 并发写入或异常中断

**解决**:
```bash
# 备份并重建日志
cp .lingma/logs/decision-log.json .lingma/logs/decision-log.json.bak
echo "[]" > .lingma/logs/decision-log.json
```

## 📝 最佳实践

1. **合理使用优先级**
   - CRITICAL: 紧急bug修复
   - HIGH: 重要功能开发
   - MEDIUM: 常规任务
   - LOW: 优化和改进

2. **设置合适的超时时间**
   - 简单任务: 60秒
   - 中等任务: 300秒
   - 复杂任务: 600秒

3. **定期检查决策日志**
   ```bash
   cat .lingma/logs/decision-log.json | python -m json.tool
   ```

4. **清理旧任务**
   ```python
   queue.cleanup_old_tasks(
       retention_days_completed=7,
       retention_days_failed=30
   )
   ```

5. **监控队列健康度**
   ```bash
   python .lingma/scripts/orchestrator.py --stats
   ```

## 🎓 学习资源

- [实施报告](../reports/orchestration-implementation-report.md)
- [Supervisor Agent定义](../agents/supervisor-agent.md)
- [任务队列API](../worker/task_queue.py)
- [Agent客户端API](../worker/agent_client.py)

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证。

---

**版本**: 1.0.0  
**最后更新**: 2026-04-16  
**维护者**: AI Assistant
