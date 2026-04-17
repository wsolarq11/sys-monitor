#!/usr/bin/env python3
"""
Multi-Agent Orchestrator - 多智能体协调器

Manager-Expert 协作模型、工作流编排、并行执行
实现复杂任务的智能分解与协调

参考社区最佳实践:
- Manager-Expert collaboration pattern
- Workflow orchestration with DAG
- Parallel execution with dependency management
- Context sharing and state coordination
"""

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from collections import defaultdict
import uuid

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent 角色"""
    MANAGER = "manager"  # 经理/协调器
    EXPERT = "expert"  # 专家
    WORKER = "worker"  # 工作者


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class ExecutionMode(Enum):
    """执行模式"""
    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"  # 并行执行
    HYBRID = "hybrid"  # 混合模式


@dataclass
class AgentProfile:
    """Agent 档案"""
    agent_id: str
    name: str
    role: AgentRole
    capabilities: List[str]  # 能力列表
    specialization: Optional[str] = None  # 专业领域
    max_concurrent_tasks: int = 1  # 最大并发任务数
    current_load: int = 0  # 当前负载
    success_rate: float = 1.0  # 成功率
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
    
    def can_accept_task(self) -> bool:
        """是否可以接受新任务"""
        return self.current_load < self.max_concurrent_tasks
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class SubTask:
    """子任务"""
    task_id: str
    description: str
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    priority: int = 0
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    execution_time: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class WorkflowDefinition:
    """工作流定义"""
    workflow_id: str
    name: str
    description: str
    tasks: List[SubTask] = field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class ExecutionContext:
    """执行上下文"""
    context_id: str
    workflow_id: str
    shared_data: Dict[str, Any] = field(default_factory=dict)
    task_results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
    
    def get_task_result(self, task_id: str) -> Optional[Any]:
        """获取任务结果"""
        return self.task_results.get(task_id)
    
    def set_task_result(self, task_id: str, result: Any):
        """设置任务结果"""
        self.task_results[task_id] = result
    
    def share_data(self, key: str, value: Any):
        """共享数据"""
        self.shared_data[key] = value
    
    def get_shared_data(self, key: str, default: Any = None) -> Any:
        """获取共享数据"""
        return self.shared_data.get(key, default)


class AgentRegistry:
    """Agent 注册中心
    
    管理所有可用的 Agent
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentProfile] = {}
        self.agent_capabilities: Dict[str, List[str]] = defaultdict(list)
    
    def register_agent(self, agent: AgentProfile):
        """注册 Agent"""
        self.agents[agent.agent_id] = agent
        
        # 建立能力索引
        for capability in agent.capabilities:
            self.agent_capabilities[capability].append(agent.agent_id)
        
        logger.info(f"Agent registered: {agent.name} ({agent.agent_id})")
    
    def unregister_agent(self, agent_id: str):
        """注销 Agent"""
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            
            # 清理能力索引
            for capability in agent.capabilities:
                if agent_id in self.agent_capabilities[capability]:
                    self.agent_capabilities[capability].remove(agent_id)
            
            logger.info(f"Agent unregistered: {agent_id}")
    
    def find_agents_by_capability(self, capability: str) -> List[AgentProfile]:
        """根据能力查找 Agent"""
        agent_ids = self.agent_capabilities.get(capability, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]
    
    def find_best_agent(self, required_capability: str) -> Optional[AgentProfile]:
        """查找最适合的 Agent（考虑负载和成功率）"""
        candidates = self.find_agents_by_capability(required_capability)
        
        if not candidates:
            return None
        
        # 过滤可接受任务的 Agent
        available = [a for a in candidates if a.can_accept_task()]
        
        if not available:
            return None
        
        # 按成功率和负载排序
        best = max(available, key=lambda a: (a.success_rate, -a.current_load))
        
        return best
    
    def update_agent_load(self, agent_id: str, delta: int):
        """更新 Agent 负载"""
        if agent_id in self.agents:
            self.agents[agent_id].current_load += delta
            self.agents[agent_id].current_load = max(0, self.agents[agent_id].current_load)
    
    def update_success_rate(self, agent_id: str, success: bool):
        """更新成功率（移动平均）"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            alpha = 0.1  # 学习率
            new_rate = 1.0 if success else 0.0
            agent.success_rate = alpha * new_rate + (1 - alpha) * agent.success_rate
    
    def get_registry_stats(self) -> Dict:
        """获取注册中心统计"""
        return {
            "total_agents": len(self.agents),
            "agents_by_role": {
                role.value: sum(1 for a in self.agents.values() if a.role == role)
                for role in AgentRole
            },
            "total_capabilities": len(self.agent_capabilities),
            "average_load": sum(a.current_load for a in self.agents.values()) / max(len(self.agents), 1)
        }


class TaskScheduler:
    """任务调度器
    
    负责任务分配和依赖管理
    """
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.execution_queue: List[SubTask] = []
        self.completed_tasks: Dict[str, SubTask] = {}
    
    def schedule_workflow(self, workflow: WorkflowDefinition) -> List[str]:
        """
        调度工作流
        
        Args:
            workflow: 工作流定义
            
        Returns:
            执行顺序
        """
        # 拓扑排序（考虑依赖关系）
        execution_order = self._topological_sort(workflow.tasks)
        
        logger.info(f"Scheduled workflow '{workflow.name}': {len(execution_order)} tasks")
        
        return execution_order
    
    def _topological_sort(self, tasks: List[SubTask]) -> List[str]:
        """拓扑排序"""
        # 构建依赖图
        graph = {task.task_id: [] for task in tasks}
        in_degree = {task.task_id: 0 for task in tasks}
        
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in graph:
                    graph[dep_id].append(task.task_id)
                    in_degree[task.task_id] += 1
        
        # Kahn's algorithm
        queue = [tid for tid, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # 按优先级排序
            queue.sort(key=lambda tid: next(t.priority for t in tasks if t.task_id == tid), reverse=True)
            
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(tasks):
            raise ValueError("Circular dependency detected in workflow")
        
        return result
    
    def assign_task(self, task: SubTask, capability: str) -> bool:
        """
        分配任务给 Agent
        
        Args:
            task: 子任务
            capability: 所需能力
            
        Returns:
            是否成功分配
        """
        agent = self.registry.find_best_agent(capability)
        
        if not agent:
            logger.warning(f"No available agent for capability: {capability}")
            return False
        
        task.assigned_agent = agent.agent_id
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now(timezone.utc).isoformat()
        
        # 更新负载
        self.registry.update_agent_load(agent.agent_id, 1)
        
        logger.info(f"Task {task.task_id} assigned to {agent.name}")
        
        return True
    
    def complete_task(self, task_id: str, success: bool, output: Any = None, error: str = None):
        """完成任务"""
        # 找到任务
        task = None
        for t in self.execution_queue:
            if t.task_id == task_id:
                task = t
                break
        
        if not task:
            logger.warning(f"Task not found: {task_id}")
            return
        
        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        task.completed_at = datetime.now(timezone.utc).isoformat()
        task.output_data = output
        task.error = error
        
        # 计算执行时间
        if task.started_at:
            start = datetime.fromisoformat(task.started_at)
            end = datetime.fromisoformat(task.completed_at)
            task.execution_time = (end - start).total_seconds()
        
        # 更新 Agent 负载和成功率
        if task.assigned_agent:
            self.registry.update_agent_load(task.assigned_agent, -1)
            self.registry.update_success_rate(task.assigned_agent, success)
        
        # 移动到已完成列表
        self.completed_tasks[task_id] = task
        
        logger.info(f"Task {task_id} completed: {'success' if success else 'failed'}")
    
    def get_ready_tasks(self, workflow: WorkflowDefinition) -> List[SubTask]:
        """获取已就绪的任务（所有依赖已完成）"""
        completed_ids = set(self.completed_tasks.keys())
        ready = []
        
        for task in workflow.tasks:
            if task.status == TaskStatus.PENDING:
                if all(dep_id in completed_ids for dep_id in task.dependencies):
                    ready.append(task)
        
        # 按优先级排序
        ready.sort(key=lambda t: t.priority, reverse=True)
        
        return ready


class WorkflowOrchestrator:
    """工作流协调器
    
    整合 Agent 注册、任务调度、上下文管理的完整编排系统
    """
    
    def __init__(self):
        self.registry = AgentRegistry()
        self.scheduler = TaskScheduler(self.registry)
        self.contexts: Dict[str, ExecutionContext] = {}
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.execution_history: List[Dict] = []
    
    def create_workflow(self, name: str, description: str, tasks: List[Dict], 
                       execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL) -> str:
        """
        创建工作流
        
        Args:
            name: 工作流名称
            description: 描述
            tasks: 任务列表（字典格式）
            execution_mode: 执行模式
            
        Returns:
            工作流ID
        """
        workflow_id = f"workflow-{uuid.uuid4().hex[:8]}"
        
        # 转换任务格式
        subtasks = []
        for task_data in tasks:
            task = SubTask(
                task_id=task_data["id"],
                description=task_data["description"],
                dependencies=task_data.get("dependencies", []),
                priority=task_data.get("priority", 0),
                input_data=task_data.get("input_data", {})
            )
            subtasks.append(task)
        
        workflow = WorkflowDefinition(
            workflow_id=workflow_id,
            name=name,
            description=description,
            tasks=subtasks,
            execution_mode=execution_mode
        )
        
        self.workflows[workflow_id] = workflow
        
        logger.info(f"Workflow created: {name} ({workflow_id})")
        
        return workflow_id
    
    def execute_workflow(self, workflow_id: str, context: Dict = None) -> Dict:
        """
        执行工作流
        
        Args:
            workflow_id: 工作流ID
            context: 初始上下文
            
        Returns:
            执行结果
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        # 创建执行上下文
        context_id = f"context-{uuid.uuid4().hex[:8]}"
        exec_context = ExecutionContext(
            context_id=context_id,
            workflow_id=workflow_id,
            shared_data=context or {}
        )
        self.contexts[context_id] = exec_context
        
        # 记录执行历史
        execution_record = {
            "workflow_id": workflow_id,
            "context_id": context_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "running",
            "tasks_completed": 0,
            "tasks_failed": 0
        }
        
        try:
            # 调度工作流
            execution_order = self.scheduler.schedule_workflow(workflow)
            self.scheduler.execution_queue = workflow.tasks.copy()
            
            # 执行任务
            for task_id in execution_order:
                task = next(t for t in workflow.tasks if t.task_id == task_id)
                
                # 检查依赖
                ready_tasks = self.scheduler.get_ready_tasks(workflow)
                if task not in ready_tasks:
                    task.status = TaskStatus.BLOCKED
                    continue
                
                # 分配任务（简化：假设需要 "general" 能力）
                capability = task.input_data.get("required_capability", "general")
                if not self.scheduler.assign_task(task, capability):
                    task.status = TaskStatus.FAILED
                    task.error = "No available agent"
                    execution_record["tasks_failed"] += 1
                    continue
                
                # 模拟执行（实际应调用 Agent）
                success, output = self._execute_task(task, exec_context)
                
                # 完成任务
                self.scheduler.complete_task(task_id, success, output)
                
                if success:
                    execution_record["tasks_completed"] += 1
                    # 将结果存入上下文
                    exec_context.set_task_result(task_id, output)
                else:
                    execution_record["tasks_failed"] += 1
            
            # 执行完成
            execution_record["status"] = "completed"
            execution_record["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Workflow '{workflow.name}' completed: {execution_record['tasks_completed']}/{len(workflow.tasks)} tasks succeeded")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "context_id": context_id,
                "results": execution_record,
                "task_outputs": exec_context.task_results
            }
        
        except Exception as e:
            execution_record["status"] = "failed"
            execution_record["error"] = str(e)
            execution_record["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            logger.error(f"Workflow '{workflow.name}' failed: {e}")
            
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": str(e),
                "results": execution_record
            }
        
        finally:
            self.execution_history.append(execution_record)
    
    def _execute_task(self, task: SubTask, context: ExecutionContext) -> Tuple[bool, Any]:
        """
        执行单个任务（模拟）
        
        Args:
            task: 子任务
            context: 执行上下文
            
        Returns:
            (成功标志, 输出数据)
        """
        # 这里应该调用实际的 Agent
        # 目前使用模拟执行
        time.sleep(0.1)  # 模拟执行时间
        
        # 模拟成功
        output = {
            "task_id": task.task_id,
            "result": f"Completed: {task.description}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return True, output
    
    def get_orchestrator_status(self) -> Dict:
        """获取协调器状态"""
        return {
            "registry": self.registry.get_registry_stats(),
            "active_workflows": len(self.workflows),
            "active_contexts": len(self.contexts),
            "total_executions": len(self.execution_history),
            "recent_executions": self.execution_history[-5:] if self.execution_history else []
        }


def create_orchestrator() -> WorkflowOrchestrator:
    """工厂函数：创建协调器"""
    return WorkflowOrchestrator()


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("Multi-Agent Orchestrator 测试")
    print("="*60)
    
    orchestrator = create_orchestrator()
    
    # 注册 Agents
    print("\n📝 注册 Agents...")
    manager = AgentProfile(
        agent_id="mgr-001",
        name="Manager Agent",
        role=AgentRole.MANAGER,
        capabilities=["planning", "coordination", "task_decomposition"],
        max_concurrent_tasks=5
    )
    orchestrator.registry.register_agent(manager)
    
    expert1 = AgentProfile(
        agent_id="exp-001",
        name="Code Expert",
        role=AgentRole.EXPERT,
        capabilities=["coding", "code_review", "testing"],
        specialization="Python development"
    )
    orchestrator.registry.register_agent(expert1)
    
    expert2 = AgentProfile(
        agent_id="exp-002",
        name="Research Expert",
        role=AgentRole.EXPERT,
        capabilities=["research", "summarization", "fact_checking"],
        specialization="Information retrieval"
    )
    orchestrator.registry.register_agent(expert2)
    
    # 创建工作流
    print("\n🔧 创建工作流...")
    workflow_id = orchestrator.create_workflow(
        name="Feature Development",
        description="Complete feature development workflow",
        tasks=[
            {
                "id": "task-research",
                "description": "Research requirements and best practices",
                "dependencies": [],
                "priority": 10,
                "input_data": {"required_capability": "research"}
            },
            {
                "id": "task-design",
                "description": "Design architecture and API",
                "dependencies": ["task-research"],
                "priority": 9,
                "input_data": {"required_capability": "planning"}
            },
            {
                "id": "task-coding",
                "description": "Implement the feature",
                "dependencies": ["task-design"],
                "priority": 8,
                "input_data": {"required_capability": "coding"}
            },
            {
                "id": "task-testing",
                "description": "Write and run tests",
                "dependencies": ["task-coding"],
                "priority": 7,
                "input_data": {"required_capability": "testing"}
            }
        ]
    )
    print(f"   工作流ID: {workflow_id}")
    
    # 执行工作流
    print("\n▶️  执行工作流...")
    result = orchestrator.execute_workflow(workflow_id)
    
    print(f"\n✅ 执行结果:")
    print(f"   成功: {result['success']}")
    print(f"   完成任务数: {result['results']['tasks_completed']}")
    print(f"   失败任务数: {result['results']['tasks_failed']}")
    
    # 获取状态
    print("\n📊 协调器状态:")
    status = orchestrator.get_orchestrator_status()
    print(json.dumps(status, indent=2, ensure_ascii=False, default=str))
    
    print("\n✅ 测试完成！")
