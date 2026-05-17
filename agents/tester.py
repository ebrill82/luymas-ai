"""
LUYMAS TESTER — Testing Agent

The Tester generates and executes unit tests, integration tests, and E2E tests
using Playwright for browser testing. It captures bug screenshots and E2E test
videos, providing comprehensive test coverage and visual evidence of failures.

Skills: test-generation, bug-capture, e2e-testing
"""

from typing import Optional, List, Dict, Any
import json
import logging
from datetime import datetime, timezone

from agents.base import BaseAgent, AgentStatus, AgentMessage


class TesterAgent(BaseAgent):
    """
    LUYMAS TESTER — Testing Agent.

    Responsibilities:
    - Generate and execute unit tests (Vitest/pytest)
    - Generate and execute integration tests
    - E2E testing with Playwright
    - Capture bug screenshots on failure
    - Record E2E test videos
    - Track test coverage and report gaps
    - Notify Coder agents of bugs with visual evidence

    Skills: test-generation, bug-capture, e2e-testing
    """

    SYSTEM_PROMPT: str = (
        "You are LUYMAS TESTER, the quality assurance engineer of the Luymas AI system. "
        "You write comprehensive tests at every level: unit, integration, and E2E. You "
        "use Playwright for browser testing and capture screenshots of bugs and videos "
        "of E2E test runs. You believe that untested code is broken code. You aim for "
        "high coverage but prioritize meaningful tests over percentage metrics."
    )

    # Test frameworks by language
    TEST_FRAMEWORKS: Dict[str, Dict[str, str]] = {
        "python": {"unit": "pytest", "e2e": "Playwright", "coverage": "pytest-cov"},
        "typescript": {"unit": "Vitest", "e2e": "Playwright", "coverage": "Vitest coverage"},
    }

    # Standard test categories
    TEST_CATEGORIES: List[str] = [
        "unit", "integration", "e2e", "snapshot", "accessibility", "performance",
    ]

    def __init__(
        self,
        name: str = "LUYMAS TESTER",
        role: str = "QA Engineer",
        email: str = "tester@luymas.ai",
        model: str = "gpt-4o",
    ):
        super().__init__(name=name, role=role, email=email, model=model)
        self.skills = ["test-generation", "bug-capture", "e2e-testing"]
        self._test_suites: Dict[str, Dict[str, Any]] = {}
        self._bug_reports: List[Dict[str, Any]] = []
        self._coverage_reports: Dict[str, Dict[str, Any]] = {}
        self._e2e_videos: Dict[str, str] = {}
        self._screenshots: Dict[str, str] = {}
        self._playwright_config: Dict[str, Any] = {}
        self.logger.info("Tester Agent initialized — quality assurance ready")

    # ------------------------------------------------------------------
    # Core message processing
    # ------------------------------------------------------------------

    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Route incoming messages to the appropriate Tester handler."""
        self.status = AgentStatus.WORKING
        try:
            msg_type = message.message_type

            if msg_type == "test_request":
                return await self._handle_test_request(message)
            elif msg_type == "e2e_test_request":
                return await self._handle_e2e_test_request(message)
            elif msg_type == "bug_report":
                return await self._handle_bug_report(message)
            elif msg_type == "coverage_check":
                return await self._handle_coverage_check(message)
            elif msg_type == "deployment_approved":
                return await self._handle_pre_deployment_test(message)
            elif msg_type == "code_review_request":
                # Code comes to us for testing, not review — forward appropriately
                return await self._handle_test_request(message)
            else:
                return await self._handle_general_message(message)
        except Exception as exc:
            self.status = AgentStatus.ERROR
            self.logger.error("Tester processing error: %s", exc, exc_info=True)
            return await self.send_message(
                message.sender,
                f"Tester encountered an error: {exc}",
                msg_type="error",
            )
        finally:
            if self.status == AgentStatus.WORKING:
                self.status = AgentStatus.IDLE

    # ------------------------------------------------------------------
    # Handler methods
    # ------------------------------------------------------------------

    async def _handle_test_request(self, message: AgentMessage) -> AgentMessage:
        """Generate tests for provided code."""
        project_name = message.metadata.get("project_name", "unnamed")
        code = message.metadata.get("code", {})
        test_type = message.metadata.get("test_type", "unit")
        language = message.metadata.get("language", "python")

        self.logger.info("Test request: %s (%s, %s)", project_name, test_type, language)

        test_suite = await self.test_generation(project_name, code, test_type, language)

        # Execute tests
        execution_result = await self._execute_tests(test_suite, language)

        # Capture bugs if any
        if not execution_result.get("all_passed", True):
            bugs = await self._capture_bugs_from_failures(execution_result, project_name)
            return await self.send_message(
                "LUYMAS PDG",
                f"Tests FAILED for {project_name}: {len(bugs)} bugs found.",
                msg_type="bugs_found",
                metadata={"bugs": bugs, "test_suite": test_suite, "execution": execution_result},
            )

        return await self.send_message(
            "LUYMAS GUARDIAN",
            f"All tests PASSED for {project_name}. Coverage: {execution_result.get('coverage', 'N/A')}",
            msg_type="tests_passed",
            metadata={"test_suite": test_suite, "execution": execution_result},
        )

    async def _handle_e2e_test_request(self, message: AgentMessage) -> AgentMessage:
        """Run E2E tests with Playwright."""
        project_name = message.metadata.get("project_name", "unnamed")
        base_url = message.metadata.get("base_url", "http://localhost:3000")
        scenarios = message.metadata.get("scenarios", [])

        self.logger.info("E2E test request: %s at %s", project_name, base_url)

        e2e_result = await self.e2e_testing(project_name, base_url, scenarios)

        return await self.send_message(
            message.sender,
            f"E2E tests {'PASSED' if e2e_result.get('all_passed') else 'FAILED'} for {project_name}",
            msg_type="e2e_result",
            metadata={"result": e2e_result},
        )

    async def _handle_bug_report(self, message: AgentMessage) -> AgentMessage:
        """Process a bug report, capture screenshot, and notify relevant coder."""
        bug = message.metadata
        project_name = bug.get("project_name", "")

        self.logger.info("Bug report received: %s", bug.get("description", "")[:60])

        # Capture screenshot of the bug
        screenshot = await self.bug_capture(
            bug.get("url", ""),
            bug.get("selector", ""),
            bug.get("description", ""),
        )

        bug_report = {
            **bug,
            "screenshot": screenshot,
            "reported_at": datetime.now(timezone.utc).isoformat(),
            "reported_by": self.name,
            "status": "open",
        }

        self._bug_reports.append(bug_report)

        # Route to appropriate coder
        if bug.get("component") == "frontend":
            recipient = "LUYMAS CODER FRONTEND"
        else:
            recipient = "LUYMAS CODER BACKEND"

        return await self.send_message(
            recipient,
            f"Bug found in {project_name}: {bug.get('description', '')[:80]}",
            msg_type="bug_fix_request",
            metadata={"bug_report": bug_report},
        )

    async def _handle_coverage_check(self, message: AgentMessage) -> AgentMessage:
        """Check test coverage for a project."""
        project_name = message.metadata.get("project_name", "")
        coverage = await self._calculate_coverage(project_name)
        return await self.send_message(
            message.sender,
            f"Coverage for {project_name}: {coverage.get('percentage', 'N/A')}%",
            msg_type="coverage_report",
            metadata={"coverage": coverage},
        )

    async def _handle_pre_deployment_test(self, message: AgentMessage) -> AgentMessage:
        """Run pre-deployment test suite."""
        project_name = message.metadata.get("project_name", "")
        self.logger.info("Pre-deployment testing: %s", project_name)

        # Run full test suite
        results = {
            "unit": {"status": "requires_live_execution"},
            "integration": {"status": "requires_live_execution"},
            "e2e": {"status": "requires_live_execution"},
        }

        return await self.send_message(
            message.sender,
            f"Pre-deployment tests for {project_name}: pending live execution",
            msg_type="pre_deployment_test_result",
            metadata={"results": results},
        )

    async def _handle_general_message(self, message: AgentMessage) -> AgentMessage:
        """Handle general messages."""
        return await self.send_message(
            message.sender,
            "Tester acknowledges. Submit code for testing or report bugs.",
            msg_type="acknowledged",
        )

    # ------------------------------------------------------------------
    # Skill implementations
    # ------------------------------------------------------------------

    async def test_generation(
        self,
        project_name: str,
        code: Dict[str, Any],
        test_type: str = "unit",
        language: str = "python",
    ) -> Dict[str, Any]:
        """
        Generate test files based on the provided code.
        Supports unit, integration, and snapshot tests.
        """
        self.logger.info("Generating %s tests for %s (%s)", test_type, project_name, language)

        test_files: Dict[str, str] = {}
        files = code.get("files", {})

        for filename, content in files.items():
            if not isinstance(content, str):
                continue

            if language == "python" and filename.endswith(".py"):
                test_content = self._generate_python_tests(filename, content, test_type)
                test_filename = f"tests/test_{filename}"
                test_files[test_filename] = test_content

            elif language == "typescript" and filename.endswith((".ts", ".tsx")):
                test_content = self._generate_ts_tests(filename, content, test_type)
                test_filename = f"{filename.replace('.ts', '.test.ts').replace('.tsx', '.test.tsx')}"
                test_files[test_filename] = test_content

        suite: Dict[str, Any] = {
            "project_name": project_name,
            "test_type": test_type,
            "language": language,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "files": test_files,
            "total_test_files": len(test_files),
        }

        self._test_suites[f"{project_name}_{test_type}"] = suite
        return suite

    async def bug_capture(
        self,
        url: str,
        selector: str = "",
        description: str = "",
    ) -> Dict[str, Any]:
        """
        Capture a bug screenshot using Playwright.
        Returns screenshot data and metadata for the bug report.
        """
        self.logger.info("Bug capture: %s (selector: %s)", url, selector or "full page")

        # Production: use Playwright to capture screenshot
        screenshot: Dict[str, Any] = {
            "url": url,
            "selector": selector,
            "description": description,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "screenshot_data": "base64_encoded_screenshot_placeholder",
            "viewport": {"width": 1280, "height": 720},
            "status": "requires_live_playwright",
        }

        screenshot_id = f"bug-{int(time.time())}"
        self._screenshots[screenshot_id] = screenshot.get("screenshot_data", "")

        return screenshot

    async def e2e_testing(
        self,
        project_name: str,
        base_url: str,
        scenarios: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Run E2E tests using Playwright with video recording.
        Scenarios define user journeys to test.
        """
        self.logger.info("E2E testing: %s at %s (%d scenarios)", project_name, base_url, len(scenarios))

        # Default scenarios if none provided
        if not scenarios:
            scenarios = [
                {
                    "name": "Homepage loads",
                    "steps": [
                        {"action": "navigate", "url": base_url},
                        {"action": "assert_visible", "selector": "h1"},
                    ],
                },
                {
                    "name": "Navigation works",
                    "steps": [
                        {"action": "navigate", "url": base_url},
                        {"action": "click", "selector": "nav a:first-child"},
                        {"action": "assert_url_change", "expected": "/about"},
                    ],
                },
            ]

        # Generate Playwright test file
        playwright_test = self._generate_playwright_test(project_name, base_url, scenarios)

        # Production: execute via `npx playwright test`
        results: Dict[str, Any] = {
            "project_name": project_name,
            "base_url": base_url,
            "scenarios_tested": len(scenarios),
            "test_file": playwright_test,
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "all_passed": False,
            "results": [
                {
                    "scenario": s["name"],
                    "status": "requires_live_playwright",
                    "duration_ms": 0,
                    "screenshots": [],
                    "video": "",
                }
                for s in scenarios
            ],
            "video_recording": f"e2e-videos/{project_name}-{int(time.time())}.webm",
            "status": "requires_live_execution",
        }

        self._e2e_videos[project_name] = results.get("video_recording", "")
        return results

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------

    def _generate_python_tests(
        self, filename: str, content: str, test_type: str
    ) -> str:
        """Generate Python test file (pytest)."""
        module_name = filename.replace(".py", "")
        test_lines = [
            f'"""Tests for {filename} — Generated by LUYMAS TESTER"""',
            "",
            "import pytest",
            f"from {module_name} import *",
            "",
        ]

        # Extract function/class names for test generation
        functions = self._extract_python_functions(content)

        for func_name in functions:
            if func_name.startswith("_"):
                continue

            if test_type == "unit":
                test_lines.extend([
                    f"def test_{func_name}_basic():",
                    f'    """Test basic behavior of {func_name}."""',
                    f"    # TODO: Implement test for {func_name}",
                    f"    pass",
                    "",
                    f"def test_{func_name}_edge_cases():",
                    f'    """Test edge cases for {func_name}."""',
                    f"    # TODO: Test with None, empty, extreme values",
                    f"    pass",
                    "",
                    f"def test_{func_name}_error_handling():",
                    f'    """Test error handling for {func_name}."""',
                    f"    with pytest.raises(Exception):",
                    f"        # TODO: Trigger error condition",
                    f"        pass",
                    "",
                ])
            elif test_type == "integration":
                test_lines.extend([
                    f"async def test_{func_name}_integration():",
                    f'    """Integration test for {func_name}."""',
                    f"    # TODO: Set up test database and dependencies",
                    f"    pass",
                    "",
                ])

        return "\n".join(test_lines)

    def _generate_ts_tests(
        self, filename: str, content: str, test_type: str
    ) -> str:
        """Generate TypeScript test file (Vitest)."""
        component_name = filename.split("/")[-1].replace(".tsx", "").replace(".ts", "")

        test_lines = [
            f'// Tests for {filename} — Generated by LUYMAS TESTER',
            "",
            'import { describe, it, expect } from "vitest"',
        ]

        if ".tsx" in filename:
            test_lines.append('import { render, screen } from "@testing-library/react"')
            test_lines.append(f'import {{ {component_name} }} from "./{component_name}"')

        test_lines.extend([
            "",
            f'describe("{component_name}", () => {{',
            f'  it("renders correctly", () => {{',
        ])

        if ".tsx" in filename:
            test_lines.extend([
                f"    render(<{component_name} />)",
                f'    expect(screen.getByRole("generic")).toBeInTheDocument()',
            ])
        else:
            test_lines.append("    // TODO: Implement test")

        test_lines.extend([
            "  })",
            "",
            '  it("handles edge cases", () => {',
            "    // TODO: Test edge cases",
            "  })",
            "",
            '  it("is accessible", () => {',
            "    // TODO: Test accessibility (aria labels, keyboard nav)",
            "  })",
            "})",
            "",
        ])

        return "\n".join(test_lines)

    def _generate_playwright_test(
        self,
        project_name: str,
        base_url: str,
        scenarios: List[Dict[str, Any]],
    ) -> str:
        """Generate a Playwright E2E test file."""
        lines = [
            f"// E2E Tests for {project_name} — Generated by LUYMAS TESTER",
            "",
            'import { test, expect } from "@playwright/test"',
            "",
            f'test.describe("{project_name} E2E", () => {{',
        ]

        for scenario in scenarios:
            name = scenario.get("name", "unnamed")
            steps = scenario.get("steps", [])
            lines.extend([
                f'  test("{name}", async ({{ page }}) => {{',
            ])

            for step in steps:
                action = step.get("action", "")
                if action == "navigate":
                    lines.append(f'    await page.goto("{step.get("url", base_url)}")')
                elif action == "click":
                    lines.append(f'    await page.click("{step.get("selector", "")}")')
                elif action == "assert_visible":
                    lines.append(f'    await expect(page.locator("{step.get("selector", "")}")).toBeVisible()')
                elif action == "fill":
                    lines.append(f'    await page.fill("{step.get("selector", "")}", "{step.get("value", "")}")')
                else:
                    lines.append(f"    // TODO: {action}")

            lines.extend([
                "  })",
                "",
            ])

        lines.append("})")
        return "\n".join(lines)

    def _extract_python_functions(self, content: str) -> List[str]:
        """Extract function names from Python code."""
        functions: List[str] = []
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("def ") or stripped.startswith("async def "):
                func_name = stripped.split("(")[0].replace("def ", "").replace("async ", "").strip()
                functions.append(func_name)
        return functions

    async def _execute_tests(
        self, test_suite: Dict[str, Any], language: str
    ) -> Dict[str, Any]:
        """Execute a test suite and return results."""
        # Production: run via subprocess (pytest, vitest)
        return {
            "all_passed": False,
            "total_tests": test_suite.get("total_test_files", 0),
            "passed": 0,
            "failed": 0,
            "coverage": "0%",
            "status": "requires_live_execution",
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _capture_bugs_from_failures(
        self, execution_result: Dict[str, Any], project_name: str
    ) -> List[Dict[str, Any]]:
        """Capture bugs from test execution failures."""
        bugs: List[Dict[str, Any]] = []
        # Production: parse test output for failure details
        bugs.append({
            "project_name": project_name,
            "description": "Test failures detected — requires live execution for details",
            "severity": "medium",
            "captured_at": datetime.now(timezone.utc).isoformat(),
        })
        return bugs

    async def _calculate_coverage(self, project_name: str) -> Dict[str, Any]:
        """Calculate test coverage for a project."""
        # Production: parse coverage reports
        return {
            "project_name": project_name,
            "percentage": 0.0,
            "lines_covered": 0,
            "lines_total": 0,
            "status": "requires_live_coverage_tool",
        }

    def get_bug_reports(self) -> List[Dict[str, Any]]:
        """Return all bug reports."""
        return self._bug_reports

    def get_test_suites(self) -> Dict[str, Dict[str, Any]]:
        """Return all test suites."""
        return self._test_suites
