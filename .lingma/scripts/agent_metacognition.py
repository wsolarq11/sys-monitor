#!/usr/bin/env python3
"""
AI Agent Metacognition & Self-Reflection System - AI Agent 元认知与自我反思系统

自我监控、自我评估、自我调整、内省觉察、信心校准
实现生产级 AI Agent 的元认知能力

参考社区最佳实践:
- Metacognition - "thinking about thinking", self-awareness of cognitive processes
- Self-Monitoring - track own performance and decision-making in real-time
- Self-Assessment - evaluate correctness and quality of outputs
- Self-Adjustment - adapt strategies based on monitoring results
- Introspective Awareness - understand own knowledge, capabilities, limitations
- Confidence Calibration - accurately assess certainty levels (5-level scale)
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


class ConfidenceLevel(Enum):
    """信心等级（5级）"""
    VERY_LOW = "very_low"  # 非常低（0.0-0.2）
    LOW = "low"  # 低（0.2-0.4）
    MEDIUM = "medium"  # 中等（0.4-0.6）
    HIGH = "high"  # 高（0.6-0.8）
    VERY_HIGH = "very_high"  # 非常高（0.8-1.0）


class ReflectionTrigger(Enum):
    """反思触发条件"""
    FIXED_INTERVAL = "fixed_interval"  # 固定间隔
    ERROR_DETECTED = "error_detected"  # 检测到错误
    LOW_CONFIDENCE = "low_confidence"  # 低信心
    REPEATED_FAILURE = "repeated_failure"  # 重复失败
    USER_FEEDBACK = "user_feedback"  # 用户反馈


@dataclass
class SelfMonitoringRecord:
    """自我监控记录"""
    record_id: str
    task_description: str
    current_step: str
    step_number: int
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.record_id:
            self.record_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class SelfAssessment:
    """自我评估结果"""
    assessment_id: str
    task_description: str
    correctness_score: float = 0.0  # 正确性 0-1
    quality_score: float = 0.0  # 质量 0-1
    completeness_score: float = 0.0  # 完整性 0-1
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    identified_issues: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.assessment_id:
            self.assessment_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    @property
    def overall_score(self) -> float:
        """综合评分"""
        return (self.correctness_score + self.quality_score + self.completeness_score) / 3
    
    def calibrate_confidence(self) -> ConfidenceLevel:
        """基于表现校准信心"""
        avg_score = self.overall_score
        
        if avg_score >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif avg_score >= 0.6:
            return ConfidenceLevel.HIGH
        elif avg_score >= 0.4:
            return ConfidenceLevel.MEDIUM
        elif avg_score >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW


@dataclass
class SelfAdjustment:
    """自我调整方案"""
    adjustment_id: str
    original_strategy: str
    adjusted_strategy: str
    reason: str
    expected_improvement: float = 0.0  # 预期改进 0-1
    applied: bool = False
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.adjustment_id:
            self.adjustment_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ReflectionResult:
    """反思结果"""
    reflection_id: str
    trigger: ReflectionTrigger
    assessment: SelfAssessment
    adjustments: List[SelfAdjustment] = field(default_factory=list)
    should_continue: bool = True
    max_reflections_reached: bool = False
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.reflection_id:
            self.reflection_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class SelfMonitor:
    """自我监控器
    
    实时监控Agent的认知过程和性能
    """
    
    def __init__(self):
        self.monitoring_records: List[SelfMonitoringRecord] = []
        self.performance_history: List[Dict] = []
    
    def monitor_step(
        self,
        task: str,
        current_step: str,
        step_number: int,
        metrics: Dict[str, float] = None
    ) -> SelfMonitoringRecord:
        """
        监控执行步骤
        
        Args:
            task: 任务描述
            current_step: 当前步骤
            step_number: 步骤编号
            metrics: 性能指标
            
        Returns:
            监控记录
        """
        if metrics is None:
            metrics = {
                "accuracy": random.uniform(0.6, 0.95),
                "efficiency": random.uniform(0.5, 0.9),
                "resource_usage": random.uniform(0.3, 0.7)
            }
        
        record = SelfMonitoringRecord(
            record_id="",
            task_description=task,
            current_step=current_step,
            step_number=step_number,
            performance_metrics=metrics
        )
        
        self.monitoring_records.append(record)
        
        # 记录性能历史
        self.performance_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step_number": step_number,
            "metrics": metrics
        })
        
        logger.debug(f"Step monitored: {task[:30]}..., step={step_number}")
        
        return record
    
    def detect_performance_issues(
        self,
        threshold: float = 0.6
    ) -> List[Dict]:
        """
        检测性能问题
        
        Args:
            threshold: 性能阈值
            
        Returns:
            问题列表
        """
        issues = []
        
        if not self.performance_history:
            return issues
        
        # 检查最近的性能趋势
        recent_performances = [
            h["metrics"].get("accuracy", 0.5)
            for h in self.performance_history[-5:]
        ]
        
        if recent_performances:
            avg_performance = statistics.mean(recent_performances)
            
            if avg_performance < threshold:
                issues.append({
                    "type": "declining_accuracy",
                    "severity": "high" if avg_performance < 0.4 else "medium",
                    "current_avg": round(avg_performance, 4),
                    "threshold": threshold
                })
        
        # 检查资源使用
        recent_resources = [
            h["metrics"].get("resource_usage", 0.5)
            for h in self.performance_history[-3:]
        ]
        
        if recent_resources and statistics.mean(recent_resources) > 0.8:
            issues.append({
                "type": "high_resource_usage",
                "severity": "medium",
                "current_avg": round(statistics.mean(recent_resources), 4)
            })
        
        logger.info(f"Performance check: {len(issues)} issues detected")
        
        return issues
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """获取监控统计"""
        if not self.monitoring_records:
            return {"total_records": 0}
        
        avg_accuracy = statistics.mean([
            r.performance_metrics.get("accuracy", 0.5)
            for r in self.monitoring_records
        ])
        
        return {
            "total_records": len(self.monitoring_records),
            "avg_accuracy": round(avg_accuracy, 4),
            "monitoring_duration_steps": len(self.performance_history)
        }


class SelfAssessor:
    """自我评估器
    
    评估Agent输出的质量和正确性
    """
    
    def __init__(self):
        self.assessments: List[SelfAssessment] = []
    
    def assess_output(
        self,
        task: str,
        output: str,
        reference_answer: str = None
    ) -> SelfAssessment:
        """
        评估输出质量
        
        Args:
            task: 任务描述
            output: Agent输出
            reference_answer: 参考答案（可选）
            
        Returns:
            评估结果
        """
        # 模拟评估（实际应调用LLM或规则引擎）
        correctness = random.uniform(0.6, 0.95)
        quality = random.uniform(0.65, 0.9)
        completeness = random.uniform(0.7, 0.95)
        
        # 识别问题
        issues = []
        if correctness < 0.7:
            issues.append("Potential factual inaccuracies detected")
        if quality < 0.7:
            issues.append("Output quality could be improved")
        if completeness < 0.7:
            issues.append("Some aspects may be incomplete")
        
        # 生成改进建议
        suggestions = []
        if issues:
            suggestions.append("Review and verify key facts")
            suggestions.append("Enhance explanation clarity")
            suggestions.append("Add missing details or examples")
        
        assessment = SelfAssessment(
            assessment_id="",
            task_description=task,
            correctness_score=correctness,
            quality_score=quality,
            completeness_score=completeness,
            identified_issues=issues,
            improvement_suggestions=suggestions
        )
        
        # 校准信心
        assessment.confidence_level = assessment.calibrate_confidence()
        
        self.assessments.append(assessment)
        
        logger.info(f"Output assessed: correctness={correctness:.2f}, quality={quality:.2f}")
        
        return assessment
    
    def assess_confidence_calibration(
        self,
        assessments: List[SelfAssessment] = None
    ) -> Dict[str, Any]:
        """
        评估信心校准准确性
        
        Args:
            assessments: 评估列表（默认使用所有）
            
        Returns:
            校准统计
        """
        if assessments is None:
            assessments = self.assessments
        
        if not assessments:
            return {"calibration_accuracy": 0}
        
        # 检查信心水平与实际表现的一致性
        calibration_data = []
        
        for assessment in assessments:
            expected_confidence = {
                ConfidenceLevel.VERY_HIGH: 0.9,
                ConfidenceLevel.HIGH: 0.7,
                ConfidenceLevel.MEDIUM: 0.5,
                ConfidenceLevel.LOW: 0.3,
                ConfidenceLevel.VERY_LOW: 0.1
            }
            
            expected_score = expected_confidence[assessment.confidence_level]
            actual_score = assessment.overall_score
            
            calibration_error = abs(expected_score - actual_score)
            calibration_data.append(calibration_error)
        
        avg_calibration_error = statistics.mean(calibration_data)
        calibration_accuracy = 1.0 - avg_calibration_error
        
        return {
            "total_assessments": len(assessments),
            "avg_calibration_error": round(avg_calibration_error, 4),
            "calibration_accuracy": round(calibration_accuracy, 4),
            "confidence_distribution": self._get_confidence_distribution(assessments)
        }
    
    def _get_confidence_distribution(
        self,
        assessments: List[SelfAssessment]
    ) -> Dict[str, int]:
        """获取信心分布"""
        distribution = defaultdict(int)
        
        for assessment in assessments:
            distribution[assessment.confidence_level.value] += 1
        
        return dict(distribution)
    
    def get_assessment_statistics(self) -> Dict[str, Any]:
        """获取评估统计"""
        if not self.assessments:
            return {"total_assessments": 0}
        
        avg_correctness = statistics.mean([a.correctness_score for a in self.assessments])
        avg_quality = statistics.mean([a.quality_score for a in self.assessments])
        avg_completeness = statistics.mean([a.completeness_score for a in self.assessments])
        
        return {
            "total_assessments": len(self.assessments),
            "avg_correctness": round(avg_correctness, 4),
            "avg_quality": round(avg_quality, 4),
            "avg_completeness": round(avg_completeness, 4)
        }


class SelfAdjuster:
    """自我调整器
    
    基于评估结果调整策略和行为
    """
    
    def __init__(self):
        self.adjustments: List[SelfAdjustment] = []
    
    def generate_adjustment(
        self,
        assessment: SelfAssessment,
        current_strategy: str
    ) -> SelfAdjustment:
        """
        生成调整方案
        
        Args:
            assessment: 评估结果
            current_strategy: 当前策略
            
        Returns:
            调整方案
        """
        # 基于问题生成调整建议
        if assessment.correctness_score < 0.7:
            adjusted_strategy = "Implement fact-checking and verification steps"
            reason = "Low correctness score indicates potential inaccuracies"
            expected_improvement = 0.15
        elif assessment.quality_score < 0.7:
            adjusted_strategy = "Enhance output formatting and explanation depth"
            reason = "Quality needs improvement for better user experience"
            expected_improvement = 0.12
        elif assessment.completeness_score < 0.7:
            adjusted_strategy = "Add comprehensive coverage of all aspects"
            reason = "Output appears incomplete in some areas"
            expected_improvement = 0.10
        else:
            adjusted_strategy = current_strategy
            reason = "Current strategy is adequate, minor refinements only"
            expected_improvement = 0.05
        
        adjustment = SelfAdjustment(
            adjustment_id="",
            original_strategy=current_strategy,
            adjusted_strategy=adjusted_strategy,
            reason=reason,
            expected_improvement=expected_improvement
        )
        
        self.adjustments.append(adjustment)
        
        logger.info(f"Adjustment generated: {adjusted_strategy[:50]}...")
        
        return adjustment
    
    def apply_adjustment(self, adjustment: SelfAdjustment) -> bool:
        """应用调整方案"""
        adjustment.applied = True
        
        logger.info(f"Adjustment applied: {adjustment.adjustment_id[:8]}...")
        
        return True
    
    def get_adjustment_statistics(self) -> Dict[str, Any]:
        """获取调整统计"""
        if not self.adjustments:
            return {"total_adjustments": 0}
        
        applied_count = sum(1 for a in self.adjustments if a.applied)
        avg_improvement = statistics.mean([a.expected_improvement for a in self.adjustments])
        
        return {
            "total_adjustments": len(self.adjustments),
            "applied_count": applied_count,
            "application_rate": round(applied_count / len(self.adjustments), 4),
            "avg_expected_improvement": round(avg_improvement, 4)
        }


class MetacognitiveEngine:
    """元认知引擎
    
    整合自我监控、评估、调整的完整元认知循环
    """
    
    def __init__(self, max_reflections: int = 3):
        self.monitor = SelfMonitor()
        self.assessor = SelfAssessor()
        self.adjuster = SelfAdjuster()
        self.max_reflections = max_reflections
        self.reflection_count = 0
        self.reflection_history: List[ReflectionResult] = []
    
    def should_reflect(
        self,
        step_count: int,
        trigger_conditions: List[ReflectionTrigger] = None
    ) -> bool:
        """
        判断是否需要反思
        
        Args:
            step_count: 当前步骤数
            trigger_conditions: 触发条件
            
        Returns:
            是否应该反思
        """
        if trigger_conditions is None:
            trigger_conditions = [ReflectionTrigger.FIXED_INTERVAL]
        
        # 检查是否超过最大反思次数
        if self.reflection_count >= self.max_reflections:
            return False
        
        # 检查触发条件
        for trigger in trigger_conditions:
            if trigger == ReflectionTrigger.FIXED_INTERVAL:
                if step_count % 3 == 0:
                    return True
            elif trigger == ReflectionTrigger.ERROR_DETECTED:
                issues = self.monitor.detect_performance_issues()
                if issues:
                    return True
            elif trigger == ReflectionTrigger.LOW_CONFIDENCE:
                # 检查最近的信心水平
                if self.assessor.assessments:
                    last_assessment = self.assessor.assessments[-1]
                    if last_assessment.confidence_level in [
                        ConfidenceLevel.VERY_LOW,
                        ConfidenceLevel.LOW
                    ]:
                        return True
        
        return False
    
    def execute_reflection(
        self,
        task: str,
        current_step: str,
        step_number: int,
        output: str,
        current_strategy: str
    ) -> ReflectionResult:
        """
        执行反思过程
        
        Args:
            task: 任务描述
            current_step: 当前步骤
            step_number: 步骤编号
            output: 当前输出
            current_strategy: 当前策略
            
        Returns:
            反思结果
        """
        self.reflection_count += 1
        
        logger.info(f"Executing reflection #{self.reflection_count} for: {task[:30]}...")
        
        # Step 1: 自我监控
        monitoring_record = self.monitor.monitor_step(task, current_step, step_number)
        
        # Step 2: 自我评估
        assessment = self.assessor.assess_output(task, output)
        
        # Step 3: 生成调整方案
        adjustment = self.adjuster.generate_adjustment(assessment, current_strategy)
        
        # Step 4: 决定是否继续
        should_continue = (
            self.reflection_count < self.max_reflections and
            assessment.overall_score < 0.85
        )
        
        # Step 5: 生成建议
        recommendations = []
        if not should_continue:
            if self.reflection_count >= self.max_reflections:
                recommendations.append("Maximum reflections reached, consider task decomposition")
            else:
                recommendations.append("Performance satisfactory, continue with current approach")
        else:
            recommendations.append("Apply suggested adjustments and continue")
            recommendations.extend(assessment.improvement_suggestions[:2])
        
        result = ReflectionResult(
            reflection_id="",
            trigger=ReflectionTrigger.FIXED_INTERVAL,
            assessment=assessment,
            adjustments=[adjustment],
            should_continue=should_continue,
            max_reflections_reached=self.reflection_count >= self.max_reflections,
            recommendations=recommendations
        )
        
        self.reflection_history.append(result)
        
        logger.info(f"Reflection completed: should_continue={should_continue}")
        
        return result
    
    def run_metacognitive_loop(
        self,
        task: str,
        num_steps: int = 10
    ) -> Dict[str, Any]:
        """
        运行元认知循环
        
        Args:
            task: 任务描述
            num_steps: 步骤数
            
        Returns:
            循环结果
        """
        logger.info(f"Starting metacognitive loop: {task}, {num_steps} steps")
        
        current_strategy = "standard_approach"
        reflections_triggered = 0
        
        for step in range(1, num_steps + 1):
            # 模拟执行步骤
            output = f"Output for step {step}"
            current_step = f"Step {step}: Processing..."
            
            # 检查是否需要反思
            if self.should_reflect(step):
                reflection = self.execute_reflection(
                    task=task,
                    current_step=current_step,
                    step_number=step,
                    output=output,
                    current_strategy=current_strategy
                )
                
                reflections_triggered += 1
                
                # 应用调整
                if reflection.adjustments:
                    self.adjuster.apply_adjustment(reflection.adjustments[0])
                    current_strategy = reflection.adjustments[0].adjusted_strategy
                
                # 如果不应继续，提前终止
                if not reflection.should_continue:
                    logger.info(f"Metacognitive loop terminated at step {step}")
                    break
        
        # 汇总结果
        loop_result = {
            "task": task,
            "total_steps_executed": min(num_steps, step),
            "reflections_triggered": reflections_triggered,
            "final_strategy": current_strategy,
            "monitoring_stats": self.monitor.get_monitoring_statistics(),
            "assessment_stats": self.assessor.get_assessment_statistics(),
            "adjustment_stats": self.adjuster.get_adjustment_statistics()
        }
        
        logger.info(f"Metacognitive loop completed: {reflections_triggered} reflections")
        
        return loop_result
    
    def get_metacognitive_overview(self) -> Dict[str, Any]:
        """获取元认知概览"""
        return {
            "reflection_count": self.reflection_count,
            "max_reflections": self.max_reflections,
            "monitoring": self.monitor.get_monitoring_statistics(),
            "assessment": self.assessor.get_assessment_statistics(),
            "confidence_calibration": self.assessor.assess_confidence_calibration(),
            "adjustment": self.adjuster.get_adjustment_statistics()
        }


def create_metacognitive_system(max_reflections: int = 3) -> MetacognitiveEngine:
    """工厂函数：创建元认知系统"""
    engine = MetacognitiveEngine(max_reflections=max_reflections)
    return engine


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Metacognition & Self-Reflection 测试")
    print("="*60)
    
    engine = create_metacognitive_system(max_reflections=3)
    
    # 测试自我监控
    print("\n👁️  测试自我监控...")
    for i in range(1, 6):
        record = engine.monitor.monitor_step(
            task="Write Python web scraper",
            current_step=f"Step {i}: Implementing...",
            step_number=i
        )
        print(f"   步骤{i}: accuracy={record.performance_metrics['accuracy']:.2f}")
    
    # 检测性能问题
    issues = engine.monitor.detect_performance_issues(threshold=0.6)
    print(f"\n   检测到 {len(issues)} 个性能问题")
    for issue in issues:
        print(f"     - {issue['type']}: {issue['severity']}")
    
    # 测试自我评估
    print("\n📊 测试自我评估...")
    assessment = engine.assessor.assess_output(
        task="Generate API documentation",
        output="Sample API docs content...",
        reference_answer=None
    )
    
    print(f"   正确性: {assessment.correctness_score:.2f}")
    print(f"   质量: {assessment.quality_score:.2f}")
    print(f"   完整性: {assessment.completeness_score:.2f}")
    print(f"   综合评分: {assessment.overall_score:.2f}")
    print(f"   信心等级: {assessment.confidence_level.value}")
    print(f"   识别问题: {len(assessment.identified_issues)}个")
    print(f"   改进建议: {len(assessment.improvement_suggestions)}个")
    
    # 测试信心校准
    print("\n🎯 测试信心校准...")
    # 生成多个评估
    for _ in range(5):
        engine.assessor.assess_output("Test task", "Sample output")
    
    calibration = engine.assessor.assess_confidence_calibration()
    print(f"   总评估数: {calibration['total_assessments']}")
    print(f"   校准误差: {calibration['avg_calibration_error']:.4f}")
    print(f"   校准准确度: {calibration['calibration_accuracy']*100:.1f}%")
    print(f"   信心分布: {calibration['confidence_distribution']}")
    
    # 测试自我调整
    print("\n🔧 测试自我调整...")
    adjustment = engine.adjuster.generate_adjustment(
        assessment=assessment,
        current_strategy="basic_implementation"
    )
    
    print(f"   原策略: {adjustment.original_strategy}")
    print(f"   调整后: {adjustment.adjusted_strategy[:60]}...")
    print(f"   原因: {adjustment.reason[:60]}...")
    print(f"   预期改进: {adjustment.expected_improvement*100:.1f}%")
    
    applied = engine.adjuster.apply_adjustment(adjustment)
    print(f"   应用状态: {'成功' if applied else '失败'}")
    
    # 测试完整元认知循环
    print("\n🔄 测试元认知循环...")
    loop_result = engine.run_metacognitive_loop(
        task="Build REST API service",
        num_steps=10
    )
    
    print(f"   任务: {loop_result['task']}")
    print(f"   执行步骤: {loop_result['total_steps_executed']}")
    print(f"   触发反思: {loop_result['reflections_triggered']}次")
    print(f"   最终策略: {loop_result['final_strategy']}")
    
    # 元认知概览
    overview = engine.get_metacognitive_overview()
    print(f"\n📈 元认知概览:")
    print(f"   反思次数: {overview['reflection_count']}/{overview['max_reflections']}")
    print(f"   监控统计:")
    mon = overview['monitoring']
    print(f"     总记录: {mon['total_records']}")
    print(f"     平均准确率: {mon['avg_accuracy']:.2f}")
    print(f"   评估统计:")
    ass = overview['assessment']
    print(f"     总评估: {ass['total_assessments']}")
    print(f"     平均正确性: {ass['avg_correctness']:.2f}")
    print(f"     平均质量: {ass['avg_quality']:.2f}")
    print(f"   信心校准:")
    cal = overview['confidence_calibration']
    print(f"     校准准确度: {cal['calibration_accuracy']*100:.1f}%")
    print(f"   调整统计:")
    adj = overview['adjustment']
    print(f"     总调整: {adj['total_adjustments']}")
    print(f"     应用率: {adj['application_rate']*100:.1f}%")
    print(f"     平均预期改进: {adj['avg_expected_improvement']*100:.1f}%")
    
    print("\n✅ 测试完成！")
