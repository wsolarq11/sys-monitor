#!/usr/bin/env python3
"""
Spec 缓存清理工具

功能：
1. 清理超过指定时间的 Spec 缓存文件
2. 保持缓存目录整洁
3. 避免磁盘空间浪费

使用方法：
    python cleanup_spec_cache.py [--max-age 3600] [--cache-dir .lingma/cache]
"""

import os
import sys
import time
import argparse
from pathlib import Path


def cleanup_spec_cache(cache_dir: Path, max_age: int = 3600) -> dict:
    """
    清理超过指定时间的 Spec 缓存
    
    Args:
        cache_dir: 缓存目录路径
        max_age: 最大保留时间（秒），默认 1 小时
        
    Returns:
        清理统计信息
    """
    stats = {
        'total_files': 0,
        'deleted_files': 0,
        'kept_files': 0,
        'freed_space': 0
    }
    
    if not cache_dir.exists():
        print(f"⚠️  缓存目录不存在: {cache_dir}")
        return stats
    
    now = time.time()
    
    for cache_file in cache_dir.glob("*.json"):
        stats['total_files'] += 1
        file_age = now - cache_file.stat().st_mtime
        
        if file_age > max_age:
            # 删除过期缓存
            file_size = cache_file.stat().st_size
            cache_file.unlink()
            stats['deleted_files'] += 1
            stats['freed_space'] += file_size
            print(f"🗑️  删除过期缓存: {cache_file.name} ({file_size / 1024:.1f}KB, {file_age / 3600:.1f}h)")
        else:
            stats['kept_files'] += 1
    
    return stats


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f}MB"


def main():
    parser = argparse.ArgumentParser(description='清理 Spec 缓存')
    parser.add_argument('--max-age', type=int, default=3600,
                       help='缓存最大保留时间（秒），默认 3600（1小时）')
    parser.add_argument('--cache-dir', type=str, default='.lingma/cache',
                       help='缓存目录路径，默认 .lingma/cache')
    
    args = parser.parse_args()
    
    cache_dir = Path(args.cache_dir)
    
    print("=" * 70)
    print("  Spec 缓存清理工具")
    print("=" * 70)
    print()
    print(f"缓存目录: {cache_dir.absolute()}")
    print(f"最大保留时间: {args.max_age} 秒 ({args.max_age / 3600:.1f} 小时)")
    print()
    
    # 执行清理
    stats = cleanup_spec_cache(cache_dir, args.max_age)
    
    print()
    print("=" * 70)
    print("  清理结果")
    print("=" * 70)
    print(f"总文件数: {stats['total_files']}")
    print(f"删除文件: {stats['deleted_files']}")
    print(f"保留文件: {stats['kept_files']}")
    print(f"释放空间: {format_size(stats['freed_space'])}")
    print()
    
    if stats['deleted_files'] > 0:
        print("✅ 清理完成！")
    else:
        print("ℹ️  没有需要清理的缓存文件")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
