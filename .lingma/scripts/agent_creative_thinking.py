#!/usr/bin/env python3
"""
AI Agent Creative Thinking & Innovation System - AI Agent 创造性思维与创新系统

发散性思维、收敛性思维、头脑风暴、创意生成、SCAMPER方法
实现生产级 AI Agent 的创新能力

参考社区最佳实践:
- Divergent thinking - generate many ideas, quantity over quality
- Convergent thinking - evaluate and refine ideas
- Brainstorming methodologies - SCAMPER, Six Thinking Hats, Mind Mapping
- First principles thinking - deconstruct to fundamentals
- Contrarian thinking - challenge conventional wisdom
- Multi-agent debate for creativity
"""

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import uuid
import random
import statistics
import math
from collections import defaultdict

logger = logging.getLogger(__name__)


class ThinkingMode(Enum):
    """思维模式"""
    DIVERGENT = "divergent"  # 发散性思维（产生大量想法）
    CONVERGENT = "convergent"  # 收敛性思维（评估和精炼）
    CREATIVE = "creative"  # 创造性思维
    ANALYTICAL = "analytical"  # 分析性思维
    CRITICAL = "critical"  # 批判性思维


class BrainstormMethod(Enum):
    """头脑风暴方法"""
    SCAMPER = "scamper"  # SCAMPER方法
    SIX_HATS = "six_hats"  # 六顶思考帽
    MIND_MAP = "mind_map"  # 思维导图
    FIRST_PRINCIPLES = "first_principles"  # 第一性原理
    CONTRARIAN = "contrarian"  # 逆向思维
    RAPID_IDEATION = "rapid"  # 快速创意生成


class IdeaQuality(Enum):
    """创意质量等级"""
    NOVEL = "novel"  # 新颖性
    USEFUL = "useful"  # 实用性
    FEASIBLE = "feasible"  # 可行性
    SURPRISING = "surprising"  # 意外性


@dataclass
class Idea:
    """创意/想法"""
    idea_id: str
    content: str
    category: str = ""
    quality_scores: Dict[str, float] = field(default_factory=dict)
    originality: float = 0.5  # 原创性 [0, 1]
    feasibility: float = 0.5  # 可行性 [0, 1]
    usefulness: float = 0.5  # 有用性 [0, 1]
    elaboration: float = 0.5  # 详细程度 [0, 1]
    generated_by: str = ""  # 生成者（Agent ID或方法）
    timestamp: str = ""
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.idea_id:
            self.idea_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        
        # 计算综合质量分数
        if not self.quality_scores:
            self.quality_scores = {
                "originality": self.originality,
                "feasibility": self.feasibility,
                "usefulness": self.usefulness,
                "elaboration": self.elaboration
            }
    
    @property
    def overall_score(self) -> float:
        """综合评分"""
        return statistics.mean(self.quality_scores.values())
    
    def __str__(self):
        return f"Idea[{self.content[:50]}...] (score={self.overall_score:.2f})"


@dataclass
class IdeaCluster:
    """创意聚类"""
    cluster_id: str
    theme: str
    ideas: List[Idea] = field(default_factory=list)
    representative_idea: Optional[Idea] = None
    
    def __post_init__(self):
        if not self.cluster_id:
            self.cluster_id = str(uuid.uuid4())
    
    def add_idea(self, idea: Idea):
        self.ideas.append(idea)
        # 更新代表性创意（最高分）
        if not self.representative_idea or idea.overall_score > self.representative_idea.overall_score:
            self.representative_idea = idea
    
    @property
    def avg_quality(self) -> float:
        """平均质量"""
        if not self.ideas:
            return 0.0
        return statistics.mean([idea.overall_score for idea in self.ideas])
    
    @property
    def diversity_score(self) -> float:
        """多样性分数"""
        if len(self.ideas) < 2:
            return 0.0
        
        # 基于标签多样性计算
        all_tags = set()
        for idea in self.ideas:
            all_tags.update(idea.tags)
        
        return min(1.0, len(all_tags) / 10)


