"""
Documentation Agent - Automated documentation generation.

Features:
- README generation
- CHANGELOG generation from Git history
- API documentation extraction
- Async parallel doc generation with Redis caching
- Event-driven communication
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict

try:
    from agent_base import AsyncAgentBase
except ImportError:
    from .agent_base import AsyncAgentBase


class DocumentationAgent(AsyncAgentBase):
    """
    Documentation Agent for automated doc generation.

    Capabilities:
    - README generation from project structure
    - CHANGELOG generation from Git commits
    - API documentation extraction from code
    - Parallel doc type generation
    """

    def __init__(self, redis_url: str = "redis://localhost:6379", timeout: int = 60):
        super().__init__(redis_url, timeout)
        self.agent_name = "documentation"

    async def _do_execute(self, task_data: Dict[str, Any]) -> Any:
        """Execute documentation generation task"""
        project = task_data.get("project")
        if not project:
            raise ValueError("No project info provided")

        return await self.generate_docs(project)

    async def generate_docs(self, project) -> Dict[str, Any]:
        """
        Generate comprehensive documentation for a project.

        Args:
            project: Project info object with hash attribute

        Returns:
            Generated documentation including readme, changelog, api_docs
        """
        # Check cache first
        cache_key = f"result:{project.hash}:documentation"
        cached = await self._get_cache(cache_key)
        if cached is not None:
            return cached

        # Generate different doc types in parallel
        readme, changelog, api_docs = await asyncio.gather(
            self.generate_readme(project),
            self.generate_changelog(project),
            self.generate_api_docs(project),
        )

        result = {
            "readme": readme,
            "changelog": changelog,
            "api_docs": api_docs,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

        # Cache the result
        await self._set_cache(cache_key, result)

        # Publish completion event
        await self._publish_event(
            "completed", {"doc_types": ["readme", "changelog", "api_docs"]}
        )

        return result

    async def generate_readme(self, project) -> str:
        """
        Generate README.md from project structure.

        Args:
            project: Project info

        Returns:
            Generated README content
        """
        # Simulate README generation
        await asyncio.sleep(0.1)

        return "# Project README\n\nAuto-generated documentation."

    async def generate_changelog(self, project) -> str:
        """
        Generate CHANGELOG.md from Git history.

        Args:
            project: Project info

        Returns:
            Generated CHANGELOG content
        """
        try:
            # Try to get Git log
            process = await asyncio.create_subprocess_exec(
                "git",
                "log",
                "--oneline",
                "--no-merges",
                "-20",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                commits = stdout.decode().strip().split("\n")
                changelog = "# Changelog\n\n"
                for commit in commits[:10]:
                    changelog += f"- {commit}\n"
                return changelog
            else:
                return "# Changelog\n\nNo Git history available."

        except FileNotFoundError:
            return "# Changelog\n\nGit not installed."
        except Exception as e:
            return f"# Changelog\n\nError: {str(e)}"

    async def generate_api_docs(self, project) -> str:
        """
        Extract API documentation from code.

        Args:
            project: Project info

        Returns:
            Generated API documentation (JSON format)
        """
        # Simulate API doc extraction
        await asyncio.sleep(0.05)

        return json.dumps(
            {"endpoints": [], "generated_at": datetime.utcnow().isoformat() + "Z"}
        )

    async def read_template_async(self, template_name: str) -> str:
        """
        Read a documentation template.

        Args:
            template_name: Template name

        Returns:
            Template content
        """
        await asyncio.sleep(0.01)
        return f"Template: {template_name}"

    async def fill_template_async(self, template: str, data: Dict[str, Any]) -> str:
        """
        Fill a template with data.

        Args:
            template: Template string
            data: Data to fill

        Returns:
            Filled template
        """
        await asyncio.sleep(0.01)
        return f"Filled: {template}"

    async def write_file_async(self, filepath: str, content: str):
        """
        Write content to file asynchronously.

        Args:
            filepath: File path
            content: Content to write
        """
        await asyncio.sleep(0.01)
        # In production, this would write to filesystem
        pass
