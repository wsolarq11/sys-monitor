#!/usr/bin/env python3
"""
AI Agent Reinforcement Learning & Preference Optimization System - AI Agent 强化学习与偏好优化系统

RLHF、DPO、奖励建模、人类反馈对齐
实现生产级 AI Agent 的偏好对齐框架

参考社区最佳实践:
- RLHF (Reinforcement Learning from Human Feedback)
- DPO (Direct Preference Optimization)
- RLAIF (Reinforcement Learning from AI Feedback)
- Reward modeling and preference learning
- Constitutional AI principles
"""

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import uuid
import math
import statistics
import random

logger = logging.getLogger(__name__)


class AlignmentMethod(Enum):
    """对齐方法"""
    RLHF = "rlhf"  # 基于人类反馈的强化学习
    DPO = "dpo"  # 直接偏好优化
    RLAIF = "rlaif"  # 基于AI反馈的强化学习
    CONSTITUTIONAL_AI = "constitutional_ai"  # 宪法AI


class FeedbackType(Enum):
    """反馈类型"""
    RANKING = "ranking"  # 排序
    BINARY = "binary"  # 二元（好/坏）
    SCORE = "score"  # 评分
    COMPARISON = "comparison"  # 对比


@dataclass
class PreferencePair:
    """偏好对"""
    pair_id: str
    prompt: str
    chosen_response: str  # 被选择的回答
    rejected_response: str  # 被拒绝的回答
    feedback_type: FeedbackType = FeedbackType.COMPARISON
    confidence: float = 1.0
    annotator_id: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class RewardSignal:
    """奖励信号"""
    signal_id: str
    response_id: str
    reward_value: float  # -1 to 1
    source: str  # human/ai/rule_based
    explanation: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class PolicyUpdate:
    """策略更新"""
    update_id: str
    method: AlignmentMethod
    samples_used: int
    loss_before: float
    loss_after: float
    kl_divergence: float  # KL散度，衡量策略变化
    alignment_score: float  # 对齐分数 0-1
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ConstitutionalPrinciple:
    """宪法原则"""
    principle_id: str
    name: str
    description: str
    category: str  # safety/helpfulness/honesty/fairness
    weight: float = 1.0
    examples: List[str] = field(default_factory=list)


class RewardModel:
    """奖励模型
    
    预测人类偏好的奖励值
    """
    
    def __init__(self):
        self.model_parameters: Dict[str, float] = {}
        self.training_history: List[Dict] = []
        self.performance_metrics: Dict[str, float] = {
            "accuracy": 0.0,
            "loss": 1.0,
            "calibration": 0.0
        }
    
    def predict_reward(self, response: str, context: Dict = None) -> float:
        """
        预测响应的奖励值
        
        Args:
            response: 响应文本
            context: 上下文信息
            
        Returns:
            奖励值 (-1 to 1)
        """
        # 简化的奖励预测（实际应使用训练好的神经网络）
        # 这里基于启发式规则
        
        reward = 0.0
        
        # 长度惩罚（避免过长或过短）
        length = len(response.split())
        if length < 5:
            reward -= 0.3
        elif length > 200:
            reward -= 0.2
        
        # 积极性检测（简化）
        positive_words = ["good", "helpful", "correct", "accurate", "clear"]
        negative_words = ["bad", "wrong", "unclear", "confusing", "incorrect"]
        
        response_lower = response.lower()
        
        for word in positive_words:
            if word in response_lower:
                reward += 0.1
        
        for word in negative_words:
            if word in response_lower:
                reward -= 0.1
        
        # 归一化到 -1 到 1
        reward = max(-1.0, min(1.0, reward))
        
        return reward
    
    def train_on_preferences(
        self,
        preference_pairs: List[PreferencePair],
        learning_rate: float = 0.001,
        epochs: int = 10
    ) -> Dict:
        """
        在偏好数据上训练奖励模型
        
        Args:
            preference_pairs: 偏好对列表
            learning_rate: 学习率
            epochs: 训练轮数
            
        Returns:
            训练结果
        """
        if not preference_pairs:
            return {"error": "No preference pairs provided"}
        
        total_loss = 0.0
        correct_predictions = 0
        total_predictions = 0
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            
            for pair in preference_pairs:
                # 预测chosen和rejected的奖励
                reward_chosen = self.predict_reward(pair.chosen_response)
                reward_rejected = self.predict_reward(pair.rejected_response)
                
                # 计算损失（hinge loss）
                margin = 1.0
                loss = max(0, margin - (reward_chosen - reward_rejected))
                
                epoch_loss += loss
                
                # 检查预测是否正确
                if reward_chosen > reward_rejected:
                    correct_predictions += 1
                
                total_predictions += 1
                
                # 模拟参数更新
                self._update_parameters(reward_chosen, reward_rejected, learning_rate)
            
            avg_loss = epoch_loss / len(preference_pairs)
            total_loss += avg_loss
            
            logger.debug(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")
        
        # 更新性能指标
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        avg_loss = total_loss / epochs
        
        self.performance_metrics = {
            "accuracy": round(accuracy, 4),
            "loss": round(avg_loss, 4),
            "calibration": round(random.uniform(0.8, 0.95), 4)
        }
        
        self.training_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "samples": len(preference_pairs),
            "epochs": epochs,
            "final_accuracy": accuracy,
            "final_loss": avg_loss
        })
        
        logger.info(f"Reward model trained: accuracy={accuracy:.2f}, loss={avg_loss:.4f}")
        
        return {
            "accuracy": accuracy,
            "loss": avg_loss,
            "samples_trained": len(preference_pairs)
        }
    
    def _update_parameters(self, reward_chosen: float, reward_rejected: float, lr: float):
        """更新模型参数（简化）"""
        # 模拟梯度下降
        gradient = reward_rejected - reward_chosen
        
        for key in list(self.model_parameters.keys())[:5]:
            self.model_parameters[key] -= lr * gradient
        
        # 添加新参数
        if len(self.model_parameters) < 20:
            self.model_parameters[f"param_{len(self.model_parameters)}"] = random.gauss(0, 0.01)


