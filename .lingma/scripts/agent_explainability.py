#!/usr/bin/env python3
"""
AI Agent Explainability & Transparency System - AI Agent 可解释性与透明度系统

XAI、思维链可视化、推理追踪、反事实解释
实现生产级 AI Agent 的可解释性框架

参考社区最佳实践:
- Chain-of-Thought (CoT) reasoning visualization
- SHAP/LIME for feature importance
- Counterfactual explanations
- Progressive disclosure of reasoning
- Trust and transparency metrics
"""

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import uuid
import statistics

logger = logging.getLogger(__name__)


class ExplanationType(Enum):
    """解释类型"""
    CHAIN_OF_THOUGHT = "chain_of_thought"  # 思维链
    FEATURE_IMPORTANCE = "feature_importance"  # 特征重要性
    COUNTERFACTUAL = "counterfactual"  # 反事实
    EXAMPLE_BASED = "example_based"  # 基于示例
    RULE_BASED = "rule_based"  # 基于规则


class ExplanationLevel(Enum):
    """解释级别"""
    SUMMARY = "summary"  # 摘要级
    INTERMEDIATE = "intermediate"  # 中间级
    DETAILED = "detailed"  # 详细级
    RAW_TRACE = "raw_trace"  # 原始追踪


class TrustMetric(Enum):
    """信任指标"""
    CONFIDENCE_SCORE = "confidence_score"
    CONSISTENCY_CHECK = "consistency_check"
    SOURCE_VERIFICATION = "source_verification"
    LOGIC_VALIDATION = "logic_validation"
    USER_FEEDBACK = "user_feedback"


@dataclass
class ReasoningStep:
    """推理步骤"""
    step_id: str
    step_number: int
    description: str
    logic_type: str  # deduction/induction/abduction/analogy
    confidence: float
    sources: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ChainOfThought:
    """思维链"""
    cot_id: str
    query: str
    final_answer: str
    reasoning_steps: List[ReasoningStep] = field(default_factory=list)
    total_steps: int = 0
    average_confidence: float = 0.0
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.total_steps:
            self.total_steps = len(self.reasoning_steps)
        if self.reasoning_steps:
            self.average_confidence = statistics.mean([s.confidence for s in self.reasoning_steps])
    
    def get_progressive_disclosure(self, level: ExplanationLevel) -> Dict:
        """渐进式披露"""
        if level == ExplanationLevel.SUMMARY:
            return {
                "query": self.query,
                "final_answer": self.final_answer,
                "total_steps": self.total_steps,
                "average_confidence": round(self.average_confidence, 4),
                "key_step": self.reasoning_steps[-1].description if self.reasoning_steps else ""
            }
        
        elif level == ExplanationLevel.INTERMEDIATE:
            return {
                "query": self.query,
                "final_answer": self.final_answer,
                "reasoning_summary": [
                    {
                        "step": s.step_number,
                        "description": s.description[:100],
                        "confidence": round(s.confidence, 2)
                    }
                    for s in self.reasoning_steps[:5]  # 只显示前5步
                ],
                "total_steps": self.total_steps
            }
        
        elif level == ExplanationLevel.DETAILED:
            return {
                "query": self.query,
                "final_answer": self.final_answer,
                "full_reasoning_chain": [asdict(s) for s in self.reasoning_steps],
                "average_confidence": round(self.average_confidence, 4)
            }
        
        else:  # RAW_TRACE
            return asdict(self)


@dataclass
class FeatureImportance:
    """特征重要性"""
    feature_name: str
    importance_score: float  # 0-1
    direction: str  # positive/negative
    explanation: str = ""
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class CounterfactualExplanation:
    """反事实解释"""
    original_input: Dict[str, Any]
    original_output: Any
    counterfactual_input: Dict[str, Any]
    counterfactual_output: Any
    changed_features: List[str] = field(default_factory=list)
    minimal_change: bool = True
    explanation: str = ""
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class Explanation:
    """解释"""
    explanation_id: str
    explanation_type: ExplanationType
    explanation_level: ExplanationLevel
    content: Dict[str, Any]
    target_user: str = "general"  # general/expert/developer
    generated_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now(timezone.utc).isoformat()


@dataclass
class TrustScore:
    """信任评分"""
    trust_id: str
    overall_score: float  # 0-1
    metric_scores: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    calculated_at: str = ""
    
    def __post_init__(self):
        if not self.calculated_at:
            self.calculated_at = datetime.now(timezone.utc).isoformat()


