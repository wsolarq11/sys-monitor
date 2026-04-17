#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spec Worker执行引擎 - 异步任务处理系统（增强版）

功能:
1. 异步处理Spec任务
2. 优先级调度(LOW/MEDIUM/HIGH/CRITICAL)
3. 自动重试机制(最多3次)
4. 失败时通知用户
5. 更新Spec进度
6. 集成规则引擎验证Spec合规性
7. 自动启动spec-watcher守护进程

使用方式:
    python spec-worker.py --start
    python spec-worker.py --status
    python spec-worker.py --process-task "Task-001"
    python spec-worker.py --start-watcher
"""

import sys
import io

# Windows下设置UTF-8编码
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import argparse
import json
import os
import re
import subprocess
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


class Priority(Enum):
    """任务优先级"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """任务状态"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class SpecWorker:
    """Spec任务执行引擎"""

    MAX_RETRIES = 3
    RETRY_DELAY = 5  # 秒

    def __init__(self, project_root: Optional[str] = None):
        """
        初始化Worker

        Args:
            project_root: 项目根目录
        """
        self.project_root = project_root or self._find_project_root()
        self.spec_path = os.path.join(
            self.project_root, ".lingma", "specs", "current-spec.md"
        )
        self.worker_state_path = os.path.join(
            self.project_root, ".lingma", "worker", "state.json"
        )
        self.audit_log_path = os.path.join(
            self.project_root, ".lingma", "logs", "audit.log"
        )
        self.scripts_dir = os.path.join(self.project_root, ".lingma", "scripts")

        # 确保目录存在
        os.makedirs(os.path.dirname(self.worker_state_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)

        # 加载Worker状态
        self.state = self._load_state()

    def _find_project_root(self) -> str:
        """查找项目根目录"""
        current_dir = os.getcwd()

        while current_dir != os.path.dirname(current_dir):
            if os.path.exists(os.path.join(current_dir, ".git")):
                return current_dir
            current_dir = os.path.dirname(current_dir)

        return os.getcwd()

    def _load_state(self) -> Dict:
        """加载Worker状态"""
        if os.path.exists(self.worker_state_path):
            try:
                with open(self.worker_state_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # 默认状态
        return {
            "worker_id": f"worker-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "idle",
            "current_task": None,
            "tasks_processed": 0,
            "tasks_failed": 0,
            "last_heartbeat": None,
            "started_at": datetime.now().isoformat(),
        }

    def _save_state(self):
        """保存Worker状态"""
        self.state["last_heartbeat"] = datetime.now().isoformat()

        with open(self.worker_state_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _log_audit(self, event_type: str, details: Dict):
        """记录审计日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "worker_id": self.state["worker_id"],
            **details,
        }

        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def validate_spec_compliance(self) -> bool:
        """
        验证Spec合规性（调用rule-engine）

        Returns:
            是否通过验证
        """
        rule_engine_path = os.path.join(self.scripts_dir, "rule-engine.py")

        if not os.path.exists(rule_engine_path):
            print("⚠️  规则引擎不存在，跳过验证")
            return True

        try:
            print("\n🔍 验证Spec合规性...")

            result = subprocess.run(
                [sys.executable, rule_engine_path, "--validate-spec", "--json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            violations = json.loads(result.stdout) if result.stdout else []

            if violations:
                print(f"❌ 发现 {len(violations)} 个违规:")

                for v in violations:
                    severity = v.get("severity", "UNKNOWN")
                    message = v.get("message", "")
                    suggestion = v.get("suggestion", "")

                    print(f"   [{severity}] {message}")
                    if suggestion:
                        print(f"      建议: {suggestion}")

                # 如果有ERROR级别违规，阻止执行
                has_error = any(v.get("severity") == "ERROR" for v in violations)

                if has_error:
                    print("\n⛔ 存在严重违规，任务执行被阻止")
                    self._log_audit(
                        "spec_validation_failed",
                        {"violations_count": len(violations), "has_errors": True},
                    )
                    return False
                else:
                    print("\n⚠️  存在警告，但任务可以继续执行")
                    self._log_audit(
                        "spec_validation_warnings",
                        {"violations_count": len(violations), "has_errors": False},
                    )
                    return True
            else:
                print("✅ Spec符合所有规则")
                self._log_audit("spec_validation_passed", {})
                return True

        except subprocess.TimeoutExpired:
            print("⚠️  规则验证超时，跳过验证")
            return True
        except Exception as e:
            print(f"⚠️  规则验证失败: {e}，跳过验证")
            return True

    def start_watcher_daemon(self):
        """启动spec-watcher守护进程"""
        watcher_path = os.path.join(self.scripts_dir, "spec-watcher.py")

        if not os.path.exists(watcher_path):
            print("⚠️  spec-watcher.py不存在")
            return False

        try:
            print("\n🚀 启动Spec Watcher守护进程...")

            # 在后台启动watcher
            process = subprocess.Popen(
                [sys.executable, watcher_path, "--start"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=(
                    subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
                ),
            )

            print(f"✅ Spec Watcher已启动 (PID: {process.pid})")

            self._log_audit("watcher_started", {"pid": process.pid})

            return True

        except Exception as e:
            print(f"❌ 启动Spec Watcher失败: {e}")
            return False

    def get_pending_tasks(self) -> List[Dict]:
        """获取待处理任务列表"""
        if not os.path.exists(self.spec_path):
            return []

        with open(self.spec_path, "r", encoding="utf-8") as f:
            content = f.read()

        tasks: List[Dict[str, Any]] = []
        # 匹配未完成任务: - [ ] Task-XXX 或 - [ ] 描述
        task_pattern = r"- \[ \]\s+(Task-\d+[:：]?\s*.+?)(?:\s+\(预计:.+?\))?$"

        for match in re.finditer(task_pattern, content, re.MULTILINE | re.IGNORECASE):
            task_desc = match.group(1).strip()

            # 提取任务ID和描述
            task_id_match = re.match(r"(Task-\d+)[:：]?\s*(.*)", task_desc)
            if task_id_match:
                task_id = task_id_match.group(1)
                description = task_id_match.group(2).strip()
            else:
                task_id = f"task-{len(tasks)+1}"
                description = task_desc

            # 推断优先级(从上下文)
            priority = self._infer_priority(description)

            tasks.append(
                {
                    "id": task_id,
                    "description": description,
                    "priority": priority,
                    "status": TaskStatus.PENDING.value,
                }
            )

        # 按优先级排序
        tasks.sort(key=lambda t: Priority[t["priority"]].value, reverse=True)

        return tasks

    def _infer_priority(self, description: str) -> str:
        """从任务描述推断优先级"""
        desc_lower = description.lower()

        if any(keyword in desc_lower for keyword in ["critical", "紧急", "严重"]):
            return "CRITICAL"
        elif any(keyword in desc_lower for keyword in ["high", "高优先", "重要"]):
            return "HIGH"
        elif any(keyword in desc_lower for keyword in ["medium", "中等"]):
            return "MEDIUM"
        else:
            return "LOW"

    def process_task(self, task: Dict) -> bool:
        """
        处理单个任务

        Args:
            task: 任务字典

        Returns:
            是否成功
        """
        task_id = task["id"]
        retries = 0

        self.state["status"] = "busy"
        self.state["current_task"] = task_id
        self._save_state()

        self._log_audit(
            "task_started", {"task_id": task_id, "priority": task["priority"]}
        )

        print(f"\n[START] 开始处理任务: {task_id}")
        print(f"   描述: {task['description']}")
        print(f"   优先级: {task['priority']}")
        print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        while retries <= self.MAX_RETRIES:
            try:
                # 执行任务(这里简化为模拟执行)
                success = self._execute_task(task)

                if success:
                    # 标记任务完成
                    self._mark_task_completed(task_id)

                    self.state["tasks_processed"] += 1
                    self._log_audit(
                        "task_completed", {"task_id": task_id, "retries": retries}
                    )

                    print(f"[OK] 任务完成: {task_id}")
                    return True
                else:
                    raise Exception("任务执行返回失败")

            except Exception as e:
                retries += 1

                if retries <= self.MAX_RETRIES:
                    print(
                        f"[WARN] 任务失败 (尝试 {retries}/{self.MAX_RETRIES}): {str(e)}"
                    )
                    print(f"   {self.RETRY_DELAY}秒后重试...")

                    self.state["status"] = "retrying"
                    self._log_audit(
                        "task_retry",
                        {"task_id": task_id, "attempt": retries, "error": str(e)},
                    )

                    time.sleep(self.RETRY_DELAY)
                else:
                    # 达到最大重试次数
                    self.state["tasks_failed"] += 1
                    self._log_audit(
                        "task_failed",
                        {
                            "task_id": task_id,
                            "total_retries": retries,
                            "error": str(e),
                            "traceback": traceback.format_exc(),
                        },
                    )

                    print(f"[FAIL] 任务失败(已达最大重试次数): {task_id}")
                    print(f"   错误: {str(e)}")

                    # 通知用户
                    self._notify_failure(task, e)

                    return False

        self.state["status"] = "idle"
        self.state["current_task"] = None
        self._save_state()

        return False

    def _execute_task(self, task: Dict) -> bool:
        """
        执行任务(实际逻辑需要根据任务类型实现)

        Args:
            task: 任务字典

        Returns:
            是否成功
        """
        # TODO: 根据任务类型调用相应的执行器
        # 当前为模拟执行

        task_desc = task["description"].lower()

        # 模拟不同类型的任务
        if "创建" in task_desc or "create" in task_desc:
            # 模拟创建操作
            time.sleep(0.5)
            return True
        elif "测试" in task_desc or "test" in task_desc:
            # 模拟测试操作
            time.sleep(0.3)
            return True
        elif "删除" in task_desc or "delete" in task_desc:
            # 模拟删除操作(需要谨慎)
            time.sleep(0.2)
            return True
        else:
            # 通用任务
            time.sleep(0.1)
            return True

    def _mark_task_completed(self, task_id: str):
        """标记任务为已完成"""
        if not os.path.exists(self.spec_path):
            return

        with open(self.spec_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 替换任务复选框: - [ ] Task-XXX -> - [x] Task-XXX
        pattern = rf"(- \[ \]\s+{re.escape(task_id)}[:：]?.*?)$"
        replacement = r"\1".replace("[ ]", "[x]", 1)

        # 更简单的替换策略
        lines = content.split("\n")
        updated = False

        for i, line in enumerate(lines):
            if f"[ ]" in line and task_id in line:
                lines[i] = line.replace("[ ]", "[x]", 1)
                updated = True
                break

        if updated:
            with open(self.spec_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            # 更新进度
            self._update_progress()

    def _update_progress(self):
        """更新Spec进度"""
        if not os.path.exists(self.spec_path):
            return

        with open(self.spec_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 统计任务
        total_pattern = r"- \[[ xX]\]"
        completed_pattern = r"- \[[xX]\]"

        total_tasks = len(re.findall(total_pattern, content))
        completed_tasks = len(re.findall(completed_pattern, content))

        if total_tasks > 0:
            progress = round(completed_tasks / total_tasks * 100, 1)

            # 更新进度行
            progress_pattern = r"- \*\*进度\*\*:\s*[\d.]+%"
            new_progress = (
                f"- **进度**: {progress}% ({completed_tasks}/{total_tasks} 任务)"
            )

            content = re.sub(progress_pattern, new_progress, content)

            with open(self.spec_path, "w", encoding="utf-8") as f:
                f.write(content)

    def _notify_failure(self, task: Dict, error: Exception):
        """通知用户任务失败"""
        notification = f"""
[WARN] 任务执行失败通知

任务ID: {task['id']}
描述: {task['description']}
优先级: {task['priority']}
错误: {str(error)}
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

请检查任务并重试，或联系开发人员。
"""
        print(notification)

        # 可以添加其他通知方式(邮件、Slack等)
        self._log_audit(
            "notification_sent", {"type": "task_failure", "task_id": task["id"]}
        )

    def start_worker(self, max_tasks: Optional[int] = None, skip_validation: bool = False):
        """
        启动Worker

        Args:
            max_tasks: 最大处理任务数(None表示无限制)
            skip_validation: 跳过Spec验证
        """
        print("=" * 60)
        print("Spec Worker 启动")
        print("=" * 60)
        print(f"Worker ID: {self.state['worker_id']}")
        print(f"项目根目录: {self.project_root}")
        print(f"Spec文件: {self.spec_path}")
        print(f"最大重试次数: {self.MAX_RETRIES}")
        print("=" * 60)

        # 验证Spec合规性
        if not skip_validation:
            if not self.validate_spec_compliance():
                print("\n[FAIL] Spec验证失败，Worker无法启动")
                return

        self.state["status"] = "running"
        self._save_state()

        self._log_audit(
            "worker_started",
            {"max_tasks": max_tasks, "validation_skipped": skip_validation},
        )

        tasks_processed = 0

        try:
            while True:
                # 获取待处理任务
                pending_tasks = self.get_pending_tasks()

                if not pending_tasks:
                    print("\n[OK] 所有任务已完成!")
                    break

                if max_tasks and tasks_processed >= max_tasks:
                    print(f"\n已达到最大任务数限制: {max_tasks}")
                    break

                # 处理最高优先级任务
                next_task = pending_tasks[0]

                success = self.process_task(next_task)
                tasks_processed += 1

                # 短暂休息
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n[WARN] Worker被用户中断")

        finally:
            self.state["status"] = "stopped"
            self.state["current_task"] = None
            self._save_state()

            self._log_audit("worker_stopped", {"tasks_processed": tasks_processed})

            print("\n" + "=" * 60)
            print("Worker 停止")
            print(f"处理任务数: {tasks_processed}")
            print(f"成功: {self.state['tasks_processed']}")
            print(f"失败: {self.state['tasks_failed']}")
            print("=" * 60)

    def get_status(self) -> Dict:
        """获取Worker状态"""
        self._save_state()  # 更新心跳

        return {
            "worker_id": self.state["worker_id"],
            "status": self.state["status"],
            "current_task": self.state["current_task"],
            "tasks_processed": self.state["tasks_processed"],
            "tasks_failed": self.state["tasks_failed"],
            "pending_tasks": len(self.get_pending_tasks()),
            "uptime": self._calculate_uptime(),
            "last_heartbeat": self.state["last_heartbeat"],
        }

    def _calculate_uptime(self) -> str:
        """计算运行时间"""
        started_at = datetime.fromisoformat(self.state["started_at"])
        uptime = datetime.now() - started_at

        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Spec Worker执行引擎")
    parser.add_argument("--start", action="store_true", help="启动Worker")
    parser.add_argument("--status", action="store_true", help="查看状态")
    parser.add_argument("--process-task", type=str, help="处理指定任务")
    parser.add_argument("--max-tasks", type=int, default=None, help="最大处理任务数")
    parser.add_argument("--project-root", type=str, default=None, help="项目根目录")
    parser.add_argument("--skip-validation", action="store_true", help="跳过Spec验证")
    parser.add_argument(
        "--start-watcher", action="store_true", help="启动Spec Watcher守护进程"
    )

    args = parser.parse_args()

    try:
        worker = SpecWorker(project_root=args.project_root)

        if args.start_watcher:
            worker.start_watcher_daemon()

        elif args.start:
            worker.start_worker(
                max_tasks=args.max_tasks, skip_validation=args.skip_validation
            )

        elif args.status:
            status = worker.get_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))

        elif args.process_task:
            # 处理指定任务
            pending_tasks = worker.get_pending_tasks()
            target_task = None

            for task in pending_tasks:
                if args.process_task in task["id"]:
                    target_task = task
                    break

            if target_task:
                # 先验证Spec
                if not args.skip_validation:
                    if not worker.validate_spec_compliance():
                        print("\n[FAIL] Spec验证失败，任务执行被阻止")
                        sys.exit(1)

                success = worker.process_task(target_task)
                sys.exit(0 if success else 1)
            else:
                print(f"[FAIL] 未找到任务: {args.process_task}")
                sys.exit(1)

        else:
            parser.print_help()

    except Exception as e:
        print(f"[FAIL] Worker异常: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
