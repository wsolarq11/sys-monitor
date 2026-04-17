#!/usr/bin/env python3
"""
AI Agent Theory of Mind & Mental Modeling System - AI Agent 心智理论与心智建模系统

心智建模、贝叶斯推理、行为预测、社会智能、多智能体协调
实现生产级 AI Agent 的心智理论能力

参考社区最佳实践:
- Theory of Mind (ToM) - understand others' beliefs, desires, intentions
- Mental Modeling - infer and track mental states of other agents
- Bayesian Inference - probabilistic reasoning about mental states
- Behavior Prediction - predict actions based on mental models
- Social Intelligence - effective multi-agent coordination
- BDI Model (Belief-Desire-Intention) - cognitive architecture
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


class MentalStateType(Enum):
    """心智状态类型"""
    BELIEF = "belief"  # 信念
    DESIRE = "desire"  # 欲望
    INTENTION = "intention"  # 意图
    EMOTION = "emotion"  # 情绪
    KNOWLEDGE = "knowledge"  # 知识


class OrderLevel(Enum):
    """心智理论阶数"""
    FIRST_ORDER = "first_order"  # 一阶：我认为他相信什么
    SECOND_ORDER = "second_order"  # 二阶：我认为他认为我相信什么
    THIRD_ORDER = "third_order"  # 三阶及以上


@dataclass
class BeliefState:
    """信念状态"""
    belief_id: str
    content: str  # 信念内容
    confidence: float = 0.5  # 置信度 0-1
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.belief_id:
            self.belief_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class DesireState:
    """欲望状态"""
    desire_id: str
    description: str  # 欲望描述
    priority: float = 0.5  # 优先级 0-1
    urgency: float = 0.5  # 紧急程度 0-1
    
    def __post_init__(self):
        if not self.desire_id:
            self.desire_id = str(uuid.uuid4())


@dataclass
class IntentionState:
    """意图状态"""
    intention_id: str
    goal: str  # 目标
    plan: List[str] = field(default_factory=list)  # 计划步骤
    current_step: int = 0  # 当前步骤
    progress: float = 0.0  # 进度 0-1
    
    def __post_init__(self):
        if not self.intention_id:
            self.intention_id = str(uuid.uuid4())


@dataclass
class EmotionState:
    """情绪状态"""
    emotion_type: str  # 情绪类型（happy/sad/angry/fear等）
    intensity: float = 0.5  # 强度 0-1
    valence: float = 0.0  # 效价 -1到1（负面到正面）
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "type": self.emotion_type,
            "intensity": self.intensity,
            "valence": self.valence
        }


@dataclass
class MentalModel:
    """心智模型
    
    对另一个Agent的心智状态的完整建模
    """
    agent_name: str
    model_id: str = ""
    
    # 一阶信念：我认为他相信什么
    inferred_beliefs: Dict[str, BeliefState] = field(default_factory=dict)
    
    # 一阶欲望：我认为他想要什么
    inferred_desires: Dict[str, DesireState] = field(default_factory=dict)
    
    # 一阶意图：我认为他打算做什么
    inferred_intentions: Dict[str, IntentionState] = field(default_factory=dict)
    
    # 情绪状态推断
    inferred_emotions: Dict[str, EmotionState] = field(default_factory=dict)
    
    # 二阶信念：我认为他认为我相信什么
    second_order_beliefs: Dict[str, float] = field(default_factory=dict)
    
    # 观察历史
    observation_history: List[str] = field(default_factory=list)
    
    # 模型置信度
    confidence: float = 0.5
    
    def __post_init__(self):
        if not self.model_id:
            self.model_id = str(uuid.uuid4())
    
    def update_confidence(self):
        """基于观察数量更新置信度"""
        num_observations = len(self.observation_history)
        self.confidence = min(0.95, 0.5 + num_observations * 0.02)


@dataclass
class BehaviorPrediction:
    """行为预测结果"""
    prediction_id: str
    predicted_action: str  # 预测的行为
    reasoning: str  # 推理过程
    alternative_actions: List[str] = field(default_factory=list)  # 其他可能的行为
    confidence: float = 0.0  # 预测置信度
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.prediction_id:
            self.prediction_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class FalseBeliefTest:
    """错误信念测试（Sally-Anne测试）"""
    test_id: str
    true_state: str  # 真实状态
    observed_by_agent: str  # Agent观察到的
    inferred_belief: str  # 推断的信念
    matches_reality: bool  # 是否与真实一致
    explanation: str  # 解释
    
    def __post_init__(self):
        if not self.test_id:
            self.test_id = str(uuid.uuid4())


class MentalModelManager:
    """心智模型管理器
    
    管理和维护多个Agent的心智模型
    """
    
    def __init__(self):
        self.models: Dict[str, MentalModel] = {}
        self.interaction_history: List[Dict] = []
    
    def create_model(self, agent_name: str) -> MentalModel:
        """创建心智模型"""
        if agent_name in self.models:
            return self.models[agent_name]
        
        model = MentalModel(agent_name=agent_name)
        self.models[agent_name] = model
        
        logger.info(f"Mental model created for: {agent_name}")
        
        return model
    
    def get_model(self, agent_name: str) -> Optional[MentalModel]:
        """获取心智模型"""
        return self.models.get(agent_name)
    
    def update_observation(
        self,
        agent_name: str,
        observation: str,
        context: str = ""
    ):
        """
        更新观察记录
        
        Args:
            agent_name: Agent名称
            observation: 观察内容
            context: 上下文
        """
        if agent_name not in self.models:
            self.create_model(agent_name)
        
        model = self.models[agent_name]
        model.observation_history.append(observation)
        model.update_confidence()
        
        # 记录交互历史
        self.interaction_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent_name,
            "observation": observation,
            "context": context
        })
        
        logger.debug(f"Observation updated for {agent_name}: {observation[:50]}...")
    
    def add_belief(
        self,
        agent_name: str,
        belief_content: str,
        confidence: float = 0.5
    ):
        """添加信念"""
        if agent_name not in self.models:
            self.create_model(agent_name)
        
        model = self.models[agent_name]
        belief = BeliefState(
            belief_id="",
            content=belief_content,
            confidence=confidence
        )
        
        model.inferred_beliefs[belief.belief_id] = belief
        
        logger.info(f"Belief added for {agent_name}: {belief_content[:50]}...")
    
    def add_desire(
        self,
        agent_name: str,
        desire_description: str,
        priority: float = 0.5,
        urgency: float = 0.5
    ):
        """添加欲望"""
        if agent_name not in self.models:
            self.create_model(agent_name)
        
        model = self.models[agent_name]
        desire = DesireState(
            desire_id="",
            description=desire_description,
            priority=priority,
            urgency=urgency
        )
        
        model.inferred_desires[desire.desire_id] = desire
        
        logger.info(f"Desire added for {agent_name}: {desire_description[:50]}...")
    
    def add_intention(
        self,
        agent_name: str,
        goal: str,
        plan: List[str] = None
    ):
        """添加意图"""
        if agent_name not in self.models:
            self.create_model(agent_name)
        
        model = self.models[agent_name]
        intention = IntentionState(
            intention_id="",
            goal=goal,
            plan=plan or []
        )
        
        model.inferred_intentions[intention.intention_id] = intention
        
        logger.info(f"Intention added for {agent_name}: {goal[:50]}...")
    
    def add_emotion(
        self,
        agent_name: str,
        emotion_type: str,
        intensity: float = 0.5,
        valence: float = 0.0
    ):
        """添加情绪"""
        if agent_name not in self.models:
            self.create_model(agent_name)
        
        model = self.models[agent_name]
        emotion = EmotionState(
            emotion_type=emotion_type,
            intensity=intensity,
            valence=valence
        )
        
        model.inferred_emotions[emotion_type] = emotion
        
        logger.info(f"Emotion added for {agent_name}: {emotion_type} (intensity={intensity:.2f})")
    
    def get_model_statistics(self) -> Dict[str, Any]:
        """获取模型统计"""
        if not self.models:
            return {"total_models": 0}
        
        total_beliefs = sum(len(m.inferred_beliefs) for m in self.models.values())
        total_desires = sum(len(m.inferred_desires) for m in self.models.values())
        total_intentions = sum(len(m.inferred_intentions) for m in self.models.values())
        total_emotions = sum(len(m.inferred_emotions) for m in self.models.values())
        
        avg_confidence = statistics.mean([m.confidence for m in self.models.values()])
        
        return {
            "total_models": len(self.models),
            "total_beliefs": total_beliefs,
            "total_desires": total_desires,
            "total_intentions": total_intentions,
            "total_emotions": total_emotions,
            "avg_model_confidence": round(avg_confidence, 4),
            "total_interactions": len(self.interaction_history)
        }


class BayesianInferenceEngine:
    """贝叶斯推理引擎
    
    使用贝叶斯推理进行心智状态推断
    """
    
    def __init__(self):
        self.inference_history: List[Dict] = []
    
    def infer_mental_state(
        self,
        observations: List[str],
        prior_beliefs: Dict[str, float] = None
    ) -> Dict[str, float]:
        """
        基于观察推断心智状态
        
        Args:
            observations: 观察列表
            prior_beliefs: 先验信念
            
        Returns:
            后验信念分布
        """
        if prior_beliefs is None:
            # 均匀先验
            prior_beliefs = {
                "has_urgent_task": 0.5,
                "is_stressed": 0.3,
                "wants_to_help": 0.7,
                "is_confused": 0.2
            }
        
        # 基于观察更新信念（简化贝叶斯更新）
        posterior_beliefs = prior_beliefs.copy()
        
        for obs in observations:
            obs_lower = obs.lower()
            
            # 更新信念（模拟似然函数）
            if "rushed" in obs_lower or "hurried" in obs_lower:
                posterior_beliefs["has_urgent_task"] = min(1.0, posterior_beliefs["has_urgent_task"] * 1.3)
                posterior_beliefs["is_stressed"] = min(1.0, posterior_beliefs["is_stressed"] * 1.2)
            
            if "worried" in obs_lower or "anxious" in obs_lower:
                posterior_beliefs["is_stressed"] = min(1.0, posterior_beliefs["is_stressed"] * 1.4)
            
            if "offered help" in obs_lower or "assisted" in obs_lower:
                posterior_beliefs["wants_to_help"] = min(1.0, posterior_beliefs["wants_to_help"] * 1.2)
            
            if "confused" in obs_lower or "uncertain" in obs_lower:
                posterior_beliefs["is_confused"] = min(1.0, posterior_beliefs["is_confused"] * 1.5)
        
        # 归一化
        total = sum(posterior_beliefs.values())
        if total > 0:
            posterior_beliefs = {k: v / total for k, v in posterior_beliefs.items()}
        
        # 记录推理历史
        self.inference_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "num_observations": len(observations),
            "prior_beliefs_count": len(prior_beliefs),
            "posterior_beliefs_count": len(posterior_beliefs)
        })
        
        logger.info(f"Bayesian inference completed: {len(observations)} observations processed")
        
        return posterior_beliefs
    
    def predict_behavior_bayesian(
        self,
        mental_state: Dict[str, float],
        situation: str
    ) -> BehaviorPrediction:
        """
        基于贝叶斯心智状态预测行为
        
        Args:
            mental_state: 心智状态分布
            situation: 情境描述
            
        Returns:
            行为预测
        """
        # 基于心智状态和情境生成预测
        predictions = []
        
        if mental_state.get("has_urgent_task", 0) > 0.6:
            predictions.append(("Rush to complete task", 0.8))
        
        if mental_state.get("is_stressed", 0) > 0.5:
            predictions.append(("Show signs of stress", 0.7))
        
        if mental_state.get("wants_to_help", 0) > 0.6:
            predictions.append(("Offer assistance to others", 0.75))
        
        if mental_state.get("is_confused", 0) > 0.4:
            predictions.append(("Ask clarifying questions", 0.65))
        
        if not predictions:
            predictions.append(("Continue normal activities", 0.5))
        
        # 选择最高概率的预测
        predictions.sort(key=lambda x: x[1], reverse=True)
        best_prediction = predictions[0]
        
        prediction = BehaviorPrediction(
            prediction_id="",
            predicted_action=best_prediction[0],
            reasoning=f"Based on mental state analysis in situation: {situation}",
            alternative_actions=[p[0] for p in predictions[1:]],
            confidence=best_prediction[1]
        )
        
        logger.info(f"Behavior predicted: {prediction.predicted_action[:50]}... (confidence={prediction.confidence:.2f})")
        
        return prediction
    
    def get_inference_statistics(self) -> Dict[str, Any]:
        """获取推理统计"""
        return {
            "total_inferences": len(self.inference_history),
            "avg_observations_per_inference": round(
                statistics.mean([h["num_observations"] for h in self.inference_history]), 2
            ) if self.inference_history else 0
        }


class FalseBeliefTester:
    """错误信念测试器
    
    执行经典的Sally-Anne测试等错误信念任务
    """
    
    def __init__(self):
        self.tests: List[FalseBeliefTest] = []
    
    def run_sally_anne_test(
        self,
        agent_name: str,
        true_state: str,
        what_agent_saw: str
    ) -> FalseBeliefTest:
        """
        运行Sally-Anne错误信念测试
        
        Args:
            agent_name: Agent名称
            true_state: 真实状态
            what_agent_saw: Agent观察到的
            
        Returns:
            测试结果
        """
        # 推断Agent的信念
        if what_agent_saw == true_state:
            inferred_belief = true_state
            matches_reality = True
            explanation = "Agent's belief matches reality"
        else:
            inferred_belief = what_agent_saw
            matches_reality = False
            explanation = f"Agent holds false belief: believes '{what_agent_saw}' but reality is '{true_state}'"
        
        test = FalseBeliefTest(
            test_id="",
            true_state=true_state,
            observed_by_agent=what_agent_saw,
            inferred_belief=inferred_belief,
            matches_reality=matches_reality,
            explanation=explanation
        )
        
        self.tests.append(test)
        
        logger.info(f"Sally-Anne test for {agent_name}: matches_reality={matches_reality}")
        
        return test
    
    def get_test_statistics(self) -> Dict[str, Any]:
        """获取测试统计"""
        if not self.tests:
            return {"total_tests": 0}
        
        correct_beliefs = sum(1 for t in self.tests if t.matches_reality)
        false_beliefs = sum(1 for t in self.tests if not t.matches_reality)
        
        return {
            "total_tests": len(self.tests),
            "correct_beliefs": correct_beliefs,
            "false_beliefs": false_beliefs,
            "accuracy": round(correct_beliefs / len(self.tests), 4) if self.tests else 0
        }


class TheoryOfMindSystem:
    """心智理论系统
    
    整合心智建模、贝叶斯推理、行为预测
    """
    
    def __init__(self):
        self.model_manager = MentalModelManager()
        self.bayesian_engine = BayesianInferenceEngine()
        self.false_belief_tester = FalseBeliefTester()
    
    def observe_and_update_model(
        self,
        observer: str,
        observed_agent: str,
        observation: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        观察并更新心智模型
        
        Args:
            observer: 观察者
            observed_agent: 被观察的Agent
            observation: 观察内容
            context: 上下文
            
        Returns:
            更新结果
        """
        # 更新观察记录
        self.model_manager.update_observation(observed_agent, observation, context)
        
        # 基于观察推断心智状态
        observations_list = [observation]
        inferred_state = self.bayesian_engine.infer_mental_state(observations_list)
        
        # 添加推断的信念
        for belief_name, confidence in inferred_state.items():
            if confidence > 0.5:
                self.model_manager.add_belief(
                    observed_agent,
                    f"{belief_name.replace('_', ' ').title()}",
                    confidence
                )
        
        result = {
            "observer": observer,
            "observed_agent": observed_agent,
            "observation": observation,
            "inferred_mental_state": inferred_state,
            "model_confidence": self.model_manager.get_model(observed_agent).confidence
        }
        
        logger.info(f"Model updated for {observed_agent} by {observer}")
        
        return result
    
    def predict_agent_behavior(
        self,
        agent_name: str,
        situation: str
    ) -> BehaviorPrediction:
        """
        预测Agent行为
        
        Args:
            agent_name: Agent名称
            situation: 情境
            
        Returns:
            行为预测
        """
        model = self.model_manager.get_model(agent_name)
        
        if not model:
            return BehaviorPrediction(
                prediction_id="",
                predicted_action="Unknown (no model available)",
                reasoning="No mental model exists for this agent",
                confidence=0.0
            )
        
        # 构建心智状态
        mental_state = {
            "has_urgent_task": max([b.confidence for b in model.inferred_beliefs.values()], default=0.5),
            "is_stressed": model.inferred_emotions.get("stressed", EmotionState("stressed", 0.3)).intensity,
            "wants_to_help": 0.7,  # 默认值
            "is_confused": model.inferred_emotions.get("confused", EmotionState("confused", 0.2)).intensity
        }
        
        # 贝叶斯行为预测
        prediction = self.bayesian_engine.predict_behavior_bayesian(mental_state, situation)
        
        return prediction
    
    def run_false_belief_test(
        self,
        agent_name: str,
        true_state: str,
        observed_state: str
    ) -> FalseBeliefTest:
        """
        运行错误信念测试
        
        Args:
            agent_name: Agent名称
            true_state: 真实状态
            observed_state: 观察到的状态
            
        Returns:
            测试结果
        """
        return self.false_belief_tester.run_sally_anne_test(
            agent_name, true_state, observed_state
        )
    
    def get_system_overview(self) -> Dict[str, Any]:
        """获取系统概览"""
        return {
            "mental_models": self.model_manager.get_model_statistics(),
            "bayesian_inference": self.bayesian_engine.get_inference_statistics(),
            "false_belief_tests": self.false_belief_tester.get_test_statistics()
        }


