#!/usr/bin/env python3
"""
AI Agent Neuromorphic Computing & Spiking Neural Networks System - AI Agent 类脑计算与脉冲神经网络系统

脉冲神经元、事件驱动处理、时空编码、STDP学习规则、神经形态架构
实现生产级 AI Agent 的类脑计算能力

参考社区最佳实践:
- Spiking Neural Networks (SNNs) - third generation neural networks
- Event-driven processing - asynchronous spike-based computation
- Spike-Timing-Dependent Plasticity (STDP) - biological learning rule
- Temporal coding - information encoded in spike timing
- Neuromorphic architectures - brain-inspired hardware/software co-design
- Energy efficiency - sparse activity, low-power operation
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


class NeuronType(Enum):
    """神经元类型"""
    LEAKY_INTEGRATE_AND_FIRE = "LIF"  # 漏积分发放神经元
    INTEGRATE_AND_FIRE = "IF"  # 积分发放神经元
    HODGKIN_HUXLEY = "HH"  # Hodgkin-Huxley模型
    IZHIKEVICH = "Izhikevich"  # Izhikevich模型


class SynapseType(Enum):
    """突触类型"""
    EXCITATORY = "excitatory"  # 兴奋性突触
    INHIBITORY = "inhibitory"  # 抑制性突触


class EncodingScheme(Enum):
    """编码方案"""
    RATE_CODING = "rate"  # 频率编码
    TEMPORAL_CODING = "temporal"  # 时间编码
    POPULATION_CODING = "population"  # 群体编码
    LATENCY_CODING = "latency"  # 延迟编码


@dataclass
class Spike:
    """脉冲（事件）"""
    spike_id: str
    neuron_id: str
    timestamp: float
    amplitude: float = 1.0
    
    def __post_init__(self):
        if not self.spike_id:
            self.spike_id = str(uuid.uuid4())


@dataclass
class Neuron:
    """脉冲神经元"""
    neuron_id: str
    neuron_type: NeuronType = NeuronType.LEAKY_INTEGRATE_AND_FIRE
    membrane_potential: float = 0.0  # 膜电位
    threshold: float = 1.0  # 发放阈值
    reset_potential: float = 0.0  # 复位电位
    leak_rate: float = 0.1  # 泄漏率（LIF模型）
    refractory_period: int = 5  # 不应期（时间步）
    last_spike_time: int = -100  # 上次发放时间
    spike_train: List[Spike] = field(default_factory=list)  # 脉冲序列
    
    def __post_init__(self):
        if not self.neuron_id:
            self.neuron_id = str(uuid.uuid4())
    
    def integrate(self, input_current: float, dt: float = 1.0):
        """积分输入电流（LIF模型）"""
        if self.neuron_type == NeuronType.LEAKY_INTEGRATE_AND_FIRE:
            # dV/dt = -(V - V_rest)/tau + I/C
            dv = -self.leak_rate * (self.membrane_potential - self.reset_potential) + input_current * dt
            self.membrane_potential += dv
        elif self.neuron_type == NeuronType.INTEGRATE_AND_FIRE:
            # 简单积分
            self.membrane_potential += input_current * dt
    
    def check_and_fire(self, current_time: int) -> Optional[Spike]:
        """检查是否发放脉冲"""
        # 检查不应期
        if current_time - self.last_spike_time < self.refractory_period:
            return None
        
        # 检查是否超过阈值
        if self.membrane_potential >= self.threshold:
            # 发放脉冲
            spike = Spike(
                spike_id="",
                neuron_id=self.neuron_id,
                timestamp=float(current_time),
                amplitude=1.0
            )
            
            self.spike_train.append(spike)
            self.last_spike_time = current_time
            
            # 重置膜电位
            self.membrane_potential = self.reset_potential
            
            return spike
        
        return None
    
    @property
    def firing_rate(self) -> float:
        """计算发放率（Hz）"""
        if not self.spike_train:
            return 0.0
        
        if len(self.spike_train) < 2:
            return 0.0
        
        # 计算平均发放间隔
        intervals = [
            self.spike_train[i+1].timestamp - self.spike_train[i].timestamp
            for i in range(len(self.spike_train) - 1)
        ]
        
        avg_interval = statistics.mean(intervals)
        
        return 1.0 / avg_interval if avg_interval > 0 else 0.0


@dataclass
class Synapse:
    """突触连接"""
    synapse_id: str
    pre_neuron_id: str
    post_neuron_id: str
    weight: float = 0.5  # 突触权重
    delay: int = 1  # 传导延迟（时间步）
    synapse_type: SynapseType = SynapseType.EXCITATORY
    plasticity_enabled: bool = True  # 是否启用可塑性
    eligibility_trace: float = 0.0  # 资格迹（用于STDP）
    
    def __post_init__(self):
        if not self.synapse_id:
            self.synapse_id = str(uuid.uuid4())
    
    def transmit_spike(self, pre_spike: Spike) -> float:
        """传递脉冲到后神经元"""
        # 考虑突触类型
        effective_weight = self.weight if self.synapse_type == SynapseType.EXCITATORY else -self.weight
        
        return effective_weight * pre_spike.amplitude


@dataclass
class SNNLayer:
    """SNN层"""
    layer_id: str
    num_neurons: int
    neurons: List[Neuron] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.layer_id:
            self.layer_id = str(uuid.uuid4())
        
        # 初始化神经元
        for i in range(self.num_neurons):
            neuron = Neuron(neuron_id=f"{self.layer_id}_neuron_{i}")
            self.neurons.append(neuron)


class SpikingNeuralNetwork:
    """脉冲神经网络
    
    第三代神经网络，基于事件驱动的异步计算
    """
    
    def __init__(self, architecture: List[int] = None):
        """
        初始化SNN
        
        Args:
            architecture: 网络架构 [输入层大小, 隐藏层大小, 输出层大小]
        """
        if architecture is None:
            architecture = [10, 20, 5]
        
        self.architecture = architecture
        self.layers: List[SNNLayer] = []
        self.synapses: Dict[Tuple[str, str], Synapse] = {}
        self.spike_history: List[Spike] = []
        self.training_history: List[Dict] = []
        
        # 构建网络
        self._build_network()
        self._initialize_synapses()
    
    def _build_network(self):
        """构建网络层"""
        for i, num_neurons in enumerate(self.architecture):
            layer = SNNLayer(layer_id=f"layer_{i}", num_neurons=num_neurons)
            self.layers.append(layer)
    
    def _initialize_synapses(self):
        """初始化突触连接（全连接）"""
        for layer_idx in range(len(self.layers) - 1):
            pre_layer = self.layers[layer_idx]
            post_layer = self.layers[layer_idx + 1]
            
            for pre_neuron in pre_layer.neurons:
                for post_neuron in post_layer.neurons:
                    synapse = Synapse(
                        synapse_id="",
                        pre_neuron_id=pre_neuron.neuron_id,
                        post_neuron_id=post_neuron.neuron_id,
                        weight=random.gauss(0.5, 0.1)  # 高斯初始化
                    )
                    self.synapses[(pre_neuron.neuron_id, post_neuron.neuron_id)] = synapse
    
    def encode_input(self, input_data: List[float], encoding: EncodingScheme = EncodingScheme.RATE_CODING) -> Dict[str, List[int]]:
        """
        编码输入数据为脉冲序列
        
        Args:
            input_data: 输入数据
            encoding: 编码方案
            
        Returns:
            {neuron_id: [spike_times]}
        """
        spike_times = {}
        
        if encoding == EncodingScheme.RATE_CODING:
            # 频率编码：值越大，发放率越高
            for i, value in enumerate(input_data):
                if i < len(self.layers[0].neurons):
                    neuron = self.layers[0].neurons[i]
                    # 根据输入值生成脉冲序列
                    num_spikes = int(value * 10)  # 简化：值*10个脉冲
                    times = sorted(random.sample(range(100), min(num_spikes, 100)))
                    spike_times[neuron.neuron_id] = times
        
        elif encoding == EncodingScheme.TEMPORAL_CODING:
            # 时间编码：值越大，首次发放时间越早
            for i, value in enumerate(input_data):
                if i < len(self.layers[0].neurons):
                    neuron = self.layers[0].neurons[i]
                    # 延迟与值成反比
                    first_spike_time = int((1.0 - value) * 50)
                    spike_times[neuron.neuron_id] = [first_spike_time]
        
        return spike_times
    
    def simulate_step(self, current_time: int, input_spikes: Dict[str, List[int]] = None):
        """
        模拟一个时间步
        
        Args:
            current_time: 当前时间步
            input_spikes: 输入脉冲 {neuron_id: spike_times}
        """
        # Step 1: 注入输入电流到输入层
        if input_spikes and current_time in input_spikes.get(self.layers[0].neurons[0].neuron_id, []):
            for neuron in self.layers[0].neurons:
                if neuron.neuron_id in input_spikes:
                    if current_time in input_spikes[neuron.neuron_id]:
                        neuron.membrane_potential += 1.0
        
        # Step 2: 逐层传播
        for layer_idx in range(len(self.layers)):
            layer = self.layers[layer_idx]
            
            for neuron in layer.neurons:
                # 收集来自前层的输入
                if layer_idx > 0:
                    pre_layer = self.layers[layer_idx - 1]
                    total_input = 0.0
                    
                    for pre_neuron in pre_layer.neurons:
                        synapse_key = (pre_neuron.neuron_id, neuron.neuron_id)
                        if synapse_key in self.synapses:
                            synapse = self.synapses[synapse_key]
                            
                            # 检查前神经元是否在适当时间发放
                            if pre_neuron.last_spike_time == current_time - synapse.delay:
                                # 创建虚拟脉冲用于传递
                                virtual_spike = Spike(
                                    spike_id="",
                                    neuron_id=pre_neuron.neuron_id,
                                    timestamp=float(current_time - synapse.delay)
                                )
                                total_input += synapse.transmit_spike(virtual_spike)
                    
                    neuron.integrate(total_input)
                
                # Step 3: 检查并发放脉冲
                spike = neuron.check_and_fire(current_time)
                
                if spike:
                    self.spike_history.append(spike)
    
    def run_simulation(self, input_data: List[float], num_steps: int = 100, 
                      encoding: EncodingScheme = EncodingScheme.RATE_CODING) -> Dict[str, Any]:
        """
        运行完整模拟
        
        Args:
            input_data: 输入数据
            num_steps: 模拟步数
            encoding: 编码方案
            
        Returns:
            模拟结果
        """
        # 编码输入
        input_spikes = self.encode_input(input_data, encoding)
        
        # 运行模拟
        for t in range(num_steps):
            self.simulate_step(t, input_spikes)
        
        # 收集输出层结果
        output_layer = self.layers[-1]
        output_rates = [neuron.firing_rate for neuron in output_layer.neurons]
        
        result = {
            "num_steps": num_steps,
            "total_spikes": len(self.spike_history),
            "output_firing_rates": output_rates,
            "predicted_class": output_rates.index(max(output_rates)) if output_rates else -1,
            "energy_efficiency": self._calculate_energy_efficiency(num_steps)
        }
        
        logger.info(f"SNN simulation completed: {result['total_spikes']} spikes, energy={result['energy_efficiency']:.2f}%")
        
        return result
    
    def train_stdp(self, training_data: List[Tuple[List[float], int]], epochs: int = 10):
        """
        使用STDP规则训练
        
        Args:
            training_data: 训练数据 [(input, label), ...]
            epochs: 训练轮数
        """
        for epoch in range(epochs):
            epoch_loss = 0.0
            
            for input_data, label in training_data:
                # 前向传播
                result = self.run_simulation(input_data, num_steps=100)
                
                # 计算损失（简化）
                predicted = result['predicted_class']
                loss = 1.0 if predicted != label else 0.0
                epoch_loss += loss
                
                # STDP更新
                self._apply_stdp_update(label)
            
            avg_loss = epoch_loss / len(training_data)
            self.training_history.append({
                "epoch": epoch + 1,
                "loss": avg_loss,
                "accuracy": 1.0 - avg_loss
            })
            
            logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}, Accuracy: {1-avg_loss:.4f}")
    
    def _apply_stdp_update(self, target_label: int):
        """应用STDP（脉冲时序依赖可塑性）更新"""
        # STDP规则：
        # 如果前神经元在后神经元之前发放 -> LTP（长时程增强）
        # 如果前神经元在后神经元之后发放 -> LTD（长时程抑制）
        
        for synapse_key, synapse in self.synapses.items():
            pre_id, post_id = synapse_key
            
            # 查找前后神经元的发放时间
            pre_neuron = self._find_neuron(pre_id)
            post_neuron = self._find_neuron(post_id)
            
            if not pre_neuron or not post_neuron:
                continue
            
            # 简化STDP实现
            if pre_neuron.last_spike_time < post_neuron.last_spike_time:
                # LTP：增强权重
                delta_w = 0.01 * math.exp(-(post_neuron.last_spike_time - pre_neuron.last_spike_time) / 20)
                synapse.weight = min(1.0, synapse.weight + delta_w)
            elif pre_neuron.last_spike_time > post_neuron.last_spike_time:
                # LTD：减弱权重
                delta_w = -0.01 * math.exp(-(pre_neuron.last_spike_time - post_neuron.last_spike_time) / 20)
                synapse.weight = max(0.0, synapse.weight + delta_w)
    
    def _find_neuron(self, neuron_id: str) -> Optional[Neuron]:
        """查找神经元"""
        for layer in self.layers:
            for neuron in layer.neurons:
                if neuron.neuron_id == neuron_id:
                    return neuron
        return None
    
    def _calculate_energy_efficiency(self, num_steps: int) -> float:
        """计算能量效率（稀疏度）"""
        total_possible_spikes = len(self.spike_history) + (num_steps * sum(len(layer.neurons) for layer in self.layers))
        
        if total_possible_spikes == 0:
            return 0.0
        
        sparsity = 1.0 - (len(self.spike_history) / total_possible_spikes)
        
        return sparsity * 100  # 百分比
    
    def get_network_stats(self) -> Dict[str, Any]:
        """获取网络统计信息"""
        total_neurons = sum(len(layer.neurons) for layer in self.layers)
        total_synapses = len(self.synapses)
        total_spikes = len(self.spike_history)
        
        avg_weights = statistics.mean([s.weight for s in self.synapses.values()]) if self.synapses else 0.0
        
        return {
            "architecture": self.architecture,
            "total_neurons": total_neurons,
            "total_synapses": total_synapses,
            "total_spikes": total_spikes,
            "avg_synaptic_weight": round(avg_weights, 4),
            "network_depth": len(self.layers)
        }


class EventDrivenProcessor:
    """事件驱动处理器
    
    异步处理脉冲事件
    """
    
    def __init__(self):
        self.event_queue: List[Dict] = []
        self.processed_events: int = 0
        self.processing_log: List[Dict] = []
    
    def enqueue_event(self, event_type: str, data: Dict, priority: int = 0):
        """将事件加入队列"""
        event = {
            "event_id": str(uuid.uuid4()),
            "type": event_type,
            "data": data,
            "priority": priority,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "processed": False
        }
        
        self.event_queue.append(event)
        
        # 按优先级排序
        self.event_queue.sort(key=lambda x: x["priority"], reverse=True)
    
    def process_events(self, max_events: int = None) -> List[Dict]:
        """处理事件"""
        if max_events is None:
            max_events = len(self.event_queue)
        
        processed = []
        
        for _ in range(min(max_events, len(self.event_queue))):
            if not self.event_queue:
                break
            
            event = self.event_queue.pop(0)
            event["processed"] = True
            event["processing_time"] = datetime.now(timezone.utc).isoformat()
            
            processed.append(event)
            self.processed_events += 1
            
            # 记录处理日志
            self.processing_log.append({
                "event_id": event["event_id"],
                "type": event["type"],
                "processed_at": event["processing_time"]
            })
        
        logger.info(f"Processed {len(processed)} events")
        
        return processed
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计"""
        return {
            "total_processed": self.processed_events,
            "queue_size": len(self.event_queue),
            "event_types": list(set(log["type"] for log in self.processing_log))
        }


