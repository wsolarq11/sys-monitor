#!/usr/bin/env python3
"""
Pattern Recognition & Adaptive Thresholds - 模式识别与自适应阈值

从历史数据中学习模式，动态调整检测阈值
支持异常检测、趋势分析、行为建模

参考社区最佳实践:
- Adaptive thresholds based on historical patterns
- Anomaly detection using statistical models
- Time-series pattern recognition
- Dynamic threshold adjustment algorithms
"""

import json
import math
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from collections import deque, defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """模式类型"""
    TREND = "trend"  # 趋势模式
    CYCLICAL = "cyclical"  # 周期性模式
    SEASONAL = "seasonal"  # 季节性模式
    ANOMALY = "anomaly"  # 异常模式
    BEHAVIOR = "behavior"  # 行为模式


class AnomalyLevel(Enum):
    """异常级别"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class DataPoint:
    """数据点"""
    timestamp: str
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_value(cls, value: float, metadata: Dict = None) -> 'DataPoint':
        """从值创建数据点"""
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            value=value,
            metadata=metadata or {}
        )


@dataclass
class DetectedPattern:
    """检测到的模式"""
    pattern_id: str
    pattern_type: PatternType
    confidence: float  # 置信度 (0-1)
    description: str
    start_time: str
    end_time: Optional[str] = None
    data_points: List[DataPoint] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class AnomalyEvent:
    """异常事件"""
    event_id: str
    anomaly_level: AnomalyLevel
    deviation_score: float  # 偏离分数
    description: str
    detected_at: str
    expected_value: float
    actual_value: float
    threshold_used: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdaptiveThreshold:
    """自适应阈值"""
    metric_name: str
    current_threshold: float
    base_threshold: float
    adjustment_factor: float  # 调整因子
    window_size: int  # 滑动窗口大小
    min_threshold: float
    max_threshold: float
    last_updated: str = ""
    update_count: int = 0
    history: List[float] = field(default_factory=list)  # 阈值历史
    
    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now(timezone.utc).isoformat()


class StatisticalAnalyzer:
    """统计分析器
    
    提供基础统计计算功能
    """
    
    @staticmethod
    def mean(values: List[float]) -> float:
        """计算均值"""
        if not values:
            return 0.0
        return sum(values) / len(values)
    
    @staticmethod
    def std_dev(values: List[float]) -> float:
        """计算标准差"""
        if len(values) < 2:
            return 0.0
        mean = StatisticalAnalyzer.mean(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)
    
    @staticmethod
    def percentile(values: List[float], p: float) -> float:
        """计算百分位数"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * p / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    @staticmethod
    def z_score(value: float, mean: float, std_dev: float) -> float:
        """计算 Z-Score"""
        if std_dev == 0:
            return 0.0
        return (value - mean) / std_dev
    
    @staticmethod
    def moving_average(values: List[float], window: int) -> List[float]:
        """计算移动平均"""
        if len(values) < window:
            return values
        
        result = []
        for i in range(len(values) - window + 1):
            window_values = values[i:i + window]
            result.append(sum(window_values) / window)
        
        return result


