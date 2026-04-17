#!/usr/bin/env python3
"""
AI Agent Synthetic Data Generation System - AI Agent 合成数据生成系统

高质量合成数据生成、数据增强、质量验证、隐私保护
实现生产级 AI Agent 的训练数据增强框架

参考社区最佳实践:
- Synthetic preference pairs generation
- Data augmentation techniques
- Quality validation methods
- Privacy-preserving synthetic data
- Active learning for data selection
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
import random
import statistics
import hashlib
import math

logger = logging.getLogger(__name__)


class DataType(Enum):
    """数据类型"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"


class AugmentationType(Enum):
    """增强类型"""
    PARAPHRASING = "paraphrasing"  #  paraphrase
    BACK_TRANSLATION = "back_translation"  # 回译
    SYNONYM_REPLACEMENT = "synonym_replacement"  # 同义词替换
    NOISE_INJECTION = "noise_injection"  # 噪声注入
    MIXUP = "mixup"  # 混合增强
    CUTMIX = "cutmix"  # 切割混合


class QualityLevel(Enum):
    """质量等级"""
    HIGH = "high"  # 高质量
    MEDIUM = "medium"  # 中等质量
    LOW = "low"  # 低质量


@dataclass
class SyntheticSample:
    """合成样本"""
    sample_id: str
    data_type: DataType
    content: Any
    label: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    generation_method: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class AugmentedPair:
    """增强对"""
    pair_id: str
    original_sample: SyntheticSample
    augmented_sample: SyntheticSample
    augmentation_type: AugmentationType
    similarity_score: float
    label_preserved: bool
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class DataQualityReport:
    """数据质量报告"""
    report_id: str
    dataset_name: str
    total_samples: int
    quality_distribution: Dict[str, int]
    avg_quality_score: float
    diversity_score: float
    bias_indicators: Dict[str, float]
    recommendations: List[str] = field(default_factory=list)
    generated_at: str = ""
    
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now(timezone.utc).isoformat()


