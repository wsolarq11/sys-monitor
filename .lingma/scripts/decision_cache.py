#!/usr/bin/env python3
"""
决策缓存模块 - 用于提高决策引擎性能

职责：
1. 缓存常用决策结果
2. 提供快速查找功能
3. 自动清理过期缓存
"""

import time
import json
import hashlib
from pathlib import Path
from typing import Any, Optional, Dict
from collections import OrderedDict


class DecisionCache:
    """决策结果缓存"""

    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        初始化决策缓存

        Args:
            max_size: 最大缓存条目数
            ttl: 缓存生存时间（秒）
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def _generate_key(self, operation: Dict[str, Any]) -> str:
        """生成缓存键"""
        # 创建操作的规范表示
        canonical = json.dumps(operation, sort_keys=True)
        return hashlib.md5(canonical.encode()).hexdigest()

    def get(self, operation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """获取缓存的决策结果"""
        key = self._generate_key(operation)

        if key in self.cache:
            entry = self.cache[key]
            # 检查是否过期
            if time.time() - entry["timestamp"] < self.ttl:
                # 移动到末尾（LRU）
                self.cache.move_to_end(key)
                self.hits += 1
                return entry["result"]
            else:
                # 删除过期条目
                del self.cache[key]

        self.misses += 1
        return None

    def set(self, operation: Dict[str, Any], result: Dict[str, Any]):
        """设置决策结果缓存"""
        key = self._generate_key(operation)

        # 如果缓存已满，删除最旧的条目
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)

        self.cache[key] = {"result": result, "timestamp": time.time()}

        # 移动到末尾（LRU）
        self.cache.move_to_end(key)

    def clear_expired(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key
            for key, entry in self.cache.items()
            if current_time - entry["timestamp"] >= self.ttl
        ]

        for key in expired_keys:
            del self.cache[key]

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_percent": round(hit_rate, 2),
            "ttl_seconds": self.ttl,
        }

    def save_to_disk(self, filepath: str = ".lingma/cache/decision_cache.json"):
        """保存缓存到磁盘"""
        cache_dir = Path(filepath).parent
        cache_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "cache": dict(self.cache),
            "stats": {"hits": self.hits, "misses": self.misses},
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_from_disk(self, filepath: str = ".lingma/cache/decision_cache.json"):
        """从磁盘加载缓存"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.cache = OrderedDict(data.get("cache", {}))
            stats = data.get("stats", {})
            self.hits = stats.get("hits", 0)
            self.misses = stats.get("misses", 0)

            # 清理过期的条目
            self.clear_expired()

            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False


# 全局缓存实例
_decision_cache = None


def get_decision_cache() -> DecisionCache:
    """获取全局决策缓存实例"""
    global _decision_cache
    if _decision_cache is None:
        _decision_cache = DecisionCache()
        # 尝试从磁盘加载
        _decision_cache.load_from_disk()
    return _decision_cache


def cache_decision(operation: Dict[str, Any], result: Dict[str, Any]):
    """缓存决策结果的便捷函数"""
    cache = get_decision_cache()
    cache.set(operation, result)


def get_cached_decision(operation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """获取缓存的决策结果的便捷函数"""
    cache = get_decision_cache()
    return cache.get(operation)


if __name__ == "__main__":
    # 测试缓存功能
    cache = DecisionCache(max_size=100, ttl=60)

    # 测试缓存操作
    test_operation = {"type": "file_read", "path": "/test/file.txt"}
    test_result = {"strategy": "auto_execute", "risk": "low"}

    # 首次访问 - 应该未命中
    result = cache.get(test_operation)
    print(f"首次访问: {result}")  # None

    # 设置缓存
    cache.set(test_operation, test_result)

    # 再次访问 - 应该命中
    result = cache.get(test_operation)
    print(f"再次访问: {result}")  # {'strategy': 'auto_execute', 'risk': 'low'}

    # 打印统计信息
    stats = cache.get_stats()
    print(f"缓存统计: {stats}")

    # 测试持久化
    cache.save_to_disk()
    print("缓存已保存到磁盘")

    # 创建新实例并加载
    new_cache = DecisionCache()
    loaded = new_cache.load_from_disk()
    print(f"缓存加载成功: {loaded}")

    # 验证加载的数据
    result = new_cache.get(test_operation)
    print(f"加载后访问: {result}")
