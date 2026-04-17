#!/usr/bin/env python3
"""
Advanced Planner - 高级规划器

基于 Tree of Thoughts (ToT) 的多路径探索规划系统
支持 BFS/DFS 搜索策略，动态任务分解和调度

参考社区最佳实践:
- Tree of Thoughts (Yao et al., 2023)
- Algorithm of Thoughts (AoT)
- Monte Carlo Tree Search (MCTS) for planning
"""

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)


class SearchStrategy(Enum):
    """搜索策略"""
    BFS = "bfs"  # 广度优先搜索
    DFS = "dfs"  # 深度优先搜索
    MCTS = "mcts"  # 蒙特卡洛树搜索（预留）
    BEAM = "beam_search"  # Beam Search（预留）


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"  # 被依赖阻塞


@dataclass
class ThoughtNode:
    """思维节点 - ToT 核心数据结构"""
    node_id: str
    state: str  # 当前思维状态
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    depth: int = 0
    score: float = 0.0  # 评估分数
    visits: int = 0  # 访问次数（用于 MCTS）
    value: float = 0.0  # 价值估计（用于 MCTS）
    is_terminal: bool = False  # 是否为终止节点
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class SubTask:
    """子任务"""
    task_id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)  # 依赖的任务ID
    priority: int = 0  # 优先级 (0-10, 越高越优先)
    estimated_time: float = 0.0  # 预估时间（秒）
    actual_time: float = 0.0  # 实际耗时
    result: Any = None
    error: Optional[str] = None
    assigned_agent: Optional[str] = None  # 分配的 agent
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class Plan:
    """执行计划"""
    plan_id: str
    goal: str  # 最终目标
    subtasks: List[SubTask] = field(default_factory=list)
    search_strategy: SearchStrategy = SearchStrategy.BFS
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    execution_order: List[str] = field(default_factory=list)  # 执行顺序
    thought_tree: Dict[str, ThoughtNode] = field(default_factory=dict)  # 思维树
    current_node_id: Optional[str] = None
    best_path: List[str] = field(default_factory=list)  # 最优路径
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: str = "draft"  # draft/executing/completed/failed
    
    def get_ready_tasks(self) -> List[SubTask]:
        """获取已就绪的任务（所有依赖已完成）"""
        completed_ids = {
            t.task_id for t in self.subtasks 
            if t.status == TaskStatus.COMPLETED
        }
        
        ready = []
        for task in self.subtasks:
            if task.status == TaskStatus.PENDING:
                # 检查所有依赖是否已完成
                if all(dep_id in completed_ids for dep_id in task.dependencies):
                    ready.append(task)
        
        # 按优先级排序
        ready.sort(key=lambda t: t.priority, reverse=True)
        return ready


class ThoughtGenerator:
    """思维生成器
    
    根据当前状态生成多个可能的下一步思维
    """
    
    def __init__(self, branch_factor: int = 3):
        """
        Args:
            branch_factor: 每个节点的分支数
        """
        self.branch_factor = branch_factor
    
    def generate(self, current_state: str, context: Dict = None) -> List[str]:
        """
        生成多个可能的下一步思维
        
        Args:
            current_state: 当前思维状态
            context: 上下文信息
            
        Returns:
            候选思维列表
        """
        # Mock 实现（Phase 3），真实实现需要调用 LLM
        # TODO: 集成 LLM API 生成多样化的思维路径
        
        candidates = self._mock_generate(current_state, context or {})
        return candidates[:self.branch_factor]
    
    def _mock_generate(self, state: str, context: Dict) -> List[str]:
        """Mock 思维生成（用于测试）"""
        # 简单的启发式生成
        if "task" in state.lower():
            return [
                f"{state} → 分解为子任务",
                f"{state} → 并行执行",
                f"{state} → 串行执行"
            ]
        elif "code" in state.lower():
            return [
                f"{state} → 编写单元测试",
                f"{state} → 实现核心逻辑",
                f"{state} → 优化性能"
            ]
        else:
            return [
                f"{state} → 方案A",
                f"{state} → 方案B",
                f"{state} → 方案C"
            ]


