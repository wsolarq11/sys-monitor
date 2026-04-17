#!/usr/bin/env python3
"""
交互式命令行界面 - 提供友好的用户交互体验

职责：
1. 提供清晰的命令提示
2. 支持命令自动补全
3. 显示帮助信息
4. 处理用户输入验证
"""

import sys
import os
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any


class InteractiveCLI:
    """交互式命令行界面"""
    
    def __init__(self, prompt: str = "> "):
        """
        初始化 CLI
        
        Args:
            prompt: 命令提示符
        """
        self.prompt = prompt
        self.commands: Dict[str, Dict[str, Any]] = {}
        self.running = False
    
    def register_command(self, name: str, func: Callable, 
                        description: str, aliases: List[str] = None):
        """
        注册命令
        
        Args:
            name: 命令名称
            func: 命令执行函数
            description: 命令描述
            aliases: 命令别名
        """
        self.commands[name] = {
            'func': func,
            'description': description,
            'aliases': aliases or []
        }
        
        # 注册别名
        if aliases:
            for alias in aliases:
                self.commands[alias] = {
                    'func': func,
                    'description': f"别名: {name}",
                    'aliases': []
                }
    
    def show_help(self):
        """显示帮助信息"""
        print("\n📖 可用命令:")
        print("=" * 60)
        
        # 按名称排序
        sorted_commands = sorted(self.commands.items(), key=lambda x: x[0])
        
        for name, info in sorted_commands:
            # 跳过别名（避免重复显示）
            if info['description'].startswith("别名:"):
                continue
            
            aliases_str = ""
            if info['aliases']:
                aliases_str = f" (别名: {', '.join(info['aliases'])})"
            
            print(f"  {name:<20} - {info['description']}{aliases_str}")
        
        print("=" * 60)
        print("输入 'quit' 或 'exit' 退出\n")
    
    def execute_command(self, command_line: str) -> bool:
        """
        执行命令
        
        Args:
            command_line: 命令行输入
            
        Returns:
            是否继续运行
        """
        if not command_line.strip():
            return True
        
        parts = command_line.strip().split()
        command_name = parts[0].lower()
        args = parts[1:]
        
        # 检查退出命令
        if command_name in ['quit', 'exit', 'q']:
            return False
        
        # 检查帮助命令
        if command_name in ['help', 'h', '?']:
            self.show_help()
            return True
        
        # 查找命令
        if command_name not in self.commands:
            print(f"❌ 未知命令: {command_name}")
            print("输入 'help' 查看可用命令\n")
            return True
        
        # 执行命令
        try:
            command_info = self.commands[command_name]
            result = command_info['func'](*args)
            if result is not None:
                print(result)
        except Exception as e:
            print(f"❌ 执行命令时出错: {e}")
            import traceback
            traceback.print_exc()
        
        return True
    
    def run(self):
        """运行交互式 CLI"""
        self.running = True
        
        print("🚀 交互式命令行界面已启动")
        print("输入 'help' 查看可用命令\n")
        
        while self.running:
            try:
                # 获取用户输入
                command_line = input(self.prompt)
                
                # 执行命令
                self.running = self.execute_command(command_line)
                
            except KeyboardInterrupt:
                print("\n\n⚠️  检测到中断信号")
                confirm = input("确定要退出吗? (y/n): ")
                if confirm.lower() == 'y':
                    break
            except EOFError:
                print("\n")
                break
        
        print("\n👋 再见！\n")


# 示例命令函数
def cmd_status(*args):
    """显示系统状态"""
    return "✅ 系统运行正常"

def cmd_version(*args):
    """显示版本信息"""
    return "版本: 1.0.0"

def cmd_clear(*args):
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')
    return None

def cmd_echo(*args):
    """回显参数"""
    return " ".join(args) if args else "未提供参数"


if __name__ == "__main__":
    # 创建 CLI 实例
    cli = InteractiveCLI(prompt="spec-driven> ")
    
    # 注册命令
    cli.register_command('status', cmd_status, '显示系统状态', ['st'])
    cli.register_command('version', cmd_version, '显示版本信息', ['ver', 'v'])
    cli.register_command('clear', cmd_clear, '清屏', ['cls'])
    cli.register_command('echo', cmd_echo, '回显参数')
    
    # 运行 CLI
    cli.run()
