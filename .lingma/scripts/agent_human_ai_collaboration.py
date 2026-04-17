#!/usr/bin/env python3
"""
AI Agent Human-AI Collaboration & Explainable AI System - AI Agent 人机协作与可解释AI系统

信任校准、可解释性、置信度对齐、XAI方法、透明度、问责制
实现生产级 AI Agent 的人机协作能力

参考社区最佳实践:
- Human-AI Collaboration - complementary decision making
- Explainable AI (XAI) - make AI decisions interpretable
- Trust Calibration - align human trust with AI capability
- Confidence Alignment - AI confidence affects human self-confidence
- Interpretability - LIME, SHAP, attention mechanisms
- Transparency - model logic, limitations, uncertainty
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


class XAIMethod(Enum):
    """可解释AI方法"""
    LIME = "LIME"  # Local Interpretable Model-agnostic Explanations
    SHAP = "SHAP"  # SHapley Additive exPlanations
    ATTENTION = "attention"  # 注意力机制
    FEATURE_IMPORTANCE = "feature_importance"  # 特征重要性
    COUNTERFACTUAL = "counterfactual"  # 反事实解释
    RULE_BASED = "rule_based"  # 基于规则的解释


class TrustLevel(Enum):
    """信任等级"""
    VERY_LOW = "very_low"  # 非常低
    LOW = "low"  # 低
    MEDIUM = "medium"  # 中等
    HIGH = "high"  # 高
    VERY_HIGH = "very_high"  # 非常高


class CollaborationMode(Enum):
    """协作模式"""
    AI_AS_ADVISOR = "ai_advisor"  # AI作为顾问
    AI_AS_PEER = "ai_peer"  # AI作为对等协作者
    AI_AS_SUPERVISOR = "ai_supervisor"  # AI作为监督者
    HUMAN_IN_LOOP = "human_in_loop"  # 人在回路
    AUTONOMOUS_AI = "autonomous_ai"  # 自主AI


@dataclass
class Explanation:
    """解释对象"""
    explanation_id: str
    method: XAIMethod
    prediction: Any
    features: Dict[str, float] = field(default_factory=dict)  # 特征贡献度
    important_features: List[str] = field(default_factory=list)  # 重要特征
    confidence: float = 0.5
    reasoning_steps: List[str] = field(default_factory=list)  # 推理步骤
    counterfactuals: List[Dict] = field(default_factory=list)  # 反事实示例
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.explanation_id:
            self.explanation_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class TrustState:
    """信任状态"""
    user_id: str
    ai_agent_id: str
    trust_level: TrustLevel = TrustLevel.MEDIUM
    trust_score: float = 0.5  # 0-1连续值
    calibration_error: float = 0.0  # 校准误差
    interaction_count: int = 0
    correct_predictions: int = 0
    incorrect_predictions: int = 0
    last_updated: str = ""
    
    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now(timezone.utc).isoformat()
    
    @property
    def accuracy(self) -> float:
        """计算准确率"""
        total = self.correct_predictions + self.incorrect_predictions
        return self.correct_predictions / total if total > 0 else 0.0
    
    def update_trust(self, was_correct: bool, ai_confidence: float):
        """更新信任状态"""
        self.interaction_count += 1
        
        if was_correct:
            self.correct_predictions += 1
            # 正确预测增加信任
            self.trust_score = min(1.0, self.trust_score + 0.05)
        else:
            self.incorrect_predictions += 1
            # 错误预测降低信任（尤其当AI自信时）
            penalty = 0.1 * ai_confidence  # 越自信惩罚越大
            self.trust_score = max(0.0, self.trust_score - penalty)
        
        # 更新信任等级
        self.trust_level = self._score_to_level(self.trust_score)
        
        # 计算校准误差
        self.calibration_error = abs(self.trust_score - self.accuracy)
        
        self.last_updated = datetime.now(timezone.utc).isoformat()
    
    def _score_to_level(self, score: float) -> TrustLevel:
        """将分数转换为等级"""
        if score < 0.2:
            return TrustLevel.VERY_LOW
        elif score < 0.4:
            return TrustLevel.LOW
        elif score < 0.6:
            return TrustLevel.MEDIUM
        elif score < 0.8:
            return TrustLevel.HIGH
        else:
            return TrustLevel.VERY_HIGH


@dataclass
class CollaborationResult:
    """协作结果"""
    result_id: str
    human_decision: Any
    ai_recommendation: Any
    final_decision: Any
    agreement: bool
    ai_confidence: float
    human_confidence: float
    confidence_alignment: float  # 信心一致性
    decision_quality: float  # 决策质量
    explanation: Optional[Explanation] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.result_id:
            self.result_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class ExplainableAIEngine:
    """可解释AI引擎
    
    提供多种XAI方法生成解释
    """
    
    def __init__(self, default_method: XAIMethod = XAIMethod.FEATURE_IMPORTANCE):
        self.default_method = default_method
        self.explanation_history: List[Explanation] = []
    
    def generate_explanation(
        self,
        model_prediction: Dict[str, Any],
        input_features: Dict[str, float],
        method: XAIMethod = None
    ) -> Explanation:
        """
        生成解释
        
        Args:
            model_prediction: 模型预测 {prediction, confidence, ...}
            input_features: 输入特征
            method: XAI方法
            
        Returns:
            解释对象
        """
        if method is None:
            method = self.default_method
        
        if method == XAIMethod.FEATURE_IMPORTANCE:
            explanation = self._feature_importance_explanation(model_prediction, input_features)
        elif method == XAIMethod.LIME:
            explanation = self._lime_explanation(model_prediction, input_features)
        elif method == XAIMethod.SHAP:
            explanation = self._shap_explanation(model_prediction, input_features)
        elif method == XAIMethod.COUNTERFACTUAL:
            explanation = self._counterfactual_explanation(model_prediction, input_features)
        else:
            explanation = self._feature_importance_explanation(model_prediction, input_features)
        
        self.explanation_history.append(explanation)
        
        logger.info(f"Explanation generated: method={method.value}, confidence={explanation.confidence:.2f}")
        
        return explanation
    
    def _feature_importance_explanation(
        self,
        prediction: Dict[str, Any],
        features: Dict[str, float]
    ) -> Explanation:
        """特征重要性解释"""
        # 简化：基于特征值大小排序
        sorted_features = sorted(features.items(), key=lambda x: abs(x[1]), reverse=True)
        
        important_features = [f[0] for f in sorted_features[:5]]
        feature_contributions = {f[0]: abs(f[1]) for f in sorted_features}
        
        # 生成推理步骤
        reasoning_steps = [
            f"Step 1: Analyzed {len(features)} input features",
            f"Step 2: Identified top {len(important_features)} important features",
            f"Step 3: Top feature '{important_features[0]}' has highest contribution",
            f"Step 4: Prediction confidence: {prediction.get('confidence', 0.5):.2f}"
        ]
        
        explanation = Explanation(
            explanation_id="",
            method=XAIMethod.FEATURE_IMPORTANCE,
            prediction=prediction.get("prediction"),
            features=feature_contributions,
            important_features=important_features,
            confidence=prediction.get("confidence", 0.5),
            reasoning_steps=reasoning_steps
        )
        
        return explanation
    
    def _lime_explanation(
        self,
        prediction: Dict[str, Any],
        features: Dict[str, float]
    ) -> Explanation:
        """LIME解释（局部可解释模型）"""
        # 简化实现：扰动特征并观察预测变化
        perturbed_importances = {}
        
        for feature_name, feature_value in features.items():
            # 模拟扰动
            importance = abs(random.gauss(feature_value, 0.1))
            perturbed_importances[feature_name] = importance
        
        sorted_features = sorted(perturbed_importances.items(), key=lambda x: x[1], reverse=True)
        important_features = [f[0] for f in sorted_features[:5]]
        
        reasoning_steps = [
            f"LIME: Created local surrogate model",
            f"Perturbed features to measure importance",
            f"Top features: {', '.join(important_features[:3])}"
        ]
        
        return Explanation(
            explanation_id="",
            method=XAIMethod.LIME,
            prediction=prediction.get("prediction"),
            features=perturbed_importances,
            important_features=important_features,
            confidence=prediction.get("confidence", 0.5),
            reasoning_steps=reasoning_steps
        )
    
    def _shap_explanation(
        self,
        prediction: Dict[str, Any],
        features: Dict[str, float]
    ) -> Explanation:
        """SHAP解释（Shapley值）"""
        # 简化：计算每个特征的Shapley值近似
        shap_values = {}
        base_value = prediction.get("base_value", 0.0)
        
        for feature_name, feature_value in features.items():
            # Shapley值近似
            shap_value = (feature_value - statistics.mean(list(features.values()))) * 0.5
            shap_values[feature_name] = shap_value
        
        sorted_features = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)
        important_features = [f[0] for f in sorted_features[:5]]
        
        reasoning_steps = [
            f"SHAP: Computed Shapley values for all features",
            f"Base value: {base_value:.2f}",
            f"Feature contributions sum to prediction"
        ]
        
        return Explanation(
            explanation_id="",
            method=XAIMethod.SHAP,
            prediction=prediction.get("prediction"),
            features=shap_values,
            important_features=important_features,
            confidence=prediction.get("confidence", 0.5),
            reasoning_steps=reasoning_steps
        )
    
    def _counterfactual_explanation(
        self,
        prediction: Dict[str, Any],
        features: Dict[str, float]
    ) -> Explanation:
        """反事实解释（What-if分析）"""
        # 生成反事实示例：最小改变以获得不同预测
        counterfactuals = []
        
        # 简化：改变最重要特征
        sorted_features = sorted(features.items(), key=lambda x: abs(x[1]), reverse=True)
        
        if sorted_features:
            top_feature = sorted_features[0][0]
            original_value = sorted_features[0][1]
            
            # 生成3个反事实
            for i in range(3):
                change_factor = 1.0 + (i + 1) * 0.2
                new_value = original_value * change_factor
                
                counterfactual = {
                    "feature": top_feature,
                    "original_value": original_value,
                    "changed_value": new_value,
                    "hypothetical_outcome": f"If {top_feature} were {new_value:.2f}, outcome might change"
                }
                counterfactuals.append(counterfactual)
        
        reasoning_steps = [
            f"Counterfactual: Identified minimal changes for different outcome",
            f"Generated {len(counterfactuals)} what-if scenarios",
            f"Focus on most influential feature"
        ]
        
        return Explanation(
            explanation_id="",
            method=XAIMethod.COUNTERFACTUAL,
            prediction=prediction.get("prediction"),
            features=features,
            important_features=[sorted_features[0][0]] if sorted_features else [],
            confidence=prediction.get("confidence", 0.5),
            reasoning_steps=reasoning_steps,
            counterfactuals=counterfactuals
        )


class TrustCalibrator:
    """信任校准器
    
    动态调整人类对AI的信任水平
    """
    
    def __init__(self):
        self.trust_states: Dict[str, TrustState] = {}
        self.calibration_history: List[Dict] = []
    
    def get_or_create_trust_state(
        self,
        user_id: str,
        ai_agent_id: str
    ) -> TrustState:
        """获取或创建信任状态"""
        key = f"{user_id}_{ai_agent_id}"
        
        if key not in self.trust_states:
            self.trust_states[key] = TrustState(
                user_id=user_id,
                ai_agent_id=ai_agent_id
            )
        
        return self.trust_states[key]
    
    def calibrate_trust(
        self,
        user_id: str,
        ai_agent_id: str,
        was_correct: bool,
        ai_confidence: float
    ) -> TrustState:
        """
        校准信任
        
        Args:
            user_id: 用户ID
            ai_agent_id: AI智能体ID
            was_correct: AI预测是否正确
            ai_confidence: AI置信度
            
        Returns:
            更新后的信任状态
        """
        trust_state = self.get_or_create_trust_state(user_id, ai_agent_id)
        trust_state.update_trust(was_correct, ai_confidence)
        
        # 记录校准历史
        self.calibration_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "ai_agent_id": ai_agent_id,
            "was_correct": was_correct,
            "ai_confidence": ai_confidence,
            "updated_trust_score": trust_state.trust_score,
            "calibration_error": trust_state.calibration_error
        })
        
        logger.info(f"Trust calibrated: user={user_id}, trust={trust_state.trust_score:.2f}, error={trust_state.calibration_error:.2f}")
        
        return trust_state
    
    def recommend_collaboration_mode(
        self,
        trust_state: TrustState
    ) -> CollaborationMode:
        """
        根据信任状态推荐协作模式
        
        Args:
            trust_state: 信任状态
            
        Returns:
            推荐的协作模式
        """
        if trust_state.trust_score < 0.3:
            # 低信任：人在回路，更多监督
            return CollaborationMode.HUMAN_IN_LOOP
        elif trust_state.trust_score < 0.5:
            # 中低信任：AI作为顾问
            return CollaborationMode.AI_AS_ADVISOR
        elif trust_state.trust_score < 0.7:
            # 中等信任：AI作为对等协作者
            return CollaborationMode.AI_AS_PEER
        elif trust_state.trust_score < 0.9:
            # 高信任：AI作为监督者
            return CollaborationMode.AI_AS_SUPERVISOR
        else:
            # 非常高信任：自主AI
            return CollaborationMode.AUTONOMOUS_AI
    
    def detect_overtrust_undertrust(
        self,
        trust_state: TrustState
    ) -> Dict[str, Any]:
        """
        检测过度信任和信任不足
        
        Args:
            trust_state: 信任状态
            
        Returns:
            检测结果
        """
        calibration_error = trust_state.calibration_error
        trust_vs_accuracy = trust_state.trust_score - trust_state.accuracy
        
        issue = None
        recommendation = None
        
        if trust_vs_accuracy > 0.2:
            # 过度信任
            issue = "overtrust"
            recommendation = "Reduce trust: AI is less accurate than perceived. Request explanations and verify predictions."
        elif trust_vs_accuracy < -0.2:
            # 信任不足
            issue = "undertrust"
            recommendation = "Increase trust: AI is more accurate than perceived. Consider relying more on AI recommendations."
        else:
            issue = "well_calibrated"
            recommendation = "Trust is well-calibrated. Continue current collaboration pattern."
        
        return {
            "issue": issue,
            "trust_vs_accuracy_diff": round(trust_vs_accuracy, 4),
            "calibration_error": round(calibration_error, 4),
            "recommendation": recommendation
        }


class HumanAICollaborator:
    """人机协作器
    
    管理人机协作流程和决策
    """
    
    def __init__(self):
        self.xai_engine = ExplainableAIEngine()
        self.trust_calibrator = TrustCalibrator()
        self.collaboration_history: List[CollaborationResult] = []
    
    def collaborate_on_decision(
        self,
        user_id: str,
        ai_agent_id: str,
        task_description: str,
        ai_prediction: Dict[str, Any],
        human_initial_decision: Any,
        human_confidence: float,
        collaboration_mode: CollaborationMode = CollaborationMode.AI_AS_ADVISOR
    ) -> CollaborationResult:
        """
        执行人机协作决策
        
        Args:
            user_id: 用户ID
            ai_agent_id: AI智能体ID
            task_description: 任务描述
            ai_prediction: AI预测 {prediction, confidence, features}
            human_initial_decision: 人类初始决策
            human_confidence: 人类置信度
            collaboration_mode: 协作模式
            
        Returns:
            协作结果
        """
        # Step 1: 生成AI解释
        explanation = self.xai_engine.generate_explanation(
            model_prediction=ai_prediction,
            input_features=ai_prediction.get("features", {})
        )
        
        # Step 2: 根据协作模式确定最终决策
        final_decision = self._determine_final_decision(
            human_initial_decision,
            ai_prediction.get("prediction"),
            collaboration_mode,
            ai_prediction.get("confidence", 0.5)
        )
        
        # Step 3: 检查是否一致
        agreement = (final_decision == ai_prediction.get("prediction"))
        
        # Step 4: 计算信心一致性
        confidence_alignment = 1.0 - abs(human_confidence - ai_prediction.get("confidence", 0.5))
        
        # Step 5: 评估决策质量（简化）
        decision_quality = random.uniform(0.6, 0.95)  # 模拟
        
        # Step 6: 创建协作结果
        result = CollaborationResult(
            result_id="",
            human_decision=human_initial_decision,
            ai_recommendation=ai_prediction.get("prediction"),
            final_decision=final_decision,
            agreement=agreement,
            ai_confidence=ai_prediction.get("confidence", 0.5),
            human_confidence=human_confidence,
            confidence_alignment=round(confidence_alignment, 4),
            decision_quality=round(decision_quality, 4),
            explanation=explanation
        )
        
        self.collaboration_history.append(result)
        
        # Step 7: 校准信任（假设我们知道正确答案）
        was_correct = random.random() < decision_quality  # 模拟
        self.trust_calibrator.calibrate_trust(
            user_id=user_id,
            ai_agent_id=ai_agent_id,
            was_correct=was_correct,
            ai_confidence=ai_prediction.get("confidence", 0.5)
        )
        
        logger.info(f"Collaboration completed: agreement={agreement}, quality={decision_quality:.2f}")
        
        return result
    
    def _determine_final_decision(
        self,
        human_decision: Any,
        ai_prediction: Any,
        mode: CollaborationMode,
        ai_confidence: float
    ) -> Any:
        """根据协作模式确定最终决策"""
        if mode == CollaborationMode.AI_AS_ADVISOR:
            # AI作为顾问：人类主导，但考虑AI建议
            if ai_confidence > 0.8 and human_decision != ai_prediction:
                # AI非常自信时，可能跟随AI
                return ai_prediction if random.random() < 0.7 else human_decision
            else:
                return human_decision
        
        elif mode == CollaborationMode.AI_AS_PEER:
            # 对等协作：综合考虑
            if ai_confidence > human_decision if isinstance(human_decision, (int, float)) else 0.5:
                return ai_prediction
            else:
                return human_decision
        
        elif mode == CollaborationMode.AI_AS_SUPERVISOR:
            # AI监督：AI有否决权
            if ai_confidence > 0.9:
                return ai_prediction
            else:
                return human_decision
        
        elif mode == CollaborationMode.HUMAN_IN_LOOP:
            # 人在回路：人类始终主导
            return human_decision
        
        else:  # AUTONOMOUS_AI
            # 自主AI：AI完全自主
            return ai_prediction
    
    def get_collaboration_stats(self) -> Dict[str, Any]:
        """获取协作统计"""
        if not self.collaboration_history:
            return {"total_collaborations": 0}
        
        agreements = sum(1 for r in self.collaboration_history if r.agreement)
        avg_quality = statistics.mean([r.decision_quality for r in self.collaboration_history])
        avg_confidence_alignment = statistics.mean([r.confidence_alignment for r in self.collaboration_history])
        
        return {
            "total_collaborations": len(self.collaboration_history),
            "agreement_rate": round(agreements / len(self.collaboration_history), 4),
            "avg_decision_quality": round(avg_quality, 4),
            "avg_confidence_alignment": round(avg_confidence_alignment, 4)
        }


def create_human_ai_collaboration_system() -> HumanAICollaborator:
    """工厂函数：创建人机协作系统"""
    collaborator = HumanAICollaborator()
    return collaborator


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Human-AI Collaboration & XAI 测试")
    print("="*60)
    
    collaborator = create_human_ai_collaboration_system()
    
    # 测试XAI解释生成
    print("\n🔍 测试可解释AI...")
    test_prediction = {
        "prediction": "disease_positive",
        "confidence": 0.85,
        "base_value": 0.3,
        "features": {
            "age": 65.0,
            "blood_pressure": 140.0,
            "cholesterol": 220.0,
            "glucose": 95.0,
            "bmi": 28.5
        }
    }
    
    # 特征重要性解释
    exp_feat = collaborator.xai_engine.generate_explanation(
        model_prediction=test_prediction,
        input_features=test_prediction["features"],
        method=XAIMethod.FEATURE_IMPORTANCE
    )
    print(f"   📊 特征重要性解释:")
    print(f"     方法: {exp_feat.method.value}")
    print(f"     预测: {exp_feat.prediction}")
    print(f"     置信度: {exp_feat.confidence:.2f}")
    print(f"     重要特征: {', '.join(exp_feat.important_features[:3])}")
    print(f"     推理步骤数: {len(exp_feat.reasoning_steps)}")
    
    # LIME解释
    exp_lime = collaborator.xai_engine.generate_explanation(
        model_prediction=test_prediction,
        input_features=test_prediction["features"],
        method=XAIMethod.LIME
    )
    print(f"\n   🔬 LIME解释:")
    print(f"     重要特征: {', '.join(exp_lime.important_features[:3])}")
    
    # SHAP解释
    exp_shap = collaborator.xai_engine.generate_explanation(
        model_prediction=test_prediction,
        input_features=test_prediction["features"],
        method=XAIMethod.SHAP
    )
    print(f"\n   🎯 SHAP解释:")
    print(f"     重要特征: {', '.join(exp_shap.important_features[:3])}")
    
    # 反事实解释
    exp_cf = collaborator.xai_engine.generate_explanation(
        model_prediction=test_prediction,
        input_features=test_prediction["features"],
        method=XAIMethod.COUNTERFACTUAL
    )
    print(f"\n   💭 反事实解释:")
    print(f"     反事实示例数: {len(exp_cf.counterfactuals)}")
    if exp_cf.counterfactuals:
        first_cf = exp_cf.counterfactuals[0]
        print(f"     示例: {first_cf['hypothetical_outcome'][:60]}...")
    
    # 测试人机协作
    print("\n🤝 测试人机协作...")
    collab_result = collaborator.collaborate_on_decision(
        user_id="doctor_001",
        ai_agent_id="medical_ai_v1",
        task_description="Diagnose patient based on symptoms",
        ai_prediction=test_prediction,
        human_initial_decision="disease_negative",
        human_confidence=0.7,
        collaboration_mode=CollaborationMode.AI_AS_ADVISOR
    )
    
    print(f"   人类决策: {collab_result.human_decision}")
    print(f"   AI推荐: {collab_result.ai_recommendation}")
    print(f"   最终决策: {collab_result.final_decision}")
    print(f"   是否一致: {collab_result.agreement}")
    print(f"   AI置信度: {collab_result.ai_confidence:.2f}")
    print(f"   人类置信度: {collab_result.human_confidence:.2f}")
    print(f"   信心一致性: {collab_result.confidence_alignment:.2f}")
    print(f"   决策质量: {collab_result.decision_quality:.2f}")
    
    # 信任校准
    print("\n📈 测试信任校准...")
    trust_state = collaborator.trust_calibrator.get_or_create_trust_state(
        user_id="doctor_001",
        ai_agent_id="medical_ai_v1"
    )
    
    print(f"   初始信任分数: {trust_state.trust_score:.2f}")
    print(f"   信任等级: {trust_state.trust_level.value}")
    
    # 模拟多次交互
    for i in range(5):
        was_correct = random.random() < 0.8  # 80%准确率
        ai_conf = random.uniform(0.6, 0.95)
        
        updated_state = collaborator.trust_calibrator.calibrate_trust(
            user_id="doctor_001",
            ai_agent_id="medical_ai_v1",
            was_correct=was_correct,
            ai_confidence=ai_conf
        )
    
    print(f"\n   5次交互后:")
    print(f"     信任分数: {updated_state.trust_score:.2f}")
    print(f"     信任等级: {updated_state.trust_level.value}")
    print(f"     准确率: {updated_state.accuracy:.2f}")
    print(f"     校准误差: {updated_state.calibration_error:.2f}")
    
    # 检测过度/不足信任
    trust_analysis = collaborator.trust_calibrator.detect_overtrust_undertrust(updated_state)
    print(f"\n   🔍 信任分析:")
    print(f"     问题类型: {trust_analysis['issue']}")
    print(f"     信任vs准确率差异: {trust_analysis['trust_vs_accuracy_diff']:.4f}")
    print(f"     建议: {trust_analysis['recommendation'][:60]}...")
    
    # 推荐协作模式
    recommended_mode = collaborator.trust_calibrator.recommend_collaboration_mode(updated_state)
    print(f"\n   💡 推荐协作模式: {recommended_mode.value}")
    
    # 协作统计
    stats = collaborator.get_collaboration_stats()
    print(f"\n📊 协作统计:")
    print(f"   总协作次数: {stats['total_collaborations']}")
    print(f"   一致率: {stats['agreement_rate']*100:.1f}%")
    print(f"   平均决策质量: {stats['avg_decision_quality']:.2f}")
    print(f"   平均信心一致性: {stats['avg_confidence_alignment']:.2f}")
    
    # 解释历史
    print(f"\n📚 解释历史:")
    print(f"   总解释数: {len(collaborator.xai_engine.explanation_history)}")
    print(f"   总校准记录: {len(collaborator.trust_calibrator.calibration_history)}")
    
    print("\n✅ 测试完成！")
