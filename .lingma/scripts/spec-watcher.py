#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spec文件监听守护进程 - 实时监控Spec变化并触发重新评估

功能:
1. 使用watchdog库监听.lingma/specs/current-spec.md变化
2. 检测到修改后自动触发重新评估
3. 后台运行，支持Windows/Linux
4. 记录所有事件到.lingma/logs/watcher.log
5. 支持热重载配置

使用方式:
    python spec-watcher.py --start
    python spec-watcher.py --status
    python spec-watcher.py --stop
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
import time
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent
except ImportError:
    print("❌ 缺少依赖: watchdog")
    print("请运行: pip install watchdog")
    sys.exit(1)


class SpecFileHandler(FileSystemEventHandler):
    """Spec文件变化处理器"""

    def __init__(self, callback, log_path: str):
        """
        初始化处理器

        Args:
            callback: 文件变化时的回调函数
            log_path: 日志文件路径
        """
        super().__init__()
        self.callback = callback
        self.log_path = log_path
        self.last_modified = {}
        self.debounce_delay = 1.0  # 防抖延迟（秒）

    def on_modified(self, event):
        """文件修改事件"""
        if not event.is_directory and self._is_spec_file(event.src_path):
            self._handle_spec_change(event.src_path)

    def _is_spec_file(self, file_path: str) -> bool:
        """检查是否为Spec文件"""
        return "current-spec.md" in file_path or file_path.endswith(".md")

    def _handle_spec_change(self, file_path: str):
        """处理Spec文件变化"""
        current_time = time.time()

        # 防抖处理：避免短时间内多次触发
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < self.debounce_delay:
                return

        self.last_modified[file_path] = current_time

        # 记录事件
        self._log_event(
            "spec_modified",
            {"file": file_path, "timestamp": datetime.now().isoformat()},
        )

        # 触发回调
        try:
            self.callback(file_path)
        except Exception as e:
            self._log_event("callback_error", {"file": file_path, "error": str(e)})

    def _log_event(self, event_type: str, details: Dict):
        """记录事件到日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            **details,
        }

        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️  日志写入失败: {e}")


class SpecWatcher:
    """Spec文件监听守护进程"""

    def __init__(self, project_root: str = None):
        """
        初始化监听器

        Args:
            project_root: 项目根目录
        """
        self.project_root = project_root or self._find_project_root()
        self.spec_dir = os.path.join(self.project_root, ".lingma", "specs")
        self.spec_file = os.path.join(self.spec_dir, "current-spec.md")
        self.log_path = os.path.join(
            self.project_root, ".lingma", "logs", "watcher.log"
        )
        self.state_path = os.path.join(
            self.project_root, ".lingma", "worker", "watcher-state.json"
        )
        self.config_path = os.path.join(
            self.project_root, ".lingma", "config", "watcher-config.json"
        )

        # 确保目录存在
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)

        # 加载配置
        self.config = self._load_config()

        # 观察者
        self.observer = None
        self.running = False
        self.state = self._load_state()

    def _find_project_root(self) -> str:
        """查找项目根目录"""
        current_dir = os.getcwd()

        while current_dir != os.path.dirname(current_dir):
            if os.path.exists(os.path.join(current_dir, ".git")):
                return current_dir
            current_dir = os.path.dirname(current_dir)

        return os.getcwd()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        default_config = {
            "debounce_delay": 1.0,
            "auto_trigger_evaluation": True,
            "log_level": "INFO",
            "watch_patterns": ["*.md"],
            "exclude_patterns": ["*~", "*.tmp"],
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    default_config.update(config)
            except Exception as e:
                print(f"⚠️  配置文件加载失败: {e}，使用默认配置")

        return default_config

    def _save_config(self):
        """保存配置文件"""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def _load_state(self) -> Dict:
        """加载状态"""
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "watcher_id": f"watcher-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "stopped",
            "started_at": None,
            "events_count": 0,
            "last_event": None,
        }

    def _save_state(self):
        """保存状态"""
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _on_spec_change(self, file_path: str):
        """Spec文件变化回调"""
        print(f"\n📝 检测到Spec文件变化: {file_path}")

        self.state["events_count"] += 1
        self.state["last_event"] = datetime.now().isoformat()
        self._save_state()

        # 如果启用自动触发评估
        if self.config.get("auto_trigger_evaluation", True):
            print("🔄 触发重新评估...")
            self._trigger_evaluation(file_path)

    def _trigger_evaluation(self, file_path: str):
        """触发重新评估（可以调用spec-worker或其他评估逻辑）"""
        # 这里可以集成实际的评估逻辑
        # 例如：调用spec-worker.py或orchestrator.py

        evaluation_log = {
            "timestamp": datetime.now().isoformat(),
            "action": "evaluation_triggered",
            "file": file_path,
            "triggered_by": "spec-watcher",
        }

        audit_log_path = os.path.join(self.project_root, ".lingma", "logs", "audit.log")
        try:
            os.makedirs(os.path.dirname(audit_log_path), exist_ok=True)
            with open(audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(evaluation_log, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️  审计日志写入失败: {e}")

        print("✅ 评估已触发")

    def start(self):
        """启动监听器"""
        if self.running:
            print("⚠️  监听器已在运行")
            return

        print("=" * 60)
        print("Spec Watcher 启动")
        print("=" * 60)
        print(f"Watcher ID: {self.state['watcher_id']}")
        print(f"项目根目录: {self.project_root}")
        print(f"监听目录: {self.spec_dir}")
        print(f"日志文件: {self.log_path}")
        print(f"防抖延迟: {self.config.get('debounce_delay', 1.0)}秒")
        print("=" * 60)

        # 创建处理器
        handler = SpecFileHandler(callback=self._on_spec_change, log_path=self.log_path)
        handler.debounce_delay = self.config.get("debounce_delay", 1.0)

        # 创建观察者
        self.observer = Observer()
        self.observer.schedule(handler, self.spec_dir, recursive=False)

        # 启动观察者
        self.observer.start()
        self.running = True
        self.state["status"] = "running"
        self.state["started_at"] = datetime.now().isoformat()
        self._save_state()

        print("\n✅ Spec Watcher 正在运行...")
        print("按 Ctrl+C 停止\n")

        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # 保持运行
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """停止监听器"""
        if not self.running:
            print("⚠️  监听器未运行")
            return

        print("\n🛑 停止 Spec Watcher...")

        self.running = False

        if self.observer:
            self.observer.stop()
            self.observer.join()

        self.state["status"] = "stopped"
        self._save_state()

        print("✅ Spec Watcher 已停止")

    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n收到信号 {signum}，准备停止...")
        self.stop()

    def get_status(self) -> Dict:
        """获取监听器状态"""
        self._save_state()

        status = {
            "watcher_id": self.state["watcher_id"],
            "status": self.state["status"],
            "started_at": self.state["started_at"],
            "events_count": self.state["events_count"],
            "last_event": self.state["last_event"],
            "uptime": self._calculate_uptime(),
            "config": self.config,
        }

        return status

    def _calculate_uptime(self) -> Optional[str]:
        """计算运行时间"""
        if not self.state["started_at"]:
            return None

        started_at = datetime.fromisoformat(self.state["started_at"])
        uptime = datetime.now() - started_at

        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def reload_config(self):
        """热重载配置"""
        print("🔄 重新加载配置...")
        old_config = self.config.copy()
        self.config = self._load_config()

        # 如果有运行的观察者，更新防抖延迟
        if self.observer and hasattr(self.observer, "handlers"):
            for handler in self.observer.handlers:
                if isinstance(handler, SpecFileHandler):
                    handler.debounce_delay = self.config.get("debounce_delay", 1.0)

        print("✅ 配置已重新加载")

        return {"old_config": old_config, "new_config": self.config}


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Spec文件监听守护进程")
    parser.add_argument("--start", action="store_true", help="启动监听器")
    parser.add_argument("--stop", action="store_true", help="停止监听器")
    parser.add_argument("--status", action="store_true", help="查看状态")
    parser.add_argument("--reload", action="store_true", help="重新加载配置")
    parser.add_argument("--project-root", type=str, default=None, help="项目根目录")

    args = parser.parse_args()

    try:
        watcher = SpecWatcher(project_root=args.project_root)

        if args.start:
            watcher.start()

        elif args.stop:
            watcher.stop()

        elif args.status:
            status = watcher.get_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))

        elif args.reload:
            result = watcher.reload_config()
            print(json.dumps(result, indent=2, ensure_ascii=False))

        else:
            parser.print_help()

    except Exception as e:
        print(f"❌ Spec Watcher异常: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