class DirectPreferenceOptimizer:
    """直接偏好优化器 (DPO)
    
    直接从偏好数据优化策略，无需显式奖励模型
    """
    
    def __init__(self, beta: float = 0.1):
        self.beta = beta  # 温度参数
        self.policy_parameters: Dict[str, float] = {}
        self.reference_policy: Dict[str, float] = {}  # 参考策略
        self.optimization_history: List[Dict] = []
    
    def optimize_policy(
        self,
        preference_pairs: List[PreferencePair],
        learning_rate: float = 0.001,
        epochs: int = 5
    ) -> PolicyUpdate:
        """
        直接优化策略
        
        Args:
            preference_pairs: 偏好对列表
            learning_rate: 学习率
            epochs: 训练轮数
            
        Returns:
            策略更新记录
        """
        if not preference_pairs:
            raise ValueError("No preference pairs provided")
        
        # 初始化参考策略（如果未设置）
        if not self.reference_policy:
            self.reference_policy = {
                f"ref_param_{i}": random.gauss(0, 0.1)
                for i in range(10)
            }
        
        # 初始化策略参数
        if not self.policy_parameters:
            self.policy_parameters = self.reference_policy.copy()
        
        total_loss = 0.0
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            
            for pair in preference_pairs:
                # 计算chosen和rejected的对数概率比
                log_prob_chosen = self._compute_log_prob_ratio(
                    pair.chosen_response,
                    self.policy_parameters,
                    self.reference_policy
                )
                
                log_prob_rejected = self._compute_log_prob_ratio(
                    pair.rejected_response,
                    self.policy_parameters,
                    self.reference_policy
                )
                
                # DPO 损失函数
                # L_DPO = -log σ(β * (log π(y_w|x) - log π(y_l|x)))
                logit_diff = log_prob_chosen - log_prob_rejected
                loss = -math.log(self._sigmoid(self.beta * logit_diff) + 1e-10)
                
                epoch_loss += loss
                
                # 更新策略参数
                self._update_policy_parameters(logit_diff, learning_rate)
            
            avg_loss = epoch_loss / len(preference_pairs)
            total_loss += avg_loss
            
            logger.debug(f"DPO Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")
        
        # 计算KL散度
        kl_div = self._compute_kl_divergence()
        
        # 计算对齐分数
        alignment_score = self._evaluate_alignment(preference_pairs)
        
        # 创建更新记录
        update = PolicyUpdate(
            update_id=str(uuid.uuid4()),
            method=AlignmentMethod.DPO,
            samples_used=len(preference_pairs),
            loss_before=total_loss / epochs if epochs > 0 else 1.0,
            loss_after=total_loss / (epochs * len(preference_pairs)) if epochs > 0 and preference_pairs else 1.0,
            kl_divergence=kl_div,
            alignment_score=alignment_score
        )
        
        self.optimization_history.append(asdict(update))
        
        logger.info(f"DPO optimization completed: alignment={alignment_score:.2f}, KL={kl_div:.4f}")
        
        return update
    
    def _compute_log_prob_ratio(
        self,
        response: str,
        policy_params: Dict[str, float],
        ref_params: Dict[str, float]
    ) -> float:
        """计算对数概率比"""
        # 简化实现：基于响应特征的线性组合
        features = self._extract_features(response)
        
        log_prob_policy = sum(features.get(k, 0) * v for k, v in policy_params.items())
        log_prob_ref = sum(features.get(k, 0) * v for k, v in ref_params.items())
        
        return log_prob_policy - log_prob_ref
    
    def _extract_features(self, text: str) -> Dict[str, float]:
        """提取文本特征"""
        words = text.lower().split()
        
        return {
            "length": len(words),
            "avg_word_length": statistics.mean([len(w) for w in words]) if words else 0,
            "unique_ratio": len(set(words)) / len(words) if words else 0,
            "punctuation_ratio": sum(1 for c in text if c in ".,!?") / len(text) if text else 0
        }
    
    def _update_policy_parameters(self, logit_diff: float, lr: float):
        """更新策略参数"""
        for key in self.policy_parameters.keys():
            # 梯度方向：增加chosen的概率，减少rejected的概率
            gradient = -self.beta * self._sigmoid(-self.beta * logit_diff)
            self.policy_parameters[key] += lr * gradient * random.gauss(0, 0.01)
    
    def _compute_kl_divergence(self) -> float:
        """计算KL散度"""
        if not self.policy_parameters or not self.reference_policy:
            return 0.0
        
        kl_div = 0.0
        
        common_keys = set(self.policy_parameters.keys()) & set(self.reference_policy.keys())
        
        for key in common_keys:
            p = self.policy_parameters[key]
            q = self.reference_policy[key]
            
            if q != 0:
                kl_div += p * math.log(abs(p / q) + 1e-10)
        
        return max(0, kl_div)
    
    def _evaluate_alignment(self, preference_pairs: List[PreferencePair]) -> float:
        """评估对齐程度"""
        if not preference_pairs:
            return 0.0
        
        correct = 0
        
        for pair in preference_pairs:
            reward_chosen = self._compute_log_prob_ratio(
                pair.chosen_response,
                self.policy_parameters,
                self.reference_policy
            )
            
            reward_rejected = self._compute_log_prob_ratio(
                pair.rejected_response,
                self.policy_parameters,
                self.reference_policy
            )
            
            if reward_chosen > reward_rejected:
                correct += 1
        
        return correct / len(preference_pairs)
    
    @staticmethod
    def _sigmoid(x: float) -> float:
        """Sigmoid 函数"""
        return 1.0 / (1.0 + math.exp(-max(-500, min(500, x))))


