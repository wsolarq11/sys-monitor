#!/usr/bin/env python3
"""
自动化系统验证脚本

测试自动化引擎、日志系统和快照管理器是否正常工作
"""

import sys
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def test_automation_engine():
    """测试自动化引擎"""
    print("=" * 60)
    print("测试 1: 自动化引擎")
    print("=" * 60)
    
    # 使用 importlib 动态导入
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "automation_engine", 
        Path(__file__).parent / "automation-engine.py"
    )
    automation_engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(automation_engine)
    
    AutomationEngine = automation_engine.AutomationEngine
    
    engine = AutomationEngine()
    
    # 测试低风险操作
    print("\n📋 测试低风险操作 (read_file)...")
    result = engine.evaluate_operation({
        "type": "read_file",
        "details": {
            "has_clear_intent": True,
            "is_repetitive_task": True
        }
    })
    print(f"  策略: {result['strategy']}")
    print(f"  风险: {result['risk_assessment']['risk_level']}")
    print(f"  置信度: {result['confidence']:.0%}")
    print(f"  建议: {result['recommendation']}")
    
    # 测试中风险操作
    print("\n📋 测试中风险操作 (modify_file)...")
    result = engine.evaluate_operation({
        "type": "modify_file",
        "details": {
            "modifies_production_files": True,
            "has_clear_intent": True
        }
    })
    print(f"  策略: {result['strategy']}")
    print(f"  风险: {result['risk_assessment']['risk_level']}")
    print(f"  置信度: {result['confidence']:.0%}")
    print(f"  建议: {result['recommendation']}")
    
    # 测试高风险操作
    print("\n📋 测试高风险操作 (delete_file)...")
    result = engine.evaluate_operation({
        "type": "delete_file",
        "details": {
            "deletes_files": True,
            "irreversible": True,
            "affects_multiple_files": True
        }
    })
    print(f"  策略: {result['strategy']}")
    print(f"  风险: {result['risk_assessment']['risk_level']}")
    print(f"  置信度: {result['confidence']:.0%}")
    print(f"  建议: {result['recommendation']}")
    
    # 显示统计
    stats = engine.get_statistics()
    print(f"\n📊 决策统计:")
    print(f"  总决策数: {stats['total_decisions']}")
    print(f"  平均评估时间: {stats.get('average_evaluation_time_ms', 0):.2f}ms")
    
    print("\n✅ 自动化引擎测试通过\n")
    return True


def test_operation_logger():
    """测试操作日志系统"""
    print("=" * 60)
    print("测试 2: 操作日志系统")
    print("=" * 60)
    
    # 使用 importlib 动态导入
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "operation_logger", 
        Path(__file__).parent / "operation-logger.py"
    )
    operation_logger = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(operation_logger)
    
    OperationLogger = operation_logger.OperationLogger
    
    logger = OperationLogger()
    
    # 记录一些测试操作
    print("\n📝 记录测试操作...")
    
    test_operations = [
        {
            "type": "create_file",
            "details": {"file": "test1.txt"}
        },
        {
            "type": "modify_file",
            "details": {"file": "test2.txt"}
        },
        {
            "type": "run_tests",
            "details": {"test_suite": "unit_tests"}
        }
    ]
    
    for i, op in enumerate(test_operations, 1):
        log_id = logger.log_operation(op, {
            "status": "success",
            "duration_ms": 100 + i * 50
        })
        print(f"  ✓ 操作 {i} 已记录 (ID: {log_id})")
    
    # 查询最近操作
    print("\n🔍 查询最近操作...")
    recent = logger.query_operations(limit=3)
    print(f"  找到 {len(recent)} 条记录")
    
    # 显示统计
    print("\n📊 操作统计:")
    report = logger.generate_report(days=7)
    print(report)
    
    print("✅ 操作日志系统测试通过\n")
    return True


def test_snapshot_manager():
    """测试快照管理器"""
    print("=" * 60)
    print("测试 3: 快照管理器")
    print("=" * 60)
    
    # 使用 importlib 动态导入
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "snapshot_manager", 
        Path(__file__).parent / "snapshot-manager.py"
    )
    snapshot_manager = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(snapshot_manager)
    
    SnapshotManager = snapshot_manager.SnapshotManager
    
    manager = SnapshotManager()
    
    # 创建测试快照
    print("\n📸 创建测试快照...")
    result = manager.create_snapshot(
        description="Test snapshot for verification",
        include_git=False  # 避免 Git 依赖
    )
    
    if result["success"]:
        print(f"  ✓ 快照创建成功: {result['snapshot_id']}")
        print(f"  大小: {result['info']['size_bytes']} bytes")
    else:
        print(f"  ✗ 快照创建失败: {result.get('error')}")
        return False
    
    # 列出快照
    print("\n📋 列出快照...")
    snapshots = manager.list_snapshots(limit=5)
    print(f"  找到 {len(snapshots)} 个快照")
    for snap in snapshots:
        print(f"    - {snap['id']}: {snap['description']}")
    
    # 显示统计
    print("\n📊 快照统计:")
    stats = manager.get_statistics()
    print(f"  总快照数: {stats['total_snapshots']}")
    print(f"  总大小: {stats.get('total_size_mb', 0):.2f} MB")
    
    print("\n✅ 快照管理器测试通过\n")
    return True


def test_config():
    """测试配置文件"""
    print("=" * 60)
    print("测试 4: 配置文件")
    print("=" * 60)
    
    import json
    
    config_path = Path(".lingma/config/automation.json")
    
    if not config_path.exists():
        print("  ✗ 配置文件不存在")
        return False
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("\n⚙️  配置内容:")
    print(f"  自动化级别: {config.get('automation_level')}")
    print(f"  启用状态: {config.get('enabled')}")
    print(f"  风险阈值:")
    thresholds = config.get('risk_thresholds', {})
    print(f"    - 自动执行: {thresholds.get('auto_execute')}")
    print(f"    - 创建快照: {thresholds.get('execute_with_snapshot')}")
    print(f"    - 询问用户: {thresholds.get('ask_user')}")
    
    print("\n✅ 配置文件测试通过\n")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  全自动化系统验证")
    print("=" * 60 + "\n")
    
    tests = [
        ("自动化引擎", test_automation_engine),
        ("操作日志系统", test_operation_logger),
        ("快照管理器", test_snapshot_manager),
        ("配置文件", test_config),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ {name} 测试失败: {str(e)}\n")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 总结
    print("=" * 60)
    print("  测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {status} - {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！自动化系统已就绪。\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查错误信息。\n")
        return 1


if __name__ == "__main__":
    exit(main())
