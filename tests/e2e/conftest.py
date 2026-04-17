"""
E2E Test Configuration and Fixtures.

Provides shared fixtures for end-to-end agent testing.
"""
import pytest
import pytest_asyncio
import sys
from pathlib import Path

# Add agents to path
agents_path = Path(__file__).parent.parent.parent / ".lingma" / "agents" / "python"
if str(agents_path) not in sys.path:
    sys.path.insert(0, str(agents_path))


class MockRedis:
    """Mock Redis client for E2E testing"""
    
    def __init__(self):
        self.data = {}
        self.published_messages = []
        
    async def get(self, key):
        return self.data.get(key)
    
    async def setex(self, key, ttl, value):
        self.data[key] = value
        
    async def publish(self, channel, message):
        self.published_messages.append({"channel": channel, "message": message})
    
    def pubsub(self):
        return MockPubSub()
    
    async def close(self):
        pass


class MockPubSub:
    """Mock Redis PubSub for E2E testing"""
    
    async def subscribe(self, *channels):
        pass
    
    async def listen(self):
        return
        yield
    
    async def unsubscribe(self):
        pass
    
    async def close(self):
        pass


@pytest_asyncio.fixture
async def mock_redis():
    """Fixture for mocked Redis client"""
    return MockRedis()


@pytest_asyncio.fixture
async def code_review_agent(mock_redis):
    """Fixture for Code Review Agent"""
    from code_review_agent import CodeReviewAgent
    
    agent = CodeReviewAgent.__new__(CodeReviewAgent)
    agent.redis_client = mock_redis
    agent.agent_name = "code_review"
    return agent


@pytest_asyncio.fixture
async def documentation_agent(mock_redis):
    """Fixture for Documentation Agent"""
    from documentation_agent import DocumentationAgent
    
    agent = DocumentationAgent.__new__(DocumentationAgent)
    agent.redis_client = mock_redis
    agent.agent_name = "documentation"
    return agent


@pytest_asyncio.fixture
async def test_runner_agent(mock_redis):
    """Fixture for Test Runner Agent"""
    from test_runner_agent import TestRunnerAgent
    
    agent = TestRunnerAgent.__new__(TestRunnerAgent)
    agent.redis_client = mock_redis
    agent.agent_name = "test_runner"
    return agent


@pytest_asyncio.fixture
async def spec_driven_agent(mock_redis):
    """Fixture for Spec-Driven Core Agent"""
    from spec_driven_core_agent import SpecDrivenCoreAgent
    
    agent = SpecDrivenCoreAgent.__new__(SpecDrivenCoreAgent)
    agent.redis_client = mock_redis
    agent.agent_name = "spec_driven"
    return agent
