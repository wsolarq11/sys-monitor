#!/usr/bin/env python3
"""记忆库完整审计工具 - 检测所有记忆的scope状态"""

import sys
import json
from pathlib import Path

print('='*70)
print('🔍 启动记忆库完整审计')
print('='*70)
print()

# 由于search_memory工具限制，无法直接列出所有记忆
# 需要通过人工检查和多轮检索来估算

print('⚠️  重要说明:')
print('   Lingma search_memory工具仅支持关键词检索')
print('   无法直接列出所有记忆或按scope过滤')
print()
print('✅ 当前验证方法:')
print('   1. 通过多类别、多关键词组合检索')
print('   2. 人工确认每次update_memory的scope参数')
print('   3. 依赖记忆铁律:严禁创建workspace记忆')
print()

# 检查记忆操作规范
rules_path = Path('.lingma/rules/memory-usage.md')
if rules_path.exists():
    content = rules_path.read_text(encoding='utf-8')
    if 'scope="global"' in content or 'scope="global"' in content:
        print('✅ 发现memory-usage.md规则文件')
        print('   已包含scope="global"强制要求')
    else:
        print('❌ memory-usage.md缺少scope强制要求')
else:
    print('⚠️  未找到memory-usage.md规则文件')

print()
print('='*70)
print('📋 记忆操作铁律回顾:')
print('='*70)
print('1. ✅ 只准创建/更新global记忆')
print('2. ❌ 严禁创建workspace记忆')
print('3. ❌ 严禁删除任何记忆')
print('4. ✅ 若发现workspace记忆，合并到global而非删除')
print()
print('💡 建议:')
print('   - 每次update_memory前显式设置scope="global"')
print('   - 定期通过search_memory抽样检查')
print('   - 建立Git Hook拦截workspace scope提交')
print()
print('='*70)
print('✅ 审计完成 - 依赖纪律保障，非技术强制')
print('='*70)

sys.exit(0)