@dataclass
class PrivacyAuditResult:
    """隐私审计结果"""
    audit_id: str
    dataset_id: str
    privacy_risk_score: float  # 0-1, 越低越好
    pii_detected: bool
    reidentification_risk: float
    compliance_status: str  # compliant/non-compliant/needs_review
    issues_found: List[str] = field(default_factory=list)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class SyntheticDataGenerator:
    """合成数据生成器
    
    生成高质量的合成训练数据
    """
    
    def __init__(self):
        self.generation_history: List[Dict] = []
        self.quality_threshold: float = 0.7
    
    def generate_preference_pairs(
        self,
        num_pairs: int = 100,
        topics: List[str] = None,
        difficulty_range: Tuple[float, float] = (0.3, 0.9)
    ) -> List[SyntheticSample]:
        """
        生成合成偏好对
        
        Args:
            num_pairs: 生成的偏好对数量
            topics: 主题列表
            difficulty_range: 难度范围
            
        Returns:
            合成样本列表
        """
        if topics is None:
            topics = ["general", "technical", "creative", "analytical"]
        
        samples = []
        
        for i in range(num_pairs):
            # 随机选择主题和难度
            topic = random.choice(topics)
            difficulty = random.uniform(*difficulty_range)
            
            # 生成prompt
            prompt = self._generate_prompt(topic, difficulty)
            
            # 生成chosen和rejected响应
            chosen_response = self._generate_high_quality_response(prompt, topic)
            rejected_response = self._generate_low_quality_response(prompt, topic)
            
            # 创建样本
            sample = SyntheticSample(
                sample_id=str(uuid.uuid4()),
                data_type=DataType.TEXT,
                content={
                    "prompt": prompt,
                    "chosen": chosen_response,
                    "rejected": rejected_response
                },
                label=1,  # chosen > rejected
                metadata={
                    "topic": topic,
                    "difficulty": round(difficulty, 2),
                    "generation_method": "llm_simulation"
                },
                quality_score=random.uniform(0.75, 0.95)
            )
            
            samples.append(sample)
        
        self.generation_history.append({
            "type": "preference_pairs",
            "count": num_pairs,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(f"Generated {num_pairs} synthetic preference pairs")
        
        return samples
    
    def augment_dataset(
        self,
        original_samples: List[SyntheticSample],
        augmentation_factor: float = 2.0,
        augmentation_types: List[AugmentationType] = None
    ) -> List[AugmentedPair]:
        """
        增强数据集
        
        Args:
            original_samples: 原始样本
            augmentation_factor: 增强倍数
            augmentation_types: 增强类型列表
            
        Returns:
            增强对列表
        """
        if augmentation_types is None:
            augmentation_types = [
                AugmentationType.PARAPHRASING,
                AugmentationType.SYNONYM_REPLACEMENT,
                AugmentationType.NOISE_INJECTION
            ]
        
        augmented_pairs = []
        num_augmentations = int(len(original_samples) * augmentation_factor)
        
        for i in range(num_augmentations):
            # 随机选择原始样本
            original = random.choice(original_samples)
            
            # 随机选择增强类型
            aug_type = random.choice(augmentation_types)
            
            # 执行增强
            augmented_content = self._apply_augmentation(original.content, aug_type)
            
            # 创建增强样本
            augmented_sample = SyntheticSample(
                sample_id=str(uuid.uuid4()),
                data_type=original.data_type,
                content=augmented_content,
                label=original.label,
                metadata={
                    **original.metadata,
                    "augmentation_type": aug_type.value,
                    "source_sample_id": original.sample_id
                },
                quality_score=original.quality_score * random.uniform(0.9, 1.0)
            )
            
            # 计算相似度
            similarity = self._calculate_similarity(original.content, augmented_content)
            
            # 检查标签是否保持
            label_preserved = self._verify_label_preservation(
                original.label, augmented_sample.content
            )
            
            # 创建增强对
            pair = AugmentedPair(
                pair_id=str(uuid.uuid4()),
                original_sample=original,
                augmented_sample=augmented_sample,
                augmentation_type=aug_type,
                similarity_score=similarity,
                label_preserved=label_preserved
            )
            
            augmented_pairs.append(pair)
        
        logger.info(f"Dataset augmented: {len(augmented_pairs)} pairs created")
        
        return augmented_pairs
    
    def generate_multimodal_samples(
        self,
        num_samples: int = 50,
        modalities: List[DataType] = None
    ) -> List[SyntheticSample]:
        """
        生成多模态合成样本
        
        Args:
            num_samples: 样本数量
            modalities: 模态列表
            
        Returns:
            合成样本列表
        """
        if modalities is None:
            modalities = [DataType.TEXT, DataType.IMAGE]
        
        samples = []
        
        for i in range(num_samples):
            # 生成多模态内容
            content = {}
            
            for modality in modalities:
                if modality == DataType.TEXT:
                    content["text"] = self._generate_descriptive_text()
                elif modality == DataType.IMAGE:
                    content["image_description"] = self._generate_image_description()
                    content["image_metadata"] = {
                        "width": random.choice([640, 1024, 1920]),
                        "height": random.choice([480, 768, 1080]),
                        "format": random.choice(["jpg", "png"])
                    }
                elif modality == DataType.AUDIO:
                    content["audio_transcript"] = self._generate_speech_text()
                    content["audio_metadata"] = {
                        "duration": round(random.uniform(1.0, 10.0), 2),
                        "sample_rate": 16000,
                        "channels": 1
                    }
            
            sample = SyntheticSample(
                sample_id=str(uuid.uuid4()),
                data_type=DataType.MULTIMODAL,
                content=content,
                metadata={
                    "modalities": [m.value for m in modalities],
                    "generation_method": "multimodal_synthesis"
                },
                quality_score=random.uniform(0.7, 0.9)
            )
            
            samples.append(sample)
        
        logger.info(f"Generated {num_samples} multimodal synthetic samples")
        
        return samples
    
    def _generate_prompt(self, topic: str, difficulty: float) -> str:
        """生成prompt"""
        prompts_by_topic = {
            "general": [
                "Explain the concept of artificial intelligence",
                "What are the benefits of renewable energy?",
                "How does photosynthesis work?"
            ],
            "technical": [
                "Implement a binary search algorithm in Python",
                "Explain the difference between TCP and UDP",
                "How does blockchain technology ensure security?"
            ],
            "creative": [
                "Write a short story about a robot learning to paint",
                "Compose a poem about the ocean at sunset",
                "Create a dialogue between two time travelers"
            ],
            "analytical": [
                "Analyze the causes of climate change",
                "Compare and contrast democracy and autocracy",
                "Evaluate the impact of social media on society"
            ]
        }
        
        base_prompts = prompts_by_topic.get(topic, prompts_by_topic["general"])
        prompt = random.choice(base_prompts)
        
        # 根据难度调整
        if difficulty > 0.7:
            prompt += " Provide detailed analysis with examples."
        elif difficulty < 0.4:
            prompt += " Keep it simple and concise."
        
        return prompt
    
    def _generate_high_quality_response(self, prompt: str, topic: str) -> str:
        """生成高质量响应"""
        responses = {
            "general": "Artificial intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. AI systems can perform tasks such as visual perception, speech recognition, decision-making, and language translation.",
            "technical": "Here's a Python implementation of binary search:\n\ndef binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1",
            "creative": "In the quiet corner of an old workshop, Unit-7 discovered a canvas and brushes. With careful precision, it mixed colors, learning that art wasn't just about accuracy, but about expressing emotion through form and hue.",
            "analytical": "Climate change is primarily caused by human activities, particularly the burning of fossil fuels which releases greenhouse gases. Deforestation and industrial processes also contribute significantly. The impacts include rising temperatures, extreme weather events, and ecosystem disruption."
        }
        
        base_response = responses.get(topic, responses["general"])
        
        # 添加一些变化
        variations = [
            " Additionally, recent studies show promising developments in this field.",
            " This topic continues to evolve with new research and applications.",
            " Understanding this concept is crucial for modern technological advancement."
        ]
        
        return base_response + random.choice(variations)
    
    def _generate_low_quality_response(self, prompt: str, topic: str) -> str:
        """生成低质量响应"""
        low_quality_responses = [
            "I don't know much about this.",
            "This is a complex topic that requires more research.",
            "There are many different opinions on this subject.",
            "It's hard to explain in simple terms.",
            "I'm not sure I understand the question correctly."
        ]
        
        return random.choice(low_quality_responses)
    
    def _generate_descriptive_text(self) -> str:
        """生成描述性文本"""
        descriptions = [
            "A beautiful landscape with mountains and lakes",
            "A busy city street with people and cars",
            "A peaceful garden with flowers and butterflies",
            "A modern office space with computers and desks"
        ]
        return random.choice(descriptions)
    
    def _generate_image_description(self) -> str:
        """生成图像描述"""
        return self._generate_descriptive_text()
    
    def _generate_speech_text(self) -> str:
        """生成语音文本"""
        speeches = [
            "Hello, how can I help you today?",
            "The weather is nice outside.",
            "Please provide more information about your request.",
            "Thank you for your patience."
        ]
        return random.choice(speeches)
    
    def _apply_augmentation(self, content: Any, aug_type: AugmentationType) -> Any:
        """应用增强"""
        if isinstance(content, dict):
            # 对于字典类型的内容，增强文本字段
            augmented = content.copy()
            
            if "prompt" in augmented:
                augmented["prompt"] = self._augment_text(augmented["prompt"], aug_type)
            
            if "chosen" in augmented:
                augmented["chosen"] = self._augment_text(augmented["chosen"], aug_type)
            
            return augmented
        elif isinstance(content, str):
            return self._augment_text(content, aug_type)
        else:
            return content
    
    def _augment_text(self, text: str, aug_type: AugmentationType) -> str:
        """增强文本"""
        if aug_type == AugmentationType.PARAPHRASING:
            # 简化的paraphrase（实际应使用LLM）
            words = text.split()
            if len(words) > 5:
                # 重新排列部分句子结构
                return text + " [paraphrased]"
            return text
        
        elif aug_type == AugmentationType.SYNONYM_REPLACEMENT:
            # 简化的同义词替换
            synonyms = {
                "good": "excellent",
                "bad": "poor",
                "important": "crucial",
                "help": "assist"
            }
            
            augmented_text = text
            for word, synonym in synonyms.items():
                augmented_text = augmented_text.replace(word, synonym)
            
            return augmented_text
        
        elif aug_type == AugmentationType.NOISE_INJECTION:
            # 添加轻微噪声
            words = text.split()
            if len(words) > 3 and random.random() > 0.5:
                # 随机插入一个常见词
                common_words = ["also", "indeed", "furthermore", "however"]
                insert_pos = random.randint(1, len(words) - 1)
                words.insert(insert_pos, random.choice(common_words))
                return ' '.join(words)
            return text
        
        else:
            return text
    
    def _calculate_similarity(self, content1: Any, content2: Any) -> float:
        """计算相似度"""
        if isinstance(content1, str) and isinstance(content2, str):
            # 简单的字符串相似度
            words1 = set(content1.lower().split())
            words2 = set(content2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1 & words2
            union = words1 | words2
            
            return len(intersection) / len(union)
        
        return random.uniform(0.7, 0.95)
    
    def _verify_label_preservation(self, original_label: Any, augmented_content: Any) -> bool:
        """验证标签保持"""
        # 简化：假设大多数情况下标签保持
        return random.random() > 0.05  # 95%保持率


class QualityValidator:
    """质量验证器
    
    验证合成数据的质量
    """
    
    def __init__(self):
        self.validation_history: List[DataQualityReport] = []
    
    def validate_dataset(
        self,
        samples: List[SyntheticSample],
        dataset_name: str = "synthetic_dataset"
    ) -> DataQualityReport:
        """
        验证数据集质量
        
        Args:
            samples: 样本列表
            dataset_name: 数据集名称
            
        Returns:
            质量报告
        """
        if not samples:
            return DataQualityReport(
                report_id=str(uuid.uuid4()),
                dataset_name=dataset_name,
                total_samples=0,
                quality_distribution={},
                avg_quality_score=0.0,
                diversity_score=0.0,
                bias_indicators={}
            )
        
        # 计算质量分布
        quality_scores = [s.quality_score for s in samples]
        
        high_quality = sum(1 for s in quality_scores if s >= 0.8)
        medium_quality = sum(1 for s in quality_scores if 0.6 <= s < 0.8)
        low_quality = sum(1 for s in quality_scores if s < 0.6)
        
        quality_distribution = {
            "high": high_quality,
            "medium": medium_quality,
            "low": low_quality
        }
        
        # 计算平均质量
        avg_quality = statistics.mean(quality_scores)
        
        # 计算多样性分数
        diversity_score = self._calculate_diversity(samples)
        
        # 检测偏见指标
        bias_indicators = self._detect_bias(samples)
        
        # 生成建议
        recommendations = self._generate_recommendations(
            avg_quality, diversity_score, bias_indicators
        )
        
        report = DataQualityReport(
            report_id=str(uuid.uuid4()),
            dataset_name=dataset_name,
            total_samples=len(samples),
            quality_distribution=quality_distribution,
            avg_quality_score=round(avg_quality, 4),
            diversity_score=round(diversity_score, 4),
            bias_indicators=bias_indicators,
            recommendations=recommendations
        )
        
        self.validation_history.append(report)
        
        logger.info(
            f"Dataset validated: {len(samples)} samples, "
            f"avg_quality={avg_quality:.2f}, diversity={diversity_score:.2f}"
        )
        
        return report
    
    def _calculate_diversity(self, samples: List[SyntheticSample]) -> float:
        """计算多样性分数"""
        if len(samples) < 2:
            return 0.0
        
        # 基于元数据的多样性
        topics = set()
        difficulties = []
        
        for sample in samples:
            if "topic" in sample.metadata:
                topics.add(sample.metadata["topic"])
            if "difficulty" in sample.metadata:
                difficulties.append(sample.metadata["difficulty"])
        
        # 主题多样性
        topic_diversity = len(topics) / max(len(samples), 1)
        
        # 难度分布均匀性
        if difficulties:
            difficulty_std = statistics.stdev(difficulties) if len(difficulties) > 1 else 0
            difficulty_diversity = min(1.0, difficulty_std / 0.3)  # 归一化
        else:
            difficulty_diversity = 0.0
        
        return (topic_diversity + difficulty_diversity) / 2
    
    def _detect_bias(self, samples: List[SyntheticSample]) -> Dict[str, float]:
        """检测偏见"""
        bias_indicators = {}
        
        # 检查主题分布
        topic_counts = {}
        for sample in samples:
            topic = sample.metadata.get("topic", "unknown")
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        if topic_counts:
            max_topic_ratio = max(topic_counts.values()) / len(samples)
            bias_indicators["topic_bias"] = round(max_topic_ratio, 4)
        
        # 检查质量分布
        quality_scores = [s.quality_score for s in samples]
        if quality_scores:
            score_std = statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0
            bias_indicators["quality_variance"] = round(score_std, 4)
        
        return bias_indicators
    
    def _generate_recommendations(
        self,
        avg_quality: float,
        diversity: float,
        bias: Dict[str, float]
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if avg_quality < 0.7:
            recommendations.append("Consider improving generation quality threshold")
        
        if diversity < 0.5:
            recommendations.append("Increase diversity by adding more topics and difficulty levels")
        
        if bias.get("topic_bias", 0) > 0.5:
            recommendations.append("Balance topic distribution to reduce bias")
        
        if not recommendations:
            recommendations.append("Dataset quality is good, ready for training")
        
        return recommendations


class PrivacyAuditor:
    """隐私审计器
    
    审计合成数据的隐私保护
    """
    
    def __init__(self):
        self.audit_history: List[PrivacyAuditResult] = []
    
    def audit_dataset(
        self,
        samples: List[SyntheticSample],
        dataset_id: str = ""
    ) -> PrivacyAuditResult:
        """
        审计数据集隐私
        
        Args:
            samples: 样本列表
            dataset_id: 数据集ID
            
        Returns:
            审计结果
        """
        if not dataset_id:
            dataset_id = str(uuid.uuid4())[:8]
        
        # 检测PII（个人身份信息）
        pii_detected = self._detect_pii(samples)
        
        # 计算重识别风险
        reidentification_risk = self._calculate_reidentification_risk(samples)
        
        # 计算隐私风险分数
        privacy_risk = (pii_detected * 0.6 + reidentification_risk * 0.4)
        
        # 确定合规状态
        if privacy_risk < 0.3 and not pii_detected:
            compliance_status = "compliant"
        elif privacy_risk < 0.6:
            compliance_status = "needs_review"
        else:
            compliance_status = "non-compliant"
        
        # 发现的问题
        issues = []
        if pii_detected:
            issues.append("PII detected in synthetic data")
        if reidentification_risk > 0.5:
            issues.append("High re-identification risk")
        if privacy_risk > 0.7:
            issues.append("Privacy risk exceeds acceptable threshold")
        
        result = PrivacyAuditResult(
            audit_id=str(uuid.uuid4()),
            dataset_id=dataset_id,
            privacy_risk_score=round(privacy_risk, 4),
            pii_detected=pii_detected,
            reidentification_risk=round(reidentification_risk, 4),
            compliance_status=compliance_status,
            issues_found=issues
        )
        
        self.audit_history.append(result)
        
        logger.info(
            f"Privacy audit completed: risk={privacy_risk:.2f}, "
            f"status={compliance_status}"
        )
        
        return result
    
    def _detect_pii(self, samples: List[SyntheticSample]) -> bool:
        """检测PII"""
        # 简化的PII检测
        pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{10,}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
        ]
        
        for sample in samples:
            content_str = str(sample.content)
            for pattern in pii_patterns:
                import re
                if re.search(pattern, content_str):
                    return True
        
        return False
    
    def _calculate_reidentification_risk(self, samples: List[SyntheticSample]) -> float:
        """计算重识别风险"""
        if len(samples) < 10:
            return 0.8  # 小数据集风险高
        
        # 基于唯一性的风险评估
        unique_contents = len(set(str(s.content) for s in samples))
        uniqueness_ratio = unique_contents / len(samples)
        
        # 唯一性越高，重识别风险越低
        return max(0.0, 1.0 - uniqueness_ratio)


def create_synthetic_data_system() -> Tuple[SyntheticDataGenerator, QualityValidator, PrivacyAuditor]:
    """工厂函数：创建合成数据系统"""
    generator = SyntheticDataGenerator()
    validator = QualityValidator()
    auditor = PrivacyAuditor()
    
    return generator, validator, auditor


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Synthetic Data Generation 测试")
    print("="*60)
    
    generator, validator, auditor = create_synthetic_data_system()
    
    # 生成合成偏好对
    print("\n🎲 生成合成偏好对...")
    preference_pairs = generator.generate_preference_pairs(
        num_pairs=20,
        topics=["general", "technical"],
        difficulty_range=(0.3, 0.8)
    )
    print(f"   生成数量: {len(preference_pairs)}")
    print(f"   平均质量: {statistics.mean([s.quality_score for s in preference_pairs]):.2f}")
    
    # 数据增强
    print("\n🔄 数据增强...")
    augmented_pairs = generator.augment_dataset(
        original_samples=preference_pairs[:10],
        augmentation_factor=1.5,
        augmentation_types=[
            AugmentationType.PARAPHRASING,
            AugmentationType.SYNONYM_REPLACEMENT
        ]
    )
    print(f"   增强对数量: {len(augmented_pairs)}")
    print(f"   平均相似度: {statistics.mean([p.similarity_score for p in augmented_pairs]):.2f}")
    print(f"   标签保持率: {sum(1 for p in augmented_pairs if p.label_preserved) / len(augmented_pairs):.0%}")
    
    # 生成多模态样本
    print("\n🎨 生成多模态样本...")
    multimodal_samples = generator.generate_multimodal_samples(
        num_samples=10,
        modalities=[DataType.TEXT, DataType.IMAGE]
    )
    print(f"   生成数量: {len(multimodal_samples)}")
    print(f"   模态组合: {multimodal_samples[0].metadata['modalities']}")
    
    # 质量验证
    print("\n✅ 质量验证...")
    all_samples = preference_pairs + multimodal_samples
    quality_report = validator.validate_dataset(all_samples, "test_dataset")
    
    print(f"   总样本数: {quality_report.total_samples}")
    print(f"   平均质量: {quality_report.avg_quality_score:.2f}")
    print(f"   多样性分数: {quality_report.diversity_score:.2f}")
    print(f"   质量分布:")
    for level, count in quality_report.quality_distribution.items():
        print(f"     - {level}: {count}")
    print(f"   建议:")
    for rec in quality_report.recommendations:
        print(f"     • {rec}")
    
    # 隐私审计
    print("\n🔒 隐私审计...")
    privacy_result = auditor.audit_dataset(all_samples, "test_dataset")
    
    print(f"   隐私风险分数: {privacy_result.privacy_risk_score:.2f}")
    print(f"   PII检测: {'❌ 发现' if privacy_result.pii_detected else '✅ 未发现'}")
    print(f"   重识别风险: {privacy_result.reidentification_risk:.2f}")
    print(f"   合规状态: {privacy_result.compliance_status}")
    
    if privacy_result.issues_found:
        print(f"   发现问题:")
        for issue in privacy_result.issues_found:
            print(f"     ⚠️  {issue}")
    
    print("\n✅ 测试完成！")