class StateEvaluator:
    """状态评估器
    
    评估思维节点的质量和可行性
    """
    
    def __init__(self):
        self.evaluation_cache = {}
    
    def evaluate(self, state: str, context: Dict = None) -> float:
        """
        评估状态质量
        
        Args:
            state: 思维状态
            context: 上下文信息
            
        Returns:
            质量分数 (0.0 - 1.0)
        """
        # Mock 实现（Phase 3），真实实现可以使用 LLM 或规则引擎
        score = self._mock_evaluate(state, context or {})
        return max(0.0, min(1.0, score))
    
    def _mock_evaluate(self, state: str, context: Dict) -> float:
        """Mock 评估（用于测试）"""
        # 简单的启发式评估
        base_score = 0.5
        
        # 如果包含关键词，提高分数
        positive_keywords = ["complete", "success", "optimal", "efficient"]
        negative_keywords = ["error", "fail", "stuck", "block"]
        
        state_lower = state.lower()
        
        for keyword in positive_keywords:
            if keyword in state_lower:
                base_score += 0.1
        
        for keyword in negative_keywords:
            if keyword in state_lower:
                base_score -= 0.15
        
        return base_score


class TaskDecomposer:
    """任务分解器
    
    将复杂目标分解为可执行的子任务
    """
    
    def __init__(self):
        self.decomposition_templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """加载分解模板"""
        return {
            "code_development": [
                "需求分析",
                "设计架构",
                "编写代码",
                "单元测试",
                "集成测试",
                "文档编写"
            ],
            "data_analysis": [
                "数据收集",
                "数据清洗",
                "特征工程",
                "模型训练",
                "结果验证",
                "报告生成"
            ],
            "general_task": [
                "任务理解",
                "方案设计",
                "执行实施",
                "结果验证",
                "总结反馈"
            ]
        }
    
    def decompose(self, goal: str, max_subtasks: int = 10) -> List[SubTask]:
        """
        分解目标为子任务
        
        Args:
            goal: 最终目标
            max_subtasks: 最大子任务数
            
        Returns:
            子任务列表
        """
        # Mock 实现（Phase 3），真实实现需要 LLM
        subtasks = self._mock_decompose(goal, max_subtasks)
        return subtasks
    
    def _mock_decompose(self, goal: str, max_subtasks: int) -> List[SubTask]:
        """Mock 任务分解（用于测试）"""
        # 根据目标类型选择模板
        if "code" in goal.lower() or "开发" in goal:
            template = self.decomposition_templates["code_development"]
        elif "data" in goal.lower() or "分析" in goal:
            template = self.decomposition_templates["data_analysis"]
        else:
            template = self.decomposition_templates["general_task"]
        
        # 创建子任务
        subtasks = []
        for i, desc in enumerate(template[:max_subtasks]):
            task = SubTask(
                task_id=f"task-{i+1:03d}",
                description=desc,
                priority=max_subtasks - i,  # 前面的任务优先级更高
                dependencies=[f"task-{j:03d}" for j in range(1, i+1)] if i > 0 else []
            )
            subtasks.append(task)
        
        return subtasks


class DynamicScheduler:
    """动态调度器
    
    根据任务状态和依赖关系动态调整执行顺序
    """
    
    def __init__(self, strategy: SearchStrategy = SearchStrategy.BFS):
        self.strategy = strategy
        self.execution_queue: deque = deque()
    
    def schedule(self, plan: Plan) -> List[str]:
        """
        调度任务执行顺序
        
        Args:
            plan: 执行计划
            
        Returns:
            执行顺序（任务ID列表）
        """
        if self.strategy == SearchStrategy.BFS:
            return self._bfs_schedule(plan)
        elif self.strategy == SearchStrategy.DFS:
            return self._dfs_schedule(plan)
        else:
            raise ValueError(f"Unsupported strategy: {self.strategy}")
    
    def _bfs_schedule(self, plan: Plan) -> List[str]:
        """广度优先调度"""
        order = []
        visited = set()
        queue = deque([t for t in plan.subtasks if not t.dependencies])
        
        while queue:
            task = queue.popleft()
            if task.task_id not in visited:
                visited.add(task.task_id)
                order.append(task.task_id)
                
                # 添加后续任务
                for next_task in plan.subtasks:
                    if task.task_id in next_task.dependencies:
                        if next_task.task_id not in visited:
                            queue.append(next_task)
        
        return order
    
    def _dfs_schedule(self, plan: Plan) -> List[str]:
        """深度优先调度"""
        order = []
        visited = set()
        
        def dfs(task_id: str):
            if task_id in visited:
                return
            visited.add(task_id)
            
            task = next((t for t in plan.subtasks if t.task_id == task_id), None)
            if task:
                # 先处理依赖
                for dep_id in task.dependencies:
                    dfs(dep_id)
                order.append(task_id)
        
        # 从没有依赖的任务开始
        for task in plan.subtasks:
            if not task.dependencies:
                dfs(task.task_id)
        
        return order
    
    def get_next_task(self, plan: Plan) -> Optional[SubTask]:
        """获取下一个可执行的任务"""
        ready_tasks = plan.get_ready_tasks()
        return ready_tasks[0] if ready_tasks else None


