#!/usr/bin/env python3
"""
AI Agent Advanced Collaboration & Swarm Intelligence System - AI Agent 高级协作与群体智能系统

共识机制、群体决策、动态分工、辩论协商
实现生产级多智能体协作的高级框架

参考社区最佳实践:
- Consensus mechanisms for multi-agent systems
- Swarm intelligence and collective decision-making
- Dynamic role assignment and task decomposition
- Debate and negotiation protocols
- Emergent behavior in agent swarms
"""

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import uuid
import random
import statistics

logger = logging.getLogger(__name__)


class ConsensusStrategy(Enum):
    """共识策略"""
    AVERAGE = "average"  # 平均共识
    MAJORITY_VOTE = "majority_vote"  # 多数投票
    WEIGHTED_VOTE = "weighted_vote"  # 加权投票
    DEBATE = "debate"  # 辩论达成共识
    LEADER_BASED = "leader_based"  # 基于领导者


class AgentRole(Enum):
    """Agent 角色"""
    MANAGER = "manager"  # 管理者
    RESEARCHER = "researcher"  # 研究员
    WRITER = "writer"  # 写手
    REVIEWER = "reviewer"  # 审核者
    CODER = "coder"  # 程序员
    TESTER = "tester"  # 测试员
    ANALYST = "analyst"  # 分析师


class CommunicationPattern(Enum):
    """通信模式"""
    BROADCAST = "broadcast"  # 广播
    POINT_TO_POINT = "point_to_point"  # 点对点
    PUBLISH_SUBSCRIBE = "publish_subscribe"  # 发布订阅
    BLACKBOARD = "blackboard"  # 黑板模式


@dataclass
class AgentOpinion:
    """Agent 观点"""
    agent_id: str
    opinion_value: float  # 数值型观点 (0-1)
    confidence: float  # 置信度 (0-1)
    reasoning: str  # 推理过程
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ConsensusResult:
    """共识结果"""
    consensus_id: str
    strategy: ConsensusStrategy
    agreed_value: float
    confidence: float
    participating_agents: int
    rounds_needed: int
    agent_opinions: List[AgentOpinion] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class TaskAssignment:
    """任务分配"""
    assignment_id: str
    task_id: str
    agent_id: str
    role: AgentRole
    priority: int  # 1-10
    deadline: Optional[str] = None
    status: str = "assigned"  # assigned/in_progress/completed/failed
    assigned_at: str = ""
    
    def __post_init__(self):
        if not self.assigned_at:
            self.assigned_at = datetime.now(timezone.utc).isoformat()


@dataclass
class SwarmState:
    """群体状态"""
    swarm_id: str
    total_agents: int
    active_agents: int
    task_completion_rate: float
    average_confidence: float
    communication_overhead: float  # 通信开销
    emergent_behaviors: List[str] = field(default_factory=list)
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.updated_at:
            self.updated_at = datetime.now(timezone.utc).isoformat()


