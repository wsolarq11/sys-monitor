#!/usr/bin/env python3
"""
紧急修复：精简所有超标的 Rules 文件
目标: Rule ≤ 3KB
"""

import os
from pathlib import Path

rules_dir = Path('.lingma/rules')

# 需要优化的 Rules（当前大小 > 3KB）
rules_to_optimize = {
    'AGENTS.md': 11.2,  # KB
    'automation-policy.md': 11.2,
    'doc-redundancy-prevention.md': 5.3,
    'memory-usage.md': 13.9,
}

print("=" * 70)
print("🔧 开始紧急修复：精简 Rules 文件")
print("=" * 70)
print()

for rule_name, current_size in rules_to_optimize.items():
    rule_path = rules_dir / rule_name
    
    if not rule_path.exists():
        print(f"⚠️  {rule_name}: 文件不存在")
        continue
    
    print(f"📄 {rule_name}: {current_size}KB → 目标 ≤3KB")
    
    # 读取内容
    content = rule_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # 策略：保留 frontmatter + 核心指令，移除详细示例
    # 这里只是标记，实际需要手动优化
    print(f"   行数: {len(lines)}")
    print(f"   状态: 需要手动优化")
    print()

print("=" * 70)
print("💡 建议:")
print("   1. 对每个 Rule 创建精简版（≤3KB）")
print("   2. 详细内容移至 .lingma/docs/architecture/")
print("   3. Rule 文件仅保留核心指令和引用链接")
print("=" * 70)
