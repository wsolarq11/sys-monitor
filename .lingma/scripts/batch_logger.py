#!/usr/bin/env python3
"""
批量日志写入优化模块

职责：
1. 批量收集日志条目
2. 异步写入日志文件
3. 减少磁盘 I/O 次数
4. 提高日志写入性能
"""

import time
import json
import threading
from pathlib import Path
from typing import List, Dict, Any
from queue import Queue, Empty
from datetime import datetime


class BatchLogger:
    """批量日志写入器"""

    def __init__(
        self,
        log_file: str = ".lingma/logs/automation.log",
        batch_size: int = 10,
        flush_interval: float = 5.0,
    ):
        """
        初始化批量日志写入器

        Args:
            log_file: 日志文件路径
            batch_size: 批量大小（达到此数量时立即写入）
            flush_interval: 刷新间隔（秒），即使未达到批量大小也会写入
        """
        self.log_file = Path(log_file)
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        # 确保日志目录存在
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # 日志队列
        self.log_queue: Queue[Dict[str, Any]] = Queue()

        # 批量缓冲区
        self.batch_buffer: List[Dict[str, Any]] = []

        # 控制标志
        self.running = True
        self.lock = threading.Lock()

        # 启动后台写入线程
        self.writer_thread = threading.Thread(
            target=self._background_writer, daemon=True
        )
        self.writer_thread.start()

        # 统计信息
        self.total_logs = 0
        self.total_batches = 0
        self.total_flushes = 0

    def log(self, entry: Dict[str, Any]):
        """添加日志条目"""
        # 添加时间戳
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.utcnow().isoformat() + "Z"

        self.log_queue.put(entry)
        self.total_logs += 1

    def _background_writer(self):
        """后台写入线程"""
        last_flush_time = time.time()

        while self.running:
            try:
                # 尝试从队列获取日志条目（超时以便定期检查刷新间隔）
                entry = self.log_queue.get(timeout=0.1)
                self.batch_buffer.append(entry)

                # 检查是否达到批量大小
                if len(self.batch_buffer) >= self.batch_size:
                    self._flush_buffer()
                    last_flush_time = time.time()

            except Empty:
                # 队列为空，检查是否需要基于时间刷新
                current_time = time.time()
                if (
                    current_time - last_flush_time
                ) >= self.flush_interval and self.batch_buffer:
                    self._flush_buffer()
                    last_flush_time = current_time

            except Exception as e:
                print(f"日志写入错误: {e}")

    def _flush_buffer(self):
        """刷新缓冲区到磁盘"""
        if not self.batch_buffer:
            return

        with self.lock:
            try:
                # 追加写入日志文件
                with open(self.log_file, "a", encoding="utf-8") as f:
                    for entry in self.batch_buffer:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

                self.total_batches += 1
                self.batch_buffer.clear()

            except Exception as e:
                print(f"刷新日志缓冲区失败: {e}")

    def flush(self):
        """立即刷新所有待处理的日志"""
        # 处理队列中剩余的条目
        while not self.log_queue.empty():
            try:
                entry = self.log_queue.get_nowait()
                self.batch_buffer.append(entry)
            except Empty:
                break

        # 刷新缓冲区
        self._flush_buffer()
        self.total_flushes += 1

    def stop(self):
        """停止日志写入器"""
        self.running = False

        # 等待队列处理完毕
        while not self.log_queue.empty():
            try:
                entry = self.log_queue.get_nowait()
                self.batch_buffer.append(entry)
            except Empty:
                break

        # 最后刷新
        self._flush_buffer()

        # 等待线程结束
        self.writer_thread.join(timeout=5)

    def get_stats(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        return {
            "total_logs": self.total_logs,
            "total_batches": self.total_batches,
            "total_flushes": self.total_flushes,
            "queue_size": self.log_queue.qsize(),
            "buffer_size": len(self.batch_buffer),
            "batch_size": self.batch_size,
            "flush_interval_seconds": self.flush_interval,
        }

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()


# 全局日志实例
_batch_logger = None


def get_batch_logger() -> BatchLogger:
    """获取全局批量日志实例"""
    global _batch_logger
    if _batch_logger is None:
        _batch_logger = BatchLogger()
    return _batch_logger


def log_entry(entry: Dict[str, Any]):
    """记录日志条目的便捷函数"""
    logger = get_batch_logger()
    logger.log(entry)


def flush_logs():
    """刷新所有待处理日志的便捷函数"""
    logger = get_batch_logger()
    logger.flush()


if __name__ == "__main__":
    import random

    print("🧪 测试批量日志写入器...")

    # 使用上下文管理器
    with BatchLogger(batch_size=5, flush_interval=2.0) as logger:
        # 模拟生成日志
        for i in range(20):
            entry = {
                "level": random.choice(["INFO", "WARNING", "ERROR"]),
                "message": f"Test log entry {i}",
                "operation": f"operation_{i % 5}",
            }
            logger.log(entry)
            time.sleep(0.05)  # 模拟操作间隔

        print(f"\n📊 日志统计:")
        stats = logger.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")

    print("\n✅ 批量日志测试完成")

    # 验证日志文件
    log_file = Path(".lingma/logs/automation.log")
    if log_file.exists():
        line_count = sum(1 for _ in open(log_file, "r", encoding="utf-8"))
        print(f"📄 日志文件行数: {line_count}")
    else:
        print("⚠️  日志文件不存在")
