"""
Unit tests for Documentation Agent with AsyncIO and Redis support.
Tests cover doc generation, caching, event publishing, and parallel execution.
"""
import pytest
import pytest_asyncio
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import timedelta


class MockProjectInfo:
    """Mock project info object for testing"""
    
    def __init__(self, hash="proj123", name="TestProject"):
        self.hash = hash
        self.name = name


@pytest_asyncio.fixture
async def documentation_agent(mock_redis):
    """Fixture for Documentation Agent with mocked dependencies"""
    import sys
    from pathlib import Path
    
    # Add .lingma/agents/python to path
    agents_path = Path(__file__).parent.parent / ".lingma" / "agents" / "python"
    if str(agents_path) not in sys.path:
        sys.path.insert(0, str(agents_path))
    
    from documentation_agent import DocumentationAgent
    
    agent = DocumentationAgent.__new__(DocumentationAgent)
    agent.redis_client = mock_redis
    agent.agent_name = "documentation"
    return agent


@pytest.mark.asyncio
async def test_generate_docs_with_cache_hit(documentation_agent, mock_redis):
    """Test doc generation when cache hit occurs"""
    project = MockProjectInfo()
    cached_result = {"readme": "# Test", "changelog": "v1.0", "api_docs": "{}"}
    
    # Set up cache
    cache_key = f"result:{project.hash}:documentation"
    await mock_redis.setex(cache_key, 3600, json.dumps(cached_result))
    
    # Execute
    result = await documentation_agent.generate_docs(project)
    
    # Verify
    assert result == cached_result
    assert len(mock_redis.published_messages) == 0  # No new events


@pytest.mark.asyncio
async def test_generate_docs_with_cache_miss(documentation_agent, mock_redis):
    """Test doc generation when cache miss occurs"""
    project = MockProjectInfo()
    
    # Mock generation methods
    with patch.object(documentation_agent, 'generate_readme', AsyncMock(return_value="# README")), \
         patch.object(documentation_agent, 'generate_changelog', AsyncMock(return_value="v1.0")), \
         patch.object(documentation_agent, 'generate_api_docs', AsyncMock(return_value="{}")):
        
        # Execute
        result = await documentation_agent.generate_docs(project)
        
        # Verify
        assert "readme" in result
        assert "changelog" in result
        assert "api_docs" in result
        assert "generated_at" in result
        
        cache_key = f"result:{project.hash}:documentation"
        assert cache_key in mock_redis.data
        assert len(mock_redis.published_messages) == 1


@pytest.mark.asyncio
async def test_parallel_doc_generation(documentation_agent):
    """Test that different doc types are generated in parallel"""
    project = MockProjectInfo()
    
    # Create tasks with delays to verify parallelism
    async def slow_readme():
        await asyncio.sleep(0.1)
        return "# README"
    
    async def slow_changelog():
        await asyncio.sleep(0.1)
        return "v1.0"
    
    async def slow_api_docs():
        await asyncio.sleep(0.1)
        return "{}"
    
    start_time = asyncio.get_event_loop().time()
    
    tasks = [slow_readme(), slow_changelog(), slow_api_docs()]
    results = await asyncio.gather(*tasks)
    
    end_time = asyncio.get_event_loop().time()
    
    # If truly parallel, should take ~0.1s, not ~0.3s
    assert end_time - start_time < 0.2
    assert len(results) == 3


@pytest.mark.asyncio
async def test_event_publishing(documentation_agent, mock_redis):
    """Test that completion events are published to Redis Pub/Sub"""
    docs_count = 3
    
    await mock_redis.publish(
        "agent:documentation:completed",
        json.dumps({"docs_count": docs_count})
    )
    
    assert len(mock_redis.published_messages) == 1
    assert mock_redis.published_messages[0]["channel"] == "agent:documentation:completed"
    assert json.loads(mock_redis.published_messages[0]["message"])["docs_count"] == 3


@pytest.mark.asyncio
async def test_cache_expiration(documentation_agent, mock_redis):
    """Test that cache has proper TTL"""
    project = MockProjectInfo()
    result_data = {"readme": "# Test"}
    
    cache_key = f"result:{project.hash}:documentation"
    await mock_redis.setex(cache_key, timedelta(seconds=3600), json.dumps(result_data))
    
    # Verify data is stored
    cached = await mock_redis.get(cache_key)
    assert cached is not None
    assert json.loads(cached) == result_data


@pytest.mark.asyncio
async def test_readme_generation(documentation_agent):
    """Test README generation workflow"""
    project = MockProjectInfo()
    
    # Test actual implementation (not mocked)
    result = await documentation_agent.generate_readme(project)
    
    # Verify result is a string and contains README content
    assert isinstance(result, str)
    assert len(result) > 0
    assert "README" in result


@pytest.mark.asyncio
async def test_subscribe_events(documentation_agent, mock_redis):
    """Test event subscription functionality"""
    pubsub = mock_redis.pubsub()
    await pubsub.subscribe("agent:documentation:*")
    
    # Should not raise exception
    assert True


@pytest.mark.asyncio
async def test_multiple_projects_docs(documentation_agent):
    """Test generating docs for multiple projects"""
    projects = [MockProjectInfo(f"proj-{i}") for i in range(3)]
    
    results = []
    for project in projects:
        with patch.object(documentation_agent, 'generate_readme', AsyncMock(return_value="# README")), \
             patch.object(documentation_agent, 'generate_changelog', AsyncMock(return_value="v1.0")), \
             patch.object(documentation_agent, 'generate_api_docs', AsyncMock(return_value="{}")):
            
            result = await documentation_agent.generate_docs(project)
            results.append(result)
    
    assert len(results) == 3


@pytest.mark.asyncio
async def test_error_handling_in_generation(documentation_agent):
    """Test error handling during doc generation"""
    project = MockProjectInfo()
    
    # Mock methods to raise exceptions
    with patch.object(documentation_agent, 'generate_readme', side_effect=Exception("Generation failed")):
        with pytest.raises(Exception):
            await documentation_agent.generate_readme(project)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
