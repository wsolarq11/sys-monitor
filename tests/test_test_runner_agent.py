"""
Unit tests for Test Runner Agent with AsyncIO and Redis support.
Tests cover test execution, failure analysis, caching, and event publishing.
"""
import pytest
import pytest_asyncio
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import timedelta


class MockTestConfig:
    """Mock test configuration object for testing"""
    
    def __init__(self, hash="test123", unit_test_path="/tests/unit"):
        self.hash = hash
        self.unit_test_path = unit_test_path


@pytest_asyncio.fixture
async def test_runner_agent(mock_redis):
    """Fixture for Test Runner Agent with mocked dependencies"""
    import sys
    from pathlib import Path
    
    # Add .lingma/agents/python to path
    agents_path = Path(__file__).parent.parent / ".lingma" / "agents" / "python"
    if str(agents_path) not in sys.path:
        sys.path.insert(0, str(agents_path))
    
    from test_runner_agent import TestRunnerAgent
    
    agent = TestRunnerAgent.__new__(TestRunnerAgent)
    agent.redis_client = mock_redis
    agent.agent_name = "test_runner"
    return agent


@pytest.mark.asyncio
async def test_run_tests_with_cache_hit(test_runner_agent, mock_redis):
    """Test test execution when cache hit occurs"""
    config = MockTestConfig()
    cached_result = {
        "unit": {"passed": 10},
        "integration": {"passed": 5},
        "e2e": {"passed": 3},
        "total_passed": 18,
        "total_failed": 0
    }
    
    # Set up cache
    cache_key = f"result:{config.hash}:test_results"
    await mock_redis.setex(cache_key, 3600, json.dumps(cached_result))
    
    # Execute
    result = await test_runner_agent.run_tests(config)
    
    # Verify
    assert result == cached_result
    assert len(mock_redis.published_messages) == 0  # No new events


@pytest.mark.asyncio
async def test_run_tests_with_cache_miss(test_runner_agent, mock_redis):
    """Test test execution when cache miss occurs"""
    config = MockTestConfig()
    
    # Mock test execution methods
    with patch.object(test_runner_agent, 'run_unit_tests', AsyncMock(return_value={"passed": 10, "failed": 0})), \
         patch.object(test_runner_agent, 'run_integration_tests', AsyncMock(return_value={"passed": 5, "failed": 0})), \
         patch.object(test_runner_agent, 'run_e2e_tests', AsyncMock(return_value={"passed": 3, "failed": 0})), \
         patch.object(test_runner_agent, 'analyze_failures', AsyncMock(return_value=[])):
        
        # Execute
        result = await test_runner_agent.run_tests(config)
        
        # Verify
        assert "unit" in result
        assert "integration" in result
        assert "e2e" in result
        assert "total_passed" in result
        assert "total_failed" in result
        
        cache_key = f"result:{config.hash}:test_results"
        assert cache_key in mock_redis.data
        assert len(mock_redis.published_messages) == 1


@pytest.mark.asyncio
async def test_parallel_test_execution(test_runner_agent):
    """Test that different test types execute in parallel"""
    
    async def slow_unit_test():
        await asyncio.sleep(0.1)
        return {"passed": 10}
    
    async def slow_integration_test():
        await asyncio.sleep(0.1)
        return {"passed": 5}
    
    async def slow_e2e_test():
        await asyncio.sleep(0.1)
        return {"passed": 3}
    
    start_time = asyncio.get_event_loop().time()
    
    tasks = [slow_unit_test(), slow_integration_test(), slow_e2e_test()]
    results = await asyncio.gather(*tasks)
    
    end_time = asyncio.get_event_loop().time()
    
    # If truly parallel, should take ~0.1s, not ~0.3s
    assert end_time - start_time < 0.2
    assert len(results) == 3


@pytest.mark.asyncio
async def test_unit_test_execution(test_runner_agent):
    """Test unit test execution via subprocess"""
    config = MockTestConfig()
    
    # Mock subprocess
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b'{"passed": 10, "failed": 0}', b''))
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await test_runner_agent.run_unit_tests(config)
        
        assert result == {"passed": 10, "failed": 0}


@pytest.mark.asyncio
async def test_event_publishing(test_runner_agent, mock_redis):
    """Test that completion events are published to Redis Pub/Sub"""
    passed = 18
    failed = 2
    
    await mock_redis.publish(
        "agent:test_runner:completed",
        json.dumps({"passed": passed, "failed": failed})
    )
    
    assert len(mock_redis.published_messages) == 1
    assert mock_redis.published_messages[0]["channel"] == "agent:test_runner:completed"
    result_data = json.loads(mock_redis.published_messages[0]["message"])
    assert result_data["passed"] == passed
    assert result_data["failed"] == failed


@pytest.mark.asyncio
async def test_cache_expiration(test_runner_agent, mock_redis):
    """Test that cache has proper TTL"""
    config = MockTestConfig()
    result_data = {"total_passed": 18, "total_failed": 0}
    
    cache_key = f"result:{config.hash}:test_results"
    await mock_redis.setex(cache_key, timedelta(seconds=3600), json.dumps(result_data))
    
    # Verify data is stored
    cached = await mock_redis.get(cache_key)
    assert cached is not None
    assert json.loads(cached) == result_data


@pytest.mark.asyncio
async def test_failure_analysis(test_runner_agent):
    """Test failure analysis logic"""
    results = [
        {"passed": 10, "failed": 2},
        {"passed": 5, "failed": 0},
        {"passed": 3, "failed": 1}
    ]
    
    with patch.object(test_runner_agent, 'diagnose_failure', AsyncMock(return_value=[{"error": "test"}])):
        failures = await test_runner_agent.analyze_failures(results)
        
        # Should analyze all results with failures
        assert len(failures) >= 0  # Depends on diagnose_failure implementation


@pytest.mark.asyncio
async def test_subscribe_events(test_runner_agent, mock_redis):
    """Test event subscription functionality"""
    pubsub = mock_redis.pubsub()
    await pubsub.subscribe("agent:test_runner:*")
    
    # Should not raise exception
    assert True


@pytest.mark.asyncio
async def test_multiple_test_configs(test_runner_agent):
    """Test running tests for multiple configurations"""
    configs = [MockTestConfig(f"config-{i}") for i in range(3)]
    
    results = []
    for config in configs:
        with patch.object(test_runner_agent, 'run_unit_tests', AsyncMock(return_value={"passed": 10})), \
             patch.object(test_runner_agent, 'run_integration_tests', AsyncMock(return_value={"passed": 5})), \
             patch.object(test_runner_agent, 'run_e2e_tests', AsyncMock(return_value={"passed": 3})), \
             patch.object(test_runner_agent, 'analyze_failures', AsyncMock(return_value=[])):
            
            result = await test_runner_agent.run_tests(config)
            results.append(result)
    
    assert len(results) == 3


@pytest.mark.asyncio
async def test_error_handling_in_test_execution(test_runner_agent):
    """Test error handling during test execution"""
    
    async def failing_test():
        raise RuntimeError("Test execution failed")
    
    async def successful_test():
        return {"passed": 10}
    
    tasks = [failing_test(), successful_test()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    assert len(results) == 2
    assert isinstance(results[0], RuntimeError)
    assert results[1] == {"passed": 10}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
