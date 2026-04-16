#!/usr/bin/env python3
"""
Supervisor Agent - 多Agent编排和质量门禁执行引擎

职责:
1. 实现TaskQueue调度和质量门禁
2. 按Sequential/Parallel/Conditional/Iterative模式编排任务
3. 执行5层质量门禁检查
4. 聚合Worker结果并做出最终决策
5. 记录详细决策日志到decision-log.json

使用方式:
    python supervisor-agent.py --json-rpc < input.json
    python supervisor-agent.py --test
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed


class SupervisorAgent:
    """Supervisor编排Agent"""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path.cwd()
        self.decision_log_path = (
            self.repo_root / ".lingma" / "logs" / "decision-log.json"
        )
        self.decision_log_path.parent.mkdir(parents=True, exist_ok=True)

        # 初始化决策日志
        if not self.decision_log_path.exists():
            self._init_decision_log()

    def _init_decision_log(self):
        """初始化决策日志文件"""
        initial_log = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "entries": [],
        }
        self.decision_log_path.write_text(
            json.dumps(initial_log, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def orchestrate_tasks(
        self,
        tasks: List[Dict[str, Any]],
        pattern: str = "sequential",
        quality_gates_enabled: bool = True,
    ) -> Dict[str, Any]:
        """
        编排任务执行

        Args:
            tasks: 任务列表
            pattern: 编排模式 (sequential/parallel/conditional/iterative)
            quality_gates_enabled: 是否启用质量门禁

        Returns:
            编排结果
        """
        start_time = datetime.now()

        result = {
            "pattern": pattern,
            "total_tasks": len(tasks),
            "completed_tasks": 0,
            "failed_tasks": 0,
            "task_results": [],
            "quality_gates": {},
            "final_decision": None,
            "duration_seconds": 0,
        }

        try:
            # 根据模式执行
            if pattern == "sequential":
                task_results = self._execute_sequential(tasks, quality_gates_enabled)
            elif pattern == "parallel":
                task_results = self._execute_parallel(tasks, quality_gates_enabled)
            elif pattern == "conditional":
                task_results = self._execute_conditional(tasks, quality_gates_enabled)
            elif pattern == "iterative":
                task_results = self._execute_iterative(tasks, quality_gates_enabled)
            else:
                raise ValueError(f"Unknown orchestration pattern: {pattern}")

            result["task_results"] = task_results
            result["completed_tasks"] = sum(
                1 for r in task_results if r.get("status") == "success"
            )
            result["failed_tasks"] = sum(
                1 for r in task_results if r.get("status") != "success"
            )

            # 执行质量门禁
            if quality_gates_enabled:
                quality_result = self._execute_quality_gates(task_results)
                result["quality_gates"] = quality_result

            # 做出最终决策
            result["final_decision"] = self._make_final_decision(result)

            # 记录决策日志
            end_time = datetime.now()
            result["duration_seconds"] = (end_time - start_time).total_seconds()

            self._log_decision(
                {
                    "timestamp": start_time.isoformat(),
                    "action": "TASK_ORCHESTRATION",
                    "pattern": pattern,
                    "result": result,
                }
            )

            return result

        except Exception as e:
            import traceback

            error_traceback = traceback.format_exc()
            print(f"ERROR in orchestrate_tasks: {e}")
            print(f"Traceback:\n{error_traceback}", file=sys.stderr)
            return {
                "pattern": pattern,
                "status": "error",
                "error": str(e),
                "traceback": error_traceback,
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
            }

    def _execute_sequential(self, tasks: List[Dict], quality_gates: bool) -> List[Dict]:
        """顺序执行任务"""
        results = []

        for i, task in enumerate(tasks):
            print(f"📋 执行任务 {i+1}/{len(tasks)}: {task.get('task_type', 'unknown')}")

            # 模拟任务执行
            result = self._simulate_task_execution(task)
            results.append(result)

            # 如果启用质量门禁且任务失败，停止执行
            if quality_gates and result.get("status") != "success":
                print(f"❌ 任务失败，停止后续执行")
                break

            # 添加小延迟以模拟真实执行时间
            time.sleep(0.1)

        return results

    def _execute_parallel(self, tasks: List[Dict], quality_gates: bool) -> List[Dict]:
        """并行执行任务"""
        results = []

        with ThreadPoolExecutor(max_workers=min(len(tasks), 5)) as executor:
            future_to_task = {
                executor.submit(self._simulate_task_execution, task): task
                for task in tasks
            }

            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(
                        {
                            "task_id": task.get("task_id", "unknown"),
                            "status": "error",
                            "error": str(e),
                        }
                    )

        return results

    def _execute_conditional(
        self, tasks: List[Dict], quality_gates: bool
    ) -> List[Dict]:
        """条件执行任务"""
        results = []

        for task in tasks:
            condition = task.get("condition")

            # 评估条件
            if condition and not self._evaluate_condition(condition):
                print(f"⏭️  跳过任务 (条件不满足): {task.get('task_type')}")
                results.append(
                    {
                        "task_id": task.get("task_id"),
                        "status": "skipped",
                        "reason": f"Condition not met: {condition}",
                    }
                )
                continue

            # 执行任务
            result = self._simulate_task_execution(task)
            results.append(result)

        return results

    def _execute_iterative(
        self, tasks: List[Dict], quality_gates: bool, max_iterations: int = 3
    ) -> List[Dict]:
        """迭代执行任务"""
        final_results = []

        for iteration in range(max_iterations):
            print(f"\n🔄 迭代 {iteration + 1}/{max_iterations}")

            iteration_results = []
            all_passed = True

            for task in tasks:
                result = self._simulate_task_execution(task)
                iteration_results.append(result)

                if result.get("status") != "success":
                    all_passed = False

            final_results = iteration_results

            # 如果所有任务都通过，提前退出
            if all_passed:
                print(f"✅ 所有任务在迭代 {iteration + 1} 中通过")
                break

            print(f"⚠️  存在失败任务，继续下一次迭代")
            time.sleep(0.1)

        return final_results

    def _simulate_task_execution(self, task: Dict) -> Dict:
        """模拟任务执行（实际应调用对应的Agent）"""
        task_type = task.get("task_type", "unknown")
        task_id = task.get("task_id", f"task_{int(time.time())}")

        # 模拟不同任务类型的执行
        execution_times = {
            "spec_driven_core": 0.2,
            "test_runner": 0.3,
            "code_reviewer": 0.2,
            "doc_generator": 0.1,
        }

        exec_time = execution_times.get(task_type, 0.1)
        time.sleep(exec_time)  # 模拟执行时间

        # 模拟成功率90%
        import random

        success = random.random() < 0.9

        if success:
            return {
                "task_id": task_id,
                "task_type": task_type,
                "status": "success",
                "output": f"Task {task_type} completed successfully",
                "execution_time": exec_time,
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
            }
        else:
            return {
                "task_id": task_id,
                "task_type": task_type,
                "status": "failed",
                "error": f"Simulated failure for {task_type}",
                "execution_time": exec_time,
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
            }

    def _evaluate_condition(self, condition: str) -> bool:
        """评估条件表达式"""
        # 简化版条件评估
        if condition == "always":
            return True
        elif condition.startswith("env:"):
            env_var = condition.split(":", 1)[1]
            import os

            return bool(os.environ.get(env_var))
        else:
            # 默认返回True
            return True

    def _execute_quality_gates(self, task_results: List[Dict]) -> Dict[str, Any]:
        """
        执行5层质量门禁

        Returns:
            质量门禁结果
        """
        gates = {
            "gate_1_self_validation": {
                "name": "Agent自检",
                "passed": True,
                "details": [],
            },
            "gate_2_test_runner": {"name": "测试验证", "passed": True, "details": []},
            "gate_3_code_review": {
                "name": "代码审查",
                "passed": True,
                "score": 0,
                "details": [],
            },
            "gate_4_documentation": {"name": "文档检查", "passed": True, "details": []},
            "gate_5_supervisor_acceptance": {
                "name": "Supervisor验收",
                "passed": True,
                "score": 0,
                "details": [],
            },
        }

        # Gate 1: Agent自检
        for result in task_results:
            if result.get("status") == "success":
                gates["gate_1_self_validation"]["details"].append(
                    f"✓ Task {result['task_id']} self-validation passed"
                )
            elif result.get("status") != "skipped":
                gates["gate_1_self_validation"]["passed"] = False
                gates["gate_1_self_validation"]["details"].append(
                    f"✗ Task {result['task_id']} self-validation failed: {result.get('error', 'Unknown error')}"
                )

        # Gate 2: 测试验证
        test_results = [r for r in task_results if r.get("task_type") == "test_runner"]
        if test_results:
            all_tests_passed = all(r.get("status") == "success" for r in test_results)
            gates["gate_2_test_runner"]["passed"] = all_tests_passed
            gates["gate_2_test_runner"]["details"].append(
                f"Tests: {'All passed' if all_tests_passed else 'Some failed'}"
            )
        else:
            gates["gate_2_test_runner"]["details"].append("No test results available")

        # Gate 3: 代码审查
        review_results = [
            r for r in task_results if r.get("task_type") == "code_reviewer"
        ]
        if review_results:
            avg_score = sum(r.get("quality_score", 0) for r in review_results) / len(
                review_results
            )
            gates["gate_3_code_review"]["score"] = round(avg_score, 1)
            gates["gate_3_code_review"]["passed"] = avg_score >= 80
            gates["gate_3_code_review"]["details"].append(
                f"Average quality score: {avg_score:.1f}/100"
            )
        else:
            gates["gate_3_code_review"]["score"] = 85  # 默认分数
            gates["gate_3_code_review"]["details"].append(
                "No code review results, using default score"
            )

        # Gate 4: 文档检查
        doc_results = [r for r in task_results if r.get("task_type") == "doc_generator"]
        if doc_results:
            all_docs_generated = all(r.get("status") == "success" for r in doc_results)
            gates["gate_4_documentation"]["passed"] = all_docs_generated
            gates["gate_4_documentation"]["details"].append(
                f"Documentation: {'Generated' if all_docs_generated else 'Failed'}"
            )
        else:
            gates["gate_4_documentation"]["details"].append(
                "No documentation generation required"
            )

        # Gate 5: Supervisor验收
        passed_gates = sum(1 for g in gates.values() if g["passed"])
        total_gates = len(gates)
        acceptance_score = (passed_gates / total_gates) * 100

        gates["gate_5_supervisor_acceptance"]["score"] = round(acceptance_score, 1)
        gates["gate_5_supervisor_acceptance"]["passed"] = acceptance_score >= 85
        gates["gate_5_supervisor_acceptance"]["details"].append(
            f"{passed_gates}/{total_gates} gates passed ({acceptance_score:.1f}%)"
        )

        return {
            "all_gates_passed": all(g["passed"] for g in gates.values()),
            "gates": gates,
            "summary": f"{sum(1 for g in gates.values() if g['passed'])}/{len(gates)} gates passed",
        }

    def _make_final_decision(self, orchestration_result: Dict) -> Dict[str, Any]:
        """做出最终决策"""
        quality_gates = orchestration_result.get("quality_gates", {})
        all_gates_passed = quality_gates.get("all_gates_passed", False)

        completed = orchestration_result.get("completed_tasks", 0)
        failed = orchestration_result.get("failed_tasks", 0)
        total = orchestration_result.get("total_tasks", 0)

        decision = {
            "verdict": "ACCEPTED" if all_gates_passed else "REJECTED",
            "reason": "",
            "recommendations": [],
        }

        if all_gates_passed:
            decision["reason"] = (
                f"All quality gates passed. {completed}/{total} tasks completed successfully."
            )
            decision["confidence"] = 0.95
        else:
            failed_gates = [
                name
                for name, gate in quality_gates.get("gates", {}).items()
                if not gate["passed"]
            ]
            decision["reason"] = f"Quality gates failed: {', '.join(failed_gates)}"
            decision["confidence"] = 0.3
            decision["recommendations"] = [
                "Review failed quality gates",
                "Fix identified issues",
                "Re-run orchestration",
            ]

        return decision

    def _log_decision(self, entry: Dict[str, Any]):
        """记录决策日志"""
        try:
            # 读取现有日志
            if self.decision_log_path.exists():
                log_data = json.loads(
                    self.decision_log_path.read_text(encoding="utf-8")
                )
                # 确保 entries 键存在
                if "entries" not in log_data:
                    log_data["entries"] = []
            else:
                log_data = {
                    "version": "1.0",
                    "created_at": datetime.now().isoformat(),
                    "entries": [],
                }

            # 添加新条目
            log_data["entries"].append(entry)

            # 写回文件
            self.decision_log_path.write_text(
                json.dumps(log_data, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        except Exception as e:
            print(f"WARNING - Failed to log decision: {e}")

    def process_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求的主入口"""
        try:
            tasks = params.get("tasks", [])
            pattern = params.get("pattern", "sequential")
            quality_gates_enabled = params.get("quality_gates_enabled", True)

            if not tasks:
                return {"status": "error", "message": "No tasks provided"}

            # 执行编排
            result = self.orchestrate_tasks(tasks, pattern, quality_gates_enabled)

            return {"status": "success", "orchestration_result": result}

        except Exception as e:
            return {
                "status": "error",
                "error_type": type(e).__name__,
                "error_message": str(e),
            }


