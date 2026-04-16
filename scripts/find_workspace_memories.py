#!/usr/bin/env python3
"""查找所有workspace scope记忆的工具"""

import json
import os
from pathlib import Path

# Lingma记忆存储位置
memory_path = Path.home() / ".lingma" / "cache" / "projects"

print('='*70)
print('🔍 查找所有workspace scope记忆')
print('='*70)
print()

# 遍历所有项目目录
workspace_memories = []
global_memories = []

for project_dir in memory_path.iterdir():
    if not project_dir.is_dir():
        continue
    
    # 查找记忆文件
    memory_files = list(project_dir.glob("**/*.json"))
    
    for mem_file in memory_files:
        try:
            with open(mem_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 检查是否是记忆数据
                if isinstance(data, dict):
                    scope = data.get('scope', 'unknown')
                    title = data.get('title', 'Unknown')
                    
                    if scope == 'workspace':
                        workspace_memories.append({
                            'file': str(mem_file),
                            'title': title,
                            'scope': scope
                        })
                    elif scope == 'global':
                        global_memories.append({
                            'file': str(mem_file),
                            'title': title,
                            'scope': scope
                        })
        except Exception as e:
            pass

print(f'📊 统计结果:')
print(f'  ✅ Global记忆: {len(global_memories)} 个')
print(f'  ❌ Workspace记忆: {len(workspace_memories)} 个')
print()

if workspace_memories:
    print('🚨 发现Workspace记忆:')
    for i, mem in enumerate(workspace_memories, 1):
        print(f'  {i}. {mem["title"]}')
        print(f'     文件: {mem["file"]}')
        print()
else:
    print('✅ 未发现Workspace记忆！')
    print()

print('='*70)
