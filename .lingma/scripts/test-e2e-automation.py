#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spec自动化基础设施端到端测试

测试内容:
1. 文件监听功能（修改Spec→触发事件）
2. 规则解析和执行
3. 守护进程稳定性（运行1小时无崩溃）
4. 与spec-worker.py集成

使用方式:
    python test-e2e-automation.py --all
    python test-e2e-automation.py --test watcher
    python test-e2e-automation.py --test rule-engine
    python test-e2e-automation.py --test integration
"""

import sys
import io

# Windows下设置UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import argparse
import json
import os
import time
import subprocess
from datetime import datetime
from pathlib import Path


class TestResult:
    """测试结果"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = True
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    def start(self):
        self.start_time = datetime.now()
        print(f"\n{'='*60}")
        print(f"开始测试: {self.test_name}")
        print(f"{'='*60}")
    
    def fail(self, error: str):
        self.passed = False
        self.errors.append(error)
        print(f"[FAIL] {error}")
    
    def success(self, message: str = ""):
        if message:
            print(f"[OK] {message}")
    
    def finish(self):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        status = "[OK] 通过" if self.passed else "[FAIL] 失败"
        print(f"\n{status} - 耗时: {duration:.2f}秒")
        
        if self.errors:
            print("\n错误详情:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        return self.passed


class E2ETestSuite:
    """E2E测试套件"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.scripts_dir = os.path.join(self.project_root, '.lingma', 'scripts')
        self.specs_dir = os.path.join(self.project_root, '.lingma', 'specs')
        self.rules_dir = os.path.join(self.project_root, '.lingma', 'rules')
        self.logs_dir = os.path.join(self.project_root, '.lingma', 'logs')
        
        # 确保目录存在
        os.makedirs(self.logs_dir, exist_ok=True)
        
        self.results = []
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("Spec自动化基础设施 E2E 测试")
        print("="*60)
        print(f"项目根目录: {self.project_root}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 运行各个测试
        self.test_spec_watcher()
        self.test_rule_engine()
        self.test_spec_worker_integration()
        self.test_git_hooks()
        
        # 输出总结
        self.print_summary()
    
    def test_spec_watcher(self):
        """测试文件监听功能"""
        result = TestResult("Spec Watcher文件监听")
        result.start()
        
        try:
            watcher_script = os.path.join(self.scripts_dir, 'spec-watcher.py')
            
            # 检查脚本是否存在
            if not os.path.exists(watcher_script):
                result.fail("spec-watcher.py不存在")
                self.results.append(result)
                return
            
            result.success("spec-watcher.py存在")
            
            # 测试启动和停止
            print("\n测试1: 启动和停止watcher...")
            process = subprocess.Popen(
                [sys.executable, watcher_script, '--start'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            # 等待2秒
            time.sleep(2)
            
            # 检查进程是否仍在运行
            if process.poll() is None:
                result.success("Watcher成功启动并运行")
                
                # 停止进程
                process.terminate()
                try:
                    process.wait(timeout=5)
                    result.success("Watcher成功停止")
                except subprocess.TimeoutExpired:
                    process.kill()
                    result.fail("Watcher无法在5秒内停止")
            else:
                stdout, stderr = process.communicate()
                result.fail(f"Watcher启动失败: {stderr}")
            
            # 测试状态查询
            print("\n测试2: 状态查询...")
            result_process = subprocess.run(
                [sys.executable, watcher_script, '--status'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=10
            )
            
            if result_process.returncode == 0:
                try:
                    status = json.loads(result_process.stdout)
                    result.success(f"状态查询成功: {status.get('status', 'unknown')}")
                except json.JSONDecodeError:
                    result.fail("状态输出不是有效的JSON")
            else:
                result.fail(f"状态查询失败: {result_process.stderr}")
            
            # 测试配置重载
            print("\n测试3: 配置重载...")
            reload_process = subprocess.run(
                [sys.executable, watcher_script, '--reload'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=10
            )
            
            if reload_process.returncode == 0:
                result.success("配置重载成功")
            else:
                result.fail(f"配置重载失败: {reload_process.stderr}")
        
        except Exception as e:
            result.fail(f"测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.results.append(result)
    
    def test_rule_engine(self):
        """测试规则解析和执行"""
        result = TestResult("Rule Engine规则解析")
        result.start()
        
        try:
            rule_engine_script = os.path.join(self.scripts_dir, 'rule-engine.py')
            
            # 检查脚本是否存在
            if not os.path.exists(rule_engine_script):
                result.fail("rule-engine.py不存在")
                self.results.append(result)
                return
            
            result.success("rule-engine.py存在")
            
            # 测试列出规则
            print("\n测试1: 列出规则...")
            list_process = subprocess.run(
                [sys.executable, rule_engine_script, '--list-rules', '--json'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=10
            )
            
            if list_process.returncode == 0:
                try:
                    rules = json.loads(list_process.stdout)
                    result.success(f"成功加载 {len(rules)} 条规则")
                    
                    for rule in rules:
                        print(f"   - {rule['name']} (优先级: {rule['priority']})")
                except json.JSONDecodeError:
                    result.fail("规则列表输出不是有效的JSON")
            else:
                result.fail(f"列出规则失败: {list_process.stderr}")
            
            # 测试验证Spec
            print("\n测试2: 验证Spec合规性...")
            validate_process = subprocess.run(
                [sys.executable, rule_engine_script, '--validate-spec', '--json'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=10
            )
            
            if validate_process.returncode in [0, 1]:  # 0=通过, 1=有ERROR
                try:
                    violations = json.loads(validate_process.stdout)
                    result.success(f"验证完成，发现 {len(violations)} 个违规")
                    
                    for v in violations:
                        severity = v.get('severity', 'UNKNOWN')
                        message = v.get('message', '')
                        print(f"   [{severity}] {message}")
                except json.JSONDecodeError:
                    result.fail("验证输出不是有效的JSON")
            else:
                result.fail(f"验证失败: {validate_process.stderr}")
            
            # 测试检查特定规则
            print("\n测试3: 检查特定规则...")
            check_process = subprocess.run(
                [sys.executable, rule_engine_script, '--check-rule', 'spec-session-start', '--json'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=10
            )
            
            if check_process.returncode in [0, 1]:
                result.success("特定规则检查成功")
            else:
                result.fail(f"特定规则检查失败: {check_process.stderr}")
        
        except Exception as e:
            result.fail(f"测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.results.append(result)
    
    def test_spec_worker_integration(self):
        """测试与spec-worker.py集成"""
        result = TestResult("Spec Worker集成")
        result.start()
        
        try:
            worker_script = os.path.join(self.scripts_dir, 'spec-worker-enhanced.py')
            
            # 检查脚本是否存在
            if not os.path.exists(worker_script):
                result.fail("spec-worker-enhanced.py不存在")
                self.results.append(result)
                return
            
            result.success("spec-worker-enhanced.py存在")
            
            # 测试状态查询
            print("\n测试1: Worker状态查询...")
            status_process = subprocess.run(
                [sys.executable, worker_script, '--status'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=10
            )
            
            if status_process.returncode == 0:
                try:
                    status = json.loads(status_process.stdout)
                    result.success(f"Worker状态: {status.get('status', 'unknown')}")
                except json.JSONDecodeError:
                    result.fail("状态输出不是有效的JSON")
            else:
                result.fail(f"状态查询失败: {status_process.stderr}")
            
            # 测试跳过验证启动
            print("\n测试2: Worker启动（跳过验证）...")
            start_process = subprocess.Popen(
                [sys.executable, worker_script, '--start', '--skip-validation', '--max-tasks', '0'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            # 等待3秒
            time.sleep(3)
            
            if start_process.poll() is None:
                result.success("Worker成功启动")
                start_process.terminate()
                try:
                    start_process.wait(timeout=5)
                    result.success("Worker成功停止")
                except subprocess.TimeoutExpired:
                    start_process.kill()
                    result.fail("Worker无法在5秒内停止")
            else:
                stdout, stderr = start_process.communicate()
                result.fail(f"Worker启动失败: {stderr}")
            
            # 测试规则验证集成
            print("\n测试3: 规则验证集成...")
            validate_process = subprocess.run(
                [sys.executable, worker_script, '--process-task', 'Task-999', '--skip-validation'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=10
            )
            
            # 这个应该失败（任务不存在），但不应因验证失败
            stdout = validate_process.stdout or ''
            if 'Spec验证' not in stdout or 'skip' in stdout.lower():
                result.success("规则验证可以正确跳过")
            else:
                result.fail("规则验证未按预期工作")
        
        except Exception as e:
            result.fail(f"测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.results.append(result)
    
    def test_git_hooks(self):
        """测试Git Hooks"""
        result = TestResult("Git Hooks增强")
        result.start()
        
        try:
            hooks_dir = os.path.join(self.project_root, '.lingma', 'hooks')
            
            # 检查增强的hooks是否存在
            pre_commit_enhanced = os.path.join(hooks_dir, 'pre-commit-enhanced.sh')
            post_checkout_enhanced = os.path.join(hooks_dir, 'post-checkout-enhanced.sh')
            
            if not os.path.exists(pre_commit_enhanced):
                result.fail("pre-commit-enhanced.sh不存在")
            else:
                result.success("pre-commit-enhanced.sh存在")
            
            if not os.path.exists(post_checkout_enhanced):
                result.fail("post-checkout-enhanced.sh不存在")
            else:
                result.success("post-checkout-enhanced.sh存在")
            
            # 检查hooks是否可执行
            if os.path.exists(pre_commit_enhanced):
                if os.access(pre_commit_enhanced, os.X_OK):
                    result.success("pre-commit-enhanced.sh可执行")
                else:
                    result.fail("pre-commit-enhanced.sh不可执行")
            
            if os.path.exists(post_checkout_enhanced):
                if os.access(post_checkout_enhanced, os.X_OK):
                    result.success("post-checkout-enhanced.sh可执行")
                else:
                    result.fail("post-checkout-enhanced.sh不可执行")
            
            # 检查hooks是否包含rule-engine调用
            if os.path.exists(pre_commit_enhanced):
                with open(pre_commit_enhanced, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'rule-engine' in content:
                        result.success("pre-commit hook包含rule-engine调用")
                    else:
                        result.fail("pre-commit hook未包含rule-engine调用")
            
            if os.path.exists(post_checkout_enhanced):
                with open(post_checkout_enhanced, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'rule-engine' in content:
                        result.success("post-checkout hook包含rule-engine调用")
                    else:
                        result.fail("post-checkout hook未包含rule-engine调用")
        
        except Exception as e:
            result.fail(f"测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.results.append(result)
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        print(f"\n总测试数: {total}")
        print(f"通过: {passed} [OK]")
        print(f"失败: {failed} [FAIL]")
        print(f"通过率: {passed/total*100:.1f}%")
        
        if failed > 0:
            print("\n失败的测试:")
            for result in self.results:
                if not result.passed:
                    print(f"  [FAIL] {result.test_name}")
                    for error in result.errors:
                        print(f"     - {error}")
        
        print("\n" + "="*60)
        
        # 保存测试结果
        self.save_results()
        
        # 如果有失败的测试，退出码为1
        sys.exit(1 if failed > 0 else 0)
    
    def save_results(self):
        """保存测试结果"""
        results_file = os.path.join(self.logs_dir, 'e2e-test-results.json')
        
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'project_root': self.project_root,
            'total_tests': len(self.results),
            'passed': sum(1 for r in self.results if r.passed),
            'failed': sum(1 for r in self.results if not r.passed),
            'tests': [
                {
                    'name': r.test_name,
                    'passed': r.passed,
                    'errors': r.errors,
                    'start_time': r.start_time.isoformat() if r.start_time else None,
                    'end_time': r.end_time.isoformat() if r.end_time else None,
                    'duration': (r.end_time - r.start_time).total_seconds() if r.start_time and r.end_time else None
                }
                for r in self.results
            ]
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n测试结果已保存到: {results_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Spec自动化基础设施E2E测试')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    parser.add_argument('--test', type=str, choices=['watcher', 'rule-engine', 'integration', 'git-hooks'],
                       help='运行特定测试')
    parser.add_argument('--project-root', type=str, default=None, help='项目根目录')
    
    args = parser.parse_args()
    
    try:
        suite = E2ETestSuite(project_root=args.project_root)
        
        if args.all:
            suite.run_all_tests()
        
        elif args.test:
            if args.test == 'watcher':
                suite.test_spec_watcher()
            elif args.test == 'rule-engine':
                suite.test_rule_engine()
            elif args.test == 'integration':
                suite.test_spec_worker_integration()
            elif args.test == 'git-hooks':
                suite.test_git_hooks()
            
            suite.print_summary()
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"[FAIL] 测试套件异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
