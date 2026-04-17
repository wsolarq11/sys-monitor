#!/usr/bin/env python3
"""
Agent Observability System - Agent 可观测性系统

分布式追踪、指标监控、日志记录、性能分析
实现生产级 AI Agent 的完整可观测性

参考社区最佳实践:
- OpenTelemetry GenAI semantic conventions
- Distributed tracing for agent workflows
- Real-time metrics and alerts
- Comprehensive logging and evaluation
"""

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from collections import defaultdict
import uuid
import hashlib

logger = logging.getLogger(__name__)


class SpanType(Enum):
    """Span 类型"""
    AGENT = "agent"  # Agent 执行
    LLM = "llm"  # LLM 调用
    TOOL = "tool"  # 工具调用
    MEMORY = "memory"  # 记忆操作
    EVALUATION = "evaluation"  # 评估
    WORKFLOW = "workflow"  # 工作流


class SpanStatus(Enum):
    """Span 状态"""
    OK = "ok"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class SpanEvent:
    """Span 事件"""
    event_id: str
    name: str
    timestamp: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpanLink:
    """Span 链接"""
    trace_id: str
    span_id: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """Span - 追踪单元
    
    遵循 OpenTelemetry GenAI 语义规范
    """
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    name: str
    span_type: SpanType
    start_time: str
    end_time: Optional[str] = None
    status: SpanStatus = SpanStatus.OK
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[SpanEvent] = field(default_factory=list)
    links: List[SpanLink] = field(default_factory=list)
    
    # GenAI 特定属性
    model_name: Optional[str] = None
    token_usage: Optional[Dict[str, int]] = None
    tool_name: Optional[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if not self.trace_id:
            self.trace_id = str(uuid.uuid4())
        if not self.span_id:
            self.span_id = str(uuid.uuid4())[:16]
    
    def duration_ms(self) -> Optional[float]:
        """计算持续时间（毫秒）"""
        if not self.end_time:
            return None
        
        start = datetime.fromisoformat(self.start_time)
        end = datetime.fromisoformat(self.end_time)
        
        return (end - start).total_seconds() * 1000
    
    def add_event(self, name: str, attributes: Dict = None):
        """添加事件"""
        event = SpanEvent(
            event_id=str(uuid.uuid4()),
            name=name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            attributes=attributes or {}
        )
        self.events.append(event)
    
    def set_error(self, error_message: str):
        """设置错误"""
        self.status = SpanStatus.ERROR
        self.error_message = error_message
        self.add_event("error", {"message": error_message})
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "span_type": self.span_type.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms(),
            "status": self.status.value,
            "attributes": self.attributes,
            "events_count": len(self.events),
            "links_count": len(self.links),
            "model_name": self.model_name,
            "token_usage": self.token_usage,
            "tool_name": self.tool_name,
            "error_message": self.error_message
        }


@dataclass
class Trace:
    """Trace - 完整追踪链路"""
    trace_id: str
    root_span_id: str
    spans: Dict[str, Span] = field(default_factory=dict)
    start_time: str = ""
    end_time: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.start_time:
            self.start_time = datetime.now(timezone.utc).isoformat()
    
    def add_span(self, span: Span):
        """添加 Span"""
        self.spans[span.span_id] = span
    
    def get_span_tree(self) -> List[Dict]:
        """获取 Span 树结构"""
        tree = []
        
        # 找到根 Span
        root_spans = [s for s in self.spans.values() if not s.parent_span_id]
        
        for root in root_spans:
            tree.append(self._build_span_tree(root))
        
        return tree
    
    def _build_span_tree(self, span: Span, depth: int = 0) -> Dict:
        """递归构建 Span 树"""
        children = [
            s for s in self.spans.values()
            if s.parent_span_id == span.span_id
        ]
        
        return {
            "span_id": span.span_id,
            "name": span.name,
            "type": span.span_type.value,
            "duration_ms": span.duration_ms(),
            "status": span.status.value,
            "depth": depth,
            "children": [self._build_span_tree(c, depth + 1) for c in children]
        }
    
    def total_duration_ms(self) -> Optional[float]:
        """计算总持续时间"""
        if not self.end_time:
            return None
        
        start = datetime.fromisoformat(self.start_time)
        end = datetime.fromisoformat(self.end_time)
        
        return (end - start).total_seconds() * 1000
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "trace_id": self.trace_id,
            "root_span_id": self.root_span_id,
            "spans_count": len(self.spans),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_duration_ms": self.total_duration_ms(),
            "metadata": self.metadata,
            "span_tree": self.get_span_tree()
        }


@dataclass
class MetricPoint:
    """指标数据点"""
    metric_name: str
    value: float
    timestamp: str
    labels: Dict[str, str] = field(default_factory=dict)
    unit: Optional[str] = None


