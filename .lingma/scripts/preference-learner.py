#!/usr/bin/env python3
"""
偏好学习系统 (Preference Learner)

职责:
1. 模式识别 - 检测用户的重复行为和决策覆盖
2. 偏好更新 - 基于历史数据自动调整风险阈值和策略偏好
3. 策略调整 - 根据学习效果优化自动化决策

设计原则:
- 完全依赖 Lingma Memory 系统存储用户偏好
- 从操作日志中识别模式
- 渐进式学习，避免激进调整
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class PreferenceLearner:
    """偏好学习器 - 从用户行为中学习并优化决策策略"""
    
    def __init__(self, logs_dir: str = ".lingma/logs", memory_api=None):
        self.logs_dir = Path(logs_dir)
        self.memory_api = memory_api  # Lingma Memory API (可选)
        self.preferences = self._load_preferences()
        
    def _load_preferences(self) -> dict:
        """加载当前用户偏好（从 Memory 或配置文件）"""
        pref_file = self.logs_dir.parent / "config" / "user-preferences.json"
        if pref_file.exists():
            with open(pref_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认偏好
        return {
            "automation_level": "balanced",
            "risk_threshold": {
                "low": 0.2,
                "medium": 0.5,
                "high": 0.8
            },
            "operation_overrides": {},
            "learning_enabled": True,
            "learning_rate": 0.1,
            "min_data_points": 10,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def save_preferences(self):
        """保存用户偏好"""
        pref_file = self.logs_dir.parent / "config" / "user-preferences.json"
        pref_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.preferences["last_updated"] = datetime.utcnow().isoformat()
        
        with open(pref_file, 'w', encoding='utf-8') as f:
            json.dump(self.preferences, f, indent=2, ensure_ascii=False)
    
    def analyze_operation_history(self, days: int = 7) -> Dict[str, Any]:
        """分析最近N天的操作历史，识别模式
        
        Returns:
            包含模式统计的字典
        """
        log_file = self.logs_dir / "automation.log"
        if not log_file.exists():
            return {"total_operations": 0, "patterns": []}
        
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
            return {"total_operations": 0, "patterns": []}
        
        # 模式识别
        patterns = self._identify_patterns(operations)
        
        return {
            "total_operations": len(operations),
            "analysis_period_days": days,
            "patterns": patterns,
            "success_rate": self._calculate_success_rate(operations),
            "override_rate": self._calculate_override_rate(operations)
        }
    
    def _identify_patterns(self, operations: List[dict]) -> List[dict]:
        """识别操作模式
        
        检测:
        1. 高频操作类型
        2. 用户覆盖的系统决策
        3. 特定操作的偏好策略
        """
        if not operations:
            return []
        
        patterns = []
        
        # 1. 按操作类型统计
        type_stats = {}
        for op in operations:
            op_type = op.get("operation_type", "unknown")
            if op_type not in type_stats:
                type_stats[op_type] = {
                    "count": 0,
                    "auto_executed": 0,
                    "user_overridden": 0,
                    "success": 0
                }
            type_stats[op_type]["count"] += 1
            
            strategy = op.get("execution_strategy", "")
            if strategy == "auto_execute":
                type_stats[op_type]["auto_executed"] += 1
            
            user_interaction = op.get("user_interaction", {})
            if user_interaction.get("asked") and user_interaction.get("user_decision"):
                type_stats[op_type]["user_overridden"] += 1
            
            result = op.get("result", {})
            if result.get("status") == "success":
                type_stats[op_type]["success"] += 1
        
        # 2. 识别显著模式
        for op_type, stats in type_stats.items():
            if stats["count"] < self.preferences.get("min_data_points", 5):
                continue
            
            override_rate = stats["user_overridden"] / stats["count"] if stats["count"] > 0 else 0
            success_rate = stats["success"] / stats["count"] if stats["count"] > 0 else 0
            
            pattern = {
                "operation_type": op_type,
                "frequency": stats["count"],
                "override_rate": round(override_rate, 2),
                "success_rate": round(success_rate, 2),
                "recommendation": None
            }
            
            # 生成建议
            if override_rate > 0.5:
                pattern["recommendation"] = f"用户对 {op_type} 经常覆盖系统决策，建议调整策略"
            elif success_rate < 0.8:
                pattern["recommendation"] = f"{op_type} 成功率较低，建议增加风险评估"
            
            patterns.append(pattern)
        
        return patterns
    
    def _calculate_success_rate(self, operations: List[dict]) -> float:
        """计算整体成功率"""
        if not operations:
            return 0.0
        
        success_count = sum(
            1 for op in operations 
            if op.get("result", {}).get("status") == "success"
        )
        return round(success_count / len(operations), 2)
    
    def _calculate_override_rate(self, operations: List[dict]) -> float:
        """计算用户覆盖率"""
        if not operations:
            return 0.0
        
        asked_ops = [
            op for op in operations 
            if op.get("user_interaction", {}).get("asked")
        ]
        
        if not asked_ops:
            return 0.0
        
        overridden = sum(
            1 for op in asked_ops
            if op.get("user_interaction", {}).get("user_decision")
        )
        
        return round(overridden / len(asked_ops), 2)
    
    def update_preferences_from_patterns(self, patterns: List[dict]) -> List[Dict[str, Any]]:
        """根据识别的模式更新偏好
        
        学习规则:
        1. 如果某类操作被频繁覆盖 (>50%)，降低其风险等级
        2. 如果某类操作成功率高且无覆盖，提高自动化级别
        3. 渐进式调整，避免激进变化
        """
        if not self.preferences.get("learning_enabled", True):
            print("ℹ️ 学习功能已禁用，跳过偏好更新")
            return []
        
        learning_rate = self.preferences.get("learning_rate", 0.1)
        updates_made = []
        
        for pattern in patterns:
            op_type = pattern["operation_type"]
            override_rate = pattern["override_rate"]
            success_rate = pattern["success_rate"]
            
            # 规则1: 高覆盖率 → 降低风险阈值
            if override_rate > 0.5:
                old_threshold = self.preferences["risk_threshold"].get("medium", 0.5)
                new_threshold = min(old_threshold + learning_rate * 0.1, 0.9)
                self.preferences["risk_threshold"]["medium"] = round(new_threshold, 2)
                
                updates_made.append({
                    "type": "risk_threshold_adjustment",
                    "operation": op_type,
                    "reason": f"高覆盖率 ({override_rate:.0%})",
                    "old_value": old_threshold,
                    "new_value": new_threshold
                })
            
            # 规则2: 记录操作覆盖
            if pattern.get("recommendation"):
                if op_type not in self.preferences["operation_overrides"]:
                    self.preferences["operation_overrides"][op_type] = {
                        "preferred_strategy": "ask_user",
                        "override_count": 0,
                        "last_override": datetime.utcnow().isoformat()
                    }
                
                self.preferences["operation_overrides"][op_type]["override_count"] += 1
                self.preferences["operation_overrides"][op_type]["last_override"] = datetime.utcnow().isoformat()
        
        if updates_made:
            self.save_preferences()
            print(f"✅ 偏好已更新 ({len(updates_made)} 项调整)")
            for update in updates_made:
                print(f"   - {update['operation']}: {update['old_value']} → {update['new_value']}")
        else:
            print("ℹ️ 无需调整偏好")
        
        return updates_made
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """基于分析结果生成个性化建议"""
        recommendations = []
        
        if analysis["total_operations"] < 10:
            recommendations.append("📊 数据不足，建议继续使用系统以积累更多样本")
            return recommendations
        
        # 成功率建议
        if analysis["success_rate"] < 0.8:
            recommendations.append(
                f"⚠️ 整体成功率较低 ({analysis['success_rate']:.0%})，"
                f"建议检查高风险操作的配置"
            )
        
        # 覆盖率建议
        if analysis["override_rate"] > 0.3:
            recommendations.append(
                f"💡 用户覆盖率较高 ({analysis['override_rate']:.0%})，"
                f"系统可能过于保守，考虑提高自动化级别"
            )
        
        # 模式建议
        for pattern in analysis.get("patterns", []):
            if pattern.get("recommendation"):
                recommendations.append(f"🎯 {pattern['recommendation']}")
        
        if not recommendations:
            recommendations.append("✅ 系统运行良好，无需调整")
        
        return recommendations
    
    def run_learning_cycle(self, days: int = 7) -> Dict[str, Any]:
        """执行完整的学习周期
        
        流程:
        1. 分析操作历史
        2. 识别模式
        3. 更新偏好
        4. 生成建议
        
        Returns:
            学习结果报告
        """
        print("🔄 开始学习周期...")
        
        # Step 1: 分析历史
        analysis = self.analyze_operation_history(days)
        print(f"📊 分析了 {analysis['total_operations']} 个操作")
        
        # Step 2: 更新偏好
        updates = self.update_preferences_from_patterns(analysis["patterns"])
        
        # Step 3: 生成建议
        recommendations = self.generate_recommendations(analysis)
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis": analysis,
            "updates": updates,
            "recommendations": recommendations,
            "current_preferences": self.preferences
        }
        
        # 保存学习报告
        report_file = self.logs_dir / f"learning-report-{datetime.utcnow().strftime('%Y%m%d')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📝 学习报告已保存: {report_file}")
        print("\n💡 建议:")
        for rec in recommendations:
            print(f"   {rec}")
        
        return report


def main():
    """主函数 - 执行偏好学习"""
    print("=" * 70)
    print("🧠 偏好学习系统")
    print("=" * 70)
    
    learner = PreferenceLearner()
    
    # 执行学习周期
    report = learner.run_learning_cycle(days=7)
    
    print("\n" + "=" * 70)
    print("✅ 学习完成")
    print("=" * 70)
    
    # 打印摘要
    print(f"\n📈 关键指标:")
    print(f"   总操作数: {report['analysis']['total_operations']}")
    print(f"   成功率: {report['analysis'].get('success_rate', 0):.0%}")
    print(f"   覆盖率: {report['analysis'].get('override_rate', 0):.0%}")
    print(f"   偏好调整: {len(report['updates'])} 项")


if __name__ == "__main__":
    main()
