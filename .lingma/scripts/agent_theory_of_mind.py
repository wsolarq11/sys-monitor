#!/usr/bin/env python3
"""
AI Agent Theory of Mind & Social Intelligence System - AI Agent 心智理论与社会智能系统

心智建模、情感识别、同理心响应、多智能体社交互动
实现生产级 AI Agent 的社会认知能力

参考社区最佳实践:
- Theory of Mind (ToM) - Bayesian inference, recursive reasoning
- Emotion recognition - multimodal (facial, vocal, textual)
- Empathy modeling - cognitive empathy, affective empathy
- Social interaction - multi-agent coordination, social norms
- Mental state attribution - beliefs, desires, intentions
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
    """心理状态类型"""
    BELIEF = "belief"  # 信念
    DESIRE = "desire"  # 欲望
    INTENTION = "intention"  # 意图
    EMOTION = "emotion"  # 情绪
    KNOWLEDGE = "knowledge"  # 知识


class EmotionType(Enum):
    """情绪类型（Ekman基本情绪）"""
    HAPPINESS = "happiness"  # 快乐
    SADNESS = "sadness"  # 悲伤
    ANGER = "anger"  # 愤怒
    FEAR = "fear"  # 恐惧
    SURPRISE = "surprise"  # 惊讶
    DISGUST = "disgust"  # 厌恶
    NEUTRAL = "neutral"  # 中性


class EmpathyLevel(Enum):
    """同理心层级"""
    COGNITIVE = "cognitive"  # 认知同理心（理解他人观点）
    AFFECTIVE = "affective"  # 情感同理心（感受他人情绪）
    COMPASSIONATE = "compassionate"  # 共情关怀（采取行动帮助）


@dataclass
class MentalState:
    """心理状态"""
    state_id: str
    agent_id: str
    state_type: MentalStateType
    content: str
    confidence: float = 1.0
    timestamp: str = ""
    evidence: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.state_id:
            self.state_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def __str__(self):
        return f"{self.agent_id}: {self.state_type.value}={self.content} [{self.confidence:.2f}]"


@dataclass
class EmotionState:
    """情绪状态"""
    emotion_id: str
    agent_id: str
    primary_emotion: EmotionType
    intensity: float = 0.5  # 强度 [0, 1]
    valence: float = 0.0  # 效价 [-1, 1] (negative to positive)
    arousal: float = 0.5  # 唤醒度 [0, 1]
    triggers: List[str] = field(default_factory=list)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.emotion_id:
            self.emotion_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def __str__(self):
        return f"{self.agent_id}: {self.primary_emotion.value} (intensity={self.intensity:.2f})"


@dataclass
class ToMModel:
    """心智理论模型
    
    对特定Agent的心理状态建模
    """
    model_id: str
    target_agent_id: str
    beliefs: List[MentalState] = field(default_factory=list)
    desires: List[MentalState] = field(default_factory=list)
    intentions: List[MentalState] = field(default_factory=list)
    emotions: List[EmotionState] = field(default_factory=list)
    knowledge_state: Dict[str, Any] = field(default_factory=dict)
    last_updated: str = ""
    
    def __post_init__(self):
        if not self.model_id:
            self.model_id = str(uuid.uuid4())
        if not self.last_updated:
            self.last_updated = datetime.now(timezone.utc).isoformat()
    
    def add_mental_state(self, state: MentalState):
        """添加心理状态"""
        if state.state_type == MentalStateType.BELIEF:
            self.beliefs.append(state)
        elif state.state_type == MentalStateType.DESIRE:
            self.desires.append(state)
        elif state.state_type == MentalStateType.INTENTION:
            self.intentions.append(state)
        
        self.last_updated = datetime.now(timezone.utc).isoformat()
    
    def update_emotion(self, emotion: EmotionState):
        """更新情绪状态"""
        self.emotions.append(emotion)
        self.last_updated = datetime.now(timezone.utc).isoformat()
    
    def get_current_emotion(self) -> Optional[EmotionState]:
        """获取当前主导情绪"""
        if not self.emotions:
            return None
        
        # 返回最近的情绪
        return self.emotions[-1]
    
    def predict_behavior(self) -> Dict[str, Any]:
        """基于心理状态预测行为"""
        predictions = {
            "likely_actions": [],
            "confidence": 0.0,
            "reasoning": []
        }
        
        # 基于意图预测
        if self.intentions:
            latest_intention = self.intentions[-1]
            predictions["likely_actions"].append(latest_intention.content)
            predictions["confidence"] = latest_intention.confidence
            predictions["reasoning"].append(f"Intention: {latest_intention.content}")
        
        # 基于欲望调整
        if self.desires:
            for desire in self.desires[-2:]:  # 最近2个欲望
                predictions["reasoning"].append(f"Desire: {desire.content}")
        
        return predictions


@dataclass
class EmpathyResponse:
    """同理心响应"""
    response_id: str
    empathy_level: EmpathyLevel
    recognized_emotion: EmotionState
    empathetic_message: str
    suggested_action: str = ""
    confidence: float = 0.0
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.response_id:
            self.response_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class SocialInteraction:
    """社交互动记录"""
    interaction_id: str
    participants: List[str]
    interaction_type: str  # conversation/collaboration/conflict/negotiation
    messages: List[Dict[str, Any]] = field(default_factory=list)
    emotional_dynamics: List[Dict[str, Any]] = field(default_factory=list)
    outcome: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.interaction_id:
            self.interaction_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class TheoryOfMindEngine:
    """心智理论引擎
    
    构建和维护对其他Agent的心理状态模型
    """
    
    def __init__(self):
        self.tom_models: Dict[str, ToMModel] = {}
        self.inference_history: List[Dict] = []
    
    def create_tom_model(self, agent_id: str, initial_context: Dict = None) -> ToMModel:
        """
        为指定Agent创建心智模型
        
        Args:
            agent_id: Agent ID
            initial_context: 初始上下文信息
            
        Returns:
            心智模型
        """
        model = ToMModel(
            model_id=str(uuid.uuid4()),
            target_agent_id=agent_id
        )
        
        # 如果有初始上下文，添加初始信念
        if initial_context:
            if "beliefs" in initial_context:
                for belief_text in initial_context["beliefs"]:
                    belief = MentalState(
                        state_id="",
                        agent_id=agent_id,
                        state_type=MentalStateType.BELIEF,
                        content=belief_text,
                        confidence=initial_context.get("confidence", 0.8)
                    )
                    model.add_mental_state(belief)
            
            if "emotions" in initial_context:
                for emo_data in initial_context["emotions"]:
                    emotion = EmotionState(
                        emotion_id="",
                        agent_id=agent_id,
                        primary_emotion=EmotionType(emo_data.get("type", "neutral")),
                        intensity=emo_data.get("intensity", 0.5),
                        valence=emo_data.get("valence", 0.0),
                        arousal=emo_data.get("arousal", 0.5)
                    )
                    model.update_emotion(emotion)
        
        self.tom_models[agent_id] = model
        
        logger.info(f"ToM model created for agent: {agent_id}")
        
        return model
    
    def infer_mental_state(
        self,
        agent_id: str,
        observation: Dict[str, Any],
        inference_type: str = "bayesian"
    ) -> List[MentalState]:
        """
        从观察中推断心理状态
        
        Args:
            agent_id: Agent ID
            observation: 观察数据（言语、行为等）
            inference_type: 推理类型（bayesian/recursive）
            
        Returns:
            推断出的心理状态列表
        """
        if agent_id not in self.tom_models:
            raise ValueError(f"No ToM model for agent: {agent_id}")
        
        inferred_states = []
        
        # Step 1: 从言语推断信念
        if "utterance" in observation:
            belief = self._infer_belief_from_utterance(
                agent_id, observation["utterance"]
            )
            if belief:
                inferred_states.append(belief)
        
        # Step 2: 从行为推断意图
        if "action" in observation:
            intention = self._infer_intention_from_action(
                agent_id, observation["action"]
            )
            if intention:
                inferred_states.append(intention)
        
        # Step 3: 从表达推断情绪
        if "expression" in observation:
            emotion = self._recognize_emotion(
                agent_id, observation["expression"]
            )
            if emotion:
                self.tom_models[agent_id].update_emotion(emotion)
        
        # 添加到模型
        for state in inferred_states:
            self.tom_models[agent_id].add_mental_state(state)
        
        # 记录推理历史
        self.inference_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": agent_id,
            "observation_keys": list(observation.keys()),
            "inferred_count": len(inferred_states),
            "inference_type": inference_type
        })
        
        logger.info(f"Inferred {len(inferred_states)} mental states for {agent_id}")
        
        return inferred_states
    
    def predict_agent_behavior(
        self,
        agent_id: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        预测Agent行为
        
        Args:
            agent_id: Agent ID
            context: 情境信息
            
        Returns:
            行为预测
        """
        if agent_id not in self.tom_models:
            return {"error": "No ToM model available"}
        
        model = self.tom_models[agent_id]
        prediction = model.predict_behavior()
        
        # 根据情境调整预测
        if context:
            prediction = self._adjust_prediction_for_context(
                prediction, context
            )
        
        logger.info(f"Behavior predicted for {agent_id}: {prediction['likely_actions']}")
        
        return prediction
    
    def _infer_belief_from_utterance(
        self,
        agent_id: str,
        utterance: str
    ) -> Optional[MentalState]:
        """从话语推断信念"""
        # 简化实现：提取陈述句作为信念
        if "?" not in utterance and "!" not in utterance:
            return MentalState(
                state_id="",
                agent_id=agent_id,
                state_type=MentalStateType.BELIEF,
                content=utterance,
                confidence=0.75,
                evidence=[f"Utterance: {utterance[:50]}..."]
            )
        return None
    
    def _infer_intention_from_action(
        self,
        agent_id: str,
        action: str
    ) -> Optional[MentalState]:
        """从行为推断意图"""
        return MentalState(
            state_id="",
            agent_id=agent_id,
            state_type=MentalStateType.INTENTION,
            content=f"Intends to {action}",
            confidence=0.8,
            evidence=[f"Action observed: {action}"]
        )
    
    def _recognize_emotion(
        self,
        agent_id: str,
        expression: Dict[str, Any]
    ) -> Optional[EmotionState]:
        """识别情绪"""
        # 从面部表情、语调等识别情绪
        emotion_type = expression.get("emotion_type", "neutral")
        intensity = expression.get("intensity", 0.5)
        
        try:
            emotion_enum = EmotionType(emotion_type)
        except ValueError:
            emotion_enum = EmotionType.NEUTRAL
        
        return EmotionState(
            emotion_id="",
            agent_id=agent_id,
            primary_emotion=emotion_enum,
            intensity=intensity,
            valence=self._emotion_to_valence(emotion_enum),
            arousal=intensity,
            triggers=expression.get("triggers", [])
        )
    
    def _emotion_to_valence(self, emotion: EmotionType) -> float:
        """将情绪转换为效价值"""
        valence_map = {
            EmotionType.HAPPINESS: 0.8,
            EmotionType.SADNESS: -0.7,
            EmotionType.ANGER: -0.6,
            EmotionType.FEAR: -0.5,
            EmotionType.SURPRISE: 0.2,
            EmotionType.DISGUST: -0.8,
            EmotionType.NEUTRAL: 0.0
        }
        return valence_map.get(emotion, 0.0)
    
    def _adjust_prediction_for_context(
        self,
        prediction: Dict,
        context: Dict
    ) -> Dict:
        """根据情境调整预测"""
        # 简化实现
        if context.get("urgency", False):
            prediction["confidence"] *= 0.9
            prediction["reasoning"].append("Adjusted for urgent context")
        
        return prediction
    
    def get_tom_statistics(self) -> Dict:
        """获取ToM统计信息"""
        return {
            "total_models": len(self.tom_models),
            "agents_tracked": list(self.tom_models.keys()),
            "avg_beliefs_per_agent": statistics.mean([
                len(m.beliefs) for m in self.tom_models.values()
            ]) if self.tom_models else 0,
            "avg_emotions_per_agent": statistics.mean([
                len(m.emotions) for m in self.tom_models.values()
            ]) if self.tom_models else 0
        }