def main():
    """主入口函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--json-rpc":
        try:
            input_data = json.loads(sys.stdin.read())
            agent = SupervisorAgent()
            result = agent.process_request(input_data.get("params", {}))

            response = {
                "jsonrpc": "2.0",
                "result": result,
                "id": input_data.get("id", ""),
            }

            print(json.dumps(response, ensure_ascii=False, indent=2))

        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32000, "message": str(e)},
                "id": "",
            }
            print(json.dumps(error_response, ensure_ascii=False, indent=2))
            sys.exit(1)
    else:
        print("用法:")
        print("  python supervisor-agent.py --json-rpc < input.json")
        print("  python supervisor-agent.py --test")


def run_tests():
    """运行单元测试"""
    import tempfile

    print("🧪 运行SupervisorAgent单元测试...\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        logs_dir = repo_root / ".lingma" / "logs"
        logs_dir.mkdir(parents=True)

        agent = SupervisorAgent(repo_root=repo_root)

        # 测试1: 顺序编排
        print("✅ 测试1: 顺序编排模式")
        tasks = [
            {"task_id": "T1", "task_type": "spec_driven_core"},
            {"task_id": "T2", "task_type": "test_runner"},
            {"task_id": "T3", "task_type": "code_reviewer"},
        ]
        result = agent.orchestrate_tasks(tasks, pattern="sequential")
        assert result["pattern"] == "sequential"
        # 检查结果结构
        assert "pattern" in result or "status" in result
        total = result.get("total_tasks", len(result.get("task_results", [])))
        assert total == 3
        assert "final_decision" in result
        completed = result.get(
            "completed_tasks",
            len(
                [
                    r
                    for r in result.get("task_results", [])
                    if r.get("status") == "success"
                ]
            ),
        )
        total = result.get("total_tasks", len(result.get("task_results", [])))
        print(f"   ✓ 顺序编排完成: {completed}/{total} 成功")

        # 测试2: 并行编排
        print("\n✅ 测试2: 并行编排模式")
        result = agent.orchestrate_tasks(tasks, pattern="parallel")
        assert result["pattern"] == "parallel"
        # 检查结果结构
        assert "pattern" in result or "status" in result
        total = result.get("total_tasks", len(result.get("task_results", [])))
        assert total == 3
        completed = result.get(
            "completed_tasks",
            len(
                [
                    r
                    for r in result.get("task_results", [])
                    if r.get("status") == "success"
                ]
            ),
        )
        total = result.get("total_tasks", len(result.get("task_results", [])))
        print(f"   ✓ 并行编排完成: {completed}/{total} 成功")

        # 测试3: 条件编排
        print("\n✅ 测试3: 条件编排模式")
        conditional_tasks = [
            {"task_id": "T1", "task_type": "spec_driven_core", "condition": "always"},
            {
                "task_id": "T2",
                "task_type": "test_runner",
                "condition": "env:NONEXISTENT",
            },
        ]
        result = agent.orchestrate_tasks(conditional_tasks, pattern="conditional")
        assert result["pattern"] == "conditional"
        skipped = sum(1 for r in result["task_results"] if r.get("status") == "skipped")
        print(f"   ✓ 条件编排完成: {skipped} 个任务被跳过")

        # 测试4: 迭代编排
        print("\n✅ 测试4: 迭代编排模式")
        result = agent.orchestrate_tasks(tasks, pattern="iterative")
        assert result["pattern"] == "iterative"
        print(f"   ✓ 迭代编排完成")

        # 测试5: 质量门禁
        print("\n✅ 测试5: 质量门禁执行")
        result = agent.orchestrate_tasks(
            tasks, pattern="sequential", quality_gates_enabled=True
        )
        assert "quality_gates" in result
        quality = result["quality_gates"]
        assert "all_gates_passed" in quality
        assert "gates" in quality
        assert len(quality["gates"]) == 5  # 5层门禁
        print(f"   ✓ 质量门禁执行: {quality['summary']}")

        # 测试6: 决策日志
        print("\n✅ 测试6: 决策日志记录")
        decision_log_path = repo_root / ".lingma" / "logs" / "decision-log.json"
        assert decision_log_path.exists()
        log_data = json.loads(decision_log_path.read_text(encoding="utf-8"))
        assert "entries" in log_data
        assert len(log_data["entries"]) > 0
        print(f"   ✓ 决策日志记录: {len(log_data['entries'])} 条记录")

        # 测试7: 完整流程
        print("\n✅ 测试7: 完整处理流程")
        params = {
            "tasks": tasks,
            "pattern": "sequential",
            "quality_gates_enabled": True,
        }
        result = agent.process_request(params)
        assert result["status"] == "success"
        assert "orchestration_result" in result
        print(f"   ✓ 完整流程执行成功")

        # 测试8: 最终决策
        print("\n✅ 测试8: 最终决策逻辑")
        orchestration_result = {
            "completed_tasks": 3,
            "failed_tasks": 0,
            "total_tasks": 3,
            "quality_gates": {
                "all_gates_passed": True,
                "gates": {
                    "gate_1": {"passed": True},
                    "gate_2": {"passed": True},
                    "gate_3": {"passed": True},
                    "gate_4": {"passed": True},
                    "gate_5": {"passed": True},
                },
            },
        }
        decision = agent._make_final_decision(orchestration_result)
        assert decision["verdict"] == "ACCEPTED"
        assert decision["confidence"] > 0.9
        print(f"   ✓ 最终决策: {decision['verdict']}")

        print("\n✅ 所有测试通过！\n")


if __name__ == "__main__":
    main()
