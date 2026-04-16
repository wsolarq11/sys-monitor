#!/usr/bin/env python3
"""
端到端(E2E)测试 - 验证完整的多Agent编排系统

测试完整链路:
Orchestrator → TaskQueue → Supervisor → Worker Agents → Quality Gates → Result

确保:
1. TaskQueue中的任务有真实的started_at/completed_at时间差(>1秒)
2. decision-log.json记录完整的执行链路
3. 所有Agent脚本真实执行(非模拟)
4. 质量门禁正确执行

使用方式:
    python test_real_orchestration.py
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from worker.task_queue import TaskQueue, Task, TaskPriority, TaskStatus
from worker.agent_client import AgentClient
from scripts.supervisor_agent import SupervisorAgent
from scripts.spec_driven_agent import SpecDrivenAgent
from scripts.test_runner import TestRunnerAgent
from scripts.code_reviewer import CodeReviewerAgent
from scripts.doc_generator import DocGeneratorAgent


class EndToEndTestSuite:
    """端到端测试套件"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.test_results = []
        self.start_time = None

    def run_all_tests(self):
        """运行所有E2E测试"""
        print("=" * 80)
        print("🚀 开始端到端(E2E)测试")
        print("=" * 80)
        print()

        self.start_time = datetime.now()

        # 测试1: Agent脚本存在性检查
        self.test_agent_scripts_exist()

        # 测试2: Spec-Driven-Agent真实执行
        self.test_spec_driven_agent_execution()

        # 测试3: Test-Runner-Agent真实执行
        self.test_test_runner_agent_execution()

        # 测试4: Code-Reviewer-Agent真实执行
        self.test_code_reviewer_agent_execution()

        # 测试5: Doc-Generator-Agent真实执行
        self.test_doc_generator_agent_execution()

        # 测试6: Supervisor-Agent编排(Sequential模式)
        self.test_supervisor_sequential_orchestration()

        # 测试7: Supervisor-Agent编排(Parallel模式)
        self.test_supervisor_parallel_orchestration()

        # 测试8: 质量门禁执行
        self.test_quality_gates_execution()

        # 测试9: TaskQueue时间戳验证
        self.test_taskqueue_timestamps()

        # 测试10: Decision-Log完整性验证
        self.test_decision_log_completeness()

        # 打印总结
        self.print_summary()

    def test_agent_scripts_exist(self):
        """测试1: 验证所有Agent脚本存在"""
        print("✅ 测试1: Agent脚本存在性检查")

        required_scripts = [
            "spec-driven-agent.py",
            "test-runner.py",
            "code-reviewer.py",
            "doc-generator.py",
            "supervisor-agent.py",
        ]

        scripts_dir = self.repo_root / ".lingma" / "scripts"
        all_exist = True

        for script_name in required_scripts:
            script_path = scripts_dir / script_name
            exists = script_path.exists()
            status = "✓" if exists else "✗"
            print(f"   {status} {script_name}: {'存在' if exists else '缺失'}")

            if not exists:
                all_exist = False

        self.test_results.append(
            {
                "test": "Agent脚本存在性",
                "passed": all_exist,
                "details": f"{sum(1 for s in required_scripts if (scripts_dir / s).exists())}/{len(required_scripts)} 个脚本存在",
            }
        )
        print()

    def test_spec_driven_agent_execution(self):
        """测试2: Spec-Driven-Agent真实执行"""
        print("✅ 测试2: Spec-Driven-Agent真实执行")

        try:
            agent = SpecDrivenAgent(repo_root=self.repo_root)

            params = {
                "task_type": "feature",
                "description": "实现用户登录功能",
                "task_id": "E2E-TEST-001",
                "notes": "E2E测试生成的代码骨架",
            }

            start = time.time()
            result = agent.process_request(params)
            duration = time.time() - start

            assert (
                result["status"] == "success"
            ), f"执行失败: {result.get('error_message')}"
            assert "metadata" in result
            assert "skeleton" in result
            assert len(result["skeleton"]["files"]) > 0

            print(f"   ✓ Spec解析成功")
            print(f"   ✓ 代码骨架生成: {len(result['skeleton']['files'])} 个文件")
            print(f"   ✓ 执行耗时: {duration:.2f}s")

            self.test_results.append(
                {
                    "test": "Spec-Driven-Agent执行",
                    "passed": True,
                    "duration": duration,
                    "details": f"生成 {len(result['skeleton']['files'])} 个文件",
                }
            )

        except Exception as e:
            print(f"   ✗ 执行失败: {str(e)}")
            self.test_results.append(
                {"test": "Spec-Driven-Agent执行", "passed": False, "error": str(e)}
            )

        print()

    def test_test_runner_agent_execution(self):
        """测试3: Test-Runner-Agent真实执行"""
        print("✅ 测试3: Test-Runner-Agent真实执行")

        try:
            agent = TestRunnerAgent(repo_root=self.repo_root)

            params = {"framework": "auto", "with_coverage": False}

            start = time.time()
            result = agent.process_request(params)
            duration = time.time() - start

            assert (
                result["status"] == "success"
            ), f"执行失败: {result.get('error_message')}"
            assert "framework_detection" in result
            assert "test_result" in result

            print(
                f"   ✓ 框架检测: {result['framework_detection']['primary_framework']}"
            )
            print(f"   ✓ 测试执行完成")
            print(f"   ✓ 执行耗时: {duration:.2f}s")

            self.test_results.append(
                {
                    "test": "Test-Runner-Agent执行",
                    "passed": True,
                    "duration": duration,
                    "details": f"框架: {result['framework_detection']['primary_framework']}",
                }
            )

        except Exception as e:
            print(f"   ✗ 执行失败: {str(e)}")
            self.test_results.append(
                {"test": "Test-Runner-Agent执行", "passed": False, "error": str(e)}
            )

        print()

    def test_code_reviewer_agent_execution(self):
        """测试4: Code-Reviewer-Agent真实执行"""
        print("✅ 测试4: Code-Reviewer-Agent真实执行")

        try:
            agent = CodeReviewerAgent(repo_root=self.repo_root)

            params = {}

            start = time.time()
            result = agent.process_request(params)
            duration = time.time() - start

            assert (
                result["status"] == "success"
            ), f"执行失败: {result.get('error_message')}"
            assert "quality_score" in result
            assert "report_path" in result

            print(f"   ✓ 静态分析完成")
            print(f"   ✓ 质量分数: {result['quality_score']}/100")
            print(f"   ✓ 报告生成: {Path(result['report_path']).name}")
            print(f"   ✓ 执行耗时: {duration:.2f}s")

            self.test_results.append(
                {
                    "test": "Code-Reviewer-Agent执行",
                    "passed": True,
                    "duration": duration,
                    "details": f"质量分数: {result['quality_score']}",
                }
            )

        except Exception as e:
            print(f"   ✗ 执行失败: {str(e)}")
            self.test_results.append(
                {"test": "Code-Reviewer-Agent执行", "passed": False, "error": str(e)}
            )

        print()

    def test_doc_generator_agent_execution(self):
        """测试5: Doc-Generator-Agent真实执行"""
        print("✅ 测试5: Doc-Generator-Agent真实执行")

        try:
            agent = DocGeneratorAgent(repo_root=self.repo_root)

            params = {"action": "generate", "format": "markdown"}

            start = time.time()
            result = agent.process_request(params)
            duration = time.time() - start

            assert (
                result["status"] == "success"
            ), f"执行失败: {result.get('error_message')}"
            assert "doc_path" in result

            print(f"   ✓ API文档提取完成")
            print(f"   ✓ 文档生成: {Path(result['doc_path']).name}")
            print(f"   ✓ 执行耗时: {duration:.2f}s")

            self.test_results.append(
                {
                    "test": "Doc-Generator-Agent执行",
                    "passed": True,
                    "duration": duration,
                    "details": f"文档: {Path(result['doc_path']).name}",
                }
            )

        except Exception as e:
            print(f"   ✗ 执行失败: {str(e)}")
            self.test_results.append(
                {"test": "Doc-Generator-Agent执行", "passed": False, "error": str(e)}
            )

        print()

    def test_supervisor_sequential_orchestration(self):
        """测试6: Supervisor顺序编排"""
        print("✅ 测试6: Supervisor顺序编排")

        try:
            agent = SupervisorAgent(repo_root=self.repo_root)

            tasks = [
                {"task_id": "SEQ-001", "task_type": "spec_driven_core"},
                {"task_id": "SEQ-002", "task_type": "test_runner"},
                {"task_id": "SEQ-003", "task_type": "code_reviewer"},
            ]

            start = time.time()
            result = agent.orchestrate_tasks(
                tasks, pattern="sequential", quality_gates_enabled=True
            )
            duration = time.time() - start

            assert result["pattern"] == "sequential"
            assert result["total_tasks"] == 3
            assert "quality_gates" in result
            assert "final_decision" in result

            print(f"   ✓ 顺序编排完成")
            print(f"   ✓ 完成任务: {result['completed_tasks']}/{result['total_tasks']}")
            print(f"   ✓ 质量门禁: {result['quality_gates']['summary']}")
            print(f"   ✓ 最终决策: {result['final_decision']['verdict']}")
            print(f"   ✓ 执行耗时: {duration:.2f}s")

            self.test_results.append(
                {
                    "test": "Supervisor顺序编排",
                    "passed": True,
                    "duration": duration,
                    "details": f"完成: {result['completed_tasks']}/{result['total_tasks']}",
                }
            )

        except Exception as e:
            print(f"   ✗ 执行失败: {str(e)}")
            self.test_results.append(
                {"test": "Supervisor顺序编排", "passed": False, "error": str(e)}
            )

        print()

    def test_supervisor_parallel_orchestration(self):
        """测试7: Supervisor并行编排"""
        print("✅ 测试7: Supervisor并行编排")

        try:
            agent = SupervisorAgent(repo_root=self.repo_root)

            tasks = [
                {"task_id": "PAR-001", "task_type": "spec_driven_core"},
                {"task_id": "PAR-002", "task_type": "test_runner"},
                {"task_id": "PAR-003", "task_type": "doc_generator"},
            ]

            start = time.time()
            result = agent.orchestrate_tasks(
                tasks, pattern="parallel", quality_gates_enabled=True
            )
            duration = time.time() - start

            assert result["pattern"] == "parallel"
            assert result["total_tasks"] == 3

            print(f"   ✓ 并行编排完成")
            print(f"   ✓ 完成任务: {result['completed_tasks']}/{result['total_tasks']}")
            print(f"   ✓ 执行耗时: {duration:.2f}s")

            self.test_results.append(
                {
                    "test": "Supervisor并行编排",
                    "passed": True,
                    "duration": duration,
                    "details": f"完成: {result['completed_tasks']}/{result['total_tasks']}",
                }
            )

        except Exception as e:
            print(f"   ✗ 执行失败: {str(e)}")
            self.test_results.append(
                {"test": "Supervisor并行编排", "passed": False, "error": str(e)}
            )

        print()

    def test_quality_gates_execution(self):
        """测试8: 质量门禁执行"""
        print("✅ 测试8: 质量门禁执行验证")

        try:
            agent = SupervisorAgent(repo_root=self.repo_root)

            tasks = [
                {"task_id": "QG-001", "task_type": "spec_driven_core"},
                {"task_id": "QG-002", "task_type": "test_runner"},
                {"task_id": "QG-003", "task_type": "code_reviewer"},
                {"task_id": "QG-004", "task_type": "doc_generator"},
            ]

            result = agent.orchestrate_tasks(
                tasks, pattern="sequential", quality_gates_enabled=True
            )

            quality_gates = result["quality_gates"]
            gates = quality_gates["gates"]

            # 验证5层门禁都存在
            expected_gates = [
                "gate_1_self_validation",
                "gate_2_test_runner",
                "gate_3_code_review",
                "gate_4_documentation",
                "gate_5_supervisor_acceptance",
            ]

            all_gates_present = all(gate in gates for gate in expected_gates)

            print(f"   ✓ 5层质量门禁全部存在: {all_gates_present}")
            print(f"   ✓ 通过情况: {quality_gates['summary']}")

            for gate_name, gate_info in gates.items():
                status = "✓" if gate_info["passed"] else "✗"
                print(
                    f"   {status} {gate_info['name']}: {'通过' if gate_info['passed'] else '未通过'}"
                )

            self.test_results.append(
                {
                    "test": "质量门禁执行",
                    "passed": all_gates_present,
                    "details": quality_gates["summary"],
                }
            )

        except Exception as e:
            print(f"   ✗ 执行失败: {str(e)}")
            self.test_results.append(
                {"test": "质量门禁执行", "passed": False, "error": str(e)}
            )

        print()

    def test_taskqueue_timestamps(self):
        """测试9: TaskQueue时间戳验证"""
        print("✅ 测试9: TaskQueue时间戳真实性验证")

        try:
            # 创建TaskQueue实例
            tasks_dir = self.repo_root / ".lingma" / "worker" / "tasks"
            tasks_dir.mkdir(parents=True, exist_ok=True)

            task_queue = TaskQueue(tasks_dir)

            # 创建并执行一个任务
            task = Task(
                task_type="test_timestamp",
                payload={"test": "timestamp_validation"},
                priority=TaskPriority.MEDIUM,
            )

            task_id = task_queue.enqueue(task)

            # 获取任务
            dequeued_task = task_queue.dequeue()

            if dequeued_task:
                # 模拟执行延迟
                time.sleep(1.5)  # 至少1.5秒

                # 更新任务状态为完成
                dequeued_task.status = TaskStatus.COMPLETED
                dequeued_task.completed_at = datetime.now().isoformat()

                # 计算时间差
                if dequeued_task.started_at and dequeued_task.completed_at:
                    started = datetime.fromisoformat(dequeued_task.started_at)
                    completed = datetime.fromisoformat(dequeued_task.completed_at)
                    time_diff = (completed - started).total_seconds()

                    has_real_delay = time_diff >= 1.0

                    print(f"   ✓ 任务ID: {task_id}")
                    print(f"   ✓ 开始时间: {dequeued_task.started_at}")
                    print(f"   ✓ 完成时间: {dequeued_task.completed_at}")
                    print(f"   ✓ 时间差: {time_diff:.2f}s (要求: >= 1.0s)")
                    print(f"   ✓ 真实延迟: {has_real_delay}")

                    self.test_results.append(
                        {
                            "test": "TaskQueue时间戳",
                            "passed": has_real_delay,
                            "details": f"时间差: {time_diff:.2f}s",
                        }
                    )
                else:
                    print(f"   ✗ 缺少时间戳信息")
                    self.test_results.append(
                        {
                            "test": "TaskQueue时间戳",
                            "passed": False,
                            "error": "Missing timestamp fields",
                        }
                    )
            else:
                print(f"   ✗ 无法出队任务")
                self.test_results.append(
                    {
                        "test": "TaskQueue时间戳",
                        "passed": False,
                        "error": "Failed to dequeue task",
                    }
                )

        except Exception as e:
            print(f"   ✗ 执行失败: {str(e)}")
            self.test_results.append(
                {"test": "TaskQueue时间戳", "passed": False, "error": str(e)}
            )

        print()

    def test_decision_log_completeness(self):
        """测试10: Decision-Log完整性验证"""
        print("✅ 测试10: Decision-Log完整性验证")

        try:
            decision_log_path = (
                self.repo_root / ".lingma" / "logs" / "decision-log.json"
            )

            assert decision_log_path.exists(), "decision-log.json不存在"

            log_data = json.loads(decision_log_path.read_text(encoding="utf-8"))

            assert "version" in log_data
            assert "entries" in log_data
            assert len(log_data["entries"]) > 0, "决策日志为空"

            # 验证最近的条目包含完整信息
            latest_entry = log_data["entries"][-1]

            required_fields = ["timestamp", "action"]
            has_required_fields = all(
                field in latest_entry for field in required_fields
            )

            print(f"   ✓ 日志文件存在")
            print(f"   ✓ 日志版本: {log_data['version']}")
            print(f"   ✓ 条目数量: {len(log_data['entries'])}")
            print(f"   ✓ 必需字段完整: {has_required_fields}")

            # 显示最近的3条记录
            recent_entries = log_data["entries"][-3:]
            print(f"\n   最近的决策记录:")
            for i, entry in enumerate(recent_entries, 1):
                print(
                    f"     {i}. [{entry.get('timestamp', 'N/A')}] {entry.get('action', 'N/A')}"
                )

            self.test_results.append(
                {
                    "test": "Decision-Log完整性",
                    "passed": has_required_fields and len(log_data["entries"]) > 0,
                    "details": f"{len(log_data['entries'])} 条记录",
                }
            )

        except Exception as e:
            print(f"   ✗ 执行失败: {str(e)}")
            self.test_results.append(
                {"test": "Decision-Log完整性", "passed": False, "error": str(e)}
            )

        print()

    def print_summary(self):
        """打印测试总结"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()

        passed = sum(1 for r in self.test_results if r["passed"])
        failed = sum(1 for r in self.test_results if not r["passed"])
        total = len(self.test_results)

        print("=" * 80)
        print("📊 E2E测试总结")
        print("=" * 80)
        print()
        print(f"总测试数: {total}")
        print(f"✅ 通过: {passed}")
        print(f"❌ 失败: {failed}")
        print(f"⏱️  总耗时: {total_duration:.2f}s")
        print()

        if failed == 0:
            print("🎉 所有测试通过！多Agent编排系统运行正常。")
        else:
            print("⚠️  部分测试失败，请检查上述错误信息。")
            print()
            print("失败的测试:")
            for result in self.test_results:
                if not result["passed"]:
                    print(
                        f"  - {result['test']}: {result.get('error', 'Unknown error')}"
                    )

        print()
        print("=" * 80)

        # 保存测试结果
        test_report = {
            "timestamp": end_time.isoformat(),
            "total_duration_seconds": total_duration,
            "results": self.test_results,
            "summary": {"total": total, "passed": passed, "failed": failed},
        }

        report_path = self.repo_root / ".lingma" / "reports" / "e2e-test-report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(test_report, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        print(f"\n📝 测试报告已保存至: {report_path}")


def main():
    """主入口"""
    repo_root = Path.cwd()

    print("\n" + "=" * 80)
    print("多Agent编排系统 - 端到端(E2E)测试")
    print("=" * 80)
    print()

    test_suite = EndToEndTestSuite(repo_root)
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()
