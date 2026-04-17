#!/usr/bin/env python3
"""
AI Agent Causal Reasoning & Counterfactual Thinking System - AI Agent 因果推理与反事实思维系统

因果图构建、反事实推理、根因分析、干预模拟
实现生产级 AI Agent 的因果认知框架

参考社区最佳实践:
- Causal graph construction and inference
- Counterfactual reasoning (What-if analysis)
- Root cause analysis (RCA) with causal chains
- Intervention simulation and effect prediction
- Abduction-Action-Prediction (A2P) framework
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


class CausalRelationType(Enum):
    """因果关系类型"""
    DIRECT_CAUSATION = "direct_causation"  # 直接因果
    INDIRECT_CAUSATION = "indirect_causation"  # 间接因果
    CONFOUNDING = "confounding"  # 混杂因素
    MEDIATION = "mediation"  # 中介效应
    MODERATION = "moderation"  # 调节效应


class CounterfactualType(Enum):
    """反事实类型"""
    ACTION_BASED = "action_based"  # 基于行动的反事实
    EVENT_BASED = "event_based"  # 基于事件的反事实
    POLICY_BASED = "policy_based"  # 基于策略的反事实


class RCAStatus(Enum):
    """根因分析状态"""
    INITIATED = "initiated"
    DATA_COLLECTION = "data_collection"
    CAUSAL_GRAPH_BUILT = "causal_graph_built"
    ROOT_CAUSES_IDENTIFIED = "root_causes_identified"
    VALIDATION_COMPLETE = "validation_complete"
    COMPLETED = "completed"


@dataclass
class CausalNode:
    """因果节点"""
    node_id: str
    name: str
    node_type: str  # variable/event/action/outcome
    value: Any = None
    probability: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.node_id:
            self.node_id = str(uuid.uuid4())


@dataclass
class CausalEdge:
    """因果边"""
    edge_id: str
    source_node_id: str
    target_node_id: str
    relation_type: CausalRelationType
    strength: float  # 0-1
    description: str = ""
    evidence: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.edge_id:
            self.edge_id = str(uuid.uuid4())


@dataclass
class CausalGraph:
    """因果图"""
    graph_id: str
    nodes: List[CausalNode] = field(default_factory=list)
    edges: List[CausalEdge] = field(default_factory=list)
    created_at: str = ""
    
    def __post_init__(self):
        if not self.graph_id:
            self.graph_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
    
    def add_node(self, node: CausalNode):
        self.nodes.append(node)
    
    def add_edge(self, edge: CausalEdge):
        self.edges.append(edge)
    
    def get_parents(self, node_id: str) -> List[CausalEdge]:
        """获取父节点边"""
        return [e for e in self.edges if e.target_node_id == node_id]
    
    def get_children(self, node_id: str) -> List[CausalEdge]:
        """获取子节点边"""
        return [e for e in self.edges if e.source_node_id == node_id]


@dataclass
class CounterfactualScenario:
    """反事实场景"""
    scenario_id: str
    scenario_type: CounterfactualType
    original_state: Dict[str, Any]
    counterfactual_state: Dict[str, Any]
    intervention: str
    predicted_outcome: Dict[str, Any]
    confidence: float
    reasoning_chain: List[str] = field(default_factory=list)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class RootCause:
    """根因"""
    root_cause_id: str
    description: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    causal_path: List[str] = field(default_factory=list)
    impact_score: float = 0.0
    remediation_suggestions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.root_cause_id:
            self.root_cause_id = str(uuid.uuid4())


@dataclass
class RCAReport:
    """根因分析报告"""
    report_id: str
    incident_id: str
    status: RCAStatus
    root_causes: List[RootCause] = field(default_factory=list)
    causal_graph: Optional[CausalGraph] = None
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    completed_at: str = ""
    
    def __post_init__(self):
        if not self.report_id:
            self.report_id = str(uuid.uuid4())
        if not self.completed_at:
            self.completed_at = datetime.now(timezone.utc).isoformat()


class CausalGraphBuilder:
    """因果图构建器
    
    从数据和领域知识构建因果图
    """
    
    def __init__(self):
        self.graph_history: List[CausalGraph] = []
    
    def build_causal_graph(
        self,
        variables: List[Dict[str, Any]],
        domain_knowledge: List[Dict[str, Any]] = None
    ) -> CausalGraph:
        """
        构建因果图
        
        Args:
            variables: 变量列表
            domain_knowledge: 领域知识
            
        Returns:
            因果图
        """
        graph = CausalGraph(graph_id=str(uuid.uuid4()))
        
        # Step 1: 创建节点
        for var in variables:
            node = CausalNode(
                node_id="",
                name=var["name"],
                node_type=var.get("type", "variable"),
                value=var.get("value"),
                probability=var.get("probability", 1.0),
                metadata=var.get("metadata", {})
            )
            graph.add_node(node)
        
        # Step 2: 基于领域知识添加边
        if domain_knowledge:
            for knowledge in domain_knowledge:
                edge = CausalEdge(
                    edge_id="",
                    source_node_id=self._find_node_id(graph, knowledge["source"]),
                    target_node_id=self._find_node_id(graph, knowledge["target"]),
                    relation_type=CausalRelationType(knowledge.get("relation_type", "direct_causation")),
                    strength=knowledge.get("strength", 0.5),
                    description=knowledge.get("description", ""),
                    evidence=knowledge.get("evidence", [])
                )
                graph.add_edge(edge)
        
        # Step 3: 基于数据发现因果关系（简化）
        self._discover_causal_relations(graph, variables)
        
        self.graph_history.append(graph)
        
        logger.info(f"Causal graph built: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        
        return graph
    
    def _find_node_id(self, graph: CausalGraph, node_name: str) -> str:
        """查找节点ID"""
        for node in graph.nodes:
            if node.name == node_name:
                return node.node_id
        return ""
    
    def _discover_causal_relations(self, graph: CausalGraph, variables: List[Dict]):
        """基于数据发现因果关系（简化实现）"""
        # 在实际应用中，这里应使用因果发现算法（如PC算法、GES等）
        # 这里仅做模拟
        pass


class CounterfactualEngine:
    """反事实引擎
    
    执行反事实推理和What-if分析
    """
    
    def __init__(self):
        self.scenario_history: List[CounterfactualScenario] = []
    
    def generate_counterfactual(
        self,
        causal_graph: CausalGraph,
        intervention: str,
        intervention_details: Dict[str, Any]
    ) -> CounterfactualScenario:
        """
        生成反事实场景
        
        Args:
            causal_graph: 因果图
            intervention: 干预描述
            intervention_details: 干预详情
            
        Returns:
            反事实场景
        """
        # Step 1: 确定原始状态
        original_state = self._extract_current_state(causal_graph)
        
        # Step 2: 应用干预
        counterfactual_state = self._apply_intervention(
            original_state, intervention, intervention_details
        )
        
        # Step 3: 预测结果
        predicted_outcome = self._predict_outcome(
            causal_graph, counterfactual_state
        )
        
        # Step 4: 构建推理链
        reasoning_chain = self._build_reasoning_chain(
            causal_graph, intervention, predicted_outcome
        )
        
        # 创建场景
        scenario = CounterfactualScenario(
            scenario_id=str(uuid.uuid4()),
            scenario_type=CounterfactualType.ACTION_BASED,
            original_state=original_state,
            counterfactual_state=counterfactual_state,
            intervention=intervention,
            predicted_outcome=predicted_outcome,
            confidence=random.uniform(0.7, 0.95),
            reasoning_chain=reasoning_chain
        )
        
        self.scenario_history.append(scenario)
        
        logger.info(f"Counterfactual scenario generated: {intervention}")
        
        return scenario
    
    def compare_scenarios(
        self,
        scenarios: List[CounterfactualScenario]
    ) -> Dict[str, Any]:
        """
        比较多个反事实场景
        
        Args:
            scenarios: 场景列表
            
        Returns:
            比较结果
        """
        if not scenarios:
            return {}
        
        comparison = {
            "scenarios_compared": len(scenarios),
            "best_scenario": None,
            "outcome_differences": {},
            "recommendation": ""
        }
        
        # 找出最佳场景（基于预期收益）
        best_scenario = max(
            scenarios,
            key=lambda s: s.predicted_outcome.get("expected_benefit", 0)
        )
        
        comparison["best_scenario"] = {
            "scenario_id": best_scenario.scenario_id[:8],
            "intervention": best_scenario.intervention,
            "confidence": best_scenario.confidence
        }
        
        # 计算差异
        for outcome_key in best_scenario.predicted_outcome.keys():
            values = [s.predicted_outcome.get(outcome_key, 0) for s in scenarios]
            comparison["outcome_differences"][outcome_key] = {
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "std": statistics.stdev(values) if len(values) > 1 else 0
            }
        
        comparison["recommendation"] = f"Recommend intervention: {best_scenario.intervention}"
        
        logger.info(f"Compared {len(scenarios)} scenarios, best: {best_scenario.intervention}")
        
        return comparison
    
    def _extract_current_state(self, graph: CausalGraph) -> Dict[str, Any]:
        """提取当前状态"""
        return {node.name: node.value for node in graph.nodes if node.value is not None}
    
    def _apply_intervention(
        self,
        state: Dict[str, Any],
        intervention: str,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用干预"""
        new_state = state.copy()
        
        # 根据干预类型修改状态
        for var, value in details.items():
            if var in new_state:
                new_state[var] = value
        
        return new_state
    
    def _predict_outcome(
        self,
        graph: CausalGraph,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """预测结果"""
        # 简化的预测逻辑
        return {
            "expected_benefit": random.uniform(0.5, 0.9),
            "risk_level": random.choice(["low", "medium", "high"]),
            "time_to_effect": round(random.uniform(1.0, 24.0), 2),
            "confidence_interval": [0.6, 0.85]
        }
    
    def _build_reasoning_chain(
        self,
        graph: CausalGraph,
        intervention: str,
        outcome: Dict[str, Any]
    ) -> List[str]:
        """构建推理链"""
        return [
            f"Intervention: {intervention}",
            f"Expected benefit: {outcome['expected_benefit']:.2f}",
            f"Risk level: {outcome['risk_level']}",
            "Causal path validated through graph traversal"
        ]


class RootCauseAnalyzer:
    """根因分析器
    
    执行根因分析（RCA）
    """
    
    def __init__(self):
        self.analysis_history: List[RCAReport] = []
    
    def analyze_root_cause(
        self,
        incident_data: Dict[str, Any],
        system_context: Dict[str, Any] = None
    ) -> RCAReport:
        """
        分析根因
        
        Args:
            incident_data: 事故数据
            system_context: 系统上下文
            
        Returns:
            RCA报告
        """
        report = RCAReport(
            report_id=str(uuid.uuid4()),
            incident_id=incident_data.get("incident_id", str(uuid.uuid4())[:8]),
            status=RCAStatus.INITIATED
        )
        
        # Step 1: 数据收集
        report.status = RCAStatus.DATA_COLLECTION
        collected_data = self._collect_evidence(incident_data, system_context)
        
        # Step 2: 构建因果图
        report.status = RCAStatus.CAUSAL_GRAPH_BUILT
        causal_graph = self._build_rca_causal_graph(collected_data)
        report.causal_graph = causal_graph
        
        # Step 3: 识别根因
        report.status = RCAStatus.ROOT_CAUSES_IDENTIFIED
        root_causes = self._identify_root_causes(causal_graph, incident_data)
        report.root_causes = root_causes
        
        # Step 4: 验证
        report.status = RCAStatus.VALIDATION_COMPLETE
        self._validate_root_causes(root_causes, collected_data)
        
        # Step 5: 生成建议
        report.recommendations = self._generate_recommendations(root_causes)
        
        # Step 6: 完成
        report.status = RCAStatus.COMPLETED
        report.completed_at = datetime.now(timezone.utc).isoformat()
        
        self.analysis_history.append(report)
        
        logger.info(f"RCA completed: {len(root_causes)} root causes identified")
        
        return report
    
    def _collect_evidence(
        self,
        incident_data: Dict,
        context: Dict = None
    ) -> Dict:
        """收集证据"""
        evidence = {
            "symptoms": incident_data.get("symptoms", []),
            "timeline": incident_data.get("timeline", []),
            "metrics": incident_data.get("metrics", {}),
            "logs": incident_data.get("logs", []),
            "context": context or {}
        }
        
        return evidence
    
    def _build_rca_causal_graph(self, evidence: Dict) -> CausalGraph:
        """构建RCA因果图"""
        graph = CausalGraph(graph_id=str(uuid.uuid4()))
        
        # 从症状创建节点
        for symptom in evidence.get("symptoms", []):
            node = CausalNode(
                node_id="",
                name=f"Symptom: {symptom}",
                node_type="symptom",
                value=True
            )
            graph.add_node(node)
        
        # 从指标创建节点
        for metric_name, metric_value in evidence.get("metrics", {}).items():
            node = CausalNode(
                node_id="",
                name=f"Metric: {metric_name}",
                node_type="metric",
                value=metric_value
            )
            graph.add_node(node)
        
        # 添加因果关系（简化）
        if len(graph.nodes) >= 2:
            edge = CausalEdge(
                edge_id="",
                source_node_id=graph.nodes[0].node_id,
                target_node_id=graph.nodes[-1].node_id,
                relation_type=CausalRelationType.DIRECT_CAUSATION,
                strength=0.8,
                description="Potential causal relationship"
            )
            graph.add_edge(edge)
        
        return graph
    
    def _identify_root_causes(
        self,
        graph: CausalGraph,
        incident_data: Dict
    ) -> List[RootCause]:
        """识别根因"""
        root_causes = []
        
        # 基于因果图识别根因
        # 寻找没有父节点的节点（根节点）
        child_nodes = set(e.target_node_id for e in graph.edges)
        
        for node in graph.nodes:
            if node.node_id not in child_nodes:
                # 这是一个潜在的根因
                root_cause = RootCause(
                    root_cause_id="",
                    description=f"Root cause: {node.name}",
                    confidence=random.uniform(0.7, 0.95),
                    evidence=[f"Node {node.name} has no upstream causes"],
                    causal_path=[node.name],
                    impact_score=random.uniform(0.6, 0.95),
                    remediation_suggestions=[
                        f"Investigate {node.name} further",
                        "Implement monitoring for this factor",
                        "Add preventive measures"
                    ]
                )
                root_causes.append(root_cause)
        
        # 如果没有找到根节点，创建默认根因
        if not root_causes:
            root_cause = RootCause(
                root_cause_id="",
                description="System configuration issue",
                confidence=0.75,
                evidence=["Multiple symptoms observed"],
                causal_path=["Configuration -> Symptoms"],
                impact_score=0.8,
                remediation_suggestions=[
                    "Review system configuration",
                    "Check recent changes",
                    "Validate deployment settings"
                ]
            )
            root_causes.append(root_cause)
        
        # 按影响分数排序
        root_causes.sort(key=lambda x: x.impact_score * x.confidence, reverse=True)
        
        return root_causes
    
    def _validate_root_causes(
        self,
        root_causes: List[RootCause],
        evidence: Dict
    ) -> bool:
        """验证根因"""
        # 简化的验证逻辑
        for rc in root_causes:
            # 检查是否有足够的证据支持
            if len(rc.evidence) >= 1:
                rc.confidence *= 1.1  # 提升置信度
                rc.confidence = min(1.0, rc.confidence)
        
        return True
    
    def _generate_recommendations(self, root_causes: List[RootCause]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        for rc in root_causes[:3]:  # Top 3根因
            recommendations.extend(rc.remediation_suggestions[:2])
        
        # 添加通用建议
        recommendations.extend([
            "Implement automated monitoring and alerting",
            "Create runbook for similar incidents",
            "Conduct post-mortem review"
        ])
        
        return list(set(recommendations))  # 去重


class A2PScaffolding:
    """Abduction-Action-Prediction 脚手架
    
    结构化因果推理框架
    """
    
    def __init__(self):
        self.reasoning_history: List[Dict] = []
    
    def execute_a2p_reasoning(
        self,
        observation: Dict[str, Any],
        failure_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行A2P推理
        
        Args:
            observation: 观测数据
            failure_context: 失败上下文
            
        Returns:
            推理结果
        """
        result = {
            "abduction": None,
            "action": None,
            "prediction": None,
            "success": False
        }
        
        # Step 1: Abduction - 推断隐藏根因
        abduction_result = self._abduce_root_causes(observation, failure_context)
        result["abduction"] = abduction_result
        
        # Step 2: Action - 定义最小修正干预
        action_result = self._define_corrective_action(abduction_result)
        result["action"] = action_result
        
        # Step 3: Prediction - 模拟后续轨迹
        prediction_result = self._predict_trajectory(action_result, failure_context)
        result["prediction"] = prediction_result
        
        # 判断是否成功
        result["success"] = prediction_result.get("resolves_failure", False)
        
        self.reasoning_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": result
        })
        
        logger.info(f"A2P reasoning completed: success={result['success']}")
        
        return result
    
    def _abduce_root_causes(
        self,
        observation: Dict,
        context: Dict
    ) -> Dict[str, Any]:
        """Abduction: 推断根因"""
        # 基于观测推断可能的根因
        inferred_causes = []
        
        symptoms = observation.get("symptoms", [])
        for symptom in symptoms:
            # 简化的因果推断
            cause = {
                "cause": f"Potential cause of {symptom}",
                "confidence": random.uniform(0.6, 0.9),
                "evidence": [symptom]
            }
            inferred_causes.append(cause)
        
        return {
            "inferred_causes": inferred_causes,
            "most_likely_cause": max(inferred_causes, key=lambda x: x["confidence"]) if inferred_causes else None
        }
    
    def _define_corrective_action(self, abduction_result: Dict) -> Dict[str, Any]:
        """Action: 定义修正行动"""
        most_likely_cause = abduction_result.get("most_likely_cause")
        
        if not most_likely_cause:
            return {"action": "No action defined", "confidence": 0.0}
        
        action = {
            "action": f"Fix: {most_likely_cause['cause']}",
            "type": "corrective",
            "estimated_effort": random.choice(["low", "medium", "high"]),
            "risk": random.choice(["low", "medium", "high"])
        }
        
        return action
    
    def _predict_trajectory(
        self,
        action: Dict,
        context: Dict
    ) -> Dict[str, Any]:
        """Prediction: 预测轨迹"""
        resolves_failure = random.random() > 0.3  # 70%成功率
        
        return {
            "resolves_failure": resolves_failure,
            "predicted_outcome": "Failure resolved" if resolves_failure else "Partial improvement",
            "confidence": random.uniform(0.7, 0.95),
            "side_effects": [] if resolves_failure else ["May require additional fixes"]
        }


def create_causal_reasoning_system() -> Tuple[CausalGraphBuilder, CounterfactualEngine, RootCauseAnalyzer, A2PScaffolding]:
    """工厂函数：创建因果推理系统"""
    builder = CausalGraphBuilder()
    engine = CounterfactualEngine()
    analyzer = RootCauseAnalyzer()
    scaffolding = A2PScaffolding()
    
    return builder, engine, analyzer, scaffolding


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Causal Reasoning & Counterfactual Thinking 测试")
    print("="*60)
    
    builder, engine, analyzer, scaffolding = create_causal_reasoning_system()
    
    # 构建因果图
    print("\n🕸️ 构建因果图...")
    variables = [
        {"name": "Server_Load", "type": "metric", "value": 85.5, "probability": 0.9},
        {"name": "Response_Time", "type": "metric", "value": 2.3, "probability": 0.85},
        {"name": "Error_Rate", "type": "metric", "value": 0.05, "probability": 0.8},
        {"name": "User_Satisfaction", "type": "outcome", "value": 0.6, "probability": 0.7}
    ]
    
    domain_knowledge = [
        {
            "source": "Server_Load",
            "target": "Response_Time",
            "relation_type": "direct_causation",
            "strength": 0.9,
            "description": "High server load causes slow response"
        },
        {
            "source": "Response_Time",
            "target": "User_Satisfaction",
            "relation_type": "direct_causation",
            "strength": 0.85,
            "description": "Slow response reduces user satisfaction"
        }
    ]
    
    causal_graph = builder.build_causal_graph(variables, domain_knowledge)
    print(f"   节点数: {len(causal_graph.nodes)}")
    print(f"   边数: {len(causal_graph.edges)}")
    
    # 反事实推理
    print("\n💭 反事实推理...")
    scenario = engine.generate_counterfactual(
        causal_graph=causal_graph,
        intervention="Reduce server load by 30%",
        intervention_details={"Server_Load": 60.0}
    )
    
    print(f"   干预: {scenario.intervention}")
    print(f"   预期收益: {scenario.predicted_outcome['expected_benefit']:.2f}")
    print(f"   风险等级: {scenario.predicted_outcome['risk_level']}")
    print(f"   置信度: {scenario.confidence:.2f}")
    print(f"   推理链长度: {len(scenario.reasoning_chain)}")
    
    # 根因分析
    print("\n🔍 根因分析...")
    incident_data = {
        "incident_id": "INC-2026-001",
        "symptoms": ["High latency", "Increased error rate", "User complaints"],
        "timeline": [
            {"time": "10:00", "event": "Latency spike detected"},
            {"time": "10:05", "event": "Error rate increased"},
            {"time": "10:10", "event": "Users reporting issues"}
        ],
        "metrics": {
            "cpu_usage": 95.2,
            "memory_usage": 88.5,
            "disk_io": 120.3
        },
        "logs": ["ERROR: Connection timeout", "WARN: High memory usage"]
    }
    
    rca_report = analyzer.analyze_root_cause(incident_data)
    print(f"   事故ID: {rca_report.incident_id}")
    print(f"   状态: {rca_report.status.value}")
    print(f"   根因数: {len(rca_report.root_causes)}")
    
    if rca_report.root_causes:
        top_cause = rca_report.root_causes[0]
        print(f"\n   🔝 顶级根因:")
        print(f"      描述: {top_cause.description}")
        print(f"      置信度: {top_cause.confidence:.2f}")
        print(f"      影响分数: {top_cause.impact_score:.2f}")
        print(f"      建议:")
        for rec in top_cause.remediation_suggestions[:2]:
            print(f"        - {rec}")
    
    print(f"\n   📋 总建议数: {len(rca_report.recommendations)}")
    
    # A2P推理
    print("\n🧠 A2P推理...")
    observation = {
        "symptoms": ["Service degradation", "Timeout errors"]
    }
    
    failure_context = {
        "service": "payment-api",
        "severity": "high"
    }
    
    a2p_result = scaffolding.execute_a2p_reasoning(observation, failure_context)
    
    print(f"   Abduction: {len(a2p_result['abduction']['inferred_causes'])} causes inferred")
    if a2p_result['abduction']['most_likely_cause']:
        print(f"   最可能原因: {a2p_result['abduction']['most_likely_cause']['cause']}")
        print(f"   置信度: {a2p_result['abduction']['most_likely_cause']['confidence']:.2f}")
    
    print(f"   Action: {a2p_result['action']['action']}")
    print(f"   Prediction: {a2p_result['prediction']['predicted_outcome']}")
    print(f"   解决失败: {'✅' if a2p_result['success'] else '❌'}")
    
    print("\n✅ 测试完成！")
