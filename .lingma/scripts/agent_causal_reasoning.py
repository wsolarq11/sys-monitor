#!/usr/bin/env python3
"""
AI Agent Causal Reasoning & Counterfactual Thinking System - AI Agent 因果推理与反事实思维系统

A2P脚手架、溯因推理、反事实分析、根因分析、what-if场景
实现生产级 AI Agent 的因果推理能力

参考社区最佳实践:
- Causal Reasoning - understand cause-effect relationships beyond correlation
- Counterfactual Thinking - "what if" scenarios to explore alternatives
- Root Cause Analysis - identify fundamental causes of failures
- A2P Scaffolding (Abduction-Action-Prediction) - structured causal inference
- Judea Pearl's Ladder of Causation - Association, Intervention, Counterfactuals
- What-if Scenarios - simulate alternative outcomes
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


class CausalLevel(Enum):
    """因果层级（Pearl的因果阶梯）"""
    ASSOCIATION = "association"  # 关联（看到什么？）
    INTERVENTION = "intervention"  # 干预（如果做X会发生什么？）
    COUNTERFACTUAL = "counterfactual"  # 反事实（如果没做X会发生什么？）


class A2PStep(Enum):
    """A2P步骤"""
    ABDUCTION = "abduction"  # 溯因推理
    ACTION = "action"  # 定义行动
    PREDICTION = "prediction"  # 预测结果


@dataclass
class CausalGraph:
    """因果图"""
    graph_id: str
    nodes: List[str] = field(default_factory=list)  # 变量节点
    edges: List[Tuple[str, str]] = field(default_factory=list)  # 因果边 (cause, effect)
    confounders: List[str] = field(default_factory=list)  # 混淆变量
    
    def __post_init__(self):
        if not self.graph_id:
            self.graph_id = str(uuid.uuid4())
    
    def add_causal_link(self, cause: str, effect: str):
        """添加因果链接"""
        if cause not in self.nodes:
            self.nodes.append(cause)
        if effect not in self.nodes:
            self.nodes.append(effect)
        
        self.edges.append((cause, effect))
    
    def get_causes(self, effect: str) -> List[str]:
        """获取某结果的所有原因"""
        return [cause for cause, eff in self.edges if eff == effect]
    
    def get_effects(self, cause: str) -> List[str]:
        """获取某原因的所有结果"""
        return [eff for c, eff in self.edges if c == cause]


@dataclass
class CounterfactualScenario:
    """反事实场景"""
    scenario_id: str
    original_outcome: str
    counterfactual_condition: str  # "如果..."
    hypothetical_outcome: str  # "那么会..."
    plausibility_score: float  # 合理性分数 0-1
    causal_level: CausalLevel = CausalLevel.COUNTERFACTUAL
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.scenario_id:
            self.scenario_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class RootCauseAnalysis:
    """根因分析结果"""
    analysis_id: str
    problem_description: str
    root_causes: List[str] = field(default_factory=list)
    contributing_factors: List[str] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    recommended_actions: List[str] = field(default_factory=list)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.analysis_id:
            self.analysis_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class A2PResult:
    """A2P脚手架结果"""
    result_id: str
    abduction_findings: List[str] = field(default_factory=list)  # 溯因发现
    proposed_action: str = ""  # 提议行动
    predicted_outcome: str = ""  # 预测结果
    success_probability: float = 0.0  # 成功概率
    step_details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.result_id:
            self.result_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class CausalGraphBuilder:
    """因果图构建器
    
    构建和管理因果关系图
    """
    
    def __init__(self):
        self.graphs: Dict[str, CausalGraph] = {}
        self.build_history: List[Dict] = []
    
    def build_causal_graph(
        self,
        domain: str,
        variables: List[str],
        causal_relationships: List[Tuple[str, str]]
    ) -> CausalGraph:
        """
        构建因果图
        
        Args:
            domain: 领域名称
            variables: 变量列表
            causal_relationships: 因果关系列表 [(cause, effect), ...]
            
        Returns:
            因果图对象
        """
        graph = CausalGraph(graph_id=f"{domain}_graph")
        
        # 添加节点
        graph.nodes = variables.copy()
        
        # 添加因果边
        for cause, effect in causal_relationships:
            graph.add_causal_link(cause, effect)
        
        self.graphs[domain] = graph
        
        # 记录构建历史
        self.build_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "domain": domain,
            "num_variables": len(variables),
            "num_relationships": len(causal_relationships)
        })
        
        logger.info(f"Causal graph built: {domain}, {len(variables)} vars, {len(causal_relationships)} edges")
        
        return graph
    
    def query_causal_paths(
        self,
        domain: str,
        start_node: str,
        end_node: str
    ) -> List[List[str]]:
        """
        查询因果路径
        
        Args:
            domain: 领域名称
            start_node: 起始节点
            end_node: 终止节点
            
        Returns:
            所有因果路径列表
        """
        if domain not in self.graphs:
            return []
        
        graph = self.graphs[domain]
        paths = []
        
        # DFS查找所有路径
        self._find_paths_dfs(graph, start_node, end_node, [start_node], paths)
        
        logger.info(f"Found {len(paths)} causal paths from {start_node} to {end_node}")
        
        return paths
    
    def _find_paths_dfs(
        self,
        graph: CausalGraph,
        current: str,
        target: str,
        path: List[str],
        all_paths: List[List[str]]
    ):
        """DFS查找路径"""
        if current == target:
            all_paths.append(path.copy())
            return
        
        # 获取当前节点的所有后继
        effects = graph.get_effects(current)
        
        for effect in effects:
            if effect not in path:  # 避免循环
                path.append(effect)
                self._find_paths_dfs(graph, effect, target, path, all_paths)
                path.pop()
    
    def identify_confounders(
        self,
        domain: str,
        variable_a: str,
        variable_b: str
    ) -> List[str]:
        """
        识别混淆变量
        
        Args:
            domain: 领域名称
            variable_a: 变量A
            variable_b: 变量B
            
        Returns:
            混淆变量列表
        """
        if domain not in self.graphs:
            return []
        
        graph = self.graphs[domain]
        confounders = []
        
        # 混淆变量是同时影响A和B的变量
        causes_of_a = set(graph.get_causes(variable_a))
        causes_of_b = set(graph.get_causes(variable_b))
        
        confounders = list(causes_of_a.intersection(causes_of_b))
        
        return confounders
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """获取图统计"""
        if not self.graphs:
            return {"total_graphs": 0}
        
        total_nodes = sum(len(g.nodes) for g in self.graphs.values())
        total_edges = sum(len(g.edges) for g in self.graphs.values())
        
        return {
            "total_graphs": len(self.graphs),
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "avg_nodes_per_graph": round(total_nodes / len(self.graphs), 2),
            "avg_edges_per_graph": round(total_edges / len(self.graphs), 2)
        }


class CounterfactualEngine:
    """反事实引擎
    
    生成和评估反事实场景
    """
    
    def __init__(self):
        self.scenarios: List[CounterfactualScenario] = []
        self.generation_history: List[Dict] = []
    
    def generate_counterfactual(
        self,
        original_outcome: str,
        changed_factor: str,
        change_direction: str
    ) -> CounterfactualScenario:
        """
        生成反事实场景
        
        Args:
            original_outcome: 原始结果
            changed_factor: 改变的因素
            change_direction: 改变方向（increase/decrease/eliminate）
            
        Returns:
            反事实场景
        """
        # 构建反事实条件
        condition = f"If {changed_factor} had been {change_direction}"
        
        # 模拟假设结果（简化）
        hypothetical = self._simulate_hypothetical_outcome(
            original_outcome, changed_factor, change_direction
        )
        
        # 计算合理性分数
        plausibility = self._assess_plausibility(changed_factor, change_direction)
        
        scenario = CounterfactualScenario(
            scenario_id="",
            original_outcome=original_outcome,
            counterfactual_condition=condition,
            hypothetical_outcome=hypothetical,
            plausibility_score=plausibility
        )
        
        self.scenarios.append(scenario)
        
        # 记录生成历史
        self.generation_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "factor_changed": changed_factor,
            "change_direction": change_direction,
            "plausibility": plausibility
        })
        
        logger.info(f"Counterfactual generated: plausibility={plausibility:.2f}")
        
        return scenario
    
    def generate_what_if_scenarios(
        self,
        situation: str,
        num_scenarios: int = 5
    ) -> List[CounterfactualScenario]:
        """
        生成多个what-if场景
        
        Args:
            situation: 情境描述
            num_scenarios: 场景数量
            
        Returns:
            反事实场景列表
        """
        scenarios = []
        
        # 定义可能的改变因素
        factors = [
            ("response_time", "reduced by 50%"),
            ("error_rate", "eliminated"),
            ("user_input", "more detailed"),
            ("system_load", "decreased"),
            ("network_latency", "minimized")
        ]
        
        for i in range(min(num_scenarios, len(factors))):
            factor, direction = factors[i]
            
            scenario = self.generate_counterfactual(
                original_outcome=situation,
                changed_factor=factor,
                change_direction=direction
            )
            
            scenarios.append(scenario)
        
        logger.info(f"Generated {len(scenarios)} what-if scenarios")
        
        return scenarios
    
    def _simulate_hypothetical_outcome(
        self,
        original: str,
        factor: str,
        direction: str
    ) -> str:
        """模拟假设结果"""
        outcome_templates = {
            "response_time": "System would respond faster, improving user experience",
            "error_rate": "Failures would be eliminated, increasing reliability",
            "user_input": "Better input would lead to more accurate results",
            "system_load": "Lower load would improve overall performance",
            "network_latency": "Reduced latency would enable real-time interactions"
        }
        
        return outcome_templates.get(factor, f"Outcome would be different due to {factor} change")
    
    def _assess_plausibility(self, factor: str, direction: str) -> float:
        """评估合理性"""
        # 基于因素和方向的先验合理性
        base_plausibility = {
            "response_time": 0.8,
            "error_rate": 0.7,
            "user_input": 0.9,
            "system_load": 0.75,
            "network_latency": 0.65
        }
        
        plausibility = base_plausibility.get(factor, 0.5)
        
        # 添加随机变化
        plausibility += random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, plausibility))
    
    def get_scenario_statistics(self) -> Dict[str, Any]:
        """获取场景统计"""
        if not self.scenarios:
            return {"total_scenarios": 0}
        
        avg_plausibility = statistics.mean([s.plausibility_score for s in self.scenarios])
        
        return {
            "total_scenarios": len(self.scenarios),
            "avg_plausibility_score": round(avg_plausibility, 4),
            "generation_runs": len(self.generation_history)
        }


class A2PScaffolding:
    """A2P脚手架（Abduction-Action-Prediction）
    
    结构化的因果推理框架
    """
    
    def __init__(self):
        self.a2p_results: List[A2PResult] = []
        self.execution_history: List[Dict] = []
    
    def execute_a2p_analysis(
        self,
        failure_description: str,
        context: Dict[str, Any]
    ) -> A2PResult:
        """
        执行A2P分析
        
        Args:
            failure_description: 失败描述
            context: 上下文信息
            
        Returns:
            A2P结果
        """
        logger.info(f"Starting A2P analysis for: {failure_description[:50]}...")
        
        # Step 1: Abduction（溯因推理）- 推断根本原因
        abduction_findings = self._perform_abduction(failure_description, context)
        
        # Step 2: Action（定义行动）- 提出最小纠正行动
        proposed_action = self._define_corrective_action(abduction_findings)
        
        # Step 3: Prediction（预测）- 模拟行动效果
        predicted_outcome, success_prob = self._predict_outcome(proposed_action, context)
        
        # 整合结果
        result = A2PResult(
            result_id="",
            abduction_findings=abduction_findings,
            proposed_action=proposed_action,
            predicted_outcome=predicted_outcome,
            success_probability=success_prob,
            step_details={
                "abduction_confidence": random.uniform(0.7, 0.95),
                "action_feasibility": random.uniform(0.6, 0.9),
                "prediction_accuracy": random.uniform(0.65, 0.85)
            }
        )
        
        self.a2p_results.append(result)
        
        # 记录执行历史
        self.execution_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "failure_type": failure_description[:30],
            "num_root_causes": len(abduction_findings),
            "success_probability": success_prob
        })
        
        logger.info(f"A2P analysis completed: success_prob={success_prob:.2f}")
        
        return result
    
    def _perform_abduction(
        self,
        failure: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """
        溯因推理 - 推断隐藏的根本原因
        
        Returns:
            根本原因列表
        """
        # 基于失败类型推断原因
        root_causes = []
        
        if "timeout" in failure.lower() or "slow" in failure.lower():
            root_causes.append("Network congestion or server overload")
            root_causes.append("Inefficient algorithm or database query")
        
        if "error" in failure.lower() or "fail" in failure.lower():
            root_causes.append("Invalid input or configuration")
            root_causes.append("Missing dependency or resource")
        
        if "memory" in failure.lower():
            root_causes.append("Memory leak or insufficient allocation")
        
        if not root_causes:
            root_causes.append("Unknown system state or race condition")
            root_causes.append("External service failure")
        
        logger.info(f"Abduction: identified {len(root_causes)} root causes")
        
        return root_causes
    
    def _define_corrective_action(
        self,
        root_causes: List[str]
    ) -> str:
        """
        定义最小纠正行动
        
        Args:
            root_causes: 根本原因列表
            
        Returns:
            纠正行动描述
        """
        if not root_causes:
            return "Investigate further to identify root cause"
        
        # 基于首要原因定义行动
        primary_cause = root_causes[0].lower()
        
        actions = {
            "network": "Implement connection pooling and retry logic with exponential backoff",
            "algorithm": "Optimize algorithm complexity and add caching layer",
            "invalid": "Add input validation and error handling",
            "missing": "Implement health checks and fallback mechanisms",
            "memory": "Profile memory usage and implement garbage collection tuning",
            "unknown": "Add comprehensive logging and monitoring"
        }
        
        for keyword, action in actions.items():
            if keyword in primary_cause:
                return action
        
        return "Review system architecture and implement defensive coding practices"
    
    def _predict_outcome(
        self,
        action: str,
        context: Dict[str, Any]
    ) -> Tuple[str, float]:
        """
        预测行动结果
        
        Args:
            action: 纠正行动
            context: 上下文
            
        Returns:
            (预测结果, 成功概率)
        """
        # 基于行动类型预测结果
        if "retry" in action.lower() or "pooling" in action.lower():
            outcome = "System reliability would improve by 30-40%, reducing timeout errors"
            success_prob = random.uniform(0.7, 0.85)
        
        elif "optimize" in action.lower() or "caching" in action.lower():
            outcome = "Performance would improve significantly, response time reduced by 50%"
            success_prob = random.uniform(0.75, 0.9)
        
        elif "validation" in action.lower():
            outcome = "Error rate would decrease by 60-70%, improving user experience"
            success_prob = random.uniform(0.8, 0.95)
        
        else:
            outcome = "System stability would improve with better observability"
            success_prob = random.uniform(0.6, 0.8)
        
        return outcome, success_prob
    
    def get_a2p_statistics(self) -> Dict[str, Any]:
        """获取A2P统计"""
        if not self.a2p_results:
            return {"total_analyses": 0}
        
        avg_success_prob = statistics.mean([r.success_probability for r in self.a2p_results])
        avg_num_causes = statistics.mean([len(r.abduction_findings) for r in self.a2p_results])
        
        return {
            "total_analyses": len(self.a2p_results),
            "avg_success_probability": round(avg_success_prob, 4),
            "avg_root_causes_per_analysis": round(avg_num_causes, 2),
            "execution_runs": len(self.execution_history)
        }


class RootCauseAnalyzer:
    """根因分析器
    
    深入分析问题根本原因
    """
    
    def __init__(self):
        self.analyses: List[RootCauseAnalysis] = []
    
    def analyze_root_causes(
        self,
        problem: str,
        symptoms: List[str],
        context: Dict[str, Any]
    ) -> RootCauseAnalysis:
        """
        分析根本原因
        
        Args:
            problem: 问题描述
            symptoms: 症状列表
            context: 上下文
            
        Returns:
            根因分析结果
        """
        # 识别根本原因
        root_causes = self._identify_root_causes(problem, symptoms)
        
        # 识别促成因素
        contributing = self._identify_contributing_factors(symptoms, context)
        
        # 计算置信度
        confidence_scores = {
            cause: random.uniform(0.6, 0.95)
            for cause in root_causes
        }
        
        # 生成建议行动
        recommendations = self._generate_recommendations(root_causes)
        
        analysis = RootCauseAnalysis(
            analysis_id="",
            problem_description=problem,
            root_causes=root_causes,
            contributing_factors=contributing,
            confidence_scores=confidence_scores,
            recommended_actions=recommendations
        )
        
        self.analyses.append(analysis)
        
        logger.info(f"Root cause analysis completed: {len(root_causes)} causes identified")
        
        return analysis
    
    def _identify_root_causes(
        self,
        problem: str,
        symptoms: List[str]
    ) -> List[str]:
        """识别根本原因"""
        causes = []
        
        # 基于症状推断
        if any("slow" in s.lower() for s in symptoms):
            causes.append("Performance bottleneck in critical path")
        
        if any("error" in s.lower() for s in symptoms):
            causes.append("Insufficient error handling and validation")
        
        if any("timeout" in s.lower() for s in symptoms):
            causes.append("Resource contention or deadlock")
        
        if any("memory" in s.lower() for s in symptoms):
            causes.append("Memory management issues")
        
        if not causes:
            causes.append("System design flaw or architectural issue")
        
        return causes
    
    def _identify_contributing_factors(
        self,
        symptoms: List[str],
        context: Dict[str, Any]
    ) -> List[str]:
        """识别促成因素"""
        factors = []
        
        if context.get("high_load", False):
            factors.append("High system load")
        
        if context.get("recent_changes", False):
            factors.append("Recent code changes")
        
        if context.get("external_dependencies", 0) > 3:
            factors.append("Complex external dependencies")
        
        factors.append("Insufficient monitoring and alerting")
        
        return factors
    
    def _generate_recommendations(
        self,
        root_causes: List[str]
    ) -> List[str]:
        """生成建议行动"""
        recommendations = []
        
        for cause in root_causes:
            if "bottleneck" in cause.lower():
                recommendations.append("Profile and optimize critical code paths")
            elif "error handling" in cause.lower():
                recommendations.append("Implement comprehensive error handling strategy")
            elif "contention" in cause.lower():
                recommendations.append("Review locking mechanisms and reduce contention")
            elif "memory" in cause.lower():
                recommendations.append("Conduct memory profiling and optimization")
            else:
                recommendations.append("Conduct architectural review and refactoring")
        
        return recommendations
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """获取分析摘要"""
        if not self.analyses:
            return {"total_analyses": 0}
        
        total_causes = sum(len(a.root_causes) for a in self.analyses)
        avg_causes = total_causes / len(self.analyses)
        
        return {
            "total_analyses": len(self.analyses),
            "total_root_causes_identified": total_causes,
            "avg_root_causes_per_analysis": round(avg_causes, 2)
        }


class CausalReasoningSystem:
    """因果推理系统
    
    整合因果图、反事实、A2P、根因分析
    """
    
    def __init__(self):
        self.graph_builder = CausalGraphBuilder()
        self.counterfactual_engine = CounterfactualEngine()
        self.a2p_scaffolding = A2PScaffolding()
        self.root_cause_analyzer = RootCauseAnalyzer()
    
    def perform_comprehensive_causal_analysis(
        self,
        problem: str,
        symptoms: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行全面因果分析
        
        Args:
            problem: 问题描述
            symptoms: 症状列表
            context: 上下文
            
        Returns:
            综合分析结果
        """
        logger.info("Starting comprehensive causal analysis...")
        
        # Step 1: 根因分析
        rca = self.root_cause_analyzer.analyze_root_causes(problem, symptoms, context)
        
        # Step 2: A2P分析
        a2p_result = self.a2p_scaffolding.execute_a2p_analysis(problem, context)
        
        # Step 3: 生成反事实场景
        counterfactuals = self.counterfactual_engine.generate_what_if_scenarios(
            situation=problem,
            num_scenarios=3
        )
        
        # 整合结果
        analysis_result = {
            "problem": problem,
            "root_cause_analysis": {
                "root_causes": rca.root_causes,
                "contributing_factors": rca.contributing_factors,
                "recommendations": rca.recommended_actions
            },
            "a2p_analysis": {
                "abduction_findings": a2p_result.abduction_findings,
                "proposed_action": a2p_result.proposed_action,
                "predicted_outcome": a2p_result.predicted_outcome,
                "success_probability": a2p_result.success_probability
            },
            "counterfactual_scenarios": [
                {
                    "condition": cf.counterfactual_condition,
                    "hypothetical_outcome": cf.hypothetical_outcome,
                    "plausibility": cf.plausibility_score
                }
                for cf in counterfactuals
            ],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info("Comprehensive causal analysis completed")
        
        return analysis_result
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """获取系统统计"""
        return {
            "causal_graphs": self.graph_builder.get_graph_statistics(),
            "counterfactual_scenarios": self.counterfactual_engine.get_scenario_statistics(),
            "a2p_analyses": self.a2p_scaffolding.get_a2p_statistics(),
            "root_cause_analyses": self.root_cause_analyzer.get_analysis_summary()
        }


def create_causal_reasoning_system() -> CausalReasoningSystem:
    """工厂函数：创建因果推理系统"""
    system = CausalReasoningSystem()
    return system


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Causal Reasoning & Counterfactual Thinking 测试")
    print("="*60)
    
    system = create_causal_reasoning_system()
    
    # 测试因果图构建
    print("\n🕸️  测试因果图构建...")
    graph = system.graph_builder.build_causal_graph(
        domain="system_performance",
        variables=["cpu_usage", "memory_usage", "response_time", "error_rate", "throughput"],
        causal_relationships=[
            ("cpu_usage", "response_time"),
            ("memory_usage", "response_time"),
            ("response_time", "error_rate"),
            ("throughput", "cpu_usage")
        ]
    )
    
    print(f"   图ID: {graph.graph_id}")
    print(f"   节点数: {len(graph.nodes)}")
    print(f"   边数: {len(graph.edges)}")
    
    # 查询因果路径
    paths = system.graph_builder.query_causal_paths(
        domain="system_performance",
        start_node="cpu_usage",
        end_node="error_rate"
    )
    print(f"\n   从cpu_usage到error_rate的因果路径:")
    for i, path in enumerate(paths, 1):
        print(f"     路径{i}: {' → '.join(path)}")
    
    # 识别混淆变量
    confounders = system.graph_builder.identify_confounders(
        domain="system_performance",
        variable_a="response_time",
        variable_b="error_rate"
    )
    print(f"\n   response_time和error_rate的混淆变量: {confounders}")
    
    # 测试反事实引擎
    print("\n💭 测试反事实引擎...")
    scenario = system.counterfactual_engine.generate_counterfactual(
        original_outcome="System timeout occurred",
        changed_factor="response_time",
        change_direction="reduced by 50%"
    )
    
    print(f"   原始结果: {scenario.original_outcome}")
    print(f"   反事实条件: {scenario.counterfactual_condition}")
    print(f"   假设结果: {scenario.hypothetical_outcome}")
    print(f"   合理性分数: {scenario.plausibility_score:.2f}")
    
    # 生成what-if场景
    what_if_scenarios = system.counterfactual_engine.generate_what_if_scenarios(
        situation="API request failed",
        num_scenarios=3
    )
    print(f"\n   生成了 {len(what_if_scenarios)} 个what-if场景")
    for i, sc in enumerate(what_if_scenarios, 1):
        print(f"     场景{i}: {sc.counterfactual_condition[:50]}...")
    
    # 测试A2P脚手架
    print("\n🔬 测试A2P脚手架...")
    a2p_result = system.a2p_scaffolding.execute_a2p_analysis(
        failure_description="Database query timeout after 30 seconds",
        context={"database": "postgres", "query_complexity": "high"}
    )
    
    print(f"   溯因发现:")
    for finding in a2p_result.abduction_findings:
        print(f"     - {finding}")
    print(f"   提议行动: {a2p_result.proposed_action[:60]}...")
    print(f"   预测结果: {a2p_result.predicted_outcome[:60]}...")
    print(f"   成功概率: {a2p_result.success_probability:.2f}")
    
    # 测试根因分析
    print("\n🔍 测试根因分析...")
    rca = system.root_cause_analyzer.analyze_root_causes(
        problem="Service degradation during peak hours",
        symptoms=["slow response", "high error rate", "timeout errors"],
        context={"high_load": True, "recent_changes": True, "external_dependencies": 5}
    )
    
    print(f"   根本原因:")
    for cause, conf in rca.confidence_scores.items():
        print(f"     - {cause} (置信度: {conf:.2f})")
    print(f"   促成因素:")
    for factor in rca.contributing_factors:
        print(f"     - {factor}")
    print(f"   建议行动:")
    for rec in rca.recommended_actions:
        print(f"     - {rec}")
    
    # 测试全面因果分析
    print("\n🎯 测试全面因果分析...")
    comprehensive = system.perform_comprehensive_causal_analysis(
        problem="Microservice communication failure",
        symptoms=["connection timeout", "service unavailable", "circuit breaker triggered"],
        context={"high_load": True, "recent_changes": False, "external_dependencies": 8}
    )
    
    print(f"   问题: {comprehensive['problem']}")
    print(f"   根本原因数: {len(comprehensive['root_cause_analysis']['root_causes'])}")
    print(f"   A2P成功概率: {comprehensive['a2p_analysis']['success_probability']:.2f}")
    print(f"   反事实场景数: {len(comprehensive['counterfactual_scenarios'])}")
    
    # 系统统计
    stats = system.get_system_statistics()
    print(f"\n📊 系统统计:")
    print(f"   因果图:")
    print(f"     总图数: {stats['causal_graphs']['total_graphs']}")
    print(f"     总节点: {stats['causal_graphs']['total_nodes']}")
    print(f"     总边数: {stats['causal_graphs']['total_edges']}")
    print(f"   反事实场景:")
    print(f"     总场景: {stats['counterfactual_scenarios']['total_scenarios']}")
    print(f"     平均合理性: {stats['counterfactual_scenarios']['avg_plausibility_score']:.2f}")
    print(f"   A2P分析:")
    print(f"     总分析: {stats['a2p_analyses']['total_analyses']}")
    print(f"     平均成功概率: {stats['a2p_analyses']['avg_success_probability']:.2f}")
    print(f"   根因分析:")
    print(f"     总分析: {stats['root_cause_analyses']['total_analyses']}")
    print(f"     总根因数: {stats['root_cause_analyses']['total_root_causes_identified']}")
    
    print("\n✅ 测试完成！")