class MetricsCollector:
    """指标收集器
    
    收集和聚合关键指标
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Dict = None):
        """增加计数器"""
        key = self._make_key(name, labels)
        self.counters[key] += value
    
    def set_gauge(self, name: str, value: float, labels: Dict = None):
        """设置仪表盘"""
        key = self._make_key(name, labels)
        self.gauges[key] = value
    
    def record_histogram(self, name: str, value: float, labels: Dict = None):
        """记录直方图"""
        key = self._make_key(name, labels)
        self.histograms[key].append(value)
    
    def record_metric(self, metric: MetricPoint):
        """记录指标点"""
        self.metrics[metric.metric_name].append(metric)
    
    def _make_key(self, name: str, labels: Dict = None) -> str:
        """生成指标键"""
        if not labels:
            return name
        
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def get_counter(self, name: str, labels: Dict = None) -> float:
        """获取计数器值"""
        key = self._make_key(name, labels)
        return self.counters.get(key, 0.0)
    
    def get_gauge(self, name: str, labels: Dict = None) -> Optional[float]:
        """获取仪表盘值"""
        key = self._make_key(name, labels)
        return self.gauges.get(key)
    
    def get_histogram_stats(self, name: str, labels: Dict = None) -> Dict:
        """获取直方图统计"""
        key = self._make_key(name, labels)
        values = self.histograms.get(key, [])
        
        if not values:
            return {"count": 0}
        
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "p50": sorted(values)[len(values) // 2],
            "p95": sorted(values)[int(len(values) * 0.95)],
            "p99": sorted(values)[int(len(values) * 0.99)]
        }
    
    def get_all_metrics(self) -> Dict:
        """获取所有指标"""
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {
                key: self.get_histogram_stats_from_values(values)
                for key, values in self.histograms.items()
            }
        }
    
    def get_histogram_stats_from_values(self, values: List[float]) -> Dict:
        """从值列表获取直方图统计"""
        if not values:
            return {"count": 0}
        
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values)
        }


class AlertRule:
    """告警规则"""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        metric_name: str,
        condition: str,
        threshold: float,
        severity: str = "warning",
        cooldown_seconds: int = 300
    ):
        self.rule_id = rule_id
        self.name = name
        self.metric_name = metric_name
        self.condition = condition  # "gt", "lt", "eq"
        self.threshold = threshold
        self.severity = severity
        self.cooldown_seconds = cooldown_seconds
        self.last_triggered: Optional[float] = None
        self.trigger_count: int = 0
    
    def should_trigger(self, current_value: float) -> bool:
        """检查是否应该触发告警"""
        # 检查冷却时间
        if self.last_triggered:
            elapsed = time.time() - self.last_triggered
            if elapsed < self.cooldown_seconds:
                return False
        
        # 检查条件
        triggered = False
        if self.condition == "gt" and current_value > self.threshold:
            triggered = True
        elif self.condition == "lt" and current_value < self.threshold:
            triggered = True
        elif self.condition == "eq" and abs(current_value - self.threshold) < 0.001:
            triggered = True
        
        if triggered:
            self.last_triggered = time.time()
            self.trigger_count += 1
        
        return triggered
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "metric_name": self.metric_name,
            "condition": self.condition,
            "threshold": self.threshold,
            "severity": self.severity,
            "trigger_count": self.trigger_count
        }


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: List[Dict] = []
    
    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.rules[rule.rule_id] = rule
        logger.info(f"Alert rule added: {rule.name}")
    
    def remove_rule(self, rule_id: str):
        """移除告警规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Alert rule removed: {rule_id}")
    
    def check_alerts(self, metrics_collector: MetricsCollector) -> List[Dict]:
        """检查告警"""
        new_alerts = []
        
        for rule in self.rules.values():
            # 获取当前指标值
            current_value = metrics_collector.get_counter(rule.metric_name)
            
            if rule.should_trigger(current_value):
                alert = {
                    "alert_id": str(uuid.uuid4()),
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "metric_name": rule.metric_name,
                    "current_value": current_value,
                    "threshold": rule.threshold,
                    "severity": rule.severity,
                    "triggered_at": datetime.now(timezone.utc).isoformat()
                }
                
                self.alerts.append(alert)
                new_alerts.append(alert)
                
                logger.warning(f"Alert triggered: {rule.name} (value={current_value}, threshold={rule.threshold})")
        
        return new_alerts
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """获取最近的告警"""
        return self.alerts[-limit:]