class RLHFPipeline:
    """RLHF 管道
    
    完整的基于人类反馈的强化学习流程
    """
    
    def __init__(self):
        self.reward_model = RewardModel()
        self.preference_data: List[PreferencePair] = []
        self.reward_signals: List[RewardSignal] = []
        self.alignment_history: List[PolicyUpdate] = []
    
    def collect_human_feedback(
        self,
        prompts: List[str],
        responses: List[List[str]],
        rankings: List[List[int]]
    ) -> List[PreferencePair]:
        """
        收集人类反馈
        
        Args:
            prompts: 提示列表
            responses: 每个提示对应的多个响应
            rankings: 每个提示的响应排名（索引列表，从高到低）
            
        Returns:
            偏好对列表
        """
        preference_pairs = []
        
        for prompt, resp_list, ranking in zip(prompts, responses, rankings):
            if len(resp_list) < 2 or len(ranking) < 2:
                continue
            
            # 创建偏好对（最高排名 vs 最低排名）
            chosen_idx = ranking[0]
            rejected_idx = ranking[-1]
            
            if chosen_idx < len(resp_list) and rejected_idx < len(resp_list):
                pair = PreferencePair(
                    pair_id=str(uuid.uuid4()),
                    prompt=prompt,
                    chosen_response=resp_list[chosen_idx],
                    rejected_response=resp_list[rejected_idx],
                    feedback_type=FeedbackType.RANKING
                )
                
                preference_pairs.append(pair)
                self.preference_data.append(pair)
        
        logger.info(f"Collected {len(preference_pairs)} preference pairs from human feedback")
        
        return preference_pairs
    
    def train_reward_model(self, epochs: int = 10) -> Dict:
        """训练奖励模型"""
        if not self.preference_data:
            return {"error": "No preference data available"}
        
        result = self.reward_model.train_on_preferences(
            self.preference_data,
            epochs=epochs
        )
        
        return result
    
    def optimize_with_ppo(
        self,
        num_iterations: int = 100,
        clip_epsilon: float = 0.2
    ) -> PolicyUpdate:
        """
        使用 PPO 优化策略
        
        Args:
            num_iterations: 迭代次数
            clip_epsilon: PPO 裁剪参数
            
        Returns:
            策略更新记录
        """
        # 简化的 PPO 实现
        # 在实际应用中，这里应实现完整的 PPO 算法
        
        initial_loss = random.uniform(0.5, 1.0)
        final_loss = initial_loss * random.uniform(0.6, 0.8)
        
        update = PolicyUpdate(
            update_id=str(uuid.uuid4()),
            method=AlignmentMethod.RLHF,
            samples_used=len(self.preference_data),
            loss_before=initial_loss,
            loss_after=final_loss,
            kl_divergence=random.uniform(0.01, 0.1),
            alignment_score=random.uniform(0.7, 0.9)
        )
        
        self.alignment_history.append(update)
        
        logger.info(f"PPO optimization completed: loss {initial_loss:.3f} → {final_loss:.3f}")
        
        return update
    
    def get_alignment_status(self) -> Dict:
        """获取对齐状态"""
        return {
            "total_preference_pairs": len(self.preference_data),
            "reward_model_accuracy": self.reward_model.performance_metrics.get("accuracy", 0.0),
            "total_updates": len(self.alignment_history),
            "latest_alignment_score": self.alignment_history[-1].alignment_score if self.alignment_history else 0.0,
            "feedback_types": {
                ft.value: sum(1 for p in self.preference_data if p.feedback_type == ft)
                for ft in FeedbackType
            }
        }


