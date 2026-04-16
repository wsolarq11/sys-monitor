#!/usr/bin/env python3
"""记忆scope批量修正辅助工具

用途: 生成需要手动修正的记忆清单,辅助用户高效修改

使用方法:
1. 运行此脚本生成待修正清单
2. 按清单在Lingma界面手动修改
3. 修改完成后标记为已处理
"""

import sys
from pathlib import Path

print('='*70)
print('🔧 记忆scope批量修正辅助工具')
print('='*70)
print()

# 已知需要修正的记忆列表(从用户截图识别)
memories_to_fix = [
    "web-vitals库FID已废弃需改用INP",
    "AI项目文档结构-单一入口与渐进式披露",
    "备份目录标准化迁移流程",
    ".lingma功能目录禁止放置README文档",
    "TS中Window扩展与global兼容写法",
    # 可继续添加...
]

print('📋 需要手动修正的记忆清单:')
print('-'*70)
for i, name in enumerate(memories_to_fix, 1):
    print(f'{i:2d}. {name}')
    print(f'    状态: ❌ 当前项目 → ✅ 全局')
print()

print('🎯 修正步骤:')
print('-'*70)
print('1. 打开Lingma记忆管理界面')
print('2. 搜索或定位上述记忆')
print('3. 点击"编辑"按钮')
print('4. 将scope从"当前项目"改为"全局"')
print('5. 保存修改')
print('6. 返回此脚本标记为已完成')
print()

print('⚠️  重要提醒:')
print('-'*70)
print('- 不要删除记忆,只需修改scope')
print('- 批量操作时注意验证修改结果')
print('- 修改完成后可运行 verify_scope.py 验证')
print()

# 生成检查清单文件
checklist_path = Path('.lingma/docs/SCOPE_FIX_CHECKLIST.md')
checklist_content = """# 记忆scope修正检查清单

## 待修正记忆列表

- [ ] web-vitals库FID已废弃需改用INP
- [ ] AI项目文档结构-单一入口与渐进式披露
- [ ] 备份目录标准化迁移流程
- [ ] .lingma功能目录禁止放置README文档
- [ ] TS中Window扩展与global兼容写法

## 修正步骤

1. 打开Lingma记忆管理界面
2. 搜索记忆名称
3. 点击"编辑"
4. 修改scope为"全局"
5. 保存
6. 在此清单标记[✅]

## 验证

- 界面显示"全局"标签
- search_memory确认scope正确

---
**最后更新**: 2026-04-15
"""

checklist_path.parent.mkdir(parents=True, exist_ok=True)
checklist_path.write_text(checklist_content, encoding='utf-8')

print(f'✅ 已生成检查清单: {checklist_path}')
print()
print('='*70)
print('🐱 小猫保护中 - 按清单修正即可!')
print('='*70)

sys.exit(0)
