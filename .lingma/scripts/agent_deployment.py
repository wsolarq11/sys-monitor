#!/usr/bin/env python3
"""
AI Agent Deployment & MLOps System - AI Agent 部署与 MLOps 系统

CI/CD 流水线、容器化部署、自动扩展、生产监控
实现生产级 AI Agent 的完整部署框架

参考社区最佳实践:
- CI/CD pipeline with quality gates
- Container orchestration (Docker/Kubernetes)
- Auto-scaling and load balancing
- Blue-green deployment / Canary releases
- Infrastructure as Code (Terraform)
"""

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import uuid
import subprocess

logger = logging.getLogger(__name__)


class DeploymentStage(Enum):
    """部署阶段"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DeploymentStrategy(Enum):
    """部署策略"""
    ROLLING_UPDATE = "rolling_update"  # 滚动更新
    BLUE_GREEN = "blue_green"  # 蓝绿部署
    CANARY = "canary"  # 金丝雀发布
    RECREATE = "recreate"  # 重建


class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class DeploymentConfig:
    """部署配置"""
    app_name: str
    version: str
    stage: DeploymentStage
    strategy: DeploymentStrategy = DeploymentStrategy.ROLLING_UPDATE
    replicas: int = 1
    resources: Dict[str, Any] = field(default_factory=lambda: {
        "cpu": "500m",
        "memory": "512Mi"
    })
    environment_vars: Dict[str, str] = field(default_factory=dict)
    health_check_path: str = "/health"
    max_surge: str = "25%"  # 最大激增
    max_unavailable: str = "25%"  # 最大不可用
    rollback_enabled: bool = True
    auto_scaling: bool = False
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_utilization: int = 70
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class BuildArtifact:
    """构建产物"""
    artifact_id: str
    name: str
    version: str
    build_time: str
    image_tag: Optional[str] = None
    checksum: Optional[str] = None
    size_mb: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.build_time:
            self.build_time = datetime.now(timezone.utc).isoformat()


@dataclass
class DeploymentRecord:
    """部署记录"""
    deployment_id: str
    app_name: str
    version: str
    stage: DeploymentStage
    strategy: DeploymentStrategy
    status: str  # pending/in_progress/success/failed/rolled_back
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    artifacts: List[BuildArtifact] = field(default_factory=list)
    health_status: HealthStatus = HealthStatus.UNKNOWN
    rollback_reason: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).isoformat()


@dataclass
class ScalingPolicy:
    """扩展策略"""
    policy_id: str
    metric_name: str  # cpu/memory/custom
    threshold: float
    scale_up_threshold: float
    scale_down_threshold: float
    cooldown_period_seconds: int = 300
    current_replicas: int = 1
    desired_replicas: int = 1
    last_scale_time: Optional[str] = None


class CICDPipeline:
    """CI/CD 流水线
    
    自动化构建、测试、部署流程
    """
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.stages: List[Dict] = []
        self.current_stage: Optional[str] = None
    
    def add_stage(self, name: str, executor: Callable, timeout: int = 300):
        """添加流水线阶段"""
        self.stages.append({
            "name": name,
            "executor": executor,
            "timeout": timeout,
            "status": "pending"
        })
    
    def execute_pipeline(self) -> Dict:
        """
        执行完整流水线
        
        Returns:
            执行结果
        """
        logger.info(f"Starting CI/CD pipeline for {self.config.app_name} v{self.config.version}")
        
        results = {
            "pipeline_id": str(uuid.uuid4()),
            "started_at": datetime.now(timezone.utc).isoformat(),
            "stages": [],
            "overall_status": "success"
        }
        
        for stage in self.stages:
            stage_name = stage["name"]
            self.current_stage = stage_name
            
            logger.info(f"Executing stage: {stage_name}")
            
            start_time = time.time()
            
            try:
                # 执行阶段
                stage_result = stage["executor"]()
                
                elapsed = time.time() - start_time
                
                stage["status"] = "success"
                stage["duration"] = elapsed
                stage["result"] = stage_result  # 保存结果
                
                results["stages"].append({
                    "name": stage_name,
                    "status": "success",
                    "duration": round(elapsed, 2),
                    "result": stage_result
                })
                
                logger.info(f"Stage '{stage_name}' completed successfully in {elapsed:.2f}s")
            
            except Exception as e:
                elapsed = time.time() - start_time
                
                stage["status"] = "failed"
                stage["error"] = str(e)
                
                results["stages"].append({
                    "name": stage_name,
                    "status": "failed",
                    "duration": round(elapsed, 2),
                    "error": str(e)
                })
                
                results["overall_status"] = "failed"
                
                logger.error(f"Stage '{stage_name}' failed: {e}")
                
                # 如果失败，停止流水线
                break
        
        results["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        total_duration = sum(s.get("duration", 0) for s in results["stages"])
        results["total_duration"] = round(total_duration, 2)
        
        logger.info(f"Pipeline completed: {results['overall_status']}")
        
        return results
    
    def run_code_quality_checks(self) -> Dict:
        """运行代码质量检查"""
        logger.info("Running code quality checks...")
        
        # 模拟检查
        checks = {
            "linting": {"status": "passed", "issues": 0},
            "type_checking": {"status": "passed", "errors": 0},
            "security_scan": {"status": "passed", "vulnerabilities": 0},
            "code_coverage": {"status": "passed", "coverage": 85.5}
        }
        
        all_passed = all(check["status"] == "passed" for check in checks.values())
        
        if not all_passed:
            raise RuntimeError("Code quality checks failed")
        
        return checks
    
    def run_tests(self) -> Dict:
        """运行测试"""
        logger.info("Running tests...")
        
        # 模拟测试
        test_results = {
            "unit_tests": {"total": 100, "passed": 100, "failed": 0},
            "integration_tests": {"total": 20, "passed": 20, "failed": 0},
            "e2e_tests": {"total": 5, "passed": 5, "failed": 0}
        }
        
        total_failed = sum(r["failed"] for r in test_results.values())
        
        if total_failed > 0:
            raise RuntimeError(f"{total_failed} tests failed")
        
        return test_results
    
    def build_artifact(self) -> BuildArtifact:
        """构建产物"""
        logger.info(f"Building artifact for {self.config.app_name}...")
        
        # 模拟构建
        artifact = BuildArtifact(
            artifact_id=str(uuid.uuid4()),
            name=self.config.app_name,
            version=self.config.version,
            image_tag=f"{self.config.app_name}:{self.config.version}",
            size_mb=125.5,
            build_time=""  # 会自动生成
        )
        
        logger.info(f"Artifact built: {artifact.image_tag}")
        
        return artifact
    
    def deploy_to_environment(self, artifact: BuildArtifact) -> Dict:
        """部署到环境"""
        logger.info(f"Deploying {artifact.image_tag} to {self.config.stage.value}...")
        
        # 模拟部署
        deployment_result = {
            "deployment_id": str(uuid.uuid4()),
            "artifact": artifact.image_tag,
            "environment": self.config.stage.value,
            "replicas": self.config.replicas,
            "status": "deployed"
        }
        
        logger.info(f"Deployment successful: {deployment_result['deployment_id']}")
        
        return deployment_result


class ContainerOrchestrator:
    """容器编排器
    
    管理容器化部署和扩展
    """
    
    def __init__(self):
        self.deployments: Dict[str, DeploymentRecord] = {}
        self.scaling_policies: Dict[str, ScalingPolicy] = {}
    
    def create_deployment(self, config: DeploymentConfig, artifact: BuildArtifact) -> DeploymentRecord:
        """
        创建部署
        
        Args:
            config: 部署配置
            artifact: 构建产物
            
        Returns:
            部署记录
        """
        deployment = DeploymentRecord(
            deployment_id=str(uuid.uuid4()),
            app_name=config.app_name,
            version=config.version,
            stage=config.stage,
            strategy=config.strategy,
            status="in_progress",
            started_at=datetime.now(timezone.utc).isoformat(),
            artifacts=[artifact]
        )
        
        self.deployments[deployment.deployment_id] = deployment
        
        logger.info(f"Creating deployment: {deployment.deployment_id}")
        
        return deployment
    
    def execute_deployment(self, deployment_id: str) -> bool:
        """
        执行部署
        
        Args:
            deployment_id: 部署ID
            
        Returns:
            是否成功
        """
        deployment = self.deployments.get(deployment_id)
        
        if not deployment:
            raise ValueError(f"Deployment not found: {deployment_id}")
        
        logger.info(f"Executing deployment {deployment_id} with strategy {deployment.strategy.value}")
        
        try:
            # 根据策略执行部署
            if deployment.strategy == DeploymentStrategy.ROLLING_UPDATE:
                self._rolling_update(deployment)
            elif deployment.strategy == DeploymentStrategy.BLUE_GREEN:
                self._blue_green_deployment(deployment)
            elif deployment.strategy == DeploymentStrategy.CANARY:
                self._canary_release(deployment)
            else:
                self._recreate_deployment(deployment)
            
            # 更新状态
            deployment.status = "success"
            deployment.completed_at = datetime.now(timezone.utc).isoformat()
            deployment.health_status = HealthStatus.HEALTHY
            
            logger.info(f"Deployment {deployment_id} completed successfully")
            
            return True
        
        except Exception as e:
            deployment.status = "failed"
            deployment.completed_at = datetime.now(timezone.utc).isoformat()
            deployment.health_status = HealthStatus.UNHEALTHY
            
            logger.error(f"Deployment {deployment_id} failed: {e}")
            
            # 如果启用回滚，执行回滚
            if deployment.rollback_enabled:
                logger.info(f"Initiating rollback for {deployment_id}")
                self.rollback_deployment(deployment_id, f"Deployment failed: {str(e)}")
            
            return False
    
    def _rolling_update(self, deployment: DeploymentRecord):
        """滚动更新"""
        logger.info("Performing rolling update...")
        # 模拟滚动更新逻辑
        time.sleep(0.1)
    
    def _blue_green_deployment(self, deployment: DeploymentRecord):
        """蓝绿部署"""
        logger.info("Performing blue-green deployment...")
        # 模拟蓝绿部署逻辑
        time.sleep(0.1)
    
    def _canary_release(self, deployment: DeploymentRecord):
        """金丝雀发布"""
        logger.info("Performing canary release...")
        # 模拟金丝雀发布逻辑
        time.sleep(0.1)
    
    def _recreate_deployment(self, deployment: DeploymentRecord):
        """重建部署"""
        logger.info("Performing recreate deployment...")
        # 模拟重建逻辑
        time.sleep(0.1)
    
    def rollback_deployment(self, deployment_id: str, reason: str):
        """回滚部署"""
        deployment = self.deployments.get(deployment_id)
        
        if not deployment:
            raise ValueError(f"Deployment not found: {deployment_id}")
        
        logger.info(f"Rolling back deployment {deployment_id}: {reason}")
        
        deployment.status = "rolled_back"
        deployment.rollback_reason = reason
        deployment.completed_at = datetime.now(timezone.utc).isoformat()
    
    def check_health(self, deployment_id: str) -> HealthStatus:
        """检查健康状态"""
        deployment = self.deployments.get(deployment_id)
        
        if not deployment:
            return HealthStatus.UNKNOWN
        
        # 模拟健康检查
        # 实际应调用健康检查端点
        deployment.health_status = HealthStatus.HEALTHY
        
        return deployment.health_status
    
    def setup_auto_scaling(self, deployment_id: str, policy: ScalingPolicy):
        """设置自动扩展"""
        self.scaling_policies[deployment_id] = policy
        logger.info(f"Auto-scaling configured for {deployment_id}")
    
    def scale_deployment(self, deployment_id: str, new_replicas: int):
        """扩展部署"""
        deployment = self.deployments.get(deployment_id)
        
        if not deployment:
            raise ValueError(f"Deployment not found: {deployment_id}")
        
        policy = self.scaling_policies.get(deployment_id)
        
        if policy:
            policy.desired_replicas = new_replicas
            policy.last_scale_time = datetime.now(timezone.utc).isoformat()
        
        logger.info(f"Scaling deployment {deployment_id} to {new_replicas} replicas")
    
    def get_deployment_status(self, deployment_id: str) -> Dict:
        """获取部署状态"""
        deployment = self.deployments.get(deployment_id)
        
        if not deployment:
            return {"error": "Deployment not found"}
        
        return {
            "deployment_id": deployment.deployment_id,
            "app_name": deployment.app_name,
            "version": deployment.version,
            "stage": deployment.stage.value,
            "status": deployment.status,
            "health_status": deployment.health_status.value,
            "strategy": deployment.strategy.value,
            "started_at": deployment.started_at,
            "completed_at": deployment.completed_at,
            "rollback_reason": deployment.rollback_reason
        }


class ProductionMonitor:
    """生产监控器
    
    监控生产环境的性能和健康状态
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[Dict]] = {}
        self.alerts: List[Dict] = []
        self.health_checks: Dict[str, HealthStatus] = {}
    
    def record_metric(self, deployment_id: str, metric_name: str, value: float, labels: Dict = None):
        """记录指标"""
        if deployment_id not in self.metrics:
            self.metrics[deployment_id] = []
        
        metric_point = {
            "metric_name": metric_name,
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "labels": labels or {}
        }
        
        self.metrics[deployment_id].append(metric_point)
    
    def check_health(self, deployment_id: str, health_endpoint: str = "/health") -> HealthStatus:
        """检查健康状态"""
        # 模拟健康检查
        # 实际应调用 HTTP 健康检查端点
        status = HealthStatus.HEALTHY
        
        self.health_checks[deployment_id] = status
        
        return status
    
    def detect_anomalies(self, deployment_id: str) -> List[Dict]:
        """检测异常"""
        anomalies = []
        
        metrics = self.metrics.get(deployment_id, [])
        
        if not metrics:
            return anomalies
        
        # 简单的阈值检测
        for metric in metrics[-10:]:  # 检查最近10个数据点
            if metric["metric_name"] == "latency_p95" and metric["value"] > 5000:
                anomaly = {
                    "anomaly_id": str(uuid.uuid4()),
                    "deployment_id": deployment_id,
                    "metric": metric["metric_name"],
                    "value": metric["value"],
                    "threshold": 5000,
                    "severity": "warning",
                    "detected_at": datetime.now(timezone.utc).isoformat()
                }
                anomalies.append(anomaly)
                self.alerts.append(anomaly)
        
        return anomalies
    
    def get_dashboard_data(self, deployment_id: str) -> Dict:
        """获取仪表板数据"""
        metrics = self.metrics.get(deployment_id, [])
        
        # 计算统计信息
        latency_values = [m["value"] for m in metrics if m["metric_name"] == "latency_p95"]
        error_rates = [m["value"] for m in metrics if m["metric_name"] == "error_rate"]
        
        return {
            "deployment_id": deployment_id,
            "health_status": self.health_checks.get(deployment_id, HealthStatus.UNKNOWN).value,
            "metrics_summary": {
                "avg_latency_p95": sum(latency_values) / len(latency_values) if latency_values else 0,
                "max_latency_p95": max(latency_values) if latency_values else 0,
                "avg_error_rate": sum(error_rates) / len(error_rates) if error_rates else 0,
                "total_requests": len(metrics)
            },
            "recent_alerts": self.alerts[-5:],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class DeploymentEngine:
    """部署引擎
    
    整合 CI/CD、容器编排、生产监控的完整系统
    """
    
    def __init__(self):
        self.orchestrator = ContainerOrchestrator()
        self.monitor = ProductionMonitor()
        self.deployment_history: List[DeploymentRecord] = []
    
    def deploy_application(
        self,
        config: DeploymentConfig,
        run_tests: bool = True,
        run_quality_checks: bool = True
    ) -> Dict:
        """
        部署应用
        
        Args:
            config: 部署配置
            run_tests: 是否运行测试
            run_quality_checks: 是否运行质量检查
            
        Returns:
            部署结果
        """
        logger.info(f"Starting deployment of {config.app_name} v{config.version}")
        
        # Step 1: 创建 CI/CD 流水线
        pipeline = CICDPipeline(config)
        
        # 添加阶段
        if run_quality_checks:
            pipeline.add_stage("code_quality", pipeline.run_code_quality_checks)
        
        if run_tests:
            pipeline.add_stage("tests", pipeline.run_tests)
        
        pipeline.add_stage("build", pipeline.build_artifact)
        
        # 部署阶段需要访问构建产物
        def deploy_stage():
            # 获取 build 阶段的结果
            build_result = None
            for stage in pipeline.stages:
                if stage["name"] == "build" and stage.get("result"):
                    build_result = stage["result"]
                    break
            
            if not build_result:
                raise RuntimeError("Build artifact not found")
            
            return pipeline.deploy_to_environment(build_result)
        
        pipeline.add_stage("deploy", deploy_stage)
        
        # Step 2: 执行流水线
        pipeline_result = pipeline.execute_pipeline()
        
        if pipeline_result["overall_status"] != "success":
            return {
                "success": False,
                "error": "Pipeline failed",
                "pipeline_result": pipeline_result
            }
        
        # Step 3: 获取构建产物
        artifact = pipeline_result["stages"][-2]["result"]  # build stage result
        
        # Step 4: 创建部署
        deployment = self.orchestrator.create_deployment(config, artifact)
        
        # Step 5: 执行部署
        success = self.orchestrator.execute_deployment(deployment.deployment_id)
        
        # Step 6: 设置监控
        if success:
            self.monitor.check_health(deployment.deployment_id)
            
            # 如果启用自动扩展，设置扩展策略
            if config.auto_scaling:
                policy = ScalingPolicy(
                    policy_id=str(uuid.uuid4()),
                    metric_name="cpu",
                    threshold=config.target_cpu_utilization,
                    scale_up_threshold=config.target_cpu_utilization + 10,
                    scale_down_threshold=config.target_cpu_utilization - 20,
                    current_replicas=config.replicas,
                    desired_replicas=config.replicas
                )
                self.orchestrator.setup_auto_scaling(deployment.deployment_id, policy)
        
        # Step 7: 记录历史
        self.deployment_history.append(deployment)
        
        return {
            "success": success,
            "deployment_id": deployment.deployment_id,
            "pipeline_result": pipeline_result,
            "deployment_status": self.orchestrator.get_deployment_status(deployment.deployment_id)
        }
    
    def rollback(self, deployment_id: str, reason: str = "Manual rollback") -> bool:
        """回滚部署"""
        try:
            self.orchestrator.rollback_deployment(deployment_id, reason)
            logger.info(f"Rollback completed for {deployment_id}")
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def get_deployment_status(self, deployment_id: str) -> Dict:
        """获取部署状态"""
        return self.orchestrator.get_deployment_status(deployment_id)
    
    def get_monitoring_dashboard(self, deployment_id: str) -> Dict:
        """获取监控仪表板"""
        return self.monitor.get_dashboard_data(deployment_id)
    
    def get_deployment_history(self, limit: int = 10) -> List[Dict]:
        """获取部署历史"""
        recent = self.deployment_history[-limit:]
        return [
            {
                "deployment_id": d.deployment_id,
                "app_name": d.app_name,
                "version": d.version,
                "stage": d.stage.value,
                "status": d.status,
                "started_at": d.started_at
            }
            for d in recent
        ]


def create_deployment_engine() -> DeploymentEngine:
    """工厂函数：创建部署引擎"""
    return DeploymentEngine()


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Deployment & MLOps 测试")
    print("="*60)
    
    engine = create_deployment_engine()
    
    # 创建部署配置
    print("\n⚙️  创建部署配置...")
    config = DeploymentConfig(
        app_name="my-agent-app",
        version="1.0.0",
        stage=DeploymentStage.PRODUCTION,
        strategy=DeploymentStrategy.ROLLING_UPDATE,
        replicas=3,
        auto_scaling=True,
        environment_vars={
            "OPENAI_API_KEY": "sk-xxx",
            "LOG_LEVEL": "INFO"
        }
    )
    
    # 部署应用
    print("\n🚀 部署应用...")
    result = engine.deploy_application(config)
    
    print(f"\n✅ 部署结果:")
    print(f"   成功: {result['success']}")
    print(f"   部署ID: {result.get('deployment_id', 'N/A')}")
    
    if result['success']:
        print(f"   状态: {result['deployment_status']['status']}")
        print(f"   健康状态: {result['deployment_status']['health_status']}")
    
    # 获取监控数据
    if result['success']:
        print("\n📊 监控仪表板:")
        dashboard = engine.get_monitoring_dashboard(result['deployment_id'])
        print(json.dumps(dashboard, indent=2, ensure_ascii=False))
    
    # 获取部署历史
    print("\n📜 部署历史:")
    history = engine.get_deployment_history(5)
    for i, dep in enumerate(history, 1):
        print(f"   {i}. {dep['app_name']} v{dep['version']} - {dep['status']} ({dep['stage']})")
    
    print("\n✅ 测试完成！")
