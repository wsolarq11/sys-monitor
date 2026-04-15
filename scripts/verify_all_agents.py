#!/usr/bin/env python3
"""
多Agent系统 - 最终验证脚本

验证所有5个Agent脚本和增强的agent_client.py是否正常工作
"""

import subprocess
import sys
from pathlib import Path
import json

def run_test(script_path: str, test_name: str) -> bool:
    """运行单个Agent的测试"""
    print(f"\n{'='*60}")
    print(f"🧪 测试: {test_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path, "--test"],
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8'
        )
        
        # 检查输出
        if "✅ 所有测试通过！" in result.stdout:
            print(f"✅ {test_name} - 通过")
            return True
        else:
            print(f"❌ {test_name} - 失败")
            if result.stderr:
                print(f"错误输出:\n{result.stderr[:500]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  {test_name} - 超时")
        return False
    except Exception as e:
        print(f"❌ {test_name} - 异常: {str(e)}")
        return False


def verify_json_rpc(script_path: str, agent_name: str) -> bool:
    """验证JSON-RPC接口"""
    print(f"\n🔌 验证 {agent_name} 的 JSON-RPC 接口...")
    
    test_input = {
        "method": "process_request",
        "params": {"test": True},
        "id": "test-123"
    }
    
    try:
        result = subprocess.run(
            [sys.executable, script_path, "--json-rpc"],
            input=json.dumps(test_input),
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            output = json.loads(result.stdout)
            if output.get("jsonrpc") == "2.0" and "id" in output:
                print(f"   ✓ JSON-RPC响应正常")
                return True
        
        print(f"   ✗ JSON-RPC响应异常")
        return False
        
    except Exception as e:
        print(f"   ✗ 错误: {str(e)}")
        return False


def main():
    """主验证流程"""
    print("\n" + "="*80)
    print("🚀 多Agent编排系统 - 最终验证")
    print("="*80)
    
    repo_root = Path.cwd()
    scripts_dir = repo_root / ".lingma" / "scripts"
    worker_dir = repo_root / ".lingma" / "worker"
    
    # 定义要测试的Agent
    agents = [
        {
            "name": "Spec-Driven Agent",
            "script": scripts_dir / "spec-driven-agent.py",
            "test_func": run_test
        },
        {
            "name": "Test Runner Agent",
            "script": scripts_dir / "test-runner.py",
            "test_func": run_test
        },
        {
            "name": "Code Reviewer Agent",
            "script": scripts_dir / "code-reviewer.py",
            "test_func": run_test
        },
        {
            "name": "Doc Generator Agent",
            "script": scripts_dir / "doc-generator.py",
            "test_func": run_test
        },
        {
            "name": "Supervisor Agent",
            "script": scripts_dir / "supervisor-agent.py",
            "test_func": run_test
        },
        {
            "name": "Agent Client",
            "script": worker_dir / "agent_client.py",
            "test_func": run_test
        }
    ]
    
    results = []
    
    # 运行所有测试
    for agent in agents:
        if agent["script"].exists():
            passed = agent["test_func"](str(agent["script"]), agent["name"])
            results.append({
                "agent": agent["name"],
                "passed": passed,
                "script_exists": True
            })
        else:
            print(f"\n❌ {agent['name']} - 脚本不存在: {agent['script']}")
            results.append({
                "agent": agent["name"],
                "passed": False,
                "script_exists": False
            })
    
    # 验证JSON-RPC接口（抽样）
    print(f"\n{'='*60}")
    print("🔌 验证 JSON-RPC 接口")
    print(f"{'='*60}")
    
    json_rpc_agents = [
        ("spec-driven-agent.py", "Spec-Driven Agent"),
        ("test-runner.py", "Test Runner"),
        ("code-reviewer.py", "Code Reviewer")
    ]
    
    for script_name, agent_name in json_rpc_agents:
        script_path = scripts_dir / script_name
        if script_path.exists():
            verify_json_rpc(str(script_path), agent_name)
    
    # 打印总结
    print(f"\n{'='*80}")
    print("📊 验证总结")
    print(f"{'='*80}")
    
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    
    print(f"\n总Agent数: {total}")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print()
    
    for result in results:
        status = "✅" if result["passed"] else "❌"
        exists = "✓" if result["script_exists"] else "✗"
        print(f"{status} {result['agent']:30s} [脚本存在: {exists}]")
    
    print()
    
    if failed == 0:
        print("🎉 所有Agent验证通过！系统已准备就绪。")
        print()
        print("📖 详细文档:")
        print(f"   - 实施报告: .lingma/docs/AGENT_IMPLEMENTATION_REPORT.md")
        print(f"   - 使用指南: 参见实施报告的'使用指南'章节")
        return 0
    else:
        print(f"⚠️  {failed} 个Agent验证失败，请检查上述错误。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
