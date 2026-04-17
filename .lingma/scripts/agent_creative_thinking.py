#!/usr/bin/env python3
"""
AI Agent Creative Thinking & Innovation System - AI Agent 创造性思维与创新系统

发散性思维、收敛性思维、SCAMPER、六顶思考帽、头脑风暴、创新方法
实现生产级 AI Agent 的创造性思维能力

参考社区最佳实践:
- Divergent Thinking - generate many diverse ideas (brainstorming)
- Convergent Thinking - evaluate and refine ideas to select best ones
- SCAMPER Method - Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse
- Six Thinking Hats - parallel thinking from multiple perspectives
- Brainstorming Techniques - structured ideation methods
- Innovation Methods - systematic approaches to creative problem solving
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
    DIVERGENT = "divergent"  # 发散性思维
    CONVERGENT = "convergent"  # 收敛性思维


class ScamperCategory(Enum):
    """SCAMPER类别"""
    SUBSTITUTE = "substitute"  # 替代
    COMBINE = "combine"  # 合并
    ADAPT = "adapt"  # 改造
    MODIFY = "modify"  # 修改
    PUT_TO_OTHER_USES = "put_to_other_uses"  # 他用
    ELIMINATE = "eliminate"  # 消除
    REVERSE = "reverse"  # 重排


class ThinkingHatColor(Enum):
    """六顶思考帽颜色"""
    WHITE = "white"  # 白色：事实和数据
    RED = "red"  # 红色：情感和直觉
    BLACK = "black"  # 黑色：批判和风险
    YELLOW = "yellow"  # 黄色：乐观和积极
    GREEN = "green"  # 绿色：创意和新想法
    BLUE = "blue"  # 蓝色：控制和组织


@dataclass
class CreativeIdea:
    """创意想法"""
    idea_id: str
    title: str
    description: str
    category: str = ""  # 分类
    originality_score: float = 0.5  # 原创性 0-1
    feasibility_score: float = 0.5  # 可行性 0-1
    impact_score: float = 0.5  # 影响力 0-1
    tags: List[str] = field(default_factory=list)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.idea_id:
            self.idea_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    @property
    def overall_score(self) -> float:
        """综合评分"""
        return (self.originality_score + self.feasibility_score + self.impact_score) / 3


@dataclass
class ScamperResult:
    """SCAMPER结果"""
    result_id: str
    category: ScamperCategory
    ideas: List[CreativeIdea] = field(default_factory=list)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.result_id:
            self.result_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class HatPerspective:
    """帽子视角"""
    hat_color: ThinkingHatColor
    perspective_title: str
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hat_color": self.hat_color.value,
            "perspective_title": self.perspective_title,
            "insights_count": len(self.insights),
            "recommendations_count": len(self.recommendations)
        }


@dataclass
class BrainstormingSession:
    """头脑风暴会话"""
    session_id: str
    topic: str
    mode: ThinkingMode
    generated_ideas: List[CreativeIdea] = field(default_factory=list)
    selected_ideas: List[CreativeIdea] = field(default_factory=list)
    duration_minutes: int = 0
    participant_count: int = 1
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class DivergentThinkingEngine:
    """发散性思维引擎
    
    生成大量多样化想法
    """
    
    def __init__(self):
        self.sessions: List[BrainstormingSession] = []
        self.total_ideas_generated = 0
    
    def brainstorm_ideas(
        self,
        topic: str,
        num_ideas: int = 10,
        constraints: List[str] = None
    ) -> BrainstormingSession:
        """
        头脑风暴生成想法
        
        Args:
            topic: 主题
            num_ideas: 想法数量
            constraints: 约束条件
            
        Returns:
            头脑风暴会话
        """
        session = BrainstormingSession(
            session_id="",
            topic=topic,
            mode=ThinkingMode.DIVERGENT
        )
        
        logger.info(f"Starting divergent brainstorming: {topic}, target={num_ideas} ideas")
        
        # 生成多样化想法
        for i in range(num_ideas):
            idea = self._generate_creative_idea(topic, i, constraints)
            session.generated_ideas.append(idea)
            self.total_ideas_generated += 1
        
        session.duration_minutes = random.randint(15, 45)
        
        self.sessions.append(session)
        
        logger.info(f"Divergent brainstorming completed: {len(session.generated_ideas)} ideas generated")
        
        return session
    
    def _generate_creative_idea(
        self,
        topic: str,
        index: int,
        constraints: List[str] = None
    ) -> CreativeIdea:
        """生成创意想法"""
        # 模拟创意生成（实际应调用LLM）
        idea_templates = [
            f"Integrate AI-powered {topic} with real-time analytics",
            f"Create a gamified version of {topic} for better engagement",
            f"Develop a collaborative platform for {topic} sharing",
            f"Build an automated workflow for {topic} optimization",
            f"Design a mobile-first solution for {topic} accessibility"
        ]
        
        template = idea_templates[index % len(idea_templates)]
        
        idea = CreativeIdea(
            idea_id="",
            title=f"Idea {index + 1}: {template[:50]}...",
            description=f"A creative approach to {topic} using innovative methods",
            category="innovation",
            originality_score=random.uniform(0.6, 0.95),
            feasibility_score=random.uniform(0.5, 0.9),
            impact_score=random.uniform(0.6, 0.95),
            tags=[topic, "creative", "innovative"]
        )
        
        if constraints:
            idea.tags.extend(constraints)
        
        return idea
    
    def get_divergent_statistics(self) -> Dict[str, Any]:
        """获取发散性思维统计"""
        if not self.sessions:
            return {"total_sessions": 0}
        
        total_ideas = sum(len(s.generated_ideas) for s in self.sessions)
        avg_ideas_per_session = total_ideas / len(self.sessions) if self.sessions else 0
        
        return {
            "total_sessions": len(self.sessions),
            "total_ideas_generated": total_ideas,
            "avg_ideas_per_session": round(avg_ideas_per_session, 2)
        }


class ConvergentThinkingEngine:
    """收敛性思维引擎
    
    评估和精选最佳想法
    """
    
    def __init__(self):
        self.evaluation_history: List[Dict] = []
    
    def evaluate_and_select(
        self,
        ideas: List[CreativeIdea],
        selection_criteria: Dict[str, float] = None,
        top_n: int = 3
    ) -> List[CreativeIdea]:
        """
        评估并选择最佳想法
        
        Args:
            ideas: 想法列表
            selection_criteria: 选择标准权重
            top_n: 选择前N个
            
        Returns:
            选中的想法列表
        """
        if not ideas:
            return []
        
        if selection_criteria is None:
            selection_criteria = {
                "originality": 0.4,
                "feasibility": 0.3,
                "impact": 0.3
            }
        
        # 计算加权分数
        scored_ideas = []
        for idea in ideas:
            weighted_score = (
                idea.originality_score * selection_criteria.get("originality", 0.4) +
                idea.feasibility_score * selection_criteria.get("feasibility", 0.3) +
                idea.impact_score * selection_criteria.get("impact", 0.3)
            )
            scored_ideas.append((idea, weighted_score))
        
        # 按分数排序
        scored_ideas.sort(key=lambda x: x[1], reverse=True)
        
        # 选择前N个
        selected = [idea for idea, score in scored_ideas[:top_n]]
        
        # 记录评估历史
        self.evaluation_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_ideas_evaluated": len(ideas),
            "selected_count": len(selected),
            "avg_selected_score": round(statistics.mean([s for _, s in scored_ideas[:top_n]]), 4) if scored_ideas else 0
        })
        
        logger.info(f"Convergent evaluation completed: selected {len(selected)} from {len(ideas)} ideas")
        
        return selected
    
    def cluster_similar_ideas(
        self,
        ideas: List[CreativeIdea]
    ) -> Dict[str, List[CreativeIdea]]:
        """
        聚类相似想法
        
        Args:
            ideas: 想法列表
            
        Returns:
            聚类结果 {category: [ideas]}
        """
        clusters = defaultdict(list)
        
        for idea in ideas:
            # 基于标签聚类（简化）
            if idea.tags:
                primary_tag = idea.tags[0]
                clusters[primary_tag].append(idea)
            else:
                clusters["uncategorized"].append(idea)
        
        logger.info(f"Idea clustering completed: {len(clusters)} clusters")
        
        return dict(clusters)
    
    def get_convergent_statistics(self) -> Dict[str, Any]:
        """获取收敛性思维统计"""
        if not self.evaluation_history:
            return {"total_evaluations": 0}
        
        total_evaluated = sum(h["total_ideas_evaluated"] for h in self.evaluation_history)
        total_selected = sum(h["selected_count"] for h in self.evaluation_history)
        
        return {
            "total_evaluations": len(self.evaluation_history),
            "total_ideas_evaluated": total_evaluated,
            "total_ideas_selected": total_selected,
            "selection_rate": round(total_selected / max(total_evaluated, 1), 4)
        }


class ScamperMethod:
    """SCAMPER方法
    
    系统性创新检查清单
    """
    
    def __init__(self):
        self.results: List[ScamperResult] = []
    
    def apply_scamper(
        self,
        topic: str,
        categories: List[ScamperCategory] = None
    ) -> List[ScamperResult]:
        """
        应用SCAMPER方法
        
        Args:
            topic: 主题
            categories: SCAMPER类别（默认全部）
            
        Returns:
            SCAMPER结果列表
        """
        if categories is None:
            categories = list(ScamperCategory)
        
        results = []
        
        for category in categories:
            result = self._apply_category(topic, category)
            results.append(result)
        
        self.results.extend(results)
        
        logger.info(f"SCAMPER applied to {topic}: {len(results)} categories processed")
        
        return results
    
    def _apply_category(
        self,
        topic: str,
        category: ScamperCategory
    ) -> ScamperResult:
        """应用单个SCAMPER类别"""
        ideas = []
        
        # 基于类别生成想法
        if category == ScamperCategory.SUBSTITUTE:
            ideas = self._generate_substitute_ideas(topic)
        elif category == ScamperCategory.COMBINE:
            ideas = self._generate_combine_ideas(topic)
        elif category == ScamperCategory.ADAPT:
            ideas = self._generate_adapt_ideas(topic)
        elif category == ScamperCategory.MODIFY:
            ideas = self._generate_modify_ideas(topic)
        elif category == ScamperCategory.PUT_TO_OTHER_USES:
            ideas = self._generate_put_to_other_uses_ideas(topic)
        elif category == ScamperCategory.ELIMINATE:
            ideas = self._generate_eliminate_ideas(topic)
        elif category == ScamperCategory.REVERSE:
            ideas = self._generate_reverse_ideas(topic)
        
        result = ScamperResult(
            result_id="",
            category=category,
            ideas=ideas
        )
        
        return result
    
    def _generate_substitute_ideas(self, topic: str) -> List[CreativeIdea]:
        """生成替代想法"""
        return [
            CreativeIdea(
                idea_id="",
                title=f"Substitute traditional {topic} with AI-driven solution",
                description="Replace conventional approach with intelligent automation",
                category="substitute",
                originality_score=0.75,
                feasibility_score=0.8,
                impact_score=0.85
            )
        ]
    
    def _generate_combine_ideas(self, topic: str) -> List[CreativeIdea]:
        """生成合并想法"""
        return [
            CreativeIdea(
                idea_id="",
                title=f"Combine {topic} with social networking features",
                description="Merge core functionality with community engagement",
                category="combine",
                originality_score=0.8,
                feasibility_score=0.7,
                impact_score=0.9
            )
        ]
    
    def _generate_adapt_ideas(self, topic: str) -> List[CreativeIdea]:
        """生成改造想法"""
        return [
            CreativeIdea(
                idea_id="",
                title=f"Adapt {topic} for mobile-first experience",
                description="Modify design for optimal mobile usage",
                category="adapt",
                originality_score=0.7,
                feasibility_score=0.85,
                impact_score=0.8
            )
        ]
    
    def _generate_modify_ideas(self, topic: str) -> List[CreativeIdea]:
        """生成修改想法"""
        return [
            CreativeIdea(
                idea_id="",
                title=f"Modify {topic} interface for better accessibility",
                description="Enhance UI/UX for inclusive design",
                category="modify",
                originality_score=0.65,
                feasibility_score=0.9,
                impact_score=0.75
            )
        ]
    
    def _generate_put_to_other_uses_ideas(self, topic: str) -> List[CreativeIdea]:
        """生成他用想法"""
        return [
            CreativeIdea(
                idea_id="",
                title=f"Apply {topic} technology to education sector",
                description="Repurpose existing solution for new domain",
                category="put_to_other_uses",
                originality_score=0.85,
                feasibility_score=0.65,
                impact_score=0.8
            )
        ]
    
    def _generate_eliminate_ideas(self, topic: str) -> List[CreativeIdea]:
        """生成消除想法"""
        return [
            CreativeIdea(
                idea_id="",
                title=f"Eliminate manual steps in {topic} workflow",
                description="Remove unnecessary processes through automation",
                category="eliminate",
                originality_score=0.7,
                feasibility_score=0.85,
                impact_score=0.85
            )
        ]
    
    def _generate_reverse_ideas(self, topic: str) -> List[CreativeIdea]:
        """生成重排想法"""
        return [
            CreativeIdea(
                idea_id="",
                title=f"Reverse {topic} user journey for fresh perspective",
                description="Rethink process flow from opposite direction",
                category="reverse",
                originality_score=0.9,
                feasibility_score=0.6,
                impact_score=0.75
            )
        ]
    
    def get_scamper_statistics(self) -> Dict[str, Any]:
        """获取SCAMPER统计"""
        if not self.results:
            return {"total_applications": 0}
        
        total_ideas = sum(len(r.ideas) for r in self.results)
        
        category_counts = defaultdict(int)
        for result in self.results:
            category_counts[result.category.value] += len(result.ideas)
        
        return {
            "total_applications": len(self.results),
            "total_ideas_generated": total_ideas,
            "category_distribution": dict(category_counts)
        }


class SixThinkingHats:
    """六顶思考帽
    
    平行思维方法，从多个角度审视问题
    """
    
    def __init__(self):
        self.sessions: List[Dict] = []
    
    def conduct_thinking_session(
        self,
        topic: str,
        hats_order: List[ThinkingHatColor] = None
    ) -> Dict[ThinkingHatColor, HatPerspective]:
        """
        进行六帽思考会话
        
        Args:
            topic: 主题
            hats_order: 帽子顺序（默认全部）
            
        Returns:
            各帽子视角结果
        """
        if hats_order is None:
            hats_order = list(ThinkingHatColor)
        
        perspectives = {}
        
        for hat_color in hats_order:
            perspective = self._apply_hat_perspective(topic, hat_color)
            perspectives[hat_color] = perspective
        
        # 记录会话
        self.sessions.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "topic": topic,
            "hats_used": [h.value for h in hats_order],
            "perspectives_count": len(perspectives)
        })
        
        logger.info(f"Six hats session completed for: {topic}")
        
        return perspectives
    
    def _apply_hat_perspective(
        self,
        topic: str,
        hat_color: ThinkingHatColor
    ) -> HatPerspective:
        """应用单个帽子视角"""
        hat_definitions = {
            ThinkingHatColor.WHITE: {
                "title": "White Hat - Facts and Data",
                "insights": [
                    f"Current market size for {topic}: $X billion",
                    f"User adoption rate: Y% annually",
                    f"Technology maturity level: Z/10"
                ],
                "recommendations": [
                    "Gather more quantitative data",
                    "Conduct market research survey"
                ]
            },
            ThinkingHatColor.RED: {
                "title": "Red Hat - Emotions and Intuition",
                "insights": [
                    f"Users feel excited about {topic} potential",
                    "Concerns about implementation complexity",
                    "Strong emotional appeal for simplicity"
                ],
                "recommendations": [
                    "Address user anxiety points",
                    "Leverage positive emotional triggers"
                ]
            },
            ThinkingHatColor.BLACK: {
                "title": "Black Hat - Critical Judgment",
                "insights": [
                    f"Risk: High development cost for {topic}",
                    "Potential regulatory compliance issues",
                    "Market saturation in certain segments"
                ],
                "recommendations": [
                    "Conduct thorough risk assessment",
                    "Develop mitigation strategies",
                    "Plan for regulatory requirements"
                ]
            },
            ThinkingHatColor.YELLOW: {
                "title": "Yellow Hat - Optimism and Benefits",
                "insights": [
                    f"{topic} can increase efficiency by 40%",
                    "Significant revenue growth potential",
                    "Strong competitive advantage opportunity"
                ],
                "recommendations": [
                    "Highlight value proposition clearly",
                    "Quantify ROI for stakeholders",
                    "Identify early adopter segments"
                ]
            },
            ThinkingHatColor.GREEN: {
                "title": "Green Hat - Creativity and New Ideas",
                "insights": [
                    f"Innovative AI integration for {topic}",
                    "Novel gamification mechanics",
                    "Unexplored partnership opportunities"
                ],
                "recommendations": [
                    "Brainstorm unconventional solutions",
                    "Explore cross-industry collaborations",
                    "Prototype radical concepts"
                ]
            },
            ThinkingHatColor.BLUE: {
                "title": "Blue Hat - Process Control",
                "insights": [
                    f"Need structured approach to {topic} development",
                    "Clear milestones and KPIs required",
                    "Stakeholder alignment essential"
                ],
                "recommendations": [
                    "Define project roadmap",
                    "Establish governance framework",
                    "Set up regular review cycles"
                ]
            }
        }
        
        definition = hat_definitions[hat_color]
        
        perspective = HatPerspective(
            hat_color=hat_color,
            perspective_title=definition["title"],
            insights=definition["insights"],
            recommendations=definition["recommendations"]
        )
        
        return perspective
    
    def get_hats_statistics(self) -> Dict[str, Any]:
        """获取帽子统计"""
        if not self.sessions:
            return {"total_sessions": 0}
        
        return {
            "total_sessions": len(self.sessions),
            "avg_hats_per_session": round(
                statistics.mean([s["perspectives_count"] for s in self.sessions]), 2
            )
        }


class CreativeThinkingSystem:
    """创造性思维系统
    
    整合发散/收敛思维、SCAMPER、六顶思考帽
    """
    
    def __init__(self):
        self.divergent_engine = DivergentThinkingEngine()
        self.convergent_engine = ConvergentThinkingEngine()
        self.scamper_method = ScamperMethod()
        self.six_hats = SixThinkingHats()
    
    def run_creative_process(
        self,
        topic: str,
        use_scamper: bool = True,
        use_six_hats: bool = True
    ) -> Dict[str, Any]:
        """
        运行完整创造性思维流程
        
        Args:
            topic: 主题
            use_scamper: 是否使用SCAMPER
            use_six_hats: 是否使用六顶思考帽
            
        Returns:
            完整结果
        """
        logger.info(f"Starting creative process for: {topic}")
        
        results = {}
        
        # Step 1: 发散性思维 - 生成想法
        divergent_session = self.divergent_engine.brainstorm_ideas(
            topic=topic,
            num_ideas=10
        )
        results["divergent_thinking"] = {
            "session_id": divergent_session.session_id,
            "ideas_generated": len(divergent_session.generated_ideas),
            "duration_minutes": divergent_session.duration_minutes
        }
        
        # Step 2: 收敛性思维 - 评估选择
        selected_ideas = self.convergent_engine.evaluate_and_select(
            ideas=divergent_session.generated_ideas,
            top_n=3
        )
        results["convergent_thinking"] = {
            "ideas_evaluated": len(divergent_session.generated_ideas),
            "ideas_selected": len(selected_ideas),
            "selected_titles": [idea.title[:50] for idea in selected_ideas]
        }
        
        # Step 3: SCAMPER方法（可选）
        if use_scamper:
            scamper_results = self.scamper_method.apply_scamper(topic)
            results["scamper"] = {
                "categories_applied": len(scamper_results),
                "total_ideas": sum(len(r.ideas) for r in scamper_results)
            }
        
        # Step 4: 六顶思考帽（可选）
        if use_six_hats:
            hats_perspectives = self.six_hats.conduct_thinking_session(topic)
            results["six_hats"] = {
                "perspectives_count": len(hats_perspectives),
                "hats_used": [h.value for h in hats_perspectives.keys()]
            }
        
        logger.info(f"Creative process completed for: {topic}")
        
        return results
    
    def get_system_overview(self) -> Dict[str, Any]:
        """获取系统概览"""
        return {
            "divergent_thinking": self.divergent_engine.get_divergent_statistics(),
            "convergent_thinking": self.convergent_engine.get_convergent_statistics(),
            "scamper_method": self.scamper_method.get_scamper_statistics(),
            "six_thinking_hats": self.six_hats.get_hats_statistics()
        }


def create_creative_thinking_system() -> CreativeThinkingSystem:
    """工厂函数：创建创造性思维系统"""
    system = CreativeThinkingSystem()
    return system


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Creative Thinking & Innovation 测试")
    print("="*60)
    
    system = create_creative_thinking_system()
    
    # 测试完整创造性思维流程
    print("\n💡 运行完整创造性思维流程...")
    results = system.run_creative_process(
        topic="smart campus delivery system",
        use_scamper=True,
        use_six_hats=True
    )
    
    print(f"\n   主题: {results.get('topic', 'smart campus delivery system')}")
    print(f"\n   发散性思维:")
    dt = results['divergent_thinking']
    print(f"     会话ID: {dt['session_id'][:8]}...")
    print(f"     生成想法数: {dt['ideas_generated']}")
    print(f"     持续时间: {dt['duration_minutes']}分钟")
    
    print(f"\n   收敛性思维:")
    ct = results['convergent_thinking']
    print(f"     评估想法数: {ct['ideas_evaluated']}")
    print(f"     选中想法数: {ct['ideas_selected']}")
    print(f"     选中想法:")
    for title in ct['selected_titles']:
        print(f"       - {title}")
    
    print(f"\n   SCAMPER方法:")
    sc = results['scamper']
    print(f"     应用类别数: {sc['categories_applied']}")
    print(f"     总想法数: {sc['total_ideas']}")
    
    print(f"\n   六顶思考帽:")
    sh = results['six_hats']
    print(f"     视角数: {sh['perspectives_count']}")
    print(f"     使用的帽子: {', '.join(sh['hats_used'])}")
    
    # 单独测试SCAMPER
    print("\n🔧 单独测试SCAMPER方法...")
    scamper_results = system.scamper_method.apply_scamper(
        topic="online learning platform",
        categories=[ScamperCategory.SUBSTITUTE, ScamperCategory.COMBINE, ScamperCategory.ELIMINATE]
    )
    
    print(f"   应用了 {len(scamper_results)} 个SCAMPER类别:")
    for result in scamper_results:
        print(f"     {result.category.value}: {len(result.ideas)} 个想法")
        if result.ideas:
            print(f"       - {result.ideas[0].title[:60]}...")
    
    # 单独测试六顶思考帽
    print("\n🎩 单独测试六顶思考帽...")
    hats_perspectives = system.six_hats.conduct_thinking_session(
        topic="AI-powered customer service",
        hats_order=[ThinkingHatColor.WHITE, ThinkingHatColor.BLACK, ThinkingHatColor.GREEN]
    )
    
    print(f"   使用了 {len(hats_perspectives)} 顶帽子:")
    for color, perspective in hats_perspectives.items():
        print(f"     {color.value}:")
        print(f"       标题: {perspective.perspective_title}")
        print(f"       洞察数: {len(perspective.insights)}")
        print(f"       建议数: {len(perspective.recommendations)}")
    
    # 系统概览
    overview = system.get_system_overview()
    print(f"\n📊 系统概览:")
    print(f"   发散性思维:")
    dt_stats = overview['divergent_thinking']
    print(f"     总会话数: {dt_stats['total_sessions']}")
    print(f"     总想法数: {dt_stats['total_ideas_generated']}")
    print(f"     平均每会话: {dt_stats['avg_ideas_per_session']}")
    print(f"   收敛性思维:")
    ct_stats = overview['convergent_thinking']
    print(f"     总评估数: {ct_stats['total_evaluations']}")
    print(f"     总评估想法: {ct_stats['total_ideas_evaluated']}")
    print(f"     总选中想法: {ct_stats['total_ideas_selected']}")
    print(f"     选择率: {ct_stats['selection_rate']*100:.1f}%")
    print(f"   SCAMPER方法:")
    sc_stats = overview['scamper_method']
    print(f"     总应用数: {sc_stats['total_applications']}")
    print(f"     总想法数: {sc_stats['total_ideas_generated']}")
    print(f"   六顶思考帽:")
    sh_stats = overview['six_thinking_hats']
    print(f"     总会话数: {sh_stats['total_sessions']}")
    print(f"     平均每会话帽子数: {sh_stats['avg_hats_per_session']}")
    
    print("\n✅ 测试完成！")
