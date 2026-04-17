#!/usr/bin/env python3
"""
用户体验改进整合器 - Phase 4 Task-014

职责：
1. 整合所有 UX 改进功能
2. 提供统一的接口
3. 生成 UX 改进报告
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from ux_improvements import (
    ProgressDisplay, 
    MessageFormatter, 
    UndoManager,
    create_progress,
    get_message_formatter,
    get_undo_manager
)
from interactive_cli import InteractiveCLI


class UXImprovementSuite:
    """用户体验改进套件"""
    
    def __init__(self):
        self.formatter = get_message_formatter()
        self.undo_manager = get_undo_manager()
        self.cli = None
    
    def demo_progress_display(self):
        """演示进度显示功能"""
        print("\n" + "="*60)
        print("📊 演示：进度显示功能")
        print("="*60 + "\n")
        
        # 示例 1: 基本进度条
        print("示例 1: 基本进度条")
        with create_progress(20, "数据处理") as progress:
            for i in range(20):
                time.sleep(0.05)
                progress.update()
        
        # 示例 2: 自定义更新
        print("\n示例 2: 自定义更新")
        progress = create_progress(100, "文件上传")
        for i in range(0, 101, 10):
            time.sleep(0.05)
            progress.update(current=i)
        progress.complete("上传完成")
    
    def demo_message_formatting(self):
        """演示消息格式化功能"""
        print("\n" + "="*60)
        print("💬 演示：消息格式化功能")
        print("="*60 + "\n")
        
        formatter = self.formatter
        
        # 各种消息类型
        print(formatter.success("操作成功", "文件已保存到 /path/to/file"))
        print()
        print(formatter.warning("配置警告", "某些参数使用了默认值"))
        print()
        print(formatter.error("连接失败", "无法连接到服务器，请检查网络"))
        print()
        print(formatter.info("系统提示", "新版本可用"))
        print()
        print(formatter.step(3, 5, "正在编译代码"))
        print()
        print(f"执行时间: {formatter.format_duration(125.7)}")
        print(f"执行时间: {formatter.format_duration(0.5)}")
        print(f"执行时间: {formatter.format_duration(3661)}")
    
    def demo_undo_redo(self):
        """演示撤销/重做功能"""
        print("\n" + "="*60)
        print("↩️  演示：撤销/重做功能")
        print("="*60 + "\n")
        
        undo_mgr = self.undo_manager
        
        # 模拟一些操作
        operations = [
            {"type": "create_file", "path": "test1.txt"},
            {"type": "modify_file", "path": "test2.txt", "content": "new content"},
            {"type": "delete_file", "path": "test3.txt"},
        ]
        
        def undo_operation(details):
            print(f"   ↩️  撤销: {details['type']} - {details.get('path', 'N/A')}")
        
        def redo_operation(details):
            print(f"   ↪️  重做: {details['type']} - {details.get('path', 'N/A')}")
        
        # 记录操作
        print("记录操作:")
        for op in operations:
            undo_mgr.record_action(op['type'], op, undo_operation, redo_operation)
            print(f"   ✅ {op['type']}: {op.get('path', 'N/A')}")
        
        # 查看历史
        print(f"\n历史记录数: {len(undo_mgr.get_history())}")
        
        # 撤销最后一个操作
        print("\n执行撤销:")
        result = undo_mgr.undo()
        if result:
            print(f"   撤销成功: {result['action_type']}")
        
        # 重做
        print("\n执行重做:")
        result = undo_mgr.redo()
        if result:
            print(f"   重做成功: {result['action_type']}")
        
        # 统计信息
        stats = undo_mgr.get_stats()
        print(f"\n统计信息: {stats}")
    
    def demo_interactive_cli(self):
        """演示交互式 CLI"""
        print("\n" + "="*60)
        print("💻 演示：交互式命令行界面")
        print("="*60 + "\n")
        
        print("启动交互式 CLI（输入 'help' 查看命令，'quit' 退出）\n")
        
        # 创建 CLI
        cli = InteractiveCLI(prompt="ux-demo> ")
        
        # 注册演示命令
        def cmd_hello(*args):
            name = args[0] if args else "World"
            return f"👋 Hello, {name}!"
        
        def cmd_time(*args):
            import datetime
            return f"🕐 当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        def cmd_calculate(*args):
            if len(args) < 3:
                return "用法: calculate <num1> <operator> <num2>"
            try:
                num1 = float(args[0])
                operator = args[1]
                num2 = float(args[2])
                
                if operator == '+':
                    result = num1 + num2
                elif operator == '-':
                    result = num1 - num2
                elif operator == '*':
                    result = num1 * num2
                elif operator == '/':
                    result = num1 / num2 if num2 != 0 else "错误: 除零"
                else:
                    return f"未知运算符: {operator}"
                
                return f"🧮 计算结果: {num1} {operator} {num2} = {result}"
            except ValueError:
                return "错误: 无效的数字"
        
        cli.register_command('hello', cmd_hello, '打招呼', ['hi'])
        cli.register_command('time', cmd_time, '显示当前时间', ['now'])
        cli.register_command('calculate', cmd_calculate, '执行计算', ['calc'])
        
        # 运行 CLI（限时演示）
        print("提示: 这是一个演示版本，将在 30 秒后自动退出\n")
        
        start_time = time.time()
        timeout = 30  # 30 秒超时
        
        cli.running = True
        while cli.running:
            try:
                # 检查超时
                if time.time() - start_time > timeout:
                    print("\n⏱️  演示超时，自动退出\n")
                    break
                
                command_line = input(cli.prompt)
                cli.running = cli.execute_command(command_line)
                
            except (KeyboardInterrupt, EOFError):
                break
        
        print("👋 CLI 演示结束\n")
    
    def run_full_demo(self):
        """运行完整演示"""
        print("\n" + "🎨"*30)
        print("用户体验改进功能完整演示")
        print("🎨"*30 + "\n")
        
        # 运行所有演示
        self.demo_progress_display()
        self.demo_message_formatting()
        self.demo_undo_redo()
        self.demo_interactive_cli()
        
        # 生成总结
        self._print_summary()
    
    def _print_summary(self):
        """打印总结"""
        print("\n" + "="*60)
        print("📋 用户体验改进总结")
        print("="*60 + "\n")
        
        improvements = [
            ("进度显示", "实时进度条、预计剩余时间、平滑更新"),
            ("消息格式化", "统一的消息样式、支持详细信息、时间格式化"),
            ("撤销/重做", "操作历史管理、可配置的撤销函数、统计信息"),
            ("交互式 CLI", "命令注册、别名支持、帮助系统、输入验证"),
        ]
        
        for title, features in improvements:
            print(f"✅ {title}")
            print(f"   特性: {features}\n")
        
        print("="*60)
        print("🎉 所有 UX 改进功能演示完成！")
        print("="*60 + "\n")


def main():
    """主函数"""
    suite = UXImprovementSuite()
    suite.run_full_demo()


if __name__ == "__main__":
    main()