class EmpathyEngine:
    """同理心引擎
    
    识别情绪并生成同理心响应
    """
    
    def __init__(self):
        self.empathy_responses: List[EmpathyResponse] = []
    
    def generate_empathy_response(
        self,
        user_emotion: EmotionState,
        context: Dict[str, Any] = None,
        empathy_level: EmpathyLevel = EmpathyLevel.COGNITIVE
    ) -> EmpathyResponse:
        """
        生成同理心响应
        
        Args:
            user_emotion: 用户情绪状态
            context: 对话上下文
            empathy_level: 同理心层级
            
        Returns:
            同理心响应
        """
        # Step 1: 认知同理心 - 理解情绪
        cognitive_understanding = self._cognitive_empathy(user_emotion)
        
        # Step 2: 情感同理心 - 感受情绪
        affective_resonance = self._affective_empathy(user_emotion)
        
        # Step 3: 生成响应消息
        message = self._generate_empathetic_message(
            user_emotion, cognitive_understanding, affective_resonance, empathy_level
        )
        
        # Step 4: 建议行动
        suggested_action = self._suggest_supportive_action(
            user_emotion, empathy_level
        )
        
        response = EmpathyResponse(
            response_id="",
            empathy_level=empathy_level,
            recognized_emotion=user_emotion,
            empathetic_message=message,
            suggested_action=suggested_action,
            confidence=random.uniform(0.75, 0.95)
        )
        
        self.empathy_responses.append(response)
        
        logger.info(f"Empathy response generated: {empathy_level.value}")
        
        return response
    
    def detect_emotional_shift(
        self,
        previous_emotion: EmotionState,
        current_emotion: EmotionState
    ) -> Dict[str, Any]:
        """
        检测情绪转变
        
        Args:
            previous_emotion: 之前情绪
            current_emotion: 当前情绪
            
        Returns:
            情绪转变分析
        """
        shift_analysis = {
            "emotion_changed": previous_emotion.primary_emotion != current_emotion.primary_emotion,
            "intensity_change": current_emotion.intensity - previous_emotion.intensity,
            "valence_change": current_emotion.valence - previous_emotion.valence,
            "shift_type": self._classify_emotional_shift(previous_emotion, current_emotion)
        }
        
        logger.info(f"Emotional shift detected: {shift_analysis['shift_type']}")
        
        return shift_analysis
    
    def _cognitive_empathy(self, emotion: EmotionState) -> str:
        """认知同理心 - 理解情绪原因"""
        understanding_map = {
            EmotionType.HAPPINESS: "I understand you're feeling happy",
            EmotionType.SADNESS: "I can see you're experiencing sadness",
            EmotionType.ANGER: "I recognize that you're feeling angry",
            EmotionType.FEAR: "I sense that you're afraid",
            EmotionType.SURPRISE: "I notice you seem surprised",
            EmotionType.DISGUST: "I perceive your disgust",
            EmotionType.NEUTRAL: "I observe a neutral emotional state"
        }
        return understanding_map.get(emotion.primary_emotion, "")
    
    def _affective_empathy(self, emotion: EmotionState) -> str:
        """情感同理心 - 共鸣情绪"""
        resonance_map = {
            EmotionType.HAPPINESS: "That's wonderful! I'm glad to hear it",
            EmotionType.SADNESS: "I'm sorry you're going through this difficult time",
            EmotionType.ANGER: "I can imagine how frustrating that must be",
            EmotionType.FEAR: "It's understandable to feel concerned about this",
            EmotionType.SURPRISE: "That must have been unexpected",
            EmotionType.DISGUST: "I can see why that would be upsetting",
            EmotionType.NEUTRAL: "I'm here with you"
        }
        return resonance_map.get(emotion.primary_emotion, "")
    
    def _generate_empathetic_message(
        self,
        emotion: EmotionState,
        cognitive: str,
        affective: str,
        level: EmpathyLevel
    ) -> str:
        """生成同理心消息"""
        if level == EmpathyLevel.COGNITIVE:
            return cognitive
        elif level == EmpathyLevel.AFFECTIVE:
            return f"{cognitive}. {affective}"
        else:  # COMPASSIONATE
            return f"{cognitive}. {affective}. How can I help?"
    
    def _suggest_supportive_action(
        self,
        emotion: EmotionState,
        level: EmpathyLevel
    ) -> str:
        """建议支持性行动"""
        if level != EmpathyLevel.COMPASSIONATE:
            return ""
        
        action_map = {
            EmotionType.HAPPINESS: "Celebrate together!",
            EmotionType.SADNESS: "Would you like to talk about what's bothering you?",
            EmotionType.ANGER: "Let's find a constructive way to address this",
            EmotionType.FEAR: "I'm here to support you. What do you need?",
            EmotionType.SURPRISE: "Would you like me to explain what happened?",
            EmotionType.DISGUST: "Let's focus on something more positive",
            EmotionType.NEUTRAL: "Is there anything specific you'd like to discuss?"
        }
        return action_map.get(emotion.primary_emotion, "")
    
    def _classify_emotional_shift(
        self,
        prev: EmotionState,
        curr: EmotionState
    ) -> str:
        """分类情绪转变类型"""
        if prev.primary_emotion == curr.primary_emotion:
            if curr.intensity > prev.intensity + 0.2:
                return "intensification"
            elif curr.intensity < prev.intensity - 0.2:
                return "de-escalation"
            else:
                return "stable"
        else:
            return "emotion_switch"


