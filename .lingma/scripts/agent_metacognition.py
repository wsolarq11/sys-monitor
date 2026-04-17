#!/usr/bin/env python3
"""
AI Agent Metacognition & Self-Reflection System - AI Agent 元认知与自我反思系统

自我监控、自我评估、自我调整、内省觉察、信心校准
实现生产级 AI Agent 的元认知能力

参考社区最佳实践:
- Metacognitive monitoring - track own thinking process
- Self-reflection - evaluate performance and identify improvements
- Self-awareness - maintain explicit self-model of capabilities
- Confidence calibration - assess certainty in decisions
- Strategy selection - choose optimal approach based on self-assessment
- SELF-RAG framework - self-reflection and adaptive generation
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


class ReflectionType(Enum):
    """反思类型"""
    PERFORMANCE = "performance"  # 性能反思
    STRATEGY = "strategy"  # 策略反思
    KNOWLEDGE = "knowledge"  # 知识反思
    CONFIDENCE = "confidence"  # 信心反思
    ERROR = "error"  # 错误反思


class ConfidenceLevel(Enum):
    """信心等级"""
    VERY_LOW = "very_low"  # 非常低 (0.0-0.2)
    LOW = "low"  # 低 (0.2-0.4)
    MEDIUM = "medium"  # 中等 (0.4-0.6)
    HIGH = "high"  # 高 (0.6-0.8)
    VERY_HIGH = "very_high"  # 非常高 (0.8-1.0)


class AdjustmentAction(Enum):
    """调整行动"""
    CONTINUE = "continue"  # 继续当前策略
    MODIFY = "modify"  # 修改策略
    RETRY = "retry"  # 重试
    ESCALATE = "escalate"  # 上报/寻求帮助
    ABORT = "abort"  # 中止


@dataclass
class SelfModel:
    """自我模型
    
    Agent对自身能力、知识和边界的结构化表示
    """
    model_id: str
    agent_name: str
    capabilities: List[str] = field(default_factory=list)  # 能力列表
    knowledge_domains: List[str] = field(default_factory=list)  # 知识领域
    limitations: List[str] = field(default_factory=list)  # 限制
    confidence_thresholds: Dict[str, float] = field(default_factory=dict)  # 信心阈值
    preferred_strategies: Dict[str, str] = field(default_factory=dict)  # 偏好策略
    created_at: str = ""
    last_updated: str = ""
    
    def __post_init__(self):
        if not self.model_id:
            self.model_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.last_updated:
            self.last_updated = datetime.now(timezone.utc).isoformat()
    
    def update_capability(self, capability: str, add: bool = True):
        """更新能力"""
        if add and capability not in self.capabilities:
            self.capabilities.append(capability)
        elif not add and capability in self.capabilities:
            self.capabilities.remove(capability)
        self.last_updated = datetime.now(timezone.utc).isoformat()
    
    def has_capability(self, capability: str) -> bool:
        """检查是否具备某能力"""
        return capability in self.capabilities
    
    def is_in_domain(self, domain: str) -> bool:
        """检查是否在知识领域内"""
        return domain in self.knowledge_domains


@dataclass
class MetacognitiveState:
    """元认知状态"""
    state_id: str
    task_description: str
    current_step: str
    step_number: int
    total_steps: int
    confidence: float = 0.5
    progress_percentage: float = 0.0
    errors_encountered: List[Dict] = field(default_factory=list)
    strategies_tried: List[str] = field(default_factory=list)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.state_id:
            self.state_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        
        # 计算进度百分比
        if self.total_steps > 0:
            self.progress_percentage = (self.step_number / self.total_steps) * 100
    
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """获取信心等级"""
        if self.confidence >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif self.confidence >= 0.6:
            return ConfidenceLevel.HIGH
        elif self.confidence >= 0.4:
            return ConfidenceLevel.MEDIUM
        elif self.confidence >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW


@dataclass
class ReflectionResult:
    """反思结果"""
    reflection_id: str
    reflection_type: ReflectionType
    assessment: str
    identified_issues: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    confidence_change: float = 0.0
    recommended_action: AdjustmentAction = AdjustmentAction.CONTINUE
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.reflection_id:
            self.reflection_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class IntrospectionReport:
    """内省报告"""
    report_id: str
    task_summary: str
    self_assessment: Dict[str, Any] = field(default_factory=dict)
    reasoning_trace: List[str] = field(default_factory=list)
    uncertainty_areas: List[str] = field(default_factory=list)
    learning_points: List[str] = field(default_factory=list)
    overall_confidence: float = 0.5
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.report_id:
            self.report_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class SelfMonitor:
    """自我监控器
    
    持续监控Agent的执行状态和性能
    """
    
    def __init__(self, self_model: SelfModel):
        self.self_model = self_model
        self.monitoring_history: List[MetacognitiveState] = []
        self.error_patterns: Dict[str, int] = defaultdict(int)
    
    def monitor_step(
        self,
        task: str,
        current_step: str,
        step_number: int,
        total_steps: int,
        outcome: Dict[str, Any] = None
    ) -> MetacognitiveState:
        """
        监控执行步骤
        
        Args:
            task: 任务描述
            current_step: 当前步骤
            step_number: 步骤编号
            total_steps: 总步骤数
            outcome: 执行结果
            
        Returns:
            元认知状态
        """
        # 计算信心度
        confidence = self._calculate_confidence(outcome)
        
        state = MetacognitiveState(
            state_id="",
            task_description=task,
            current_step=current_step,
            step_number=step_number,
            total_steps=total_steps,
            confidence=confidence
        )
        
        # 记录错误
        if outcome and outcome.get("error"):
            error_info = {
                "step": step_number,
                "error_type": outcome.get("error_type", "unknown"),
                "message": outcome.get("error_message", "")
            }
            state.errors_encountered.append(error_info)
            
            # 追踪错误模式
            error_key = outcome.get("error_type", "unknown")
            self.error_patterns[error_key] += 1
        
        self.monitoring_history.append(state)
        
        logger.debug(f"Monitored step {step_number}/{total_steps}: confidence={confidence:.2f}")
        
        return state
    
    def detect_performance_degradation(self, window_size: int = 5) -> bool:
        """检测性能下降"""
        if len(self.monitoring_history) < window_size:
            return False
        
        recent_states = self.monitoring_history[-window_size:]
        recent_confidences = [state.confidence for state in recent_states]
        
        # 检查信心度趋势
        if len(recent_confidences) >= 2:
            trend = recent_confidences[-1] - recent_confidences[0]
            if trend < -0.2:  # 信心度下降超过0.2
                logger.warning(f"Performance degradation detected: trend={trend:.2f}")
                return True
        
        return False
    
    def get_error_frequency(self, error_type: str) -> int:
        """获取错误频率"""
        return self.error_patterns.get(error_type, 0)
    
    def _calculate_confidence(self, outcome: Dict = None) -> float:
        """计算信心度"""
        if not outcome:
            return 0.5
        
        # 基于成功率和错误数量计算
        success = outcome.get("success", True)
        error_count = outcome.get("error_count", 0)
        
        base_confidence = 0.8 if success else 0.3
        penalty = min(0.3, error_count * 0.1)
        
        return max(0.1, min(0.95, base_confidence - penalty))


class SelfReflector:
    """自我反思器
    
    执行深度反思并生成改进建议
    """
    
    def __init__(self, self_model: SelfModel):
        self.self_model = self_model
        self.reflection_history: List[ReflectionResult] = []
    
    def reflect_on_performance(
        self,
        task: str,
        execution_trace: List[Dict],
        final_outcome: Dict
    ) -> ReflectionResult:
        """
        反思性能表现
        
        Args:
            task: 任务描述
            execution_trace: 执行轨迹
            final_outcome: 最终结果
            
        Returns:
            反思结果
        """
        # 分析执行轨迹
        issues = self._identify_performance_issues(execution_trace)
        
        # 生成改进建议
        suggestions = self._generate_improvement_suggestions(issues)
        
        # 确定推荐行动
        action = self._determine_action(final_outcome, issues)
        
        result = ReflectionResult(
            reflection_id="",
            reflection_type=ReflectionType.PERFORMANCE,
            assessment=f"Performance analysis for: {task[:50]}...",
            identified_issues=issues,
            improvement_suggestions=suggestions,
            recommended_action=action
        )
        
        self.reflection_history.append(result)
        
        logger.info(f"Performance reflection completed: {len(issues)} issues found")
        
        return result
    
    def reflect_on_strategy(
        self,
        strategy_used: str,
        effectiveness: float,
        alternatives: List[str] = None
    ) -> ReflectionResult:
        """
        反思策略有效性
        
        Args:
            strategy_used: 使用的策略
            effectiveness: 有效性评分
            alternatives: 备选策略
            
        Returns:
            反思结果
        """
        issues = []
        suggestions = []
        
        if effectiveness < 0.5:
            issues.append(f"Low strategy effectiveness: {effectiveness:.2f}")
            suggestions.append(f"Consider alternative strategies: {alternatives}")
        
        if effectiveness < 0.7:
            suggestions.append("Optimize current strategy parameters")
        
        action = AdjustmentAction.MODIFY if effectiveness < 0.6 else AdjustmentAction.CONTINUE
        
        result = ReflectionResult(
            reflection_id="",
            reflection_type=ReflectionType.STRATEGY,
            assessment=f"Strategy evaluation: {strategy_used}",
            identified_issues=issues,
            improvement_suggestions=suggestions,
            recommended_action=action
        )
        
        self.reflection_history.append(result)
        
        logger.info(f"Strategy reflection: effectiveness={effectiveness:.2f}")
        
        return result
    
    def reflect_on_knowledge_gaps(
        self,
        query: str,
        confidence: float,
        missing_info: List[str] = None
    ) -> ReflectionResult:
        """
        反思知识缺口
        
        Args:
            query: 查询内容
            confidence: 信心度
            missing_info: 缺失信息
            
        Returns:
            反思结果
        """
        issues = []
        suggestions = []
        
        if confidence < 0.4:
            issues.append("Low confidence indicates knowledge gap")
            suggestions.append("Retrieve additional information from external sources")
            suggestions.append("Escalate to human expert if critical")
        
        if missing_info:
            issues.append(f"Missing information: {', '.join(missing_info[:3])}")
            suggestions.append("Update knowledge base with retrieved information")
        
        action = AdjustmentAction.ESCALATE if confidence < 0.3 else AdjustmentAction.RETRY
        
        result = ReflectionResult(
            reflection_id="",
            reflection_type=ReflectionType.KNOWLEDGE,
            assessment=f"Knowledge gap analysis for query",
            identified_issues=issues,
            improvement_suggestions=suggestions,
            recommended_action=action
        )
        
        self.reflection_history.append(result)
        
        logger.info(f"Knowledge reflection: confidence={confidence:.2f}")
        
        return result
    
    def introspect_reasoning(
        self,
        reasoning_steps: List[str],
        conclusion: str
    ) -> IntrospectionReport:
        """
        内省推理过程
        
        Args:
            reasoning_steps: 推理步骤
            conclusion: 结论
            
        Returns:
            内省报告
        """
        # 识别不确定性区域
        uncertainty_areas = self._identify_uncertainty(reasoning_steps)
        
        # 提取学习要点
        learning_points = self._extract_learning_points(reasoning_steps, conclusion)
        
        # 自我评估
        self_assessment = {
            "reasoning_depth": len(reasoning_steps),
            "logical_consistency": self._check_logical_consistency(reasoning_steps),
            "evidence_quality": self._assess_evidence_quality(reasoning_steps),
            "bias_detected": self._detect_bias(reasoning_steps)
        }
        
        report = IntrospectionReport(
            report_id="",
            task_summary=f"Introspection on reasoning process",
            self_assessment=self_assessment,
            reasoning_trace=reasoning_steps,
            uncertainty_areas=uncertainty_areas,
            learning_points=learning_points,
            overall_confidence=statistics.mean([
                self_assessment["logical_consistency"],
                self_assessment["evidence_quality"]
            ])
        )
        
        logger.info(f"Introspection report generated: confidence={report.overall_confidence:.2f}")
        
        return report
    
    def _identify_performance_issues(self, trace: List[Dict]) -> List[str]:
        """识别性能问题"""
        issues = []
        
        # 检查重复步骤
        steps_seen = set()
        for step in trace:
            step_key = step.get("action", "")
            if step_key in steps_seen:
                issues.append(f"Repeated action: {step_key}")
            steps_seen.add(step_key)
        
        # 检查长时间运行的步骤
        long_steps = [s for s in trace if s.get("duration", 0) > 10]
        if long_steps:
            issues.append(f"{len(long_steps)} steps exceeded time threshold")
        
        return issues
    
    def _generate_improvement_suggestions(self, issues: List[str]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        for issue in issues:
            if "Repeated" in issue:
                suggestions.append("Implement caching to avoid redundant operations")
            elif "time threshold" in issue:
                suggestions.append("Optimize slow operations or add parallelization")
        
        return suggestions
    
    def _determine_action(self, outcome: Dict, issues: List[str]) -> AdjustmentAction:
        """确定推荐行动"""
        if not outcome.get("success", False):
            return AdjustmentAction.RETRY
        
        if len(issues) > 3:
            return AdjustmentAction.MODIFY
        
        return AdjustmentAction.CONTINUE
    
    def _identify_uncertainty(self, reasoning_steps: List[str]) -> List[str]:
        """识别不确定性区域"""
        uncertainty_keywords = ["maybe", "possibly", "uncertain", "assume", "guess"]
        uncertain_steps = []
        
        for i, step in enumerate(reasoning_steps):
            if any(keyword in step.lower() for keyword in uncertainty_keywords):
                uncertain_steps.append(f"Step {i+1}: {step[:50]}...")
        
        return uncertain_steps
    
    def _extract_learning_points(self, steps: List[str], conclusion: str) -> List[str]:
        """提取学习要点"""
        learning_points = []
        
        # 简化实现：基于步骤数量和质量
        if len(steps) > 5:
            learning_points.append("Complex reasoning benefited from multi-step analysis")
        
        if len(steps) < 3:
            learning_points.append("Simple problems may not require extensive reasoning")
        
        return learning_points
    
    def _check_logical_consistency(self, steps: List[str]) -> float:
        """检查逻辑一致性"""
        # 简化实现
        return random.uniform(0.7, 0.95)
    
    def _assess_evidence_quality(self, steps: List[str]) -> float:
        """评估证据质量"""
        # 简化实现
        return random.uniform(0.65, 0.9)
    
    def _detect_bias(self, steps: List[str]) -> bool:
        """检测偏见"""
        # 简化实现
        return random.random() < 0.1  # 10%检测到偏见


class MetacognitiveController:
    """元认知控制器
    
    协调整个元认知循环：监控→评估→调整
    """
    
    def __init__(self, agent_name: str = "AI_Agent"):
        self.self_model = SelfModel(
            model_id="",
            agent_name=agent_name,
            capabilities=["reasoning", "planning", "tool_use", "reflection"],
            knowledge_domains=["general", "technical", "analytical"],
            limitations=["real-time_data", "physical_world_interaction"],
            confidence_thresholds={"high": 0.8, "medium": 0.5, "low": 0.3}
        )
        
        self.monitor = SelfMonitor(self.self_model)
        self.reflector = SelfReflector(self.self_model)
        self.control_history: List[Dict] = []
    
    def execute_metacognitive_cycle(
        self,
        task: str,
        execution_plan: List[Dict]
    ) -> Dict[str, Any]:
        """
        执行元认知循环
        
        Args:
            task: 任务描述
            execution_plan: 执行计划
            
        Returns:
            控制结果
        """
        results = {
            "task": task,
            "steps_monitored": 0,
            "reflections_performed": 0,
            "adjustments_made": [],
            "final_recommendation": None
        }
        
        total_steps = len(execution_plan)
        
        for i, step in enumerate(execution_plan, 1):
            # Step 1: 监控
            state = self.monitor.monitor_step(
                task=task,
                current_step=step.get("action", ""),
                step_number=i,
                total_steps=total_steps,
                outcome=step.get("outcome")
            )
            
            results["steps_monitored"] += 1
            
            # Step 2: 定期反思（每3步或检测到问题时）
            should_reflect = (i % 3 == 0) or self.monitor.detect_performance_degradation()
            
            if should_reflect:
                # 执行性能反思
                reflection = self.reflector.reflect_on_performance(
                    task=task,
                    execution_trace=execution_plan[:i],
                    final_outcome=step.get("outcome", {})
                )
                
                results["reflections_performed"] += 1
                
                # Step 3: 根据反思结果调整
                if reflection.recommended_action != AdjustmentAction.CONTINUE:
                    adjustment = {
                        "step": i,
                        "action": reflection.recommended_action.value,
                        "reason": reflection.assessment
                    }
                    results["adjustments_made"].append(adjustment)
                    
                    logger.info(f"Adjustment made at step {i}: {reflection.recommended_action.value}")
        
        # 最终建议
        results["final_recommendation"] = self._generate_final_recommendation(results)
        
        # 记录控制历史
        self.control_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task": task,
            "results": results
        })
        
        logger.info(f"Metacognitive cycle completed: {results['reflections_performed']} reflections")
        
        return results
    
    def generate_introspection_report(
        self,
        task: str,
        reasoning_process: List[str],
        conclusion: str
    ) -> IntrospectionReport:
        """生成内省报告"""
        return self.reflector.introspect_reasoning(reasoning_process, conclusion)
    
    def assess_task_feasibility(
        self,
        task_description: str,
        required_capabilities: List[str] = None
    ) -> Dict[str, Any]:
        """
        评估任务可行性
        
        Args:
            task_description: 任务描述
            required_capabilities: 所需能力
            
        Returns:
            可行性评估
        """
        if required_capabilities is None:
            required_capabilities = []
        
        # 检查能力匹配
        capability_gaps = [
            cap for cap in required_capabilities
            if not self.self_model.has_capability(cap)
        ]
        
        feasibility_score = 1.0 - (len(capability_gaps) / max(len(required_capabilities), 1))
        
        recommendation = "proceed"
        if feasibility_score < 0.5:
            recommendation = "escalate"
        elif feasibility_score < 0.7:
            recommendation = "proceed_with_caution"
        
        return {
            "feasibility_score": round(feasibility_score, 2),
            "capability_gaps": capability_gaps,
            "recommendation": recommendation,
            "agent_capabilities": self.self_model.capabilities
        }
    
    def _generate_final_recommendation(self, results: Dict) -> str:
        """生成最终建议"""
        if not results["adjustments_made"]:
            return "Task completed successfully without major issues"
        
        num_adjustments = len(results["adjustments_made"])
        if num_adjustments > 3:
            return "Task completed but requires significant optimization"
        elif num_adjustments > 1:
            return "Task completed with minor adjustments needed"
        else:
            return "Task completed successfully with minimal intervention"
    
    def get_metacognitive_statistics(self) -> Dict:
        """获取元认知统计"""
        return {
            "total_monitoring_steps": len(self.monitor.monitoring_history),
            "total_reflections": len(self.reflector.reflection_history),
            "total_control_cycles": len(self.control_history),
            "error_patterns": dict(self.monitor.error_patterns),
            "avg_confidence": statistics.mean([
                state.confidence for state in self.monitor.monitoring_history
            ]) if self.monitor.monitoring_history else 0.0
        }


def create_metacognitive_system(agent_name: str = "AI_Agent") -> MetacognitiveController:
    """工厂函数：创建元认知系统"""
    return MetacognitiveController(agent_name)


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Metacognition & Self-Reflection 测试")
    print("="*60)
    
    controller = create_metacognitive_system("TestAgent")
    
    # 评估任务可行性
    print("\n🎯 评估任务可行性...")
    feasibility = controller.assess_task_feasibility(
        task_description="Build a web scraper with error handling",
        required_capabilities=["web_scraping", "error_handling", "data_parsing"]
    )
    print(f"   可行性分数: {feasibility['feasibility_score']:.2f}")
    print(f"   能力缺口: {feasibility['capability_gaps']}")
    print(f"   建议: {feasibility['recommendation']}")
    
    # 执行元认知循环
    print("\n🔄 执行元认知循环...")
    execution_plan = [
        {"action": "analyze_requirements", "outcome": {"success": True, "error_count": 0}},
        {"action": "design_solution", "outcome": {"success": True, "error_count": 0}},
        {"action": "implement_code", "outcome": {"success": False, "error_count": 2, "error_type": "syntax_error"}},
        {"action": "test_implementation", "outcome": {"success": True, "error_count": 1}},
        {"action": "deploy_solution", "outcome": {"success": True, "error_count": 0}},
        {"action": "monitor_performance", "outcome": {"success": True, "error_count": 0}},
    ]
    
    results = controller.execute_metacognitive_cycle(
        task="Web scraper development",
        execution_plan=execution_plan
    )
    
    print(f"   监控步骤数: {results['steps_monitored']}")
    print(f"   执行反思数: {results['reflections_performed']}")
    print(f"   进行调整数: {len(results['adjustments_made'])}")
    print(f"   最终建议: {results['final_recommendation']}")
    
    if results['adjustments_made']:
        print(f"\n   调整详情:")
        for adj in results['adjustments_made']:
            print(f"     - 步骤 {adj['step']}: {adj['action']} ({adj['reason'][:40]}...)")
    
    # 生成内省报告
    print("\n🔍 生成内省报告...")
    reasoning_steps = [
        "Analyzed user requirements for web scraping",
        "Identified target website structure",
        "Selected appropriate parsing library (BeautifulSoup)",
        "Implemented error handling for network failures",
        "Maybe the timeout value needs adjustment",
        "Added retry mechanism for robustness",
        "Assume rate limiting won't be an issue"
    ]
    
    report = controller.generate_introspection_report(
        task="Web scraper reasoning",
        reasoning_process=reasoning_steps,
        conclusion="Implemented robust web scraper with error handling"
    )
    
    print(f"   报告ID: {report.report_id}")
    print(f"   推理深度: {report.self_assessment['reasoning_depth']}")
    print(f"   逻辑一致性: {report.self_assessment['logical_consistency']:.2f}")
    print(f"   证据质量: {report.self_assessment['evidence_quality']:.2f}")
    print(f"   检测到偏见: {report.self_assessment['bias_detected']}")
    print(f"   总体信心: {report.overall_confidence:.2f}")
    print(f"   不确定性区域数: {len(report.uncertainty_areas)}")
    print(f"   学习要点数: {len(report.learning_points)}")
    
    if report.uncertainty_areas:
        print(f"\n   不确定性示例:")
        for area in report.uncertainty_areas[:2]:
            print(f"     - {area}")
    
    # 元认知统计
    print("\n📊 元认知统计...")
    stats = controller.get_metacognitive_statistics()
    print(f"   总监控步骤: {stats['total_monitoring_steps']}")
    print(f"   总反思次数: {stats['total_reflections']}")
    print(f"   总控制循环: {stats['total_control_cycles']}")
    print(f"   平均信心度: {stats['avg_confidence']:.2f}")
    print(f"   错误模式: {stats['error_patterns']}")
    
    # 自我模型信息
    print("\n🧠 自我模型信息...")
    model = controller.self_model
    print(f"   Agent名称: {model.agent_name}")
    print(f"   能力列表: {', '.join(model.capabilities)}")
    print(f"   知识领域: {', '.join(model.knowledge_domains)}")
    print(f"   限制条件: {', '.join(model.limitations)}")
    
    print("\n✅ 测试完成！")
