#!/usr/bin/env python3
"""
AI Agent Cost Optimization & Budget Management System - AI Agent 成本优化与预算管理系统

Token 使用追踪、成本控制、预算管理、智能路由
实现生产级 AI Agent 的成本优化框架

参考社区最佳实践:
- Token usage tracking and billing
- Budget control with soft/hard limits
- Smart model routing based on cost-performance
- Prompt compression and caching
- Cost attribution by project/team/app
"""

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import statistics

logger = logging.getLogger(__name__)


class BudgetLimitType(Enum):
    """预算限制类型"""
    SOFT_LIMIT = "soft_limit"  # 软限制（告警）
    HARD_LIMIT = "hard_limit"  # 硬限制（拒绝）


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ModelTier(Enum):
    """模型层级"""
    PREMIUM = "premium"  # 高性能高成本 (GPT-4/Claude Opus)
    STANDARD = "standard"  # 标准性能中等成本 (GPT-3.5/Claude Sonnet)
    ECONOMY = "economy"  # 基础性能低成本 (GPT-3.5-turbo/Claude Haiku)


@dataclass
class TokenUsage:
    """Token 使用记录"""
    usage_id: str
    timestamp: str
    model_name: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    user_id: Optional[str] = None
    app_id: Optional[str] = None
    project_id: Optional[str] = None
    workflow_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.total_tokens == 0:
            self.total_tokens = self.input_tokens + self.output_tokens
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class BudgetConfig:
    """预算配置"""
    budget_id: str
    name: str
    monthly_budget_usd: float
    alert_thresholds: List[float] = field(default_factory=lambda: [0.8, 0.9, 1.0])  # 80%, 90%, 100%
    limit_type: BudgetLimitType = BudgetLimitType.SOFT_LIMIT
    scope_type: str = "global"  # global/project/team/user
    scope_id: Optional[str] = None
    reset_day: int = 1  # 每月重置日
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class CostAlert:
    """成本告警"""
    alert_id: str
    budget_id: str
    alert_level: AlertLevel
    message: str
    current_usage_usd: float
    budget_usd: float
    usage_percentage: float
    triggered_at: str
    action_taken: Optional[str] = None  # notified/blocked/none
    
    def __post_init__(self):
        if not self.triggered_at:
            self.triggered_at = datetime.now(timezone.utc).isoformat()


@dataclass
class ModelPricing:
    """模型定价"""
    model_name: str
    tier: ModelTier
    input_price_per_1k: float  # 每1K输入token价格
    output_price_per_1k: float  # 每1K输出token价格
    context_window: int  # 上下文窗口大小
    max_output_tokens: int
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """计算成本"""
        input_cost = (input_tokens / 1000) * self.input_price_per_1k
        output_cost = (output_tokens / 1000) * self.output_price_per_1k
        return round(input_cost + output_cost, 6)