class ConsensusEngine:
    """共识引擎
    
    实现多种共识达成机制
    """
    
    def __init__(self):
        self.consensus_history: List[ConsensusResult] = []
    
    def reach_consensus(
        self,
        opinions: List[AgentOpinion],
        strategy: ConsensusStrategy = ConsensusStrategy.AVERAGE,
        max_rounds: int = 10,
        threshold: float = 0.8
    ) -> ConsensusResult:
        """
        达成共识
        
        Args:
            opinions: Agent 观点列表
            strategy: 共识策略
            max_rounds: 最大轮数
            threshold: 共识阈值
            
        Returns:
            共识结果
        """
        logger.info(f"Reaching consensus with {len(opinions)} agents using {strategy.value}")
        
        if not opinions:
            raise ValueError("No opinions provided")
        
        # 根据策略执行共识
        if strategy == ConsensusStrategy.AVERAGE:
            result = self._average_consensus(opinions)
        elif strategy == ConsensusStrategy.MAJORITY_VOTE:
            result = self._majority_vote_consensus(opinions, threshold)
        elif strategy == ConsensusStrategy.WEIGHTED_VOTE:
            result = self._weighted_vote_consensus(opinions)
        elif strategy == ConsensusStrategy.DEBATE:
            result = self._debate_consensus(opinions, max_rounds)
        elif strategy == ConsensusStrategy.LEADER_BASED:
            result = self._leader_based_consensus(opinions)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # 记录历史
        self.consensus_history.append(result)
        
        logger.info(f"Consensus reached: value={result.agreed_value:.2f}, confidence={result.confidence:.2f}")
        
        return result
    
    def _average_consensus(self, opinions: List[AgentOpinion]) -> ConsensusResult:
        """平均共识"""
        values = [op.opinion_value for op in opinions]
        avg_value = statistics.mean(values)
        
        # 计算置信度（基于意见的一致性）
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        confidence = max(0.0, 1.0 - std_dev)
        
        return ConsensusResult(
            consensus_id=str(uuid.uuid4()),
            strategy=ConsensusStrategy.AVERAGE,
            agreed_value=round(avg_value, 4),
            confidence=round(confidence, 4),
            participating_agents=len(opinions),
            rounds_needed=1,
            agent_opinions=opinions
        )
    
    def _majority_vote_consensus(
        self,
        opinions: List[AgentOpinion],
        threshold: float
    ) -> ConsensusResult:
        """多数投票共识"""
        # 将观点分组（四舍五入到最近的0.1）
        groups: Dict[float, List[AgentOpinion]] = {}
        
        for op in opinions:
            rounded = round(op.opinion_value, 1)
            if rounded not in groups:
                groups[rounded] = []
            groups[rounded].append(op)
        
        # 找到最大的组
        majority_value = max(groups.keys(), key=lambda k: len(groups[k]))
        majority_group = groups[majority_value]
        
        # 检查是否达到阈值
        support_ratio = len(majority_group) / len(opinions)
        confidence = support_ratio if support_ratio >= threshold else 0.0
        
        return ConsensusResult(
            consensus_id=str(uuid.uuid4()),
            strategy=ConsensusStrategy.MAJORITY_VOTE,
            agreed_value=majority_value,
            confidence=round(confidence, 4),
            participating_agents=len(opinions),
            rounds_needed=1,
            agent_opinions=opinions,
            metadata={"support_ratio": round(support_ratio, 4)}
        )
    
    def _weighted_vote_consensus(self, opinions: List[AgentOpinion]) -> ConsensusResult:
        """加权投票共识"""
        # 使用置信度作为权重
        total_weight = sum(op.confidence for op in opinions)
        
        if total_weight == 0:
            # 如果所有置信度都是0，退化为平均
            return self._average_consensus(opinions)
        
        weighted_sum = sum(op.opinion_value * op.confidence for op in opinions)
        weighted_avg = weighted_sum / total_weight
        
        # 置信度基于加权一致性
        weighted_variance = sum(
            op.confidence * (op.opinion_value - weighted_avg) ** 2
            for op in opinions
        ) / total_weight
        
        confidence = max(0.0, 1.0 - weighted_variance)
        
        return ConsensusResult(
            consensus_id=str(uuid.uuid4()),
            strategy=ConsensusStrategy.WEIGHTED_VOTE,
            agreed_value=round(weighted_avg, 4),
            confidence=round(confidence, 4),
            participating_agents=len(opinions),
            rounds_needed=1,
            agent_opinions=opinions
        )
    
    def _debate_consensus(
        self,
        opinions: List[AgentOpinion],
        max_rounds: int
    ) -> ConsensusResult:
        """辩论共识（模拟多轮辩论）"""
        current_opinions = opinions.copy()
        rounds = 0
        
        for round_num in range(max_rounds):
            rounds = round_num + 1
            
            # 模拟辩论：Agents 调整观点向群体平均值靠拢
            avg_value = statistics.mean([op.opinion_value for op in current_opinions])
            
            adjusted_opinions = []
            for op in current_opinions:
                # 每个 Agent 向平均值移动一定比例
                adjustment = (avg_value - op.opinion_value) * 0.3
                new_value = op.opinion_value + adjustment
                
                # 保持边界
                new_value = max(0.0, min(1.0, new_value))
                
                adjusted_opinions.append(AgentOpinion(
                    agent_id=op.agent_id,
                    opinion_value=new_value,
                    confidence=op.confidence,
                    reasoning=f"Round {rounds}: Adjusted toward group average"
                ))
            
            current_opinions = adjusted_opinions
            
            # 检查是否达成共识（标准差小于阈值）
            std_dev = statistics.stdev([op.opinion_value for op in current_opinions])
            
            if std_dev < 0.05:  # 共识阈值
                break
        
        # 最终共识值
        final_value = statistics.mean([op.opinion_value for op in current_opinions])
        final_std = statistics.stdev([op.opinion_value for op in current_opinions]) if len(current_opinions) > 1 else 0
        confidence = max(0.0, 1.0 - final_std)
        
        return ConsensusResult(
            consensus_id=str(uuid.uuid4()),
            strategy=ConsensusStrategy.DEBATE,
            agreed_value=round(final_value, 4),
            confidence=round(confidence, 4),
            participating_agents=len(opinions),
            rounds_needed=rounds,
            agent_opinions=current_opinions
        )
    
    def _leader_based_consensus(self, opinions: List[AgentOpinion]) -> ConsensusResult:
        """基于领导者的共识"""
        if not opinions:
            raise ValueError("No opinions provided")
        
        # 选择置信度最高的 Agent 作为领导者
        leader = max(opinions, key=lambda op: op.confidence)
        
        return ConsensusResult(
            consensus_id=str(uuid.uuid4()),
            strategy=ConsensusStrategy.LEADER_BASED,
            agreed_value=leader.opinion_value,
            confidence=leader.confidence,
            participating_agents=len(opinions),
            rounds_needed=1,
            agent_opinions=opinions,
            metadata={"leader_id": leader.agent_id}
        )


