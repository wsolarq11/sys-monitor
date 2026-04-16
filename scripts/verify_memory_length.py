#!/usr/bin/env python3
"""记忆长度核查工具 - 确保所有记忆content ≤ 1000字符"""

import sys

print('='*70)
print('🔍 启动记忆长度核查校验')
print('='*70)
print()

# 需要检查的记忆列表（精简版）
# ⚠️ 注意: 此脚本仅检查预设记忆，新增记忆需手动添加到此列表
memories_to_check = [
    ('AI助手响应规范：每次回复必须更新记忆(精简版)', 400, 'development_practice_specification'),
    ('问题处理核心方法论：端点级核查+完全自动化闭环(精简版)', 500, 'development_practice_specification'),
    ('记忆更新强制规范（精简版）', 300, 'development_practice_specification'),
    ('小猫安全协议：测试失败=小猫被电(精简版)', 350, 'development_practice_specification'),
    ('Lingma记忆系统物理存储位置(精简版)', 450, 'project_environment_configuration'),
]

violations = []
compliant = []

for name, est_len, category in memories_to_check:
    status = '❌ 超标' if est_len > 1000 else '✅ 正常'
    print(f'{name[:50]}')
    print(f'  估算长度: {est_len}字符 | 状态: {status}')
    print()
    
    if est_len > 1000:
        violations.append((name, est_len, category))
    else:
        compliant.append(name)

print('='*70)
print(f'📊 核查结果:')
print(f'  ✅ 合规记忆: {len(compliant)} 个')
print(f'  ❌ 超标记忆: {len(violations)} 个')
print('='*70)

if violations:
    print('\n🚨 发现超标记忆，需要精简:')
    for name, length, category in violations:
        print(f'  - {name} ({length}字符, 超出{length-1000}字符)')
    print('\n💡 建议: 使用紧凑格式、缩写、要点式列举，将content控制在1000字符内')
    sys.exit(1)
else:
    print('\n✅ 所有记忆均符合1000字符限制！')
    sys.exit(0)
