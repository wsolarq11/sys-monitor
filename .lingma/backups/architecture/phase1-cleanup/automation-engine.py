#!/usr/bin/env python3
"""
自动化决策引擎

核心功能：
1. 评估操作风险
2. 计算执行置信度
3. 选择执行策略
4. 记录决策过程
"""

import json
import time
from pathlib import Path
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"           # 风险分数 < 0.2
    MEDIUM = "medium"     # 风险分数 0.2 - 0.5
    HIGH = "high"         # 风险分数 0.5 - 0.8
    CRITICAL = "critical" # 风险分数 >= 0.8


class ExecutionStrategy(Enum):
    """执行策略"""
    AUTO_EXECUTE = "auto_execute"               # 自动执行
    EXECUTE_WITH_SNAPSHOT = "execute_with_snapshot"  # 创建快照后执行
    ASK_USER = "ask_user"                       # 询问用户
    REQUIRE_EXPLICIT_APPROVAL = "require_explicit_approval"  # 需要明确授权


class OperationType(Enum):
    """操作类型"""
    READ_FILE = "read_file"
    CREATE_FILE = "create_file"
    MODIFY_FILE = "modify_file"
    DELETE_FILE = "delete_file"
    RUN_COMMAND = "run_command"
    GIT_OPERATION = "git_operation"
    DATABASE_OPERATION = "database_operation"
    DEPLOY = "deploy"
    UPDATE_SPEC = "update_spec"
    RUN_TESTS = "run_tests"


# 风险配置
RISK_CONFIG = {
    "base_risk_scores": {
        OperationType.READ_FILE: 0.0,
        OperationType.CREATE_FILE: 0.1,
        OperationType.MODIFY_FILE: 0.2,
        OperationType.DELETE_FILE: 0.5,
        OperationType.RUN_COMMAND: 0.3,
        OperationType.GIT_OPERATION: 0.2,
        OperationType.DATABASE_OPERATION: 0.4,
        OperationType.DEPLOY: 0.7,
        OperationType.UPDATE_SPEC: 0.1,
        OperationType.RUN_TESTS: 0.1,
    },
    
    "risk_factors": {
        "modifies_production_files": 0.3,
        "deletes_files": 0.4,
        "requires_network": 0.1,
        "involves_secrets": 0.3,
        "irreversible": 0.4,
        "affects_multiple_files": 0.2,
    },
    
    "confidence_factors": {
        "has_clear_intent": 0.2,
        "has_examples": 0.15,
        "is_repetitive_task": 0.15,
        "has_validation": 0.1,
        "has_rollback_plan": 0.1,
    }
}


