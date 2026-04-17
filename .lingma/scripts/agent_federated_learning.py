#!/usr/bin/env python3
"""
AI Agent Federated Learning & Privacy-Preserving ML System - AI Agent 联邦学习与隐私保护机器学习系统

联邦平均、差分隐私、安全聚合、同态加密、边缘计算
实现生产级 AI Agent 的隐私保护学习能力

参考社区最佳实践:
- Federated Learning - train models across decentralized devices without sharing data
- Differential Privacy (DP) - add noise to protect individual privacy
- Secure Aggregation - cryptographic protocols for private model updates
- Homomorphic Encryption - compute on encrypted data
- Edge Computing - process data at the edge, not in central servers
- FedAvg algorithm - federated averaging for global model updates
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


class AggregationMethod(Enum):
    """聚合方法"""
    FEDERATED_AVERAGING = "FedAvg"  # 联邦平均
    SECURE_AGGREGATION = "secure_agg"  # 安全聚合
    HOMOMORPHIC_ENCRYPTION = "homomorphic"  # 同态加密
    DIFFERENTIAL_PRIVACY = "differential_privacy"  # 差分隐私


class PrivacyMechanism(Enum):
    """隐私保护机制"""
    LOCAL_DP = "local_dp"  # 本地差分隐私
    CENTRAL_DP = "central_dp"  # 中心差分隐私
    SECURE_MPC = "secure_mpc"  # 安全多方计算
    HOMOMORPHIC_ENC = "homomorphic_enc"  # 同态加密


@dataclass
class ClientNode:
    """客户端节点（边缘设备）"""
    client_id: str
    data_size: int = 0
    local_model: Dict[str, float] = field(default_factory=dict)
    training_history: List[Dict] = field(default_factory=list)
    is_active: bool = True
    
    def __post_init__(self):
        if not self.client_id:
            self.client_id = str(uuid.uuid4())
    
    def local_train(self, global_model: Dict[str, float], epochs: int = 5) -> Dict[str, float]:
        """
        本地训练
        
        Args:
            global_model: 全局模型参数
            epochs: 本地训练轮数
            
        Returns:
            模型更新
        """
        # 初始化本地模型
        if not self.local_model:
            self.local_model = {k: v + random.gauss(0, 0.1) for k, v in global_model.items()}
        
        # 模拟本地训练（简化）
        model_update = {}
        for param_name in global_model:
            # 本地梯度下降（模拟）
            gradient = random.gauss(0, 0.01) * self.data_size / 1000
            self.local_model[param_name] -= 0.01 * gradient
            model_update[param_name] = self.local_model[param_name] - global_model[param_name]
        
        # 记录训练历史
        self.training_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "epochs": epochs,
            "data_size": self.data_size,
            "num_params": len(model_update)
        })
        
        logger.debug(f"Client {self.client_id} trained: {len(model_update)} params updated")
        
        return model_update


@dataclass
class GlobalModel:
    """全局模型"""
    model_id: str
    parameters: Dict[str, float] = field(default_factory=dict)
    version: int = 0
    training_rounds: int = 0
    
    def __post_init__(self):
        if not self.model_id:
            self.model_id = str(uuid.uuid4())
    
    def update_parameters(self, aggregated_params: Dict[str, float]):
        """更新模型参数"""
        self.parameters = aggregated_params.copy()
        self.version += 1
        self.training_rounds += 1


@dataclass
class PrivacyBudget:
    """隐私预算（ε, δ）- 差分隐私"""
    epsilon: float = 1.0  # 隐私损失参数（越小越隐私）
    delta: float = 1e-5  # 失败概率
    spent_epsilon: float = 0.0  # 已消耗隐私预算
    
    @property
    def remaining_budget(self) -> float:
        """剩余隐私预算"""
        return max(0, self.epsilon - self.spent_epsilon)
    
    def spend_budget(self, epsilon_spent: float):
        """消耗隐私预算"""
        self.spent_epsilon += epsilon_spent
        
        if self.spent_epsilon > self.epsilon:
            logger.warning(f"Privacy budget exceeded! Spent: {self.spent_epsilon:.2f}, Budget: {self.epsilon}")


class DifferentialPrivacy:
    """差分隐私
    
    通过添加噪声保护个体隐私
    """
    
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5, sensitivity: float = 1.0):
        self.privacy_budget = PrivacyBudget(epsilon=epsilon, delta=delta)
        self.sensitivity = sensitivity  # 敏感度
        self.noise_history: List[Dict] = []
    
    def add_gaussian_noise(self, value: float) -> float:
        """
        添加高斯噪声
        
        σ = Δf * sqrt(2 * ln(1.25/δ)) / ε
        
        Args:
            value: 原始值
            
        Returns:
            加噪后的值
        """
        if self.privacy_budget.remaining_budget <= 0:
            logger.error("Privacy budget exhausted!")
            return value
        
        # 计算噪声标准差
        sigma = self.sensitivity * math.sqrt(2 * math.log(1.25 / self.privacy_budget.delta)) / self.privacy_budget.epsilon
        
        # 添加噪声
        noise = random.gauss(0, sigma)
        noisy_value = value + noise
        
        # 记录噪声
        self.noise_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "original_value": value,
            "noise_added": noise,
            "noisy_value": noisy_value,
            "sigma": sigma,
            "epsilon_spent": self.privacy_budget.epsilon / 10  # 简化：每次消耗1/10预算
        })
        
        # 消耗隐私预算
        self.privacy_budget.spend_budget(self.privacy_budget.epsilon / 10)
        
        return noisy_value
    
    def add_laplace_noise(self, value: float) -> float:
        """
        添加拉普拉斯噪声
        
        b = Δf / ε
        
        Args:
            value: 原始值
            
        Returns:
            加噪后的值
        """
        if self.privacy_budget.remaining_budget <= 0:
            return value
        
        # 计算尺度参数
        b = self.sensitivity / self.privacy_budget.epsilon
        
        # 添加拉普拉斯噪声
        noise = random.lapvariate(0, b)
        noisy_value = value + noise
        
        # 消耗预算
        self.privacy_budget.spend_budget(self.privacy_budget.epsilon / 10)
        
        return noisy_value
    
    def clip_gradient(self, gradient: float, max_norm: float = 1.0) -> float:
        """梯度裁剪（限制敏感度）"""
        return max(-max_norm, min(max_norm, gradient))


class SecureAggregator:
    """安全聚合器
    
    使用密码学协议保护模型更新隐私
    """
    
    def __init__(self, method: AggregationMethod = AggregationMethod.FEDERATED_AVERAGING):
        self.method = method
        self.aggregation_history: List[Dict] = []
        self.dp_mechanism = DifferentialPrivacy(epsilon=1.0)
    
    def federated_average(
        self,
        client_updates: List[Dict[str, Any]],
        total_data_size: int
    ) -> Dict[str, float]:
        """
        联邦平均算法 (FedAvg)
        
        w^{t+1} = Σ (n_k / n) * w_k^{t+1}
        
        Args:
            client_updates: 客户端更新列表 [{client_id, update, data_size}]
            total_data_size: 总数据量
            
        Returns:
            聚合后的模型参数
        """
        if not client_updates:
            return {}
        
        aggregated_params = {}
        
        # 获取所有参数名
        param_names = list(client_updates[0]["update"].keys())
        
        for param_name in param_names:
            weighted_sum = 0.0
            
            for update in client_updates:
                client_weight = update["data_size"] / total_data_size
                param_value = update["update"][param_name]
                
                # 可选：应用差分隐私
                if self.method == AggregationMethod.DIFFERENTIAL_PRIVACY:
                    param_value = self.dp_mechanism.add_gaussian_noise(param_value)
                
                weighted_sum += client_weight * param_value
            
            aggregated_params[param_name] = weighted_sum
        
        # 记录聚合历史
        self.aggregation_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": self.method.value,
            "num_clients": len(client_updates),
            "total_data_size": total_data_size,
            "num_params": len(aggregated_params)
        })
        
        logger.info(f"Federated averaging completed: {len(client_updates)} clients, {len(aggregated_params)} params")
        
        return aggregated_params
    
    def secure_aggregate_with_encryption(
        self,
        client_updates: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        带加密的安全聚合（模拟同态加密）
        
        Args:
            client_updates: 客户端更新列表
            
        Returns:
            聚合后的模型参数
        """
        if not client_updates:
            return {}
        
        # 模拟同态加密聚合
        aggregated_params = {}
        param_names = list(client_updates[0]["update"].keys())
        
        for param_name in param_names:
            # 在"加密域"中求和（简化：直接相加）
            encrypted_sum = sum(update["update"][param_name] for update in client_updates)
            
            # "解密"得到平均值
            aggregated_params[param_name] = encrypted_sum / len(client_updates)
        
        logger.info(f"Secure aggregation with encryption: {len(client_updates)} clients")
        
        return aggregated_params


