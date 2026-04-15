#!/usr/bin/env python3
"""
Spec Worker执行引擎 - 后台任务处理器

职责：
1. 异步处理Spec相关任务
2. 监控Spec状态变化
3. 自动执行低风险操作
4. 生成进度报告

架构：
- 基于文件系统的任务队列
- 轮询模式检测新任务
- 支持优先级调度
- 完整的错误处理和重试机制
"""

import json
import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum
import threading
import logging


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


class SpecTask:
    """Spec任务"""
    
    def __init__(self, task_id: str, task_type: str, payload: Dict, priority: TaskPriority = TaskPriority.MEDIUM):
        self.task_id = task_id
        self.task_type = task_type
        self.payload = payload
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        self.retry_count = 0
        self.max_retries = 3
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "payload": self.payload,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "retry_count": self.retry_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SpecTask':
        task = cls(
            task_id=data["task_id"],
            task_type=data["task_type"],
            payload=data["payload"],
            priority=TaskPriority(data.get("priority", 1))
        )
        task.status = TaskStatus(data["status"])
        task.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("started_at"):
            task.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        task.error = data.get("error")
        task.retry_count = data.get("retry_count", 0)
        return task


class TaskQueue:
    """
    基于文件系统的任务队列
    
    目录结构：
    .lingma/worker/tasks/
    ├── pending/      # 待处理任务
    ├── running/      # 运行中任务
    ├── completed/    # 已完成任务
    └── failed/       # 失败任务
    """
    
    def __init__(self, queue_dir: Path):
        self.queue_dir = queue_dir
        self.pending_dir = queue_dir / "pending"
        self.running_dir = queue_dir / "running"
        self.completed_dir = queue_dir / "completed"
        self.failed_dir = queue_dir / "failed"
        
        # 创建目录结构
        for dir_path in [self.pending_dir, self.running_dir, self.completed_dir, self.failed_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def enqueue(self, task: SpecTask):
        """添加任务到队列"""
        task_file = self.pending_dir / f"{task.task_id}.json"
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)
    
    def dequeue(self) -> Optional[SpecTask]:
        """获取最高优先级的待处理任务"""
        # 获取所有待处理任务
        pending_files = list(self.pending_dir.glob("*.json"))
        
        if not pending_files:
            return None
        
        # 按优先级排序（高优先级在前）
        tasks = []
        for task_file in pending_files:
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                    tasks.append(SpecTask.from_dict(task_data))
            except Exception as e:
                print(f"⚠️  无法读取任务文件 {task_file}: {e}", file=sys.stderr)
        
        if not tasks:
            return None
        
        # 选择最高优先级的任务
        tasks.sort(key=lambda t: t.priority.value, reverse=True)
        highest_priority_task = tasks[0]
        
        # 移动到running目录
        task_file = self.pending_dir / f"{highest_priority_task.task_id}.json"
        running_file = self.running_dir / f"{highest_priority_task.task_id}.json"
        shutil.move(str(task_file), str(running_file))
        
        highest_priority_task.status = TaskStatus.RUNNING
        highest_priority_task.started_at = datetime.now()
        
        return highest_priority_task
    
    def complete_task(self, task: SpecTask):
        """标记任务完成"""
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        
        running_file = self.running_dir / f"{task.task_id}.json"
        completed_file = self.completed_dir / f"{task.task_id}.json"
        
        if running_file.exists():
            with open(completed_file, 'w', encoding='utf-8') as f:
                json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)
            running_file.unlink()
    
    def fail_task(self, task: SpecTask, error: str):
        """标记任务失败"""
        task.status = TaskStatus.FAILED
        task.error = error
        task.completed_at = datetime.now()
        
        running_file = self.running_dir / f"{task.task_id}.json"
        failed_file = self.failed_dir / f"{task.task_id}.json"
        
        if running_file.exists():
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)
            running_file.unlink()
    
    def get_queue_stats(self) -> Dict:
        """获取队列统计信息"""
        return {
            "pending": len(list(self.pending_dir.glob("*.json"))),
            "running": len(list(self.running_dir.glob("*.json"))),
            "completed": len(list(self.completed_dir.glob("*.json"))),
            "failed": len(list(self.failed_dir.glob("*.json")))
        }