class AutomationEngine:
    """
    自动化决策引擎
    
    根据操作的风险和确定性，智能选择执行策略
    """
    
    def __init__(self, config_path: str = ".lingma/config/automation.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.decision_log = []
        
    def load_config(self) -> Dict[str, Any]:
        """加载自动化配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认配置（平衡模式）
        return {
            "automation_level": "balanced",
            "risk_thresholds": {
                "auto_execute": 0.2,
                "execute_with_snapshot": 0.5,
                "ask_user": 0.8
            },
            "enabled": True,
            "log_decisions": True
        }
    
    def save_config(self):
        """保存配置"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def assess_risk(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估操作风险
        
        Args:
            operation: 操作描述字典
            
        Returns:
            风险评估结果
        """
        op_type = operation.get("type", "unknown")
        details = operation.get("details", {})
        
        # 获取基础风险分数
        try:
            op_enum = OperationType(op_type)
            base_risk = RISK_CONFIG["base_risk_scores"].get(op_enum, 0.3)
        except ValueError:
            base_risk = 0.3  # 未知操作类型使用中等风险
        
        # 应用风险因子
        risk_score = base_risk
        for factor, weight in RISK_CONFIG["risk_factors"].items():
            if details.get(factor, False):
                risk_score += weight
        
        # 限制在 0-1 范围
        risk_score = min(max(risk_score, 0.0), 1.0)
        
        # 确定风险等级
        if risk_score < 0.2:
            risk_level = RiskLevel.LOW
        elif risk_score < 0.5:
            risk_level = RiskLevel.MEDIUM
        elif risk_score < 0.8:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL
        
        return {
            "risk_score": round(risk_score, 3),
            "risk_level": risk_level.value,
            "base_risk": base_risk,
            "risk_factors_applied": [
                factor for factor in RISK_CONFIG["risk_factors"].keys()
                if details.get(factor, False)
            ]
        }
    
    def calculate_confidence(self, operation: Dict[str, Any]) -> float:
        """
        计算执行置信度
        
        Args:
            operation: 操作描述字典
            
        Returns:
            置信度分数 (0-1)
        """
        details = operation.get("details", {})
        
        # 基础置信度
        confidence = 0.5
        
        # 应用置信度因子
        for factor, bonus in RISK_CONFIG["confidence_factors"].items():
            if details.get(factor, False):
                confidence += bonus
        
        # 如果有历史成功记录，增加置信度
        if details.get("has_successful_history", False):
            confidence += 0.1
        
        # 如果是不确定的操作，降低置信度
        if details.get("is_uncertain", False):
            confidence -= 0.2
        
        # 限制在 0-1 范围
        confidence = min(max(confidence, 0.0), 1.0)
        
        return round(confidence, 3)
    
    def select_strategy(self, risk_assessment: Dict, confidence: float) -> ExecutionStrategy:
        """
        选择执行策略
        
        Args:
            risk_assessment: 风险评估结果
            confidence: 置信度分数
            
        Returns:
            执行策略
        """
        risk_score = risk_assessment["risk_score"]
        thresholds = self.config["risk_thresholds"]
        
        # 根据风险分数和置信度决定策略
        if risk_score < thresholds["auto_execute"] and confidence > 0.8:
            return ExecutionStrategy.AUTO_EXECUTE
        elif risk_score < thresholds["execute_with_snapshot"]:
            return ExecutionStrategy.EXECUTE_WITH_SNAPSHOT
        elif risk_score < thresholds["ask_user"]:
            return ExecutionStrategy.ASK_USER
        else:
            return ExecutionStrategy.REQUIRE_EXPLICIT_APPROVAL
    
    def evaluate_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """
        完整评估一个操作
        
        Args:
            operation: 操作描述，包含 type 和 details
            
        Returns:
            完整的评估结果
        """
        start_time = time.time()
        
        # 检查是否启用自动化
        if not self.config.get("enabled", True):
            return {
                "strategy": ExecutionStrategy.ASK_USER.value,
                "reason": "Automation is disabled",
                "risk_assessment": None,
                "confidence": 0.0
            }
        
        # 评估风险
        risk_assessment = self.assess_risk(operation)
        
        # 计算置信度
        confidence = self.calculate_confidence(operation)
        
        # 选择策略
        strategy = self.select_strategy(risk_assessment, confidence)
        
        # 计算评估耗时
        evaluation_time = time.time() - start_time
        
        # 构建结果
        result = {
            "operation": operation,
            "strategy": strategy.value,
            "risk_assessment": risk_assessment,
            "confidence": confidence,
            "evaluation_time_ms": round(evaluation_time * 1000, 2),
            "timestamp": datetime.now().isoformat(),
            "recommendation": self._generate_recommendation(strategy, risk_assessment, confidence)
        }
        
        # 记录决策
        if self.config.get("log_decisions", True):
            self.decision_log.append(result)
            self._save_decision_log()
        
        return result
    
    def _generate_recommendation(self, strategy: ExecutionStrategy, 
                                 risk_assessment: Dict, confidence: float) -> str:
        """生成人类可读的建议"""
        
        recommendations = {
            ExecutionStrategy.AUTO_EXECUTE: 
                f"✅ 可以安全自动执行 (风险: {risk_assessment['risk_level']}, 置信度: {confidence:.0%})",
            
            ExecutionStrategy.EXECUTE_WITH_SNAPSHOT: 
                f"⚠️ 建议创建快照后执行 (风险: {risk_assessment['risk_level']}, 置信度: {confidence:.0%})",
            
            ExecutionStrategy.ASK_USER: 
                f"❓ 建议请求用户确认 (风险: {risk_assessment['risk_level']}, 置信度: {confidence:.0%})",
            
            ExecutionStrategy.REQUIRE_EXPLICIT_APPROVAL: 
                f"🚫 需要明确授权 (风险: {risk_assessment['risk_level']}, 置信度: {confidence:.0%})"
        }
        
        return recommendations.get(strategy, "未知策略")
    
    def _save_decision_log(self):
        """保存决策日志"""
        log_path = Path(".lingma/logs/decision-log.json")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 只保留最近 1000 条决策
        recent_logs = self.decision_log[-1000:]
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(recent_logs, f, indent=2, ensure_ascii=False)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取决策统计信息"""
        if not self.decision_log:
            return {"total_decisions": 0}
        
        total = len(self.decision_log)
        strategies = {}
        risk_levels = {}
        
        for decision in self.decision_log:
            strategy = decision["strategy"]
            strategies[strategy] = strategies.get(strategy, 0) + 1
            
            if decision.get("risk_assessment"):
                level = decision["risk_assessment"]["risk_level"]
                risk_levels[level] = risk_levels.get(level, 0) + 1
        
        return {
            "total_decisions": total,
            "strategy_distribution": strategies,
            "risk_level_distribution": risk_levels,
            "average_evaluation_time_ms": sum(
                d.get("evaluation_time_ms", 0) for d in self.decision_log
            ) / total if total > 0 else 0
        }
    
    def update_config(self, updates: Dict[str, Any]):
        """更新配置"""
        self.config.update(updates)
        self.save_config()
    
    def enable_automation(self):
        """启用自动化"""
        self.update_config({"enabled": True})
    
    def disable_automation(self):
        """禁用自动化"""
        self.update_config({"enabled": False})


# 便捷函数
def quick_evaluate(operation_type: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    快速评估操作
    
    Args:
        operation_type: 操作类型
        details: 操作详情
        
    Returns:
        评估结果
    """
    engine = AutomationEngine()
    operation = {
        "type": operation_type,
        "details": details or {}
    }
    return engine.evaluate_operation(operation)


if __name__ == "__main__":
    # 测试示例
    engine = AutomationEngine()
    
    # 测试低风险操作
    low_risk_op = {
        "type": "read_file",
        "details": {
            "has_clear_intent": True,
            "is_repetitive_task": True
        }
    }
    
    result = engine.evaluate_operation(low_risk_op)
    print("低风险操作评估:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    # 测试高风险操作
    high_risk_op = {
        "type": "delete_file",
        "details": {
            "deletes_files": True,
            "irreversible": True,
            "affects_multiple_files": True
        }
    }
    
    result = engine.evaluate_operation(high_risk_op)
    print("高风险操作评估:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    # 显示统计
    stats = engine.get_statistics()
    print("决策统计:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
