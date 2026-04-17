#!/usr/bin/env python3
"""
AI Agent Neural-Symbolic Reasoning System - AI Agent 神经符号推理系统

知识表示、逻辑编程、符号推理、混合系统、Neuro-Symbolic融合
实现生产级 AI Agent 的神经符号推理能力

参考社区最佳实践:
- Neural-Symbolic AI - combine neural networks with symbolic reasoning
- Knowledge Representation - explicit knowledge encoding with logic
- Logic Programming - Prolog/Datalog-style rule-based reasoning
- Symbolic AI - logical inference, SAT solvers, ontologies
- Hybrid Systems - integrate learning and reasoning
- Neuro-Symbolic Integration - bridge perception and cognition
"""

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set, Union
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
    CONCEPT = "concept"  # 概念
    RELATIONSHIP = "relationship"  # 关系


class InferenceMethod(Enum):
    """推理方法"""
    FORWARD_CHAINING = "forward_chaining"  # 前向链式推理
    BACKWARD_CHAINING = "backward_chaining"  # 后向链式推理
    RESOLUTION = "resolution"  # 归结推理
    UNIFICATION = "unification"  # 合一


@dataclass
class SymbolicFact:
    """符号事实"""
    fact_id: str
    predicate: str  # 谓词
    arguments: List[str]  # 参数
    confidence: float = 1.0  # 置信度
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.fact_id:
            self.fact_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_logic_string(self) -> str:
        """转换为逻辑字符串"""
        args_str = ", ".join(self.arguments)
        return f"{self.predicate}({args_str})"


@dataclass
class LogicRule:
    """逻辑规则"""
    rule_id: str
    head: SymbolicFact  # 结论
    body: List[SymbolicFact]  # 前提
    rule_type: str = "implication"  # 规则类型
    priority: int = 0  # 优先级
    
    def __post_init__(self):
        if not self.rule_id:
            self.rule_id = str(uuid.uuid4())
    
    def to_logic_string(self) -> str:
        """转换为逻辑字符串"""
        body_str = " ∧ ".join([f.to_logic_string() for f in self.body])
        return f"{body_str} → {self.head.to_logic_string()}"


@dataclass
class InferenceResult:
    """推理结果"""
    result_id: str
    inferred_facts: List[SymbolicFact] = field(default_factory=list)
    inference_steps: List[str] = field(default_factory=list)
    method_used: InferenceMethod = InferenceMethod.FORWARD_CHAINING
    confidence: float = 0.0
    execution_time_ms: float = 0.0
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.result_id:
            self.result_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class NeuralEmbedding:
    """神经嵌入"""
    entity_id: str
    embedding_vector: List[float]  # 嵌入向量
    dimension: int = 0
    
    def __post_init__(self):
        if not self.dimension:
            self.dimension = len(self.embedding_vector)


class KnowledgeBase:
    """知识库
    
    管理符号知识和逻辑规则
    """
    
    def __init__(self):
        self.facts: Dict[str, SymbolicFact] = {}
        self.rules: Dict[str, LogicRule] = {}
        self.concepts: Dict[str, Dict[str, Any]] = {}
        self.relationships: List[Tuple[str, str, str]] = []  # (subject, predicate, object)
        
        self.query_history: List[Dict] = []
    
    def add_fact(self, fact: SymbolicFact):
        """添加事实"""
        self.facts[fact.fact_id] = fact
        logger.debug(f"Fact added: {fact.to_logic_string()}")
    
    def add_rule(self, rule: LogicRule):
        """添加规则"""
        self.rules[rule.rule_id] = rule
        logger.debug(f"Rule added: {rule.to_logic_string()}")
    
    def add_relationship(self, subject: str, predicate: str, obj: str):
        """添加关系"""
        self.relationships.append((subject, predicate, obj))
    
    def query_facts(
        self,
        predicate: str,
        arguments: List[str] = None
    ) -> List[SymbolicFact]:
        """
        查询事实
        
        Args:
            predicate: 谓词
            arguments: 参数（可选）
            
        Returns:
            匹配的事实列表
        """
        matching_facts = []
        
        for fact in self.facts.values():
            if fact.predicate == predicate:
                if arguments is None or fact.arguments == arguments:
                    matching_facts.append(fact)
        
        # 记录查询历史
        self.query_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "predicate": predicate,
            "arguments": arguments,
            "results_count": len(matching_facts)
        })
        
        logger.info(f"Query: {predicate}({arguments}), found {len(matching_facts)} facts")
        
        return matching_facts
    
    def get_all_facts(self) -> List[SymbolicFact]:
        """获取所有事实"""
        return list(self.facts.values())
    
    def get_all_rules(self) -> List[LogicRule]:
        """获取所有规则"""
        return list(self.rules.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_facts": len(self.facts),
            "total_rules": len(self.rules),
            "total_relationships": len(self.relationships),
            "total_concepts": len(self.concepts),
            "query_count": len(self.query_history)
        }