class SwarmIntelligence:
    """群体智能
    
    实现群体行为和涌现特性
    """
    
    def __init__(self):
        self.swarm_states: List[SwarmState] = []
    
    def analyze_swarm_behavior(
        self,
        agents: List[Dict],
        tasks: List[Dict],
        communications: List[Dict]
    ) -> SwarmState:
        """
        分析群体行为
        
        Args:
            agents: Agent 列表
            tasks: 任务列表
            communications: 通信记录
            
        Returns:
            群体状态
        """
        total_agents = len(agents)
        active_agents = sum(1 for a in agents if a.get("status") == "active")
        
        # 计算任务完成率
        completed_tasks = sum(1 for t in tasks if t.get("status") == "completed")
        completion_rate = completed_tasks / len(tasks) if tasks else 0.0
        
        # 计算平均置信度
        confidences = [a.get("confidence", 0.5) for a in agents]
        avg_confidence = statistics.mean(confidences) if confidences else 0.5
        
        # 计算通信开销
        comm_overhead = len(communications) / max(total_agents, 1)
        
        # 检测涌现行为
        emergent_behaviors = self._detect_emergent_behaviors(agents, tasks, communications)
        
        state = SwarmState(
            swarm_id=str(uuid.uuid4()),
            total_agents=total_agents,
            active_agents=active_agents,
            task_completion_rate=round(completion_rate, 4),
            average_confidence=round(avg_confidence, 4),
            communication_overhead=round(comm_overhead, 4),
            emergent_behaviors=emergent_behaviors
        )
        
        self.swarm_states.append(state)
        
        logger.info(f"Swarm analyzed: {active_agents}/{total_agents} active, {completion_rate*100:.1f}% completion")
        
        return state
    
    def _detect_emergent_behaviors(
        self,
        agents: List[Dict],
        tasks: List[Dict],
        communications: List[Dict]
    ) -> List[str]:
        """检测涌现行为"""
        behaviors = []
        
        # 1. 自组织：Agents 自发形成协作模式
        if len(communications) > len(agents) * 2:
            behaviors.append("self_organization")
        
        # 2. 分工专业化：Agents 专注于特定类型任务
        task_types = {}
        for comm in communications:
            task_type = comm.get("task_type", "unknown")
            if task_type not in task_types:
                task_types[task_type] = 0
            task_types[task_type] += 1
        
        if len(task_types) > 1:
            dominant_type = max(task_types.keys(), key=lambda k: task_types[k])
            if task_types[dominant_type] > len(communications) * 0.6:
                behaviors.append("specialization")
        
        # 3. 集体智慧：群体表现优于个体
        avg_agent_performance = statistics.mean([a.get("performance", 0.5) for a in agents]) if agents else 0.5
        completed = sum(1 for t in tasks if t.get("status") == "completed")
        if completed > len(tasks) * 0.8 and avg_agent_performance < 0.7:
            behaviors.append("collective_intelligence")
        
        # 4. 适应性：群体快速响应变化
        recent_comms = [c for c in communications if c.get("timestamp", "") > ""]
        if len(recent_comms) > len(communications) * 0.5:
            behaviors.append("adaptability")
        
        return behaviors


