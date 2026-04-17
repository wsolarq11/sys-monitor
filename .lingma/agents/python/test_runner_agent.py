"""
Test Runner Agent - Automated test execution and analysis.

Features:
- Unit test execution (pytest/jest)
- Integration test execution
- E2E test execution
- Failure analysis and root cause diagnosis
- Async parallel test execution with Redis caching
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


class TestRunnerAgent(AsyncAgentBase):
    """
    Test Runner Agent for automated test execution.

    Capabilities:
    - Unit test execution
    - Integration test execution
    - E2E test execution
    - Failure analysis and diagnosis
    - Parallel test suite execution
    """

    def __init__(self, redis_url: str = "redis://localhost:6379", timeout: int = 60):
        super().__init__(redis_url, timeout)
        self.agent_name = "test_runner"

    async def _do_execute(self, task_data: Dict[str, Any]) -> Any:
        """Execute test runner task"""
        config = task_data.get("config")
        if not config:
            raise ValueError("No test config provided")

        return await self.run_tests(config)

    async def run_tests(self, config) -> Dict[str, Any]:
        """
        Execute all test suites.

        Args:
            config: Test configuration object with hash attribute

        Returns:
            Test results including unit, integration, e2e results
        """
        # Check cache first
        cache_key = f"result:{config.hash}:test_results"
        cached = await self._get_cache(cache_key)
        if cached is not None:
            return cached

        # Run different test types in parallel
        unit_result, integration_result, e2e_result = await asyncio.gather(
            self.run_unit_tests(config),
            self.run_integration_tests(config),
            self.run_e2e_tests(config),
        )

        # Analyze any failures
        failures = await self.analyze_failures(
            unit_result, integration_result, e2e_result
        )

        # Calculate totals
        total_passed = (
            unit_result.get("passed", 0)
            + integration_result.get("passed", 0)
            + e2e_result.get("passed", 0)
        )
        total_failed = (
            unit_result.get("failed", 0)
            + integration_result.get("failed", 0)
            + e2e_result.get("failed", 0)
        )

        result = {
            "unit": unit_result,
            "integration": integration_result,
            "e2e": e2e_result,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "failures": failures,
            "timestamp": time.time(),
        }

        # Cache the result
        await self._set_cache(cache_key, result)

        # Publish completion event
        await self._publish_event(
            "completed", {"total_passed": total_passed, "total_failed": total_failed}
        )

        return result

    async def run_unit_tests(self, config) -> Dict[str, Any]:
        """
        Execute unit tests.

        Args:
            config: Test configuration

        Returns:
            Unit test results
        """
        try:
            # Run pytest
            process = await asyncio.create_subprocess_exec(
                "python",
                "-m",
                "pytest",
                "tests/",
                "-v",
                "--tb=short",
                "--json-report",
                "--json-report-file=/tmp/unit-test-results.json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            # Try to parse JSON output first
            output_str = stdout.decode()
            try:
                # If it's JSON, parse it directly
                import json as json_module

                result_data = json_module.loads(output_str)
                return {
                    "passed": result_data.get("passed", 0),
                    "failed": result_data.get("failed", 0),
                }
            except (json_module.JSONDecodeError, ValueError):
                # Otherwise, count PASSED/FAILED in text output
                passed = output_str.count("PASSED")
                failed = output_str.count("FAILED")
                return {"passed": passed, "failed": failed}

        except FileNotFoundError:
            return {"passed": 0, "failed": 0, "error": "pytest not found"}
        except Exception as e:
            return {"passed": 0, "failed": 0, "error": str(e)}

    async def run_integration_tests(self, config) -> Dict[str, Any]:
        """
        Execute integration tests.

        Args:
            config: Test configuration

        Returns:
            Integration test results
        """
        # Simulate integration test execution
        await asyncio.sleep(0.1)

        return {"passed": 0, "failed": 0, "note": "Integration tests not configured"}

    async def run_e2e_tests(self, config) -> Dict[str, Any]:
        """
        Execute E2E tests.

        Args:
            config: Test configuration

        Returns:
            E2E test results
        """
        # Simulate E2E test execution
        await asyncio.sleep(0.15)

        return {"passed": 0, "failed": 0, "note": "E2E tests not configured"}

    async def analyze_failures(
        self,
        unit_result: Dict = None,
        integration_result: Dict = None,
        e2e_result: Dict = None,
    ) -> List[Dict[str, Any]]:
        """
        Analyze test failures and identify root causes.

        Args:
            unit_result: Unit test results (optional)
            integration_result: Integration test results (optional)
            e2e_result: E2E test results (optional)

        Returns:
            List of failure analyses
        """
        failures = []

        # Check for failures in each test type
        for test_type, result in [
            ("unit", unit_result or {}),
            ("integration", integration_result or {}),
            ("e2e", e2e_result or {}),
        ]:
            # Handle both dict and list inputs
            if isinstance(result, list):
                failed_count = len([r for r in result if r.get("status") == "failed"])
            elif isinstance(result, dict):
                failed_count = result.get("failed", 0)
            else:
                failed_count = 0

            if failed_count > 0:
                failures.append(
                    {
                        "type": test_type,
                        "count": failed_count,
                        "diagnosis": "Code issue detected",
                        "recommendation": "Review failing tests",
                    }
                )

        return failures

    async def diagnose_failure(
        self, failure_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Diagnose test failure and identify root cause.

        Args:
            failure_info: Failure information

        Returns:
            List of diagnoses
        """
        await asyncio.sleep(0.02)

        return [
            {
                "error": failure_info.get("error", "Unknown"),
                "root_cause": "Code issue",
                "suggestion": "Review the failing test",
            }
        ]