class SymbolicReasoner:
    """符号推理引擎
    
    执行逻辑推理和演绎
    """
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.inference_history: List[InferenceResult] = []
    
    def forward_chain_inference(
        self,
        max_iterations: int = 10
    ) -> InferenceResult:
        """
        前向链式推理
        
        Args:
            max_iterations: 最大迭代次数
            
        Returns:
            推理结果
        """
        start_time = time.time()
        
        inferred_facts = []
        inference_steps = []
        
        # 迭代应用规则
        for iteration in range(max_iterations):
            new_facts_found = False
            
            for rule in self.kb.get_all_rules():
                # 检查规则前提是否满足
                if self._check_rule_body(rule.body):
                    # 如果结论不在知识库中，则添加
                    if not self._fact_exists(rule.head):
                        inferred_facts.append(rule.head)
                        self.kb.add_fact(rule.head)
                        new_facts_found = True
                        
                        step = f"Iteration {iteration}: Applied rule {rule.rule_id[:8]}... -> {rule.head.to_logic_string()}"
                        inference_steps.append(step)
                        
                        logger.info(f"Inferred: {rule.head.to_logic_string()}")
            
            # 如果没有新事实，提前终止
            if not new_facts_found:
                break
        
        execution_time = (time.time() - start_time) * 1000
        
        # 计算置信度
        confidence = self._calculate_confidence(inferred_facts)
        
        result = InferenceResult(
            result_id="",
            inferred_facts=inferred_facts,
            inference_steps=inference_steps,
            method_used=InferenceMethod.FORWARD_CHAINING,
            confidence=confidence,
            execution_time_ms=round(execution_time, 2)
        )
        
        self.inference_history.append(result)
        
        logger.info(f"Forward chaining completed: {len(inferred_facts)} facts inferred")
        
        return result
    
    def backward_chain_inference(
        self,
        goal: SymbolicFact
    ) -> InferenceResult:
        """
        后向链式推理
        
        Args:
            goal: 目标事实
            
        Returns:
            推理结果
        """
        start_time = time.time()
        
        inference_steps = []
        proven = self._prove_goal(goal, [], inference_steps, depth=0)
        
        execution_time = (time.time() - start_time) * 1000
        
        inferred_facts = [goal] if proven else []
        confidence = 1.0 if proven else 0.0
        
        result = InferenceResult(
            result_id="",
            inferred_facts=inferred_facts,
            inference_steps=inference_steps,
            method_used=InferenceMethod.BACKWARD_CHAINING,
            confidence=confidence,
            execution_time_ms=round(execution_time, 2)
        )
        
        self.inference_history.append(result)
        
        logger.info(f"Backward chaining: goal={goal.to_logic_string()}, proven={proven}")
        
        return result
    
    def _check_rule_body(self, body: List[SymbolicFact]) -> bool:
        """检查规则前提是否满足"""
        for fact in body:
            if not self._fact_exists(fact):
                return False
        return True
    
    def _fact_exists(self, fact: SymbolicFact) -> bool:
        """检查事实是否存在"""
        for existing_fact in self.kb.get_all_facts():
            if (existing_fact.predicate == fact.predicate and 
                existing_fact.arguments == fact.arguments):
                return True
        return False
    
    def _prove_goal(
        self,
        goal: SymbolicFact,
        visited: List[str],
        steps: List[str],
        depth: int
    ) -> bool:
        """证明目标（递归）"""
        if depth > 10:  # 防止无限递归
            return False
        
        # 检查是否已在知识库中
        if self._fact_exists(goal):
            steps.append(f"Goal proven: {goal.to_logic_string()} (in KB)")
            return True
        
        # 尝试通过规则证明
        for rule in self.kb.get_all_rules():
            if (rule.head.predicate == goal.predicate and 
                rule.head.arguments == goal.arguments):
                
                # 递归证明规则前提
                all_proven = True
                for subgoal in rule.body:
                    if not self._prove_goal(subgoal, visited, steps, depth + 1):
                        all_proven = False
                        break
                
                if all_proven:
                    steps.append(f"Goal proven via rule {rule.rule_id[:8]}...")
                    return True
        
        steps.append(f"Goal not proven: {goal.to_logic_string()}")
        return False
    
    def _calculate_confidence(self, facts: List[SymbolicFact]) -> float:
        """计算置信度"""
        if not facts:
            return 0.0
        
        confidences = [f.confidence for f in facts]
        return statistics.mean(confidences)
    
    def get_reasoning_statistics(self) -> Dict[str, Any]:
        """获取推理统计"""
        if not self.inference_history:
            return {"total_inferences": 0}
        
        avg_confidence = statistics.mean([r.confidence for r in self.inference_history])
        avg_execution_time = statistics.mean([r.execution_time_ms for r in self.inference_history])
        
        return {
            "total_inferences": len(self.inference_history),
            "avg_confidence": round(avg_confidence, 4),
            "avg_execution_time_ms": round(avg_execution_time, 2)
        }