class SpecWorkerEngine:
    """
    Spec Worker执行引擎
    
    功能：
    1. 从任务队列获取任务
    2. 执行任务处理器
    3. 记录执行结果
    4. 支持热重载和优雅关闭
    """
    
    def __init__(self, repo_root: Path = None, poll_interval: float = 2.0):
        self.repo_root = repo_root or Path.cwd()
        self.poll_interval = poll_interval
        self.worker_dir = self.repo_root / ".lingma" / "worker"
        self.task_queue = TaskQueue(self.worker_dir / "tasks")
        self.log_file = self.repo_root / ".lingma" / "logs" / "worker.log"
        
        self.running = False
        self.current_task: Optional[SpecTask] = None
        self.processed_count = 0
        self.error_count = 0
        
        # 注册任务处理器
        self.task_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()
        
        # 配置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """配置日志系统"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("SpecWorker")
    
    def _register_default_handlers(self):
        """注册默认任务处理器"""
        self.task_handlers = {
            "validate_spec": self._handle_validate_spec,
            "update_spec_status": self._handle_update_spec_status,
            "generate_report": self._handle_generate_report,
            "cleanup_old_tasks": self._handle_cleanup_old_tasks,
        }
    
    def register_handler(self, task_type: str, handler: Callable):
        """注册自定义任务处理器"""
        self.task_handlers[task_type] = handler
        self.logger.info(f"注册任务处理器: {task_type}")
    
    def start(self):
        """启动Worker引擎"""
        self.logger.info("🚀 Spec Worker引擎启动")
        self.running = True
        
        try:
            while self.running:
                # 获取下一个任务
                task = self.task_queue.dequeue()
                
                if task is None:
                    # 没有任务，等待
                    time.sleep(self.poll_interval)
                    continue
                
                # 执行任务
                self._execute_task(task)
                
        except KeyboardInterrupt:
            self.logger.info("收到中断信号，正在关闭...")
        finally:
            self.shutdown()
    
    def stop(self):
        """停止Worker引擎"""
        self.logger.info("正在停止Worker引擎...")
        self.running = False
    
    def shutdown(self):
        """优雅关闭"""
        self.logger.info(f"Worker关闭 - 已处理: {self.processed_count}, 错误: {self.error_count}")
    
    def _execute_task(self, task: SpecTask):
        """执行单个任务"""
        self.current_task = task
        self.logger.info(f"执行任务: {task.task_id} (类型: {task.task_type})")
        
        try:
            # 查找处理器
            handler = self.task_handlers.get(task.task_type)
            
            if handler is None:
                raise ValueError(f"未找到任务处理器: {task.task_type}")
            
            # 执行任务
            result = handler(task)
            
            # 标记完成
            self.task_queue.complete_task(task)
            self.processed_count += 1
            
            self.logger.info(f"任务完成: {task.task_id}")
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"任务失败: {task.task_id} - {str(e)}")
            
            # 重试逻辑
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                self.task_queue.enqueue(task)
                self.logger.info(f"任务将重试 ({task.retry_count}/{task.max_retries}): {task.task_id}")
            else:
                self.task_queue.fail_task(task, str(e))
                self.logger.error(f"任务达到最大重试次数: {task.task_id}")
        
        finally:
            self.current_task = None
    
    # ==================== 默认任务处理器 ====================
    
    def _handle_validate_spec(self, task: SpecTask) -> Dict:
        """处理Spec验证任务"""
        # 动态导入避免循环依赖
        spec_validator_path = self.repo_root / ".lingma" / "scripts" / "spec-validator.py"
        if spec_validator_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("spec_validator", spec_validator_path)
            spec_validator_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(spec_validator_module)
            
            validator = spec_validator_module.SpecValidator(self.repo_root)
            is_valid, errors, warnings = validator.validate(strict_mode=False)
            
            return {
                "valid": is_valid,
                "errors_count": len(errors),
                "warnings_count": len(warnings),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"valid": False, "error": "spec-validator.py not found"}
    
    def _handle_update_spec_status(self, task: SpecTask) -> Dict:
        """处理Spec状态更新任务"""
        new_status = task.payload.get("status")
        spec_path = self.repo_root / ".lingma" / "specs" / "current-spec.md"
        
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec文件不存在: {spec_path}")
        
        content = spec_path.read_text(encoding='utf-8')
        
        # 简单替换状态（实际应该更智能地解析）
        if "- **状态**:" in content:
            updated_content = content.replace(
                content.split("- **状态**:")[1].split("\n")[0],
                f" {new_status}"
            )
            spec_path.write_text(updated_content, encoding='utf-8')
        
        return {
            "old_status": "unknown",
            "new_status": new_status,
            "updated": True
        }
    
    def _handle_generate_report(self, task: SpecTask) -> Dict:
        """处理报告生成任务"""
        stats = self.task_queue.get_queue_stats()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "queue_stats": stats,
            "worker_stats": {
                "processed_count": self.processed_count,
                "error_count": self.error_count,
                "uptime_seconds": 0  # 可以计算实际运行时间
            }
        }
        
        # 保存报告
        report_dir = self.repo_root / ".lingma" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"worker-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return {
            "report_file": str(report_file),
            "stats": stats
        }
    
    def _handle_cleanup_old_tasks(self, task: SpecTask) -> Dict:
        """处理旧任务清理任务"""
        retention_days = task.payload.get("retention_days", 7)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        cleaned_count = 0
        
        # 清理completed目录
        for task_file in self.task_queue.completed_dir.glob("*.json"):
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                    completed_at = datetime.fromisoformat(task_data["completed_at"])
                    
                    if completed_at < cutoff_date:
                        task_file.unlink()
                        cleaned_count += 1
            except Exception as e:
                self.logger.warning(f"无法清理任务文件 {task_file}: {e}")
        
        # 清理failed目录
        for task_file in self.task_queue.failed_dir.glob("*.json"):
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                    completed_at = datetime.fromisoformat(task_data["completed_at"])
                    
                    if completed_at < cutoff_date:
                        task_file.unlink()
                        cleaned_count += 1
            except Exception as e:
                self.logger.warning(f"无法清理任务文件 {task_file}: {e}")
        
        return {
            "cleaned_count": cleaned_count,
            "retention_days": retention_days
        }


