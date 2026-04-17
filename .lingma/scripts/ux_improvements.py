#!/usr/bin/env python3
"""
用户体验改进模块 - Phase 4 Task-014

职责：
1. 改进系统提示信息
2. 添加实时进度显示
3. 实现操作撤销功能
4. 提供友好的用户交互
"""

import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProgressDisplay:
    """进度显示管理器"""
    
    def __init__(self, total: int = 100, description: str = "处理中"):
        """
        初始化进度显示
        
        Args:
            total: 总任务数
            description: 任务描述
        """
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.last_update_time = 0
    
    def update(self, current: Optional[int] = None, increment: int = 1):
        """更新进度"""
        if current is not None:
            self.current = current
        else:
            self.current += increment
        
        # 限制更新频率（最多每秒更新一次）
        current_time = time.time()
        if current_time - self.last_update_time < 0.1:
            return
        
        self.last_update_time = current_time
        self._display()
    
    def _display(self):
        """显示进度条"""
        percentage = (self.current / self.total * 100) if self.total > 0 else 0
        elapsed = time.time() - self.start_time
        
        # 计算预计剩余时间
        if self.current > 0:
            avg_time_per_item = elapsed / self.current
            remaining_items = self.total - self.current
            eta = avg_time_per_item * remaining_items
        else:
            eta = 0
        
        # 创建进度条
        bar_length = 30
        filled_length = int(bar_length * self.current // self.total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # 格式化输出
        output = f"\r{self.description}: [{bar}] {percentage:.1f}% ({self.current}/{self.total})"
        output += f" | 耗时: {elapsed:.1f}s"
        if eta > 0:
            output += f" | 预计剩余: {eta:.1f}s"
        
        sys.stdout.write(output)
        sys.stdout.flush()
    
    def complete(self, message: str = "完成"):
        """完成任务"""
        self.current = self.total
        self._display()
        elapsed = time.time() - self.start_time
        print(f"\n✅ {message} (总耗时: {elapsed:.2f}s)")
    
    def __enter__(self):
        """上下文管理器入口"""
        self._display()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if exc_type is None:
            self.complete()
        else:
            print(f"\n❌ 任务失败: {exc_val}")


class MessageFormatter:
    """消息格式化工具"""
    
    @staticmethod
    def success(message: str, details: Optional[str] = None) -> str:
        """格式化成功消息"""
        result = f"✅ {message}"
        if details:
            result += f"\n   {details}"
        return result
    
    @staticmethod
    def warning(message: str, details: Optional[str] = None) -> str:
        """格式化警告消息"""
        result = f"⚠️  {message}"
        if details:
            result += f"\n   {details}"
        return result
    
    @staticmethod
    def error(message: str, details: Optional[str] = None) -> str:
        """格式化错误消息"""
        result = f"❌ {message}"
        if details:
            result += f"\n   {details}"
        return result
    
    @staticmethod
    def info(message: str, details: Optional[str] = None) -> str:
        """格式化信息消息"""
        result = f"ℹ️  {message}"
        if details:
            result += f"\n   {details}"
        return result
    
    @staticmethod
    def step(step_num: int, total_steps: int, message: str) -> str:
        """格式化步骤消息"""
        return f"[{step_num}/{total_steps}] {message}"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """格式化时间长度"""
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}小时"


class UndoManager:
    """操作撤销管理器"""
    
    def __init__(self, max_history: int = 50):
        """
        初始化撤销管理器
        
        Args:
            max_history: 最大历史记录数
        """
        self.max_history = max_history
        self.history: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []
    
    def record_action(self, action_type: str, details: Dict[str, Any], 
                     undo_func=None, redo_func=None):
        """
        记录操作
        
        Args:
            action_type: 操作类型
            details: 操作详情
            undo_func: 撤销函数
            redo_func: 重做函数
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'details': details,
            'undo_func': undo_func,
            'redo_func': redo_func
        }
        
        self.history.append(entry)
        
        # 限制历史记录大小
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # 清空重做栈
        self.redo_stack.clear()
    
    def undo(self) -> Optional[Dict[str, Any]]:
        """撤销最后一个操作"""
        if not self.history:
            return None
        
        entry = self.history.pop()
        
        # 执行撤销函数
        if entry.get('undo_func'):
            try:
                entry['undo_func'](entry['details'])
            except Exception as e:
                print(f"撤销失败: {e}")
        
        # 添加到重做栈
        self.redo_stack.append(entry)
        
        return entry
    
    def redo(self) -> Optional[Dict[str, Any]]:
        """重做最后一个撤销的操作"""
        if not self.redo_stack:
            return None
        
        entry = self.redo_stack.pop()
        
        # 执行重做函数
        if entry.get('redo_func'):
            try:
                entry['redo_func'](entry['details'])
            except Exception as e:
                print(f"重做失败: {e}")
        
        # 添加回历史记录
        self.history.append(entry)
        
        return entry
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取操作历史"""
        return self.history[-limit:]
    
    def clear(self):
        """清空历史"""
        self.history.clear()
        self.redo_stack.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            'history_size': len(self.history),
            'redo_stack_size': len(self.redo_stack),
            'max_history': self.max_history
        }


# 全局实例
_progress_display = None
_message_formatter = MessageFormatter()
_undo_manager = UndoManager()


def get_progress_display() -> ProgressDisplay:
    """获取进度显示实例"""
    global _progress_display
    return _progress_display


def create_progress(total: int, description: str = "处理中") -> ProgressDisplay:
    """创建进度显示"""
    global _progress_display
    _progress_display = ProgressDisplay(total=total, description=description)
    return _progress_display


def get_message_formatter() -> MessageFormatter:
    """获取消息格式化器"""
    return _message_formatter


def get_undo_manager() -> UndoManager:
    """获取撤销管理器"""
    return _undo_manager


if __name__ == "__main__":
    print("🧪 测试用户体验改进模块...\n")
    
    # 测试进度显示
    print("1️⃣  测试进度显示:")
    with create_progress(10, "测试任务") as progress:
        for i in range(10):
            time.sleep(0.1)
            progress.update()
    
    # 测试消息格式化
    print("\n2️⃣  测试消息格式化:")
    formatter = get_message_formatter()
    print(formatter.success("操作成功", "文件已保存"))
    print(formatter.warning("需要注意", "某些配置可能需要调整"))
    print(formatter.error("操作失败", "请检查网络连接"))
    print(formatter.info("提示信息", "这是一个示例"))
    print(formatter.step(2, 5, "正在处理数据"))
    print(f"   持续时间: {formatter.format_duration(125.5)}")
    
    # 测试撤销管理
    print("\n3️⃣  测试撤销管理:")
    undo_mgr = get_undo_manager()
    
    # 模拟操作
    test_data = {"value": 100}
    
    def undo_change(details):
        print(f"   撤销操作: {details}")
    
    def redo_change(details):
        print(f"   重做操作: {details}")
    
    undo_mgr.record_action("modify_value", test_data, undo_change, redo_change)
    print(f"   记录操作: {test_data}")
    
    # 撤销
    result = undo_mgr.undo()
    print(f"   撤销结果: {'成功' if result else '失败'}")
    
    # 重做
    result = undo_mgr.redo()
    print(f"   重做结果: {'成功' if result else '失败'}")
    
    # 查看历史
    history = undo_mgr.get_history()
    print(f"   历史记录数: {len(history)}")
    
    stats = undo_mgr.get_stats()
    print(f"   统计信息: {stats}")
    
    print("\n✅ 所有测试完成")