def create_theory_of_mind_system() -> TheoryOfMindSystem:
    """工厂函数：创建心智理论系统"""
    system = TheoryOfMindSystem()
    return system


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Theory of Mind & Mental Modeling 测试")
    print("="*60)
    
    system = create_theory_of_mind_system()
    
    # 测试心智模型管理
    print("\n🧠 测试心智模型管理...")
    
    # Alice观察Bob
    observations = [
        "Bob看了看手表，皱了皱眉",
        "Bob快步走向会议室",
        "Bob在门口停下来深呼吸"
    ]
    
    for obs in observations:
        result = system.observe_and_update_model(
            observer="Alice",
            observed_agent="Bob",
            observation=obs,
            context="现在是下午2:55，3点有重要会议"
        )
        print(f"   观察: {obs[:30]}...")
        print(f"     推断心智状态: {list(result['inferred_mental_state'].keys())}")
        print(f"     模型置信度: {result['model_confidence']:.2f}")
    
    # 添加明确的信念、欲望、意图
    print("\n💭 添加明确的心智状态...")
    system.model_manager.add_belief("Bob", "Meeting is important", 0.9)
    system.model_manager.add_desire("Bob", "Arrive on time", priority=0.9, urgency=0.8)
    system.model_manager.add_intention("Bob", "Attend meeting", plan=["Walk to room", "Enter room", "Sit down"])
    system.model_manager.add_emotion("Bob", "anxious", intensity=0.7, valence=-0.5)
    
    # 查看Bob的心智模型
    bob_model = system.model_manager.get_model("Bob")
    print(f"\n   Bob的心智模型:")
    print(f"     信念数: {len(bob_model.inferred_beliefs)}")
    print(f"     欲望数: {len(bob_model.inferred_desires)}")
    print(f"     意图数: {len(bob_model.inferred_intentions)}")
    print(f"     情绪数: {len(bob_model.inferred_emotions)}")
    print(f"     观察历史: {len(bob_model.observation_history)}条")
    print(f"     模型置信度: {bob_model.confidence:.2f}")
    
    # 测试行为预测
    print("\n🔮 测试行为预测...")
    prediction = system.predict_agent_behavior(
        agent_name="Bob",
        situation="会议室门锁着"
    )
    
    print(f"   预测行为: {prediction.predicted_action}")
    print(f"   推理: {prediction.reasoning[:50]}...")
    print(f"   置信度: {prediction.confidence:.2f}")
    if prediction.alternative_actions:
        print(f"   替代行为: {', '.join(prediction.alternative_actions[:2])}")
    
    # 测试错误信念（Sally-Anne测试）
    print("\n🧪 测试错误信念（Sally-Anne测试）...")
    
    # 场景1：Bob看到球在篮子里，但球被移到了盒子里
    test1 = system.run_false_belief_test(
        agent_name="Bob",
        true_state="Ball is in the box",
        observed_state="Ball is in the basket"
    )
    
    print(f"   测试1:")
    print(f"     真实状态: {test1.true_state}")
    print(f"     Bob观察到: {test1.observed_by_agent}")
    print(f"     Bob相信: {test1.inferred_belief}")
    print(f"     与现实一致: {test1.matches_reality}")
    print(f"     解释: {test1.explanation[:60]}...")
    
    # 场景2：Charlie看到球被移到盒子里
    test2 = system.run_false_belief_test(
        agent_name="Charlie",
        true_state="Ball is in the box",
        observed_state="Ball is in the box"
    )
    
    print(f"\n   测试2:")
    print(f"     真实状态: {test2.true_state}")
    print(f"     Charlie观察到: {test2.observed_by_agent}")
    print(f"     Charlie相信: {test2.inferred_belief}")
    print(f"     与现实一致: {test2.matches_reality}")
    print(f"     解释: {test2.explanation[:60]}...")
    
    # 测试贝叶斯推理
    print("\n📊 测试贝叶斯推理...")
    mental_state = system.bayesian_engine.infer_mental_state(
        observations=["Bob rushed to the door", "Bob looked worried"],
        prior_beliefs={"has_urgent_task": 0.5, "is_stressed": 0.3}
    )
    
    print(f"   推断的心智状态:")
    for state, prob in mental_state.items():
        print(f"     {state}: {prob:.2f}")
    
    # 系统概览
    overview = system.get_system_overview()
    print(f"\n📈 系统概览:")
    print(f"   心智模型:")
    mm = overview['mental_models']
    print(f"     总模型数: {mm['total_models']}")
    print(f"     总信念数: {mm['total_beliefs']}")
    print(f"     总欲望数: {mm['total_desires']}")
    print(f"     总意图数: {mm['total_intentions']}")
    print(f"     平均置信度: {mm['avg_model_confidence']:.2f}")
    print(f"   贝叶斯推理:")
    bi = overview['bayesian_inference']
    print(f"     总推理数: {bi['total_inferences']}")
    print(f"   错误信念测试:")
    fb = overview['false_belief_tests']
    print(f"     总测试数: {fb['total_tests']}")
    print(f"     正确信念: {fb['correct_beliefs']}")
    print(f"     错误信念: {fb['false_beliefs']}")
    print(f"     准确率: {fb['accuracy']*100:.1f}%")
    
    print("\n✅ 测试完成！")