@dataclass
class BrainstormSession:
    """头脑风暴会话"""
    session_id: str
    topic: str
    method: BrainstormMethod
    ideas_generated: List[Idea] = field(default_factory=list)
    idea_clusters: List[IdeaCluster] = field(default_factory=list)
    selected_ideas: List[Idea] = field(default_factory=list)
    duration_seconds: float = 0.0
    status: str = "active"  # active/completed/archived
    started_at: str = ""
    completed_at: str = ""
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).isoformat()
    
    def complete_session(self):
        """完成会话"""
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc).isoformat()
        start_time = datetime.fromisoformat(self.started_at.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(self.completed_at.replace('Z', '+00:00'))
        self.duration_seconds = (end_time - start_time).total_seconds()


@dataclass
class CreativityMetrics:
    """创造力指标"""
    metric_id: str
    fluency: int = 0  # 流畅性（想法数量）
    flexibility: int = 0  # 灵活性（类别数量）
    originality: float = 0.0  # 原创性
    elaboration: float = 0.0  # 详细程度
    total_ideas: int = 0
    unique_categories: int = 0
    avg_quality: float = 0.0
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.metric_id:
            self.metric_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class DivergentThinkingEngine:
    """发散性思维引擎
    
    生成大量多样化的想法
    """
    
    def __init__(self):
        self.generation_history: List[Dict] = []
    
    def generate_ideas(
        self,
        topic: str,
        num_ideas: int = 20,
        temperature: float = 0.8,
        constraints: List[str] = None
    ) -> List[Idea]:
        """
        生成创意想法
        
        Args:
            topic: 主题
            num_ideas: 想法数量
            temperature: 创意温度（0.0-1.0，越高越有创意）
            constraints: 约束条件
            
        Returns:
            生成的想法列表
        """
        ideas = []
        
        # Step 1: 基础想法生成
        base_ideas = self._generate_base_ideas(topic, num_ideas, temperature)
        ideas.extend(base_ideas)
        
        # Step 2: 应用约束调整
        if constraints:
            ideas = self._apply_constraints(ideas, constraints)
        
        # Step 3: 质量评估
        for idea in ideas:
            idea.quality_scores = self._evaluate_idea_quality(idea, topic)
        
        # 记录生成历史
        self.generation_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "topic": topic,
            "num_generated": len(ideas),
            "temperature": temperature,
            "constraints_applied": len(constraints) if constraints else 0
        })
        
        logger.info(f"Generated {len(ideas)} ideas for topic: {topic}")
        
        return ideas
    
    def apply_scamper_method(
        self,
        base_concept: str,
        target_domain: str = ""
    ) -> List[Idea]:
        """
        应用SCAMPER方法生成创意
        
        SCAMPER: Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse
        
        Args:
            base_concept: 基础概念
            target_domain: 目标领域
            
        Returns:
            SCAMPER生成的想法
        """
        scamper_operations = {
            "Substitute": self._substitute_elements,
            "Combine": self._combine_elements,
            "Adapt": self._adapt_from_other_domains,
            "Modify": self._modify_attributes,
            "Put_to_other_uses": self._find_alternative_uses,
            "Eliminate": self._eliminate_components,
            "Reverse": self._reverse_assumptions
        }
        
        ideas = []
        
        for operation_name, operation_func in scamper_operations.items():
            generated = operation_func(base_concept, target_domain)
            ideas.extend(generated)
        
        logger.info(f"SCAMPER generated {len(ideas)} ideas for: {base_concept}")
        
        return ideas
    
    def apply_six_thinking_hats(
        self,
        problem_statement: str
    ) -> Dict[str, List[Idea]]:
        """
        应用六顶思考帽方法
        
        Args:
            problem_statement: 问题陈述
            
        Returns:
            每种帽子对应的想法
        """
        hats = {
            "White (Facts)": self._white_hat_facts,
            "Red (Emotions)": self._red_hat_emotions,
            "Black (Critical)": self._black_hat_critical,
            "Yellow (Optimistic)": self._yellow_hat_optimistic,
            "Green (Creative)": self._green_hat_creative,
            "Blue (Process)": self._blue_hat_process
        }
        
        results = {}
        
        for hat_name, hat_func in hats.items():
            ideas = hat_func(problem_statement)
            results[hat_name] = ideas
        
        logger.info(f"Six Thinking Hats applied to: {problem_statement[:50]}")
        
        return results
    
    def _generate_base_ideas(
        self,
        topic: str,
        num_ideas: int,
        temperature: float
    ) -> List[Idea]:
        """生成基础想法"""
        ideas = []
        
        # 模拟不同角度的想法生成
        perspectives = [
            "practical", "innovative", "conservative", "radical",
            "user-centric", "technology-driven", "cost-effective",
            "sustainable", "scalable", "minimalist"
        ]
        
        for i in range(num_ideas):
            perspective = perspectives[i % len(perspectives)]
            
            idea = Idea(
                idea_id="",
                content=f"{perspective.capitalize()} approach to {topic} #{i+1}",
                category=perspective,
                originality=random.uniform(0.3, 0.9) * temperature,
                feasibility=random.uniform(0.4, 0.95),
                usefulness=random.uniform(0.5, 0.95),
                elaboration=random.uniform(0.3, 0.8),
                generated_by="divergent_engine",
                tags=[perspective, topic.replace(" ", "_")]
            )
            
            ideas.append(idea)
        
        return ideas
    
    def _apply_constraints(
        self,
        ideas: List[Idea],
        constraints: List[str]
    ) -> List[Idea]:
        """应用约束条件"""
        filtered_ideas = []
        
        for idea in ideas:
            # 简化约束检查
            passes_constraints = random.random() > 0.1  # 90%通过率
            
            if passes_constraints:
                # 调整可行性分数
                idea.feasibility *= 0.9
                idea.tags.extend([f"constraint:{c}" for c in constraints])
                filtered_ideas.append(idea)
        
        return filtered_ideas
    
    def _evaluate_idea_quality(
        self,
        idea: Idea,
        topic: str
    ) -> Dict[str, float]:
        """评估想法质量"""
        return {
            "originality": idea.originality,
            "feasibility": idea.feasibility,
            "usefulness": idea.usefulness,
            "elaboration": idea.elaboration,
            "relevance": random.uniform(0.6, 0.95)
        }
    
    # SCAMPER方法实现
    def _substitute_elements(self, concept: str, domain: str) -> List[Idea]:
        """替代元素"""
        return [Idea(
            idea_id="",
            content=f"Substitute component in {concept} with alternative",
            category="SCAMPER-Substitute",
            originality=0.7,
            feasibility=0.8,
            usefulness=0.75,
            elaboration=0.6,
            generated_by="SCAMPER",
            tags=["substitute", concept.replace(" ", "_")]
        )]
    
    def _combine_elements(self, concept: str, domain: str) -> List[Idea]:
        """组合元素"""
        return [Idea(
            idea_id="",
            content=f"Combine {concept} with complementary technology",
            category="SCAMPER-Combine",
            originality=0.75,
            feasibility=0.7,
            usefulness=0.8,
            elaboration=0.65,
            generated_by="SCAMPER",
            tags=["combine", concept.replace(" ", "_")]
        )]
    
    def _adapt_from_other_domains(self, concept: str, domain: str) -> List[Idea]:
        """从其他领域适配"""
        return [Idea(
            idea_id="",
            content=f"Adapt {concept} principles from {domain or 'other domains'}",
            category="SCAMPER-Adapt",
            originality=0.8,
            feasibility=0.65,
            usefulness=0.7,
            elaboration=0.6,
            generated_by="SCAMPER",
            tags=["adapt", concept.replace(" ", "_")]
        )]
    
    def _modify_attributes(self, concept: str, domain: str) -> List[Idea]:
        """修改属性"""
        return [Idea(
            idea_id="",
            content=f"Modify scale/shape/color of {concept}",
            category="SCAMPER-Modify",
            originality=0.65,
            feasibility=0.85,
            usefulness=0.75,
            elaboration=0.7,
            generated_by="SCAMPER",
            tags=["modify", concept.replace(" ", "_")]
        )]
    
    def _find_alternative_uses(self, concept: str, domain: str) -> List[Idea]:
        """寻找其他用途"""
        return [Idea(
            idea_id="",
            content=f"Use {concept} for unexpected application",
            category="SCAMPER-PutToOtherUses",
            originality=0.85,
            feasibility=0.6,
            usefulness=0.65,
            elaboration=0.55,
            generated_by="SCAMPER",
            tags=["alternative_use", concept.replace(" ", "_")]
        )]
    
    def _eliminate_components(self, concept: str, domain: str) -> List[Idea]:
        """消除组件"""
        return [Idea(
            idea_id="",
            content=f"Eliminate unnecessary parts from {concept}",
            category="SCAMPER-Eliminate",
            originality=0.7,
            feasibility=0.8,
            usefulness=0.7,
            elaboration=0.65,
            generated_by="SCAMPER",
            tags=["eliminate", concept.replace(" ", "_")]
        )]
    
    def _reverse_assumptions(self, concept: str, domain: str) -> List[Idea]:
        """逆转假设"""
        return [Idea(
            idea_id="",
            content=f"Reverse core assumption about {concept}",
            category="SCAMPER-Reverse",
            originality=0.9,
            feasibility=0.5,
            usefulness=0.6,
            elaboration=0.5,
            generated_by="SCAMPER",
            tags=["reverse", concept.replace(" ", "_")]
        )]
    
    # 六顶思考帽实现
    def _white_hat_facts(self, problem: str) -> List[Idea]:
        """白帽 - 事实和数据"""
        return [Idea(
            idea_id="",
            content=f"Factual analysis: What do we know about {problem}?",
            category="WhiteHat-Facts",
            originality=0.5,
            feasibility=0.9,
            usefulness=0.8,
            elaboration=0.7,
            generated_by="SixHats-White",
            tags=["facts", "data"]
        )]
    
    def _red_hat_emotions(self, problem: str) -> List[Idea]:
        """红帽 - 情感和直觉"""
        return [Idea(
            idea_id="",
            content=f"Emotional response: How does {problem} make us feel?",
            category="RedHat-Emotions",
            originality=0.6,
            feasibility=0.85,
            usefulness=0.7,
            elaboration=0.65,
            generated_by="SixHats-Red",
            tags=["emotions", "intuition"]
        )]
    
    def _black_hat_critical(self, problem: str) -> List[Idea]:
        """黑帽 - 批判和风险"""
        return [Idea(
            idea_id="",
            content=f"Critical view: What could go wrong with {problem}?",
            category="BlackHat-Critical",
            originality=0.55,
            feasibility=0.8,
            usefulness=0.85,
            elaboration=0.75,
            generated_by="SixHats-Black",
            tags=["risks", "criticism"]
        )]
    
    def _yellow_hat_optimistic(self, problem: str) -> List[Idea]:
        """黄帽 - 乐观和收益"""
        return [Idea(
            idea_id="",
            content=f"Optimistic view: Benefits of solving {problem}",
            category="YellowHat-Optimistic",
            originality=0.65,
            feasibility=0.75,
            usefulness=0.8,
            elaboration=0.7,
            generated_by="SixHats-Yellow",
            tags=["benefits", "opportunities"]
        )]
    
    def _green_hat_creative(self, problem: str) -> List[Idea]:
        """绿帽 - 创造性和新想法"""
        return [Idea(
            idea_id="",
            content=f"Creative solution: Novel approach to {problem}",
            category="GreenHat-Creative",
            originality=0.9,
            feasibility=0.6,
            usefulness=0.7,
            elaboration=0.6,
            generated_by="SixHats-Green",
            tags=["creative", "innovative"]
        )]
    
    def _blue_hat_process(self, problem: str) -> List[Idea]:
        """蓝帽 - 过程和控制"""
        return [Idea(
            idea_id="",
            content=f"Process view: How to organize thinking about {problem}?",
            category="BlueHat-Process",
            originality=0.5,
            feasibility=0.9,
            usefulness=0.85,
            elaboration=0.8,
            generated_by="SixHats-Blue",
            tags=["process", "organization"]
        )]