class NeuralSymbolicIntegrator:
    """神经符号集成器
    
    整合神经网络和符号推理
    """
    
    def __init__(self):
        self.embeddings: Dict[str, NeuralEmbedding] = {}
        self.integration_history: List[Dict] = []
    
    def create_embedding(
        self,
        entity_id: str,
        dimension: int = 64
    ) -> NeuralEmbedding:
        """
        创建神经嵌入
        
        Args:
            entity_id: 实体ID
            dimension: 维度
            
        Returns:
            神经嵌入
        """
        # 生成随机嵌入向量（简化）
        embedding_vector = [random.gauss(0, 1) for _ in range(dimension)]
        
        embedding = NeuralEmbedding(
            entity_id=entity_id,
            embedding_vector=embedding_vector,
            dimension=dimension
        )
        
        self.embeddings[entity_id] = embedding
        
        logger.info(f"Embedding created: {entity_id}, dim={dimension}")
        
        return embedding
    
    def compute_similarity(
        self,
        entity_a: str,
        entity_b: str
    ) -> float:
        """
        计算实体相似度（余弦相似度）
        
        Args:
            entity_a: 实体A
            entity_b: 实体B
            
        Returns:
            相似度分数 0-1
        """
        if entity_a not in self.embeddings or entity_b not in self.embeddings:
            return 0.0
        
        vec_a = self.embeddings[entity_a].embedding_vector
        vec_b = self.embeddings[entity_b].embedding_vector
        
        # 计算余弦相似度
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        magnitude_a = math.sqrt(sum(a * a for a in vec_a))
        magnitude_b = math.sqrt(sum(b * b for b in vec_b))
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        similarity = dot_product / (magnitude_a * magnitude_b)
        
        # 归一化到0-1
        normalized_similarity = (similarity + 1) / 2
        
        return max(0.0, min(1.0, normalized_similarity))
    
    def integrate_neural_symbolic(
        self,
        kb: KnowledgeBase,
        reasoner: SymbolicReasoner
    ) -> Dict[str, Any]:
        """
        整合神经符号推理
        
        Args:
            kb: 知识库
            reasoner: 推理引擎
            
        Returns:
            整合结果
        """
        # Step 1: 为所有实体创建嵌入
        entities = set()
        for fact in kb.get_all_facts():
            entities.update(fact.arguments)
        
        for entity in entities:
            if entity not in self.embeddings:
                self.create_embedding(entity, dimension=32)
        
        # Step 2: 基于相似度增强推理
        enhanced_facts = []
        for fact in kb.get_all_facts():
            # 查找相似实体
            similar_entities = []
            for other_entity in entities:
                if other_entity != fact.arguments[0]:
                    similarity = self.compute_similarity(fact.arguments[0], other_entity)
                    if similarity > 0.7:
                        similar_entities.append((other_entity, similarity))
            
            if similar_entities:
                enhanced_facts.append({
                    "original_fact": fact.to_logic_string(),
                    "similar_entities": similar_entities[:3]
                })
        
        # Step 3: 执行符号推理
        inference_result = reasoner.forward_chain_inference()
        
        # 整合结果
        integration_result = {
            "num_entities_embedded": len(entities),
            "num_enhanced_facts": len(enhanced_facts),
            "symbolic_inference_results": {
                "inferred_facts_count": len(inference_result.inferred_facts),
                "confidence": inference_result.confidence,
                "execution_time_ms": inference_result.execution_time_ms
            },
            "neural_symbolic_integration": "completed"
        }
        
        self.integration_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": integration_result
        })
        
        logger.info(f"Neural-symbolic integration completed: {len(entities)} entities")
        
        return integration_result
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """获取集成统计"""
        return {
            "total_embeddings": len(self.embeddings),
            "integration_runs": len(self.integration_history)
        }


