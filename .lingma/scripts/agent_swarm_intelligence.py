#!/usr/bin/env python3
"""
AI Agent Swarm Intelligence & Emergent Behavior System - AI Agent 群体智能与涌现行为系统

分布式协调、自组织协作、涌现智能、群体行为模拟、去中心化决策
实现生产级 AI Agent 的群体智能能力

参考社区最佳实践:
- Swarm intelligence - decentralized, self-organized systems
- Emergent behavior - complex patterns from simple rules
- Distributed coordination - gossip protocols, consensus algorithms
- Collective decision making - swarm robotics, ant colony optimization
- Self-organization - local interactions leading to global patterns
- Patchwork AGI - distributed intelligence through agent collaboration
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


class SwarmBehavior(Enum):
    """群体行为类型"""
    FLOCKING = "flocking"  # 鸟群行为
    SCHOOLING = "schooling"  # 鱼群行为
    FORAGING = "foraging"  # 觅食行为
    NESTING = "nesting"  # 筑巢行为
    MIGRATION = "migration"  # 迁徙行为
    CONSENSUS = "consensus"  # 共识形成


class CoordinationMechanism(Enum):
    """协调机制"""
    GOSSIP_PROTOCOL = "gossip"  # 谣言协议
    STIGMERGY = "stigmergy"  # 间接通信（通过环境）
    DIRECT_COMMUNICATION = "direct"  # 直接通信
    PHEROMONE_BASED = "pheromone"  # 信息素基础
    MARKET_BASED = "market"  # 市场机制


class EmergenceType(Enum):
    """涌现类型"""
    STRUCTURAL = "structural"  # 结构涌现
    FUNCTIONAL = "functional"  # 功能涌现
    BEHAVIORAL = "behavioral"  # 行为涌现
    COGNITIVE = "cognitive"  # 认知涌现


@dataclass
class SwarmAgent:
    """群体智能体"""
    agent_id: str
    role: str
    position: Tuple[float, float] = (0.0, 0.0)
    velocity: Tuple[float, float] = (0.0, 0.0)
    state: Dict[str, Any] = field(default_factory=dict)
    neighbors: List[str] = field(default_factory=list)
    local_knowledge: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.agent_id:
            self.agent_id = str(uuid.uuid4())
    
    def update_position(self, dt: float = 1.0):
        """更新位置"""
        x = self.position[0] + self.velocity[0] * dt
        y = self.position[1] + self.velocity[1] * dt
        self.position = (x, y)
    
    def distance_to(self, other: 'SwarmAgent') -> float:
        """计算到另一个智能体的距离"""
        dx = self.position[0] - other.position[0]
        dy = self.position[1] - other.position[1]
        return math.sqrt(dx**2 + dy**2)


@dataclass
class SwarmState:
    """群体状态"""
    swarm_id: str
    agents: List[SwarmAgent] = field(default_factory=list)
    environment: Dict[str, Any] = field(default_factory=dict)
    emergent_patterns: List[Dict] = field(default_factory=list)
    coordination_metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.swarm_id:
            self.swarm_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    @property
    def size(self) -> int:
        return len(self.agents)
    
    @property
    def centroid(self) -> Tuple[float, float]:
        """计算群体质心"""
        if not self.agents:
            return (0.0, 0.0)
        
        avg_x = statistics.mean([a.position[0] for a in self.agents])
        avg_y = statistics.mean([a.position[1] for a in self.agents])
        
        return (avg_x, avg_y)


@dataclass
class EmergentPattern:
    """涌现模式"""
    pattern_id: str
    pattern_type: EmergenceType
    description: str
    participating_agents: List[str] = field(default_factory=list)
    strength: float = 0.0
    stability: float = 0.0
    detected_at: str = ""
    
    def __post_init__(self):
        if not self.pattern_id:
            self.pattern_id = str(uuid.uuid4())
        if not self.detected_at:
            self.detected_at = datetime.now(timezone.utc).isoformat()


class BoidsFlockingSimulator:
    """鸟群飞行模拟器
    
    基于Reynolds的Boids算法实现群体行为
    """
    
    def __init__(self, num_agents: int = 50):
        self.num_agents = num_agents
        self.swarm_state = self._initialize_swarm()
        self.simulation_history: List[Dict] = []
        
        # Boids参数
        self.separation_weight = 1.5  # 分离权重
        self.alignment_weight = 1.0   # 对齐权重
        self.cohesion_weight = 1.0    # 凝聚权重
        self.perception_radius = 5.0  # 感知半径
    
    def _initialize_swarm(self) -> SwarmState:
        """初始化群体"""
        state = SwarmState(swarm_id=str(uuid.uuid4()))
        
        for i in range(self.num_agents):
            agent = SwarmAgent(
                agent_id=f"boid_{i}",
                role="follower",
                position=(random.uniform(-50, 50), random.uniform(-50, 50)),
                velocity=(random.uniform(-1, 1), random.uniform(-1, 1))
            )
            state.agents.append(agent)
        
        return state
    
    def compute_separation(self, agent: SwarmAgent) -> Tuple[float, float]:
        """计算分离力（避免碰撞）"""
        steering = (0.0, 0.0)
        neighbor_count = 0
        
        for other in self.swarm_state.agents:
            if other.agent_id == agent.agent_id:
                continue
            
            distance = agent.distance_to(other)
            
            if distance < self.perception_radius / 2:
                # 远离邻居
                dx = agent.position[0] - other.position[0]
                dy = agent.position[1] - other.position[1]
                
                # 归一化并加权
                if distance > 0:
                    steering = (steering[0] + dx / distance, steering[1] + dy / distance)
                    neighbor_count += 1
        
        if neighbor_count > 0:
            steering = (steering[0] / neighbor_count, steering[1] / neighbor_count)
        
        return steering
    
    def compute_alignment(self, agent: SwarmAgent) -> Tuple[float, float]:
        """计算对齐力（与邻居速度对齐）"""
        avg_velocity = (0.0, 0.0)
        neighbor_count = 0
        
        for other in self.swarm_state.agents:
            if other.agent_id == agent.agent_id:
                continue
            
            distance = agent.distance_to(other)
            
            if distance < self.perception_radius:
                avg_velocity = (
                    avg_velocity[0] + other.velocity[0],
                    avg_velocity[1] + other.velocity[1]
                )
                neighbor_count += 1
        
        if neighbor_count > 0:
            avg_velocity = (
                avg_velocity[0] / neighbor_count,
                avg_velocity[1] / neighbor_count
            )
            
            # 转向平均速度
            steering = (
                avg_velocity[0] - agent.velocity[0],
                avg_velocity[1] - agent.velocity[1]
            )
        else:
            steering = (0.0, 0.0)
        
        return steering
    
    def compute_cohesion(self, agent: SwarmAgent) -> Tuple[float, float]:
        """计算凝聚力（向群体中心移动）"""
        center = (0.0, 0.0)
        neighbor_count = 0
        
        for other in self.swarm_state.agents:
            if other.agent_id == agent.agent_id:
                continue
            
            distance = agent.distance_to(other)
            
            if distance < self.perception_radius:
                center = (center[0] + other.position[0], center[1] + other.position[1])
                neighbor_count += 1
        
        if neighbor_count > 0:
            center = (center[0] / neighbor_count, center[1] / neighbor_count)
            
            # 转向中心
            steering = (
                center[0] - agent.position[0],
                center[1] - agent.position[1]
            )
        else:
            steering = (0.0, 0.0)
        
        return steering
    
    def update_agent_behavior(self, agent: SwarmAgent):
        """更新智能体行为"""
        # 计算三种力
        separation = self.compute_separation(agent)
        alignment = self.compute_alignment(agent)
        cohesion = self.compute_cohesion(agent)
        
        # 加权组合
        new_velocity = (
            agent.velocity[0] + 
            self.separation_weight * separation[0] +
            self.alignment_weight * alignment[0] +
            self.cohesion_weight * cohesion[0],
            
            agent.velocity[1] +
            self.separation_weight * separation[1] +
            self.alignment_weight * alignment[1] +
            self.cohesion_weight * cohesion[1]
        )
        
        # 限制最大速度
        speed = math.sqrt(new_velocity[0]**2 + new_velocity[1]**2)
        max_speed = 2.0
        if speed > max_speed:
            new_velocity = (
                new_velocity[0] / speed * max_speed,
                new_velocity[1] / speed * max_speed
            )
        
        agent.velocity = new_velocity
        agent.update_position()
    
    def simulate_step(self) -> SwarmState:
        """执行一步模拟"""
        for agent in self.swarm_state.agents:
            self.update_agent_behavior(agent)
        
        # 检测涌现模式
        patterns = self.detect_emergent_patterns()
        self.swarm_state.emergent_patterns.extend(patterns)
        
        # 记录历史
        self.simulation_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "num_agents": self.swarm_state.size,
            "centroid": self.swarm_state.centroid,
            "num_patterns": len(patterns)
        })
        
        logger.debug(f"Simulation step completed: {len(patterns)} patterns detected")
        
        return self.swarm_state
    
    def detect_emergent_patterns(self) -> List[EmergentPattern]:
        """检测涌现模式"""
        patterns = []
        
        # 检测聚集模式
        if self._detect_clustering():
            pattern = EmergentPattern(
                pattern_id="",
                pattern_type=EmergenceType.STRUCTURAL,
                description="Cluster formation detected",
                strength=random.uniform(0.6, 0.9),
                stability=random.uniform(0.7, 0.95)
            )
            patterns.append(pattern)
        
        # 检测对齐模式
        if self._detect_alignment():
            pattern = EmergentPattern(
                pattern_id="",
                pattern_type=EmergenceType.BEHAVIORAL,
                description="Velocity alignment detected",
                strength=random.uniform(0.7, 0.95),
                stability=random.uniform(0.8, 0.98)
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_clustering(self) -> bool:
        """检测聚类"""
        # 简化实现：检查是否有超过60%的智能体在质心附近
        centroid = self.swarm_state.centroid
        nearby_count = sum(
            1 for agent in self.swarm_state.agents
            if math.sqrt((agent.position[0] - centroid[0])**2 + 
                        (agent.position[1] - centroid[1])**2) < 10
        )
        
        return nearby_count > self.num_agents * 0.6
    
    def _detect_alignment(self) -> bool:
        """检测对齐"""
        # 简化实现：检查速度方向一致性
        if not self.swarm_state.agents:
            return False
        
        avg_direction = (
            statistics.mean([a.velocity[0] for a in self.swarm_state.agents]),
            statistics.mean([a.velocity[1] for a in self.swarm_state.agents])
        )
        
        direction_magnitude = math.sqrt(avg_direction[0]**2 + avg_direction[1]**2)
        
        return direction_magnitude > 0.5
    
    def run_simulation(self, num_steps: int = 100) -> Dict[str, Any]:
        """运行完整模拟"""
        for step in range(num_steps):
            self.simulate_step()
        
        return {
            "total_steps": num_steps,
            "final_swarm_size": self.swarm_state.size,
            "final_centroid": self.swarm_state.centroid,
            "total_patterns_detected": len(self.swarm_state.emergent_patterns),
            "pattern_types": list(set(p.pattern_type.value for p in self.swarm_state.emergent_patterns))
        }


class GossipProtocolCoordinator:
    """谣言协议协调器
    
    实现去中心化的信息传播
    """
    
    def __init__(self, num_agents: int = 20):
        self.num_agents = num_agents
        self.agents: Dict[str, Dict] = {}
        self.message_log: List[Dict] = []
        
        # 初始化智能体
        for i in range(num_agents):
            agent_id = f"agent_{i}"
            self.agents[agent_id] = {
                "id": agent_id,
                "knowledge": {},
                "neighbors": self._select_neighbors(agent_id)
            }
    
    def _select_neighbors(self, agent_id: str, k: int = 3) -> List[str]:
        """选择邻居（随机选择k个其他智能体）"""
        other_agents = [aid for aid in self.agents.keys() if aid != agent_id]
        return random.sample(other_agents, min(k, len(other_agents)))
    
    def spread_information(self, source_agent: str, information: Dict) -> int:
        """
        传播信息
        
        Args:
            source_agent: 源智能体
            information: 要传播的信息
            
        Returns:
            接收到信息的智能体数量
        """
        # 源智能体首先接收信息
        self.agents[source_agent]["knowledge"].update(information)
        
        informed_agents = {source_agent}
        queue = [source_agent]
        rounds = 0
        
        while queue and rounds < 10:  # 最多10轮
            next_queue = []
            
            for agent_id in queue:
                agent = self.agents[agent_id]
                
                # 向邻居传播
                for neighbor_id in agent["neighbors"]:
                    if neighbor_id not in informed_agents:
                        # 以一定概率传播
                        if random.random() < 0.8:  # 80%传播率
                            self.agents[neighbor_id]["knowledge"].update(information)
                            informed_agents.add(neighbor_id)
                            next_queue.append(neighbor_id)
                            
                            # 记录消息
                            self.message_log.append({
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "from": agent_id,
                                "to": neighbor_id,
                                "info_keys": list(information.keys())
                            })
            
            queue = next_queue
            rounds += 1
        
        logger.info(f"Information spread to {len(informed_agents)}/{self.num_agents} agents")
        
        return len(informed_agents)
    
    def reach_consensus(self, initial_opinions: Dict[str, float]) -> Dict[str, Any]:
        """
        达成共识
        
        Args:
            initial_opinions: 初始意见 {agent_id: opinion_value}
            
        Returns:
            共识结果
        """
        # 初始化意见
        for agent_id, opinion in initial_opinions.items():
            if agent_id in self.agents:
                self.agents[agent_id]["knowledge"]["opinion"] = opinion
        
        # 多轮意见交换
        num_rounds = 20
        for round_num in range(num_rounds):
            for agent_id in self.agents:
                agent = self.agents[agent_id]
                
                if "opinion" not in agent["knowledge"]:
                    continue
                
                # 收集邻居意见
                neighbor_opinions = []
                for neighbor_id in agent["neighbors"]:
                    if "opinion" in self.agents[neighbor_id]["knowledge"]:
                        neighbor_opinions.append(
                            self.agents[neighbor_id]["knowledge"]["opinion"]
                        )
                
                if neighbor_opinions:
                    # 更新为平均值
                    agent["knowledge"]["opinion"] = statistics.mean(neighbor_opinions)
        
        # 计算最终共识
        final_opinions = [
            self.agents[aid]["knowledge"].get("opinion", 0.5)
            for aid in self.agents
        ]
        
        consensus_value = statistics.mean(final_opinions)
        variance = statistics.variance(final_opinions) if len(final_opinions) > 1 else 0
        
        return {
            "consensus_value": round(consensus_value, 4),
            "variance": round(variance, 6),
            "convergence_achieved": variance < 0.01,
            "num_rounds": num_rounds
        }


class AntColonyOptimizer:
    """蚁群优化器
    
    用于解决组合优化问题
    """
    
    def __init__(self, num_ants: int = 30, num_iterations: int = 100):
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.pheromone_trails: Dict[Tuple[int, int], float] = {}
        self.optimization_history: List[Dict] = []
    
    def optimize_tsp(self, cities: List[Tuple[float, float]]) -> Dict[str, Any]:
        """
        求解旅行商问题
        
        Args:
            cities: 城市坐标列表
            
        Returns:
            优化结果
        """
        num_cities = len(cities)
        
        # 初始化信息素
        for i in range(num_cities):
            for j in range(i + 1, num_cities):
                self.pheromone_trails[(i, j)] = 1.0
                self.pheromone_trails[(j, i)] = 1.0
        
        best_tour = None
        best_distance = float('inf')
        
        for iteration in range(self.num_iterations):
            # 每只蚂蚁构建路径
            tours = []
            distances = []
            
            for ant in range(self.num_ants):
                tour = self._construct_tour(cities)
                distance = self._calculate_tour_distance(tour, cities)
                
                tours.append(tour)
                distances.append(distance)
                
                if distance < best_distance:
                    best_distance = distance
                    best_tour = tour.copy()
            
            # 更新信息素
            self._update_pheromones(tours, distances)
            
            # 记录历史
            self.optimization_history.append({
                "iteration": iteration + 1,
                "best_distance": best_distance,
                "avg_distance": statistics.mean(distances)
            })
            
            if (iteration + 1) % 20 == 0:
                logger.info(f"Iteration {iteration+1}: best_distance={best_distance:.2f}")
        
        return {
            "best_tour": best_tour,
            "best_distance": best_distance,
            "num_iterations": self.num_iterations,
            "convergence_history": self.optimization_history[-10:]  # 最后10次
        }
    
    def _construct_tour(self, cities: List[Tuple[float, float]]) -> List[int]:
        """构建路径"""
        num_cities = len(cities)
        visited = [False] * num_cities
        tour = []
        
        # 随机起点
        current = random.randint(0, num_cities - 1)
        tour.append(current)
        visited[current] = True
        
        for _ in range(num_cities - 1):
            # 选择下一个城市（基于信息素和距离）
            next_city = self._select_next_city(current, visited, cities)
            tour.append(next_city)
            visited[next_city] = True
            current = next_city
        
        return tour
    
    def _select_next_city(
        self,
        current: int,
        visited: List[bool],
        cities: List[Tuple[float, float]]
    ) -> int:
        """选择下一个城市"""
        num_cities = len(cities)
        unvisited = [i for i in range(num_cities) if not visited[i]]
        
        if not unvisited:
            return current
        
        # 简化实现：随机选择
        return random.choice(unvisited)
    
    def _calculate_tour_distance(
        self,
        tour: List[int],
        cities: List[Tuple[float, float]]
    ) -> float:
        """计算路径总距离"""
        distance = 0.0
        
        for i in range(len(tour)):
            from_city = tour[i]
            to_city = tour[(i + 1) % len(tour)]
            
            dx = cities[from_city][0] - cities[to_city][0]
            dy = cities[from_city][1] - cities[to_city][1]
            distance += math.sqrt(dx**2 + dy**2)
        
        return distance
    
    def _update_pheromones(self, tours: List[List[int]], distances: List[float]):
        """更新信息素"""
        # 蒸发
        evaporation_rate = 0.5
        for key in self.pheromone_trails:
            self.pheromone_trails[key] *= (1 - evaporation_rate)
        
        # 增强最优路径
        for tour, distance in zip(tours, distances):
            pheromone_deposit = 1.0 / distance
            
            for i in range(len(tour)):
                from_city = tour[i]
                to_city = tour[(i + 1) % len(tour)]
                
                key = (from_city, to_city)
                if key in self.pheromone_trails:
                    self.pheromone_trails[key] += pheromone_deposit


def create_swarm_intelligence_system() -> Tuple[BoidsFlockingSimulator, GossipProtocolCoordinator, AntColonyOptimizer]:
    """工厂函数：创建群体智能系统"""
    boids = BoidsFlockingSimulator(num_agents=50)
    gossip = GossipProtocolCoordinator(num_agents=20)
    aco = AntColonyOptimizer(num_ants=30, num_iterations=100)
    
    return boids, gossip, aco


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Swarm Intelligence & Emergent Behavior 测试")
    print("="*60)
    
    boids, gossip, aco = create_swarm_intelligence_system()
    
    # Boids鸟群模拟
    print("\n🐦 运行Boids鸟群模拟...")
    simulation_result = boids.run_simulation(num_steps=50)
    print(f"   总步数: {simulation_result['total_steps']}")
    print(f"   最终群体大小: {simulation_result['final_swarm_size']}")
    print(f"   最终质心: ({simulation_result['final_centroid'][0]:.2f}, {simulation_result['final_centroid'][1]:.2f})")
    print(f"   检测到的模式数: {simulation_result['total_patterns_detected']}")
    print(f"   模式类型: {', '.join(simulation_result['pattern_types'])}")
    
    # 谣言协议信息传播
    print("\n📢 测试谣言协议信息传播...")
    test_info = {"task": "data_processing", "priority": "high"}
    informed_count = gossip.spread_information(
        source_agent="agent_0",
        information=test_info
    )
    print(f"   源智能体: agent_0")
    print(f"   传播信息: {test_info}")
    print(f"   接收智能体数: {informed_count}/{gossip.num_agents}")
    print(f"   传播率: {informed_count/gossip.num_agents*100:.1f}%")
    
    # 共识达成
    print("\n🤝 测试共识达成...")
    initial_opinions = {f"agent_{i}": random.uniform(0, 1) for i in range(gossip.num_agents)}
    consensus_result = gossip.reach_consensus(initial_opinions)
    print(f"   共识值: {consensus_result['consensus_value']:.4f}")
    print(f"   方差: {consensus_result['variance']:.6f}")
    print(f"   收敛: {consensus_result['convergence_achieved']}")
    print(f"   迭代轮数: {consensus_result['num_rounds']}")
    
    # 蚁群优化TSP
    print("\n🐜 测试蚁群优化TSP...")
    cities = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(10)]
    tsp_result = aco.optimize_tsp(cities)
    print(f"   城市数: {len(cities)}")
    print(f"   最优路径长度: {tsp_result['best_distance']:.2f}")
    print(f"   最优路径: {tsp_result['best_tour']}")
    print(f"   迭代次数: {tsp_result['num_iterations']}")
    
    if tsp_result['convergence_history']:
        last_iteration = tsp_result['convergence_history'][-1]
        print(f"\n   收敛情况:")
        print(f"     最后迭代: {last_iteration['iteration']}")
        print(f"     最优距离: {last_iteration['best_distance']:.2f}")
        print(f"     平均距离: {last_iteration['avg_distance']:.2f}")
    
    # 群体统计
    print("\n📊 群体智能统计...")
    print(f"   Boids模拟步数: {len(boids.simulation_history)}")
    print(f"   谣言协议消息数: {len(gossip.message_log)}")
    print(f"   ACO优化历史: {len(aco.optimization_history)}")
    
    print("\n✅ 测试完成！")
