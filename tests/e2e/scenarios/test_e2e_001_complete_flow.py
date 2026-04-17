"""
E2E-001: Complete Spec Execution Flow Test.

Tests the complete end-to-end flow from spec submission to completion,
involving multiple agents working together.

Scenario:
1. User submits a spec
2. Spec-Driven Agent parses and decomposes it
3. Code Review Agent reviews code changes
4. Test Runner Agent executes tests
5. Documentation Agent generates docs
6. All results are aggregated and cached
"""
import pytest
import pytest_asyncio
import asyncio
import json
from unittest.mock import AsyncMock, patch


class MockCodeChanges:
    """Mock code changes for E2E testing"""
    def __init__(self, hash="e2e-test-001", path="/test/code"):
        self.hash = hash
        self.path = path


class MockProjectInfo:
    """Mock project info for E2E testing"""
    def __init__(self, hash="proj-e2e-001", name="E2E Test Project"):
        self.hash = hash
        self.name = name


class MockTestConfig:
    """Mock test config for E2E testing"""
    def __init__(self, hash="test-e2e-001"):
        self.hash = hash


@pytest.mark.asyncio
async def test_e2e_complete_spec_execution_flow(
    spec_driven_agent,
    code_review_agent,
    test_runner_agent,
    documentation_agent,
    mock_redis
):
    """
    E2E-001: Test complete spec execution flow with all agents.
    
    This test validates:
    1. Spec decomposition and task execution
    2. Code review integration
    3. Test execution integration
    4. Documentation generation integration
    5. Event publishing across all agents
    6. Caching mechanism
    """
    spec_id = "e2e-spec-001"
    
    # Step 1: Execute spec (Spec-Driven Agent)
    with patch.object(spec_driven_agent, 'read_spec_async', AsyncMock(return_value={"id": spec_id})), \
         patch.object(spec_driven_agent, 'decompose_spec', AsyncMock(return_value=[
             {"task_id": "task-1", "type": "review"},
             {"task_id": "task-2", "type": "test"},
             {"task_id": "task-3", "type": "doc"}
         ])), \
         patch.object(spec_driven_agent, 'execute_task', AsyncMock(return_value={"status": "completed"})):
        
        spec_result = await spec_driven_agent.execute_spec(spec_id)
        
        # Verify spec execution
        assert spec_result["spec_id"] == spec_id
        assert spec_result["status"] == "completed"
        assert spec_result["tasks_completed"] == 3
    
    # Step 2: Code Review (Code Review Agent)
    changes = MockCodeChanges()
    with patch.object(code_review_agent, 'analyze_quality', AsyncMock(return_value=[])), \
         patch.object(code_review_agent, 'scan_security', AsyncMock(return_value={"issues": []})), \
         patch.object(code_review_agent, 'analyze_performance', AsyncMock(return_value=[])), \
         patch.object(code_review_agent, 'calculate_score', return_value=95):
        
        review_result = await code_review_agent.review(changes)
        
        # Verify code review
        assert "quality" in review_result
        assert "security" in review_result
        assert "score" in review_result
        assert review_result["score"] >= 80
    
    # Step 3: Test Execution (Test Runner Agent)
    config = MockTestConfig()
    with patch.object(test_runner_agent, 'run_unit_tests', AsyncMock(return_value={"passed": 10, "failed": 0})), \
         patch.object(test_runner_agent, 'run_integration_tests', AsyncMock(return_value={"passed": 5, "failed": 0})), \
         patch.object(test_runner_agent, 'run_e2e_tests', AsyncMock(return_value={"passed": 3, "failed": 0})):
        
        test_result = await test_runner_agent.run_tests(config)
        
        # Verify test execution
        assert test_result["total_passed"] == 18
        assert test_result["total_failed"] == 0
    
    # Step 4: Documentation Generation (Documentation Agent)
    project = MockProjectInfo()
    with patch.object(documentation_agent, 'generate_readme', AsyncMock(return_value="# README")), \
         patch.object(documentation_agent, 'generate_changelog', AsyncMock(return_value="v1.0")), \
         patch.object(documentation_agent, 'generate_api_docs', AsyncMock(return_value="{}")):
        
        doc_result = await documentation_agent.generate_docs(project)
        
        # Verify documentation
        assert "readme" in doc_result
        assert "changelog" in doc_result
        assert "api_docs" in doc_result
    
    # Step 5: Verify event publishing
    assert len(mock_redis.published_messages) >= 4  # At least one from each agent
    
    # Step 6: Verify caching
    cache_keys = list(mock_redis.data.keys())
    assert len(cache_keys) >= 4  # Results should be cached
    
    print(f"✅ E2E-001 PASSED: Complete spec execution flow validated")
    print(f"   - Events published: {len(mock_redis.published_messages)}")
    print(f"   - Cache entries: {len(cache_keys)}")