class TokenTracker:
    """Token 追踪器
    
    记录和追踪所有 Token 使用情况
    """
    
    def __init__(self):
        self.usage_records: List[TokenUsage] = []
        self.model_pricing: Dict[str, ModelPricing] = {}
        self._init_default_pricing()
    
    def _init_default_pricing(self):
        """初始化默认定价"""
        # OpenAI 定价 (2024-2025)
        self.model_pricing["gpt-4o"] = ModelPricing(
            model_name="gpt-4o",
            tier=ModelTier.PREMIUM,
            input_price_per_1k=0.0025,
            output_price_per_1k=0.01,
            context_window=128000,
            max_output_tokens=16384
        )
        
        self.model_pricing["gpt-4-turbo"] = ModelPricing(
            model_name="gpt-4-turbo",
            tier=ModelTier.PREMIUM,
            input_price_per_1k=0.01,
            output_price_per_1k=0.03,
            context_window=128000,
            max_output_tokens=4096
        )
        
        self.model_pricing["gpt-3.5-turbo"] = ModelPricing(
            model_name="gpt-3.5-turbo",
            tier=ModelTier.ECONOMY,
            input_price_per_1k=0.0005,
            output_price_per_1k=0.0015,
            context_window=16385,
            max_output_tokens=4096
        )
        
        # Anthropic 定价 (2024-2025)
        self.model_pricing["claude-3-opus"] = ModelPricing(
            model_name="claude-3-opus",
            tier=ModelTier.PREMIUM,
            input_price_per_1k=0.015,
            output_price_per_1k=0.075,
            context_window=200000,
            max_output_tokens=4096
        )
        
        self.model_pricing["claude-3-sonnet"] = ModelPricing(
            model_name="claude-3-sonnet",
            tier=ModelTier.STANDARD,
            input_price_per_1k=0.003,
            output_price_per_1k=0.015,
            context_window=200000,
            max_output_tokens=4096
        )
        
        self.model_pricing["claude-3-haiku"] = ModelPricing(
            model_name="claude-3-haiku",
            tier=ModelTier.ECONOMY,
            input_price_per_1k=0.00025,
            output_price_per_1k=0.00125,
            context_window=200000,
            max_output_tokens=4096
        )
    
    def record_usage(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        user_id: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        metadata: Dict = None
    ) -> TokenUsage:
        """
        记录 Token 使用
        
        Args:
            model_name: 模型名称
            input_tokens: 输入 token 数
            output_tokens: 输出 token 数
            user_id: 用户ID
            app_id: 应用ID
            project_id: 项目ID
            workflow_id: 工作流ID
            metadata: 额外元数据
            
        Returns:
            Token 使用记录
        """
        # 获取定价
        pricing = self.model_pricing.get(model_name)
        
        if not pricing:
            logger.warning(f"Unknown model: {model_name}, using default pricing")
            # 默认定价
            cost = (input_tokens + output_tokens) / 1000 * 0.002
        else:
            cost = pricing.calculate_cost(input_tokens, output_tokens)
        
        # 创建记录
        usage = TokenUsage(
            usage_id=str(uuid.uuid4()),
            timestamp="",  # 会自动生成
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=0,  # 会自动计算
            cost_usd=cost,
            user_id=user_id,
            app_id=app_id,
            project_id=project_id,
            workflow_id=workflow_id,
            metadata=metadata or {}
        )
        
        self.usage_records.append(usage)
        
        logger.debug(f"Recorded usage: {model_name} - {usage.total_tokens} tokens - ${cost:.6f}")
        
        return usage
    
    def get_usage_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        filter_by: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        获取使用摘要
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            filter_by: 过滤条件 (user_id/app_id/project_id)
            
        Returns:
            使用摘要
        """
        records = self.usage_records
        
        # 日期过滤
        if start_date:
            records = [r for r in records if datetime.fromisoformat(r.timestamp.replace('Z', '+00:00')) >= start_date]
        
        if end_date:
            records = [r for r in records if datetime.fromisoformat(r.timestamp.replace('Z', '+00:00')) <= end_date]
        
        # 属性过滤
        if filter_by:
            for key, value in filter_by.items():
                if hasattr(records[0], key) if records else False:
                    records = [r for r in records if getattr(r, key) == value]
        
        if not records:
            return {
                "total_tokens": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost_usd": 0.0,
                "record_count": 0
            }
        
        # 计算统计信息
        total_tokens = sum(r.total_tokens for r in records)
        total_input = sum(r.input_tokens for r in records)
        total_output = sum(r.output_tokens for r in records)
        total_cost = sum(r.cost_usd for r in records)
        
        # 按模型分组
        by_model = {}
        for r in records:
            if r.model_name not in by_model:
                by_model[r.model_name] = {"tokens": 0, "cost": 0.0, "count": 0}
            by_model[r.model_name]["tokens"] += r.total_tokens
            by_model[r.model_name]["cost"] += r.cost_usd
            by_model[r.model_name]["count"] += 1
        
        return {
            "total_tokens": total_tokens,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_cost_usd": round(total_cost, 6),
            "record_count": len(records),
            "by_model": by_model,
            "avg_tokens_per_request": round(total_tokens / len(records), 2),
            "avg_cost_per_request": round(total_cost / len(records), 6)
        }
    
    def get_cost_by_dimension(self, dimension: str) -> Dict[str, float]:
        """
        按维度获取成本
        
        Args:
            dimension: 维度 (user_id/app_id/project_id)
            
        Returns:
            各维度的成本
        """
        costs = {}
        
        for record in self.usage_records:
            dim_value = getattr(record, dimension, None)
            
            if dim_value:
                if dim_value not in costs:
                    costs[dim_value] = 0.0
                costs[dim_value] += record.cost_usd
        
        # 四舍五入
        return {k: round(v, 6) for k, v in costs.items()}


class BudgetManager:
    """预算管理器
    
    管理预算、监控使用、触发告警
    """
    
    def __init__(self, token_tracker: TokenTracker):
        self.token_tracker = token_tracker
        self.budgets: Dict[str, BudgetConfig] = {}
        self.alerts: List[CostAlert] = []
    
    def create_budget(self, config: BudgetConfig) -> BudgetConfig:
        """创建预算"""
        self.budgets[config.budget_id] = config
        logger.info(f"Budget created: {config.name} - ${config.monthly_budget_usd:.2f}/month")
        return config
    
    def check_budget(self, budget_id: str) -> Tuple[bool, Optional[CostAlert]]:
        """
        检查预算状态
        
        Args:
            budget_id: 预算ID
            
        Returns:
            (是否在预算内, 告警对象)
        """
        budget = self.budgets.get(budget_id)
        
        if not budget:
            raise ValueError(f"Budget not found: {budget_id}")
        
        if not budget.enabled:
            return True, None
        
        # 获取当前月份的使用情况
        now = datetime.now(timezone.utc)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # 根据范围过滤
        filter_by = {}
        if budget.scope_type != "global":
            filter_by[budget.scope_type] = budget.scope_id
        
        summary = self.token_tracker.get_usage_summary(
            start_date=start_of_month,
            filter_by=filter_by if filter_by else None
        )
        
        current_usage = summary["total_cost_usd"]
        usage_percentage = current_usage / budget.monthly_budget_usd if budget.monthly_budget_usd > 0 else 0
        
        # 检查是否超过阈值
        alert = None
        
        for threshold in sorted(budget.alert_thresholds, reverse=True):
            if usage_percentage >= threshold:
                # 确定告警级别
                if threshold >= 1.0:
                    level = AlertLevel.CRITICAL
                elif threshold >= 0.9:
                    level = AlertLevel.WARNING
                else:
                    level = AlertLevel.INFO
                
                # 创建告警
                alert = CostAlert(
                    alert_id=str(uuid.uuid4()),
                    budget_id=budget_id,
                    alert_level=level,
                    message=f"Budget usage at {usage_percentage*100:.1f}% (${current_usage:.2f}/${budget.monthly_budget_usd:.2f})",
                    current_usage_usd=current_usage,
                    budget_usd=budget.monthly_budget_usd,
                    usage_percentage=round(usage_percentage * 100, 2),
                    triggered_at=""
                )
                
                # 执行相应操作
                if budget.limit_type == BudgetLimitType.HARD_LIMIT and threshold >= 1.0:
                    alert.action_taken = "blocked"
                    logger.warning(f"Hard limit reached for budget {budget_id}. Blocking further usage.")
                else:
                    alert.action_taken = "notified"
                    logger.info(f"Budget alert: {alert.message}")
                
                self.alerts.append(alert)
                
                break
        
        # 如果超过100%，返回失败
        in_budget = usage_percentage < 1.0 or budget.limit_type == BudgetLimitType.SOFT_LIMIT
        
        return in_budget, alert
    
    def get_alerts(self, budget_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """获取告警历史"""
        alerts = self.alerts
        
        if budget_id:
            alerts = [a for a in alerts if a.budget_id == budget_id]
        
        recent = alerts[-limit:]
        
        return [
            {
                "alert_id": a.alert_id,
                "budget_id": a.budget_id,
                "level": a.alert_level.value,
                "message": a.message,
                "usage_percentage": a.usage_percentage,
                "triggered_at": a.triggered_at,
                "action_taken": a.action_taken
            }
            for a in recent
        ]


class SmartRouter:
    """智能路由器
    
    基于成本效益自动选择模型
    """
    
    def __init__(self, token_tracker: TokenTracker):
        self.token_tracker = token_tracker
        self.task_complexity_cache: Dict[str, ModelTier] = {}
    
    def select_model(
        self,
        task_description: str,
        complexity: Optional[str] = None,
        budget_constraint: Optional[float] = None
    ) -> str:
        """
        智能选择模型
        
        Args:
            task_description: 任务描述
            complexity: 复杂度 (simple/medium/complex)
            budget_constraint: 预算约束
            
        Returns:
            推荐的模型名称
        """
        # 如果没有指定复杂度，尝试推断
        if not complexity:
            complexity = self._infer_complexity(task_description)
        
        # 基于复杂度选择模型层级
        if complexity == "simple":
            tier = ModelTier.ECONOMY
        elif complexity == "medium":
            tier = ModelTier.STANDARD
        else:  # complex
            tier = ModelTier.PREMIUM
        
        # 如果有预算约束，选择最便宜的合适模型
        if budget_constraint:
            return self._select_cheapest_in_tier(tier, budget_constraint)
        
        # 否则选择该层级的代表性模型
        return self._get_representative_model(tier)
    
    def _infer_complexity(self, task_description: str) -> str:
        """推断任务复杂度"""
        description_lower = task_description.lower()
        
        # 简单任务关键词
        simple_keywords = ["read file", "format", "simple", "basic", "extract"]
        if any(kw in description_lower for kw in simple_keywords):
            return "simple"
        
        # 复杂任务关键词
        complex_keywords = ["analyze", "reason", "complex", "creative", "generate code", "debug"]
        if any(kw in description_lower for kw in complex_keywords):
            return "complex"
        
        # 默认中等
        return "medium"
    
    def _select_cheapest_in_tier(self, tier: ModelTier, max_cost: float) -> str:
        """在指定层级中选择最便宜的模型"""
        candidates = [
            (name, pricing)
            for name, pricing in self.token_tracker.model_pricing.items()
            if pricing.tier == tier
        ]
        
        if not candidates:
            # 降级到更便宜的层级
            if tier == ModelTier.PREMIUM:
                return self._select_cheapest_in_tier(ModelTier.STANDARD, max_cost)
            elif tier == ModelTier.STANDARD:
                return self._select_cheapest_in_tier(ModelTier.ECONOMY, max_cost)
            else:
                return "gpt-3.5-turbo"  # 默认
        
        # 选择最便宜的
        cheapest = min(candidates, key=lambda x: x[1].input_price_per_1k)
        
        return cheapest[0]
    
    def _get_representative_model(self, tier: ModelTier) -> str:
        """获取层级的代表性模型"""
        representatives = {
            ModelTier.PREMIUM: "gpt-4o",
            ModelTier.STANDARD: "claude-3-sonnet",
            ModelTier.ECONOMY: "gpt-3.5-turbo"
        }
        
        return representatives.get(tier, "gpt-3.5-turbo")


class CostOptimizer:
    """成本优化器
    
    提供成本优化建议和自动化
    """
    
    def __init__(self, token_tracker: TokenTracker):
        self.token_tracker = token_tracker
    
    def analyze_optimization_opportunities(self) -> Dict:
        """分析优化机会"""
        summary = self.token_tracker.get_usage_summary()
        
        opportunities = []
        
        # 1. 检查是否有高成本模型用于简单任务
        by_model = summary.get("by_model", {})
        
        premium_models = [name for name in by_model.keys() if "gpt-4" in name or "opus" in name]
        economy_models = [name for name in by_model.keys() if "3.5" in name or "haiku" in name]
        
        if premium_models and not economy_models:
            opportunities.append({
                "type": "model_downgrade",
                "severity": "high",
                "description": "Only using premium models. Consider using economy models for simple tasks.",
                "potential_savings": "Up to 80% cost reduction"
            })
        
        # 2. 检查平均 token 使用量
        avg_tokens = summary.get("avg_tokens_per_request", 0)
        
        if avg_tokens > 10000:
            opportunities.append({
                "type": "prompt_compression",
                "severity": "medium",
                "description": f"High average token usage ({avg_tokens:.0f}). Consider prompt compression.",
                "potential_savings": "30-50% token reduction"
            })
        
        # 3. 检查是否有重复请求（可以通过缓存优化）
        # 这里简化处理，实际应分析请求内容相似度
        
        return {
            "opportunities": opportunities,
            "current_summary": summary
        }
    
    def estimate_cost_savings(self, optimization_type: str, current_usage: Dict) -> float:
        """估算优化后的成本节省"""
        current_cost = current_usage.get("total_cost_usd", 0)
        
        savings_rates = {
            "model_downgrade": 0.8,  # 80% 节省
            "prompt_compression": 0.4,  # 40% 节省
            "caching": 0.3,  # 30% 节省
            "batch_processing": 0.2  # 20% 节省
        }
        
        rate = savings_rates.get(optimization_type, 0)
        
        return round(current_cost * rate, 6)


class CostManagementEngine:
    """成本管理引擎
    
    整合 Token 追踪、预算管理、智能路由、成本优化的完整系统
    """
    
    def __init__(self):
        self.token_tracker = TokenTracker()
        self.budget_manager = BudgetManager(self.token_tracker)
        self.smart_router = SmartRouter(self.token_tracker)
        self.cost_optimizer = CostOptimizer(self.token_tracker)
    
    def track_llm_call(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        **kwargs
    ) -> Dict:
        """
        追踪 LLM 调用
        
        Args:
            model_name: 模型名称
            input_tokens: 输入 token 数
            output_tokens: 输出 token 数
            **kwargs: 其他参数 (user_id, app_id, project_id, etc.)
            
        Returns:
            追踪结果
        """
        # 记录使用
        usage = self.token_tracker.record_usage(
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            **kwargs
        )
        
        # 检查预算
        budget_alerts = []
        
        for budget_id in self.budget_manager.budgets.keys():
            in_budget, alert = self.budget_manager.check_budget(budget_id)
            
            if alert:
                budget_alerts.append(alert.to_dict() if hasattr(alert, 'to_dict') else asdict(alert))
            
            if not in_budget:
                logger.warning(f"Budget exceeded for {budget_id}")
        
        return {
            "usage_id": usage.usage_id,
            "model": model_name,
            "tokens": usage.total_tokens,
            "cost_usd": usage.cost_usd,
            "alerts": budget_alerts
        }
    
    def recommend_model(self, task_description: str, **kwargs) -> Dict:
        """推荐模型"""
        recommended_model = self.smart_router.select_model(task_description, **kwargs)
        
        pricing = self.token_tracker.model_pricing.get(recommended_model)
        
        return {
            "recommended_model": recommended_model,
            "tier": pricing.tier.value if pricing else "unknown",
            "estimated_cost_per_1k_input": pricing.input_price_per_1k if pricing else 0,
            "estimated_cost_per_1k_output": pricing.output_price_per_1k if pricing else 0
        }
    
    def get_cost_dashboard(self) -> Dict:
        """获取成本仪表板"""
        # 获取总体使用情况
        summary = self.token_tracker.get_usage_summary()
        
        # 获取按维度分组的成本
        cost_by_app = self.token_tracker.get_cost_by_dimension("app_id")
        cost_by_project = self.token_tracker.get_cost_by_dimension("project_id")
        cost_by_user = self.token_tracker.get_cost_by_dimension("user_id")
        
        # 获取优化建议
        optimization = self.cost_optimizer.analyze_optimization_opportunities()
        
        # 获取最近的告警
        recent_alerts = self.budget_manager.get_alerts(limit=5)
        
        return {
            "summary": summary,
            "cost_by_app": cost_by_app,
            "cost_by_project": cost_by_project,
            "cost_by_user": cost_by_user,
            "optimization_opportunities": optimization["opportunities"],
            "recent_alerts": recent_alerts,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def setup_budget(self, **kwargs) -> BudgetConfig:
        """设置预算"""
        config = BudgetConfig(**kwargs)
        return self.budget_manager.create_budget(config)


def create_cost_management_engine() -> CostManagementEngine:
    """工厂函数：创建成本管理引擎"""
    return CostManagementEngine()


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Cost Optimization 测试")
    print("="*60)
    
    engine = create_cost_management_engine()
    
    # 设置预算
    print("\n💰 设置预算...")
    budget = engine.setup_budget(
        budget_id=str(uuid.uuid4()),
        name="Project Alpha Budget",
        monthly_budget_usd=100.0,
        alert_thresholds=[0.8, 0.9, 1.0],
        limit_type=BudgetLimitType.SOFT_LIMIT,
        scope_type="project",
        scope_id="proj_alpha"
    )
    
    print(f"   预算: ${budget.monthly_budget_usd:.2f}/month")
    
    # 模拟一些 LLM 调用
    print("\n📊 模拟 LLM 调用...")
    
    calls = [
        {"model": "gpt-4o", "input": 1000, "output": 500, "app": "chatbot", "project": "proj_alpha"},
        {"model": "gpt-3.5-turbo", "input": 500, "output": 200, "app": "chatbot", "project": "proj_alpha"},
        {"model": "claude-3-sonnet", "input": 2000, "output": 1000, "app": "analyzer", "project": "proj_alpha"},
        {"model": "gpt-4o", "input": 1500, "output": 800, "app": "coder", "project": "proj_beta"},
    ]
    
    for call in calls:
        result = engine.track_llm_call(
            model_name=call["model"],
            input_tokens=call["input"],
            output_tokens=call["output"],
            app_id=call["app"],
            project_id=call["project"]
        )
        print(f"   {call['model']}: {result['tokens']} tokens - ${result['cost_usd']:.6f}")
    
    # 获取成本仪表板
    print("\n📈 成本仪表板:")
    dashboard = engine.get_cost_dashboard()
    
    print(f"\n   总成本: ${dashboard['summary']['total_cost_usd']:.6f}")
    print(f"   总 Token: {dashboard['summary']['total_tokens']}")
    print(f"   平均每次请求: {dashboard['summary']['avg_tokens_per_request']:.0f} tokens")
    
    print(f"\n   按应用分组:")
    for app, cost in dashboard['cost_by_app'].items():
        print(f"     - {app}: ${cost:.6f}")
    
    print(f"\n   按项目分组:")
    for proj, cost in dashboard['cost_by_project'].items():
        print(f"     - {proj}: ${cost:.6f}")
    
    # 模型推荐
    print("\n🎯 模型推荐:")
    
    tasks = [
        "Read a file and extract text",
        "Analyze customer feedback sentiment",
        "Generate creative marketing copy"
    ]
    
    for task in tasks:
        rec = engine.recommend_model(task)
        print(f"   Task: {task[:40]}...")
        print(f"     → {rec['recommended_model']} ({rec['tier']})")
    
    # 优化建议
    print("\n💡 优化建议:")
    optimization = engine.cost_optimizer.analyze_optimization_opportunities()
    
    if optimization["opportunities"]:
        for opp in optimization["opportunities"]:
            print(f"   ⚠️  [{opp['severity'].upper()}] {opp['description']}")
            print(f"      Potential savings: {opp['potential_savings']}")
    else:
        print("   ✅ No optimization opportunities found")
    
    print("\n✅ 测试完成！")