class ChainOfThoughtEngine:
    """思维链引擎
    
    生成和管理推理链条
    """
    
    def __init__(self):
        self.cot_history: List[ChainOfThought] = []
    
    def generate_cot(
        self,
        query: str,
        reasoning_steps_data: List[Dict],
        final_answer: str
    ) -> ChainOfThought:
        """
        生成思维链
        
        Args:
            query: 查询问题
            reasoning_steps_data: 推理步骤数据
            final_answer: 最终答案
            
        Returns:
            思维链对象
        """
        reasoning_steps = []
        
        for i, step_data in enumerate(reasoning_steps_data, 1):
            step = ReasoningStep(
                step_id=str(uuid.uuid4()),
                step_number=i,
                description=step_data.get("description", ""),
                logic_type=step_data.get("logic_type", "deduction"),
                confidence=step_data.get("confidence", 0.8),
                sources=step_data.get("sources", []),
                assumptions=step_data.get("assumptions", [])
            )
            reasoning_steps.append(step)
        
        cot = ChainOfThought(
            cot_id=str(uuid.uuid4()),
            query=query,
            final_answer=final_answer,
            reasoning_steps=reasoning_steps
        )
        
        self.cot_history.append(cot)
        
        logger.info(f"CoT generated: {cot.total_steps} steps, avg confidence={cot.average_confidence:.2f}")
        
        return cot
    
    def visualize_cot(self, cot: ChainOfThought, format: str = "text") -> str:
        """
        可视化思维链
        
        Args:
            cot: 思维链对象
            format: 输出格式 (text/markdown/json)
            
        Returns:
            可视化字符串
        """
        if format == "text":
            return self._text_visualization(cot)
        elif format == "markdown":
            return self._markdown_visualization(cot)
        elif format == "json":
            return json.dumps(asdict(cot), indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _text_visualization(self, cot: ChainOfThought) -> str:
        """文本可视化"""
        lines = [
            f"Query: {cot.query}",
            f"{'='*60}",
            ""
        ]
        
        for step in cot.reasoning_steps:
            confidence_bar = "█" * int(step.confidence * 10) + "░" * (10 - int(step.confidence * 10))
            lines.append(f"Step {step.step_number}: {step.description}")
            lines.append(f"  Logic: {step.logic_type} | Confidence: [{confidence_bar}] {step.confidence:.2f}")
            
            if step.sources:
                lines.append(f"  Sources: {', '.join(step.sources)}")
            
            if step.assumptions:
                lines.append(f"  Assumptions: {', '.join(step.assumptions)}")
            
            lines.append("")
        
        lines.append(f"{'='*60}")
        lines.append(f"Final Answer: {cot.final_answer}")
        lines.append(f"Average Confidence: {cot.average_confidence:.2f}")
        
        return "\n".join(lines)
    
    def _markdown_visualization(self, cot: ChainOfThought) -> str:
        """Markdown 可视化"""
        lines = [
            f"# Query: {cot.query}",
            "",
            "## Reasoning Chain",
            ""
        ]
        
        for step in cot.reasoning_steps:
            lines.append(f"### Step {step.step_number}: {step.description}")
            lines.append(f"- **Logic Type**: {step.logic_type}")
            lines.append(f"- **Confidence**: {step.confidence:.2f}")
            
            if step.sources:
                lines.append(f"- **Sources**: {', '.join(step.sources)}")
            
            if step.assumptions:
                lines.append(f"- **Assumptions**: {', '.join(step.assumptions)}")
            
            lines.append("")
        
        lines.append("---")
        lines.append(f"**Final Answer**: {cot.final_answer}")
        lines.append(f"**Average Confidence**: {cot.average_confidence:.2f}")
        
        return "\n".join(lines)


class FeatureImportanceAnalyzer:
    """特征重要性分析器
    
    使用 SHAP/LIME 等方法
    """
    
    def __init__(self):
        self.importance_history: List[List[FeatureImportance]] = []
    
    def analyze_feature_importance(
        self,
        model_prediction: Dict,
        features: Dict[str, float],
        method: str = "shap"
    ) -> List[FeatureImportance]:
        """
        分析特征重要性
        
        Args:
            model_prediction: 模型预测结果
            features: 输入特征
            method: 分析方法 (shap/lime/permutation)
            
        Returns:
            特征重要性列表
        """
        importances = []
        
        # 模拟 SHAP 值计算
        for feature_name, feature_value in features.items():
            # 在实际应用中，这里应该调用 SHAP/LIME 库
            # 目前使用简化的启发式方法
            importance_score = abs(feature_value) / (sum(abs(v) for v in features.values()) + 1e-10)
            direction = "positive" if feature_value > 0 else "negative"
            
            importance = FeatureImportance(
                feature_name=feature_name,
                importance_score=round(importance_score, 4),
                direction=direction,
                explanation=f"{feature_name} contributes {importance_score*100:.1f}% to the prediction"
            )
            
            importances.append(importance)
        
        # 按重要性排序
        importances.sort(key=lambda x: x.importance_score, reverse=True)
        
        self.importance_history.append(importances)
        
        logger.info(f"Feature importance analyzed: {len(importances)} features")
        
        return importances
    
    def visualize_importance(self, importances: List[FeatureImportance], top_k: int = 10) -> str:
        """可视化特征重要性"""
        lines = ["Feature Importance Analysis", "="*60, ""]
        
        for i, imp in enumerate(importances[:top_k], 1):
            bar_length = int(imp.importance_score * 50)
            bar = "█" * bar_length + "░" * (50 - bar_length)
            
            direction_symbol = "↑" if imp.direction == "positive" else "↓"
            
            lines.append(f"{i:2d}. {imp.feature_name:30s} [{bar}] {imp.importance_score:.4f} {direction_symbol}")
            lines.append(f"    {imp.explanation}")
            lines.append("")
        
        return "\n".join(lines)


class CounterfactualGenerator:
    """反事实解释生成器
    
    生成"What-if"场景
    """
    
    def __init__(self):
        self.counterfactuals: List[CounterfactualExplanation] = []
    
    def generate_counterfactual(
        self,
        original_input: Dict[str, Any],
        original_output: Any,
        desired_output: Any,
        feature_ranges: Dict[str, Tuple[float, float]]
    ) -> CounterfactualExplanation:
        """
        生成反事实解释
        
        Args:
            original_input: 原始输入
            original_output: 原始输出
            desired_output: 期望输出
            feature_ranges: 特征取值范围
            
        Returns:
            反事实解释
        """
        # 模拟寻找最小变化
        counterfactual_input = original_input.copy()
        changed_features = []
        
        # 简单策略：调整最关键的特征
        for feature_name, (min_val, max_val) in list(feature_ranges.items())[:2]:
            current_value = original_input.get(feature_name, 0)
            
            # 尝试改变特征值
            if isinstance(current_value, (int, float)):
                # 向期望方向调整
                adjustment = (max_val - min_val) * 0.2
                new_value = current_value + adjustment
                
                # 确保在范围内
                new_value = max(min_val, min(max_val, new_value))
                
                counterfactual_input[feature_name] = new_value
                changed_features.append(feature_name)
        
        # 模拟新的输出
        counterfactual_output = desired_output
        
        explanation = CounterfactualExplanation(
            original_input=original_input,
            original_output=original_output,
            counterfactual_input=counterfactual_input,
            counterfactual_output=counterfactual_output,
            changed_features=changed_features,
            minimal_change=True,
            explanation=f"If {', '.join(changed_features)} were adjusted, the output would change to {desired_output}"
        )
        
        self.counterfactuals.append(explanation)
        
        logger.info(f"Counterfactual generated: {len(changed_features)} features changed")
        
        return explanation
    
    def visualize_counterfactual(self, cf: CounterfactualExplanation) -> str:
        """可视化反事实解释"""
        lines = [
            "Counterfactual Explanation",
            "="*60,
            "",
            "Original Input:",
        ]
        
        for key, value in cf.original_input.items():
            lines.append(f"  {key}: {value}")
        
        lines.append(f"\nOriginal Output: {cf.original_output}")
        lines.append("\nCounterfactual Input:")
        
        for key, value in cf.counterfactual_input.items():
            original_value = cf.original_input.get(key)
            
            if key in cf.changed_features:
                lines.append(f"  {key}: {original_value} → {value} (changed)")
            else:
                lines.append(f"  {key}: {value}")
        
        lines.append(f"\nCounterfactual Output: {cf.counterfactual_output}")
        lines.append(f"\nExplanation: {cf.explanation}")
        
        return "\n".join(lines)


class TrustCalculator:
    """信任计算器
    
    计算和监控信任指标
    """
    
    def __init__(self):
        self.trust_history: List[TrustScore] = []
    
    def calculate_trust(
        self,
        confidence_score: float,
        consistency_check: bool,
        source_verification: Optional[float] = None,
        logic_validation: Optional[float] = None,
        user_feedback: Optional[float] = None
    ) -> TrustScore:
        """
        计算信任评分
        
        Args:
            confidence_score: 置信度分数
            consistency_check: 一致性检查
            source_verification: 源验证分数
            logic_validation: 逻辑验证分数
            user_feedback: 用户反馈分数
            
        Returns:
            信任评分
        """
        metric_scores = {
            "confidence_score": confidence_score,
            "consistency_check": 1.0 if consistency_check else 0.0
        }
        
        if source_verification is not None:
            metric_scores["source_verification"] = source_verification
        
        if logic_validation is not None:
            metric_scores["logic_validation"] = logic_validation
        
        if user_feedback is not None:
            metric_scores["user_feedback"] = user_feedback
        
        # 计算总体分数（加权平均）
        weights = {
            "confidence_score": 0.3,
            "consistency_check": 0.25,
            "source_verification": 0.2,
            "logic_validation": 0.15,
            "user_feedback": 0.1
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric, score in metric_scores.items():
            weight = weights.get(metric, 0.1)
            weighted_sum += score * weight
            total_weight += weight
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # 生成建议
        recommendations = []
        
        if confidence_score < 0.7:
            recommendations.append("Low confidence - consider providing more context or using a different model")
        
        if not consistency_check:
            recommendations.append("Inconsistent results detected - review input data quality")
        
        if source_verification is not None and source_verification < 0.8:
            recommendations.append("Source verification low - verify information sources")
        
        if logic_validation is not None and logic_validation < 0.7:
            recommendations.append("Logic validation failed - check reasoning chain")
        
        trust_score = TrustScore(
            trust_id=str(uuid.uuid4()),
            overall_score=round(overall_score, 4),
            metric_scores={k: round(v, 4) for k, v in metric_scores.items()},
            recommendations=recommendations
        )
        
        self.trust_history.append(trust_score)
        
        logger.info(f"Trust score calculated: {overall_score:.2f}")
        
        return trust_score
    
    def get_trust_trend(self, window: int = 10) -> Dict:
        """获取信任趋势"""
        recent_scores = self.trust_history[-window:]
        
        if not recent_scores:
            return {"error": "No trust scores available"}
        
        scores = [t.overall_score for t in recent_scores]
        
        return {
            "current_score": round(scores[-1], 4),
            "average_score": round(statistics.mean(scores), 4),
            "trend": "increasing" if len(scores) > 1 and scores[-1] > scores[0] else "decreasing",
            "volatility": round(statistics.stdev(scores), 4) if len(scores) > 1 else 0.0,
            "sample_size": len(scores)
        }


class ExplainabilityEngine:
    """可解释性引擎
    
    整合所有 XAI 组件的完整系统
    """
    
    def __init__(self):
        self.cot_engine = ChainOfThoughtEngine()
        self.feature_analyzer = FeatureImportanceAnalyzer()
        self.counterfactual_gen = CounterfactualGenerator()
        self.trust_calculator = TrustCalculator()
        self.explanation_history: List[Explanation] = []
    
    def explain_decision(
        self,
        query: str,
        reasoning_steps: List[Dict],
        final_answer: str,
        features: Optional[Dict[str, float]] = None,
        explanation_type: ExplanationType = ExplanationType.CHAIN_OF_THOUGHT,
        explanation_level: ExplanationLevel = ExplanationLevel.INTERMEDIATE
    ) -> Explanation:
        """
        解释决策
        
        Args:
            query: 查询问题
            reasoning_steps: 推理步骤
            final_answer: 最终答案
            features: 输入特征（可选）
            explanation_type: 解释类型
            explanation_level: 解释级别
            
        Returns:
            解释对象
        """
        content = {}
        
        if explanation_type == ExplanationType.CHAIN_OF_THOUGHT:
            cot = self.cot_engine.generate_cot(query, reasoning_steps, final_answer)
            content = cot.get_progressive_disclosure(explanation_level)
        
        elif explanation_type == ExplanationType.FEATURE_IMPORTANCE and features:
            importances = self.feature_analyzer.analyze_feature_importance({}, features)
            content = {
                "feature_importances": [asdict(imp) for imp in importances],
                "visualization": self.feature_analyzer.visualize_importance(importances)
            }
        
        elif explanation_type == ExplanationType.COUNTERFACTUAL:
            # 需要额外参数，这里简化处理
            content = {"message": "Counterfactual requires additional parameters"}
        
        explanation = Explanation(
            explanation_id=str(uuid.uuid4()),
            explanation_type=explanation_type,
            explanation_level=explanation_level,
            content=content,
            metadata={
                "query": query,
                "final_answer": final_answer
            }
        )
        
        self.explanation_history.append(explanation)
        
        logger.info(f"Explanation generated: {explanation_type.value}")
        
        return explanation
    
    def calculate_trust_for_decision(
        self,
        confidence: float,
        has_consistent_reasoning: bool,
        **kwargs
    ) -> TrustScore:
        """计算决策的信任评分"""
        return self.trust_calculator.calculate_trust(
            confidence_score=confidence,
            consistency_check=has_consistent_reasoning,
            **kwargs
        )
    
    def get_explainability_dashboard(self) -> Dict:
        """获取可解释性仪表板"""
        return {
            "total_explanations": len(self.explanation_history),
            "explanation_types": {
                etype.value: sum(1 for e in self.explanation_history if e.explanation_type == etype)
                for etype in ExplanationType
            },
            "trust_trend": self.trust_calculator.get_trust_trend(),
            "recent_explanations": [
                {
                    "id": e.explanation_id[:8],
                    "type": e.explanation_type.value,
                    "level": e.explanation_level.value,
                    "generated_at": e.generated_at
                }
                for e in self.explanation_history[-5:]
            ]
        }


def create_explainability_engine() -> ExplainabilityEngine:
    """工厂函数：创建可解释性引擎"""
    return ExplainabilityEngine()


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Explainability & Transparency 测试")
    print("="*60)
    
    engine = create_explainability_engine()
    
    # 生成思维链
    print("\n🧠 生成思维链...")
    reasoning_steps = [
        {"description": "Analyze the problem statement", "logic_type": "deduction", "confidence": 0.9},
        {"description": "Identify key variables and constraints", "logic_type": "analysis", "confidence": 0.85},
        {"description": "Apply relevant formulas and rules", "logic_type": "deduction", "confidence": 0.88},
        {"description": "Calculate intermediate results", "logic_type": "computation", "confidence": 0.92},
        {"description": "Verify solution against constraints", "logic_type": "validation", "confidence": 0.95},
    ]
    
    cot = engine.cot_engine.generate_cot(
        query="What is the optimal learning rate for training this neural network?",
        reasoning_steps_data=reasoning_steps,
        final_answer="The optimal learning rate is 0.001 based on grid search and validation performance."
    )
    
    print(f"   思维链生成: {cot.total_steps} 步")
    print(f"   平均置信度: {cot.average_confidence:.2f}")
    
    # 可视化思维链
    print("\n📊 思维链可视化 (Summary):")
    summary = cot.get_progressive_disclosure(ExplanationLevel.SUMMARY)
    print(f"   Query: {summary['query'][:50]}...")
    print(f"   Answer: {summary['final_answer'][:60]}...")
    print(f"   Steps: {summary['total_steps']}")
    print(f"   Confidence: {summary['average_confidence']:.2f}")
    
    # 特征重要性分析
    print("\n🔍 特征重要性分析...")
    features = {
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 100,
        "dropout_rate": 0.2,
        "weight_decay": 0.0001
    }
    
    importances = engine.feature_analyzer.analyze_feature_importance({}, features)
    print(engine.feature_analyzer.visualize_importance(importances, top_k=5))
    
    # 反事实解释
    print("\n💭 反事实解释...")
    cf = engine.counterfactual_gen.generate_counterfactual(
        original_input={"learning_rate": 0.001, "batch_size": 32},
        original_output="accuracy: 0.85",
        desired_output="accuracy: 0.90",
        feature_ranges={
            "learning_rate": (0.0001, 0.01),
            "batch_size": (16, 128)
        }
    )
    
    print(engine.counterfactual_gen.visualize_counterfactual(cf))
    
    # 信任评分
    print("\n✅ 信任评分计算...")
    trust = engine.calculate_trust_for_decision(
        confidence=0.88,
        has_consistent_reasoning=True,
        source_verification=0.92,
        logic_validation=0.85
    )
    
    print(f"   总体信任分: {trust.overall_score:.2f}")
    print(f"   各项指标:")
    for metric, score in trust.metric_scores.items():
        print(f"     - {metric}: {score:.2f}")
    
    if trust.recommendations:
        print(f"   建议:")
        for rec in trust.recommendations:
            print(f"     • {rec}")
    
    # 仪表板
    print("\n📈 可解释性仪表板:")
    dashboard = engine.get_explainability_dashboard()
    print(f"   总解释数: {dashboard['total_explanations']}")
    print(f"   信任趋势: {dashboard['trust_trend']['trend']}")
    print(f"   当前信任分: {dashboard['trust_trend']['current_score']:.2f}")
    
    print("\n✅ 测试完成！")