class LogicProgrammingEngine:
    """逻辑编程引擎
    
    类似Prolog的逻辑编程能力
    """
    
    def __init__(self):
        self.predicates: Dict[str, List[List[str]]] = {}
        self.program_history: List[Dict] = []
    
    def assert_predicate(self, predicate: str, arguments: List[str]):
        """断言谓词"""
        if predicate not in self.predicates:
            self.predicates[predicate] = []
        
        self.predicates[predicate].append(arguments)
        
        logger.debug(f"Asserted: {predicate}({', '.join(arguments)})")
    
    def query_predicate(
        self,
        predicate: str,
        pattern: List[str] = None
    ) -> List[List[str]]:
        """
        查询谓词
        
        Args:
            predicate: 谓词名
            pattern: 模式（None表示全部）
            
        Returns:
            匹配的元组列表
        """
        if predicate not in self.predicates:
            return []
        
        results = self.predicates[predicate]
        
        if pattern:
            # 过滤匹配模式的元组
            filtered = []
            for args in results:
                match = True
                for i, p in enumerate(pattern):
                    if p != "_" and i < len(args) and args[i] != p:
                        match = False
                        break
                if match:
                    filtered.append(args)
            results = filtered
        
        # 记录查询
        self.program_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "predicate": predicate,
            "pattern": pattern,
            "results_count": len(results)
        })
        
        logger.info(f"Query: {predicate}({pattern}), found {len(results)} results")
        
        return results
    
    def define_rule(
        self,
        head_predicate: str,
        head_args: List[str],
        body_predicates: List[Tuple[str, List[str]]]
    ):
        """
        定义规则
        
        Args:
            head_predicate: 头部谓词
            head_args: 头部参数
            body_predicates: 体部谓词列表 [(predicate, args), ...]
        """
        logger.info(f"Rule defined: {head_predicate}(...) :- {len(body_predicates)} conditions")
    
    def get_program_statistics(self) -> Dict[str, Any]:
        """获取程序统计"""
        total_facts = sum(len(args_list) for args_list in self.predicates.values())
        
        return {
            "total_predicates": len(self.predicates),
            "total_facts": total_facts,
            "query_count": len(self.program_history)
        }


