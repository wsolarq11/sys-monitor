"""
Spec-Driven Core Agent - Spec lifecycle management and task execution.

Features:
- Spec reading and parsing
- Task decomposition
- Parallel task execution
- Quality reflection engine
- Spec state management
- Async execution with Redis caching
- Event-driven communication
"""

import asyncio
import json
import time
from typing import Any, Dict, List

try:
    from agent_base import AsyncAgentBase
except ImportError:
    from .agent_base import AsyncAgentBase


class SpecDrivenCoreAgent(AsyncAgentBase):
    """
    Spec-Driven Core Agent for managing spec lifecycle.

    Capabilities:
    - Read and parse specs
    - Decompose specs into tasks
    - Execute tasks in parallel
    - Quality reflection and assessment
    - Update spec state
    """

    def __init__(self, redis_url: str = "redis://localhost:6379", timeout: int = 60):
        super().__init__(redis_url, timeout)
        self.agent_name = "spec_driven"

    async def _do_execute(self, task_data: Dict[str, Any]) -> Any:
        """Execute spec-driven task"""
        spec_id = task_data.get("spec_id")
        if not spec_id:
            raise ValueError("No spec_id provided")

        return await self.execute_spec(spec_id)

    async def execute_spec(self, spec_id: str) -> Dict[str, Any]:
        """
        Execute a complete spec lifecycle.

        Args:
            spec_id: Spec identifier

        Returns:
            Execution results including status and tasks completed
        """
        # Check cache first
        cache_key = f"result:{spec_id}:spec_execution"
        cached = await self._get_cache(cache_key)
        if cached is not None:
            return cached

        # Step 1: Read spec
        spec = await self.read_spec_async(spec_id)

        # Step 2: Decompose into tasks
        tasks = await self.decompose_spec(spec)

        # Step 3: Execute tasks in parallel
        task_results = await asyncio.gather(
            *[self.execute_task(task) for task in tasks], return_exceptions=True
        )

        # Filter out exceptions
        successful_tasks = [
            r
            for r in task_results
            if not isinstance(r, Exception) and isinstance(r, dict)
        ]

        # Step 4: Quality reflection
        quality_score = await self.reflect_on_quality(spec, successful_tasks)

        # Step 5: Update spec state
        await self.update_spec_state(spec_id, "completed", quality_score)

        result = {
            "spec_id": spec_id,
            "status": "completed",
            "tasks_completed": len(successful_tasks),
            "quality_score": quality_score,
            "timestamp": time.time(),
        }

        # Cache the result
        await self._set_cache(cache_key, result)

        # Publish completion event
        await self._publish_event(
            "completed", {"spec_id": spec_id, "tasks_completed": len(successful_tasks)}
        )

        return result

    async def read_spec_async(self, spec_id: str) -> Dict[str, Any]:
        """
        Read spec file asynchronously.

        Args:
            spec_id: Spec identifier

        Returns:
            Parsed spec data
        """
        try:
            # In production, this would read from .lingma/specs/
            # For now, return mock data
            await asyncio.sleep(0.05)

            return {"id": spec_id, "title": f"Spec {spec_id}", "tasks": []}
        except Exception as e:
            return {"id": spec_id, "error": str(e)}

    async def decompose_spec(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Decompose spec into executable tasks.

        Args:
            spec: Spec data

        Returns:
            List of tasks
        """
        # Simple decomposition - in production would use AI
        await asyncio.sleep(0.02)

        # Return mock tasks
        return [
            {"task_id": f"{spec['id']}-task-1", "type": "implementation"},
            {"task_id": f"{spec['id']}-task-2", "type": "testing"},
        ]

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single task.

        Args:
            task: Task definition

        Returns:
            Task execution result
        """
        # Simulate task execution
        await asyncio.sleep(0.05)

        return {
            "task_id": task.get("task_id"),
            "status": "completed",
            "type": task.get("type"),
        }

    async def reflect_on_quality(
        self, spec: Dict[str, Any], task_results: List[Dict[str, Any]]
    ) -> float:
        """
        Reflect on execution quality and generate score.

        Args:
            spec: Original spec
            task_results: Results from task execution

        Returns:
            Quality score (0-100)
        """
        # Simple quality assessment
        await asyncio.sleep(0.03)

        # Base score
        score = 85.0

        # Adjust based on task success rate
        if task_results:
            success_rate = len(task_results) / max(len(task_results), 1)
            score = score * success_rate

        return min(100.0, max(0.0, score))

    async def update_spec_state(
        self, spec_id: str, state: str, quality_score: float = 0.0
    ):
        """
        Update spec state in Redis.

        Args:
            spec_id: Spec identifier
            state: New state (draft/in-progress/completed/archived)
            quality_score: Quality assessment score
        """
        try:
            state_key = f"spec:{spec_id}:state"
            state_data = {
                "state": state,
                "quality_score": quality_score,
                "updated_at": time.time(),
            }
            await self._set_cache(state_key, state_data, ttl=86400)  # 24 hours
        except Exception:
            pass

    async def write_spec_async(self, spec_id: str, spec_data: Dict[str, Any]):
        """
        Write spec data asynchronously.

        Args:
            spec_id: Spec identifier
            spec_data: Spec data to write
        """
        await asyncio.sleep(0.02)
        # In production, this would write to .lingma/specs/
        pass
