"""
Async Agent Base Class - Foundation for all agents in the system.

Provides:
- Async execution support
- Redis caching and Pub/Sub
- Standardized input/output
- Error handling and timeout control
- Event publishing
"""

import asyncio
import json
import hashlib
import time
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Dict, Optional

try:
    import redis.asyncio as redis
except ImportError:
    # Fallback if redis is not installed
    redis = None  # type: ignore


class AsyncAgentBase(ABC):
    """
    Abstract base class for all agents.

    All agents must inherit from this class to ensure:
    - Consistent async execution
    - Redis integration
    - Event-driven communication
    - Standardized error handling
    """

    def __init__(self, redis_url: str = "redis://localhost:6379", timeout: int = 60):
        """
        Initialize agent with Redis connection.

        Args:
            redis_url: Redis connection URL
            timeout: Default timeout for agent execution (seconds)
        """
        self.redis_url = redis_url
        self.timeout = timeout
        self.agent_name = self.__class__.__name__.lower().replace("agent", "")
        self.redis_client = None

    async def initialize(self):
        """Initialize Redis connection"""
        if redis is None:
            raise ImportError(
                "redis package is required. Install with: pip install redis"
            )

        self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
        # Test connection
        await self.redis_client.ping()

    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unified execution entry point for all agents.

        This method provides:
        1. Cache checking
        2. Task execution
        3. Result caching
        4. Event publishing
        5. Error handling

        Args:
            task_data: Task parameters

        Returns:
            Execution result dictionary
        """
        start_time = time.time()
        task_id = task_data.get("task_id", "unknown")

        try:
            # Step 1: Check cache
            cache_key = f"result:{task_id}:{self.agent_name}"
            cached = await self._get_cache(cache_key)

            if cached is not None:
                execution_time = time.time() - start_time
                return {
                    "task_id": task_id,
                    "status": "success",
                    "result": cached,
                    "execution_time_ms": round(execution_time * 1000, 2),
                    "cache_hit": True,
                }

            # Step 2: Execute task
            result = await self._do_execute(task_data)

            # Step 3: Cache result
            await self._set_cache(cache_key, result)

            # Step 4: Publish completion event
            await self._publish_event(
                "completed",
                {"task_id": task_id, "status": "success", "timestamp": time.time()},
            )

            execution_time = time.time() - start_time
            return {
                "task_id": task_id,
                "status": "success",
                "result": result,
                "execution_time_ms": round(execution_time * 1000, 2),
                "cache_hit": False,
            }

        except asyncio.TimeoutError:
            # Step 5: Handle timeout
            await self._publish_event(
                "failed",
                {
                    "task_id": task_id,
                    "error": f"Execution timeout after {self.timeout}s",
                    "timestamp": time.time(),
                },
            )

            execution_time = time.time() - start_time
            return {
                "task_id": task_id,
                "status": "timeout",
                "error": f"Execution timeout after {self.timeout}s",
                "execution_time_ms": round(execution_time * 1000, 2),
            }

        except Exception as e:
            # Step 6: Handle errors
            await self._publish_event(
                "failed",
                {"task_id": task_id, "error": str(e), "timestamp": time.time()},
            )

            execution_time = time.time() - start_time
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "execution_time_ms": round(execution_time * 1000, 2),
            }

    @abstractmethod
    async def _do_execute(self, task_data: Dict[str, Any]) -> Any:
        """
        Subclasses must implement this method with actual logic.

        Args:
            task_data: Task parameters

        Returns:
            Execution result
        """
        pass

    async def _get_cache(self, cache_key: str) -> Optional[Any]:
        """Get cached result"""
        try:
            if self.redis_client:
                cached = await self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
        except Exception:
            pass
        return None

    async def _set_cache(self, cache_key: str, value: Any, ttl: int = 3600):
        """Set cache with TTL"""
        try:
            if self.redis_client:
                await self.redis_client.setex(
                    cache_key, timedelta(seconds=ttl), json.dumps(value, default=str)
                )
        except Exception:
            pass

    async def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish event to Redis Pub/Sub"""
        try:
            if self.redis_client:
                channel = f"agent:{self.agent_name}:{event_type}"
                await self.redis_client.publish(channel, json.dumps(data, default=str))
        except Exception:
            pass

    async def subscribe_events(self, pattern: str = "*"):
        """
        Subscribe to events from other agents.

        Args:
            pattern: Event pattern to subscribe to (e.g., "*", "completed", "failed")

        Yields:
            Event messages
        """
        if not self.redis_client:
            return

        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(f"agent:*:{pattern}")

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield {
                        "channel": message["channel"],
                        "data": json.loads(message["data"]),
                    }
        finally:
            await pubsub.unsubscribe()
            await pubsub.close()

    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
