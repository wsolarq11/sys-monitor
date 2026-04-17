#!/usr/bin/env python3
"""
AI Agent Continuous & Online Learning System - AI Agent 持续学习与在线学习系统

增量学习、灾难性遗忘防护、自适应训练、元学习
实现生产级 AI Agent 的终身学习框架

参考社区最佳实践:
- Online learning with streaming data
- Incremental learning without catastrophic forgetting
- Elastic Weight Consolidation (EWC)
- Experience replay and memory buffers
- Meta-learning for fast adaptation
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
from collections import deque

logger = logging.getLogger(__name__)


class LearningStrategy(Enum):
    """学习策略"""
    ONLINE_GRADIENT = "online_gradient"  # 在线梯度下降
    EWC = "ewc"  # 弹性权重固化
    EXPERIENCE_REPLAY = "experience_replay"  # 经验回放
    PROGRESSIVE_NETS = "progressive_nets"  # 渐进式网络
    META_LEARNING = "meta_learning"  # 元学习


class ForgettingMitigation(Enum):
    """遗忘缓解策略"""
    MEMORY_REPLAY = "memory_replay"  # 记忆回放
    REGULARIZATION = "regularization"  # 正则化
    PARAMETER_ISOLATION = "parameter_isolation"  # 参数隔离
    ARCHITECTURE_EXPANSION = "architecture_expansion"  # 架构扩展


@dataclass
class LearningEvent:
    """学习事件"""
    event_id: str
    timestamp: str
    event_type: str  # interaction/feedback/correction/new_task
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    reward: Optional[float] = None  # 奖励信号 (-1 to 1)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ModelUpdate:
    """模型更新记录"""
    update_id: str
    strategy: LearningStrategy
    parameters_changed: int
    performance_before: float
    performance_after: float
    forgetting_score: float  # 0-1, 越低越好
    training_samples: int
    update_time: str = ""
    
    def __post_init__(self):
        if not self.update_time:
            self.update_time = datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryBuffer:
    """记忆缓冲区"""
    buffer_id: str
    capacity: int
    current_size: int
    samples: deque = field(default_factory=deque)
    sampling_strategy: str = "uniform"  # uniform/priority/recency
    
    def add_sample(self, sample: Dict):
        """添加样本"""
        if len(self.samples) >= self.capacity:
            self.samples.popleft()  # FIFO
        
        self.samples.append(sample)
        self.current_size = len(self.samples)
    
    def sample(self, batch_size: int = 10) -> List[Dict]:
        """采样"""
        if not self.samples:
            return []
        
        if self.sampling_strategy == "uniform":
            return random.sample(list(self.samples), min(batch_size, len(self.samples)))
        elif self.sampling_strategy == "recency":
            return list(self.samples)[-batch_size:]
        else:
            # priority-based (简化实现)
            return random.sample(list(self.samples), min(batch_size, len(self.samples)))


@dataclass
class PerformanceMetrics:
    """性能指标"""
    metric_id: str
    task_name: str
    accuracy: float
    loss: float
    latency_ms: float
    throughput: float  # samples/sec
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class OnlineLearner:
    """在线学习器
    
    支持流式数据实时更新
    """
    
    def __init__(self, learning_rate: float = 0.001):
        self.learning_rate = learning_rate
        self.model_parameters: Dict[str, float] = {}
        self.update_history: List[ModelUpdate] = []
        self.performance_history: List[PerformanceMetrics] = []
    
    def online_update(
        self,
        batch_data: List[Dict],
        labels: List[float],
        strategy: LearningStrategy = LearningStrategy.ONLINE_GRADIENT
    ) -> ModelUpdate:
        """
        在线更新模型
        
        Args:
            batch_data: 批次数据
            labels: 标签
            strategy: 学习策略
            
        Returns:
            模型更新记录
        """
        if not batch_data:
            raise ValueError("Empty batch data")
        
        # 记录更新前性能
        perf_before = self._evaluate_current_performance()
        
        # 执行更新
        if strategy == LearningStrategy.ONLINE_GRADIENT:
            params_changed = self._online_gradient_descent(batch_data, labels)
        elif strategy == LearningStrategy.EWC:
            params_changed = self._elastic_weight_consolidation(batch_data, labels)
        else:
            params_changed = self._online_gradient_descent(batch_data, labels)
        
        # 记录更新后性能
        perf_after = self._evaluate_current_performance()
        
        # 计算遗忘分数
        forgetting_score = self._calculate_forgetting_score()
        
        # 创建更新记录
        update = ModelUpdate(
            update_id=str(uuid.uuid4()),
            strategy=strategy,
            parameters_changed=params_changed,
            performance_before=perf_before,
            performance_after=perf_after,
            forgetting_score=forgetting_score,
            training_samples=len(batch_data)
        )
        
        self.update_history.append(update)
        
        logger.info(f"Online update completed: {params_changed} params changed, perf {perf_before:.3f} → {perf_after:.3f}")
        
        return update
    
    def _online_gradient_descent(self, batch_data: List[Dict], labels: List[float]) -> int:
        """在线梯度下降"""
        # 模拟参数更新
        params_changed = 0
        
        for i, (data, label) in enumerate(zip(batch_data, labels)):
            # 计算预测
            prediction = self._predict(data)
            
            # 计算误差
            error = label - prediction
            
            # 更新参数（简化）
            for key in data.keys():
                if key not in self.model_parameters:
                    self.model_parameters[key] = 0.0
                
                gradient = error * data[key]
                self.model_parameters[key] += self.learning_rate * gradient
                params_changed += 1
        
        return params_changed
    
    def _elastic_weight_consolidation(self, batch_data: List[Dict], labels: List[float]) -> int:
        """弹性权重固化 (EWC) - 防止灾难性遗忘"""
        # EWC 通过惩罚重要参数的变化来防止遗忘
        # 这里简化实现
        
        importance_weights = self._calculate_parameter_importance()
        
        params_changed = 0
        
        for i, (data, label) in enumerate(zip(batch_data, labels)):
            prediction = self._predict(data)
            error = label - prediction
            
            for key in data.keys():
                if key not in self.model_parameters:
                    self.model_parameters[key] = 0.0
                
                # EWC: 结合梯度和重要性权重
                gradient = error * data[key]
                importance = importance_weights.get(key, 1.0)
                
                # 降低重要参数的更新幅度
                adjusted_gradient = gradient / (1.0 + importance)
                self.model_parameters[key] += self.learning_rate * adjusted_gradient
                params_changed += 1
        
        return params_changed
    
    def _calculate_parameter_importance(self) -> Dict[str, float]:
        """计算参数重要性 (Fisher Information Matrix 近似)"""
        importance = {}
        
        for key, value in self.model_parameters.items():
            # 简化：使用参数值的绝对值作为重要性代理
            importance[key] = abs(value)
        
        return importance
    
    def _predict(self, data: Dict) -> float:
        """预测"""
        if not self.model_parameters:
            return 0.5
        
        # 简单线性组合
        prediction = sum(data.get(key, 0) * value for key, value in self.model_parameters.items())
        
        # Sigmoid 激活
        return 1.0 / (1.0 + math.exp(-max(-500, min(500, prediction))))
    
    def _evaluate_current_performance(self) -> float:
        """评估当前性能"""
        if not self.performance_history:
            return 0.5
        
        recent_perfs = self.performance_history[-10:]
        return statistics.mean([p.accuracy for p in recent_perfs])
    
    def _calculate_forgetting_score(self) -> float:
        """计算遗忘分数"""
        if len(self.update_history) < 2:
            return 0.0
        
        # 比较最近两次更新的性能变化
        recent_updates = self.update_history[-5:]
        
        if not recent_updates:
            return 0.0
        
        # 遗忘分数 = 性能下降的程度
        initial_perf = recent_updates[0].performance_after
        final_perf = recent_updates[-1].performance_after
        
        if initial_perf > 0:
            forgetting = max(0, (initial_perf - final_perf) / initial_perf)
        else:
            forgetting = 0.0
        
        return min(1.0, forgetting)
    
    def record_performance(self, metrics: PerformanceMetrics):
        """记录性能指标"""
        self.performance_history.append(metrics)


class ExperienceReplayBuffer:
    """经验回放缓冲区
    
    存储历史经验用于回放学习
    """
    
    def __init__(self, capacity: int = 10000):
        self.buffer = MemoryBuffer(
            buffer_id=str(uuid.uuid4()),
            capacity=capacity,
            current_size=0,
            sampling_strategy="priority"
        )
        self.priority_table: Dict[str, float] = {}
    
    def store_experience(
        self,
        state: Dict,
        action: Any,
        reward: float,
        next_state: Dict,
        done: bool
    ):
        """存储经验"""
        experience = {
            "state": state,
            "action": action,
            "reward": reward,
            "next_state": next_state,
            "done": done,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "priority": abs(reward) + 1e-6  # 初始优先级
        }
        
        exp_id = str(uuid.uuid4())
        self.priority_table[exp_id] = experience["priority"]
        experience["id"] = exp_id
        
        self.buffer.add_sample(experience)
        
        logger.debug(f"Experience stored: reward={reward:.2f}, priority={experience['priority']:.4f}")
    
    def sample_batch(self, batch_size: int = 32) -> List[Dict]:
        """采样批次"""
        return self.buffer.sample(batch_size)
    
    def update_priorities(self, experience_ids: List[str], new_priorities: List[float]):
        """更新优先级"""
        for exp_id, priority in zip(experience_ids, new_priorities):
            if exp_id in self.priority_table:
                self.priority_table[exp_id] = priority


class MetaLearner:
    """元学习器
    
    学习如何快速适应新任务
    """
    
    def __init__(self):
        self.task_history: List[Dict] = []
        self.meta_knowledge: Dict[str, Any] = {}
    
    def learn_from_task(self, task_data: Dict, performance: float):
        """从任务中学习"""
        task_record = {
            "task_id": str(uuid.uuid4()),
            "task_type": task_data.get("type", "unknown"),
            "difficulty": task_data.get("difficulty", "medium"),
            "performance": performance,
            "learning_rate_used": task_data.get("learning_rate", 0.001),
            "strategy_used": task_data.get("strategy", "online_gradient"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.task_history.append(task_record)
        
        # 更新元知识
        self._update_meta_knowledge(task_record)
        
        logger.info(f"Meta-learning from task: type={task_record['task_type']}, perf={performance:.2f}")
    
    def recommend_config(self, new_task: Dict) -> Dict:
        """推荐配置"""
        task_type = new_task.get("type", "unknown")
        difficulty = new_task.get("difficulty", "medium")
        
        # 基于历史任务表现推荐
        similar_tasks = [
            t for t in self.task_history
            if t["task_type"] == task_type
        ]
        
        if similar_tasks:
            # 选择表现最好的配置
            best_task = max(similar_tasks, key=lambda t: t["performance"])
            
            return {
                "recommended_learning_rate": best_task["learning_rate_used"],
                "recommended_strategy": best_task["strategy_used"],
                "confidence": best_task["performance"],
                "based_on_tasks": len(similar_tasks)
            }
        else:
            # 默认配置
            return {
                "recommended_learning_rate": 0.001,
                "recommended_strategy": "online_gradient",
                "confidence": 0.5,
                "based_on_tasks": 0
            }
    
    def _update_meta_knowledge(self, task_record: Dict):
        """更新元知识"""
        task_type = task_record["task_type"]
        
        if task_type not in self.meta_knowledge:
            self.meta_knowledge[task_type] = {
                "total_tasks": 0,
                "avg_performance": 0.0,
                "best_strategy": None,
                "best_performance": 0.0
            }
        
        knowledge = self.meta_knowledge[task_type]
        knowledge["total_tasks"] += 1
        
        # 更新平均性能
        n = knowledge["total_tasks"]
        old_avg = knowledge["avg_performance"]
        knowledge["avg_performance"] = old_avg + (task_record["performance"] - old_avg) / n
        
        # 更新最佳策略
        if task_record["performance"] > knowledge["best_performance"]:
            knowledge["best_performance"] = task_record["performance"]
            knowledge["best_strategy"] = task_record["strategy_used"]


class AdaptiveTrainer:
    """自适应训练器
    
    根据环境和性能自动调整训练策略
    """
    
    def __init__(self):
        self.online_learner = OnlineLearner()
        self.replay_buffer = ExperienceReplayBuffer(capacity=5000)
        self.meta_learner = MetaLearner()
        self.adaptation_history: List[Dict] = []
    
    def adapt_and_learn(
        self,
        new_data: List[Dict],
        labels: List[float],
        context: Dict = None
    ) -> Dict:
        """
        自适应学习
        
        Args:
            new_data: 新数据
            labels: 标签
            context: 上下文信息
            
        Returns:
            学习结果
        """
        context = context or {}
        
        # Step 1: 检测分布偏移
        distribution_shift = self._detect_distribution_shift(new_data)
        
        # Step 2: 选择学习策略
        if distribution_shift > 0.3:
            strategy = LearningStrategy.EWC  # 大偏移用 EWC
        else:
            strategy = LearningStrategy.ONLINE_GRADIENT
        
        # Step 3: 元学习推荐
        task_info = {
            "type": context.get("task_type", "general"),
            "difficulty": context.get("difficulty", "medium")
        }
        
        config = self.meta_learner.recommend_config(task_info)
        
        # Step 4: 执行在线学习
        update = self.online_learner.online_update(new_data, labels, strategy)
        
        # Step 5: 存储经验用于回放
        for i, (data, label) in enumerate(zip(new_data, labels)):
            self.replay_buffer.store_experience(
                state=data,
                action={"prediction": update.performance_after},
                reward=label - update.performance_before,
                next_state={},
                done=(i == len(new_data) - 1)
            )
        
        # Step 6: 定期经验回放
        if len(self.replay_buffer.buffer.samples) > 100:
            replay_batch = self.replay_buffer.sample_batch(batch_size=20)
            if replay_batch:
                replay_data = [exp["state"] for exp in replay_batch]
                replay_labels = [exp["reward"] + 0.5 for exp in replay_batch]  # 转换到 0-1
                
                self.online_learner.online_update(replay_data, replay_labels, strategy)
        
        # Step 7: 记录元学习
        self.meta_learner.learn_from_task(
            task_data={**task_info, **config},
            performance=update.performance_after
        )
        
        # 记录适应历史
        adaptation_record = {
            "distribution_shift": distribution_shift,
            "strategy_used": strategy.value,
            "meta_config": config,
            "update_result": asdict(update),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.adaptation_history.append(adaptation_record)
        
        logger.info(f"Adaptive learning completed: shift={distribution_shift:.2f}, strategy={strategy.value}")
        
        return {
            "update": update,
            "distribution_shift": distribution_shift,
            "meta_recommendation": config,
            "replay_buffer_size": self.replay_buffer.buffer.current_size
        }
    
    def _detect_distribution_shift(self, new_data: List[Dict]) -> float:
        """检测分布偏移"""
        if not new_data:
            return 0.0
        
        # 简化：计算新数据的统计特征与历史数据的差异
        # 实际应使用更复杂的方法如 MMD, KS test 等
        
        new_means = {}
        for key in new_data[0].keys():
            values = [d.get(key, 0) for d in new_data if isinstance(d.get(key), (int, float))]
            if values:
                new_means[key] = statistics.mean(values)
        
        # 与模型参数比较（作为历史分布代理）
        if not self.online_learner.model_parameters:
            return 0.5  # 无历史数据，假设中等偏移
        
        shifts = []
        for key, new_mean in new_means.items():
            old_value = self.online_learner.model_parameters.get(key, 0)
            if old_value != 0:
                shift = abs(new_mean - old_value) / abs(old_value)
                shifts.append(min(shift, 1.0))
        
        return statistics.mean(shifts) if shifts else 0.0
    
    def get_learning_analytics(self) -> Dict:
        """获取学习分析"""
        return {
            "total_updates": len(self.online_learner.update_history),
            "current_performance": self.online_learner._evaluate_current_performance(),
            "forgetting_score": self.online_learner._calculate_forgetting_score() if self.online_learner.update_history else 0.0,
            "replay_buffer_size": self.replay_buffer.buffer.current_size,
            "meta_tasks_learned": len(self.meta_learner.task_history),
            "adaptation_count": len(self.adaptation_history),
            "recent_adaptations": self.adaptation_history[-5:]
        }


def create_adaptive_trainer() -> AdaptiveTrainer:
    """工厂函数：创建自适应训练器"""
    return AdaptiveTrainer()


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Continuous & Online Learning 测试")
    print("="*60)
    
    trainer = create_adaptive_trainer()
    
    # 模拟在线学习场景
    print("\n📚 模拟在线学习...")
    
    for episode in range(5):
        print(f"\n--- Episode {episode + 1} ---")
        
        # 生成模拟数据
        batch_size = 10
        new_data = [
            {"feature_1": random.uniform(0, 1), "feature_2": random.uniform(0, 1)}
            for _ in range(batch_size)
        ]
        labels = [random.uniform(0, 1) for _ in range(batch_size)]
        
        # 上下文
        context = {
            "task_type": "classification",
            "difficulty": "medium"
        }
        
        # 自适应学习
        result = trainer.adapt_and_learn(new_data, labels, context)
        
        print(f"   分布偏移: {result['distribution_shift']:.2f}")
        print(f"   学习策略: {result['update'].strategy.value}")
        print(f"   性能: {result['update'].performance_before:.3f} → {result['update'].performance_after:.3f}")
        print(f"   遗忘分数: {result['update'].forgetting_score:.3f}")
        print(f"   回放缓冲: {result['replay_buffer_size']} 样本")
    
    # 学习分析
    print("\n📊 学习分析:")
    analytics = trainer.get_learning_analytics()
    print(f"   总更新次数: {analytics['total_updates']}")
    print(f"   当前性能: {analytics['current_performance']:.3f}")
    print(f"   遗忘分数: {analytics['forgetting_score']:.3f}")
    print(f"   回放缓冲大小: {analytics['replay_buffer_size']}")
    print(f"   元学习任务数: {analytics['meta_tasks_learned']}")
    print(f"   适应次数: {analytics['adaptation_count']}")
    
    # 元学习推荐
    print("\n🎯 元学习推荐:")
    new_task = {"type": "classification", "difficulty": "hard"}
    recommendation = trainer.meta_learner.recommend_config(new_task)
    print(f"   推荐学习率: {recommendation['recommended_learning_rate']}")
    print(f"   推荐策略: {recommendation['recommended_strategy']}")
    print(f"   置信度: {recommendation['confidence']:.2f}")
    print(f"   基于任务数: {recommendation['based_on_tasks']}")
    
    print("\n✅ 测试完成！")