class DynamicTaskAllocator:
    """动态任务分配器
    
    基于 Agent 能力和负载智能分配任务
    """
    
    def __init__(self):
        self.assignments: List[TaskAssignment] = []
        self.agent_workload: Dict[str, int] = {}
    
    def allocate_tasks(
        self,
        tasks: List[Dict],
        agents: List[Dict],
        strategy: str = "balanced"
    ) -> List[TaskAssignment]:
        """
        分配任务
        
        Args:
            tasks: 任务列表
            agents: Agent 列表
            strategy: 分配策略 (balanced/skill_based/priority_based)
            
        Returns:
            任务分配列表
        """
        assignments = []
        
        # 初始化工作量
        for agent in agents:
            agent_id = agent["id"]
            if agent_id not in self.agent_workload:
                self.agent_workload[agent_id] = 0
        
        for task in tasks:
            # 选择最合适的 Agent
            best_agent = self._select_best_agent(task, agents, strategy)
            
            if best_agent:
                assignment = TaskAssignment(
                    assignment_id=str(uuid.uuid4()),
                    task_id=task["id"],
                    agent_id=best_agent["id"],
                    role=AgentRole(best_agent.get("role", "researcher")),
                    priority=task.get("priority", 5),
                    deadline=task.get("deadline"),
                    status="assigned"
                )
                
                assignments.append(assignment)
                self.assignments.append(assignment)
                
                # 更新工作量
                self.agent_workload[best_agent["id"]] += 1
        
        logger.info(f"Allocated {len(assignments)} tasks to {len(set(a.agent_id for a in assignments))} agents")
        
        return assignments
    
    def _select_best_agent(
        self,
        task: Dict,
        agents: List[Dict],
        strategy: str
    ) -> Optional[Dict]:
        """选择最佳 Agent"""
        if not agents:
            return None
        
        if strategy == "balanced":
            # 选择工作量最少的 Agent
            return min(agents, key=lambda a: self.agent_workload.get(a["id"], 0))
        
        elif strategy == "skill_based":
            # 基于技能匹配
            required_skill = task.get("required_skill")
            candidates = [a for a in agents if a.get("skills", []).includes(required_skill)]
            
            if candidates:
                return min(candidates, key=lambda a: self.agent_workload.get(a["id"], 0))
            
            # 如果没有匹配的，退回平衡策略
            return min(agents, key=lambda a: self.agent_workload.get(a["id"], 0))
        
        elif strategy == "priority_based":
            # 高优先级任务给高性能 Agent
            task_priority = task.get("priority", 5)
            
            if task_priority >= 8:
                # 高优先级：选择性能最好的
                return max(agents, key=lambda a: a.get("performance", 0.5))
            else:
                # 普通优先级：平衡负载
                return min(agents, key=lambda a: self.agent_workload.get(a["id"], 0))
        
        else:
            # 默认：随机选择
            return random.choice(agents)


