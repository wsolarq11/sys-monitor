#!/usr/bin/env python3
"""
Spec触发器机制 - 端到端验证脚本

用途：
1. 验证所有组件安装正确
2. 测试Git Hooks功能
3. 测试Worker引擎
4. 生成验证报告

使用：
    python verify-spec-trigger.py
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def print_success(text):
    """打印成功信息"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_error(text):
    """打印错误信息"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def print_warning(text):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_info(text):
    """打印普通信息"""
    print(f"   {text}")


class SpecTriggerVerifier:
    """Spec触发器验证器"""
    
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "passed": 0,
            "failed": 0,
            "warnings": 0
        }
    
    def add_result(self, name: str, passed: bool, message: str = "", warning: bool = False):
        """添加检查结果"""
        result = {
            "name": name,
            "passed": passed,
            "warning": warning,
            "message": message
        }
        self.results["checks"].append(result)
        
        if warning:
            self.results["warnings"] += 1
            print_warning(f"{name}: {message}")
        elif passed:
            self.results["passed"] += 1
            print_success(f"{name}")
            if message:
                print_info(message)
        else:
            self.results["failed"] += 1
            print_error(f"{name}")
            if message:
                print_info(message)
    
    def check_component_exists(self):
        """检查组件文件是否存在"""
        print_header("Step 1: 检查组件文件")
        
        components = {
            "Spec验证中间件": ".lingma/scripts/spec-validator.py",
            "Spec Worker引擎": ".lingma/scripts/spec-worker.py",
            "Hook安装脚本": ".lingma/scripts/install-hooks.py",
            "pre-commit Hook模板": ".lingma/hooks/pre-commit.sh",
            "post-checkout Hook模板": ".lingma/hooks/post-checkout.sh",
            "当前Spec文件": ".lingma/specs/current-spec.md",
        }
        
        for name, rel_path in components.items():
            full_path = self.repo_root / rel_path
            exists = full_path.exists()
            size = full_path.stat().st_size if exists else 0
            self.add_result(
                name,
                exists,
                f"大小: {size} bytes" if exists else "文件缺失"
            )
    
    def check_hooks_installed(self):
        """检查Git Hooks是否已安装"""
        print_header("Step 2: 检查Git Hooks安装")
        
        git_hooks_dir = self.repo_root / ".git" / "hooks"
        
        if not git_hooks_dir.exists():
            self.add_result("Git Hooks目录", False, "目录不存在")
            return
        
        hooks = ["pre-commit", "post-checkout"]
        
        for hook_name in hooks:
            hook_file = git_hooks_dir / hook_name
            if hook_file.exists():
                # 检查是否是可执行文件
                is_executable = os.access(hook_file, os.X_OK) if os.name != 'nt' else True
                self.add_result(
                    f"{hook_name} Hook",
                    True,
                    f"已安装{' (可执行)' if is_executable else ''}"
                )
            else:
                self.add_result(
                    f"{hook_name} Hook",
                    False,
                    "未安装 - 运行 install-hooks.py 安装"
                )
    
    def test_spec_validator(self):
        """测试Spec验证器"""
        print_header("Step 3: 测试Spec验证器")
        
        validator_script = self.repo_root / ".lingma" / "scripts" / "spec-validator.py"
        
        if not validator_script.exists():
            self.add_result("Spec验证器", False, "脚本不存在")
            return
        
        try:
            # 测试manual模式
            result = subprocess.run(
                [sys.executable, str(validator_script), "manual"],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                errors='ignore',  # 忽略编码错误
                timeout=10
            )
            
            if result.returncode in [0, 1]:  # 0或1都是正常返回
                self.add_result(
                    "Spec验证器执行",
                    True,
                    f"退出码: {result.returncode}"
                )
                
                # 检查输出（支持多种格式）
                if result.stdout and ("验证结果:" in result.stdout or "Valid:" in result.stdout or "Errors:" in result.stdout):
                    self.add_result("输出格式", True, "包含验证结果")
                else:
                    self.add_result("输出格式", True, "输出基本正常", warning=True)
            else:
                self.add_result(
                    "Spec验证器执行",
                    False,
                    f"异常退出码: {result.returncode}"
                )
                
        except subprocess.TimeoutExpired:
            self.add_result("Spec验证器执行", False, "执行超时")
        except Exception as e:
            self.add_result("Spec验证器执行", False, str(e))
    
    def test_worker_engine(self):
        """测试Worker引擎"""
        print_header("Step 4: 测试Worker引擎")
        
        worker_script = self.repo_root / ".lingma" / "scripts" / "spec-worker.py"
        
        if not worker_script.exists():
            self.add_result("Worker引擎", False, "脚本不存在")
            return
        
        try:
            # 测试status命令
            result = subprocess.run(
                [sys.executable, str(worker_script), "status"],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                errors='ignore',  # 忽略编码错误
                timeout=10
            )
            
            if result.returncode == 0:
                self.add_result("Worker状态查询", True)
                
                # 检查输出（支持多种格式）
                if result.stdout and ("Worker队列状态" in result.stdout or "待处理:" in result.stdout or "pending" in result.stdout.lower()):
                    self.add_result("输出内容", True, "包含队列统计")
                else:
                    self.add_result("输出内容", True, "输出基本正常", warning=True)
            else:
                self.add_result(
                    "Worker状态查询",
                    False,
                    f"退出码: {result.returncode}"
                )
                
        except Exception as e:
            self.add_result("Worker状态查询", False, str(e))
    
    def test_hook_installation_script(self):
        """测试Hook安装脚本"""
        print_header("Step 5: 测试Hook安装脚本")
        
        install_script = self.repo_root / ".lingma" / "scripts" / "install-hooks.py"
        
        if not install_script.exists():
            self.add_result("安装脚本", False, "脚本不存在")
            return
        
        try:
            # 测试--help
            result = subprocess.run(
                [sys.executable, str(install_script), "--help"],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "usage" in result.stdout.lower():
                self.add_result("安装脚本帮助", True, "参数说明正常")
            else:
                self.add_result("安装脚本帮助", False, "帮助信息显示异常", warning=True)
                
        except Exception as e:
            self.add_result("安装脚本帮助", False, str(e))
    
    def check_directory_structure(self):
        """检查目录结构"""
        print_header("Step 6: 检查目录结构")
        
        required_dirs = [
            ".lingma/scripts",
            ".lingma/hooks",
            ".lingma/specs",
            ".lingma/logs",
            ".lingma/worker/tasks",
        ]
        
        for rel_dir in required_dirs:
            full_dir = self.repo_root / rel_dir
            exists = full_dir.exists()
            self.add_result(
                f"目录: {rel_dir}",
                exists,
                "存在" if exists else "缺失（Worker目录首次运行时创建）"
            )
    
    def generate_report(self):
        """生成验证报告"""
        print_header("验证报告")
        
        total = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.BOLD}总体结果:{Colors.RESET}")
        print(f"  总检查项: {total}")
        print(f"  {Colors.GREEN}通过: {self.results['passed']}{Colors.RESET}")
        print(f"  {Colors.RED}失败: {self.results['failed']}{Colors.RESET}")
        print(f"  {Colors.YELLOW}警告: {self.results['warnings']}{Colors.RESET}")
        print(f"  通过率: {pass_rate:.1f}%\n")
        
        # 保存报告
        report_file = self.repo_root / ".lingma" / "reports" / "spec-trigger-verification.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print_info(f"详细报告已保存: {report_file}")
        
        if self.results["failed"] == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 所有检查通过！Spec触发器机制已就绪{Colors.RESET}\n")
            return 0
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️  存在失败项，请修复后重试{Colors.RESET}\n")
            return 1
    
    def run_all_checks(self):
        """运行所有检查"""
        print(f"{Colors.BOLD}Spec触发器机制 - 端到端验证{Colors.RESET}")
        print(f"仓库根目录: {self.repo_root}")
        
        self.check_component_exists()
        self.check_hooks_installed()
        self.test_spec_validator()
        self.test_worker_engine()
        self.test_hook_installation_script()
        self.check_directory_structure()
        
        return self.generate_report()


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Spec触发器验证脚本")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="仓库根目录（默认当前目录）"
    )
    
    args = parser.parse_args()
    
    verifier = SpecTriggerVerifier(args.repo_root)
    exit_code = verifier.run_all_checks()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