class PatternRecognizer:
    """模式识别器
    
    从历史数据中识别各种模式
    """
    
    def __init__(self, window_size: int = 50):
        """
        Args:
            window_size: 分析窗口大小
        """
        self.window_size = window_size
        self.history: deque = deque(maxlen=window_size)
        self.detected_patterns: List[DetectedPattern] = []
    
    def add_data_point(self, data_point: DataPoint):
        """添加数据点"""
        self.history.append(data_point)
    
    def recognize_patterns(self) -> List[DetectedPattern]:
        """
        识别模式
        
        Returns:
            检测到的模式列表
        """
        if len(self.history) < 10:
            return []
        
        patterns = []
        
        # 检测趋势模式
        trend_pattern = self._detect_trend()
        if trend_pattern:
            patterns.append(trend_pattern)
        
        # 检测周期性模式
        cyclical_pattern = self._detect_cyclical()
        if cyclical_pattern:
            patterns.append(cyclical_pattern)
        
        # 检测异常模式
        anomaly_pattern = self._detect_anomalies()
        if anomaly_pattern:
            patterns.append(anomaly_pattern)
        
        self.detected_patterns.extend(patterns)
        return patterns
    
    def _detect_trend(self) -> Optional[DetectedPattern]:
        """检测趋势模式"""
        values = [dp.value for dp in self.history]
        
        if len(values) < 10:
            return None
        
        # 简单的线性回归
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return None
        
        slope = numerator / denominator
        
        # 判断趋势方向
        if abs(slope) > 0.01:  # 斜率阈值
            direction = "increasing" if slope > 0 else "decreasing"
            confidence = min(1.0, abs(slope) * 10)  # 归一化置信度
            
            import uuid
            return DetectedPattern(
                pattern_id=str(uuid.uuid4()),
                pattern_type=PatternType.TREND,
                confidence=confidence,
                description=f"Detected {direction} trend (slope={slope:.4f})",
                start_time=self.history[0].timestamp,
                end_time=self.history[-1].timestamp,
                data_points=list(self.history),
                parameters={"slope": slope, "direction": direction}
            )
        
        return None
    
    def _detect_cyclical(self) -> Optional[DetectedPattern]:
        """检测周期性模式"""
        values = [dp.value for dp in self.history]
        
        if len(values) < 20:
            return None
        
        # 简单的自相关检测
        mean = StatisticalAnalyzer.mean(values)
        centered = [v - mean for v in values]
        
        # 计算不同滞后期的自相关
        correlations = []
        for lag in range(1, len(values) // 2):
            if lag >= len(centered):
                break
            
            correlation = sum(centered[i] * centered[i + lag] for i in range(len(centered) - lag))
            correlations.append((lag, correlation))
        
        # 找到最大自相关的滞后期
        if correlations:
            max_lag, max_corr = max(correlations, key=lambda x: x[1])
            
            if max_corr > 0 and max_lag > 2:
                import uuid
                return DetectedPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=PatternType.CYCLICAL,
                    confidence=min(1.0, max_corr / 100),
                    description=f"Detected cyclical pattern (period={max_lag})",
                    start_time=self.history[0].timestamp,
                    end_time=self.history[-1].timestamp,
                    data_points=list(self.history),
                    parameters={"period": max_lag, "correlation": max_corr}
                )
        
        return None
    
    def _detect_anomalies(self) -> Optional[DetectedPattern]:
        """检测异常模式"""
        values = [dp.value for dp in self.history]
        
        if len(values) < 10:
            return None
        
        mean = StatisticalAnalyzer.mean(values)
        std = StatisticalAnalyzer.std_dev(values)
        
        if std == 0:
            return None
        
        # 检测超出 2 标准差的点
        anomalies = []
        for dp in self.history:
            z_score = StatisticalAnalyzer.z_score(dp.value, mean, std)
            if abs(z_score) > 2:
                anomalies.append((dp, z_score))
        
        if anomalies:
            import uuid
            return DetectedPattern(
                pattern_id=str(uuid.uuid4()),
                pattern_type=PatternType.ANOMALY,
                confidence=len(anomalies) / len(values),
                description=f"Detected {len(anomalies)} anomalies",
                start_time=self.history[0].timestamp,
                end_time=self.history[-1].timestamp,
                data_points=[dp for dp, _ in anomalies],
                parameters={"anomaly_count": len(anomalies), "mean": mean, "std": std}
            )
        
        return None