class AdvancedPlanner:
    """高级规划器
    
    整合 ToT、任务分解、动态调度的完整规划系统
    """
    
    def __init__(
        self,
        search_strategy: SearchStrategy = SearchStrategy.BFS,
        max_depth: int = 5,
        beam_width: int = 3,
        branch_factor: int = 3
    ):
        """
        Args:
            search_strategy: 搜索策略
            max_depth: 最大搜索深度
            beam_width: Beam width (BFS)
            branch_factor: 分支因子
        """
        self.search_strategy = search_strategy
        self.max_depth = max_depth
        self.beam_width = beam_width
        
        self.thought_generator = ThoughtGenerator(branch_factor)
        self.state_evaluator = StateEvaluator()
        self.task_decomposer = TaskDecomposer()
        self.scheduler = DynamicScheduler(search_strategy)
        
        self.plans: Dict[str, Plan] = {}
    
    def create_plan(self, goal: str, context: Dict = None) -> Plan:
        """
        创建执行计划
        
        Args:
            goal: 最终目标
            context: 上下文信息
            
        Returns:
            执行计划
        """
        plan_id = f"plan-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        
        # Step 1: 任务分解
        logger.info(f"Decomposing goal: {goal}")
        subtasks = self.task_decomposer.decompose(goal)
        
        # Step 2: 构建思维树（ToT）
        logger.info("Building thought tree...")
        thought_tree = self._build_thought_tree(goal, context or {})
        
        # Step 3: 创建计划
        plan = Plan(
            plan_id=plan_id,
            goal=goal,
            subtasks=subtasks,
            search_strategy=self.search_strategy,
            total_steps=len(subtasks),
            thought_tree=thought_tree
        )
        
        # Step 4: 调度执行顺序
        execution_order = self.scheduler.schedule(plan)
        plan.execution_order = execution_order
        
        self.plans[plan_id] = plan
        
        logger.info(f"Plan created: {plan_id} with {len(subtasks)} subtasks")
        return plan
    
    def _build_thought_tree(self, root_state: str, context: Dict) -> Dict[str, ThoughtNode]:
        """
        构建思维树
        
        Args:
            root_state: 根节点状态
            context: 上下文信息
            
        Returns:
            思维树字典
        """
        tree = {}
        node_counter = [0]
        
        def create_node(state: str, parent_id: Optional[str], depth: int) -> str:
            node_id = f"node-{node_counter[0]}"
            node_counter[0] += 1
            
            node = ThoughtNode(
                node_id=node_id,
                state=state,
                parent_id=parent_id,
                depth=depth,
                score=self.state_evaluator.evaluate(state, context)
            )
            
            tree[node_id] = node
            
            # 递归生成子节点
            if depth < self.max_depth:
                children_states = self.thought_generator.generate(state, context)
                for child_state in children_states:
                    child_id = create_node(child_state, node_id, depth + 1)
                    node.children.append(child_id)
            
            return node_id
        
        # 创建根节点
        create_node(root_state, None, 0)
        
        return tree
    
    def execute_plan(self, plan_id: str, task_executor: Callable) -> Dict:
        """
        执行计划
        
        Args:
            plan_id: 计划ID
            task_executor: 任务执行函数 (task: SubTask) -> result
            
        Returns:
            执行结果
        """
        plan = self.plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan not found: {plan_id}")
        
        plan.status = "executing"
        plan.start_time = datetime.now(timezone.utc).isoformat()
        
        logger.info(f"Executing plan: {plan_id}")
        
        start_time = time.time()
        
        try:
            # 按调度顺序执行任务
            for task_id in plan.execution_order:
                task = next((t for t in plan.subtasks if t.task_id == task_id), None)
                if not task:
                    continue
                
                # 检查依赖
                if not self._check_dependencies(task, plan):
                    task.status = TaskStatus.BLOCKED
                    plan.failed_steps += 1
                    continue
                
                # 执行任务
                logger.info(f"Executing task: {task.description}")
                task.status = TaskStatus.IN_PROGRESS
                task.started_at = datetime.now(timezone.utc).isoformat()
                
                task_start = time.time()
                try:
                    result = task_executor(task)
                    task.result = result
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now(timezone.utc).isoformat()
                    plan.completed_steps += 1
                    
                except Exception as e:
                    task.error = str(e)
                    task.status = TaskStatus.FAILED
                    plan.failed_steps += 1
                    logger.error(f"Task failed: {e}")
                
                task.actual_time = time.time() - task_start
            
            plan.status = "completed"
            plan.end_time = datetime.now(timezone.utc).isoformat()
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "plan_id": plan_id,
                "total_tasks": len(plan.subtasks),
                "completed_tasks": plan.completed_steps,
                "failed_tasks": plan.failed_steps,
                "execution_time": round(execution_time, 3),
                "status": plan.status
            }
        
        except Exception as e:
            plan.status = "failed"
            plan.end_time = datetime.now(timezone.utc).isoformat()
            
            return {
                "success": False,
                "plan_id": plan_id,
                "error": str(e),
                "status": plan.status
            }
    
    def _check_dependencies(self, task: SubTask, plan: Plan) -> bool:
        """检查任务依赖是否满足"""
        for dep_id in task.dependencies:
            dep_task = next((t for t in plan.subtasks if t.task_id == dep_id), None)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    def get_plan_status(self, plan_id: str) -> Dict:
        """获取计划状态"""
        plan = self.plans.get(plan_id)
        if not plan:
            return {"error": f"Plan not found: {plan_id}"}
        
        return {
            "plan_id": plan.plan_id,
            "goal": plan.goal,
            "status": plan.status,
            "total_steps": plan.total_steps,
            "completed_steps": plan.completed_steps,
            "failed_steps": plan.failed_steps,
            "progress": round(plan.completed_steps / plan.total_steps * 100, 2) if plan.total_steps > 0 else 0,
            "subtasks": [asdict(t) for t in plan.subtasks],
            "thought_tree_size": len(plan.thought_tree)
        }