def submit_task(task_type: str, payload: Dict, priority: TaskPriority = TaskPriority.MEDIUM, repo_root: Path = None):
    """
    提交任务到Worker队列
    
    Args:
        task_type: 任务类型
        payload: 任务参数
        priority: 优先级
        repo_root: 仓库根目录
    """
    repo_root = repo_root or Path.cwd()
    worker_dir = repo_root / ".lingma" / "worker"
    task_queue = TaskQueue(worker_dir / "tasks")
    
    task_id = f"{task_type}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{os.getpid()}"
    task = SpecTask(task_id, task_type, payload, priority)
    
    task_queue.enqueue(task)
    
    print(f"✅ 任务已提交: {task_id}")
    return task_id


def main():
    """命令行入口"""
    import argparse
    
    # Windows UTF-8支持
    if sys.platform == 'win32':
        import io
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    parser = argparse.ArgumentParser(description="Spec Worker执行引擎")
    parser.add_argument(
        "command",
        choices=["start", "submit", "status"],
        help="命令"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="仓库根目录（默认当前目录）"
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=2.0,
        help="轮询间隔（秒）"
    )
    parser.add_argument(
        "--task-type",
        type=str,
        help="任务类型（submit命令使用）"
    )
    parser.add_argument(
        "--payload",
        type=str,
        help="任务参数JSON（submit命令使用）"
    )
    parser.add_argument(
        "--priority",
        type=str,
        choices=["low", "medium", "high", "critical"],
        default="medium",
        help="任务优先级"
    )
    
    args = parser.parse_args()
    
    if args.command == "start":
        engine = SpecWorkerEngine(args.repo_root, args.poll_interval)
        engine.start()
    
    elif args.command == "submit":
        if not args.task_type:
            print("❌ 错误: 必须指定 --task-type")
            sys.exit(1)
        
        payload = {}
        if args.payload:
            try:
                payload = json.loads(args.payload)
            except json.JSONDecodeError as e:
                print(f"❌ 错误: 无效的JSON payload: {e}")
                sys.exit(1)
        
        priority_map = {
            "low": TaskPriority.LOW,
            "medium": TaskPriority.MEDIUM,
            "high": TaskPriority.HIGH,
            "critical": TaskPriority.CRITICAL
        }
        
        task_id = submit_task(
            args.task_type,
            payload,
            priority_map[args.priority],
            args.repo_root
        )
        print(f"任务ID: {task_id}")
    
    elif args.command == "status":
        repo_root = args.repo_root or Path.cwd()
        worker_dir = repo_root / ".lingma" / "worker"
        task_queue = TaskQueue(worker_dir / "tasks")
        
        stats = task_queue.get_queue_stats()
        print("\n📊 Worker队列状态:")
        print(f"  待处理: {stats['pending']}")
        print(f"  运行中: {stats['running']}")
        print(f"  已完成: {stats['completed']}")
        print(f"  失败:   {stats['failed']}")


if __name__ == "__main__":
    main()
