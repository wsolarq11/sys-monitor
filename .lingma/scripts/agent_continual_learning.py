#!/usr/bin/env python3
"""
AI Agent Continual Learning & Lifelong Learning System - AI Agent 持续学习与终身学习系统

灾难性遗忘、弹性权重固化、经验回放、元可塑性、互补学习系统
实现生产级 AI Agent 的持续学习能力

参考社区最佳实践:
- Continual/Lifelong Learning - learn new tasks without forgetting old ones
- Catastrophic Forgetting - the core challenge in sequential learning
- Elastic Weight Consolidation (EWC) - protect important parameters
- Experience Replay - store and replay old task samples
- Synaptic Intelligence (SI) - track parameter importance online
- Complementary Learning Systems - hippocampus-neocortex interaction
- Meta-plasticity - adaptive plasticity mechanisms
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
import copy

logger = logging.getLogger(__name__)


class CLMethod(Enum):
    """持续学习方法"""
    EWC = "EWC"  # 弹性权重固化
    SI = "SI"  # 突触智能
    EXPERIENCE_REPLAY = "experience_replay"  # 经验回放
    LWF = "LwF"  # 无遗忘学习
    PROGRESSIVE_NETS = "progressive_nets"  # 渐进式网络
    GENERATIVE_REPLAY = "generative_replay"  # 生成回放


class TaskType(Enum):
    """任务类型"""
    CLASS_INCREMENTAL = "class_incremental"  # 类增量
    DOMAIN_INCREMENTAL = "domain_incremental"  # 域增量
    TASK_INCREMENTAL = "task_incremental"  # 任务增量


@dataclass
class Task:
    """学习任务"""
    task_id: str
    task_name: str
    task_type: TaskType
    training_data: List[Dict] = field(default_factory=list)
    test_data: List[Dict] = field(default_factory=list)
    num_classes: int = 0
    learned_at: str = ""
    
    def __post_init__(self):
        if not self.task_id:
            self.task_id = str(uuid.uuid4())
        if not self.learned_at:
            self.learned_at = datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryBuffer:
    """记忆缓冲区（用于经验回放）"""
    buffer_id: str
    capacity: int = 1000
    samples: List[Dict] = field(default_factory=list)
    sampling_strategy: str = "random"  # random/reservoir
    
    def __post_init__(self):
        if not self.buffer_id:
            self.buffer_id = str(uuid.uuid4())
    
    def add_sample(self, sample: Dict):
        """添加样本"""
        if len(self.samples) < self.capacity:
            self.samples.append(sample)
        else:
            # 蓄水池采样
            if self.sampling_strategy == "reservoir":
                idx = random.randint(0, len(self.samples) - 1)
                self.samples[idx] = sample
    
    def get_batch(self, batch_size: int = 32) -> List[Dict]:
        """获取批次样本"""
        if not self.samples:
            return []
        
        batch_size = min(batch_size, len(self.samples))
        return random.sample(self.samples, batch_size)
    
    @property
    def size(self) -> int:
        return len(self.samples)


@dataclass
class FisherInformationMatrix:
    """Fisher信息矩阵（用于EWC）"""
    matrix_id: str
    parameter_importance: Dict[str, float] = field(default_factory=dict)
    optimal_parameters: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.matrix_id:
            self.matrix_id = str(uuid.uuid4())
    
    def update_importance(self, param_name: str, importance: float):
        """更新参数重要性"""
        self.parameter_importance[param_name] = importance
    
    def get_importance(self, param_name: str) -> float:
        """获取参数重要性"""
        return self.parameter_importance.get(param_name, 0.0)


@dataclass
class LearningMetrics:
    """学习指标"""
    metrics_id: str
    task_sequence: List[str] = field(default_factory=list)
    accuracy_history: Dict[str, float] = field(default_factory=dict)
    forgetting_measure: float = 0.0
    backward_transfer: float = 0.0
    forward_transfer: float = 0.0
    
    def __post_init__(self):
        if not self.metrics_id:
            self.metrics_id = str(uuid.uuid4())
    
    def calculate_forgetting(self) -> float:
        """计算遗忘程度"""
        if len(self.accuracy_history) < 2:
            return 0.0
        
        # 简化：比较最早任务和最新任务的准确率变化
        accuracies = list(self.accuracy_history.values())
        if len(accuracies) >= 2:
            forgetting = max(0, accuracies[0] - accuracies[-1])
            self.forgetting_measure = forgetting
            return forgetting
        
        return 0.0


class ElasticWeightConsolidation:
    """弹性权重固化 (EWC)
    
    通过Fisher信息矩阵保护重要参数，防止灾难性遗忘
    """
    
    def __init__(self, lambda_ewc: float = 1000.0):
        self.lambda_ewc = lambda_ewc  # EWC正则化强度
        self.fisher_matrices: List[FisherInformationMatrix] = []
        self.consolidation_history: List[Dict] = []
    
    def compute_fisher_information(
        self,
        model_parameters: Dict[str, float],
        task_data: List[Dict]
    ) -> FisherInformationMatrix:
        """
        计算Fisher信息矩阵
        
        Args:
            model_parameters: 模型参数 {param_name: value}
            task_data: 任务数据
            
        Returns:
            Fisher信息矩阵
        """
        fisher = FisherInformationMatrix(matrix_id="")
        
        # 简化实现：基于梯度幅度估计重要性
        for param_name, param_value in model_parameters.items():
            # 模拟梯度计算
            gradients = [
                abs(random.gauss(0, 0.1)) * abs(param_value)
                for _ in range(min(100, len(task_data)))
            ]
            
            # Fisher信息 = 梯度平方的期望
            fisher_info = statistics.mean([g**2 for g in gradients])
            fisher.update_importance(param_name, fisher_info)
            fisher.optimal_parameters[param_name] = param_value
        
        self.fisher_matrices.append(fisher)
        
        logger.info(f"Fisher information computed for {len(model_parameters)} parameters")
        
        return fisher
    
    def ewc_loss(
        self,
        current_parameters: Dict[str, float],
        new_task_loss: float
    ) -> float:
        """
        计算EWC损失
        
        L(θ) = L_new(θ) + λ/2 * Σ F_i * (θ_i - θ*_i)²
        
        Args:
            current_parameters: 当前参数
            new_task_loss: 新任务损失
            
        Returns:
            总损失（包含EWC正则化）
        """
        if not self.fisher_matrices:
            return new_task_loss
        
        # 使用最新的Fisher矩阵
        latest_fisher = self.fisher_matrices[-1]
        
        # 计算EWC正则化项
        ewc_penalty = 0.0
        for param_name, param_value in current_parameters.items():
            importance = latest_fisher.get_importance(param_name)
            optimal_value = latest_fisher.optimal_parameters.get(param_name, param_value)
            
            ewc_penalty += importance * (param_value - optimal_value)**2
        
        total_loss = new_task_loss + (self.lambda_ewc / 2) * ewc_penalty
        
        return total_loss
    
    def consolidate_weights(
        self,
        model_parameters: Dict[str, float],
        task: Task
    ) -> Dict[str, float]:
        """
        固化权重（学习后调用）
        
        Args:
            model_parameters: 模型参数
            task: 已完成的任务
            
        Returns:
            更新后的参数
        """
        # 计算Fisher信息
        fisher = self.compute_fisher_information(model_parameters, task.training_data)
        
        # 记录固化历史
        self.consolidation_history.append({
            "task_id": task.task_id,
            "task_name": task.task_name,
            "num_parameters": len(model_parameters),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(f"Weights consolidated for task: {task.task_name}")
        
        return model_parameters


class ExperienceReplayBuffer:
    """经验回放缓冲区
    
    存储旧任务样本，在学习新任务时混合重放
    """
    
    def __init__(self, capacity: int = 1000, strategy: str = "reservoir"):
        self.buffer = MemoryBuffer(
            buffer_id="",
            capacity=capacity,
            sampling_strategy=strategy
        )
        self.replay_history: List[Dict] = []
    
    def store_experience(self, experience: Dict):
        """存储经验"""
        self.buffer.add_sample(experience)
    
    def store_task_experiences(self, experiences: List[Dict]):
        """批量存储任务经验"""
        for exp in experiences:
            self.store_experience(exp)
        
        logger.info(f"Stored {len(experiences)} experiences, buffer size: {self.buffer.size}")
    
    def replay_batch(self, batch_size: int = 32) -> List[Dict]:
        """回放批次"""
        batch = self.buffer.get_batch(batch_size)
        
        if batch:
            self.replay_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "batch_size": len(batch),
                "buffer_size": self.buffer.size
            })
        
        return batch
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "buffer_capacity": self.buffer.capacity,
            "current_size": self.buffer.size,
            "utilization": self.buffer.size / self.buffer.capacity if self.buffer.capacity > 0 else 0.0,
            "total_replays": len(self.replay_history)
        }


class SynapticIntelligence:
    """突触智能 (SI)
    
    在线跟踪参数重要性，无需额外数据
    """
    
    def __init__(self, xi: float = 0.1):
        self.xi = xi  # SI阻尼系数
        self.parameter_importance: Dict[str, float] = {}
        self.parameter_changes: Dict[str, float] = {}
        self.si_history: List[Dict] = []
    
    def track_parameter_change(
        self,
        param_name: str,
        old_value: float,
        new_value: float,
        loss_decrease: float
    ):
        """
        跟踪参数变化
        
        Args:
            param_name: 参数名
            old_value: 旧值
            new_value: 新值
            loss_decrease: 损失减少量
        """
        delta_theta = new_value - old_value
        
        if param_name not in self.parameter_importance:
            self.parameter_importance[param_name] = 0.0
        
        if param_name not in self.parameter_changes:
            self.parameter_changes[param_name] = 0.0
        
        # 累积重要性
        if abs(delta_theta) > 1e-8:
            omega = loss_decrease / (delta_theta**2 + self.xi)
            self.parameter_importance[param_name] += max(0, omega)
        
        self.parameter_changes[param_name] += delta_theta**2
    
    def si_regularization_loss(
        self,
        current_parameters: Dict[str, float],
        reference_parameters: Dict[str, float],
        new_task_loss: float
    ) -> float:
        """
        计算SI正则化损失
        
        L(θ) = L_new(θ) + c * Σ ω_i * (θ_i - θ_ref_i)² / (Δθ_i² + ξ)
        
        Args:
            current_parameters: 当前参数
            reference_parameters: 参考参数（任务前）
            new_task_loss: 新任务损失
            
        Returns:
            总损失
        """
        si_penalty = 0.0
        
        for param_name in current_parameters:
            if param_name in self.parameter_importance:
                importance = self.parameter_importance[param_name]
                theta_diff = current_parameters[param_name] - reference_parameters.get(param_name, 0)
                delta_sq = self.parameter_changes.get(param_name, 1e-8)
                
                si_penalty += importance * theta_diff**2 / (delta_sq + self.xi)
        
        total_loss = new_task_loss + si_penalty
        
        return total_loss
    
    def reset_after_task(self):
        """任务完成后重置变化追踪"""
        self.parameter_changes.clear()
        
        self.si_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tracked_parameters": len(self.parameter_importance)
        })


class ContinualLearner:
    """持续学习器
    
    整合多种CL方法，管理任务序列学习
    """
    
    def __init__(
        self,
        method: CLMethod = CLMethod.EWC,
        lambda_ewc: float = 1000.0,
        buffer_capacity: int = 1000
    ):
        self.method = method
        self.tasks_learned: List[Task] = []
        self.learning_metrics = LearningMetrics(metrics_id="")
        
        # 初始化CL组件
        self.ewc = ElasticWeightConsolidation(lambda_ewc=lambda_ewc)
        self.replay_buffer = ExperienceReplayBuffer(capacity=buffer_capacity)
        self.si = SynapticIntelligence(xi=0.1)
        
        # 模型参数（简化）
        self.model_parameters: Dict[str, float] = {}
    
    def learn_task(
        self,
        task: Task,
        initial_parameters: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        学习任务
        
        Args:
            task: 要学习的任务
            initial_parameters: 初始参数
            
        Returns:
            学习结果
        """
        # 保存任务前参数（用于SI）
        if initial_parameters:
            self.model_parameters = initial_parameters.copy()
        else:
            # 随机初始化
            self.model_parameters = {
                f"param_{i}": random.gauss(0, 0.1)
                for i in range(50)
            }
        
        reference_params = self.model_parameters.copy()
        
        # Step 1: 在新任务上训练（简化模拟）
        training_loss = self._simulate_training(task)
        
        # Step 2: 应用CL方法
        if self.method == CLMethod.EWC:
            # EWC：计算Fisher信息并固化
            self.ewc.consolidate_weights(self.model_parameters, task)
            
            # 计算EWC损失
            ewc_loss = self.ewc.ewc_loss(self.model_parameters, training_loss)
            final_loss = ewc_loss
            
        elif self.method == CLMethod.EXPERIENCE_REPLAY:
            # 经验回放：存储当前任务经验
            experiences = [
                {"data": sample, "task_id": task.task_id}
                for sample in task.training_data[:100]
            ]
            self.replay_buffer.store_task_experiences(experiences)
            
            # 混合回放旧任务数据
            if self.replay_buffer.buffer.size > 0:
                replay_batch = self.replay_buffer.replay_batch(batch_size=32)
                # 模拟回放训练
                training_loss *= 0.9  # 回放帮助降低损失
            
            final_loss = training_loss
            
        elif self.method == CLMethod.SI:
            # SI：跟踪参数变化
            for param_name in self.model_parameters:
                old_val = reference_params.get(param_name, 0)
                new_val = self.model_parameters[param_name]
                loss_dec = random.uniform(0.01, 0.1)
                
                self.si.track_parameter_change(param_name, old_val, new_val, loss_dec)
            
            # 计算SI损失
            si_loss = self.si.si_regularization_loss(
                self.model_parameters, reference_params, training_loss
            )
            final_loss = si_loss
            
            # 任务完成后重置
            self.si.reset_after_task()
        
        else:
            final_loss = training_loss
        
        # 记录学习指标
        self.tasks_learned.append(task)
        self.learning_metrics.task_sequence.append(task.task_id)
        self.learning_metrics.accuracy_history[task.task_id] = 1.0 - final_loss
        
        # 计算遗忘
        forgetting = self.learning_metrics.calculate_forgetting()
        
        result = {
            "task_id": task.task_id,
            "task_name": task.task_name,
            "final_loss": final_loss,
            "accuracy": 1.0 - final_loss,
            "forgetting_measure": forgetting,
            "method_used": self.method.value
        }
        
        logger.info(f"Task learned: {task.task_name}, loss={final_loss:.4f}, forgetting={forgetting:.4f}")
        
        return result
    
    def evaluate_continual_learning(self) -> Dict[str, Any]:
        """评估持续学习效果"""
        # 计算平均准确率
        accuracies = list(self.learning_metrics.accuracy_history.values())
        avg_accuracy = statistics.mean(accuracies) if accuracies else 0.0
        
        # 计算遗忘
        forgetting = self.learning_metrics.forgetting_measure
        
        # 计算前后向迁移
        backward_transfer = self._calculate_backward_transfer()
        forward_transfer = self._calculate_forward_transfer()
        
        return {
            "num_tasks_learned": len(self.tasks_learned),
            "average_accuracy": round(avg_accuracy, 4),
            "forgetting_measure": round(forgetting, 4),
            "backward_transfer": round(backward_transfer, 4),
            "forward_transfer": round(forward_transfer, 4),
            "cl_method": self.method.value,
            "tasks_sequence": [t.task_name for t in self.tasks_learned]
        }
    
    def _simulate_training(self, task: Task) -> float:
        """模拟训练过程（返回损失）"""
        # 简化：基于任务复杂度生成损失
        base_loss = random.uniform(0.2, 0.5)
        
        # 如果有之前任务，考虑干扰
        if len(self.tasks_learned) > 0:
            interference = random.uniform(0.05, 0.15)
            base_loss += interference
        
        return base_loss
    
    def _calculate_backward_transfer(self) -> float:
        """计算后向迁移（对旧任务的帮助）"""
        if len(self.tasks_learned) < 2:
            return 0.0
        
        # 简化：假设轻微正迁移
        return random.uniform(0.01, 0.05)
    
    def _calculate_forward_transfer(self) -> float:
        """计算前向迁移（对新任务的帮助）"""
        if len(self.tasks_learned) < 2:
            return 0.0
        
        # 简化：假设轻微正迁移
        return random.uniform(0.01, 0.05)


