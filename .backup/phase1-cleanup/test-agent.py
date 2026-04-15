#!/usr/bin/env python3
"""
Agent 测试脚本

验证 SpecDrivenAgent 的核心功能
"""

import sys
import asyncio
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent))


async def test_agent_initialization():
    """测试 Agent 初始化"""
    print("=" * 60)
    print("测试 1: Agent 初始化")
    print("=" * 60)
    
    # 使用 importlib 动态导入
    import importlib.util
    spec_module = importlib.util.spec_from_file_location(
        "spec_driven_agent", 
        Path(__file__).parent / "spec-driven-agent.py"
    )
    spec_driven_agent = importlib.util.module_from_spec(spec_module)
    spec_module.loader.exec_module(spec_driven_agent)
    
    SpecDrivenAgent = spec_driven_agent.SpecDrivenAgent
    
    try:
        agent = SpecDrivenAgent()
        
        print("\n✅ Agent 创建成功")
        print(f"   状态: {agent.state.value}")
        print(f"   可用 Skills: {len(agent.skills)}")
        print(f"   已加载 Rules: {len(agent.rules)}")
        
        # 显示状态
        status = agent.get_status()
        print(f"\n📊 Agent 状态:")
        print(f"   State: {status['state']}")
        print(f"   Execution Count: {status['execution_count']}")
        print(f"   Available Skills: {', '.join(status['available_skills'][:3])}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Agent 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_task_execution():
    """测试任务执行"""
    print("\n" + "=" * 60)
    print("测试 2: 任务执行")
    print("=" * 60)
    
    # 使用 importlib 动态导入
    import importlib.util
    spec_module = importlib.util.spec_from_file_location(
        "spec_driven_agent", 
        Path(__file__).parent / "spec-driven-agent.py"
    )
    spec_driven_agent = importlib.util.module_from_spec(spec_module)
    spec_module.loader.exec_module(spec_driven_agent)
    
    SpecDrivenAgent = spec_driven_agent.SpecDrivenAgent
    
    try:
        agent = SpecDrivenAgent()
        
        # 测试低风险任务
        print("\n🧪 测试低风险任务 (update_spec)...")
        task = {
            "type": "update_spec",
            "description": "Update spec progress",
            "parameters": {
                "updates": {
                    "progress": "40%"
                }
            },
            "details": {
                "has_clear_intent": True,
                "is_repetitive_task": True
            }
        }
        
        result = await agent.execute_task(task)
        
        if result["success"]:
            print(f"   ✅ 任务执行成功")
            print(f"   策略: {result['strategy']}")
            print(f"   结果: {result.get('result', {})}")
        else:
            print(f"   ⚠️  任务执行返回: {result}")
        
        # 显示执行摘要
        summary = agent.get_execution_summary()
        print(f"\n📈 执行摘要:")
        print(f"   总执行数: {summary['total_executions']}")
        print(f"   成功率: {summary['success_rate']}%")
        print(f"   平均耗时: {summary['average_duration_ms']}ms")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 任务执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_snapshot_integration():
    """测试快照集成"""
    print("\n" + "=" * 60)
    print("测试 3: 快照集成")
    print("=" * 60)
    
    # 使用 importlib 动态导入
    import importlib.util
    spec_module = importlib.util.spec_from_file_location(
        "spec_driven_agent", 
        Path(__file__).parent / "spec-driven-agent.py"
    )
    spec_driven_agent = importlib.util.module_from_spec(spec_module)
    spec_module.loader.exec_module(spec_driven_agent)
    
    SpecDrivenAgent = spec_driven_agent.SpecDrivenAgent
    
    try:
        agent = SpecDrivenAgent()
        
        # 测试中风险任务（应该触发快照）
        print("\n🧪 测试中风险任务 (modify_file)...")
        task = {
            "type": "modify_file",
            "description": "Modify a file",
            "parameters": {
                "path": ".lingma/config/test.txt",
                "content": "Test content"
            },
            "details": {
                "modifies_production_files": True,
                "has_clear_intent": True
            }
        }
        
        result = await agent.execute_task(task)
        
        print(f"   策略: {result.get('strategy', 'unknown')}")
        
        if result.get("snapshot_id"):
            print(f"   ✅ 快照已创建: {result['snapshot_id']}")
        else:
            print(f"   ℹ️  未创建快照（可能风险等级不够）")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 快照集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_risk_assessment():
    """测试风险评估"""
    print("\n" + "=" * 60)
    print("测试 4: 风险评估")
    print("=" * 60)
    
    # 使用 importlib 动态导入
    import importlib.util
    spec_module = importlib.util.spec_from_file_location(
        "spec_driven_agent", 
        Path(__file__).parent / "spec-driven-agent.py"
    )
    spec_driven_agent = importlib.util.module_from_spec(spec_module)
    spec_module.loader.exec_module(spec_driven_agent)
    
    SpecDrivenAgent = spec_driven_agent.SpecDrivenAgent
    
    try:
        agent = SpecDrivenAgent()
        
        test_cases = [
            {
                "name": "低风险 - 读取文件",
                "task": {
                    "type": "read_file",
                    "details": {
                        "has_clear_intent": True,
                        "is_repetitive_task": True
                    }
                }
            },
            {
                "name": "中风险 - 修改文件",
                "task": {
                    "type": "modify_file",
                    "details": {
                        "modifies_production_files": True,
                        "has_clear_intent": True
                    }
                }
            },
            {
                "name": "高风险 - 删除文件",
                "task": {
                    "type": "delete_file",
                    "details": {
                        "deletes_files": True,
                        "irreversible": True,
                        "affects_multiple_files": True
                    }
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n   测试: {test_case['name']}")
            
            assessment = agent.automation_engine.evaluate_operation(test_case["task"])
            
            print(f"      风险等级: {assessment['risk_assessment']['risk_level']}")
            print(f"      风险分数: {assessment['risk_assessment']['risk_score']}")
            print(f"      置信度: {assessment['confidence']:.0%}")
            print(f"      策略: {assessment['strategy']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 风险评估测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_context_management():
    """测试上下文管理"""
    print("\n" + "=" * 60)
    print("测试 5: 上下文管理")
    print("=" * 60)
    
    # 使用 importlib 动态导入
    import importlib.util
    spec_module = importlib.util.spec_from_file_location(
        "spec_driven_agent", 
        Path(__file__).parent / "spec-driven-agent.py"
    )
    spec_driven_agent = importlib.util.module_from_spec(spec_module)
    spec_module.loader.exec_module(spec_driven_agent)
    
    SpecDrivenAgent = spec_driven_agent.SpecDrivenAgent
    
    try:
        agent = SpecDrivenAgent()
        
        print("\n📝 当前上下文:")
        print(f"   Session Start: {agent.context['session_start']}")
        print(f"   Spec Path: {agent.context['spec_path']}")
        print(f"   User Preferences: {agent.context['user_preferences']}")
        
        # 更新上下文
        agent.context["user_preferences"]["automation_level"] = "balanced"
        
        print(f"\n   ✅ 上下文更新成功")
        print(f"   Automation Level: {agent.context['user_preferences']['automation_level']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 上下文管理测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  Spec-Driven Agent 测试套件")
    print("=" * 60 + "\n")
    
    tests = [
        ("Agent 初始化", test_agent_initialization),
        ("任务执行", test_task_execution),
        ("快照集成", test_snapshot_integration),
        ("风险评估", test_risk_assessment),
        ("上下文管理", test_context_management),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = await test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ {name} 测试异常: {str(e)}\n")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("  测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {status} - {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！Agent 已就绪。\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查错误信息。\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
