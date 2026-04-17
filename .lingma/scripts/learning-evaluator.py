#!/usr/bin/env python3
"""
学习效果评估系统 (Learning Effectiveness Evaluator)

职责:
1. 指标收集 - 从操作日志和偏好系统中提取关键指标
2. 效果分析 - 评估学习系统的准确性和效率
3. 报告生成 - 生成详细的学习效果报告

评估维度:
- 记忆准确性: 预测的用户偏好 vs 实际行为
- 学习效率: 达到稳定状态所需的操作数
- 用户满意度: 基于覆盖率和成功率推断
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Collection


class LearningEvaluator:
    """学习效果评估器"""
    
    def __init__(self, logs_dir: str = ".lingma/logs"):
        self.logs_dir = Path(logs_dir)
        self.config_dir = self.logs_dir.parent / "config"
        
    def collect_metrics(self, days: int = 7) -> Dict[str, Any]:
        """收集学习效果指标
        
        Returns:
            包含所有关键指标的字典
        """
        metrics = {
            "collection_timestamp": datetime.utcnow().isoformat(),
            "analysis_period_days": days,
            "operational_metrics": self._collect_operational_metrics(days),
            "learning_metrics": self._collect_learning_metrics(),
            "preference_accuracy": self._evaluate_preference_accuracy(days),
            "system_health": self._assess_system_health()
        }
        
        return metrics
    
    def _collect_operational_metrics(self, days: int) -> Dict[str, Any]:
        """收集操作层面的指标"""
        log_file = self.logs_dir / "automation.log"
        if not log_file.exists():
            return {"total_operations": 0}
        
        operations = []
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                        op_time = datetime.fromisoformat(entry.get("timestamp", ""))
                        if op_time >= cutoff_date:
                            operations.append(entry)
                    except (json.JSONDecodeError, ValueError):
                        continue
        except Exception as e:
            print(f"⚠️ 读取日志失败: {e}")
            return {"total_operations": 0}
        
        if not operations:
            return {"total_operations": 0}
        
        # 计算各项指标
        total = len(operations)
        success_count = sum(1 for op in operations if op.get("result", {}).get("status") == "success")
        failed_count = sum(1 for op in operations if op.get("result", {}).get("status") == "failed")
        
        auto_executed = sum(1 for op in operations if op.get("execution_strategy") == "auto_execute")
        asked_user = sum(1 for op in operations if op.get("user_interaction", {}).get("asked"))
        overridden = sum(
            1 for op in operations 
            if op.get("user_interaction", {}).get("asked") and op.get("user_interaction", {}).get("user_decision")
        )
        
        avg_duration = sum(
            op.get("result", {}).get("duration_ms", 0) for op in operations
        ) / total if total > 0 else 0
        
        return {
            "total_operations": total,
            "success_count": success_count,
            "failed_count": failed_count,
            "success_rate": round(success_count / total, 2) if total > 0 else 0,
            "auto_execution_rate": round(auto_executed / total, 2) if total > 0 else 0,
            "user_asked_count": asked_user,
            "user_override_count": overridden,
            "override_rate": round(overridden / asked_user, 2) if asked_user > 0 else 0,
            "avg_decision_time_ms": round(avg_duration, 2),
            "operations_by_type": self._group_by_operation_type(operations)
        }
    
    def _group_by_operation_type(self, operations: List[dict]) -> Dict[str, int]:
        """按操作类型分组统计"""
        type_counts: Dict[str, int] = {}
        for op in operations:
            op_type = op.get("operation_type", "unknown")
            type_counts[op_type] = type_counts.get(op_type, 0) + 1
        return type_counts
    
    def _collect_learning_metrics(self) -> Dict[str, Any]:
        """收集学习相关的指标"""
        # 读取学习报告
        learning_reports = list(self.logs_dir.glob("learning-report-*.json"))
        
        if not learning_reports:
            return {
                "total_learning_cycles": 0,
                "last_learning_cycle": None,
                "total_preference_updates": 0
            }
        
        # 加载最新的学习报告
        latest_report = max(learning_reports, key=lambda p: p.stat().st_mtime)
        with open(latest_report, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        # 统计历史更新次数
        pref_file = self.config_dir / "user-preferences.json"
        total_updates = 0
        if pref_file.exists():
            with open(pref_file, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
                total_updates = sum(
                    info.get("override_count", 0) 
                    for info in prefs.get("operation_overrides", {}).values()
                )
        
        return {
            "total_learning_cycles": len(learning_reports),
            "last_learning_cycle": report_data.get("timestamp"),
            "total_preference_updates": total_updates,
            "latest_report_path": str(latest_report)
        }
    
    def _evaluate_preference_accuracy(self, days: int) -> Dict[str, Any]:
        """评估偏好预测的准确性
        
        方法:
        1. 检查系统决策与用户实际行为的一致性
        2. 计算预测准确率
        """
        log_file = self.logs_dir / "automation.log"
        if not log_file.exists():
            return {"accuracy": 0.0, "sample_size": 0}
        
        operations = []
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                        op_time = datetime.fromisoformat(entry.get("timestamp", ""))
                        if op_time >= cutoff_date:
                            operations.append(entry)
                    except (json.JSONDecodeError, ValueError):
                        continue
        except Exception:
            return {"accuracy": 0.0, "sample_size": 0}
        
        if not operations:
            return {"accuracy": 0.0, "sample_size": 0}
        
        # 计算预测准确率
        # 准确预测 = 系统自动执行且用户未覆盖 OR 系统询问且用户同意
        correct_predictions = 0
        total_evaluated = 0
        
        for op in operations:
            strategy = op.get("execution_strategy", "")
            user_interaction = op.get("user_interaction", {})
            result = op.get("result", {}).get("status", "")
            
            if strategy == "auto_execute":
                # 自动执行，如果成功则视为正确预测
                if result == "success":
                    correct_predictions += 1
                total_evaluated += 1
            
            elif user_interaction.get("asked"):
                total_evaluated += 1
                # 用户未覆盖（同意系统建议）
                if not user_interaction.get("user_decision"):
                    correct_predictions += 1
        
        accuracy = round(correct_predictions / total_evaluated, 2) if total_evaluated > 0 else 0.0
        
        return {
            "accuracy": accuracy,
            "correct_predictions": correct_predictions,
            "total_evaluated": total_evaluated,
            "sample_size": len(operations)
        }
    
    def _assess_system_health(self) -> Dict[str, Any]:
        """评估系统整体健康状态"""
        health_indicators = {}
        
        # 1. 检查配置文件
        pref_file = self.config_dir / "user-preferences.json"
        health_indicators["preferences_configured"] = pref_file.exists()
        
        # 2. 检查日志文件
        log_file = self.logs_dir / "automation.log"
        health_indicators["logging_active"] = log_file.exists()
        
        # 3. 检查学习报告
        learning_reports = list(self.logs_dir.glob("learning-report-*.json"))
        health_indicators["learning_active"] = len(learning_reports) > 0
        
        # 4. 综合评分
        active_components = sum(health_indicators.values())
        total_components = len(health_indicators)
        health_score = round(active_components / total_components, 2) if total_components > 0 else 0
        
        return {
            "indicators": health_indicators,
            "health_score": health_score,
            "status": "healthy" if health_score >= 0.8 else "degraded" if health_score >= 0.5 else "unhealthy"
        }
    
    def analyze_effectiveness(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """分析学习效果
        
        Returns:
            包含分析结果和建议的字典
        """
        analysis: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_assessment": "",
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "trend_analysis": {}
        }
        
        ops_metrics = metrics.get("operational_metrics", {})
        accuracy_metrics = metrics.get("preference_accuracy", {})
        learning_metrics = metrics.get("learning_metrics", {})
        
        # 评估整体表现
        success_rate = ops_metrics.get("success_rate", 0)
        override_rate = ops_metrics.get("override_rate", 0)
        accuracy = accuracy_metrics.get("accuracy", 0)
        
        # 强项识别
        if success_rate >= 0.9:
            analysis["strengths"].append(f"✅ 高成功率 ({success_rate:.0%})")
        if accuracy >= 0.8:
            analysis["strengths"].append(f"✅ 高预测准确率 ({accuracy:.0%})")
        if override_rate < 0.2:
            analysis["strengths"].append(f"✅ 低用户覆盖率 ({override_rate:.0%})，系统决策可靠")
        
        # 弱项识别
        if success_rate < 0.8:
            analysis["weaknesses"].append(f"⚠️ 成功率偏低 ({success_rate:.0%})")
        if override_rate > 0.4:
            analysis["weaknesses"].append(f"⚠️ 用户覆盖率高 ({override_rate:.0%})，需调整策略")
        if accuracy < 0.6:
            analysis["weaknesses"].append(f"⚠️ 预测准确率低 ({accuracy:.0%})")
        if learning_metrics.get("total_learning_cycles", 0) == 0:
            analysis["weaknesses"].append("⚠️ 尚未执行学习周期")
        
        # 生成建议
        if override_rate > 0.3:
            analysis["recommendations"].append(
                "💡 考虑提高自动化级别或降低风险阈值"
            )
        if success_rate < 0.8:
            analysis["recommendations"].append(
                "🔧 检查高风险操作的配置，可能需要更保守的策略"
            )
        if learning_metrics.get("total_learning_cycles", 0) < 3:
            analysis["recommendations"].append(
                "📊 建议执行更多学习周期以积累数据"
            )
        if not analysis["recommendations"]:
            analysis["recommendations"].append("✅ 系统运行良好，继续保持")
        
        # 总体评估
        if len(analysis["strengths"]) >= 2 and len(analysis["weaknesses"]) == 0:
            analysis["overall_assessment"] = "优秀 - 学习系统效果显著"
        elif len(analysis["weaknesses"]) <= 1:
            analysis["overall_assessment"] = "良好 - 有改进空间"
        else:
            analysis["overall_assessment"] = "需要改进 - 多个指标不达标"
        
        return analysis
    
    def generate_report(self, days: int = 7, output_format: str = "text") -> str:
        """生成完整的学习效果报告
        
        Args:
            days: 分析的天数范围
            output_format: 输出格式 (text/json)
        
        Returns:
            格式化的报告字符串
        """
        print("📊 收集指标...")
        metrics = self.collect_metrics(days)
        
        print("🔍 分析效果...")
        analysis = self.analyze_effectiveness(metrics)
        
        # 组合完整报告
        report = {
            "title": "学习效果评估报告",
            "generated_at": datetime.utcnow().isoformat(),
            "analysis_period_days": days,
            "metrics": metrics,
            "analysis": analysis
        }
        
        # 保存 JSON 报告
        report_file = self.logs_dir / f"effectiveness-report-{datetime.utcnow().strftime('%Y%m%d')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 生成文本报告
        if output_format == "text":
            text_report = self._format_text_report(report)
            print(f"\n{text_report}")
            print(f"\n📝 详细报告已保存: {report_file}")
            return text_report
        else:
            print(f"📝 JSON 报告已保存: {report_file}")
            return json.dumps(report, indent=2, ensure_ascii=False)
    
    def _format_text_report(self, report: dict) -> str:
        """格式化文本报告"""
        lines = []
        lines.append("=" * 70)
        lines.append("📊 学习效果评估报告")
        lines.append("=" * 70)
        lines.append(f"生成时间: {report['generated_at']}")
        lines.append(f"分析周期: {report['analysis_period_days']} 天")
        lines.append("")
        
        # 运营指标
        ops = report["metrics"].get("operational_metrics", {})
        lines.append("📈 运营指标:")
        lines.append(f"   总操作数: {ops.get('total_operations', 0)}")
        lines.append(f"   成功率: {ops.get('success_rate', 0):.0%}")
        lines.append(f"   自动化率: {ops.get('auto_execution_rate', 0):.0%}")
        lines.append(f"   用户覆盖率: {ops.get('override_rate', 0):.0%}")
        lines.append(f"   平均决策时间: {ops.get('avg_decision_time_ms', 0):.2f}ms")
        lines.append("")
        
        # 学习指标
        learn = report["metrics"].get("learning_metrics", {})
        lines.append("🧠 学习指标:")
        lines.append(f"   学习周期数: {learn.get('total_learning_cycles', 0)}")
        lines.append(f"   偏好更新次数: {learn.get('total_preference_updates', 0)}")
        lines.append(f"   最后学习: {learn.get('last_learning_cycle', 'N/A')}")
        lines.append("")
        
        # 预测准确性
        accuracy = report["metrics"].get("preference_accuracy", {})
        lines.append("🎯 预测准确性:")
        lines.append(f"   准确率: {accuracy.get('accuracy', 0):.0%}")
        lines.append(f"   正确预测: {accuracy.get('correct_predictions', 0)}")
        lines.append(f"   评估样本: {accuracy.get('total_evaluated', 0)}")
        lines.append("")
        
        # 系统健康
        health = report["metrics"].get("system_health", {})
        lines.append("💚 系统健康:")
        lines.append(f"   健康评分: {health.get('health_score', 0):.0%}")
        lines.append(f"   状态: {health.get('status', 'unknown')}")
        lines.append("")
        
        # 分析结果
        analysis = report["analysis"]
        lines.append("📋 分析结果:")
        lines.append(f"   总体评估: {analysis['overall_assessment']}")
        lines.append("")
        
        if analysis["strengths"]:
            lines.append("   ✅ 强项:")
            for strength in analysis["strengths"]:
                lines.append(f"      {strength}")
            lines.append("")
        
        if analysis["weaknesses"]:
            lines.append("   ⚠️  弱项:")
            for weakness in analysis["weaknesses"]:
                lines.append(f"      {weakness}")
            lines.append("")
        
        if analysis["recommendations"]:
            lines.append("   💡 建议:")
            for rec in analysis["recommendations"]:
                lines.append(f"      {rec}")
            lines.append("")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)


def main():
    """主函数 - 执行学习效果评估"""
    print("=" * 70)
    print("📊 学习效果评估系统")
    print("=" * 70)
    
    evaluator = LearningEvaluator()
    
    # 生成报告
    report = evaluator.generate_report(days=7, output_format="text")
    
    print("\n" + "=" * 70)
    print("✅ 评估完成")
    print("=" * 70)


if __name__ == "__main__":
    main()