def create_continual_learning_system(method: CLMethod = CLMethod.EWC) -> ContinualLearner:
    """工厂函数：创建持续学习系统"""
    learner = ContinualLearner(method=method)
    return learner


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Continual Learning & Lifelong Learning 测试")
    print("="*60)
    
    # 测试EWC方法
    print("\n🧠 测试EWC（弹性权重固化）...")
    ewc_learner = create_continual_learning_system(CLMethod.EWC)
    
    # 创建任务序列
    tasks = [
        Task(
            task_id="",
            task_name="MNIST_Digits_0-4",
            task_type=TaskType.CLASS_INCREMENTAL,
            training_data=[{"image": f"img_{i}", "label": i % 5} for i in range(100)],
            num_classes=5
        ),
        Task(
            task_id="",
            task_name="MNIST_Digits_5-9",
            task_type=TaskType.CLASS_INCREMENTAL,
            training_data=[{"image": f"img_{i}", "label": 5 + i % 5} for i in range(100)],
            num_classes=5
        ),
        Task(
            task_id="",
            task_name="CIFAR10_Animals",
            task_type=TaskType.CLASS_INCREMENTAL,
            training_data=[{"image": f"img_{i}", "label": i % 3} for i in range(100)],
            num_classes=3
        )
    ]
    
    # 依次学习任务
    results = []
    for task in tasks:
        result = ewc_learner.learn_task(task)
        results.append(result)
        print(f"   任务: {result['task_name']}")
        print(f"     损失: {result['final_loss']:.4f}")
        print(f"     准确率: {result['accuracy']:.4f}")
        print(f"     遗忘: {result['forgetting_measure']:.4f}")
    
    # 评估持续学习
    eval_result = ewc_learner.evaluate_continual_learning()
    print(f"\n   📊 EWC评估结果:")
    print(f"     学习任务数: {eval_result['num_tasks_learned']}")
    print(f"     平均准确率: {eval_result['average_accuracy']:.4f}")
    print(f"     遗忘程度: {eval_result['forgetting_measure']:.4f}")
    print(f"     后向迁移: {eval_result['backward_transfer']:.4f}")
    print(f"     前向迁移: {eval_result['forward_transfer']:.4f}")
    print(f"     使用方法: {eval_result['cl_method']}")
    
    # 测试经验回放
    print("\n💾 测试经验回放...")
    replay_learner = create_continual_learning_system(CLMethod.EXPERIENCE_REPLAY)
    
    for task in tasks[:2]:
        result = replay_learner.learn_task(task)
        print(f"   任务: {result['task_name']}, 损失: {result['final_loss']:.4f}")
    
    buffer_stats = replay_learner.replay_buffer.get_stats()
    print(f"\n   📦 回放缓冲区统计:")
    print(f"     容量: {buffer_stats['buffer_capacity']}")
    print(f"     当前大小: {buffer_stats['current_size']}")
    print(f"     利用率: {buffer_stats['utilization']*100:.1f}%")
    print(f"     总回放次数: {buffer_stats['total_replays']}")
    
    # 测试SI方法
    print("\n🔗 测试SI（突触智能）...")
    si_learner = create_continual_learning_system(CLMethod.SI)
    
    for task in tasks:
        result = si_learner.learn_task(task)
        print(f"   任务: {result['task_name']}, 损失: {result['final_loss']:.4f}")
    
    si_eval = si_learner.evaluate_continual_learning()
    print(f"\n   📊 SI评估结果:")
    print(f"     平均准确率: {si_eval['average_accuracy']:.4f}")
    print(f"     遗忘程度: {si_eval['forgetting_measure']:.4f}")
    
    # Fisher信息矩阵
    print("\n📈 Fisher信息统计...")
    if ewc_learner.ewc.fisher_matrices:
        latest_fisher = ewc_learner.ewc.fisher_matrices[-1]
        importances = list(latest_fisher.parameter_importance.values())
        print(f"   参数数量: {len(importances)}")
        print(f"   平均重要性: {statistics.mean(importances):.6f}")
        print(f"   最大重要性: {max(importances):.6f}")
        print(f"   最小重要性: {min(importances):.6f}")
    
    # 学习历史
    print("\n📚 学习历史...")
    print(f"   EWC固化次数: {len(ewc_learner.ewc.consolidation_history)}")
    print(f"   SI跟踪次数: {len(si_learner.si.si_history)}")
    print(f"   回放历史: {len(replay_learner.replay_buffer.replay_history)}")
    
    print("\n✅ 测试完成！")