class AdaptiveThresholdManager:
    """自适应阈值管理器
    
    根据历史数据动态调整检测阈值
    """
    
    def __init__(self):
        self.thresholds: Dict[str, AdaptiveThreshold] = {}
        self.data_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
    
    def create_threshold(
        self,
        metric_name: str,
        base_threshold: float,
        window_size: int = 50,
        min_threshold: Optional[float] = None,
        max_threshold: Optional[float] = None
    ) -> AdaptiveThreshold:
        """
        创建自适应阈值
        
        Args:
            metric_name: 指标名称
            base_threshold: 基础阈值
            window_size: 滑动窗口大小
            min_threshold: 最小阈值
            max_threshold: 最大阈值
            
        Returns:
            自适应阈值对象
        """
        threshold = AdaptiveThreshold(
            metric_name=metric_name,
            current_threshold=base_threshold,
            base_threshold=base_threshold,
            adjustment_factor=1.0,
            window_size=window_size,
            min_threshold=min_threshold or base_threshold * 0.5,
            max_threshold=max_threshold or base_threshold * 2.0
        )
        
        self.thresholds[metric_name] = threshold
        logger.info(f"Created adaptive threshold for {metric_name}: {base_threshold}")
        
        return threshold
    
    def update_threshold(self, metric_name: str, new_value: float) -> float:
        """
        更新阈值
        
        Args:
            metric_name: 指标名称
            new_value: 新观测值
            
        Returns:
            更新后的阈值
        """
        threshold = self.thresholds.get(metric_name)
        if not threshold:
            raise ValueError(f"Threshold not found: {metric_name}")
        
        # 记录历史数据
        self.data_history[metric_name].append(new_value)
        
        # 如果数据不足，不调整
        if len(self.data_history[metric_name]) < threshold.window_size:
            return threshold.current_threshold
        
        # 计算统计数据
        values = list(self.data_history[metric_name])
        mean = StatisticalAnalyzer.mean(values)
        std = StatisticalAnalyzer.std_dev(values)
        
        # 基于标准差调整阈值
        # 如果波动增大，提高阈值；如果波动减小，降低阈值
        cv = std / mean if mean != 0 else 0  # 变异系数
        
        # 调整因子：CV 越大，阈值越高
        adjustment_factor = 1.0 + cv
        
        # 应用调整
        new_threshold = threshold.base_threshold * adjustment_factor
        
        # 限制在合理范围内
        new_threshold = max(threshold.min_threshold, min(threshold.max_threshold, new_threshold))
        
        # 更新阈值
        threshold.current_threshold = new_threshold
        threshold.adjustment_factor = adjustment_factor
        threshold.last_updated = datetime.now(timezone.utc).isoformat()
        threshold.update_count += 1
        threshold.history.append(new_threshold)
        
        logger.debug(f"Updated threshold for {metric_name}: {new_threshold:.4f} (factor={adjustment_factor:.2f})")
        
        return new_threshold
    
    def check_anomaly(self, metric_name: str, value: float) -> AnomalyEvent:
        """
        检查异常
        
        Args:
            metric_name: 指标名称
            value: 当前值
            
        Returns:
            异常事件
        """
        threshold = self.thresholds.get(metric_name)
        if not threshold:
            raise ValueError(f"Threshold not found: {metric_name}")
        
        # 更新阈值
        current_threshold = self.update_threshold(metric_name, value)
        
        # 计算偏离程度
        deviation = abs(value - threshold.base_threshold)
        deviation_ratio = deviation / threshold.base_threshold if threshold.base_threshold != 0 else 0
        
        # 判断异常级别
        if deviation_ratio > 2.0:
            level = AnomalyLevel.CRITICAL
        elif deviation_ratio > 1.5:
            level = AnomalyLevel.WARNING
        else:
            level = AnomalyLevel.NORMAL
        
        import uuid
        event = AnomalyEvent(
            event_id=str(uuid.uuid4()),
            anomaly_level=level,
            deviation_score=deviation_ratio,
            description=f"Value {value:.2f} vs threshold {current_threshold:.2f}",
            detected_at=datetime.now(timezone.utc).isoformat(),
            expected_value=threshold.base_threshold,
            actual_value=value,
            threshold_used=current_threshold,
            metadata={
                "deviation_ratio": deviation_ratio,
                "adjustment_factor": threshold.adjustment_factor
            }
        )
        
        if level != AnomalyLevel.NORMAL:
            logger.warning(f"Anomaly detected for {metric_name}: {event.description}")
        
        return event
    
    def get_threshold_stats(self, metric_name: str) -> Dict:
        """获取阈值统计信息"""
        threshold = self.thresholds.get(metric_name)
        if not threshold:
            return {"error": f"Threshold not found: {metric_name}"}
        
        return {
            "metric_name": threshold.metric_name,
            "current_threshold": threshold.current_threshold,
            "base_threshold": threshold.base_threshold,
            "adjustment_factor": threshold.adjustment_factor,
            "update_count": threshold.update_count,
            "min_threshold": threshold.min_threshold,
            "max_threshold": threshold.max_threshold,
            "history_length": len(threshold.history)
        }


