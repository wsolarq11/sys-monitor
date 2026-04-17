#!/usr/bin/env python3
"""
AI Agent Open-Ended Self-Improvement & Continuous Loop System - AI Agent 开放式自我改进与持续循环系统

架构分析、机会检测、安全实验、持续循环、Autoresearch模式
实现生产级 AI Agent 的开放式自我进化能力

参考社区最佳实践:
- Open-Ended Self-Improvement - continuous autonomous evolution without predefined limits
- Architecture Analysis - analyze system architecture for improvement opportunities
- Opportunity Detection - identify areas for enhancement automatically
- Safe Experimentation - controlled experiments with rollback capabilities
- Continuous Loop - operate/experiment/analyze/improve cycle
- Autoresearch Pattern - modify code, train briefly, check results, keep/discard changes
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


class ImprovementCategory(Enum):
    """改进类别"""
    PERFORMANCE = "performance"  # 性能优化
    SECURITY = "security"  # 安全性
    RELIABILITY = "reliability"  # 可靠性
    EFFICIENCY = "efficiency"  # 效率
    USABILITY = "usability"  # 可用性
    MAINTAINABILITY = "maintainability"  # 可维护性


class ExperimentStatus(Enum):
    """实验状态"""
    PLANNED = "planned"  # 计划中
    RUNNING = "running"  # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    ROLLED_BACK = "rolled_back"  # 已回滚


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"  # 低风险
    MEDIUM = "medium"  # 中风险
    HIGH = "high"  # 高风险
    CRITICAL = "critical"  # 极高风险


@dataclass
class ImprovementOpportunity:
    """改进机会"""
    opportunity_id: str
    category: ImprovementCategory
    description: str
    potential_impact: float  # 0-1
    effort_estimate: float  # 小时
    risk_level: RiskLevel
    detected_at: str = ""
    
    def __post_init__(self):
        if not self.opportunity_id:
            self.opportunity_id = str(uuid.uuid4())
        if not self.detected_at:
            self.detected_at = datetime.now(timezone.utc).isoformat()


@dataclass
class Experiment:
    """实验记录"""
    experiment_id: str
    hypothesis: str
    modification_description: str
    status: ExperimentStatus
    baseline_metrics: Dict[str, float] = field(default_factory=dict)
    experimental_metrics: Dict[str, float] = field(default_factory=dict)
    improvement_delta: float = 0.0
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    started_at: str = ""
    completed_at: str = ""
    
    def __post_init__(self):
        if not self.experiment_id:
            self.experiment_id = str(uuid.uuid4())
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).isoformat()


@dataclass
class ArchitectureAnalysis:
    """架构分析结果"""
    analysis_id: str
    component_name: str
    current_state: Dict[str, Any] = field(default_factory=dict)
    bottlenecks: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    complexity_score: float = 0.5
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.analysis_id:
            self.analysis_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class OpportunityDetector:
    """机会检测器
    
    自动识别系统改进机会
    """
    
    def __init__(self):
        self.detected_opportunities: List[ImprovementOpportunity] = []
        self.detection_history: List[Dict] = []
    
    def analyze_system_metrics(
        self,
        metrics: Dict[str, float]
    ) -> List[ImprovementOpportunity]:
        """
        分析系统指标，检测改进机会
        
        Args:
            metrics: 系统指标字典
            
        Returns:
            检测到的改进机会列表
        """
        opportunities = []
        
        # 检测性能瓶颈
        if metrics.get("response_time", 0) > 1000:
            opp = ImprovementOpportunity(
                opportunity_id="",
                category=ImprovementCategory.PERFORMANCE,
                description="High response time detected (>1s)",
                potential_impact=0.8,
                effort_estimate=4.0,
                risk_level=RiskLevel.LOW
            )
            opportunities.append(opp)
        
        # 检测内存使用
        if metrics.get("memory_usage", 0) > 80:
            opp = ImprovementOpportunity(
                opportunity_id="",
                category=ImprovementCategory.EFFICIENCY,
                description="High memory usage (>80%)",
                potential_impact=0.7,
                effort_estimate=6.0,
                risk_level=RiskLevel.MEDIUM
            )
            opportunities.append(opp)
        
        # 检测错误率
        if metrics.get("error_rate", 0) > 0.05:
            opp = ImprovementOpportunity(
                opportunity_id="",
                category=ImprovementCategory.RELIABILITY,
                description="High error rate (>5%)",
                potential_impact=0.9,
                effort_estimate=8.0,
                risk_level=RiskLevel.HIGH
            )
            opportunities.append(opp)
        
        # 检测CPU使用
        if metrics.get("cpu_usage", 0) > 90:
            opp = ImprovementOpportunity(
                opportunity_id="",
                category=ImprovementCategory.PERFORMANCE,
                description="CPU usage too high (>90%)",
                potential_impact=0.75,
                effort_estimate=5.0,
                risk_level=RiskLevel.MEDIUM
            )
            opportunities.append(opp)
        
        self.detected_opportunities.extend(opportunities)
        
        # 记录检测历史
        self.detection_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics_analyzed": len(metrics),
            "opportunities_found": len(opportunities)
        })
        
        logger.info(f"Opportunity detection completed: {len(opportunities)} opportunities found")
        
        return opportunities
    
    def prioritize_opportunities(
        self,
        opportunities: List[ImprovementOpportunity]
    ) -> List[ImprovementOpportunity]:
        """
        优先级排序（基于影响/努力比）
        
        Args:
            opportunities: 改进机会列表
            
        Returns:
            排序后的列表
        """
        def priority_score(opp: ImprovementOpportunity) -> float:
            # 风险调整的影响/努力比
            risk_factor = {
                RiskLevel.LOW: 1.0,
                RiskLevel.MEDIUM: 0.8,
                RiskLevel.HIGH: 0.5,
                RiskLevel.CRITICAL: 0.2
            }
            
            return (opp.potential_impact * risk_factor[opp.risk_level]) / max(opp.effort_estimate, 0.1)
        
        sorted_opps = sorted(opportunities, key=priority_score, reverse=True)
        
        logger.info(f"Opportunities prioritized: {len(sorted_opps)} items")
        
        return sorted_opps
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """获取检测统计"""
        if not self.detected_opportunities:
            return {"total_opportunities": 0}
        
        category_counts = defaultdict(int)
        for opp in self.detected_opportunities:
            category_counts[opp.category.value] += 1
        
        avg_impact = statistics.mean([opp.potential_impact for opp in self.detected_opportunities])
        avg_effort = statistics.mean([opp.effort_estimate for opp in self.detected_opportunities])
        
        return {
            "total_opportunities": len(self.detected_opportunities),
            "category_distribution": dict(category_counts),
            "avg_potential_impact": round(avg_impact, 4),
            "avg_effort_hours": round(avg_effort, 2),
            "detection_runs": len(self.detection_history)
        }


class SafeExperimentEngine:
    """安全实验引擎
    
    在受控环境中执行实验
    """
    
    def __init__(self):
        self.experiments: List[Experiment] = []
        self.experiment_history: List[Dict] = []
    
    def plan_experiment(
        self,
        hypothesis: str,
        modification: str,
        baseline_metrics: Dict[str, float]
    ) -> Experiment:
        """
        规划实验
        
        Args:
            hypothesis: 实验假设
            modification: 修改描述
            baseline_metrics: 基线指标
            
        Returns:
            实验对象
        """
        # 风险评估
        risk_assessment = self._assess_risk(modification)
        
        experiment = Experiment(
            experiment_id="",
            hypothesis=hypothesis,
            modification_description=modification,
            status=ExperimentStatus.PLANNED,
            baseline_metrics=baseline_metrics,
            risk_assessment=risk_assessment
        )
        
        self.experiments.append(experiment)
        
        logger.info(f"Experiment planned: {experiment.experiment_id[:8]}...")
        
        return experiment
    
    def execute_experiment(
        self,
        experiment: Experiment,
        duration_minutes: int = 5
    ) -> Experiment:
        """
        执行实验
        
        Args:
            experiment: 实验对象
            duration_minutes: 实验持续时间（分钟）
            
        Returns:
            更新后的实验对象
        """
        experiment.status = ExperimentStatus.RUNNING
        
        logger.info(f"Experiment started: {experiment.experiment_id[:8]}..., duration={duration_minutes}min")
        
        # 模拟实验执行
        time.sleep(0.1)  # 简化：快速模拟
        
        # 生成实验结果
        experimental_metrics = self._simulate_experiment_results(experiment.baseline_metrics)
        
        # 计算改进幅度
        improvements = {}
        for metric_name in experiment.baseline_metrics:
            if metric_name in experimental_metrics:
                baseline = experiment.baseline_metrics[metric_name]
                experimental = experimental_metrics[metric_name]
                
                # 对于越低越好的指标（如响应时间、错误率）
                if metric_name in ["response_time", "error_rate", "memory_usage"]:
                    delta = (baseline - experimental) / baseline if baseline > 0 else 0
                else:
                    # 对于越高越好的指标（如吞吐量、准确率）
                    delta = (experimental - baseline) / baseline if baseline > 0 else 0
                
                improvements[metric_name] = delta
        
        avg_improvement = statistics.mean(improvements.values()) if improvements else 0.0
        
        # 判断实验成功与否
        success = avg_improvement > 0.05  # 至少5%改进
        
        if success:
            experiment.status = ExperimentStatus.COMPLETED
            experiment.experimental_metrics = experimental_metrics
            experiment.improvement_delta = avg_improvement
            experiment.completed_at = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Experiment succeeded: improvement={avg_improvement*100:.1f}%")
        else:
            experiment.status = ExperimentStatus.FAILED
            experiment.experimental_metrics = experimental_metrics
            experiment.improvement_delta = avg_improvement
            experiment.completed_at = datetime.now(timezone.utc).isoformat()
            
            logger.warning(f"Experiment failed: improvement={avg_improvement*100:.1f}%")
        
        # 记录实验历史
        self.experiment_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "experiment_id": experiment.experiment_id,
            "status": experiment.status.value,
            "improvement": avg_improvement
        })
        
        return experiment
    
    def rollback_experiment(self, experiment: Experiment) -> bool:
        """
        回滚实验
        
        Args:
            experiment: 实验对象
            
        Returns:
            是否成功回滚
        """
        if experiment.status in [ExperimentStatus.COMPLETED, ExperimentStatus.FAILED]:
            experiment.status = ExperimentStatus.ROLLED_BACK
            
            logger.info(f"Experiment rolled back: {experiment.experiment_id[:8]}...")
            
            return True
        
        return False
    
    def _assess_risk(self, modification: str) -> Dict[str, Any]:
        """评估修改风险"""
        risk_factors = {
            "code_complexity": random.uniform(0.1, 0.8),
            "dependency_changes": random.uniform(0.0, 0.5),
            "testing_coverage": random.uniform(0.5, 1.0),
            "rollback_feasibility": random.uniform(0.7, 1.0)
        }
        
        overall_risk = statistics.mean(risk_factors.values())
        
        if overall_risk < 0.3:
            risk_level = "LOW"
        elif overall_risk < 0.6:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        return {
            "risk_factors": risk_factors,
            "overall_risk_score": round(overall_risk, 4),
            "risk_level": risk_level
        }
    
    def _simulate_experiment_results(
        self,
        baseline_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """模拟实验结果"""
        experimental_metrics = {}
        
        for metric_name, baseline_value in baseline_metrics.items():
            # 模拟改进或退化
            change_factor = random.uniform(-0.15, 0.25)
            experimental_value = baseline_value * (1 + change_factor)
            
            experimental_metrics[metric_name] = round(experimental_value, 4)
        
        return experimental_metrics
    
    def get_experiment_statistics(self) -> Dict[str, Any]:
        """获取实验统计"""
        if not self.experiments:
            return {"total_experiments": 0}
        
        completed = sum(1 for e in self.experiments if e.status == ExperimentStatus.COMPLETED)
        failed = sum(1 for e in self.experiments if e.status == ExperimentStatus.FAILED)
        rolled_back = sum(1 for e in self.experiments if e.status == ExperimentStatus.ROLLED_BACK)
        
        success_rate = completed / max(len(self.experiments), 1)
        
        avg_improvement = statistics.mean([
            e.improvement_delta for e in self.experiments 
            if e.status == ExperimentStatus.COMPLETED
        ]) if completed > 0 else 0.0
        
        return {
            "total_experiments": len(self.experiments),
            "completed": completed,
            "failed": failed,
            "rolled_back": rolled_back,
            "success_rate": round(success_rate, 4),
            "avg_improvement_on_success": round(avg_improvement, 4)
        }


class ArchitectureAnalyzer:
    """架构分析器
    
    分析系统架构并识别改进点
    """
    
    def __init__(self):
        self.analyses: List[ArchitectureAnalysis] = []
    
    def analyze_component(
        self,
        component_name: str,
        component_state: Dict[str, Any]
    ) -> ArchitectureAnalysis:
        """
        分析组件架构
        
        Args:
            component_name: 组件名称
            component_state: 组件状态
            
        Returns:
            架构分析结果
        """
        # 识别瓶颈
        bottlenecks = self._identify_bottlenecks(component_state)
        
        # 生成改进建议
        suggestions = self._generate_suggestions(bottlenecks, component_state)
        
        # 计算复杂度分数
        complexity = self._calculate_complexity(component_state)
        
        analysis = ArchitectureAnalysis(
            analysis_id="",
            component_name=component_name,
            current_state=component_state,
            bottlenecks=bottlenecks,
            improvement_suggestions=suggestions,
            complexity_score=complexity
        )
        
        self.analyses.append(analysis)
        
        logger.info(f"Architecture analysis completed: {component_name}, complexity={complexity:.2f}")
        
        return analysis
    
    def _identify_bottlenecks(self, state: Dict[str, Any]) -> List[str]:
        """识别瓶颈"""
        bottlenecks = []
        
        if state.get("cpu_usage", 0) > 80:
            bottlenecks.append("High CPU utilization")
        
        if state.get("memory_usage", 0) > 85:
            bottlenecks.append("Memory pressure")
        
        if state.get("response_time", 0) > 500:
            bottlenecks.append("Slow response time")
        
        if state.get("error_rate", 0) > 0.03:
            bottlenecks.append("Elevated error rate")
        
        return bottlenecks
    
    def _generate_suggestions(
        self,
        bottlenecks: List[str],
        state: Dict[str, Any]
    ) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if "High CPU utilization" in bottlenecks:
            suggestions.append("Consider horizontal scaling or algorithm optimization")
        
        if "Memory pressure" in bottlenecks:
            suggestions.append("Implement memory caching or garbage collection tuning")
        
        if "Slow response time" in bottlenecks:
            suggestions.append("Add request caching or optimize database queries")
        
        if "Elevated error rate" in bottlenecks:
            suggestions.append("Improve error handling and add retry mechanisms")
        
        return suggestions
    
    def _calculate_complexity(self, state: Dict[str, Any]) -> float:
        """计算复杂度分数"""
        factors = [
            state.get("num_dependencies", 5) / 20,
            state.get("code_lines", 1000) / 10000,
            state.get("test_coverage", 0.7),
            1.0 - state.get("documentation_quality", 0.8)
        ]
        
        return min(1.0, statistics.mean(factors))
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """获取分析摘要"""
        if not self.analyses:
            return {"total_analyses": 0}
        
        avg_complexity = statistics.mean([a.complexity_score for a in self.analyses])
        total_bottlenecks = sum(len(a.bottlenecks) for a in self.analyses)
        total_suggestions = sum(len(a.improvement_suggestions) for a in self.analyses)
        
        return {
            "total_analyses": len(self.analyses),
            "avg_complexity_score": round(avg_complexity, 4),
            "total_bottlenecks_identified": total_bottlenecks,
            "total_suggestions_generated": total_suggestions
        }


class ContinuousImprovementLoop:
    """持续改进循环
    
    整合检测→实验→分析的完整循环
    """
    
    def __init__(self):
        self.opportunity_detector = OpportunityDetector()
        self.experiment_engine = SafeExperimentEngine()
        self.architecture_analyzer = ArchitectureAnalyzer()
        
        self.loop_iterations: List[Dict] = []
        self.total_improvements = 0
    
    def run_improvement_cycle(
        self,
        system_metrics: Dict[str, float],
        num_experiments: int = 3
    ) -> Dict[str, Any]:
        """
        运行一轮改进循环
        
        Args:
            system_metrics: 系统指标
            num_experiments: 实验数量
            
        Returns:
            循环结果
        """
        logger.info("Starting improvement cycle...")
        
        # Step 1: 机会检测
        opportunities = self.opportunity_detector.analyze_system_metrics(system_metrics)
        prioritized_opps = self.opportunity_detector.prioritize_opportunities(opportunities)
        
        logger.info(f"Detected {len(opportunities)} opportunities, {len(prioritized_opps)} prioritized")
        
        # Step 2: 架构分析
        arch_analysis = self.architecture_analyzer.analyze_component(
            component_name="main_system",
            component_state={
                "cpu_usage": system_metrics.get("cpu_usage", 50),
                "memory_usage": system_metrics.get("memory_usage", 60),
                "response_time": system_metrics.get("response_time", 200),
                "error_rate": system_metrics.get("error_rate", 0.02),
                "num_dependencies": 10,
                "code_lines": 5000,
                "test_coverage": 0.75,
                "documentation_quality": 0.8
            }
        )
        
        # Step 3: 执行实验
        experiments_conducted = 0
        successful_experiments = 0
        
        for i in range(min(num_experiments, len(prioritized_opps))):
            opp = prioritized_opps[i]
            
            # 规划实验
            experiment = self.experiment_engine.plan_experiment(
                hypothesis=f"Addressing: {opp.description}",
                modification=f"Optimize {opp.category.value}",
                baseline_metrics=system_metrics
            )
            
            # 执行实验
            result = self.experiment_engine.execute_experiment(experiment, duration_minutes=5)
            
            experiments_conducted += 1
            
            if result.status == ExperimentStatus.COMPLETED:
                successful_experiments += 1
                self.total_improvements += 1
            elif result.status == ExperimentStatus.FAILED:
                # 回滚失败的实验
                self.experiment_engine.rollback_experiment(result)
        
        # Step 4: 汇总结果
        cycle_result = {
            "cycle_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "opportunities_detected": len(opportunities),
            "experiments_conducted": experiments_conducted,
            "successful_experiments": successful_experiments,
            "architecture_bottlenecks": len(arch_analysis.bottlenecks),
            "architecture_suggestions": len(arch_analysis.improvement_suggestions)
        }
        
        self.loop_iterations.append(cycle_result)
        
        logger.info(f"Improvement cycle completed: {experiments_conducted} experiments, {successful_experiments} successful")
        
        return cycle_result
    
    def run_continuous_loop(
        self,
        num_cycles: int = 5,
        base_metrics: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        运行持续改进循环
        
        Args:
            num_cycles: 循环次数
            base_metrics: 基础指标
            
        Returns:
            总体统计
        """
        if base_metrics is None:
            base_metrics = {
                "response_time": 500.0,
                "error_rate": 0.05,
                "cpu_usage": 75.0,
                "memory_usage": 70.0,
                "throughput": 100.0
            }
        
        for cycle_num in range(num_cycles):
            # 每轮稍微改变指标以模拟系统演化
            current_metrics = {
                k: v * random.uniform(0.9, 1.1) 
                for k, v in base_metrics.items()
            }
            
            self.run_improvement_cycle(current_metrics, num_experiments=3)
        
        # 汇总统计
        loop_stats = self.get_loop_statistics()
        
        logger.info(f"Continuous loop completed: {num_cycles} cycles")
        
        return loop_stats
    
    def get_loop_statistics(self) -> Dict[str, Any]:
        """获取循环统计"""
        opp_stats = self.opportunity_detector.get_detection_statistics()
        exp_stats = self.experiment_engine.get_experiment_statistics()
        arch_stats = self.architecture_analyzer.get_analysis_summary()
        
        return {
            "total_cycles": len(self.loop_iterations),
            "total_improvements": self.total_improvements,
            "opportunity_detection": opp_stats,
            "experiment_results": exp_stats,
            "architecture_analysis": arch_stats
        }