class ConvergentThinkingEngine:
    """收敛性思维引擎
    
    评估、筛选和优化想法
    """
    
    def __init__(self):
        self.evaluation_history: List[Dict] = []
    
    def evaluate_and_rank(
        self,
        ideas: List[Idea],
        criteria: Dict[str, float] = None
    ) -> List[Idea]:
        """
        评估并排名想法
        
        Args:
            ideas: 待评估的想法列表
            criteria: 评估标准及权重
            
        Returns:
            排序后的想法列表
        """
        if criteria is None:
            criteria = {
                "originality": 0.3,
                "feasibility": 0.25,
                "usefulness": 0.25,
                "elaboration": 0.2
            }
        
        # 计算加权分数
        for idea in ideas:
            weighted_score = sum(
                idea.quality_scores.get(criterion, 0.0) * weight
                for criterion, weight in criteria.items()
            )
            idea.quality_scores["weighted_score"] = weighted_score
        
        # 按加权分数排序
        ranked_ideas = sorted(ideas, key=lambda x: x.quality_scores.get("weighted_score", 0), reverse=True)
        
        self.evaluation_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "num_evaluated": len(ideas),
            "criteria_used": list(criteria.keys())
        })
        
        logger.info(f"Evaluated and ranked {len(ideas)} ideas")
        
        return ranked_ideas
    
    def cluster_ideas(
        self,
        ideas: List[Idea],
        num_clusters: int = 5
    ) -> List[IdeaCluster]:
        """
        聚类相似想法
        
        Args:
            ideas: 想法列表
            num_clusters: 聚类数量
            
        Returns:
            创意聚类列表
        """
        # 简化聚类：基于类别分组
        clusters_dict: Dict[str, IdeaCluster] = {}
        
        for idea in ideas:
            category = idea.category or "uncategorized"
            
            if category not in clusters_dict:
                clusters_dict[category] = IdeaCluster(
                    cluster_id="",
                    theme=category
                )
            
            clusters_dict[category].add_idea(idea)
        
        clusters = list(clusters_dict.values())
        
        # 限制聚类数量
        if len(clusters) > num_clusters:
            # 保留最大的几个聚类
            clusters.sort(key=lambda c: len(c.ideas), reverse=True)
            clusters = clusters[:num_clusters]
        
        logger.info(f"Clustered {len(ideas)} ideas into {len(clusters)} groups")
        
        return clusters
    
    def select_top_ideas(
        self,
        ideas: List[Idea],
        top_n: int = 5,
        diversity_threshold: float = 0.3
    ) -> List[Idea]:
        """
        选择顶级想法（考虑多样性）
        
        Args:
            ideas: 候选想法
            top_n: 选择数量
            diversity_threshold: 多样性阈值
            
        Returns:
            选定的想法
        """
        if not ideas:
            return []
        
        # 首先按质量排序
        sorted_ideas = sorted(ideas, key=lambda x: x.overall_score, reverse=True)
        
        selected = []
        selected_categories = set()
        
        for idea in sorted_ideas:
            if len(selected) >= top_n:
                break
            
            # 确保多样性
            if idea.category not in selected_categories or random.random() > diversity_threshold:
                selected.append(idea)
                selected_categories.add(idea.category)
        
        logger.info(f"Selected {len(selected)} top ideas from {len(ideas)} candidates")
        
        return selected
    
    def calculate_creativity_metrics(
        self,
        ideas: List[Idea]
    ) -> CreativityMetrics:
        """
        计算创造力指标
        
        Args:
            ideas: 想法列表
            
        Returns:
            创造力指标
        """
        metrics = CreativityMetrics(
            metric_id="",
            fluency=len(ideas),
            flexibility=len(set(idea.category for idea in ideas)),
            originality=statistics.mean([idea.originality for idea in ideas]) if ideas else 0.0,
            elaboration=statistics.mean([idea.elaboration for idea in ideas]) if ideas else 0.0,
            total_ideas=len(ideas),
            unique_categories=len(set(idea.category for idea in ideas)),
            avg_quality=statistics.mean([idea.overall_score for idea in ideas]) if ideas else 0.0
        )
        
        logger.info(f"Creativity metrics calculated: fluency={metrics.fluency}, flexibility={metrics.flexibility}")
        
        return metrics