class CollaborationOrchestrator:
    """协作协调器
    
    整合共识、群体智能、任务分配的完整系统
    """
    
    def __init__(self):
        self.consensus_engine = ConsensusEngine()
        self.swarm_intelligence = SwarmIntelligence()
        self.task_allocator = DynamicTaskAllocator()
        self.collaboration_sessions: List[Dict] = []
    
    def start_collaboration_session(
        self,
        session_name: str,
        agents: List[Dict],
        tasks: List[Dict],
        consensus_strategy: ConsensusStrategy = ConsensusStrategy.AVERAGE
    ) -> Dict:
        """
        启动协作会话
        
        Args:
            session_name: 会话名称
            agents: Agent 列表
            tasks: 任务列表
            consensus_strategy: 共识策略
            
        Returns:
            会话结果
        """
        logger.info(f"Starting collaboration session: {session_name}")
        
        session_id = str(uuid.uuid4())
        
        # Step 1: 分配任务
        assignments = self.task_allocator.allocate_tasks(tasks, agents, strategy="balanced")
        
        # Step 2: 模拟任务执行
        completed_tasks = self._simulate_task_execution(assignments, agents)
        
        # Step 3: 收集观点并达成共识
        opinions = self._collect_agent_opinions(agents, completed_tasks)
        
        if opinions:
            consensus = self.consensus_engine.reach_consensus(
                opinions=opinions,
                strategy=consensus_strategy
            )
        else:
            consensus = None
        
        # Step 4: 分析群体行为
        communications = self._generate_communication_log(assignments)
        swarm_state = self.swarm_intelligence.analyze_swarm_behavior(
            agents=agents,
            tasks=completed_tasks,
            communications=communications
        )
        
        # 记录会话
        session_result = {
            "session_id": session_id,
            "session_name": session_name,
            "total_agents": len(agents),
            "total_tasks": len(tasks),
            "assignments": [asdict(a) for a in assignments],
            "completed_tasks": len(completed_tasks),
            "consensus": asdict(consensus) if consensus else None,
            "swarm_state": asdict(swarm_state),
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.collaboration_sessions.append(session_result)
        
        logger.info(f"Collaboration session completed: {session_id}")
        
        return session_result
    
    def _simulate_task_execution(
        self,
        assignments: List[TaskAssignment],
        agents: List[Dict]
    ) -> List[Dict]:
        """模拟任务执行"""
        completed_tasks = []
        
        for assignment in assignments:
            # 模拟执行（成功率基于 Agent 性能）
            agent = next((a for a in agents if a["id"] == assignment.agent_id), None)
            
            if agent:
                success_rate = agent.get("performance", 0.8)
                is_success = random.random() < success_rate
                
                completed_tasks.append({
                    "id": assignment.task_id,
                    "assigned_to": assignment.agent_id,
                    "status": "completed" if is_success else "failed",
                    "quality": random.uniform(0.6, 1.0) if is_success else 0.0
                })
        
        return completed_tasks
    
    def _collect_agent_opinions(
        self,
        agents: List[Dict],
        tasks: List[Dict]
    ) -> List[AgentOpinion]:
        """收集 Agent 观点"""
        opinions = []
        
        for agent in agents:
            # 模拟 Agent 基于任务完成情况形成观点
            agent_tasks = [t for t in tasks if t["assigned_to"] == agent["id"]]
            
            if agent_tasks:
                avg_quality = statistics.mean([t["quality"] for t in agent_tasks])
            else:
                avg_quality = 0.5
            
            opinion = AgentOpinion(
                agent_id=agent["id"],
                opinion_value=avg_quality,
                confidence=agent.get("confidence", 0.7),
                reasoning=f"Based on {len(agent_tasks)} completed tasks"
            )
            
            opinions.append(opinion)
        
        return opinions
    
    def _generate_communication_log(
        self,
        assignments: List[TaskAssignment]
    ) -> List[Dict]:
        """生成通信日志"""
        communications = []
        
        for assignment in assignments:
            communications.append({
                "from": "manager",
                "to": assignment.agent_id,
                "type": "task_assignment",
                "task_type": "general",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return communications
    
    def get_collaboration_analytics(self) -> Dict:
        """获取协作分析"""
        if not self.collaboration_sessions:
            return {"error": "No sessions available"}
        
        # 统计信息
        total_sessions = len(self.collaboration_sessions)
        avg_agents = statistics.mean([s["total_agents"] for s in self.collaboration_sessions])
        avg_tasks = statistics.mean([s["total_tasks"] for s in self.collaboration_sessions])
        avg_completion = statistics.mean([s["completed_tasks"] / s["total_tasks"] for s in self.collaboration_sessions]) if all(s["total_tasks"] > 0 for s in self.collaboration_sessions) else 0
        
        # 共识统计
        consensus_strategies = {}
        for session in self.collaboration_sessions:
            if session.get("consensus"):
                strategy = session["consensus"]["strategy"]
                if strategy not in consensus_strategies:
                    consensus_strategies[strategy] = 0
                consensus_strategies[strategy] += 1
        
        return {
            "total_sessions": total_sessions,
            "average_agents_per_session": round(avg_agents, 2),
            "average_tasks_per_session": round(avg_tasks, 2),
            "average_completion_rate": round(avg_completion * 100, 2),
            "consensus_strategies_used": consensus_strategies,
            "recent_sessions": self.collaboration_sessions[-5:]
        }


def create_collaboration_orchestrator() -> CollaborationOrchestrator:
    """工厂函数：创建协作协调器"""
    return CollaborationOrchestrator()


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Advanced Collaboration 测试")
    print("="*60)
    
    orchestrator = create_collaboration_orchestrator()
    
    # 创建 Agents
    print("\n🤖 创建 Agents...")
    agents = [
        {"id": "agent_1", "role": "researcher", "performance": 0.9, "confidence": 0.85, "skills": ["research", "analysis"]},
        {"id": "agent_2", "role": "writer", "performance": 0.85, "confidence": 0.8, "skills": ["writing", "editing"]},
        {"id": "agent_3", "role": "reviewer", "performance": 0.95, "confidence": 0.9, "skills": ["review", "quality"]},
        {"id": "agent_4", "role": "coder", "performance": 0.88, "confidence": 0.82, "skills": ["coding", "testing"]},
    ]
    
    print(f"   创建了 {len(agents)} 个 Agents")
    
    # 创建任务
    print("\n📋 创建任务...")
    tasks = [
        {"id": "task_1", "description": "Research market trends", "priority": 8, "required_skill": "research"},
        {"id": "task_2", "description": "Write report draft", "priority": 7, "required_skill": "writing"},
        {"id": "task_3", "description": "Review and edit", "priority": 9, "required_skill": "review"},
        {"id": "task_4", "description": "Implement feature", "priority": 6, "required_skill": "coding"},
    ]
    
    print(f"   创建了 {len(tasks)} 个任务")
    
    # 启动协作会话
    print("\n🚀 启动协作会话...")
    session = orchestrator.start_collaboration_session(
        session_name="Market Analysis Project",
        agents=agents,
        tasks=tasks,
        consensus_strategy=ConsensusStrategy.DEBATE
    )
    
    print(f"\n✅ 会话完成:")
    print(f"   会话ID: {session['session_id'][:8]}...")
    print(f"   Agents: {session['total_agents']}")
    print(f"   任务: {session['total_tasks']}")
    print(f"   完成: {session['completed_tasks']}")
    
    if session.get('consensus'):
        print(f"\n🎯 共识结果:")
        print(f"   策略: {session['consensus']['strategy']}")
        print(f"   共识值: {session['consensus']['agreed_value']:.2f}")
        print(f"   置信度: {session['consensus']['confidence']:.2f}")
        print(f"   轮数: {session['consensus']['rounds_needed']}")
    
    print(f"\n🐝 群体状态:")
    swarm = session['swarm_state']
    print(f"   活跃 Agents: {swarm['active_agents']}/{swarm['total_agents']}")
    print(f"   完成率: {swarm['task_completion_rate']*100:.1f}%")
    print(f"   平均置信度: {swarm['average_confidence']:.2f}")
    print(f"   通信开销: {swarm['communication_overhead']:.2f}")
    
    if swarm['emergent_behaviors']:
        print(f"   涌现行为: {', '.join(swarm['emergent_behaviors'])}")
    
    # 获取分析
    print("\n📊 协作分析:")
    analytics = orchestrator.get_collaboration_analytics()
    print(f"   总会话数: {analytics['total_sessions']}")
    print(f"   平均完成率: {analytics['average_completion_rate']:.1f}%")
    
    if analytics.get('consensus_strategies_used'):
        print(f"   使用的共识策略:")
        for strategy, count in analytics['consensus_strategies_used'].items():
            print(f"     - {strategy}: {count} 次")
    
    print("\n✅ 测试完成！")
