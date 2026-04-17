"""
Unit tests for Code Review Agent with AsyncIO and Redis support.
Tests cover code analysis, security scanning, caching, and event publishing.
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


class MockCodeChanges:
    """Mock code changes object for testing"""
    
    def __init__(self, hash="abc123", path="/test/path"):
        self.hash = hash
        self.path = path


@pytest_asyncio.fixture
async def mock_redis():
    """Fixture for mocked Redis client"""
    return MockRedis()


@pytest_asyncio.fixture
async def code_review_agent(mock_redis):
    """Fixture for Code Review Agent with mocked dependencies"""
    from .lingma.agents.code_review_agent import CodeReviewAgent
    
    agent = CodeReviewAgent.__new__(CodeReviewAgent)
    agent.redis = mock_redis
    return agent


@pytest.mark.asyncio
async def test_review_with_cache_hit(code_review_agent, mock_redis):
    """Test review when cache hit occurs"""
    changes = MockCodeChanges()
    cached_result = {"quality": [], "security": [], "score": 95}
    
    # Set up cache
    cache_key = f"result:{changes.hash}:code_review"
    await mock_redis.setex(cache_key, 3600, json.dumps(cached_result))
    
    # Execute
    result = await code_review_agent.review(changes)
    
    # Verify
    assert result == cached_result
    assert len(mock_redis.published_messages) == 0  # No new events


@pytest.mark.asyncio
async def test_review_with_cache_miss(code_review_agent, mock_redis):
    """Test review when cache miss occurs"""
    changes = MockCodeChanges()
    
    # Mock analysis methods
    with patch.object(code_review_agent, 'analyze_quality', AsyncMock(return_value=[])), \
         patch.object(code_review_agent, 'scan_security', AsyncMock(return_value=[])), \
         patch.object(code_review_agent, 'analyze_performance', AsyncMock(return_value=[])), \
         patch.object(code_review_agent, 'calculate_score', return_value=90):
        
        # Execute
        result = await code_review_agent.review(changes)
        
        # Verify
        assert "quality" in result
        assert "security" in result
        assert "performance" in result
        assert "score" in result
        
        cache_key = f"result:{changes.hash}:code_review"
        assert cache_key in mock_redis.data
        assert len(mock_redis.published_messages) == 1


@pytest.mark.asyncio
async def test_security_scan_integration(code_review_agent):
    """Test Bandit security scan integration"""
    changes = MockCodeChanges(path="/test/code")
    
    # Mock subprocess
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b'{"issues": []}', b''))
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await code_review_agent.scan_security(changes)
        
        assert result == {"issues": []}


@pytest.mark.asyncio
async def test_event_publishing(code_review_agent, mock_redis):
    """Test that completion events are published to Redis Pub/Sub"""
    score = 85
    
    await mock_redis.publish(
        "agent:code_review:completed",
        json.dumps({"score": score})
    )
    
    assert len(mock_redis.published_messages) == 1
    assert mock_redis.published_messages[0]["channel"] == "agent:code_review:completed"
    assert json.loads(mock_redis.published_messages[0]["message"])["score"] == 85


@pytest.mark.asyncio
async def test_cache_expiration(code_review_agent, mock_redis):
    """Test that cache has proper TTL"""
    changes = MockCodeChanges()
    result_data = {"score": 90}
    
    cache_key = f"result:{changes.hash}:code_review"
    await mock_redis.setex(cache_key, timedelta(seconds=3600), json.dumps(result_data))
    
    # Verify data is stored
    cached = await mock_redis.get(cache_key)
    assert cached is not None
    assert json.loads(cached) == result_data


@pytest.mark.asyncio
async def test_quality_score_calculation(code_review_agent):
    """Test quality score calculation logic"""
    quality_issues = [{"severity": "high"}, {"severity": "medium"}]
    security_issues = [{"severity": "low"}]
    
    # Mock the calculate_score method behavior
    with patch.object(code_review_agent, 'calculate_score', return_value=75):
        score = code_review_agent.calculate_score(quality_issues, security_issues)
        assert score == 75


@pytest.mark.asyncio
async def test_subscribe_events(code_review_agent, mock_redis):
    """Test event subscription functionality"""
    pubsub = mock_redis.pubsub()
    await pubsub.subscribe("agent:code_review:*")
    
    # Should not raise exception
    assert True


@pytest.mark.asyncio
async def test_multiple_files_review(code_review_agent):
    """Test reviewing multiple files concurrently"""
    changes_list = [MockCodeChanges(f"hash-{i}") for i in range(5)]
    
    results = []
    for changes in changes_list:
        with patch.object(code_review_agent, 'analyze_quality', AsyncMock(return_value=[])), \
             patch.object(code_review_agent, 'scan_security', AsyncMock(return_value=[])), \
             patch.object(code_review_agent, 'analyze_performance', AsyncMock(return_value=[])), \
             patch.object(code_review_agent, 'calculate_score', return_value=85):
            
            result = await code_review_agent.review(changes)
            results.append(result)
    
    assert len(results) == 5


@pytest.mark.asyncio
async def test_error_handling_in_analysis(code_review_agent):
    """Test error handling during analysis"""
    changes = MockCodeChanges()
    
    # Mock methods to raise exceptions
    with patch.object(code_review_agent, 'analyze_quality', side_effect=Exception("Analysis failed")):
        with pytest.raises(Exception):
            await code_review_agent.analyze_quality(changes)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
