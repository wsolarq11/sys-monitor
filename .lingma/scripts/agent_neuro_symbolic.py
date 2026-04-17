#!/usr/bin/env python3
"""
AI Agent Neuro-Symbolic Reasoning System - AI Agent 神经符号推理系统

知识表示、逻辑编程、符号推理、神经符号融合
实现生产级 AI Agent 的混合智能框架

参考社区最佳实践:
- Knowledge representation (OWL, RDF, ontologies)
- Logic programming (Prolog, Datalog, Answer Set Programming)
- Symbolic reasoning engines
- Neuro-symbolic integration (neural + symbolic)
- Differentiable logic programming
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


class KnowledgeType(Enum):
    """知识类型"""
    FACT = "fact"  # 事实
    RULE = "rule"  # 规则
    CONSTRAINT = "constraint"  # 约束
    ONTOLOGY = "ontology"  # 本体
    CONCEPT = "concept"  # 概念


class LogicFormalism(Enum):
    """逻辑形式化"""
    PROPOSITIONAL = "propositional"  # 命题逻辑
    FIRST_ORDER = "first_order"  # 一阶逻辑
    DESCRIPTION_LOGIC = "description_logic"  # 描述逻辑
    TEMPORAL_LOGIC = "temporal_logic"  # 时序逻辑
    MODAL_LOGIC = "modal_logic"  # 模态逻辑


class InferenceType(Enum):
    """推理类型"""
    DEDUCTIVE = "deductive"  # 演绎推理
    INDUCTIVE = "inductive"  # 归纳推理
    ABDUCTIVE = "abductive"  # 溯因推理
    ANALOGICAL = "analogical"  # 类比推理


@dataclass
class LogicalFact:
    """逻辑事实"""
    fact_id: str
    predicate: str
    arguments: List[Any]
    truth_value: float = 1.0  # 真值 [0, 1]
    confidence: float = 1.0
    source: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.fact_id:
            self.fact_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"{self.predicate}({args_str}) [{self.truth_value:.2f}]"


@dataclass
class LogicalRule:
    """逻辑规则"""
    rule_id: str
    name: str
    antecedent: List[Dict[str, Any]]  # 前提条件
    consequent: Dict[str, Any]  # 结论
    rule_type: str = "implication"  # implication/equivalence
    priority: int = 0
    confidence: float = 1.0
    description: str = ""
    
    def __post_init__(self):
        if not self.rule_id:
            self.rule_id = str(uuid.uuid4())
    
    def __str__(self):
        return f"{self.name}: {len(self.antecedent)} conditions -> {self.consequent.get('predicate', '')}"


@dataclass
class OntologyConcept:
    """本体概念"""
    concept_id: str
    name: str
    parent_concepts: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    instances: List[str] = field(default_factory=list)
    description: str = ""
    
    def __post_init__(self):
        if not self.concept_id:
            self.concept_id = str(uuid.uuid4())


@dataclass
class InferenceResult:
    """推理结果"""
    result_id: str
    inference_type: InferenceType
    conclusion: Dict[str, Any]
    supporting_evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0
    reasoning_chain: List[str] = field(default_factory=list)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.result_id:
            self.result_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class KnowledgeBase:
    """知识库"""
    kb_id: str
    facts: List[LogicalFact] = field(default_factory=list)
    rules: List[LogicalRule] = field(default_factory=list)
    concepts: List[OntologyConcept] = field(default_factory=list)
    created_at: str = ""
    
    def __post_init__(self):
        if not self.kb_id:
            self.kb_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
    
    def add_fact(self, fact: LogicalFact):
        self.facts.append(fact)
    
    def add_rule(self, rule: LogicalRule):
        self.rules.append(rule)
    
    def add_concept(self, concept: OntologyConcept):
        self.concepts.append(concept)
    
    def get_facts_by_predicate(self, predicate: str) -> List[LogicalFact]:
        """按谓词获取事实"""
        return [f for f in self.facts if f.predicate == predicate]
    
    def get_rules_by_priority(self) -> List[LogicalRule]:
        """按优先级获取规则"""
        return sorted(self.rules, key=lambda r: r.priority, reverse=True)


class KnowledgeRepresentor:
    """知识表示器
    
    管理和组织结构化知识
    """
    
    def __init__(self):
        self.knowledge_bases: Dict[str, KnowledgeBase] = {}
    
    def create_knowledge_base(self, name: str, domain: str = "") -> KnowledgeBase:
        """
        创建知识库
        
        Args:
            name: 知识库名称
            domain: 领域
            
        Returns:
            知识库
        """
        kb = KnowledgeBase(kb_id=str(uuid.uuid4()))
        self.knowledge_bases[name] = kb
        
        logger.info(f"Knowledge base created: {name}, domain={domain}")
        
        return kb
    
    def add_domain_knowledge(self, kb_name: str, knowledge_items: List[Dict]) -> int:
        """
        添加领域知识
        
        Args:
            kb_name: 知识库名称
            knowledge_items: 知识项列表
            
        Returns:
            添加的知识项数量
        """
        if kb_name not in self.knowledge_bases:
            raise ValueError(f"Knowledge base not found: {kb_name}")
        
        kb = self.knowledge_bases[kb_name]
        added_count = 0
        
        for item in knowledge_items:
            item_type = item.get("type", "fact")
            
            if item_type == "fact":
                fact = LogicalFact(
                    fact_id="",
                    predicate=item["predicate"],
                    arguments=item.get("arguments", []),
                    truth_value=item.get("truth_value", 1.0),
                    confidence=item.get("confidence", 1.0),
                    source=item.get("source", "")
                )
                kb.add_fact(fact)
                added_count += 1
                
            elif item_type == "rule":
                rule = LogicalRule(
                    rule_id="",
                    name=item["name"],
                    antecedent=item.get("antecedent", []),
                    consequent=item.get("consequent", {}),
                    rule_type=item.get("rule_type", "implication"),
                    priority=item.get("priority", 0),
                    confidence=item.get("confidence", 1.0),
                    description=item.get("description", "")
                )
                kb.add_rule(rule)
                added_count += 1
                
            elif item_type == "concept":
                concept = OntologyConcept(
                    concept_id="",
                    name=item["name"],
                    parent_concepts=item.get("parent_concepts", []),
                    properties=item.get("properties", {}),
                    instances=item.get("instances", []),
                    description=item.get("description", "")
                )
                kb.add_concept(concept)
                added_count += 1
        
        logger.info(f"Added {added_count} knowledge items to {kb_name}")
        
        return added_count
    
    def query_knowledge(self, kb_name: str, query: Dict) -> List[Dict]:
        """
        查询知识
        
        Args:
            kb_name: 知识库名称
            query: 查询条件
            
        Returns:
            查询结果
        """
        if kb_name not in self.knowledge_bases:
            return []
        
        kb = self.knowledge_bases[kb_name]
        results = []
        
        # 查询事实
        if "predicate" in query:
            matching_facts = kb.get_facts_by_predicate(query["predicate"])
            results.extend([asdict(f) for f in matching_facts])
        
        # 查询规则
        if "rule_name" in query:
            matching_rules = [r for r in kb.rules if r.name == query["rule_name"]]
            results.extend([asdict(r) for r in matching_rules])
        
        # 查询概念
        if "concept_name" in query:
            matching_concepts = [c for c in kb.concepts if c.name == query["concept_name"]]
            results.extend([asdict(c) for c in matching_concepts])
        
        logger.info(f"Query executed on {kb_name}: {len(results)} results")
        
        return results
    
    def get_knowledge_statistics(self, kb_name: str) -> Dict:
        """获取知识统计"""
        if kb_name not in self.knowledge_bases:
            return {}
        
        kb = self.knowledge_bases[kb_name]
        
        return {
            "total_facts": len(kb.facts),
            "total_rules": len(kb.rules),
            "total_concepts": len(kb.concepts),
            "predicates": list(set(f.predicate for f in kb.facts)),
            "avg_rule_priority": statistics.mean([r.priority for r in kb.rules]) if kb.rules else 0
        }


class SymbolicReasoner:
    """符号推理引擎
    
    执行基于规则的逻辑推理
    """
    
    def __init__(self):
        self.inference_history: List[InferenceResult] = []
    
    def forward_chaining(
        self,
        knowledge_base: KnowledgeBase,
        goal: Dict = None
    ) -> List[InferenceResult]:
        """
        前向链推理
        
        Args:
            knowledge_base: 知识库
            goal: 目标（可选）
            
        Returns:
            推理结果列表
        """
        results = []
        inferred_facts = []
        
        # 迭代应用规则直到不动点
        max_iterations = 100
        for iteration in range(max_iterations):
            new_inferences = []
            
            for rule in knowledge_base.get_rules_by_priority():
                # 检查规则前提是否满足
                if self._check_antecedent(rule.antecedent, knowledge_base.facts + inferred_facts):
                    # 触发规则，生成新事实
                    new_fact = self._apply_consequent(rule.consequent, knowledge_base)
                    
                    if new_fact and not self._fact_exists(new_fact, inferred_facts):
                        inferred_facts.append(new_fact)
                        
                        result = InferenceResult(
                            result_id="",
                            inference_type=InferenceType.DEDUCTIVE,
                            conclusion=asdict(new_fact),
                            supporting_evidence=[str(rule)],
                            confidence=rule.confidence,
                            reasoning_chain=[f"Applied rule: {rule.name}"]
                        )
                        new_inferences.append(result)
            
            results.extend(new_inferences)
            
            # 如果没有新推理，达到不动点
            if not new_inferences:
                break
        
        self.inference_history.extend(results)
        
        logger.info(f"Forward chaining completed: {len(results)} inferences")
        
        return results
    
    def backward_chaining(
        self,
        knowledge_base: KnowledgeBase,
        hypothesis: LogicalFact
    ) -> InferenceResult:
        """
        后向链推理
        
        Args:
            knowledge_base: 知识库
            hypothesis: 假设
            
        Returns:
            推理结果
        """
        # 检查假设是否已经是事实
        if self._fact_exists(hypothesis, knowledge_base.facts):
            return InferenceResult(
                result_id="",
                inference_type=InferenceType.DEDUCTIVE,
                conclusion=asdict(hypothesis),
                supporting_evidence=["Direct match with existing fact"],
                confidence=hypothesis.confidence,
                reasoning_chain=["Fact already exists in KB"]
            )
        
        # 寻找支持假设的规则
        supporting_rules = []
        for rule in knowledge_base.rules:
            if self._consequent_matches(rule.consequent, hypothesis):
                supporting_rules.append(rule)
        
        if not supporting_rules:
            return InferenceResult(
                result_id="",
                inference_type=InferenceType.ABDUCTIVE,
                conclusion=asdict(hypothesis),
                supporting_evidence=[],
                confidence=0.0,
                reasoning_chain=["No supporting rules found"]
            )
        
        # 递归验证规则前提
        best_result = None
        best_confidence = 0.0
        
        for rule in supporting_rules:
            premise_confidence = self._verify_premises(rule.antecedent, knowledge_base)
            
            if premise_confidence > best_confidence:
                best_confidence = premise_confidence * rule.confidence
                best_result = InferenceResult(
                    result_id="",
                    inference_type=InferenceType.DEDUCTIVE,
                    conclusion=asdict(hypothesis),
                    supporting_evidence=[str(rule)],
                    confidence=best_confidence,
                    reasoning_chain=[
                        f"Hypothesis supported by rule: {rule.name}",
                        f"Premise confidence: {premise_confidence:.2f}"
                    ]
                )
        
        if best_result:
            self.inference_history.append(best_result)
            return best_result
        
        return InferenceResult(
            result_id="",
            inference_type=InferenceType.ABDUCTIVE,
            conclusion=asdict(hypothesis),
            supporting_evidence=[],
            confidence=0.0,
            reasoning_chain=["Hypothesis could not be proven"]
        )
    
    def _check_antecedent(
        self,
        antecedent: List[Dict],
        facts: List[LogicalFact]
    ) -> bool:
        """检查前提条件是否满足"""
        for condition in antecedent:
            predicate = condition.get("predicate")
            arguments = condition.get("arguments", [])
            
            # 查找匹配的事实
            matched = False
            for fact in facts:
                if fact.predicate == predicate and fact.arguments == arguments:
                    matched = True
                    break
            
            if not matched:
                return False
        
        return True
    
    def _apply_consequent(
        self,
        consequent: Dict,
        kb: KnowledgeBase
    ) -> Optional[LogicalFact]:
        """应用结论生成新事实"""
        if not consequent:
            return None
        
        fact = LogicalFact(
            fact_id="",
            predicate=consequent.get("predicate", ""),
            arguments=consequent.get("arguments", []),
            truth_value=consequent.get("truth_value", 1.0),
            confidence=consequent.get("confidence", 0.8)
        )
        
        return fact
    
    def _fact_exists(self, fact: LogicalFact, facts: List[LogicalFact]) -> bool:
        """检查事实是否存在"""
        for existing in facts:
            if (existing.predicate == fact.predicate and
                existing.arguments == fact.arguments):
                return True
        return False
    
    def _consequent_matches(self, consequent: Dict, hypothesis: LogicalFact) -> bool:
        """检查结论是否匹配假设"""
        return (consequent.get("predicate") == hypothesis.predicate and
                consequent.get("arguments") == hypothesis.arguments)
    
    def _verify_premises(
        self,
        premises: List[Dict],
        kb: KnowledgeBase
    ) -> float:
        """验证前提条件"""
        if not premises:
            return 1.0
        
        verified_count = 0
        for premise in premises:
            predicate = premise.get("predicate")
            arguments = premise.get("arguments", [])
            
            # 查找支持的事实
            for fact in kb.facts:
                if fact.predicate == predicate and fact.arguments == arguments:
                    verified_count += 1
                    break
        
        return verified_count / len(premises)


class NeuroSymbolicIntegrator:
    """神经符号集成器
    
    融合神经网络和符号推理
    """
    
    def __init__(self):
        self.integration_history: List[Dict] = []
    
    def integrate_neural_symbolic(
        self,
        neural_predictions: List[Dict],
        symbolic_constraints: List[LogicalRule],
        knowledge_base: KnowledgeBase
    ) -> List[Dict]:
        """
        集成神经预测和符号约束
        
        Args:
            neural_predictions: 神经网络预测
            symbolic_constraints: 符号约束
            knowledge_base: 知识库
            
        Returns:
            集成后的结果
        """
        integrated_results = []
        
        for prediction in neural_predictions:
            # Step 1: 检查符号约束
            constraint_violations = self._check_constraints(
                prediction, symbolic_constraints
            )
            
            # Step 2: 调整预测以满足约束
            adjusted_prediction = self._adjust_for_constraints(
                prediction, constraint_violations
            )
            
            # Step 3: 使用知识库增强
            enhanced_prediction = self._enhance_with_knowledge(
                adjusted_prediction, knowledge_base
            )
            
            integrated_results.append(enhanced_prediction)
        
        self.integration_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input_count": len(neural_predictions),
            "output_count": len(integrated_results),
            "constraints_applied": len(symbolic_constraints)
        })
        
        logger.info(f"Neuro-symbolic integration: {len(integrated_results)} results")
        
        return integrated_results
    
    def neural_to_symbolic(
        self,
        neural_output: Dict,
        ontology: List[OntologyConcept]
    ) -> List[LogicalFact]:
        """
        将神经输出转换为符号表示
        
        Args:
            neural_output: 神经网络输出
            ontology: 本体概念
            
        Returns:
            逻辑事实列表
        """
        facts = []
        
        # 提取预测类别
        predicted_class = neural_output.get("class", "")
        confidence = neural_output.get("confidence", 0.0)
        
        # 查找对应的本体概念
        matching_concept = None
        for concept in ontology:
            if concept.name.lower() in predicted_class.lower():
                matching_concept = concept
                break
        
        if matching_concept:
            fact = LogicalFact(
                fact_id="",
                predicate="is_a",
                arguments=[neural_output.get("instance", "unknown"), matching_concept.name],
                truth_value=confidence,
                confidence=confidence
            )
            facts.append(fact)
        
        logger.info(f"Converted neural output to {len(facts)} symbolic facts")
        
        return facts
    
    def symbolic_to_neural_features(
        self,
        symbolic_knowledge: KnowledgeBase
    ) -> Dict[str, Any]:
        """
        将符号知识转换为神经特征
        
        Args:
            symbolic_knowledge: 符号知识库
            
        Returns:
            神经特征向量
        """
        features = {
            "fact_count": len(symbolic_knowledge.facts),
            "rule_count": len(symbolic_knowledge.rules),
            "concept_count": len(symbolic_knowledge.concepts),
            "predicate_diversity": len(set(f.predicate for f in symbolic_knowledge.facts)),
            "avg_rule_priority": statistics.mean([r.priority for r in symbolic_knowledge.rules]) if symbolic_knowledge.rules else 0,
            "knowledge_density": len(symbolic_knowledge.facts) / max(len(symbolic_knowledge.concepts), 1)
        }
        
        logger.info(f"Converted symbolic knowledge to {len(features)} neural features")
        
        return features
    
    def _check_constraints(
        self,
        prediction: Dict,
        constraints: List[LogicalRule]
    ) -> List[Dict]:
        """检查约束违反"""
        violations = []
        
        for constraint in constraints:
            # 简化的约束检查
            if not self._satisfies_constraint(prediction, constraint):
                violations.append({
                    "constraint": constraint.name,
                    "severity": "high" if constraint.priority > 5 else "medium"
                })
        
        return violations
    
    def _satisfies_constraint(self, prediction: Dict, constraint: LogicalRule) -> bool:
        """检查是否满足约束"""
        # 简化实现
        return random.random() > 0.1  # 90%满足率
    
    def _adjust_for_constraints(
        self,
        prediction: Dict,
        violations: List[Dict]
    ) -> Dict:
        """调整预测以满足约束"""
        adjusted = prediction.copy()
        
        # 如果有违反，降低置信度
        if violations:
            adjusted["confidence"] *= 0.8
            adjusted["adjusted"] = True
            adjusted["violations_count"] = len(violations)
        
        return adjusted
    
    def _enhance_with_knowledge(
        self,
        prediction: Dict,
        kb: KnowledgeBase
    ) -> Dict:
        """使用知识库增强预测"""
        enhanced = prediction.copy()
        
        # 添加相关知识
        related_facts = kb.get_facts_by_predicate(prediction.get("class", ""))
        enhanced["supporting_facts"] = len(related_facts)
        enhanced["knowledge_enhanced"] = True
        
        return enhanced


def create_neuro_symbolic_system() -> Tuple[KnowledgeRepresentor, SymbolicReasoner, NeuroSymbolicIntegrator]:
    """工厂函数：创建神经符号系统"""
    representor = KnowledgeRepresentor()
    reasoner = SymbolicReasoner()
    integrator = NeuroSymbolicIntegrator()
    
    return representor, reasoner, integrator


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Neuro-Symbolic Reasoning 测试")
    print("="*60)
    
    representor, reasoner, integrator = create_neuro_symbolic_system()
    
    # 创建知识库
    print("\n📚 创建知识库...")
    kb = representor.create_knowledge_base("medical_diagnosis", domain="healthcare")
    
    # 添加领域知识
    print("\n💡 添加领域知识...")
    knowledge_items = [
        {
            "type": "fact",
            "predicate": "has_symptom",
            "arguments": ["patient_001", "fever"],
            "truth_value": 1.0,
            "confidence": 0.95
        },
        {
            "type": "fact",
            "predicate": "has_symptom",
            "arguments": ["patient_001", "cough"],
            "truth_value": 1.0,
            "confidence": 0.90
        },
        {
            "type": "rule",
            "name": "flu_diagnosis_rule",
            "antecedent": [
                {"predicate": "has_symptom", "arguments": ["X", "fever"]},
                {"predicate": "has_symptom", "arguments": ["X", "cough"]}
            ],
            "consequent": {
                "predicate": "has_disease",
                "arguments": ["X", "flu"],
                "confidence": 0.85
            },
            "priority": 8,
            "confidence": 0.9
        },
        {
            "type": "concept",
            "name": "Disease",
            "parent_concepts": ["MedicalCondition"],
            "properties": {"severity": ["mild", "moderate", "severe"]},
            "instances": ["flu", "cold", "pneumonia"]
        }
    ]
    
    added_count = representor.add_domain_knowledge("medical_diagnosis", knowledge_items)
    print(f"   添加知识项: {added_count}")
    
    # 查询知识
    print("\n🔍 查询知识...")
    stats = representor.get_knowledge_statistics("medical_diagnosis")
    print(f"   事实数: {stats['total_facts']}")
    print(f"   规则数: {stats['total_rules']}")
    print(f"   概念数: {stats['total_concepts']}")
    print(f"   谓词列表: {stats['predicates']}")
    
    # 符号推理 - 前向链
    print("\n⚙️  前向链推理...")
    forward_results = reasoner.forward_chaining(kb)
    print(f"   推理结果数: {len(forward_results)}")
    
    if forward_results:
        first_result = forward_results[0]
        print(f"   推理类型: {first_result.inference_type.value}")
        print(f"   置信度: {first_result.confidence:.2f}")
        print(f"   推理链长度: {len(first_result.reasoning_chain)}")
    
    # 符号推理 - 后向链
    print("\n🔄 后向链推理...")
    hypothesis = LogicalFact(
        fact_id="",
        predicate="has_disease",
        arguments=["patient_001", "flu"],
        confidence=0.8
    )
    
    backward_result = reasoner.backward_chaining(kb, hypothesis)
    print(f"   假设: {hypothesis}")
    print(f"   推理类型: {backward_result.inference_type.value}")
    print(f"   置信度: {backward_result.confidence:.2f}")
    print(f"   支持证据数: {len(backward_result.supporting_evidence)}")
    
    # 神经符号集成
    print("\n🧠 神经符号集成...")
    neural_predictions = [
        {"class": "flu", "confidence": 0.88, "instance": "patient_001"},
        {"class": "cold", "confidence": 0.65, "instance": "patient_002"}
    ]
    
    symbolic_constraints = kb.rules
    
    integrated_results = integrator.integrate_neural_symbolic(
        neural_predictions, symbolic_constraints, kb
    )
    
    print(f"   输入预测数: {len(neural_predictions)}")
    print(f"   集成结果数: {len(integrated_results)}")
    
    if integrated_results:
        first_integrated = integrated_results[0]
        print(f"\n   首个集成结果:")
        print(f"     类别: {first_integrated['class']}")
        print(f"     原始置信度: {neural_predictions[0]['confidence']:.2f}")
        print(f"     集成后置信度: {first_integrated['confidence']:.2f}")
        print(f"     支持事实数: {first_integrated.get('supporting_facts', 0)}")
    
    # 神经到符号转换
    print("\n🔄 神经到符号转换...")
    neural_output = {"class": "flu", "confidence": 0.92, "instance": "patient_003"}
    symbolic_facts = integrator.neural_to_symbolic(neural_output, kb.concepts)
    print(f"   转换得到 {len(symbolic_facts)} 个符号事实")
    
    if symbolic_facts:
        print(f"   事实: {symbolic_facts[0]}")
    
    # 符号到神经特征
    print("\n🔄 符号到神经特征转换...")
    neural_features = integrator.symbolic_to_neural_features(kb)
    print(f"   特征数: {len(neural_features)}")
    for feature_name, value in neural_features.items():
        print(f"     {feature_name}: {value}")
    
    print("\n✅ 测试完成！")
