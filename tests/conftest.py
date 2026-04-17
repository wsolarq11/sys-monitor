"""
Shared test fixtures for all agent tests.
"""

import pytest
import pytest_asyncio


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

    def pubsub(self):
        return MockPubSub()

    async def close(self):
        pass


class MockPubSub:
    """Mock Redis PubSub for testing"""

    async def subscribe(self, *channels):
        pass

    async def listen(self):
        # Return empty iterator
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