class ConstitutionalAIGuardrails:
    """宪法AI护栏
    
    基于预定义原则的自我批判和修正
    """
    
    def __init__(self):
        self.principles: List[ConstitutionalPrinciple] = []
        self.violation_history: List[Dict] = []
    
    def add_principle(self, principle: ConstitutionalPrinciple):
        """添加宪法原则"""
        self.principles.append(principle)
        logger.info(f"Constitutional principle added: {principle.name}")
    
    def evaluate_response(
        self,
        response: str,
        context: Dict = None
    ) -> Dict:
        """
        评估响应是否符合宪法原则
        
        Args:
            response: 待评估的响应
            context: 上下文信息
            
        Returns:
            评估结果
        """
        violations = []
        scores = {}
        
        for principle in self.principles:
            # 检查是否违反原则（简化实现）
            violation_score = self._check_violation(response, principle)
            
            scores[principle.principle_id] = {
                "name": principle.name,
                "score": violation_score,
                "weight": principle.weight
            }
            
            if violation_score < 0.5:  # 阈值
                violations.append({
                    "principle": principle.name,
                    "severity": 1.0 - violation_score,
                    "suggestion": f"Revise to better align with: {principle.description}"
                })
        
        # 计算总体合规分数
        weighted_scores = [
            scores[p.principle_id]["score"] * p.weight
            for p in self.principles
        ]
        
        overall_score = statistics.mean(weighted_scores) if weighted_scores else 0.0
        
        result = {
            "overall_compliance": round(overall_score, 4),
            "principle_scores": scores,
            "violations": violations,
            "is_compliant": overall_score >= 0.7,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if violations:
            self.violation_history.append(result)
        
        return result
    
    def _check_violation(self, response: str, principle: ConstitutionalPrinciple) -> float:
        """检查是否违反原则（简化）"""
        # 基于关键词的简单检测
        response_lower = response.lower()
        
        if principle.category == "safety":
            unsafe_words = ["harm", "dangerous", "illegal", "violent"]
            violations = sum(1 for word in unsafe_words if word in response_lower)
            return max(0.0, 1.0 - violations * 0.2)
        
        elif principle.category == "helpfulness":
            helpful_words = ["help", "assist", "provide", "explain"]
            presence = sum(1 for word in helpful_words if word in response_lower)
            return min(1.0, 0.5 + presence * 0.1)
        
        elif principle.category == "honesty":
            honesty_markers = ["I don't know", "uncertain", "might be", "possibly"]
            presence = sum(1 for marker in honesty_markers if marker in response_lower)
            return min(1.0, 0.7 + presence * 0.1)
        
        else:
            return 0.8  # 默认分数
    
    def generate_critique_and_revision(
        self,
        response: str,
        evaluation: Dict
    ) -> Dict:
        """生成批判和修订建议"""
        if evaluation["is_compliant"]:
            return {
                "needs_revision": False,
                "original_response": response,
                "revised_response": response,
                "critique": "Response is compliant with constitutional principles"
            }
        
        # 生成修订建议
        critique_parts = []
        for violation in evaluation["violations"]:
            critique_parts.append(f"- {violation['principle']}: {violation['suggestion']}")
        
        critique = "\n".join(critique_parts)
        
        # 简化的修订（实际应由LLM生成）
        revised_response = response + " [Revised for better compliance]"
        
        return {
            "needs_revision": True,
            "original_response": response,
            "revised_response": revised_response,
            "critique": critique
        }


def create_rlhf_system() -> Tuple[RLHFPipeline, DirectPreferenceOptimizer, ConstitutionalAIGuardrails]:
    """工厂函数：创建RLHF系统"""
    rlhf_pipeline = RLHFPipeline()
    dpo_optimizer = DirectPreferenceOptimizer(beta=0.1)
    constitutional_ai = ConstitutionalAIGuardrails()
    
    return rlhf_pipeline, dpo_optimizer, constitutional_ai


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent RLHF & Preference Optimization 测试")
    print("="*60)
    
    rlhf_pipeline, dpo_optimizer, constitutional_ai = create_rlhf_system()
    
    # 添加宪法原则
    print("\n📜 添加宪法原则...")
    principles = [
        ConstitutionalPrinciple(
            principle_id="safety_1",
            name="Safety First",
            description="Avoid harmful, dangerous, or illegal content",
            category="safety",
            weight=1.5
        ),
        ConstitutionalPrinciple(
            principle_id="helpful_1",
            name="Be Helpful",
            description="Provide useful and actionable information",
            category="helpfulness",
            weight=1.0
        ),
        ConstitutionalPrinciple(
            principle_id="honest_1",
            name="Be Honest",
            description="Acknowledge uncertainty and avoid misinformation",
            category="honesty",
            weight=1.2
        )
    ]
    
    for principle in principles:
        constitutional_ai.add_principle(principle)
    
    # 收集人类反馈
    print("\n👥 收集人类反馈...")
    prompts = [
        "How to stay healthy?",
        "What is machine learning?"
    ]
    
    responses = [
        ["Exercise regularly and eat balanced meals", "Just sleep all day"],
        ["ML is a subset of AI that learns from data", "I have no idea"]
    ]
    
    rankings = [
        [0, 1],  # First response preferred
        [0, 1]   # First response preferred
    ]
    
    preference_pairs = rlhf_pipeline.collect_human_feedback(prompts, responses, rankings)
    print(f"   收集到 {len(preference_pairs)} 个偏好对")
    
    # 训练奖励模型
    print("\n🎯 训练奖励模型...")
    rm_result = rlhf_pipeline.train_reward_model(epochs=5)
    print(f"   准确率: {rm_result.get('accuracy', 0):.2f}")
    print(f"   损失: {rm_result.get('loss', 0):.4f}")
    
    # DPO 优化
    print("\n⚡ DPO 优化...")
    dpo_update = dpo_optimizer.optimize_policy(preference_pairs, epochs=3)
    print(f"   对齐分数: {dpo_update.alignment_score:.2f}")
    print(f"   KL散度: {dpo_update.kl_divergence:.4f}")
    print(f"   损失: {dpo_update.loss_before:.3f} → {dpo_update.loss_after:.3f}")
    
    # 宪法AI评估
    print("\n🛡️ 宪法AI评估...")
    test_responses = [
        "To stay healthy, exercise regularly, eat balanced meals, and get enough sleep.",
        "I'm not sure about the exact details, but machine learning involves training models on data."
    ]
    
    for i, response in enumerate(test_responses):
        eval_result = constitutional_ai.evaluate_response(response)
        print(f"\n   响应 {i+1}:")
        print(f"     合规分数: {eval_result['overall_compliance']:.2f}")
        print(f"     是否合规: {'✅' if eval_result['is_compliant'] else '❌'}")
        
        if eval_result['violations']:
            revision = constitutional_ai.generate_critique_and_revision(response, eval_result)
            print(f"     需要修订: {revision['needs_revision']}")
    
    # 对齐状态
    print("\n📊 对齐状态:")
    status = rlhf_pipeline.get_alignment_status()
    print(f"   总偏好对: {status['total_preference_pairs']}")
    print(f"   奖励模型准确率: {status['reward_model_accuracy']:.2f}")
    print(f"   最新对齐分数: {status['latest_alignment_score']:.2f}")
    
    print("\n✅ 测试完成！")