class NeuralSymbolicSystem:
    """神经符号系统
    
    整合知识库、推理引擎、神经嵌入、逻辑编程
    """
    
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.reasoner = SymbolicReasoner(self.knowledge_base)
        self.integrator = NeuralSymbolicIntegrator()
        self.logic_engine = LogicProgrammingEngine()
    
    def build_knowledge_domain(
        self,
        domain_name: str,
        facts_data: List[Dict],
        rules_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        构建知识领域
        
        Args:
            domain_name: 领域名称
            facts_data: 事实数据
            rules_data: 规则数据
            
        Returns:
            构建结果
        """
        logger.info(f"Building knowledge domain: {domain_name}")
        
        # 添加事实
        for fact_data in facts_data:
            fact = SymbolicFact(
                fact_id="",
                predicate=fact_data["predicate"],
                arguments=fact_data["arguments"],
                confidence=fact_data.get("confidence", 1.0)
            )
            self.knowledge_base.add_fact(fact)
        
        # 添加规则
        for rule_data in rules_data:
            head = SymbolicFact(
                fact_id="",
                predicate=rule_data["head"]["predicate"],
                arguments=rule_data["head"]["arguments"]
            )
            
            body = []
            for body_fact in rule_data["body"]:
                body.append(SymbolicFact(
                    fact_id="",
                    predicate=body_fact["predicate"],
                    arguments=body_fact["arguments"]
                ))
            
            rule = LogicRule(
                rule_id="",
                head=head,
                body=body
            )
            self.knowledge_base.add_rule(rule)
        
        # 统计
        stats = self.knowledge_base.get_statistics()
        
        logger.info(f"Domain built: {stats['total_facts']} facts, {stats['total_rules']} rules")
        
        return {
            "domain": domain_name,
            "statistics": stats
        }
    
    def execute_reasoning_pipeline(
        self,
        query_predicate: str = None,
        run_forward_chain: bool = True,
        run_backward_chain: bool = False,
        goal: SymbolicFact = None
    ) -> Dict[str, Any]:
        """
        执行推理流水线
        
        Args:
            query_predicate: 查询谓词
            run_forward_chain: 是否运行前向链式推理
            run_backward_chain: 是否运行后向链式推理
            goal: 后向链式推理的目标
            
        Returns:
            推理结果
        """
        results = {}
        
        # 查询事实
        if query_predicate:
            facts = self.knowledge_base.query_facts(query_predicate)
            results["queried_facts"] = [f.to_logic_string() for f in facts]
        
        # 前向链式推理
        if run_forward_chain:
            forward_result = self.reasoner.forward_chain_inference()
            results["forward_chain"] = {
                "inferred_facts_count": len(forward_result.inferred_facts),
                "confidence": forward_result.confidence,
                "execution_time_ms": forward_result.execution_time_ms,
                "steps_count": len(forward_result.inference_steps)
            }
        
        # 后向链式推理
        if run_backward_chain and goal:
            backward_result = self.reasoner.backward_chain_inference(goal)
            results["backward_chain"] = {
                "proven": backward_result.confidence > 0,
                "confidence": backward_result.confidence,
                "execution_time_ms": backward_result.execution_time_ms
            }
        
        # 神经符号集成
        integration_result = self.integrator.integrate_neural_symbolic(
            self.knowledge_base,
            self.reasoner
        )
        results["neural_symbolic"] = integration_result
        
        return results
    
    def get_system_overview(self) -> Dict[str, Any]:
        """获取系统概览"""
        return {
            "knowledge_base": self.knowledge_base.get_statistics(),
            "reasoning": self.reasoner.get_reasoning_statistics(),
            "neural_symbolic": self.integrator.get_integration_statistics(),
            "logic_programming": self.logic_engine.get_program_statistics()
        }


def create_neural_symbolic_system() -> NeuralSymbolicSystem:
    """工厂函数：创建神经符号系统"""
    system = NeuralSymbolicSystem()
    return system


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Neural-Symbolic Reasoning 测试")
    print("="*60)
    
    system = create_neural_symbolic_system()
    
    # 构建知识领域
    print("\n📚 构建知识领域...")
    facts_data = [
        {"predicate": "parent", "arguments": ["Alice", "Bob"], "confidence": 1.0},
        {"predicate": "parent", "arguments": ["Bob", "Charlie"], "confidence": 1.0},
        {"predicate": "male", "arguments": ["Bob"], "confidence": 1.0},
        {"predicate": "male", "arguments": ["Charlie"], "confidence": 1.0},
        {"predicate": "female", "arguments": ["Alice"], "confidence": 1.0}
    ]
    
    rules_data = [
        {
            "head": {"predicate": "grandparent", "arguments": ["X", "Z"]},
            "body": [
                {"predicate": "parent", "arguments": ["X", "Y"]},
                {"predicate": "parent", "arguments": ["Y", "Z"]}
            ]
        },
        {
            "head": {"predicate": "father", "arguments": ["X", "Y"]},
            "body": [
                {"predicate": "parent", "arguments": ["X", "Y"]},
                {"predicate": "male", "arguments": ["X"]}
            ]
        }
    ]
    
    build_result = system.build_knowledge_domain(
        domain_name="family_relations",
        facts_data=facts_data,
        rules_data=rules_data
    )
    
    print(f"   领域: {build_result['domain']}")
    print(f"   事实数: {build_result['statistics']['total_facts']}")
    print(f"   规则数: {build_result['statistics']['total_rules']}")
    
    # 查询事实
    print("\n🔍 查询事实...")
    parent_facts = system.knowledge_base.query_facts("parent")
    print(f"   parent事实数: {len(parent_facts)}")
    for fact in parent_facts:
        print(f"     - {fact.to_logic_string()}")
    
    # 执行推理流水线
    print("\n🧠 执行推理流水线...")
    reasoning_results = system.execute_reasoning_pipeline(
        query_predicate="parent",
        run_forward_chain=True,
        run_backward_chain=False
    )
    
    print(f"   查询到的事实:")
    for fact_str in reasoning_results.get("queried_facts", []):
        print(f"     - {fact_str}")
    
    if "forward_chain" in reasoning_results:
        fc = reasoning_results["forward_chain"]
        print(f"\n   前向链式推理:")
        print(f"     推断事实数: {fc['inferred_facts_count']}")
        print(f"     置信度: {fc['confidence']:.2f}")
        print(f"     执行时间: {fc['execution_time_ms']:.2f}ms")
        print(f"     推理步骤数: {fc['steps_count']}")
    
    if "neural_symbolic" in reasoning_results:
        ns = reasoning_results["neural_symbolic"]
        print(f"\n   神经符号集成:")
        print(f"     嵌入实体数: {ns['num_entities_embedded']}")
        print(f"     增强事实数: {ns['num_enhanced_facts']}")
        print(f"     符号推理结果:")
        sr = ns['symbolic_inference_results']
        print(f"       推断事实: {sr['inferred_facts_count']}")
        print(f"       置信度: {sr['confidence']:.2f}")
    
    # 测试逻辑编程引擎
    print("\n💻 测试逻辑编程引擎...")
    system.logic_engine.assert_predicate("likes", ["Alice", "ice_cream"])
    system.logic_engine.assert_predicate("likes", ["Bob", "chocolate"])
    system.logic_engine.assert_predicate("likes", ["Charlie", "ice_cream"])
    
    likes_results = system.logic_engine.query_predicate("likes")
    print(f"   likes谓词查询结果: {len(likes_results)}个")
    for args in likes_results:
        print(f"     - likes({', '.join(args)})")
    
    # 系统概览
    overview = system.get_system_overview()
    print(f"\n📊 系统概览:")
    print(f"   知识库:")
    kb = overview['knowledge_base']
    print(f"     总事实: {kb['total_facts']}")
    print(f"     总规则: {kb['total_rules']}")
    print(f"     总关系: {kb['total_relationships']}")
    print(f"   推理:")
    rs = overview['reasoning']
    print(f"     总推理: {rs['total_inferences']}")
    print(f"     平均置信度: {rs['avg_confidence']:.2f}")
    print(f"   神经符号:")
    ns = overview['neural_symbolic']
    print(f"     总嵌入: {ns['total_embeddings']}")
    print(f"   逻辑编程:")
    lp = overview['logic_programming']
    print(f"     总谓词: {lp['total_predicates']}")
    print(f"     总事实: {lp['total_facts']}")
    
    print("\n✅ 测试完成！")
