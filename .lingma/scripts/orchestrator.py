#!/usr/bin/env python3
"""
Orchestrator - 多Agent编排系统入口脚本

职责：
1. 接收用户请求
2. 创建任务并委派给Supervisor
3. 轮询检查完成状态
4. 聚合结果并返回

使用方式：
    python orchestrator.py --request "实现用户认证功能"
    python orchestrator.py --status <task_id>
    python orchestrator.py --list
"""

import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from worker.task_queue import TaskQueue, Task, TaskPriority, TaskStatus
from worker.agent_client import AgentClient


class Orchestrator:
    """
    编排器 - 用户请求的入口点
    
    工作流程：
    1. 接收用户请求
    2. 调用Supervisor Agent进行任务分解
    3. 监控任务执行进度
    4. 聚合结果并返回
    """
    
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path.cwd()
        self.task_queue = TaskQueue(self.repo_root / ".lingma" / "worker" / "tasks")
        self.agent_client = AgentClient(
            agents_dir=self.repo_root / ".lingma" / "agents",
            default_timeout=60,
            log_dir=self.repo_root / ".lingma" / "logs"
        )
        
        # 决策日志文件
        self.decision_log_path = self.repo_root / ".lingma" / "logs" / "decision-log.json"
    
    def submit_request(self, user_request: str, priority: str = "MEDIUM") -> str:
        """
        提交用户请求
        
        Args:
            user_request: 用户的自然语言请求
            priority: 任务优先级 (LOW/MEDIUM/HIGH/CRITICAL)
            
        Returns:
            主任务ID
        """
        print(f"📥 接收请求: {user_request}")
        
        # Step 1: 创建主任务，委派给Supervisor Agent
        priority_enum = TaskPriority[priority.upper()]
        
        main_task = Task(
            task_type="supervisor_orchestration",
            payload={
                "user_request": user_request,
                "priority": priority,
                "submitted_at": datetime.now().isoformat()
            },
            priority=priority_enum,
            assigned_agent="supervisor-agent",
            timeout_seconds=600  # 10分钟超时
        )
        
        task_id = self.task_queue.enqueue(main_task)
        
        print(f"✅ 任务已创建: {task_id}")
        print(f"   优先级: {priority}")
        print(f"   委派给: supervisor-agent")
        
        # Step 2: 记录决策日志
        self._log_decision("REQUEST_SUBMITTED", {
            "task_id": task_id,
            "user_request": user_request,
            "priority": priority
        })
        
        return task_id
    
    def execute_and_wait(self, task_id: str, poll_interval: float = 2.0, timeout: int = 600) -> Dict[str, Any]:
        """
        执行任务并等待完成
        
        Args:
            task_id: 任务ID
            poll_interval: 轮询间隔（秒）
            timeout: 超时时间（秒）
            
        Returns:
            任务执行结果
        """
        print(f"\n🚀 开始执行任务: {task_id}")
        print(f"   轮询间隔: {poll_interval}s")
        print(f"   超时时间: {timeout}s\n")
        
        start_time = time.time()
        
        while True:
            # 检查超时
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"❌ 任务超时 ({timeout}s)")
                self._log_decision("TASK_TIMEOUT", {
                    "task_id": task_id,
                    "elapsed_seconds": elapsed
                })
                return {
                    "status": "TIMEOUT",
                    "error": f"Task timed out after {timeout}s"
                }
            
            # 获取任务状态
            task = self.task_queue.get_task(task_id)
            
            if task is None:
                print(f"⚠️  任务不存在: {task_id}")
                return {
                    "status": "NOT_FOUND",
                    "error": f"Task {task_id} not found"
                }
            
            # 显示进度
            status_icon = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.RUNNING: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.FAILED: "❌"
            }.get(task.status, "❓")
            
            print(f"   {status_icon} 状态: {task.status.value} (已用时: {elapsed:.1f}s)")
            
            # 检查是否完成
            if task.status == TaskStatus.COMPLETED:
                print(f"\n✅ 任务完成!")
                print(f"   总用时: {elapsed:.1f}s")
                
                result = {
                    "status": "COMPLETED",
                    "task_id": task_id,
                    "result": task.result,
                    "elapsed_seconds": elapsed
                }
                
                self._log_decision("TASK_COMPLETED", {
                    "task_id": task_id,
                    "elapsed_seconds": elapsed
                })
                
                return result
            
            elif task.status == TaskStatus.FAILED:
                print(f"\n❌ 任务失败!")
                print(f"   错误: {task.error}")
                
                result = {
                    "status": "FAILED",
                    "task_id": task_id,
                    "error": task.error,
                    "elapsed_seconds": elapsed
                }
                
                self._log_decision("TASK_FAILED", {
                    "task_id": task_id,
                    "error": task.error,
                    "elapsed_seconds": elapsed
                })
                
                return result
            
            # 继续轮询
            time.sleep(poll_interval)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        查询任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务信息字典
        """
        task = self.task_queue.get_task(task_id)
        
        if task is None:
            return None
        
        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "status": task.status.value,
            "priority": task.priority.name,
            "assigned_agent": task.assigned_agent,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error": task.error,
            "result": task.result,
            "retry_count": task.retry_count
        }
    
    def list_tasks(self, status_filter: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        列出任务
        
        Args:
            status_filter: 状态过滤器 (pending/running/completed/failed)
            limit: 最大返回数量
            
        Returns:
            任务列表
        """
        tasks = []
        
        # 确定要扫描的目录
        directories = []
        if status_filter is None:
            directories = [
                self.task_queue.pending_dir,
                self.task_queue.running_dir,
                self.task_queue.completed_dir,
                self.task_queue.failed_dir
            ]
        else:
            dir_map = {
                "pending": self.task_queue.pending_dir,
                "running": self.task_queue.running_dir,
                "completed": self.task_queue.completed_dir,
                "failed": self.task_queue.failed_dir
            }
            if status_filter in dir_map:
                directories = [dir_map[status_filter]]
        
        # 读取任务文件
        for directory in directories:
            for task_file in sorted(directory.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                        tasks.append({
                            "task_id": task_data["task_id"],
                            "task_type": task_data["task_type"],
                            "status": task_data["status"],
                            "priority": TaskPriority(task_data["priority"]).name,
                            "created_at": task_data["created_at"],
                            "assigned_agent": task_data.get("assigned_agent")
                        })
                        
                        if len(tasks) >= limit:
                            return tasks
                except Exception as e:
                    print(f"⚠️  无法读取任务文件 {task_file}: {e}", file=sys.stderr)
        
        return tasks
    
    def get_queue_stats(self) -> Dict[str, int]:
        """
        获取队列统计信息
        
        Returns:
            各状态任务数量
        """
        return self.task_queue.get_queue_stats()
    
    def _log_decision(self, action: str, metadata: Dict[str, Any]):
        """
        记录决策日志
        
        Args:
            action: 动作描述
            metadata: 元数据
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "orchestrator",
            "action": action,
            "metadata": metadata
        }
        
        # 确保日志目录存在
        self.decision_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 读取现有日志
        logs = []
        if self.decision_log_path.exists():
            try:
                with open(self.decision_log_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
        
        # 追加新日志
        logs.append(log_entry)
        
        # 写入日志
        with open(self.decision_log_path, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="多Agent编排系统 - Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 提交新请求
  python orchestrator.py --request "实现用户认证功能"
  
  # 指定优先级
  python orchestrator.py --request "修复登录bug" --priority HIGH
  
  # 查询任务状态
  python orchestrator.py --status <task_id>
  
  # 列出所有任务
  python orchestrator.py --list
  
  # 列出待处理任务
  python orchestrator.py --list --filter pending
  
  # 查看队列统计
  python orchestrator.py --stats
        """
    )
    
    parser.add_argument(
        "--request",
        type=str,
        help="提交用户请求（自然语言）"
    )
    
    parser.add_argument(
        "--priority",
        type=str,
        choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        default="MEDIUM",
        help="任务优先级（默认: MEDIUM）"
    )
    
    parser.add_argument(
        "--status",
        type=str,
        help="查询任务状态（需要提供task_id）"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出任务"
    )
    
    parser.add_argument(
        "--filter",
        type=str,
        choices=["pending", "running", "completed", "failed"],
        help="任务状态过滤器（与--list配合使用）"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="列出任务时的最大数量（默认: 10）"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="显示队列统计信息"
    )
    
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="仓库根目录（默认: 当前目录）"
    )
    
    args = parser.parse_args()
    
    # 创建Orchestrator实例
    orchestrator = Orchestrator(args.repo_root)
    
    # 处理命令
    if args.request:
        # 提交请求
        task_id = orchestrator.submit_request(args.request, args.priority)
        
        # 询问是否立即执行并等待
        print(f"\n是否立即执行并等待结果? (y/n): ", end="")
        try:
            response = input().strip().lower()
            if response == 'y':
                result = orchestrator.execute_and_wait(task_id)
                print(f"\n📊 执行结果:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
        except EOFError:
            # 非交互模式，不等待
            print("\n💡 提示: 使用 --status 命令查询任务状态")
    
    elif args.status:
        # 查询状态
        status = orchestrator.get_task_status(args.status)
        if status:
            print(f"\n📋 任务状态:")
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print(f"❌ 任务不存在: {args.status}")
    
    elif args.list:
        # 列出任务
        tasks = orchestrator.list_tasks(args.filter, args.limit)
        
        if tasks:
            print(f"\n📋 任务列表 (共{len(tasks)}个):")
            print("-" * 80)
            for task in tasks:
                status_icon = {
                    "pending": "⏳",
                    "running": "🔄",
                    "completed": "✅",
                    "failed": "❌"
                }.get(task["status"], "❓")
                
                print(f"{status_icon} [{task['priority']}] {task['task_id'][:8]}...")
                print(f"   类型: {task['task_type']}")
                print(f"   状态: {task['status']}")
                print(f"   Agent: {task.get('assigned_agent', 'N/A')}")
                print(f"   创建时间: {task['created_at']}")
                print()
        else:
            print("\n📭 没有任务")
    
    elif args.stats:
        # 显示统计
        stats = orchestrator.get_queue_stats()
        print(f"\n📊 队列统计:")
        print(f"  待处理: {stats['pending']}")
        print(f"  运行中: {stats['running']}")
        print(f"  已完成: {stats['completed']}")
        print(f"  失败:   {stats['failed']}")
        print(f"  总计:   {sum(stats.values())}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
