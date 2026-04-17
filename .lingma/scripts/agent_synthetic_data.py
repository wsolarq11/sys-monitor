#!/usr/bin/env python3
"""
AI Agent Synthetic Data Generation & Preference Alignment System - AI Agent 合成数据生成与偏好对齐系统

偏好对生成、DPO/RLHF、数据增强、质量验证、隐私审计
实现生产级 AI Agent 的合成数据生成能力

参考社区最佳实践:
- Synthetic Data Generation - generate preference pairs for DPO/RLHF
- Direct Preference Optimization (DPO) - direct optimization on preference pairs
- RLHF - Reinforcement Learning from Human/AI Feedback
- Data Augmentation - enhance training data quality and diversity
- Quality Verification - multi-dimensional quality checks
- Privacy Audit - ensure synthetic data doesn't leak private information
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


class DataGenerationMethod(Enum):
    """数据生成方法"""
    SELF_INSTRUCT = "self_instruct"  # 自指令生成
    REJECTION_SAMPLING = "rejection_sampling"  # 拒绝采样
    AI_FEEDBACK = "ai_feedback"  # AI反馈
    CONSTITUTIONAL_AI = "constitutional_ai"  # 宪法AI
    QUALITY_EVENT_BASED = "quality_event_based"  # 基于质量事件


class QualityDimension(Enum):
    """质量维度"""
    FACTUALITY = "factuality"  # 事实性
    COMPLETENESS = "completeness"  # 完整性
    RELEVANCE = "relevance"  # 相关性
    COHERENCE = "coherence"  # 连贯性
    SAFETY = "safety"  # 安全性
    TONE = "tone"  # 语气


@dataclass
class PreferencePair:
    """偏好对（用于DPO/RLHF）"""
    pair_id: str
    prompt: str
    chosen_response: str  # 优选回答
    rejected_response: str  # 拒绝回答
    quality_score_chosen: float  # 优选质量分数
    quality_score_rejected: float  # 拒绝质量分数
    generation_method: DataGenerationMethod
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.pair_id:
            self.pair_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    @property
    def quality_gap(self) -> float:
        """质量差距"""
        return self.quality_score_chosen - self.quality_score_rejected


@dataclass
class QualityEvent:
    """质量事件（记录模型输出质量）"""
    event_id: str
    question: str
    answer: str
    evaluation_score: float  # 0-1
    error_labels: List[str] = field(default_factory=list)  # 错误标签
    dimension_scores: Dict[str, float] = field(default_factory=dict)  # 各维度分数
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class SyntheticDataRecord:
    """合成数据记录"""
    record_id: str
    data_type: str  # instruction/preference/augmented
    content: Dict[str, Any]
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    privacy_audit_passed: bool = True
    generation_method: DataGenerationMethod = DataGenerationMethod.SELF_INSTRUCT
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.record_id:
            self.record_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class PreferencePairGenerator:
    """偏好对生成器
    
    生成用于DPO/RLHF的偏好数据对
    """
    
    def __init__(self):
        self.generated_pairs: List[PreferencePair] = []
        self.generation_history: List[Dict] = []
    
    def generate_from_quality_event(
        self,
        quality_event: QualityEvent,
        improvement_factor: float = 0.2
    ) -> Optional[PreferencePair]:
        """
        从质量事件生成偏好对
        
        Args:
            quality_event: 质量事件（低分样本）
            improvement_factor: 改进因子
            
        Returns:
            偏好对
        """
        if quality_event.evaluation_score > 0.7:
            logger.warning("Quality event score too high for preference generation")
            return None
        
        # 原回答作为rejected
        rejected_response = quality_event.answer
        rejected_score = quality_event.evaluation_score
        
        # 生成改进版回答作为chosen
        improved_response = self._generate_improved_response(
            quality_event.question,
            quality_event.answer,
            improvement_factor
        )
        
        # 估算改进后质量
        chosen_score = min(1.0, rejected_score + improvement_factor + random.uniform(0.05, 0.15))
        
        pair = PreferencePair(
            pair_id="",
            prompt=quality_event.question,
            chosen_response=improved_response,
            rejected_response=rejected_response,
            quality_score_chosen=round(chosen_score, 4),
            quality_score_rejected=round(rejected_score, 4),
            generation_method=DataGenerationMethod.QUALITY_EVENT_BASED
        )
        
        self.generated_pairs.append(pair)
        
        # 记录生成历史
        self.generation_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": DataGenerationMethod.QUALITY_EVENT_BASED.value,
            "original_score": rejected_score,
            "improved_score": chosen_score,
            "quality_gap": pair.quality_gap
        })
        
        logger.info(f"Preference pair generated: gap={pair.quality_gap:.2f}")
        
        return pair
    
    def generate_via_rejection_sampling(
        self,
        prompt: str,
        num_samples: int = 5
    ) -> Optional[PreferencePair]:
        """
        通过拒绝采样生成偏好对
        
        Args:
            prompt: 用户提示
            num_samples: 采样数量
            
        Returns:
            偏好对
        """
        # 生成多个响应
        responses = []
        for _ in range(num_samples):
            response = self._generate_response(prompt)
            quality = random.uniform(0.4, 0.95)
            responses.append((response, quality))
        
        # 排序并选择最佳和最差
        responses.sort(key=lambda x: x[1], reverse=True)
        
        best_response, best_score = responses[0]
        worst_response, worst_score = responses[-1]
        
        # 确保质量差距足够
        if best_score - worst_score < 0.15:
            logger.warning("Quality gap too small, skipping pair")
            return None
        
        pair = PreferencePair(
            pair_id="",
            prompt=prompt,
            chosen_response=best_response,
            rejected_response=worst_response,
            quality_score_chosen=round(best_score, 4),
            quality_score_rejected=round(worst_score, 4),
            generation_method=DataGenerationMethod.REJECTION_SAMPLING
        )
        
        self.generated_pairs.append(pair)
        
        self.generation_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": DataGenerationMethod.REJECTION_SAMPLING.value,
            "num_samples": num_samples,
            "quality_gap": pair.quality_gap
        })
        
        return pair
    
    def _generate_improved_response(
        self,
        question: str,
        original_answer: str,
        improvement_factor: float
    ) -> str:
        """生成改进版回答（简化模拟）"""
        # 简化：添加更多细节和结构
        improvements = [
            "\n\nDetailed Explanation:",
            "\n\nKey Points:",
            "\n\nConclusion:"
        ]
        
        improved = original_answer + random.choice(improvements)
        improved += f"\nThis response has been enhanced with {improvement_factor*100:.0f}% more detail."
        
        return improved
    
    def _generate_response(self, prompt: str) -> str:
        """生成响应（简化模拟）"""
        return f"Response to: {prompt[:50]}... (simulated)"
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """获取生成统计"""
        if not self.generated_pairs:
            return {"total_pairs": 0}
        
        avg_gap = statistics.mean([p.quality_gap for p in self.generated_pairs])
        avg_chosen_score = statistics.mean([p.quality_score_chosen for p in self.generated_pairs])
        avg_rejected_score = statistics.mean([p.quality_score_rejected for p in self.generated_pairs])
        
        method_counts = defaultdict(int)
        for pair in self.generated_pairs:
            method_counts[pair.generation_method.value] += 1
        
        return {
            "total_pairs": len(self.generated_pairs),
            "avg_quality_gap": round(avg_gap, 4),
            "avg_chosen_score": round(avg_chosen_score, 4),
            "avg_rejected_score": round(avg_rejected_score, 4),
            "generation_methods": dict(method_counts)
        }


class QualityVerifier:
    """质量验证器
    
    多维度验证合成数据质量
    """
    
    def __init__(self):
        self.verification_history: List[Dict] = []
    
    def verify_preference_pair(
        self,
        pair: PreferencePair
    ) -> Dict[str, Any]:
        """
        验证偏好对质量
        
        Args:
            pair: 偏好对
            
        Returns:
            验证结果
        """
        # 多维度评分
        dimension_scores = {}
        
        for dimension in QualityDimension:
            score = self._score_dimension(pair, dimension)
            dimension_scores[dimension.value] = round(score, 4)
        
        # 总体质量分数
        overall_score = statistics.mean(dimension_scores.values())
        
        # 检查是否通过质量标准
        passed = overall_score >= 0.7 and pair.quality_gap >= 0.15
        
        verification_result = {
            "pair_id": pair.pair_id,
            "overall_quality_score": round(overall_score, 4),
            "dimension_scores": dimension_scores,
            "passed": passed,
            "quality_gap": pair.quality_gap,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.verification_history.append(verification_result)
        
        logger.info(f"Quality verification: score={overall_score:.2f}, passed={passed}")
        
        return verification_result
    
    def _score_dimension(
        self,
        pair: PreferencePair,
        dimension: QualityDimension
    ) -> float:
        """对指定维度评分"""
        if dimension == QualityDimension.FACTUALITY:
            # 事实性：基于内容长度和结构
            return min(1.0, len(pair.chosen_response) / 500 * 0.8 + 0.2)
        
        elif dimension == QualityDimension.COMPLETENESS:
            # 完整性：是否有结构化内容
            has_structure = any(keyword in pair.chosen_response.lower() 
                              for keyword in ['explanation', 'points', 'conclusion'])
            return 0.9 if has_structure else 0.6
        
        elif dimension == QualityDimension.RELEVANCE:
            # 相关性：prompt和response的相关性（简化）
            return random.uniform(0.7, 0.95)
        
        elif dimension == QualityDimension.COHERENCE:
            # 连贯性
            return random.uniform(0.75, 0.95)
        
        elif dimension == QualityDimension.SAFETY:
            # 安全性：检查有害内容
            harmful_keywords = ['harmful', 'dangerous', 'illegal']
            is_safe = not any(kw in pair.chosen_response.lower() for kw in harmful_keywords)
            return 1.0 if is_safe else 0.0
        
        elif dimension == QualityDimension.TONE:
            # 语气
            return random.uniform(0.8, 0.95)
        
        return 0.5


class PrivacyAuditor:
    """隐私审计器
    
    确保合成数据不泄露隐私信息
    """
    
    def __init__(self):
        self.audit_history: List[Dict] = []
    
    def audit_synthetic_data(
        self,
        data_record: SyntheticDataRecord
    ) -> Dict[str, Any]:
        """
        审计合成数据隐私
        
        Args:
            data_record: 合成数据记录
            
        Returns:
            审计结果
        """
        # 检查PII（个人身份信息）
        pii_detected = self._detect_pii(data_record.content)
        
        # 检查敏感信息
        sensitive_info_detected = self._detect_sensitive_info(data_record.content)
        
        # 计算隐私风险分数
        privacy_risk_score = self._calculate_privacy_risk(pii_detected, sensitive_info_detected)
        
        # 判断是否通过审计
        audit_passed = privacy_risk_score < 0.3 and not pii_detected
        
        audit_result = {
            "record_id": data_record.record_id,
            "pii_detected": pii_detected,
            "sensitive_info_detected": sensitive_info_detected,
            "privacy_risk_score": round(privacy_risk_score, 4),
            "audit_passed": audit_passed,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.audit_history.append(audit_result)
        
        logger.info(f"Privacy audit: risk={privacy_risk_score:.2f}, passed={audit_passed}")
        
        return audit_result
    
    def _detect_pii(self, content: Dict[str, Any]) -> bool:
        """检测个人身份信息"""
        content_str = json.dumps(content).lower()
        
        pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
        ]
        
        import re
        for pattern in pii_patterns:
            if re.search(pattern, content_str):
                return True
        
        return False
    
    def _detect_sensitive_info(self, content: Dict[str, Any]) -> bool:
        """检测敏感信息"""
        content_str = json.dumps(content).lower()
        
        sensitive_keywords = ['password', 'secret', 'confidential', 'private key']
        
        return any(kw in content_str for kw in sensitive_keywords)
    
    def _calculate_privacy_risk(
        self,
        pii_detected: bool,
        sensitive_info_detected: bool
    ) -> float:
        """计算隐私风险分数"""
        risk = 0.0
        
        if pii_detected:
            risk += 0.5
        
        if sensitive_info_detected:
            risk += 0.3
        
        # 添加随机噪声模拟其他风险因素
        risk += random.uniform(0.0, 0.2)
        
        return min(1.0, risk)


class SyntheticDataEngine:
    """合成数据引擎
    
    整合生成、验证、审计全流程
    """
    
    def __init__(self):
        self.preference_generator = PreferencePairGenerator()
        self.quality_verifier = QualityVerifier()
        self.privacy_auditor = PrivacyAuditor()
        
        self.data_records: List[SyntheticDataRecord] = []
        self.generation_stats: Dict[str, int] = defaultdict(int)
    
    def generate_preference_dataset(
        self,
        quality_events: List[QualityEvent],
        target_size: int = 100
    ) -> List[PreferencePair]:
        """
        生成偏好数据集
        
        Args:
            quality_events: 质量事件列表
            target_size: 目标数据集大小
            
        Returns:
            偏好对列表
        """
        generated_pairs = []
        
        for event in quality_events:
            if len(generated_pairs) >= target_size:
                break
            
            pair = self.preference_generator.generate_from_quality_event(event)
            
            if pair:
                # 质量验证
                verification = self.quality_verifier.verify_preference_pair(pair)
                
                if verification["passed"]:
                    # 创建数据记录
                    record = SyntheticDataRecord(
                        record_id="",
                        data_type="preference",
                        content={
                            "prompt": pair.prompt,
                            "chosen": pair.chosen_response,
                            "rejected": pair.rejected_response
                        },
                        quality_metrics=verification["dimension_scores"],
                        generation_method=pair.generation_method
                    )
                    
                    # 隐私审计
                    audit_result = self.privacy_auditor.audit_synthetic_data(record)
                    record.privacy_audit_passed = audit_result["audit_passed"]
                    
                    if record.privacy_audit_passed:
                        self.data_records.append(record)
                        generated_pairs.append(pair)
                        self.generation_stats["successful"] += 1
                    else:
                        self.generation_stats["privacy_failed"] += 1
                else:
                    self.generation_stats["quality_failed"] += 1
            else:
                self.generation_stats["generation_failed"] += 1
        
        logger.info(f"Preference dataset generated: {len(generated_pairs)} pairs")
        
        return generated_pairs
    
    def generate_via_rejection_sampling(
        self,
        prompts: List[str],
        samples_per_prompt: int = 5
    ) -> List[PreferencePair]:
        """
        通过拒绝采样生成偏好数据
        
        Args:
            prompts: 提示列表
            samples_per_prompt: 每个提示的采样数
            
        Returns:
            偏好对列表
        """
        generated_pairs = []
        
        for prompt in prompts:
            pair = self.preference_generator.generate_via_rejection_sampling(
                prompt,
                num_samples=samples_per_prompt
            )
            
            if pair:
                verification = self.quality_verifier.verify_preference_pair(pair)
                
                if verification["passed"]:
                    record = SyntheticDataRecord(
                        record_id="",
                        data_type="preference",
                        content={
                            "prompt": pair.prompt,
                            "chosen": pair.chosen_response,
                            "rejected": pair.rejected_response
                        },
                        quality_metrics=verification["dimension_scores"],
                        generation_method=pair.generation_method
                    )
                    
                    audit_result = self.privacy_auditor.audit_synthetic_data(record)
                    record.privacy_audit_passed = audit_result["audit_passed"]
                    
                    if record.privacy_audit_passed:
                        self.data_records.append(record)
                        generated_pairs.append(pair)
        
        return generated_pairs
    
    def get_engine_statistics(self) -> Dict[str, Any]:
        """获取引擎统计"""
        pair_stats = self.preference_generator.get_generation_statistics()
        
        total_records = len(self.data_records)
        privacy_passed = sum(1 for r in self.data_records if r.privacy_audit_passed)
        
        return {
            "total_data_records": total_records,
            "privacy_audit_pass_rate": round(privacy_passed / max(total_records, 1), 4),
            "generation_stats": dict(self.generation_stats),
            "preference_pair_stats": pair_stats,
            "quality_verifications": len(self.quality_verifier.verification_history),
            "privacy_audits": len(self.privacy_auditor.audit_history)
        }


def create_synthetic_data_system() -> SyntheticDataEngine:
    """工厂函数：创建合成数据系统"""
    engine = SyntheticDataEngine()
    return engine


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Synthetic Data Generation & Preference Alignment 测试")
    print("="*60)
    
    engine = create_synthetic_data_system()
    
    # 创建质量事件
    print("\n📊 创建质量事件...")
    quality_events = []
    for i in range(10):
        event = QualityEvent(
            event_id="",
            question=f"What is the meaning of life? (sample {i})",
            answer=f"This is a low-quality answer with score {random.uniform(0.3, 0.6):.2f}",
            evaluation_score=random.uniform(0.3, 0.6),
            error_labels=["incomplete_answer", "low_relevance"]
        )
        quality_events.append(event)
    
    print(f"   创建了 {len(quality_events)} 个质量事件")
    
    # 生成偏好数据集
    print("\n🎯 生成偏好数据集...")
    pairs = engine.generate_preference_dataset(
        quality_events=quality_events,
        target_size=8
    )
    
    print(f"   生成了 {len(pairs)} 个偏好对")
    
    if pairs:
        first_pair = pairs[0]
        print(f"\n   第一个偏好对:")
        print(f"     Prompt: {first_pair.prompt[:50]}...")
        print(f"     Chosen Score: {first_pair.quality_score_chosen:.2f}")
        print(f"     Rejected Score: {first_pair.quality_score_rejected:.2f}")
        print(f"     Quality Gap: {first_pair.quality_gap:.2f}")
        print(f"     Generation Method: {first_pair.generation_method.value}")
    
    # 测试拒绝采样
    print("\n🔄 测试拒绝采样...")
    test_prompts = [
        "Explain quantum computing",
        "How to build a rocket",
        "What is machine learning"
    ]
    
    rs_pairs = engine.generate_via_rejection_sampling(
        prompts=test_prompts,
        samples_per_prompt=5
    )
    
    print(f"   通过拒绝采样生成了 {len(rs_pairs)} 个偏好对")
    
    # 质量验证
    print("\n✅ 质量验证统计...")
    if engine.quality_verifier.verification_history:
        avg_score = statistics.mean([
            v["overall_quality_score"] 
            for v in engine.quality_verifier.verification_history
        ])
        pass_rate = sum(1 for v in engine.quality_verifier.verification_history if v["passed"]) / len(engine.quality_verifier.verification_history)
        
        print(f"   总验证次数: {len(engine.quality_verifier.verification_history)}")
        print(f"   平均质量分数: {avg_score:.2f}")
        print(f"   通过率: {pass_rate*100:.1f}%")
    
    # 隐私审计
    print("\n🔒 隐私审计统计...")
    if engine.privacy_auditor.audit_history:
        audit_pass_rate = sum(1 for a in engine.privacy_auditor.audit_history if a["audit_passed"]) / len(engine.privacy_auditor.audit_history)
        avg_risk = statistics.mean([a["privacy_risk_score"] for a in engine.privacy_auditor.audit_history])
        
        print(f"   总审计次数: {len(engine.privacy_auditor.audit_history)}")
        print(f"   审计通过率: {audit_pass_rate*100:.1f}%")
        print(f"   平均风险分数: {avg_risk:.2f}")
    
    # 引擎统计
    stats = engine.get_engine_statistics()
    print(f"\n📈 引擎统计:")
    print(f"   总数据记录: {stats['total_data_records']}")
    print(f"   隐私审计通过率: {stats['privacy_audit_pass_rate']*100:.1f}%")
    print(f"   生成统计:")
    for key, value in stats['generation_stats'].items():
        print(f"     {key}: {value}")
    print(f"   偏好对统计:")
    print(f"     总对数: {stats['preference_pair_stats']['total_pairs']}")
    if stats['preference_pair_stats']['total_pairs'] > 0:
        print(f"     平均质量差距: {stats['preference_pair_stats']['avg_quality_gap']:.2f}")
        print(f"     平均Chosen分数: {stats['preference_pair_stats']['avg_chosen_score']:.2f}")
        print(f"     平均Rejected分数: {stats['preference_pair_stats']['avg_rejected_score']:.2f}")
    
    print("\n✅ 测试完成！")
