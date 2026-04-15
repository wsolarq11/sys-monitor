# Agent Communication Protocol (ACP)

## 概述

本目录定义了自迭代流系统中 Agent 之间的通信协议，遵循 [ACP (Agent Client Protocol)](https://agentclientprotocol.com) 和 [A2A (Agent-to-Agent Protocol)](https://google.github.io/a2a) 开放标准。

**目标**: 
- 标准化 Agent 之间的通信格式
- 支持多 Agent 协作和任务分发
- 实现可观测性和追踪
- 提供权限控制和审计

## 协议架构

### 四层协议栈
```
┌─────────────────────────────────────┐
│   Application Layer (业务逻辑)       │
│   - Task Delegation                 │
│   - Result Aggregation              │
│   - Conflict Resolution             │
└──────────────┬──────────────────────┘
               │ ACP Messages
┌──────────────▼──────────────────────┐
│   Communication Layer (通信层)       │
│   - JSON-RPC 2.0                    │
│   - Session Management              │
│   - Permission Control              │
└──────────────┬──────────────────────┘
               │ Transport
┌──────────────▼──────────────────────┐
│   Transport Layer (传输层)           │
│   - stdio (本地进程)                 │
│   - HTTP/WebSocket (远程)            │
└──────────────┬──────────────────────┘
               │ Infrastructure
┌──────────────▼──────────────────────┘
│   Infrastructure Layer (基础设施)    │
│   - Process Management              │
│   - Resource Isolation              │
│   - Logging & Monitoring            │
└─────────────────────────────────────┘
```

## 消息格式

### 基础消息结构
```json
{
  "jsonrpc": "2.0",
  "id": "uuid-v4",
  "method": "session/prompt",
  "params": {
    "sessionId": "sess_123456",
    "prompt": "扫描文件夹大小",
    "context": {
      "traceId": "trace_abc123",
      "callerAgent": "spec-driven-core-agent",
      "targetAgent": "test-runner-agent"
    },
    "metadata": {
      "priority": "high",
      "timeout": 30000,
      "retryPolicy": {
        "maxRetries": 3,
        "backoff": "exponential"
      }
    }
  }
}
```

### 消息类型

#### 1. Request（请求）
```json
{
  "jsonrpc": "2.0",
  "id": "req_001",
  "method": "task/delegate",
  "params": {
    "taskId": "task_001",
    "taskType": "test_execution",
    "description": "运行单元测试并生成报告",
    "input": {
      "testPattern": "src/**/*.test.ts",
      "coverage": true
    },
    "expectedOutput": {
      "format": "json",
      "fields": ["passRate", "failures", "coverage"]
    },
    "deadline": "2026-04-15T10:00:00Z"
  }
}
```

#### 2. Response（响应）
```json
{
  "jsonrpc": "2.0",
  "id": "req_001",
  "result": {
    "status": "completed",
    "output": {
      "passRate": 98.5,
      "failures": [
        {
          "test": "formatBytes",
          "error": "Expected '1.5 MB', got '1.4 MB'"
        }
      ],
      "coverage": 85.2
    },
    "executionTime": 12500,
    "metadata": {
      "agentId": "test-runner-agent",
      "timestamp": "2026-04-15T09:58:30Z"
    }
  }
}
```

#### 3. Error（错误）
```json
{
  "jsonrpc": "2.0",
  "id": "req_001",
  "error": {
    "code": -32000,
    "message": "Test execution failed",
    "data": {
      "type": "EnvironmentError",
      "details": "Node.js version mismatch",
      "suggestion": "Use Node.js >= 18",
      "recoverable": true
    }
  }
}
```

#### 4. Notification（通知）
```json
{
  "jsonrpc": "2.0",
  "method": "session/update",
  "params": {
    "sessionId": "sess_123456",
    "status": "in_progress",
    "progress": {
      "current": 5,
      "total": 10,
      "stage": "Running E2E tests"
    },
    "timestamp": "2026-04-15T09:57:00Z"
  }
}
```

## 会话管理

### 创建会话
```json
// Request
{
  "method": "session/new",
  "params": {
    "agentId": "test-runner-agent",
    "capabilities": ["test_execution", "report_generation"],
    "context": {
      "projectId": "FolderSizeMonitor",
      "branch": "main"
    }
  }
}

// Response
{
  "result": {
    "sessionId": "sess_123456",
    "status": "active",
    "expiresAt": "2026-04-15T10:30:00Z"
  }
}
```

### 发送 Prompt
```json
// Request
{
  "method": "session/prompt",
  "params": {
    "sessionId": "sess_123456",
    "prompt": "运行所有测试",
    "mode": "agent"
  }
}

// Response (streaming)
{
  "result": {
    "stopReason": "end_turn",
    "content": [
      {
        "type": "text",
        "text": "✅ 测试执行完成\n\n- 通过率: 98.5%\n- 失败: 3 个\n- 执行时间: 12.5s"
      }
    ]
  }
}
```

### 加载历史会话
```json
// Request
{
  "method": "session/load",
  "params": {
    "sessionId": "sess_123456"
  }
}

// Response
{
  "result": {
    "sessionId": "sess_123456",
    "history": [
      {
        "role": "user",
        "content": "运行所有测试"
      },
      {
        "role": "assistant",
        "content": "✅ 测试执行完成..."
      }
    ]
  }
}
```

## 权限控制

### 请求权限
```json
// Agent 请求执行敏感操作
{
  "method": "request_permission",
  "params": {
    "action": "execute_command",
    "command": "pnpm run test",
    "reason": "需要运行测试验证代码质量",
    "riskLevel": "low",
    "autoApprove": false
  }
}

// 用户批准
{
  "result": {
    "approved": true,
    "approvedBy": "user",
    "timestamp": "2026-04-15T09:56:00Z"
  }
}
```

### 权限级别
| 级别 | 说明 | 示例 | 自动批准 |
|------|------|------|----------|
| Low | 只读操作 | 读取文件、查询数据库 | ✅ |
| Medium | 写入操作 | 修改文档、运行测试 | ❌ |
| High | 系统操作 | 安装依赖、重启服务 | ❌ |
| Critical | 危险操作 | 删除文件、格式化磁盘 | ❌ + 二次确认 |

## 任务委托模式

### 模式 1: 单 Agent 监督者（Single-Agent Supervisor）
```
用户请求
    ↓
Spec-Driven Core Agent (监督者)
    ├─ 分析任务
    ├─ 决定是否需要委托
    └─ 直接执行或委托给专业 Agent
```

**适用场景**: 
- 简单任务
- 监督者具备所需能力
- 低延迟要求

**示例**:
```json
{
  "method": "task/delegate",
  "params": {
    "strategy": "supervisor",
    "task": {
      "type": "code_review",
      "description": "审查 PR #123"
    },
    "delegateTo": "code-review-agent",
    "waitForCompletion": true
  }
}
```

### 模式 2: 初始化器-执行器分离（Initializer-Executor Split）
```
用户请求
    ↓
Initializer Agent (分解任务)
    ├─ 创建子任务 1 → Executor Agent A
    ├─ 创建子任务 2 → Executor Agent B
    └─ 汇总结果
```

**适用场景**: 
- 中等复杂度任务
- 可并行执行的子任务
- 需要专业化能力

**示例**:
```json
{
  "method": "task/delegate",
  "params": {
    "strategy": "initializer-executor",
    "task": {
      "type": "feature_development",
      "description": "实现文件夹监控功能"
    },
    "subtasks": [
      {
        "id": "subtask_1",
        "description": "编写 Rust 后端代码",
        "assignedTo": "rust-expert-agent"
      },
      {
        "id": "subtask_2",
        "description": "编写 React 前端组件",
        "assignedTo": "react-expert-agent"
      },
      {
        "id": "subtask_3",
        "description": "运行测试",
        "assignedTo": "test-runner-agent"
      }
    ]
  }
}
```

### 模式 3: 多 Agent 协调（Multi-Agent Coordination）
```
用户请求
    ↓
Orchestrator Agent (编排者)
    ├─ Research Agent (调研)
    ├─ Design Agent (设计)
    ├─ Code Agent (编码)
    ├─ Test Agent (测试)
    └─ Review Agent (审查)
         ↓
    汇总并验证结果
```

**适用场景**: 
- 复杂项目
- 需要多领域专业知识
- 高质量要求

**示例**:
```json
{
  "method": "task/delegate",
  "params": {
    "strategy": "multi-agent-coordination",
    "task": {
      "type": "system_refactoring",
      "description": "重构数据库层"
    },
    "agents": [
      {
        "role": "researcher",
        "agentId": "database-expert-agent",
        "task": "调研最佳实践"
      },
      {
        "role": "designer",
        "agentId": "architect-agent",
        "task": "设计新架构",
        "dependsOn": ["researcher"]
      },
      {
        "role": "implementer",
        "agentId": "rust-expert-agent",
        "task": "实现新架构",
        "dependsOn": ["designer"]
      },
      {
        "role": "tester",
        "agentId": "test-runner-agent",
        "task": "验证实现",
        "dependsOn": ["implementer"]
      }
    ]
  }
}
```

## 错误处理

### 重试策略
```json
{
  "retryPolicy": {
    "maxRetries": 3,
    "backoff": "exponential",
    "initialDelay": 1000,
    "maxDelay": 10000,
    "retryableErrors": [
      "NetworkError",
      "TimeoutError",
      "RateLimitError"
    ]
  }
}
```

### 超时处理
```json
{
  "timeout": 30000,
  "onTimeout": {
    "action": "cancel",
    "notify": true,
    "fallback": "use_cached_result"
  }
}
```

### 降级策略
```json
{
  "fallback": {
    "enabled": true,
    "strategies": [
      {
        "condition": "primary_agent_unavailable",
        "action": "use_backup_agent",
        "backupAgentId": "general-purpose-agent"
      },
      {
        "condition": "timeout",
        "action": "return_partial_result",
        "includeMetadata": true
      }
    ]
  }
}
```

## 可观测性

### 追踪上下文
```json
{
  "traceContext": {
    "traceId": "trace_abc123",
    "spanId": "span_def456",
    "parentSpanId": "span_ghi789",
    "samplingRate": 1.0
  }
}
```

### 指标收集
```json
{
  "metrics": {
    "latency": 12500,
    "tokenUsage": {
      "prompt": 1500,
      "completion": 800,
      "total": 2300
    },
    "cost": 0.0046,
    "retries": 0,
    "errors": 0
  }
}
```

### 日志记录
```json
{
  "log": {
    "level": "info",
    "message": "Task delegated to test-runner-agent",
    "timestamp": "2026-04-15T09:56:00Z",
    "fields": {
      "taskId": "task_001",
      "agentId": "test-runner-agent",
      "traceId": "trace_abc123"
    }
  }
}
```

## 安全考虑

### 认证
```json
{
  "auth": {
    "type": "api_key",
    "credentials": {
      "apiKey": "sk-xxx"
    }
  }
}
```

### 授权
```json
{
  "authorization": {
    "roles": ["developer", "reviewer"],
    "permissions": [
      "read:code",
      "write:docs",
      "execute:tests"
    ]
  }
}
```

### 审计
```json
{
  "audit": {
    "action": "task_delegate",
    "actor": "spec-driven-core-agent",
    "target": "test-runner-agent",
    "timestamp": "2026-04-15T09:56:00Z",
    "result": "success",
    "ipAddress": "127.0.0.1"
  }
}
```

## 实现指南

### 本地进程通信（stdio）
```typescript
// Client (Editor/IDE)
import { spawn } from 'child_process';

const agent = spawn('claude-code', ['--agent', 'test-runner']);

// 发送请求
agent.stdin.write(JSON.stringify({
  jsonrpc: '2.0',
  id: 'req_001',
  method: 'session/prompt',
  params: { ... }
}) + '\n');

// 接收响应
agent.stdout.on('data', (data) => {
  const response = JSON.parse(data.toString());
  console.log(response);
});
```

### 远程通信（HTTP）
```typescript
// Server (Agent Service)
import express from 'express';

const app = express();
app.use(express.json());

app.post('/rpc', async (req, res) => {
  const { method, params } = req.body;
  
  if (method === 'session/prompt') {
    const result = await handlePrompt(params);
    res.json({
      jsonrpc: '2.0',
      id: req.body.id,
      result
    });
  }
});

app.listen(3000);
```

### WebSocket 实时通信
```typescript
// Bidirectional streaming
import WebSocket from 'ws';

const ws = new WebSocket('ws://agent-server:3000/ws');

ws.on('open', () => {
  ws.send(JSON.stringify({
    method: 'session/new',
    params: { ... }
  }));
});

ws.on('message', (data) => {
  const notification = JSON.parse(data.toString());
  console.log('Progress:', notification.params.progress);
});
```

## 工具和资源

### 协议规范
- [ACP Official Specification](https://agentclientprotocol.com)
- [A2A Protocol](https://google.github.io/a2a)
- [JSON-RPC 2.0](https://www.jsonrpc.org/specification)

### 参考实现
- [OpenClaw ACP Implementation](https://github.com/openclaw/openclaw)
- [Zed Editor ACP Client](https://github.com/zed-industries/zed)
- [Claude Code ACP Server](https://github.com/anthropics/claude-code)

### 调试工具
```bash
# 测试 ACP 连接
curl -X POST http://localhost:3000/rpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"test","method":"ping"}'

# 监控 ACP 流量
tcpdump -i lo port 3000 -X

# 日志分析
grep "ACP" .lingma/logs/agent-communication.log | jq
```

---

**最后更新**: 2026-04-15  
**版本**: v1.0.0  
**状态**: ✅ Active  
**标准**: ACP + A2A + JSON-RPC 2.0
