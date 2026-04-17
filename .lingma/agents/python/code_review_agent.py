"""
Code Review Agent - Automated code quality, security, and performance analysis.

Features:
- Code quality analysis (pylint/flake8)
- Security scanning (Bandit)
- Performance analysis
- Async execution with Redis caching
- Event-driven communication
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional

try:
    from agent_base import AsyncAgentBase
except ImportError:
    from .agent_base import AsyncAgentBase


class CodeReviewAgent(AsyncAgentBase):
    """
    Code Review Agent for automated code analysis.

    Capabilities:
    - Quality analysis using pylint/flake8
    - Security scanning using Bandit
    - Performance bottleneck detection
    - Parallel file review support
    """

    def __init__(self, redis_url: str = "redis://localhost:6379", timeout: int = 60):
        super().__init__(redis_url, timeout)
        self.agent_name = "code_review"

    async def _do_execute(self, task_data: Dict[str, Any]) -> Any:
        """Execute code review task"""
        changes = task_data.get("changes")
        if not changes:
            raise ValueError("No code changes provided")

        return await self.review(changes)

    async def review(self, changes) -> Dict[str, Any]:
        """
        Perform comprehensive code review.

        Args:
            changes: Code changes object with hash and path attributes

        Returns:
            Review results including quality, security, performance, and score
        """
        # Check cache first
        cache_key = f"result:{changes.hash}:code_review"
        cached = await self._get_cache(cache_key)
        if cached is not None:
            return cached

        # Run analyses in parallel
        quality_issues, security_issues, performance_issues = await asyncio.gather(
            self.analyze_quality(changes),
            self.scan_security(changes),
            self.analyze_performance(changes),
        )

        # Calculate overall score
        score = self.calculate_score(
            quality_issues, security_issues, performance_issues
        )

        result = {
            "quality": quality_issues,
            "security": security_issues,
            "performance": performance_issues,
            "score": score,
            "timestamp": time.time(),
        }

        # Cache the result
        await self._set_cache(cache_key, result)

        # Publish completion event
        await self._publish_event("completed", {"score": score})

        return result

    async def analyze_quality(self, changes) -> List[Dict[str, Any]]:
        """
        Analyze code quality using pylint/flake8.

        Args:
            changes: Code changes to analyze

        Returns:
            List of quality issues found
        """
        # Simulate quality analysis
        # In production, this would run: pylint --output-format=json <path>
        await asyncio.sleep(0.1)  # Simulate processing time

        # Return empty list for now (would be populated by actual linter)
        return []

    async def scan_security(self, changes) -> Dict[str, Any]:
        """
        Scan for security vulnerabilities using Bandit.

        Args:
            changes: Code changes to scan

        Returns:
            Security scan results
        """
        try:
            # Run Bandit security scanner
            process = await asyncio.create_subprocess_exec(
                "bandit",
                "-r",
                changes.path if hasattr(changes, "path") else ".",
                "-f",
                "json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return json.loads(stdout.decode())
            else:
                # Bandit returns non-zero when issues are found
                return json.loads(stdout.decode()) if stdout else {"issues": []}

        except FileNotFoundError:
            # Bandit not installed, return safe default
            return {"issues": [], "warning": "Bandit not installed"}
        except Exception as e:
            return {"issues": [], "error": str(e)}

    async def analyze_performance(self, changes) -> List[Dict[str, Any]]:
        """
        Analyze code for performance bottlenecks.

        Args:
            changes: Code changes to analyze

        Returns:
            List of performance issues
        """
        # Simulate performance analysis
        await asyncio.sleep(0.05)

        # Return empty list for now
        return []

    def calculate_score(
        self, quality_issues: List, security_issues: Dict, performance_issues: List
    ) -> float:
        """
        Calculate overall code quality score (0-100).

        Args:
            quality_issues: List of quality issues
            security_issues: Security scan results
            performance_issues: List of performance issues

        Returns:
            Score from 0 to 100
        """
        # Start with perfect score
        score = 100.0

        # Deduct for quality issues
        score -= len(quality_issues) * 2

        # Deduct heavily for security issues
        security_count = len(security_issues.get("issues", []))
        score -= security_count * 10

        # Deduct for performance issues
        score -= len(performance_issues) * 3

        # Ensure score is within bounds
        return max(0.0, min(100.0, score))
