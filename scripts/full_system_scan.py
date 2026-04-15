#!/usr/bin/env python3
"""全盘扫描所有可能的冗余问题"""

import os
from pathlib import Path

print('='*70)
print('🔍 全盘扫描：检查所有可能的冗余问题')
print('='*70)

# 1. 检查 .lingma/docs/ 根目录文档数量
docs_dir = Path('.lingma/docs')
root_docs = list(docs_dir.glob('*.md'))
print(f'\n📄 .lingma/docs/ 根目录文档: {len(root_docs)} 个')
if len(root_docs) > 5:
    print(f'   ❌ 过多！应该 ≤5 个')
    for f in sorted(root_docs):
        print(f'      - {f.name}')

# 2. 检查是否有重复主题的文档
print('\n🔎 检查重复主题...')
themes = {
    'MCP': [f for f in root_docs if 'MCP' in f.name],
    'ROOT_CLEANLINESS': [f for f in root_docs if 'ROOT' in f.name or 'CLEANLINESS' in f.name],
    'RULES_INDEX': [f for f in root_docs if 'RULES' in f.name or 'rules' in f.name],
    'OPTIMIZATION': [f for f in root_docs if 'OPTIMIZATION' in f.name or 'optimization' in f.name],
    'REPORT': [f for f in root_docs if 'REPORT' in f.name or 'report' in f.name]
}

for theme, files in themes.items():
    if len(files) > 1:
        print(f'   ❌ {theme}: {len(files)} 个重复文档')
        for f in files:
            print(f'      - {f.name}')

# 3. 检查其他目录是否有类似问题
print('\n📂 检查其他目录...')
for subdir in ['agents', 'rules', 'skills']:
    dir_path = Path(f'.lingma/{subdir}')
    if dir_path.exists():
        readme_files = list(dir_path.glob('README.md'))
        if readme_files:
            print(f'   ❌ .lingma/{subdir}/ 有 README.md（违反规范）')

# 4. 🔥 硬扫描：检查所有目录的临时文件
print('\n🏠 检查项目根目录...')
root_dir = Path('.')
temp_patterns = ['*.log', '*.tmp', '*.bak']
temp_files = []
for pattern in temp_patterns:
    temp_files.extend(root_dir.glob(pattern))

# 🔥 新增：检测数字、大小标记等临时文件
import re
temp_name_pattern = re.compile(r'^\d+$|^\d+KB$|^\d+MB$|^\d+GB$|^temp_|^tmp_|^test_|^debug_|^check_|^verify_')
for item in root_dir.iterdir():
    if item.is_file() and temp_name_pattern.match(item.name):
        temp_files.append(item)

if temp_files:
    print(f'   ❌ 检测到 {len(temp_files)} 个临时文件:')
    for f in sorted(temp_files):
        print(f'      - {f.name}')
    print(f'   💡 临时文件必须用完即删！')
else:
    print(f'   ✅ 无临时文件')

print('\n' + '='*70)
print('✅ 全盘扫描完成')
print('='*70)