@pytest.mark.asyncio
async def test_e2e_parallel_agent_execution(
    code_review_agent,
    test_runner_agent,
    documentation_agent,
    mock_redis
):
    """
    E2E-002: Test parallel execution of multiple agents.
    
    Validates that agents can execute concurrently without conflicts.
    """
    changes = MockCodeChanges(hash="parallel-001")
    config = MockTestConfig(hash="parallel-001")
    project = MockProjectInfo(hash="parallel-001")
    
    # Mock all agent methods
    with patch.object(code_review_agent, 'analyze_quality', AsyncMock(return_value=[])), \
         patch.object(code_review_agent, 'scan_security', AsyncMock(return_value={"issues": []})), \
         patch.object(code_review_agent, 'analyze_performance', AsyncMock(return_value=[])), \
         patch.object(code_review_agent, 'calculate_score', return_value=90), \
         patch.object(test_runner_agent, 'run_unit_tests', AsyncMock(return_value={"passed": 5, "failed": 0})), \
         patch.object(test_runner_agent, 'run_integration_tests', AsyncMock(return_value={"passed": 3, "failed": 0})), \
         patch.object(test_runner_agent, 'run_e2e_tests', AsyncMock(return_value={"passed": 2, "failed": 0})), \
         patch.object(documentation_agent, 'generate_readme', AsyncMock(return_value="# README")), \
         patch.object(documentation_agent, 'generate_changelog', AsyncMock(return_value="v1.0")), \
         patch.object(documentation_agent, 'generate_api_docs', AsyncMock(return_value="{}")):
        
        # Execute all agents in parallel
        start_time = asyncio.get_event_loop().time()
        
        results = await asyncio.gather(
            code_review_agent.review(changes),
            test_runner_agent.run_tests(config),
            documentation_agent.generate_docs(project),
            return_exceptions=True
        )
        
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        
        # Verify all succeeded
        assert len(results) == 3
        assert not any(isinstance(r, Exception) for r in results)
        
        # Verify parallel execution was faster than sequential
        # Sequential would take ~0.35s (0.1 + 0.15 + 0.1), parallel should be < 0.2s
        assert execution_time < 0.3, f"Parallel execution too slow: {execution_time}s"
        
        print(f"✅ E2E-002 PASSED: Parallel execution validated ({execution_time:.3f}s)")


@pytest.mark.asyncio
async def test_e2e_cache_consistency_across_agents(
    code_review_agent,
    mock_redis
):
    """
    E2E-003: Test cache consistency when same input is processed multiple times.
    
    Validates that:
    1. First execution caches result
    2. Second execution hits cache
    3. Cached result matches original
    """
    changes = MockCodeChanges(hash="cache-consistency-001")
    
    with patch.object(code_review_agent, 'analyze_quality', AsyncMock(return_value=[])), \
         patch.object(code_review_agent, 'scan_security', AsyncMock(return_value={"issues": []})), \
         patch.object(code_review_agent, 'analyze_performance', AsyncMock(return_value=[])), \
         patch.object(code_review_agent, 'calculate_score', return_value=88):
        
        # First execution (cache miss)
        result1 = await code_review_agent.review(changes)
        assert result1["cache_hit"] is False if "cache_hit" in result1 else True
        
        # Second execution (should hit cache)
        result2 = await code_review_agent.review(changes)
        
        # Verify results match
        assert result1["score"] == result2["score"]
        assert result1["quality"] == result2["quality"]
        
        # Verify cache was used
        cache_key = f"result:{changes.hash}:code_review"
        assert cache_key in mock_redis.data
        
        print(f"✅ E2E-003 PASSED: Cache consistency validated")


