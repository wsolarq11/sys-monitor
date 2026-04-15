#!/usr/bin/env python3
"""
Spec Status Checker
检查当前 spec 的状态和进度
"""

import re
import sys
from pathlib import Path
from datetime import datetime


def format_progress(completed: int, total: int) -> str:
    """格式化进度显示"""
    if total == 0:
        return "0.0%"
    percentage = (completed / total) * 100
    bar_length = 20
    filled = int(bar_length * completed / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    return f"{bar} {percentage:.1f}% ({completed}/{total})"


def extract_metadata(content: str) -> dict:
    """提取 spec 元数据"""
    metadata = {}
    
    # 状态
    status_match = re.search(r'\*\*状态\*\*:\s*(\w+)', content)
    if status_match:
        metadata['status'] = status_match.group(1)
    
    # 优先级
    priority_match = re.search(r'\*\*优先级\*\*:\s*(P\d+)', content)
    if priority_match:
        metadata['priority'] = priority_match.group(1)
    
    # 负责人
    owner_match = re.search(r'\*\*负责人\*\*:\s*(.+?)(?:\n|$)', content)
    if owner_match:
        metadata['owner'] = owner_match.group(1).strip()
    
    return metadata


def analyze_tasks(content: str) -> dict:
    """分析任务完成情况"""
    tasks = {
        'total': 0,
        'completed': 0,
        'pending': [],
        'in_progress': []
    }
    
    # 匹配所有任务项
    task_pattern = r'- \[([ xX])\]\s+(Task-\d+:.+?)(?=\n-|\n\n|$)'
    matches = re.finditer(task_pattern, content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        status = match.group(1)
        task_desc = match.group(2).strip()
        tasks['total'] += 1
        
        if status.lower() == 'x':
            tasks['completed'] += 1
        else:
            tasks['pending'].append(task_desc)
    
    return tasks


def get_acceptance_criteria_status(content: str) -> dict:
    """获取验收标准状态"""
    ac_stats = {
        'total': 0,
        'completed': 0,
        'pending': []
    }
    
    # 匹配验收标准
    ac_pattern = r'- \[([ xX])\]\s+(AC-\d+:.+?)(?=\n-|\n\n|$)'
    matches = re.finditer(ac_pattern, content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        status = match.group(1)
        ac_desc = match.group(2).strip()
        ac_stats['total'] += 1
        
        if status.lower() == 'x':
            ac_stats['completed'] += 1
        else:
            ac_stats['pending'].append(ac_desc)
    
    return ac_stats


def get_recent_notes(content: str, count: int = 3) -> list:
    """获取最近的实施笔记"""
    notes = []
    note_pattern = r'### 实施笔记 - (.+?)\n\n(.*?)(?=\n### 实施笔记|\Z)'
    matches = re.findall(note_pattern, content, re.DOTALL)
    
    # 返回最近的 count 条笔记
    for date, note_content in matches[-count:]:
        notes.append({
            'date': date.strip(),
            'content': note_content.strip()
        })
    
    return notes


def check_spec_status(spec_path: str = ".lingma/specs/current-spec.md"):
    """检查 spec 状态并输出报告"""
    spec_file = Path(spec_path)
    
    if not spec_file.exists():
        print("❌ 未找到活跃的 spec 文件")
        print(f"\n路径: {spec_file.absolute()}")
        print("\n💡 提示: 开始新功能时，AI 会自动创建 spec")
        return False
    
    try:
        content = spec_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ 读取 spec 文件失败: {e}")
        return False
    
    # 提取信息
    metadata = extract_metadata(content)
    tasks = analyze_tasks(content)
    ac_stats = get_acceptance_criteria_status(content)
    recent_notes = get_recent_notes(content)
    
    # 获取 spec 名称（从第一行标题）
    title_match = re.match(r'# (.+)', content)
    spec_name = title_match.group(1) if title_match else "Unknown Spec"
    
    # 输出报告
    print("=" * 70)
    print(f"📋 Spec 状态报告")
    print("=" * 70)
    print(f"\n📝 名称: {spec_name}")
    
    if 'status' in metadata:
        status_emoji = {
            'draft': '📝',
            'approved': '✅',
            'in-progress': '⏳',
            'completed': '✨',
            'cancelled': '❌'
        }.get(metadata['status'], '❓')
        print(f"{status_emoji} 状态: {metadata['status']}")
    
    if 'priority' in metadata:
        print(f"🎯 优先级: {metadata['priority']}")
    
    if 'owner' in metadata:
        print(f"👤 负责人: {metadata['owner']}")
    
    print(f"\n{'─' * 70}")
    print(f"📊 任务进度")
    print(f"{'─' * 70}")
    print(format_progress(tasks['completed'], tasks['total']))
    
    if tasks['pending']:
        print(f"\n⏳ 待完成任务:")
        for i, task in enumerate(tasks['pending'][:5], 1):  # 只显示前5个
            print(f"  {i}. {task}")
        if len(tasks['pending']) > 5:
            print(f"  ... 还有 {len(tasks['pending']) - 5} 个任务")
    
    if ac_stats['total'] > 0:
        print(f"\n{'─' * 70}")
        print(f"✓ 验收标准")
        print(f"{'─' * 70}")
        print(format_progress(ac_stats['completed'], ac_stats['total']))
        
        if ac_stats['pending']:
            print(f"\n⚠️  未完成的验收标准:")
            for ac in ac_stats['pending'][:3]:  # 只显示前3个
                print(f"  • {ac}")
    
    if recent_notes:
        print(f"\n{'─' * 70}")
        print(f"📝 最近实施笔记")
        print(f"{'─' * 70}")
        for note in recent_notes:
            print(f"\n🕒 {note['date']}")
            # 显示笔记的第一行
            first_line = note['content'].split('\n')[0]
            print(f"   {first_line}")
    
    # 下一步建议
    print(f"\n{'─' * 70}")
    print(f"💡 下一步建议")
    print(f"{'─' * 70}")
    
    status = metadata.get('status', 'unknown')
    if status == 'draft':
        print("  → 审查 spec 并标记为 approved")
    elif status == 'approved':
        print("  → 开始执行第一个任务")
    elif status == 'in-progress':
        if tasks['pending']:
            print(f"  → 继续执行: {tasks['pending'][0]}")
        else:
            print("  → 所有任务已完成，准备验收")
    elif status == 'completed':
        print("  → Spec 已完成，可以归档")
        print(f"  → 运行: mv {spec_path} .lingma/specs/spec-history/")
    
    print("\n" + "=" * 70)
    
    return True


def generate_summary_report(spec_path: str = ".lingma/specs/current-spec.md", 
                           output_path: str = None):
    """生成摘要报告"""
    spec_file = Path(spec_path)
    
    if not spec_file.exists():
        print("❌ Spec 文件不存在")
        return
    
    content = spec_file.read_text(encoding='utf-8')
    metadata = extract_metadata(content)
    tasks = analyze_tasks(content)
    
    report = {
        'spec_name': spec_file.stem,
        'status': metadata.get('status', 'unknown'),
        'priority': metadata.get('priority', 'N/A'),
        'progress': {
            'tasks_completed': tasks['completed'],
            'tasks_total': tasks['total'],
            'percentage': (tasks['completed'] / tasks['total'] * 100) if tasks['total'] > 0 else 0
        },
        'last_updated': datetime.now().isoformat()
    }
    
    if output_path:
        import json
        output_file = Path(output_path)
        output_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"✅ 报告已保存到: {output_path}")
    else:
        import json
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Spec 状态检查工具')
    parser.add_argument('--spec', '-s', 
                       default='.lingma/specs/current-spec.md',
                       help='Spec 文件路径 (默认: .lingma/specs/current-spec.md)')
    parser.add_argument('--summary', '-m',
                       action='store_true',
                       help='生成 JSON 格式的摘要报告')
    parser.add_argument('--output', '-o',
                       help='输出文件路径 (与 --summary 一起使用)')
    
    args = parser.parse_args()
    
    if args.summary:
        generate_summary_report(args.spec, args.output)
    else:
        success = check_spec_status(args.spec)
        sys.exit(0 if success else 1)