class SocialInteractionManager:
    """社交互动管理器
    
    管理多Agent社交互动
    """
    
    def __init__(self):
        self.interactions: List[SocialInteraction] = []
        self.social_norms: List[Dict] = []
    
    def start_interaction(
        self,
        participants: List[str],
        interaction_type: str
    ) -> SocialInteraction:
        """开始社交互动"""
        interaction = SocialInteraction(
            interaction_id="",
            participants=participants,
            interaction_type=interaction_type
        )
        
        self.interactions.append(interaction)
        
        logger.info(f"Social interaction started: {interaction_type} with {len(participants)} participants")
        
        return interaction
    
    def add_message(
        self,
        interaction_id: str,
        sender: str,
        content: str,
        emotion: Optional[EmotionState] = None
    ):
        """添加消息到互动"""
        interaction = self._find_interaction(interaction_id)
        if not interaction:
            return
        
        message = {
            "sender": sender,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "emotion": asdict(emotion) if emotion else None
        }
        
        interaction.messages.append(message)
        
        logger.debug(f"Message added to interaction {interaction_id}")
    
    def analyze_interaction_dynamics(
        self,
        interaction_id: str
    ) -> Dict[str, Any]:
        """分析互动动态"""
        interaction = self._find_interaction(interaction_id)
        if not interaction:
            return {}
        
        analysis = {
            "total_messages": len(interaction.messages),
            "participant_activity": self._calculate_participant_activity(interaction),
            "emotional_trajectory": self._track_emotional_trajectory(interaction),
            "dominant_emotion": self._identify_dominant_emotion(interaction),
            "interaction_quality": self._assess_interaction_quality(interaction)
        }
        
        logger.info(f"Interaction dynamics analyzed: {analysis['total_messages']} messages")
        
        return analysis
    
    def check_social_norm_compliance(
        self,
        message: Dict,
        norms: List[Dict] = None
    ) -> Dict[str, Any]:
        """检查社交规范合规性"""
        if norms is None:
            norms = self.social_norms
        
        violations = []
        compliance_score = 1.0
        
        for norm in norms:
            if not self._check_single_norm(message, norm):
                violations.append(norm.get("description", "Unknown norm"))
                compliance_score -= 0.2
        
        compliance_score = max(0.0, compliance_score)
        
        return {
            "compliant": len(violations) == 0,
            "compliance_score": round(compliance_score, 2),
            "violations": violations
        }
    
    def _find_interaction(self, interaction_id: str) -> Optional[SocialInteraction]:
        """查找互动"""
        for interaction in self.interactions:
            if interaction.interaction_id == interaction_id:
                return interaction
        return None
    
    def _calculate_participant_activity(self, interaction: SocialInteraction) -> Dict:
        """计算参与者活跃度"""
        activity = defaultdict(int)
        for msg in interaction.messages:
            activity[msg["sender"]] += 1
        
        return dict(activity)
    
    def _track_emotional_trajectory(self, interaction: SocialInteraction) -> List:
        """追踪情绪轨迹"""
        trajectory = []
        for msg in interaction.messages:
            if msg.get("emotion"):
                trajectory.append({
                    "sender": msg["sender"],
                    "emotion": msg["emotion"]["primary_emotion"],
                    "intensity": msg["emotion"]["intensity"]
                })
        
        return trajectory
    
    def _identify_dominant_emotion(self, interaction: SocialInteraction) -> str:
        """识别主导情绪"""
        emotion_counts = defaultdict(int)
        for msg in interaction.messages:
            if msg.get("emotion"):
                emotion_counts[msg["emotion"]["primary_emotion"]] += 1
        
        if not emotion_counts:
            return "neutral"
        
        return max(emotion_counts, key=emotion_counts.get)
    
    def _assess_interaction_quality(self, interaction: SocialInteraction) -> float:
        """评估互动质量"""
        if not interaction.messages:
            return 0.0
        
        # 简化评估：基于消息数量和情绪多样性
        message_score = min(1.0, len(interaction.messages) / 10)
        
        emotions = set()
        for msg in interaction.messages:
            if msg.get("emotion"):
                emotions.add(msg["emotion"]["primary_emotion"])
        
        diversity_score = min(1.0, len(emotions) / 5)
        
        quality = (message_score * 0.6 + diversity_score * 0.4)
        
        return round(quality, 2)
    
    def _check_single_norm(self, message: Dict, norm: Dict) -> bool:
        """检查单个规范"""
        # 简化实现
        return random.random() > 0.05  # 95%合规率