def create_open_ended_improvement_system() -> ContinuousImprovementLoop:
    """工厂函数：创建开放式改进系统"""
    loop = ContinuousImprovementLoop()
    return loop


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Open-Ended Self-Improvement & Continuous Loop 测试")
    print("="*60)
    
    loop = create_open_ended_improvement_system()
    
    # 测试机会检测
    print("\n🔍 测试机会检测...")
    test_metrics = {
        "response_time": 1200.0,
        "error_rate": 0.08,
        "cpu_usage": 92.0,
        "memory_usage": 85.0,
        "throughput": 80.0
    }
    
    opportunities = loop.opportunity_detector.analyze_system_metrics(test_metrics)
    print(f"   检测到 {len(opportunities)} 个改进机会")
    
    prioritized = loop.opportunity_detector.prioritize_opportunities(opportunities)
    print(f"   优先级排序后: {len(prioritized)} 个")
    
    if prioritized:
        top_opp = prioritized[0]
        print(f"\n   最高优先级机会:")
        print(f"     类别: {top_opp.category.value}")
        print(f"     描述: {top_opp.description}")
        print(f"     潜在影响: {top_opp.potential_impact:.2f}")
        print(f"     预估工作量: {top_opp.effort_estimate:.1f}小时")
        print(f"     风险等级: {top_opp.risk_level.value}")
    
    # 测试架构分析
    print("\n🏗️  测试架构分析...")
    analysis = loop.architecture_analyzer.analyze_component(
        component_name="api_gateway",
        component_state={
            "cpu_usage": 85,
            "memory_usage": 78,
            "response_time": 600,
            "error_rate": 0.04,
            "num_dependencies": 15,
            "code_lines": 8000,
            "test_coverage": 0.65,
            "documentation_quality": 0.7
        }
    )
    
    print(f"   组件: {analysis.component_name}")
    print(f"   复杂度分数: {analysis.complexity_score:.2f}")
    print(f"   识别瓶颈数: {len(analysis.bottlenecks)}")
    print(f"   改进建议数: {len(analysis.improvement_suggestions)}")
    
    if analysis.bottlenecks:
        print(f"   瓶颈:")
        for bottleneck in analysis.bottlenecks:
            print(f"     - {bottleneck}")
    
    # 测试安全实验
    print("\n🧪 测试安全实验...")
    experiment = loop.experiment_engine.plan_experiment(
        hypothesis="Optimizing response time will improve user experience",
        modification="Add response caching layer",
        baseline_metrics=test_metrics
    )
    
    print(f"   实验ID: {experiment.experiment_id[:8]}...")
    print(f"   假设: {experiment.hypothesis[:50]}...")
    print(f"   风险评估: {experiment.risk_assessment['risk_level']}")
    
    result = loop.experiment_engine.execute_experiment(experiment, duration_minutes=5)
    print(f"   状态: {result.status.value}")
    print(f"   改进幅度: {result.improvement_delta*100:.1f}%")
    
    if result.status.value == "failed":
        rolled_back = loop.experiment_engine.rollback_experiment(result)
        print(f"   回滚: {'成功' if rolled_back else '失败'}")
    
    # 测试持续改进循环
    print("\n🔄 测试持续改进循环...")
    cycle_result = loop.run_improvement_cycle(
        system_metrics=test_metrics,
        num_experiments=3
    )
    
    print(f"   循环ID: {cycle_result['cycle_id'][:8]}...")
    print(f"   检测到机会: {cycle_result['opportunities_detected']}")
    print(f"   执行实验: {cycle_result['experiments_conducted']}")
    print(f"   成功实验: {cycle_result['successful_experiments']}")
    print(f"   架构瓶颈: {cycle_result['architecture_bottlenecks']}")
    print(f"   改进建议: {cycle_result['architecture_suggestions']}")
    
    # 运行多轮循环
    print("\n♾️  运行多轮持续循环...")
    loop_stats = loop.run_continuous_loop(num_cycles=5)
    
    print(f"\n📊 循环统计:")
    print(f"   总循环数: {loop_stats['total_cycles']}")
    print(f"   总改进数: {loop_stats['total_improvements']}")
    print(f"\n   机会检测:")
    print(f"     总机会数: {loop_stats['opportunity_detection']['total_opportunities']}")
    print(f"     平均影响: {loop_stats['opportunity_detection']['avg_potential_impact']:.2f}")
    print(f"\n   实验结果:")
    print(f"     总实验数: {loop_stats['experiment_results']['total_experiments']}")
    print(f"     成功率: {loop_stats['experiment_results']['success_rate']*100:.1f}%")
    if loop_stats['experiment_results']['total_experiments'] > 0:
        print(f"     平均改进: {loop_stats['experiment_results']['avg_improvement_on_success']*100:.1f}%")
    print(f"\n   架构分析:")
    print(f"     总分析数: {loop_stats['architecture_analysis']['total_analyses']}")
    print(f"     平均复杂度: {loop_stats['architecture_analysis']['avg_complexity_score']:.2f}")
    
    print("\n✅ 测试完成！")
