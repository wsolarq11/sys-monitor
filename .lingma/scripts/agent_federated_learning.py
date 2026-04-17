#!/usr/bin/env python3
"""
AI Agent Federated Learning & Privacy-Preserving System - AI Agent 联邦学习与隐私保护系统

联邦学习、差分隐私、安全聚合、边缘计算
实现生产级 AI Agent 的隐私保护分布式训练框架

参考社区最佳实践:
- Federated Learning with secure aggregation
- Differential privacy for gradient protection
- Edge computing deployment
- Privacy-preserving distributed training
- Secure multi-party computation
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
import math
import statistics
import random
import hashlib

logger = logging.getLogger(__name__)


class AggregationStrategy(Enum):
    """聚合策略"""
    FEDAVG = "fedavg"  # FedAvg (Federated Averaging)
    FEDPROX = "fedprox"  # FedProx
    SECURE_AGG = "secure_agg"  # 安全聚合
    WEIGHTED_AGG = "weighted_agg"  # 加权聚合


class PrivacyMechanism(Enum):
    """隐私保护机制"""
    DIFFERENTIAL_PRIVACY = "differential_privacy"  # 差分隐私
    SECURE_MULTI_PARTY = "secure_multi_party"  # 安全多方计算
    HOMOMORPHIC_ENCRYPTION = "homomorphic_encryption"  # 同态加密
    SECRET_SHARING = "secret_sharing"  # 秘密分享


@dataclass
class ClientUpdate:
    """客户端更新"""
    client_id: str
    update_id: str
    model_updates: Dict[str, float]
    num_samples: int
    local_epochs: int
    training_loss: float
    timestamp: str = ""
    encrypted: bool = False
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class PrivacyBudget:
    """隐私预算"""
    budget_id: str
    epsilon: float  # 隐私预算参数 ε
    delta: float  # 失败概率 δ
    spent_epsilon: float = 0.0
    mechanism: PrivacyMechanism = PrivacyMechanism.DIFFERENTIAL_PRIVACY
    remaining_budget: float = 0.0
    
    def __post_init__(self):
        self.remaining_budget = self.epsilon - self.spent_epsilon
    
    def spend(self, epsilon_spent: float) -> bool:
        """消耗隐私预算"""
        if self.remaining_budget >= epsilon_spent:
            self.spent_epsilon += epsilon_spent
            self.remaining_budget = self.epsilon - self.spent_epsilon
            return True
        else:
            logger.warning(f"Privacy budget exceeded: {epsilon_spent} > {self.remaining_budget}")
            return False


@dataclass
class FederatedRound:
    """联邦学习轮次"""
    round_id: str
    round_number: int
    participating_clients: int
    aggregated_model: Dict[str, float]
    global_loss: float
    convergence_metric: float
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class EdgeNode:
    """边缘节点"""
    node_id: str
    location: str
    compute_capacity: float  # 0-1
    bandwidth: float  # Mbps
    current_load: float  # 0-1
    available: bool = True
    last_heartbeat: str = ""
    
    def __post_init__(self):
        if not self.last_heartbeat:
            self.last_heartbeat = datetime.now(timezone.utc).isoformat()


class DifferentialPrivacyEngine:
    """差分隐私引擎
    
    为梯度添加噪声以保护隐私
    """
    
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        self.privacy_budget = PrivacyBudget(
            budget_id=str(uuid.uuid4()),
            epsilon=epsilon,
            delta=delta
        )
        self.noise_history: List[Dict] = []
    
    def add_noise_to_gradients(
        self,
        gradients: Dict[str, float],
        sensitivity: float = 1.0
    ) -> Dict[str, float]:
        """
        为梯度添加拉普拉斯噪声
        
        Args:
            gradients: 原始梯度
            sensitivity: 敏感度
            
        Returns:
            加噪后的梯度
        """
        # 计算噪声尺度
        # 根据隐私预算和敏感度确定噪声大小
        if self.privacy_budget.remaining_budget <= 0:
            logger.warning("Privacy budget exhausted, returning original gradients")
            return gradients
        
        # 简化的噪声尺度计算
        noise_scale = sensitivity / max(self.privacy_budget.remaining_budget, 1e-10)
        
        noisy_gradients = {}
        
        for param_name, grad_value in gradients.items():
            # 添加拉普拉斯噪声
            noise = random.gauss(0, noise_scale)  # 使用高斯噪声替代
            noisy_gradients[param_name] = grad_value + noise
        
        # 记录噪声添加
        epsilon_spent = sensitivity / noise_scale if noise_scale > 0 else 0
        self.privacy_budget.spend(epsilon_spent)
        
        self.noise_history.append({
            "noise_scale": noise_scale,
            "epsilon_spent": epsilon_spent,
            "remaining_budget": self.privacy_budget.remaining_budget,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        logger.debug(f"Noise added: scale={noise_scale:.4f}, epsilon_spent={epsilon_spent:.4f}")
        
        return noisy_gradients
    
    def get_privacy_status(self) -> Dict:
        """获取隐私状态"""
        return {
            "total_budget": self.privacy_budget.epsilon,
            "spent_budget": self.privacy_budget.spent_epsilon,
            "remaining_budget": self.privacy_budget.remaining_budget,
            "budget_utilization": round(
                self.privacy_budget.spent_epsilon / self.privacy_budget.epsilon * 100, 2
            ) if self.privacy_budget.epsilon > 0 else 0,
            "mechanism": self.privacy_budget.mechanism.value
        }


class SecureAggregator:
    """安全聚合器
    
    使用秘密分享和安全聚合协议
    """
    
    def __init__(self):
        self.aggregation_history: List[Dict] = []
    
    def secure_aggregate(
        self,
        client_updates: List[ClientUpdate],
        strategy: AggregationStrategy = AggregationStrategy.SECURE_AGG
    ) -> Dict[str, float]:
        """
        安全聚合客户端更新
        
        Args:
            client_updates: 客户端更新列表
            strategy: 聚合策略
            
        Returns:
            聚合后的模型参数
        """
        if not client_updates:
            return {}
        
        if strategy == AggregationStrategy.FEDAVG:
            return self._fedavg_aggregate(client_updates)
        elif strategy == AggregationStrategy.WEIGHTED_AGG:
            return self._weighted_aggregate(client_updates)
        elif strategy == AggregationStrategy.SECURE_AGG:
            return self._secure_aggregation_protocol(client_updates)
        else:
            return self._fedavg_aggregate(client_updates)
    
    def _fedavg_aggregate(self, client_updates: List[ClientUpdate]) -> Dict[str, float]:
        """FedAvg 聚合"""
        total_samples = sum(update.num_samples for update in client_updates)
        
        if total_samples == 0:
            return {}
        
        # 按样本数加权平均
        aggregated = {}
        
        for update in client_updates:
            weight = update.num_samples / total_samples
            
            for param_name, param_value in update.model_updates.items():
                if param_name not in aggregated:
                    aggregated[param_name] = 0.0
                aggregated[param_name] += param_value * weight
        
        logger.info(f"FedAvg aggregation: {len(client_updates)} clients, {total_samples} samples")
        
        return aggregated
    
    def _weighted_aggregate(self, client_updates: List[ClientUpdate]) -> Dict[str, float]:
        """加权聚合（基于训练质量）"""
        # 计算权重（基于损失值的倒数）
        losses = [update.training_loss for update in client_updates]
        min_loss = min(losses) if losses else 1e-10
        
        weights = []
        for update in client_updates:
            # 损失越小，权重越大
            weight = 1.0 / max(update.training_loss, 1e-10)
            weights.append(weight)
        
        total_weight = sum(weights)
        
        if total_weight == 0:
            return {}
        
        # 加权聚合
        aggregated = {}
        
        for update, weight in zip(client_updates, weights):
            normalized_weight = weight / total_weight
            
            for param_name, param_value in update.model_updates.items():
                if param_name not in aggregated:
                    aggregated[param_name] = 0.0
                aggregated[param_name] += param_value * normalized_weight
        
        logger.info(f"Weighted aggregation: {len(client_updates)} clients")
        
        return aggregated
    
    def _secure_aggregation_protocol(self, client_updates: List[ClientUpdate]) -> Dict[str, float]:
        """安全聚合协议（简化版秘密分享）"""
        # 在实际应用中，这里应实现真正的安全多方计算
        # 目前使用简化的掩码方案
        
        num_clients = len(client_updates)
        
        if num_clients == 0:
            return {}
        
        # 生成随机掩码
        masks = {}
        mask_sum = {}
        
        for update in client_updates:
            client_mask = {}
            
            for param_name in update.model_updates.keys():
                mask = random.gauss(0, 0.1)
                client_mask[param_name] = mask
                
                if param_name not in mask_sum:
                    mask_sum[param_name] = 0.0
                mask_sum[param_name] += mask
            
            masks[update.client_id] = client_mask
        
        # 应用掩码并聚合
        masked_updates = []
        
        for update in client_updates:
            masked_params = {}
            
            for param_name, param_value in update.model_updates.items():
                mask = masks[update.client_id].get(param_name, 0.0)
                masked_params[param_name] = param_value + mask
            
            masked_update = ClientUpdate(
                client_id=update.client_id,
                update_id=update.update_id,
                model_updates=masked_params,
                num_samples=update.num_samples,
                local_epochs=update.local_epochs,
                training_loss=update.training_loss,
                encrypted=True
            )
            
            masked_updates.append(masked_update)
        
        # 聚合掩码后的更新
        aggregated = self._fedavg_aggregate(masked_updates)
        
        # 移除掩码总和
        for param_name in aggregated.keys():
            if param_name in mask_sum:
                aggregated[param_name] -= mask_sum[param_name] / num_clients
        
        logger.info(f"Secure aggregation: {num_clients} clients with masking")
        
        return aggregated


class FederatedLearningCoordinator:
    """联邦学习协调器
    
    协调多个客户端的联邦学习过程
    """
    
    def __init__(
        self,
        num_rounds: int = 100,
        min_clients: int = 2,
        fraction_fit: float = 0.1
    ):
        self.num_rounds = num_rounds
        self.min_clients = min_clients
        self.fraction_fit = fraction_fit
        
        self.global_model: Dict[str, float] = {}
        self.round_history: List[FederatedRound] = []
        self.dp_engine = DifferentialPrivacyEngine()
        self.secure_aggregator = SecureAggregator()
        
        # 模拟客户端
        self.clients: Dict[str, Dict] = {}
    
    def register_client(self, client_id: str, metadata: Dict = None):
        """注册客户端"""
        self.clients[client_id] = {
            "client_id": client_id,
            "metadata": metadata or {},
            "status": "active",
            "last_update": None
        }
        
        logger.info(f"Client registered: {client_id}")
    
    def simulate_local_training(self, client_id: str, global_model: Dict) -> ClientUpdate:
        """
        模拟客户端本地训练
        
        Args:
            client_id: 客户端ID
            global_model: 全局模型
            
        Returns:
            客户端更新
        """
        # 模拟本地训练过程
        num_samples = random.randint(100, 1000)
        local_epochs = random.randint(1, 5)
        
        # 模拟模型更新（在真实场景中，这是通过本地数据训练的）
        model_updates = {}
        
        for param_name, param_value in global_model.items():
            # 模拟梯度更新
            gradient = random.gauss(0, 0.01)
            model_updates[param_name] = param_value + gradient
        
        # 模拟训练损失
        training_loss = random.uniform(0.1, 1.0)
        
        update = ClientUpdate(
            client_id=client_id,
            update_id=str(uuid.uuid4()),
            model_updates=model_updates,
            num_samples=num_samples,
            local_epochs=local_epochs,
            training_loss=training_loss
        )
        
        logger.debug(f"Local training completed for {client_id}: {num_samples} samples, loss={training_loss:.3f}")
        
        return update
    
    def execute_federated_round(self, round_number: int) -> FederatedRound:
        """
        执行一轮联邦学习
        
        Args:
            round_number: 轮次号
            
        Returns:
            轮次结果
        """
        logger.info(f"Starting federated round {round_number}")
        
        # Step 1: 选择参与客户端
        num_clients_to_select = max(
            self.min_clients,
            int(len(self.clients) * self.fraction_fit)
        )
        
        selected_clients = random.sample(
            list(self.clients.keys()),
            min(num_clients_to_select, len(self.clients))
        )
        
        if not selected_clients:
            raise ValueError("No clients available for training")
        
        # Step 2: 分发全局模型并收集更新
        client_updates = []
        
        for client_id in selected_clients:
            # 模拟本地训练
            update = self.simulate_local_training(client_id, self.global_model)
            
            # 应用差分隐私
            if update.model_updates:
                noisy_updates = self.dp_engine.add_noise_to_gradients(update.model_updates)
                update.model_updates = noisy_updates
            
            client_updates.append(update)
            
            # 更新客户端状态
            self.clients[client_id]["last_update"] = datetime.now(timezone.utc).isoformat()
        
        # Step 3: 安全聚合
        aggregated_model = self.secure_aggregator.secure_aggregate(
            client_updates,
            strategy=AggregationStrategy.SECURE_AGG
        )
        
        # Step 4: 更新全局模型
        self.global_model = aggregated_model
        
        # Step 5: 计算收敛指标
        avg_loss = statistics.mean([u.training_loss for u in client_updates])
        convergence = self._calculate_convergence(round_number)
        
        # Step 6: 记录轮次
        round_result = FederatedRound(
            round_id=str(uuid.uuid4()),
            round_number=round_number,
            participating_clients=len(selected_clients),
            aggregated_model=aggregated_model,
            global_loss=avg_loss,
            convergence_metric=convergence
        )
        
        self.round_history.append(round_result)
        
        logger.info(
            f"Round {round_number} completed: "
            f"{len(selected_clients)} clients, loss={avg_loss:.3f}, "
            f"convergence={convergence:.4f}"
        )
        
        return round_result
    
    def run_federated_learning(self) -> Dict:
        """
        运行完整的联邦学习过程
        
        Returns:
            训练结果
        """
        logger.info(f"Starting federated learning: {self.num_rounds} rounds")
        
        # 初始化全局模型
        if not self.global_model:
            self.global_model = {
                f"param_{i}": random.gauss(0, 0.1)
                for i in range(10)
            }
        
        results = {
            "total_rounds": self.num_rounds,
            "final_loss": None,
            "convergence_history": [],
            "privacy_status": None
        }
        
        for round_num in range(1, self.num_rounds + 1):
            round_result = self.execute_federated_round(round_num)
            
            results["convergence_history"].append({
                "round": round_num,
                "loss": round_result.global_loss,
                "convergence": round_result.convergence_metric
            })
            
            # 检查是否收敛
            if round_result.convergence_metric < 0.001:
                logger.info(f"Converged at round {round_num}")
                break
        
        results["final_loss"] = self.round_history[-1].global_loss if self.round_history else None
        results["privacy_status"] = self.dp_engine.get_privacy_status()
        
        logger.info(f"Federated learning completed: final_loss={results['final_loss']}")
        
        return results
    
    def _calculate_convergence(self, current_round: int) -> float:
        """计算收敛指标"""
        if len(self.round_history) < 2:
            return 1.0
        
        # 计算最近几轮损失的 change
        recent_losses = [r.global_loss for r in self.round_history[-5:]]
        
        if len(recent_losses) < 2:
            return 1.0
        
        # 计算损失变化的标准差
        loss_changes = [
            abs(recent_losses[i] - recent_losses[i-1])
            for i in range(1, len(recent_losses))
        ]
        
        if not loss_changes:
            return 1.0
        
        avg_change = statistics.mean(loss_changes)
        
        # 归一化到 0-1
        return min(1.0, avg_change / 0.1)


class EdgeComputingManager:
    """边缘计算管理器
    
    管理边缘节点的部署和调度
    """
    
    def __init__(self):
        self.edge_nodes: Dict[str, EdgeNode] = {}
        self.deployment_history: List[Dict] = []
    
    def register_edge_node(self, node: EdgeNode):
        """注册边缘节点"""
        self.edge_nodes[node.node_id] = node
        logger.info(f"Edge node registered: {node.node_id} at {node.location}")
    
    def select_optimal_nodes(
        self,
        required_capacity: float,
        num_nodes: int = 3
    ) -> List[EdgeNode]:
        """
        选择最优边缘节点
        
        Args:
            required_capacity: 所需计算能力
            num_nodes: 需要选择的节点数
            
        Returns:
            选中的节点列表
        """
        # 过滤可用节点
        available_nodes = [
            node for node in self.edge_nodes.values()
            if node.available and node.compute_capacity >= required_capacity
        ]
        
        if not available_nodes:
            logger.warning("No suitable edge nodes available")
            return []
        
        # 按负载排序（选择负载最低的）
        available_nodes.sort(key=lambda n: n.current_load)
        
        selected = available_nodes[:num_nodes]
        
        logger.info(f"Selected {len(selected)} edge nodes for deployment")
        
        return selected
    
    def get_edge_analytics(self) -> Dict:
        """获取边缘计算分析"""
        if not self.edge_nodes:
            return {"error": "No edge nodes registered"}
        
        capacities = [n.compute_capacity for n in self.edge_nodes.values()]
        loads = [n.current_load for n in self.edge_nodes.values()]
        
        return {
            "total_nodes": len(self.edge_nodes),
            "available_nodes": sum(1 for n in self.edge_nodes.values() if n.available),
            "avg_capacity": round(statistics.mean(capacities), 2),
            "avg_load": round(statistics.mean(loads), 2),
            "locations": list(set(n.location for n in self.edge_nodes.values()))
        }


def create_federated_learning_system() -> Tuple[FederatedLearningCoordinator, EdgeComputingManager]:
    """工厂函数：创建联邦学习系统"""
    coordinator = FederatedLearningCoordinator(
        num_rounds=10,
        min_clients=2,
        fraction_fit=0.3
    )
    
    edge_manager = EdgeComputingManager()
    
    return coordinator, edge_manager


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Federated Learning & Privacy 测试")
    print("="*60)
    
    coordinator, edge_manager = create_federated_learning_system()
    
    # 注册客户端
    print("\n👥 注册客户端...")
    for i in range(10):
        coordinator.register_client(f"client_{i}", {"device_type": "mobile"})
    
    print(f"   已注册 {len(coordinator.clients)} 个客户端")
    
    # 注册边缘节点
    print("\n🌐 注册边缘节点...")
    locations = ["Beijing", "Shanghai", "Guangzhou", "Shenzhen"]
    
    for i, location in enumerate(locations):
        node = EdgeNode(
            node_id=f"edge_{i}",
            location=location,
            compute_capacity=random.uniform(0.5, 1.0),
            bandwidth=random.uniform(50, 200),
            current_load=random.uniform(0.1, 0.5)
        )
        edge_manager.register_edge_node(node)
    
    print(f"   已注册 {len(edge_manager.edge_nodes)} 个边缘节点")
    
    # 运行联邦学习
    print("\n🔄 运行联邦学习...")
    results = coordinator.run_federated_learning()
    
    print(f"\n📊 训练结果:")
    print(f"   总轮次: {results['total_rounds']}")
    print(f"   最终损失: {results['final_loss']:.4f}")
    print(f"   收敛历史长度: {len(results['convergence_history'])}")
    
    # 隐私状态
    print(f"\n🔒 隐私保护状态:")
    privacy = results['privacy_status']
    print(f"   总预算: {privacy['total_budget']:.2f}")
    print(f"   已使用: {privacy['spent_budget']:.2f}")
    print(f"   剩余: {privacy['remaining_budget']:.2f}")
    print(f"   使用率: {privacy['budget_utilization']:.1f}%")
    
    # 边缘节点分析
    print(f"\n🌍 边缘计算分析:")
    analytics = edge_manager.get_edge_analytics()
    print(f"   总节点数: {analytics['total_nodes']}")
    print(f"   可用节点: {analytics['available_nodes']}")
    print(f"   平均容量: {analytics['avg_capacity']:.2f}")
    print(f"   平均负载: {analytics['avg_load']:.2f}")
    print(f"   位置分布: {', '.join(analytics['locations'])}")
    
    # 选择最优节点
    print(f"\n🎯 选择最优节点...")
    optimal_nodes = edge_manager.select_optimal_nodes(required_capacity=0.6, num_nodes=2)
    print(f"   选中 {len(optimal_nodes)} 个节点:")
    for node in optimal_nodes:
        print(f"     - {node.node_id} ({node.location}): capacity={node.compute_capacity:.2f}, load={node.current_load:.2f}")
    
    print("\n✅ 测试完成！")
