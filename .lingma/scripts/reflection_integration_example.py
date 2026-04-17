#!/usr/bin/env python3
"""
Reflection Engine 集成示例

展示如何在 Agent 工作流中集成自我反思机制
"""

import sys
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from reflection_engine import create_reflection_engine, quick_reflect


def example_code_generation():
    """示例1: 代码生成后的质量反思"""
    print("="*60)
    print("示例1: 代码生成后的质量反思")
    print("="*60)
    
    # 模拟生成的代码
    generated_code = """
def calculate_sum(a, b):
    result = a + b
    return result
"""
    
    # 创建反思引擎
    engine = create_reflection_engine()
    
    # 执行反思
    reflection = engine.reflect_on_task(
        task_id="code-gen-001",
        result=generated_code,
        context={"type": "code", "language": "python"}
    )
    
    # 输出结果
    print(f"\n📊 质量评分: {reflection.quality_score.overall}/1.0")
    print(f"   - 正确性: {reflection.quality_score.correctness}")
    print(f"   - 完整性: {reflection.quality_score.completeness}")
    print(f"   - 可读性: {reflection.quality_score.readability}")
    print(f"   - 可维护性: {reflection.quality_score.maintainability}")
    
    print(f"\n🔍 发现问题: {len(reflection.issues)}")
    for issue in reflection.issues:
        print(f"   [{issue.severity.value.upper()}] {issue.description}")
    
    print(f"\n💡 改进建议: {len(reflection.suggestions)}")
    for sugg in reflection.suggestions:
        print(f"   {sugg.action}")
        print(f"      {sugg.description}")
        if sugg.example:
            print(f"      示例: {sugg.example[:50]}...")
    
    print(f"\n⏱️  反思耗时: {reflection.execution_time}s")
    
    return reflection


def example_documentation_review():
    """示例2: 文档质量审查"""
    print("\n" + "="*60)
    print("示例2: 文档质量审查")
    print("="*60)
    
    # 模拟生成的文档
    doc_content = """
# API 文档

## 接口说明

这个接口用于获取用户信息。

### 参数

- user_id: 用户ID

### 返回

用户信息对象
"""
    
    engine = create_reflection_engine()
    
    reflection = engine.reflect_on_task(
        task_id="doc-review-001",
        result=doc_content,
        context={"type": "documentation"}
    )
    
    print(f"\n📊 文档质量评分: {reflection.quality_score.overall}/1.0")
    print(f"   - 完整性: {reflection.quality_score.completeness}")
    print(f"   - 可读性: {reflection.quality_score.readability}")
    
    print(f"\n🔍 发现问题: {len(reflection.issues)}")
    for issue in reflection.issues:
        print(f"   [{issue.severity.value.upper()}] {issue.description}")
    
    print(f"\n💡 改进建议:")
    for sugg in reflection.suggestions:
        print(f"   • {sugg.action}")
    
    return reflection


def example_security_check():
    """示例3: 安全风险检测"""
    print("\n" + "="*60)
    print("示例3: 安全风险检测")
    print("="*60)
    
    # 包含安全风险的代码
    risky_code = """
def process_user_input(user_data):
    # 不安全：直接使用 eval
    result = eval(user_data)
    
    # 不安全：硬编码密码
    password = "secret123"
    
    return result
"""
    
    engine = create_reflection_engine()
    
    reflection = engine.reflect_on_task(
        task_id="security-check-001",
        result=risky_code,
        context={"type": "code", "check_security": True}
    )
    
    print(f"\n📊 安全评分: {reflection.quality_score.security}/1.0")
    
    print(f"\n🚨 发现安全问题: {len(reflection.issues)}")
    for issue in reflection.issues:
        if issue.issue_type.value == 'security_risk':
            print(f"   [{issue.severity.value.upper()}] {issue.description}")
            print(f"      证据: {issue.evidence}")
            print(f"      影响: {issue.impact}")
    
    print(f"\n💡 安全修复建议:")
    for sugg in reflection.suggestions:
        if '安全' in sugg.description or '风险' in sugg.description:
            print(f"   • {sugg.action}")
            print(f"      {sugg.description}")
            if sugg.example:
                print(f"      示例:\n{sugg.example}")
    
    return reflection


def example_performance_optimization():
    """示例4: 性能问题检测"""
    print("\n" + "="*60)
    print("示例4: 性能问题检测")
    print("="*60)
    
    # 包含性能问题的代码
    slow_code = """
def concatenate_strings(items):
    result = ''
    for item in items:
        result += str(item)
    return result
"""
    
    engine = create_reflection_engine()
    
    reflection = engine.reflect_on_task(
        task_id="perf-check-001",
        result=slow_code,
        context={"type": "code", "check_performance": True}
    )
    
    print(f"\n📊 性能评分: {reflection.quality_score.performance}/1.0")
    
    print(f"\n⚡ 发现性能问题: {len(reflection.issues)}")
    for issue in reflection.issues:
        if issue.issue_type.value == 'performance_issue':
            print(f"   [{issue.severity.value.upper()}] {issue.description}")
            print(f"      影响: {issue.impact}")
    
    print(f"\n💡 性能优化建议:")
    for sugg in reflection.suggestions:
        if '性能' in sugg.description or 'O(n' in sugg.expected_improvement:
            print(f"   • {sugg.action}")
            print(f"      {sugg.description}")
            if sugg.example:
                print(f"      优化前 vs 优化后:\n{sugg.example}")
    
    return reflection


def example_reflection_history():
    """示例5: 查看反思历史"""
    print("\n" + "="*60)
    print("示例5: 查看反思历史")
    print("="*60)
    
    engine = create_reflection_engine()
    
    # 获取摘要
    summary = engine.get_reflection_summary()
    
    print(f"\n📈 反思统计:")
    print(f"   总反思次数: {summary['total_reflections']}")
    print(f"   平均质量分: {summary['average_quality_score']}")
    print(f"   发现问题总数: {summary['total_issues_found']}")
    print(f"   生成建议总数: {summary['total_suggestions_generated']}")
    
    # 获取历史记录
    history = engine.recorder.get_history(limit=5)
    
    print(f"\n📋 最近5次反思:")
    for i, record in enumerate(history, 1):
        print(f"   {i}. 任务: {record['task_id']}")
        print(f"      时间: {record['timestamp'][:19]}")
        print(f"      质量: {record['quality_score']}")
        print(f"      问题: {record['issues_count']} | 建议: {record['suggestions_count']}")
    
    return summary


def main():
    """运行所有示例"""
    print("\n" + "🎯 Reflection Engine 集成示例".center(60))
    print("="*60)
    
    try:
        # 运行示例
        example_code_generation()
        example_documentation_review()
        example_security_check()
        example_performance_optimization()
        example_reflection_history()
        
        print("\n" + "="*60)
        print("✅ 所有示例运行完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
