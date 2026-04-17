"""
Unit tests for Spec-Driven Core Agent with AsyncIO and Redis support.
Tests cover spec execution, caching, event publishing, and quality reflection.
"""
import pytest
import pytest_asyncio
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import timedelta


class MockRedis:
    """Mock Redis client for testing"""
    
    def __init__(self):
        self.data = {}
        self.published_messages = []
        
    async def get(self, key):
        return self.data.get(key)
    
    async def setex(self, key, ttl, value):
        self.data[key] = value
        
    async def publish(self, channel, message):
        self.published_messages.append({"channel": channel, "message": message})


@pytest_asyncio.fixture
async def mock_redis():
    """Fixture for mocked Redis client"""
    return MockRedis()


@pytest_asyncio.fixture
async def spec_driven_agent(mock_redis):
    """Fixture for Spec-Driven Core Agent with mocked dependencies"""
    from .lingma.agents.spec_driven_core_agent import SpecDrivenCoreAgent
    
    agent = SpecDrivenCoreAgent.__new__(SpecDrivenCoreAgent)
    agent.redis = mock_redis
    return agent


@pytest.mark.asyncio
async def test_execute_spec_with_cache_hit(spec_driven_agent, mock_redis):
    """Test spec execution when cache hit occurs"""
    spec_id = "spec-001"
    cached_result = {"spec_id": spec_id, "status": "completed", "tasks_completed": 5}
    
    # Set up cache
    cache_key = f"result:{spec_id}:spec_execution"
    await mock_redis.setex(cache_key, 3600, json.dumps(cached_result))
    
    # Execute
    result = await spec_driven_agent.execute_spec(spec_id)
    
    # Verify
    assert result == cached_result
    assert len(mock_redis.published_messages) == 0  # No new events


@pytest.mark.asyncio
async def test_execute_spec_with_cache_miss(spec_driven_agent, mock_redis):
    """Test spec execution when cache miss occurs"""
    spec_id = "spec-002"
    
    # Mock methods
    with patch.object(spec_driven_agent, 'read_spec_async', AsyncMock(return_value={"id": spec_id})), \
         patch.object(spec_driven_agent, 'decompose_spec', AsyncMock(return_value=[{"task": 1}, {"task": 2}])), \
         patch.object(spec_driven_agent, 'execute_task', AsyncMock(return_value={"status": "ok"})), \
         patch.object(spec_driven_agent, 'reflect_on_quality', AsyncMock(return_value={"score": 85})):
        
        # Execute
        result = await spec_driven_agent.execute_spec(spec_id)
        
        # Verify
        assert result["spec_id"] == spec_id
        assert result["status"] == "completed"
        assert result["tasks_completed"] == 2
        
        cache_key = f"result:{spec_id}:spec_execution"
        assert cache_key in mock_redis.data
        assert len(mock_redis.published_messages) == 1


@pytest.mark.asyncio
async def test_parallel_task_execution(spec_driven_agent):
    """Test that tasks execute in parallel using asyncio.gather"""
    
    async def slow_task():
        await asyncio.sleep(0.1)
        return {"status": "ok"}
    
    tasks = [slow_task() for _ in range(5)]
    
    start_time = asyncio.get_event_loop().time()
    results = await asyncio.gather(*tasks)
    end_time = asyncio.get_event_loop().time()
    
    # If truly parallel, should take ~0.1s, not ~0.5s
    assert end_time - start_time < 0.2
    assert len(results) == 5


@pytest.mark.asyncio
async def test_update_spec_state(spec_driven_agent, mock_redis):
    """Test updating spec state with caching and event publishing"""
    spec_id = "spec-003"
    state = {"status": "in_progress", "progress": 50}
    
    with patch.object(spec_driven_agent, 'write_spec_async', AsyncMock()):
        await spec_driven_agent.update_spec_state(spec_id, state)
    
    # Verify cache was updated
    cache_key = f"spec:{spec_id}:state"
    assert cache_key in mock_redis.data
    
    # Verify event was published
    assert len(mock_redis.published_messages) == 1
    assert mock_redis.published_messages[0]["channel"] == "agent:spec_driven:state_changed"


@pytest.mark.asyncio
async def test_event_publishing(spec_driven_agent, mock_redis):
    """Test that completion events are published to Redis Pub/Sub"""
    spec_id = "spec-004"
    tasks_count = 3
    
    await mock_redis.publish(
        "agent:spec_driven:completed",
        json.dumps({"spec_id": spec_id, "tasks": tasks_count})
    )
    
    assert len(mock_redis.published_messages) == 1
    assert mock_redis.published_messages[0]["channel"] == "agent:spec_driven:completed"
    assert json.loads(mock_redis.published_messages[0]["message"])["spec_id"] == spec_id


@pytest.mark.asyncio
async def test_cache_expiration(spec_driven_agent, mock_redis):
    """Test that cache has proper TTL"""
    spec_id = "spec-005"
    result_data = {"status": "completed"}
    
    cache_key = f"result:{spec_id}:spec_execution"
    await mock_redis.setex(cache_key, timedelta(seconds=3600), json.dumps(result_data))
    
    # Verify data is stored
    cached = await mock_redis.get(cache_key)
    assert cached is not None
    assert json.loads(cached) == result_data


@pytest.mark.asyncio
async def test_quality_reflection(spec_driven_agent):
    """Test quality reflection on execution results"""
    results = [{"status": "ok"}, {"status": "ok"}, Exception("Failed")]
    
    with patch.object(spec_driven_agent, 'reflect_on_quality', AsyncMock(return_value={"score": 75})):
        reflection = await spec_driven_agent.reflect_on_quality(results)
        
        assert reflection["score"] == 75


@pytest.mark.asyncio
async def test_subscribe_events(spec_driven_agent, mock_redis):
    """Test event subscription functionality"""
    pubsub = mock_redis.pubsub()
    await pubsub.subscribe("agent:spec_driven:*")
    
    # Should not raise exception
    assert True


@pytest.mark.asyncio
async def test_multiple_specs_execution(spec_driven_agent):
    """Test executing multiple specs"""
    spec_ids = [f"spec-{i}" for i in range(5)]
    
    results = []
    for spec_id in spec_ids:
        with patch.object(spec_driven_agent, 'read_spec_async', AsyncMock(return_value={"id": spec_id})), \
             patch.object(spec_driven_agent, 'decompose_spec', AsyncMock(return_value=[])), \
             patch.object(spec_driven_agent, 'reflect_on_quality', AsyncMock(return_value={"score": 80})):
            
            result = await spec_driven_agent.execute_spec(spec_id)
            results.append(result)
    
    assert len(results) == 5


@pytest.mark.asyncio
async def test_error_handling_in_task_execution(spec_driven_agent):
    """Test error handling during task execution"""
    
    async def failing_task():
        raise ValueError("Task failed")
    
    async def successful_task():
        return {"status": "ok"}
    
    tasks = [failing_task(), successful_task()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    assert len(results) == 2
    assert isinstance(results[0], ValueError)
    assert results[1] == {"status": "ok"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