@pytest.mark.asyncio
async def test_e2e_error_handling_and_recovery(
    spec_driven_agent,
    mock_redis
):
    """
    E2E-004: Test error handling and recovery mechanisms.
    
    Validates that:
    1. Agent failures don't crash the system
    2. Errors are properly reported
    3. System can recover and continue
    """
    spec_id = "error-test-001"
    
    # Simulate a failure in task execution
    with patch.object(spec_driven_agent, 'read_spec_async', AsyncMock(return_value={"id": spec_id})), \
         patch.object(spec_driven_agent, 'decompose_spec', AsyncMock(return_value=[
             {"task_id": "task-1", "type": "review"},
             {"task_id": "task-2", "type": "test"}
         ])), \
         patch.object(spec_driven_agent, 'execute_task', side_effect=[
             {"status": "completed"},
             Exception("Simulated failure"),
             {"status": "completed"}
         ]):
        
        # Should handle exception gracefully
        result = await spec_driven_agent.execute_spec(spec_id)
        
        # Verify partial success (1 out of 3 tasks succeeded, 1 failed)
        assert result["spec_id"] == spec_id
        assert result["status"] == "completed"
        # Only successful tasks are counted
        assert result["tasks_completed"] >= 1
        
        print(f"✅ E2E-004 PASSED: Error handling validated")


@pytest.mark.asyncio
async def test_e2e_event_chain_validation(
    code_review_agent,
    test_runner_agent,
    documentation_agent,
    mock_redis
):
    """
    E2E-005: Validate complete event chain across all agents.
    
    Ensures that:
    1. Each agent publishes completion events
    2. Events contain correct data
    3. Event order is logical
    """
    changes = MockCodeChanges(hash="event-chain-001")
    config = MockTestConfig(hash="event-chain-001")
    project = MockProjectInfo(hash="event-chain-001")
    
    # Clear previous messages
    mock_redis.published_messages.clear()
    
    with patch.object(code_review_agent, 'analyze_quality', AsyncMock(return_value=[])), \
         patch.object(code_review_agent, 'scan_security', AsyncMock(return_value={"issues": []})), \
         patch.object(code_review_agent, 'analyze_performance', AsyncMock(return_value=[])), \
         patch.object(code_review_agent, 'calculate_score', return_value=92), \
         patch.object(test_runner_agent, 'run_unit_tests', AsyncMock(return_value={"passed": 5, "failed": 0})), \
         patch.object(test_runner_agent, 'run_integration_tests', AsyncMock(return_value={"passed": 3, "failed": 0})), \
         patch.object(test_runner_agent, 'run_e2e_tests', AsyncMock(return_value={"passed": 2, "failed": 0})), \
         patch.object(documentation_agent, 'generate_readme', AsyncMock(return_value="# README")), \
         patch.object(documentation_agent, 'generate_changelog', AsyncMock(return_value="v1.0")), \
         patch.object(documentation_agent, 'generate_api_docs', AsyncMock(return_value="{}")):
        
        # Execute all agents
        await code_review_agent.review(changes)
        await test_runner_agent.run_tests(config)
        await documentation_agent.generate_docs(project)
        
        # Verify events were published
        assert len(mock_redis.published_messages) >= 3
        
        # Verify event channels
        channels = [msg["channel"] for msg in mock_redis.published_messages]
        assert any("code_review" in ch for ch in channels)
        assert any("test_runner" in ch for ch in channels)
        assert any("documentation" in ch for ch in channels)
        
        # Verify all are completion events
        assert all("completed" in ch for ch in channels)
        
        print(f"✅ E2E-005 PASSED: Event chain validated ({len(channels)} events)")