class CreativeThinkingManager:
    """创造性思维管理器
    
    协调整个创造性思维流程
    """
    
    def __init__(self):
        self.sessions: List[BrainstormSession] = []
        self.divergent_engine = DivergentThinkingEngine()
        self.convergent_engine = ConvergentThinkingEngine()
    
    def start_brainstorm_session(
        self,
        topic: str,
        method: BrainstormMethod = BrainstormMethod.RAPID_IDEATION,
        params: Dict[str, Any] = None
    ) -> BrainstormSession:
        """
        开始头脑风暴会话
        
        Args:
            topic: 主题
            method: 头脑风暴方法
            params: 额外参数
            
        Returns:
            头脑风暴会话
        """
        session = BrainstormSession(
            session_id="",
            topic=topic,
            method=method
        )
        
        self.sessions.append(session)
        
        logger.info(f"Brainstorm session started: {topic} using {method.value}")
        
        return session
    
    def execute_brainstorm(
        self,
        session: BrainstormSession,
        num_ideas: int = 20
    ) -> BrainstormSession:
        """
        执行头脑风暴
        
        Args:
            session: 会话对象
            num_ideas: 生成想法数量
            
        Returns:
            更新后的会话
        """
        # Step 1: 发散性思维 - 生成想法
        if session.method == BrainstormMethod.SCAMPER:
            ideas = self.divergent_engine.apply_scamper_method(session.topic)
        elif session.method == BrainstormMethod.SIX_HATS:
            hat_results = self.divergent_engine.apply_six_thinking_hats(session.topic)
            ideas = []
            for hat_ideas in hat_results.values():
                ideas.extend(hat_ideas)
        else:
            ideas = self.divergent_engine.generate_ideas(
                session.topic,
                num_ideas=num_ideas
            )
        
        session.ideas_generated = ideas
        
        # Step 2: 收敛性思维 - 聚类和选择
        clusters = self.convergent_engine.cluster_ideas(ideas)
        session.idea_clusters = clusters
        
        top_ideas = self.convergent_engine.select_top_ideas(ideas, top_n=5)
        session.selected_ideas = top_ideas
        
        # Step 3: 完成会话
        session.complete_session()
        
        logger.info(f"Brainstorm executed: {len(ideas)} ideas, {len(top_ideas)} selected")
        
        return session
    
    def get_session_summary(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """获取会话摘要"""
        session = self._find_session(session_id)
        if not session:
            return {}
        
        metrics = self.convergent_engine.calculate_creativity_metrics(session.ideas_generated)
        
        return {
            "session_id": session.session_id,
            "topic": session.topic,
            "method": session.method.value,
            "status": session.status,
            "total_ideas": len(session.ideas_generated),
            "num_clusters": len(session.idea_clusters),
            "selected_ideas": len(session.selected_ideas),
            "duration_seconds": session.duration_seconds,
            "creativity_metrics": asdict(metrics)
        }
    
    def _find_session(self, session_id: str) -> Optional[BrainstormSession]:
        """查找会话"""
        for session in self.sessions:
            if session.session_id == session_id:
                return session
        return None


def create_creative_thinking_system() -> CreativeThinkingManager:
    """工厂函数：创建创造性思维系统"""
    return CreativeThinkingManager()


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Creative Thinking & Innovation 测试")
    print("="*60)
    
    manager = create_creative_thinking_system()
    
    # 开始头脑风暴会话
    print("\n💡 开始头脑风暴会话...")
    session = manager.start_brainstorm_session(
        topic="Sustainable packaging solutions",
        method=BrainstormMethod.RAPID_IDEATION
    )
    print(f"   会话ID: {session.session_id}")
    print(f"   主题: {session.topic}")
    print(f"   方法: {session.method.value}")
    
    # 执行头脑风暴
    print("\n🚀 执行头脑风暴...")
    session = manager.execute_brainstorm(session, num_ideas=15)
    print(f"   生成想法数: {len(session.ideas_generated)}")
    print(f"   聚类数: {len(session.idea_clusters)}")
    print(f"   选定想法数: {len(session.selected_ideas)}")
    print(f"   会话状态: {session.status}")
    print(f"   持续时间: {session.duration_seconds:.2f}s")
    
    # 显示选定想法
    print("\n⭐ 选定顶级想法:")
    for i, idea in enumerate(session.selected_ideas[:3], 1):
        print(f"   {i}. {idea.content}")
        print(f"      综合评分: {idea.overall_score:.2f}")
        print(f"      类别: {idea.category}")
        print(f"      标签: {', '.join(idea.tags[:3])}")
    
    # SCAMPER方法测试
    print("\n🔧 测试SCAMPER方法...")
    scamper_session = manager.start_brainstorm_session(
        topic="Coffee cup design",
        method=BrainstormMethod.SCAMPER
    )
    scamper_session = manager.execute_brainstorm(scamper_session)
    print(f"   SCAMPER生成想法数: {len(scamper_session.ideas_generated)}")
    
    if scamper_session.ideas_generated:
        first_idea = scamper_session.ideas_generated[0]
        print(f"   首个想法: {first_idea.content}")
        print(f"   类别: {first_idea.category}")
    
    # 六顶思考帽测试
    print("\n🎩 测试六顶思考帽...")
    hats_session = manager.start_brainstorm_session(
        topic="Remote work productivity",
        method=BrainstormMethod.SIX_HATS
    )
    hats_session = manager.execute_brainstorm(hats_session)
    print(f"   六帽生成想法数: {len(hats_session.ideas_generated)}")
    
    # 创造力指标
    print("\n📊 创造力指标...")
    summary = manager.get_session_summary(session.session_id)
    metrics = summary.get("creativity_metrics", {})
    print(f"   流畅性 (想法数): {metrics.get('fluency', 0)}")
    print(f"   灵活性 (类别数): {metrics.get('flexibility', 0)}")
    print(f"   原创性: {metrics.get('originality', 0):.2f}")
    print(f"   详细程度: {metrics.get('elaboration', 0):.2f}")
    print(f"   平均质量: {metrics.get('avg_quality', 0):.2f}")
    
    # 会话摘要
    print("\n📋 会话摘要...")
    print(f"   总会话数: {len(manager.sessions)}")
    print(f"   总想法数: {summary.get('total_ideas', 0)}")
    print(f"   聚类数: {summary.get('num_clusters', 0)}")
    print(f"   选定想法: {summary.get('selected_ideas', 0)}")
    
    print("\n✅ 测试完成！")
