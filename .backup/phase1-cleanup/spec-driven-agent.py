#!/usr/bin/env python3
"""
Spec-Driven Development Agent

核心 Agent 实现，负责：
1. 接收用户意图
2. 加载相关 Skills
3. 应用 Rules 约束
4. 协调任务执行
5. 验证结果
6. 更新 Spec 状态
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class AgentState(Enum):
    """Agent 状态"""
    IDLE = "idle"                   # 空闲
    PLANNING = "planning"           # 规划中
    EXECUTING = "executing"         # 执行中
    WAITING_FOR_USER = "waiting_for_user"  # 等待用户
    COMPLETED = "completed"         # 完成
    FAILED = "failed"               # 失败


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class SpecDrivenAgent:
    """
    Spec-Driven Development Agent
    
    职责：
    1. 解析用户意图并映射到 Spec 任务
    2. 加载和执行 Skills
    3. 应用 Rules 约束
    4. 协调自动化引擎、日志、快照
    5. 管理任务生命周期
    6. 维护上下文和记忆
    """
    
    def __init__(self, config_path: str = ".lingma/config/automation.json"):
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 初始化组件（使用动态导入）
        import importlib.util
        
        # 导入 automation_engine
        spec_ae = importlib.util.spec_from_file_location(
            "automation_engine", 
            Path(__file__).parent / "automation-engine.py"
        )
        automation_engine_module = importlib.util.module_from_spec(spec_ae)
        spec_ae.loader.exec_module(automation_engine_module)
        AutomationEngine = automation_engine_module.AutomationEngine
        
        # 导入 operation_logger
        spec_ol = importlib.util.spec_from_file_location(
            "operation_logger", 
            Path(__file__).parent / "operation-logger.py"
        )
        operation_logger_module = importlib.util.module_from_spec(spec_ol)
        spec_ol.loader.exec_module(operation_logger_module)
        OperationLogger = operation_logger_module.OperationLogger
        
        # 导入 snapshot_manager
        spec_sm = importlib.util.spec_from_file_location(
            "snapshot_manager", 
            Path(__file__).parent / "snapshot-manager.py"
        )
        snapshot_manager_module = importlib.util.module_from_spec(spec_sm)
        spec_sm.loader.exec_module(snapshot_manager_module)
        SnapshotManager = snapshot_manager_module.SnapshotManager
        
        self.automation_engine = AutomationEngine(config_path)
        self.operation_logger = OperationLogger()
        self.snapshot_manager = SnapshotManager()
        
        # Agent 状态
        self.state = AgentState.IDLE
        self.current_task = None
        self.execution_history = []
        
        # 加载 Skills 和 Rules
        self.skills = self._load_skills()
        self.rules = self._load_rules()
        
        # 上下文记忆
        self.context = {
            "session_start": datetime.now().isoformat(),
            "spec_path": ".lingma/specs/current-spec.md",
            "user_preferences": {}
        }
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        path = Path(config_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"automation_level": "balanced", "enabled": True}
    
    def _load_skills(self) -> Dict[str, Any]:
        """加载可用的 Skills"""
        skills_dir = Path(".lingma/skills")
        skills = {}
        
        if skills_dir.exists():
            for skill_dir in skills_dir.iterdir():
                if skill_dir.is_dir():
                    skill_file = skill_dir / "SKILL.md"
                    if skill_file.exists():
                        # 解析 Skill 元数据
                        skills[skill_dir.name] = {
                            "path": str(skill_dir),
                            "description": self._extract_skill_description(skill_file)
                        }
        
        return skills
    
    def _extract_skill_description(self, skill_file: Path) -> str:
        """从 SKILL.md 提取描述"""
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read(500)  # 只读取前 500 字符
                # 简单提取 description
                if "description:" in content:
                    start = content.find("description:") + len("description:")
                    end = content.find("\n", start)
                    return content[start:end].strip()
        except Exception:
            pass
        return "No description available"
    
    def _load_rules(self) -> List[Dict[str, Any]]:
        """加载 Rules"""
        rules_dir = Path(".lingma/rules")
        rules = []
        
        if rules_dir.exists():
            for rule_file in rules_dir.glob("*.md"):
                rules.append({
                    "name": rule_file.stem,
                    "path": str(rule_file)
                })
        
        return rules
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务的主入口
        
        Args:
            task: 任务描述
                {
                    "type": "task_type",
                    "description": "任务描述",
                    "parameters": {...},
                    "expected_outcome": "预期结果"
                }
        
        Returns:
            执行结果
        """
        start_time = time.time()
        
        try:
            # Step 1: 验证前置条件
            self._validate_preconditions(task)
            
            # Step 2: 评估风险并选择策略
            assessment = self.automation_engine.evaluate_operation({
                "type": task["type"],
                "details": task.get("details", {})
            })
            
            # Step 3: 根据策略执行
            strategy = assessment["strategy"]
            
            if strategy == "auto_execute":
                result = await self._execute_auto(task, assessment)
            elif strategy == "execute_with_snapshot":
                result = await self._execute_with_snapshot(task, assessment)
            elif strategy == "ask_user":
                result = await self._execute_ask_user(task, assessment)
            elif strategy == "require_explicit_approval":
                result = await self._execute_require_approval(task, assessment)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown strategy: {strategy}"
                }
            
            # Step 4: 记录执行历史
            duration_ms = (time.time() - start_time) * 1000
            self.execution_history.append({
                "task": task,
                "result": result,
                "duration_ms": round(duration_ms, 2),
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 5: 记录操作日志
            self.operation_logger.log_operation(task, {
                "status": "success" if result["success"] else "failed",
                "duration_ms": round(duration_ms, 2),
                "strategy": strategy
            })
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # 记录错误
            self.operation_logger.log_operation(task, {
                "status": "failed",
                "error": str(e),
                "duration_ms": round(duration_ms, 2)
            })
            
            return {
                "success": False,
                "error": str(e),
                "task": task
            }
    
    def _validate_preconditions(self, task: Dict[str, Any]):
        """验证前置条件"""
        # 检查 spec 是否存在
        spec_path = Path(self.context["spec_path"])
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")
        
        # 检查自动化是否启用
        if not self.config.get("enabled", True):
            raise RuntimeError("Automation is disabled")
    
    async def _execute_auto(self, task: Dict[str, Any], assessment: Dict) -> Dict[str, Any]:
        """自动执行（低风险）"""
        self.state = AgentState.EXECUTING
        
        try:
            # 执行任务逻辑
            result = await self._perform_task(task)
            
            self.state = AgentState.COMPLETED
            return {
                "success": True,
                "strategy": "auto_execute",
                "result": result,
                "message": "Task executed automatically"
            }
            
        except Exception as e:
            self.state = AgentState.FAILED
            return {
                "success": False,
                "strategy": "auto_execute",
                "error": str(e)
            }
    
    async def _execute_with_snapshot(self, task: Dict[str, Any], assessment: Dict) -> Dict[str, Any]:
        """创建快照后执行（中风险）"""
        self.state = AgentState.EXECUTING
        
        # Step 1: 创建快照
        snapshot_result = self.snapshot_manager.create_snapshot(
            description=f"Before executing: {task.get('description', 'unknown')}",
            include_git=True
        )
        
        if not snapshot_result["success"]:
            return {
                "success": False,
                "strategy": "execute_with_snapshot",
                "error": f"Failed to create snapshot: {snapshot_result.get('error')}"
            }
        
        snapshot_id = snapshot_result["snapshot_id"]
        
        try:
            # Step 2: 执行任务
            result = await self._perform_task(task)
            
            # Step 3: 验证结果
            if self._verify_result(result, task):
                self.state = AgentState.COMPLETED
                return {
                    "success": True,
                    "strategy": "execute_with_snapshot",
                    "snapshot_id": snapshot_id,
                    "result": result,
                    "message": "Task executed with snapshot backup"
                }
            else:
                # Step 4: 验证失败，回滚
                rollback_result = self.snapshot_manager.rollback_to_snapshot(snapshot_id)
                
                self.state = AgentState.FAILED
                return {
                    "success": False,
                    "strategy": "execute_with_snapshot",
                    "snapshot_id": snapshot_id,
                    "rolled_back": rollback_result["success"],
                    "error": "Result verification failed, rolled back",
                    "result": result
                }
                
        except Exception as e:
            # 发生异常，回滚
            rollback_result = self.snapshot_manager.rollback_to_snapshot(snapshot_id)
            
            self.state = AgentState.FAILED
            return {
                "success": False,
                "strategy": "execute_with_snapshot",
                "snapshot_id": snapshot_id,
                "rolled_back": rollback_result["success"],
                "error": str(e)
            }
    
    async def _execute_ask_user(self, task: Dict[str, Any], assessment: Dict) -> Dict[str, Any]:
        """询问用户后执行（高风险）"""
        self.state = AgentState.WAITING_FOR_USER
        
        # 构建用户确认请求
        confirmation_request = {
            "task": task,
            "risk_assessment": assessment,
            "message": f"此操作风险等级: {assessment['risk_assessment']['risk_level']}\n"
                      f"建议: {assessment['recommendation']}\n\n"
                      f"是否继续执行？(yes/no)"
        }
        
        # 这里应该与用户交互，暂时返回等待状态
        return {
            "success": False,
            "strategy": "ask_user",
            "requires_user_input": True,
            "confirmation_request": confirmation_request,
            "message": "Waiting for user confirmation"
        }
    
    async def _execute_require_approval(self, task: Dict[str, Any], assessment: Dict) -> Dict[str, Any]:
        """需要明确授权（严重风险）"""
        self.state = AgentState.WAITING_FOR_USER
        
        approval_request = {
            "task": task,
            "risk_assessment": assessment,
            "message": f"⚠️ 高风险操作警告\n"
                      f"风险等级: {assessment['risk_assessment']['risk_level']}\n"
                      f"风险分数: {assessment['risk_assessment']['risk_score']}\n"
                      f"建议: {assessment['recommendation']}\n\n"
                      f"请输入 'APPROVE' 以确认执行此操作"
        }
        
        return {
            "success": False,
            "strategy": "require_explicit_approval",
            "requires_explicit_approval": True,
            "approval_request": approval_request,
            "message": "Explicit approval required"
        }
    
    async def _perform_task(self, task: Dict[str, Any]) -> Any:
        """
        执行具体任务
        
        这是一个占位方法，实际实现会根据 task type 调用不同的处理逻辑
        """
        task_type = task.get("type")
        
        # 根据任务类型分发
        if task_type == "update_spec":
            return await self._handle_update_spec(task)
        elif task_type == "create_file":
            return await self._handle_create_file(task)
        elif task_type == "modify_file":
            return await self._handle_modify_file(task)
        elif task_type == "run_tests":
            return await self._handle_run_tests(task)
        else:
            # 默认处理
            return {"message": f"Task type '{task_type}' executed", "task": task}
    
    async def _handle_update_spec(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理 spec 更新任务"""
        spec_path = Path(self.context["spec_path"])
        
        # 读取 spec
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec_content = f.read()
        
        # 应用更新（简化示例）
        updates = task.get("updates", {})
        for field, value in updates.items():
            # 这里应该有实际的 spec 更新逻辑
            pass
        
        # 写回 spec
        with open(spec_path, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        return {"action": "spec_updated", "updates": updates}
    
    async def _handle_create_file(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理文件创建任务"""
        file_path = Path(task["parameters"]["path"])
        content = task["parameters"].get("content", "")
        
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {"action": "file_created", "path": str(file_path)}
    
    async def _handle_modify_file(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理文件修改任务"""
        # 实际实现会调用 search_replace 等工具
        return {"action": "file_modified", "path": task["parameters"]["path"]}
    
    async def _handle_run_tests(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理运行测试任务"""
        # 实际实现会调用测试框架
        return {"action": "tests_executed", "result": "passed"}
    
    def _verify_result(self, result: Any, task: Dict[str, Any]) -> bool:
        """验证执行结果"""
        # 简化验证逻辑
        if isinstance(result, dict):
            return result.get("success", True)
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """获取 Agent 状态"""
        return {
            "state": self.state.value,
            "current_task": self.current_task,
            "execution_count": len(self.execution_history),
            "available_skills": list(self.skills.keys()),
            "loaded_rules": len(self.rules),
            "context": self.context
        }
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        if not self.execution_history:
            return {"total_executions": 0}
        
        total = len(self.execution_history)
        successful = sum(1 for h in self.execution_history if h["result"].get("success"))
        failed = total - successful
        
        avg_duration = sum(h["duration_ms"] for h in self.execution_history) / total
        
        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(successful / total * 100, 2) if total > 0 else 0,
            "average_duration_ms": round(avg_duration, 2)
        }


# 便捷函数
async def run_agent_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """快速运行 Agent 任务"""
    agent = SpecDrivenAgent()
    return await agent.execute_task(task)


if __name__ == "__main__":
    import asyncio
    
    # 测试示例
    async def main():
        agent = SpecDrivenAgent()
        
        print("=" * 60)
        print("Spec-Driven Agent 测试")
        print("=" * 60)
        
        # 显示初始状态
        print("\n📊 Agent 状态:")
        status = agent.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
        # 测试低风险任务
        print("\n🧪 测试低风险任务 (update_spec)...")
        task = {
            "type": "update_spec",
            "description": "Update spec progress",
            "parameters": {
                "updates": {
                    "progress": "40%"
                }
            },
            "details": {
                "has_clear_intent": True,
                "is_repetitive_task": True
            }
        }
        
        result = await agent.execute_task(task)
        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 显示执行摘要
        print("\n📈 执行摘要:")
        summary = agent.get_execution_summary()
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    asyncio.run(main())