def create_neuromorphic_system() -> Tuple[SpikingNeuralNetwork, EventDrivenProcessor]:
    """工厂函数：创建类脑计算系统"""
    snn = SpikingNeuralNetwork(architecture=[10, 20, 5])
    processor = EventDrivenProcessor()
    
    return snn, processor


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Neuromorphic Computing & SNN 测试")
    print("="*60)
    
    snn, processor = create_neuromorphic_system()
    
    # 网络统计
    print("\n🧠 网络统计...")
    stats = snn.get_network_stats()
    print(f"   网络架构: {stats['architecture']}")
    print(f"   总神经元数: {stats['total_neurons']}")
    print(f"   总突触数: {stats['total_synapses']}")
    print(f"   网络深度: {stats['network_depth']}")
    
    # 运行SNN模拟（频率编码）
    print("\n⚡ 运行SNN模拟（频率编码）...")
    test_input = [0.8, 0.6, 0.9, 0.3, 0.7, 0.5, 0.4, 0.8, 0.2, 0.6]
    result_rate = snn.run_simulation(
        input_data=test_input,
        num_steps=100,
        encoding=EncodingScheme.RATE_CODING
    )
    print(f"   编码方案: Rate Coding")
    print(f"   模拟步数: {result_rate['num_steps']}")
    print(f"   总脉冲数: {result_rate['total_spikes']}")
    print(f"   输出发放率: {[f'{r:.2f}' for r in result_rate['output_firing_rates']]}")
    print(f"   预测类别: {result_rate['predicted_class']}")
    print(f"   能量效率: {result_rate['energy_efficiency']:.2f}%")
    
    # 运行SNN模拟（时间编码）
    print("\n⏱️  运行SNN模拟（时间编码）...")
    result_temporal = snn.run_simulation(
        input_data=test_input,
        num_steps=100,
        encoding=EncodingScheme.TEMPORAL_CODING
    )
    print(f"   编码方案: Temporal Coding")
    print(f"   总脉冲数: {result_temporal['total_spikes']}")
    print(f"   输出发放率: {[f'{r:.2f}' for r in result_temporal['output_firing_rates']]}")
    print(f"   预测类别: {result_temporal['predicted_class']}")
    print(f"   能量效率: {result_temporal['energy_efficiency']:.2f}%")
    
    # STDP训练
    print("\n🎓 运行STDP训练...")
    training_data = [
        ([0.9, 0.8, 0.7, 0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.2], 0),
        ([0.1, 0.2, 0.1, 0.8, 0.9, 0.7, 0.8, 0.9, 0.8, 0.7], 1),
        ([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], 2)
    ]
    
    snn.train_stdp(training_data=training_data, epochs=3)
    
    if snn.training_history:
        last_epoch = snn.training_history[-1]
        print(f"\n   最终训练结果:")
        print(f"     轮次: {last_epoch['epoch']}")
        print(f"     损失: {last_epoch['loss']:.4f}")
        print(f"     准确率: {last_epoch['accuracy']:.4f}")
    
    # 事件驱动处理
    print("\n📨 测试事件驱动处理...")
    processor.enqueue_event("spike", {"neuron_id": "n1", "time": 10}, priority=2)
    processor.enqueue_event("spike", {"neuron_id": "n2", "time": 15}, priority=1)
    processor.enqueue_event("synaptic_update", {"synapse_id": "s1"}, priority=3)
    
    processed = processor.process_events(max_events=2)
    print(f"   入队事件数: 3")
    print(f"   处理事件数: {len(processed)}")
    print(f"   剩余队列大小: {processor.event_queue.__len__() if hasattr(processor.event_queue, '__len__') else len(processor.event_queue)}")
    
    proc_stats = processor.get_processing_stats()
    print(f"\n   处理统计:")
    print(f"     总处理数: {proc_stats['total_processed']}")
    print(f"     事件类型: {', '.join(proc_stats['event_types'])}")
    
    # 突触权重分布
    print("\n🔗 突触权重统计...")
    weights = [s.weight for s in snn.synapses.values()]
    print(f"   平均权重: {statistics.mean(weights):.4f}")
    print(f"   最小权重: {min(weights):.4f}")
    print(f"   最大权重: {max(weights):.4f}")
    print(f"   权重标准差: {statistics.stdev(weights):.4f}")
    
    # 脉冲历史
    print("\n📊 脉冲历史统计...")
    print(f"   总脉冲数: {len(snn.spike_history)}")
    
    if snn.spike_history:
        spike_times = [s.timestamp for s in snn.spike_history[:10]]
        print(f"   前10个脉冲时间: {[f'{t:.0f}' for t in spike_times]}")
    
    print("\n✅ 测试完成！")