class BehaviorModeler:
    """行为建模器
    
    学习和预测系统行为模式
    """
    
    def __init__(self):
        self.behavior_profiles: Dict[str, Dict] = {}
    
    def learn_behavior(self, user_id: str, actions: List[Dict]) -> Dict:
        """
        学习用户行为模式
        
        Args:
            user_id: 用户ID
            actions: 行为列表
            
        Returns:
            行为画像
        """
        if not actions:
            return {}
        
        # 统计行为频率
        action_counts = defaultdict(int)
        for action in actions:
            action_type = action.get("type", "unknown")
            action_counts[action_type] += 1
        
        # 计算时间分布
        timestamps = [action.get("timestamp", "") for action in actions if "timestamp" in action]
        
        profile = {
            "user_id": user_id,
            "total_actions": len(actions),
            "action_distribution": dict(action_counts),
            "most_common_action": max(action_counts, key=action_counts.get) if action_counts else None,
            "learned_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.behavior_profiles[user_id] = profile
        
        logger.info(f"Learned behavior profile for {user_id}: {len(action_counts)} action types")
        
        return profile
    
    def detect_behavior_anomaly(self, user_id: str, new_action: Dict) -> bool:
        """
        检测行为异常
        
        Args:
            user_id: 用户ID
            new_action: 新行为
            
        Returns:
            是否异常
        """
        profile = self.behavior_profiles.get(user_id)
        if not profile:
            return False  # 没有历史数据，无法判断
        
        action_type = new_action.get("type", "unknown")
        
        # 如果是不常见的行为类型，标记为异常
        if action_type not in profile["action_distribution"]:
            logger.warning(f"Unusual action detected for {user_id}: {action_type}")
            return True
        
        return False


class LearningEngine:
    """学习引擎
    
    整合模式识别、自适应阈值、行为建模的完整学习系统
    """
    
    def __init__(self):
        self.pattern_recognizer = PatternRecognizer()
        self.threshold_manager = AdaptiveThresholdManager()
        self.behavior_modeler = BehaviorModeler()
        
        self.learning_history: List[Dict] = []
    
    def observe(self, metric_name: str, value: float, context: Dict = None) -> Dict:
        """
        观察并学习
        
        Args:
            metric_name: 指标名称
            value: 观测值
            context: 上下文信息
            
        Returns:
            学习结果
        """
        result = {
            "metric": metric_name,
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Step 1: 添加数据点
        data_point = DataPoint.from_value(value, context)
        self.pattern_recognizer.add_data_point(data_point)
        
        # Step 2: 检查异常
        try:
            anomaly_event = self.threshold_manager.check_anomaly(metric_name, value)
            result["anomaly"] = {
                "level": anomaly_event.anomaly_level.value,
                "deviation_score": anomaly_event.deviation_score,
                "description": anomaly_event.description
            }
        except ValueError:
            # 阈值不存在，创建默认阈值
            self.threshold_manager.create_threshold(metric_name, base_threshold=value)
            result["anomaly"] = {"level": "normal", "note": "Threshold created"}
        
        # Step 3: 识别模式（定期执行）
        if len(self.pattern_recognizer.history) % 10 == 0:
            patterns = self.pattern_recognizer.recognize_patterns()
            result["patterns"] = [
                {
                    "type": p.pattern_type.value,
                    "confidence": p.confidence,
                    "description": p.description
                }
                for p in patterns
            ]
        
        # 记录学习历史
        self.learning_history.append(result)
        
        return result
    
    def get_insights(self) -> Dict:
        """获取学习洞察"""
        return {
            "total_observations": len(self.learning_history),
            "patterns_detected": len(self.pattern_recognizer.detected_patterns),
            "active_thresholds": len(self.threshold_manager.thresholds),
            "behavior_profiles": len(self.behavior_modeler.behavior_profiles)
        }


def create_learning_engine() -> LearningEngine:
    """工厂函数：创建学习引擎"""
    return LearningEngine()


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("Pattern Recognition & Adaptive Thresholds 测试")
    print("="*60)
    
    engine = create_learning_engine()
    
    # 模拟观测数据
    print("\n📊 模拟观测...")
    import random
    base_value = 100.0
    
    for i in range(50):
        # 生成带噪声的数据
        if i < 40:
            value = base_value + random.gauss(0, 5)  # 正常波动
        else:
            value = base_value + random.gauss(0, 15)  # 异常波动
        
        result = engine.observe("test_metric", value)
        
        if i % 10 == 9:
            print(f"   观测 #{i+1}: value={value:.2f}")
            if "patterns" in result:
                for pattern in result["patterns"]:
                    print(f"      🔍 模式: {pattern['type']} (置信度: {pattern['confidence']:.2f})")
    
    # 获取洞察
    print("\n💡 学习洞察:")
    insights = engine.get_insights()
    print(json.dumps(insights, indent=2, ensure_ascii=False))
    
    # 阈值统计
    print("\n📈 阈值统计:")
    stats = engine.threshold_manager.get_threshold_stats("test_metric")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    print("\n✅ 测试完成！")