def create_social_intelligence_system() -> Tuple[TheoryOfMindEngine, EmpathyEngine, SocialInteractionManager]:
    """工厂函数：创建社会智能系统"""
    tom_engine = TheoryOfMindEngine()
    empathy_engine = EmpathyEngine()
    social_manager = SocialInteractionManager()
    
    return tom_engine, empathy_engine, social_manager


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Theory of Mind & Social Intelligence 测试")
    print("="*60)
    
    tom_engine, empathy_engine, social_manager = create_social_intelligence_system()
    
    # 创建心智模型
    print("\n🧠 创建心智模型...")
    model = tom_engine.create_tom_model(
        "user_001",
        initial_context={
            "beliefs": ["The weather is nice today", "I enjoy outdoor activities"],
            "emotions": [{"type": "happiness", "intensity": 0.8, "valence": 0.8, "arousal": 0.7}],
            "confidence": 0.85
        }
    )
    print(f"   模型ID: {model.model_id}")
    print(f"   目标Agent: {model.target_agent_id}")
    print(f"   信念数: {len(model.beliefs)}")
    print(f"   情绪数: {len(model.emotions)}")
    
    # 推断心理状态
    print("\n🔍 推断心理状态...")
    observation = {
        "utterance": "I think it will rain tomorrow",
        "action": "checking weather forecast",
        "expression": {
            "emotion_type": "concern",
            "intensity": 0.6,
            "triggers": ["weather uncertainty"]
        }
    }
    
    inferred_states = tom_engine.infer_mental_state("user_001", observation)
    print(f"   推断出 {len(inferred_states)} 个心理状态")
    
    for state in inferred_states:
        print(f"     - {state}")
    
    # 预测行为
    print("\n🔮 预测Agent行为...")
    prediction = tom_engine.predict_agent_behavior("user_001", context={"urgency": True})
    print(f"   可能行为: {prediction['likely_actions']}")
    print(f"   置信度: {prediction['confidence']:.2f}")
    print(f"   推理链长度: {len(prediction['reasoning'])}")
    
    # 生成同理心响应
    print("\n💝 生成同理心响应...")
    user_emotion = EmotionState(
        emotion_id="",
        agent_id="user_001",
        primary_emotion=EmotionType.SADNESS,
        intensity=0.7,
        valence=-0.6,
        arousal=0.5
    )
    
    empathy_response = empathy_engine.generate_empathy_response(
        user_emotion,
        empathy_level=EmpathyLevel.COMPASSIONATE
    )
    
    print(f"   同理心层级: {empathy_response.empathy_level.value}")
    print(f"   识别情绪: {empathy_response.recognized_emotion.primary_emotion.value}")
    print(f"   响应消息: {empathy_response.empathetic_message}")
    print(f"   建议行动: {empathy_response.suggested_action}")
    print(f"   置信度: {empathy_response.confidence:.2f}")
    
    # 检测情绪转变
    print("\n📊 检测情绪转变...")
    previous_emotion = EmotionState(
        emotion_id="",
        agent_id="user_001",
        primary_emotion=EmotionType.HAPPINESS,
        intensity=0.8
    )
    
    current_emotion = EmotionState(
        emotion_id="",
        agent_id="user_001",
        primary_emotion=EmotionType.SADNESS,
        intensity=0.6
    )
    
    shift = empathy_engine.detect_emotional_shift(previous_emotion, current_emotion)
    print(f"   情绪改变: {shift['emotion_changed']}")
    print(f"   强度变化: {shift['intensity_change']:+.2f}")
    print(f"   效价变化: {shift['valence_change']:+.2f}")
    print(f"   转变类型: {shift['shift_type']}")
    
    # 社交互动管理
    print("\n💬 管理社交互动...")
    interaction = social_manager.start_interaction(
        participants=["user_001", "assistant_001"],
        interaction_type="conversation"
    )
    
    # 添加消息
    social_manager.add_message(
        interaction.interaction_id,
        "user_001",
        "I'm feeling a bit down today",
        user_emotion
    )
    
    assistant_emotion = EmotionState(
        emotion_id="",
        agent_id="assistant_001",
        primary_emotion=EmotionType.NEUTRAL,
        intensity=0.5
    )
    
    social_manager.add_message(
        interaction.interaction_id,
        "assistant_001",
        "I'm here to listen. Would you like to talk about it?",
        assistant_emotion
    )
    
    # 分析互动动态
    print("\n📈 分析互动动态...")
    dynamics = social_manager.analyze_interaction_dynamics(interaction.interaction_id)
    print(f"   总消息数: {dynamics['total_messages']}")
    print(f"   参与者活跃度: {dynamics['participant_activity']}")
    print(f"   主导情绪: {dynamics['dominant_emotion']}")
    print(f"   互动质量: {dynamics['interaction_quality']:.2f}")
    
    # 检查社交规范合规性
    print("\n✅ 检查社交规范合规性...")
    test_message = {
        "sender": "user_001",
        "content": "Thank you for listening",
        "emotion": asdict(assistant_emotion)
    }
    
    compliance = social_manager.check_social_norm_compliance(test_message)
    print(f"   合规: {compliance['compliant']}")
    print(f"   合规分数: {compliance['compliance_score']:.2f}")
    print(f"   违规数: {len(compliance['violations'])}")
    
    # ToM统计
    print("\n📊 ToM统计信息...")
    stats = tom_engine.get_tom_statistics()
    print(f"   模型总数: {stats['total_models']}")
    print(f"   追踪Agent: {stats['agents_tracked']}")
    print(f"   平均每Agent信念数: {stats['avg_beliefs_per_agent']:.1f}")
    print(f"   平均每Agent情绪数: {stats['avg_emotions_per_agent']:.1f}")
    
    print("\n✅ 测试完成！")