def create_advanced_planner(config: Optional[Dict] = None) -> AdvancedPlanner:
    """工厂函数：创建高级规划器"""
    if config:
        return AdvancedPlanner(**config)
    return AdvancedPlanner()


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("Advanced Planner 测试")
    print("="*60)
    
    planner = create_advanced_planner({
        "search_strategy": SearchStrategy.BFS,
        "max_depth": 3,
        "beam_width": 3,
        "branch_factor": 3
    })
    
    # 创建计划
    goal = "开发一个用户管理系统"
    plan = planner.create_plan(goal)
    
    print(f"\n📋 计划 ID: {plan.plan_id}")
    print(f"🎯 目标: {plan.goal}")
    print(f"📊 子任务数: {len(plan.subtasks)}")
    print(f"🔍 思维树节点数: {len(plan.thought_tree)}")
    print(f"📝 执行顺序: {plan.execution_order}")
    
    print(f"\n📌 子任务详情:")
    for task in plan.subtasks:
        deps = f" (依赖: {', '.join(task.dependencies)})" if task.dependencies else ""
        print(f"   [{task.task_id}] {task.description}{deps} - 优先级: {task.priority}")
    
    # 模拟执行
    def mock_executor(task: SubTask):
        time.sleep(0.1)  # 模拟执行时间
        return f"Result for {task.description}"
    
    print(f"\n⚙️  执行计划...")
    result = planner.execute_plan(plan.plan_id, mock_executor)
    
    print(f"\n✅ 执行结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 获取状态
    status = planner.get_plan_status(plan.plan_id)
    print(f"\n📈 计划状态:")
    print(f"   进度: {status['progress']}%")
    print(f"   完成: {status['completed_steps']}/{status['total_steps']}")