class TraceStore:
    """追踪存储
    
    存储和查询追踪数据
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else Path("./traces")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.traces: Dict[str, Trace] = {}
        self.trace_index: Dict[str, List[str]] = defaultdict(list)  # attribute -> trace_ids
    
    def store_trace(self, trace: Trace):
        """存储追踪"""
        self.traces[trace.trace_id] = trace
        
        # 建立索引
        for key, value in trace.metadata.items():
            self.trace_index[f"{key}:{value}"].append(trace.trace_id)
        
        # 持久化到文件
        file_path = self.storage_path / f"{trace.trace_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(trace.to_dict(), f, indent=2, ensure_ascii=False, default=str)
        
        logger.debug(f"Trace stored: {trace.trace_id}")
    
    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """获取追踪"""
        return self.traces.get(trace_id)
    
    def search_traces(self, filters: Dict = None) -> List[Trace]:
        """搜索追踪"""
        if not filters:
            return list(self.traces.values())
        
        results = []
        for trace in self.traces.values():
            match = True
            
            for key, value in filters.items():
                if key in trace.metadata:
                    if trace.metadata[key] != value:
                        match = False
                        break
                elif key == "status":
                    # 检查是否有错误状态的 Span
                    has_error = any(s.status == SpanStatus.ERROR for s in trace.spans.values())
                    if value == "error" and not has_error:
                        match = False
                        break
                else:
                    match = False
                    break
            
            if match:
                results.append(trace)
        
        return results
    
    def get_trace_count(self) -> int:
        """获取追踪数量"""
        return len(self.traces)


class ObservabilityEngine:
    """可观测性引擎
    
    整合追踪、指标、告警的完整系统
    """
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.alert_manager = AlertManager()
        self.trace_store = TraceStore()
        
        self.active_traces: Dict[str, Trace] = {}
        self.current_spans: Dict[str, Span] = {}  # span_id -> Span
        
        # 初始化默认告警规则
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """设置默认告警规则"""
        # 高错误率告警
        self.alert_manager.add_rule(AlertRule(
            rule_id="high-error-rate",
            name="High Error Rate",
            metric_name="agent.errors",
            condition="gt",
            threshold=10,
            severity="critical"
        ))
        
        # 高延迟告警
        self.alert_manager.add_rule(AlertRule(
            rule_id="high-latency",
            name="High Latency",
            metric_name="agent.latency.p95",
            condition="gt",
            threshold=5000,  # 5秒
            severity="warning"
        ))
    
    def start_trace(self, name: str, metadata: Dict = None) -> str:
        """开始追踪"""
        trace_id = str(uuid.uuid4())
        
        trace = Trace(
            trace_id=trace_id,
            root_span_id="",  # 将在第一个 span 中设置
            metadata=metadata or {}
        )
        
        self.active_traces[trace_id] = trace
        
        logger.info(f"Trace started: {name} ({trace_id})")
        
        return trace_id
    
    def start_span(
        self,
        trace_id: str,
        name: str,
        span_type: SpanType,
        parent_span_id: Optional[str] = None,
        attributes: Dict = None
    ) -> str:
        """开始 Span"""
        trace = self.active_traces.get(trace_id)
        if not trace:
            raise ValueError(f"Trace not found: {trace_id}")
        
        span = Span(
            trace_id=trace_id,
            span_id="",  # 自动生成
            parent_span_id=parent_span_id,
            name=name,
            span_type=span_type,
            start_time=datetime.now(timezone.utc).isoformat(),
            attributes=attributes or {}
        )
        
        # 如果是第一个 span，设置为根 span
        if not trace.root_span_id:
            trace.root_span_id = span.span_id
        
        trace.add_span(span)
        self.current_spans[span.span_id] = span
        
        # 记录指标
        self.metrics.increment_counter(f"spans.started.{span_type.value}")
        
        return span.span_id
    
    def end_span(self, span_id: str, status: SpanStatus = SpanStatus.OK, error: str = None):
        """结束 Span"""
        span = self.current_spans.get(span_id)
        if not span:
            logger.warning(f"Span not found: {span_id}")
            return
        
        span.end_time = datetime.now(timezone.utc).isoformat()
        span.status = status
        
        if error:
            span.set_error(error)
        
        # 记录指标
        duration = span.duration_ms()
        if duration is not None:
            self.metrics.record_histogram(
                f"spans.duration.{span.span_type.value}",
                duration
            )
        
        if status == SpanStatus.ERROR:
            self.metrics.increment_counter("agent.errors")
        
        # 从当前 spans 中移除
        if span_id in self.current_spans:
            del self.current_spans[span_id]
        
        logger.debug(f"Span ended: {span.name} ({span_id})")
    
    def end_trace(self, trace_id: str):
        """结束追踪"""
        trace = self.active_traces.get(trace_id)
        if not trace:
            logger.warning(f"Trace not found: {trace_id}")
            return
        
        trace.end_time = datetime.now(timezone.utc).isoformat()
        
        # 存储追踪
        self.trace_store.store_trace(trace)
        
        # 记录指标
        duration = trace.total_duration_ms()
        if duration is not None:
            self.metrics.record_histogram("trace.duration", duration)
        
        # 从 active traces 中移除
        if trace_id in self.active_traces:
            del self.active_traces[trace_id]
        
        logger.info(f"Trace ended: {trace_id} (duration={duration:.2f}ms)")
    
    def record_llm_call(
        self,
        trace_id: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        parent_span_id: Optional[str] = None
    ):
        """记录 LLM 调用"""
        span_id = self.start_span(
            trace_id=trace_id,
            name=f"LLM:{model_name}",
            span_type=SpanType.LLM,
            parent_span_id=parent_span_id,
            attributes={
                "gen_ai.system": "openai",  # 示例
                "gen_ai.request.model": model_name
            }
        )
        
        span = self.current_spans.get(span_id)
        if span:
            span.model_name = model_name
            span.token_usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        
        # 记录指标
        self.metrics.increment_counter("llm.calls")
        self.metrics.increment_counter("llm.tokens.prompt", prompt_tokens)
        self.metrics.increment_counter("llm.tokens.completion", completion_tokens)
        self.metrics.record_histogram("llm.latency", latency_ms)
        
        self.end_span(span_id)
    
    def record_tool_call(
        self,
        trace_id: str,
        tool_name: str,
        success: bool,
        latency_ms: float,
        parent_span_id: Optional[str] = None
    ):
        """记录工具调用"""
        span_id = self.start_span(
            trace_id=trace_id,
            name=f"Tool:{tool_name}",
            span_type=SpanType.TOOL,
            parent_span_id=parent_span_id
        )
        
        span = self.current_spans.get(span_id)
        if span:
            span.tool_name = tool_name
        
        # 记录指标
        self.metrics.increment_counter(f"tool.calls.{tool_name}")
        if success:
            self.metrics.increment_counter("tool.calls.success")
        else:
            self.metrics.increment_counter("tool.calls.failure")
        
        self.metrics.record_histogram(f"tool.latency.{tool_name}", latency_ms)
        
        status = SpanStatus.OK if success else SpanStatus.ERROR
        self.end_span(span_id, status=status)
    
    def check_and_alert(self) -> List[Dict]:
        """检查并触发告警"""
        return self.alert_manager.check_alerts(self.metrics)
    
    def get_dashboard_data(self) -> Dict:
        """获取仪表板数据"""
        return {
            "metrics": self.metrics.get_all_metrics(),
            "active_traces": len(self.active_traces),
            "total_traces": self.trace_store.get_trace_count(),
            "recent_alerts": self.alert_manager.get_recent_alerts(5),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


def create_observability_engine() -> ObservabilityEngine:
    """工厂函数：创建可观测性引擎"""
    return ObservabilityEngine()


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("Agent Observability System 测试")
    print("="*60)
    
    engine = create_observability_engine()
    
    # 开始追踪
    print("\n🔍 开始追踪...")
    trace_id = engine.start_trace("test-workflow", {"user_id": "user-001"})
    
    # 模拟 Agent 执行
    print("\n⚙️  模拟 Agent 执行...")
    agent_span_id = engine.start_span(
        trace_id=trace_id,
        name="Agent:Planning",
        span_type=SpanType.AGENT
    )
    
    # 模拟 LLM 调用
    print("\n🤖 模拟 LLM 调用...")
    engine.record_llm_call(
        trace_id=trace_id,
        model_name="gpt-4",
        prompt_tokens=100,
        completion_tokens=50,
        latency_ms=1500,
        parent_span_id=agent_span_id
    )
    
    # 模拟工具调用
    print("\n🔧 模拟工具调用...")
    engine.record_tool_call(
        trace_id=trace_id,
        tool_name="search",
        success=True,
        latency_ms=300,
        parent_span_id=agent_span_id
    )
    
    engine.record_tool_call(
        trace_id=trace_id,
        tool_name="database_query",
        success=False,
        latency_ms=5000,
        parent_span_id=agent_span_id
    )
    
    # 结束 Agent span
    engine.end_span(agent_span_id)
    
    # 结束追踪
    print("\n✅ 结束追踪...")
    engine.end_trace(trace_id)
    
    # 检查告警
    print("\n⚠️  检查告警...")
    alerts = engine.check_and_alert()
    if alerts:
        print(f"   触发 {len(alerts)} 个告警:")
        for alert in alerts:
            print(f"   - {alert['rule_name']}: {alert['current_value']}")
    else:
        print("   无告警")
    
    # 获取仪表板数据
    print("\n📊 仪表板数据:")
    dashboard = engine.get_dashboard_data()
    print(json.dumps(dashboard, indent=2, ensure_ascii=False, default=str))
    
    print("\n✅ 测试完成！")