class FederatedLearningServer:
    """联邦学习服务器
    
    协调客户端训练和模型聚合
    """
    
    def __init__(
        self,
        num_clients: int = 10,
        aggregation_method: AggregationMethod = AggregationMethod.FEDERATED_AVERAGING,
        client_fraction: float = 0.2
    ):
        self.num_clients = num_clients
        self.aggregation_method = aggregation_method
        self.client_fraction = client_fraction  # 每轮参与客户端比例
        
        # 初始化全局模型
        self.global_model = GlobalModel(
            model_id="",
            parameters={f"param_{i}": random.gauss(0, 0.1) for i in range(50)},
            version=0
        )
        
        # 初始化客户端
        self.clients: Dict[str, ClientNode] = {}
        for i in range(num_clients):
            client = ClientNode(
                client_id=f"client_{i}",
                data_size=random.randint(100, 1000)
            )
            self.clients[client.client_id] = client
        
        # 聚合器
        self.aggregator = SecureAggregator(method=aggregation_method)
        
        # 训练历史
        self.training_history: List[Dict] = []
    
    def select_clients(self, round_num: int) -> List[ClientNode]:
        """选择参与本轮训练的客户端"""
        num_selected = max(1, int(self.num_clients * self.client_fraction))
        active_clients = [c for c in self.clients.values() if c.is_active]
        
        selected = random.sample(active_clients, min(num_selected, len(active_clients)))
        
        logger.info(f"Round {round_num}: Selected {len(selected)}/{len(active_clients)} clients")
        
        return selected
    
    def train_round(self, round_num: int, local_epochs: int = 5) -> Dict[str, Any]:
        """
        执行一轮联邦学习训练
        
        Args:
            round_num: 轮次编号
            local_epochs: 本地训练轮数
            
        Returns:
            训练结果
        """
        # Step 1: 选择客户端
        selected_clients = self.select_clients(round_num)
        
        # Step 2: 客户端本地训练
        client_updates = []
        total_data_size = 0
        
        for client in selected_clients:
            # 本地训练
            update = client.local_train(self.global_model.parameters, epochs=local_epochs)
            
            client_updates.append({
                "client_id": client.client_id,
                "update": update,
                "data_size": client.data_size
            })
            
            total_data_size += client.data_size
        
        # Step 3: 安全聚合
        if self.aggregation_method == AggregationMethod.SECURE_AGGREGATION:
            aggregated_params = self.aggregator.secure_aggregate_with_encryption(client_updates)
        else:
            aggregated_params = self.aggregator.federated_average(client_updates, total_data_size)
        
        # Step 4: 更新全局模型
        self.global_model.update_parameters(aggregated_params)
        
        # 记录训练历史
        round_result = {
            "round": round_num,
            "num_clients_participated": len(selected_clients),
            "total_data_size": total_data_size,
            "global_model_version": self.global_model.version,
            "aggregation_method": self.aggregation_method.value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.training_history.append(round_result)
        
        logger.info(f"Round {round_num} completed: model version {self.global_model.version}")
        
        return round_result
    
    def run_federated_learning(
        self,
        num_rounds: int = 10,
        local_epochs: int = 5
    ) -> Dict[str, Any]:
        """
        运行完整联邦学习过程
        
        Args:
            num_rounds: 总轮数
            local_epochs: 本地训练轮数
            
        Returns:
            最终结果
        """
        for round_num in range(1, num_rounds + 1):
            self.train_round(round_num, local_epochs)
        
        # 汇总统计
        final_stats = {
            "total_rounds": num_rounds,
            "final_model_version": self.global_model.version,
            "num_clients": self.num_clients,
            "client_fraction": self.client_fraction,
            "aggregation_method": self.aggregation_method.value,
            "total_training_rounds_recorded": len(self.training_history)
        }
        
        # 隐私预算使用情况
        if hasattr(self.aggregator.dp_mechanism, 'privacy_budget'):
            budget = self.aggregator.dp_mechanism.privacy_budget
            final_stats["privacy_budget"] = {
                "epsilon_total": budget.epsilon,
                "epsilon_spent": budget.spent_epsilon,
                "epsilon_remaining": budget.remaining_budget
            }
        
        logger.info(f"Federated learning completed: {num_rounds} rounds, version {self.global_model.version}")
        
        return final_stats
    
    def get_client_statistics(self) -> Dict[str, Any]:
        """获取客户端统计信息"""
        active_clients = sum(1 for c in self.clients.values() if c.is_active)
        total_data = sum(c.data_size for c in self.clients.values())
        avg_data = statistics.mean([c.data_size for c in self.clients.values()])
        
        return {
            "total_clients": self.num_clients,
            "active_clients": active_clients,
            "total_data_size": total_data,
            "avg_data_per_client": round(avg_data, 2)
        }


def create_federated_learning_system(
    num_clients: int = 10,
    method: AggregationMethod = AggregationMethod.FEDERATED_AVERAGING
) -> FederatedLearningServer:
    """工厂函数：创建联邦学习系统"""
    server = FederatedLearningServer(
        num_clients=num_clients,
        aggregation_method=method
    )
    return server


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Federated Learning & Privacy-Preserving ML 测试")
    print("="*60)
    
    # 测试FedAvg
    print("\n🌐 测试联邦平均 (FedAvg)...")
    fedavg_server = create_federated_learning_system(
        num_clients=10,
        method=AggregationMethod.FEDERATED_AVERAGING
    )
    
    # 运行10轮联邦学习
    result = fedavg_server.run_federated_learning(num_rounds=10, local_epochs=5)
    print(f"   总轮数: {result['total_rounds']}")
    print(f"   最终模型版本: {result['final_model_version']}")
    print(f"   客户端数: {result['num_clients']}")
    print(f"   参与比例: {result['client_fraction']*100:.0f}%")
    print(f"   聚合方法: {result['aggregation_method']}")
    
    client_stats = fedavg_server.get_client_statistics()
    print(f"\n   📊 客户端统计:")
    print(f"     活跃客户端: {client_stats['active_clients']}/{client_stats['total_clients']}")
    print(f"     总数据量: {client_stats['total_data_size']}")
    print(f"     平均每客户端: {client_stats['avg_data_per_client']}")
    
    # 测试差分隐私
    print("\n🔒 测试差分隐私...")
    dp_server = create_federated_learning_system(
        num_clients=10,
        method=AggregationMethod.DIFFERENTIAL_PRIVACY
    )
    
    dp_result = dp_server.run_federated_learning(num_rounds=5, local_epochs=3)
    print(f"   总轮数: {dp_result['total_rounds']}")
    
    if "privacy_budget" in dp_result:
        budget = dp_result["privacy_budget"]
        print(f"\n   🛡️  隐私预算:")
        print(f"     总ε: {budget['epsilon_total']}")
        print(f"     已消耗: {budget['epsilon_spent']:.4f}")
        print(f"     剩余: {budget['epsilon_remaining']:.4f}")
    
    # 测试安全聚合
    print("\n🔐 测试安全聚合...")
    secure_server = create_federated_learning_system(
        num_clients=10,
        method=AggregationMethod.SECURE_AGGREGATION
    )
    
    secure_result = secure_server.run_federated_learning(num_rounds=5, local_epochs=3)
    print(f"   总轮数: {secure_result['total_rounds']}")
    print(f"   聚合方法: {secure_result['aggregation_method']}")
    
    # 差分隐私机制测试
    print("\n⚙️  测试差分隐私机制...")
    dp_mech = DifferentialPrivacy(epsilon=1.0, delta=1e-5, sensitivity=1.0)
    
    test_values = [1.0, 2.0, 3.0, 4.0, 5.0]
    noisy_values = [dp_mech.add_gaussian_noise(v) for v in test_values]
    
    print(f"   原始值: {test_values}")
    print(f"   加噪值: {[f'{v:.2f}' for v in noisy_values]}")
    print(f"   噪声幅度: {[f'{abs(n-o):.2f}' for n, o in zip(noisy_values, test_values)]}")
    print(f"   剩余隐私预算: {dp_mech.privacy_budget.remaining_budget:.4f}")
    
    # 梯度裁剪测试
    gradients = [-2.0, -0.5, 0.0, 0.5, 2.0]
    clipped = [dp_mech.clip_gradient(g, max_norm=1.0) for g in gradients]
    print(f"\n   梯度裁剪:")
    print(f"     原始梯度: {gradients}")
    print(f"     裁剪后: {clipped}")
    
    # 训练历史
    print("\n📚 训练历史...")
    print(f"   FedAvg训练轮数: {len(fedavg_server.training_history)}")
    print(f"   DP训练轮数: {len(dp_server.training_history)}")
    print(f"   Secure训练轮数: {len(secure_server.training_history)}")
    
    if fedavg_server.training_history:
        last_round = fedavg_server.training_history[-1]
        print(f"\n   最后一轮详情:")
        print(f"     轮次: {last_round['round']}")
        print(f"     参与客户端: {last_round['num_clients_participated']}")
        print(f"     总数据量: {last_round['total_data_size']}")
    
    print("\n✅ 测试完成！")
