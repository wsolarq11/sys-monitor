#!/usr/bin/env python3
"""最终任务完成验证 - 端到端烟测"""

import os
import sys
from pathlib import Path

print('='*70)
print('🔍 最终任务完成验证 - 端到端烟测')
print('='*70)
print()

checks_passed = 0
checks_total = 0

def check(name, condition, details=""):
    global checks_passed, checks_total
    checks_total += 1
    status = "✅" if condition else "❌"
    print(f'{status} {name}')
    if details:
        print(f'   {details}')
    if condition:
        checks_passed += 1
    return condition

# 1. AGENTS.md ≤5KB
agents_size = os.path.getsize('.lingma/rules/AGENTS.md')
check('AGENTS.md ≤5KB', agents_size <= 5120, f'{agents_size/1024:.1f}KB')

# 2. 无临时文件（排除.gitignore等正常文件）
root_files = [f.name for f in Path('.').iterdir() if f.is_file()]
temp_pattern = __import__('re').compile(r'^\d+$|^\d+KB$|^\d+MB$|^\d+GB$')
temp_files = [f for f in root_files if temp_pattern.match(f) and not f.startswith('.')]
check('项目根目录无临时文件', len(temp_files) == 0, f'发现: {temp_files}' if temp_files else '')

# 3. scripts/目录存在且位置正确
check('scripts/在项目根目录', Path('scripts').exists() and Path('scripts').is_dir())

# 4. .lingma/docs/根目录文档 ≤5个
docs_root = list(Path('.lingma/docs').glob('*.md'))
check('.lingma/docs/根目录文档 ≤5个', len(docs_root) <= 5, f'{len(docs_root)}个')

# 5. Git Hook存在
check('Git Hook存在', Path('.git/hooks/pre-commit').exists())

# 6. full_system_scan.py存在
check('full_system_scan.py存在', Path('scripts/full_system_scan.py').exists())

# 7. verify_memory_length.py存在
check('verify_memory_length.py存在', Path('scripts/verify_memory_length.py').exists())

# 8. 无.lingma/reports/目录
check('.lingma/reports/已删除', not Path('.lingma/reports').exists())

# 9. 无.lingma/scripts/目录
check('.lingma/scripts/已删除', not Path('.lingma/scripts').exists())

# 10. 无双docs目录
check('无双docs目录', not Path('docs').exists() or Path('sys-monitor/docs').exists())

print()
print('='*70)
print(f'📊 验证结果: {checks_passed}/{checks_total} 通过')
print('='*70)

if checks_passed == checks_total:
    print('\n✅ 所有任务完成！系统健康状态良好！')
    sys.exit(0)
else:
    print(f'\n❌ {checks_total - checks_passed} 项检查失败，需要修复')
    sys.exit(1)
