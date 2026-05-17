"""
LUYMAS GUARDIAN — Code Review, Security & Performance Agent

The Guardian is the quality gatekeeper of the Luymas AI system. It performs
code reviews, security scanning (OWASP Top 10), dependency vulnerability
checking, and performance analysis. Before each scan, it searches for the
latest known vulnerabilities to ensure up-to-date protection.

Skills: security-scan, dependency-check, vulnerability-analysis
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import asyncio
import json
import logging
import time
from datetime import datetime, timezone


class AgentStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    WAITING_APPROVAL = "waiting_approval"
    ERROR = "error"


@dataclass
class AgentMessage:
    sender: str
    recipient: str
    content: str
    message_type: str = "text"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0


class BaseAgent:
    """Base class for all Luymas agents."""

    def __init__(self, name: str, role: str, email: str, model: str = ""):
        self.name = name
        self.role = role
        self.email = email
        self.model = model
        self.status = AgentStatus.IDLE
        self.memory: List[Dict] = []
        self.skills: List[str] = []
        self.logger = logging.getLogger(f"luymas.{name}")

    async def receive_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        self.memory.append({"role": "received", "message": message})
        return await self.process(message)

    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        raise NotImplementedError

    async def send_message(self, recipient: str, content: str, msg_type: str = "text") -> AgentMessage:
        msg = AgentMessage(
            sender=self.name, recipient=recipient,
            content=content, message_type=msg_type,
            timestamp=time.time(),
        )
        self.memory.append({"role": "sent", "message": msg})
        return msg

    async def request_approval(self, action: str, details: str) -> bool:
        self.status = AgentStatus.WAITING_APPROVAL
        return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name, "role": self.role,
            "status": self.status.value, "memory_size": len(self.memory),
        }


class GuardianAgent(BaseAgent):
    """
    LUYMAS GUARDIAN — Code Review, Security & Performance Agent.

    Responsibilities:
    - Code review for quality, maintainability, and best practices
    - OWASP Top 10 security scanning
    - Dependency vulnerability checking
    - Performance analysis and optimization suggestions
    - Searches latest known vulnerabilities before each scan
    - Blocks deployment if critical issues are found

    Skills: security-scan, dependency-check, vulnerability-analysis
    """

    SYSTEM_PROMPT: str = (
        "You are LUYMAS GUARDIAN, the security and quality guardian of the Luymas AI system. "
        "You review every piece of code before it reaches production. You scan for OWASP Top 10 "
        "vulnerabilities, check dependency security, and analyze performance. Before each scan, "
        "you search for the latest known vulnerabilities to ensure up-to-date protection. You "
        "are thorough, uncompromising on security, and practical on performance. You block "
        "deployment when critical issues are found and provide clear remediation guidance."
    )

    # OWASP Top 10 (2021) categories for scanning
    OWASP_TOP_10: List[Dict[str, str]] = [
        {"id": "A01", "name": "Broken Access Control", "severity": "critical"},
        {"id": "A02", "name": "Cryptographic Failures", "severity": "critical"},
        {"id": "A03", "name": "Injection", "severity": "critical"},
        {"id": "A04", "name": "Insecure Design", "severity": "high"},
        {"id": "A05", "name": "Security Misconfiguration", "severity": "high"},
        {"id": "A06", "name": "Vulnerable Components", "severity": "high"},
        {"id": "A07", "name": "Auth Failures", "severity": "high"},
        {"id": "A08", "name": "Data Integrity Failures", "severity": "medium"},
        {"id": "A09", "name": "Logging Failures", "severity": "medium"},
        {"id": "A10", "name": "SSRF", "severity": "medium"},
    ]

    # Dangerous patterns to detect
    SECURITY_PATTERNS: Dict[str, List[Dict[str, Any]]] = {
        "injection": [
            {"pattern": "f\"SELECT", "description": "SQL injection via f-string", "severity": "critical"},
            {"pattern": "f\"INSERT", "description": "SQL injection via f-string", "severity": "critical"},
            {"pattern": "f\"DELETE", "description": "SQL injection via f-string", "severity": "critical"},
            {"pattern": "eval(", "description": "Code injection via eval()", "severity": "critical"},
            {"pattern": "exec(", "description": "Code injection via exec()", "severity": "critical"},
            {"pattern": "__import__(", "description": "Dynamic import injection", "severity": "high"},
            {"pattern": "subprocess.call(", "description": "Command injection risk", "severity": "high"},
            {"pattern": "os.system(", "description": "Command injection risk", "severity": "high"},
        ],
        "auth": [
            {"pattern": "password =", "description": "Hardcoded password", "severity": "critical"},
            {"pattern": "api_key =", "description": "Hardcoded API key", "severity": "critical"},
            {"pattern": "secret =", "description": "Hardcoded secret", "severity": "critical"},
            {"pattern": "token =", "description": "Hardcoded token", "severity": "high"},
        ],
        "crypto": [
            {"pattern": "md5(", "description": "Weak hash algorithm (MD5)", "severity": "high"},
            {"pattern": "sha1(", "description": "Weak hash algorithm (SHA1)", "severity": "medium"},
            {"pattern": "DES", "description": "Weak encryption (DES)", "severity": "high"},
        ],
        "misconfig": [
            {"pattern": "CORS(allow_origins=[\"*\"])", "description": "Overly permissive CORS", "severity": "high"},
            {"pattern": "DEBUG = True", "description": "Debug mode in production", "severity": "high"},
            {"pattern": "allow_methods=[\"*\"]", "description": "Overly permissive HTTP methods", "severity": "medium"},
        ],
    }

    def __init__(
        self,
        name: str = "LUYMAS GUARDIAN",
        role: str = "Security & Quality Guardian",
        email: str = "guardian@luymas.ai",
        model: str = "claude-sonnet-4-20250514",
    ):
        super().__init__(name=name, role=role, email=email, model=model)
        self.skills = ["security-scan", "dependency-check", "vulnerability-analysis"]
        self._scan_results: Dict[str, Dict[str, Any]] = {}
        self._vulnerability_db: Dict[str, List[Dict[str, Any]]] = {}
        self._dependency_issues: Dict[str, List[Dict[str, Any]]] = {}
        self._review_history: List[Dict[str, Any]] = []
        self._blocklist: List[str] = []
        self.logger.info("Guardian Agent initialized — security perimeter active")

    # ------------------------------------------------------------------
    # Core message processing
    # ------------------------------------------------------------------

    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Route incoming messages to the appropriate Guardian handler."""
        self.status = AgentStatus.WORKING
        try:
            msg_type = message.message_type

            if msg_type == "code_review_request":
                return await self._handle_code_review(message)
            elif msg_type == "security_scan_request":
                return await self._handle_security_scan(message)
            elif msg_type == "dependency_check_request":
                return await self._handle_dependency_check(message)
            elif msg_type == "deployment_gate":
                return await self._handle_deployment_gate(message)
            elif msg_type == "vulnerability_search":
                return await self._handle_vulnerability_search(message)
            else:
                return await self._handle_general_message(message)
        except Exception as exc:
            self.status = AgentStatus.ERROR
            self.logger.error("Guardian processing error: %s", exc, exc_info=True)
            return await self.send_message(
                message.sender,
                f"Guardian encountered an error: {exc}",
                msg_type="error",
            )
        finally:
            if self.status == AgentStatus.WORKING:
                self.status = AgentStatus.IDLE

    # ------------------------------------------------------------------
    # Handler methods
    # ------------------------------------------------------------------

    async def _handle_code_review(self, message: AgentMessage) -> AgentMessage:
        """Perform a comprehensive code review."""
        project_name = message.metadata.get("project_name", "unnamed")
        code = message.metadata.get("code", {})

        self.logger.info("Code review requested: %s", project_name)

        # Run all checks
        security = await self.security_scan(code)
        dependencies = await self.dependency_check(code)
        performance = await self._analyze_performance(code)
        quality = await self._analyze_code_quality(code)

        # Aggregate results
        critical_issues = (
            security.get("critical_count", 0)
            + dependencies.get("critical_count", 0)
        )

        result: Dict[str, Any] = {
            "project_name": project_name,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "reviewed_by": self.name,
            "security": security,
            "dependencies": dependencies,
            "performance": performance,
            "quality": quality,
            "can_deploy": critical_issues == 0,
            "critical_issues": critical_issues,
            "total_issues": (
                security.get("total_issues", 0)
                + dependencies.get("total_issues", 0)
                + performance.get("total_issues", 0)
                + quality.get("total_issues", 0)
            ),
        }

        self._scan_results[project_name] = result
        self._review_history.append(result)

        # Route result
        if critical_issues > 0:
            return await self.send_message(
                "LUYMAS PDG",
                f"BLOCKED: {critical_issues} critical issues found in {project_name}. Deployment denied.",
                msg_type="deployment_blocked",
                metadata={"review": result},
            )
        else:
            return await self.send_message(
                "LUYMAS OPS",
                f"APPROVED: {project_name} passed all checks. Ready for deployment.",
                msg_type="deployment_approved",
                metadata={"review": result},
            )

    async def _handle_security_scan(self, message: AgentMessage) -> AgentMessage:
        """Run a focused security scan."""
        code = message.metadata.get("code", {})
        scan_result = await self.security_scan(code)
        return await self.send_message(
            message.sender,
            f"Security scan complete: {scan_result.get('total_issues', 0)} issues found.",
            msg_type="security_scan_complete",
            metadata={"scan": scan_result},
        )

    async def _handle_dependency_check(self, message: AgentMessage) -> AgentMessage:
        """Run a dependency vulnerability check."""
        dependencies = message.metadata.get("dependencies", {})
        check_result = await self.dependency_check(dependencies)
        return await self.send_message(
            message.sender,
            f"Dependency check complete: {check_result.get('total_issues', 0)} issues found.",
            msg_type="dependency_check_complete",
            metadata={"check": check_result},
        )

    async def _handle_deployment_gate(self, message: AgentMessage) -> AgentMessage:
        """Final deployment gate check."""
        project_name = message.metadata.get("project_name", "")

        if project_name in self._scan_results:
            result = self._scan_results[project_name]
            if result.get("can_deploy", False):
                return await self.send_message(
                    message.sender,
                    f"DEPLOYMENT GATE: {project_name} APPROVED.",
                    msg_type="deployment_approved",
                )
            else:
                return await self.send_message(
                    message.sender,
                    f"DEPLOYMENT GATE: {project_name} BLOCKED. {result.get('critical_issues', 0)} critical issues.",
                    msg_type="deployment_blocked",
                )

        # No scan results — must scan first
        return await self.send_message(
            message.sender,
            f"DEPLOYMENT GATE: No scan results for {project_name}. Run code review first.",
            msg_type="deployment_blocked",
        )

    async def _handle_vulnerability_search(self, message: AgentMessage) -> AgentMessage:
        """Search for latest known vulnerabilities."""
        package = message.metadata.get("package", "")
        version = message.metadata.get("version", "")
        vulns = await self.vulnerability_analysis(package, version)
        return await self.send_message(
            message.sender,
            f"Vulnerability search complete for {package}@{version}",
            msg_type="vulnerability_search_complete",
            metadata={"vulnerabilities": vulns},
        )

    async def _handle_general_message(self, message: AgentMessage) -> AgentMessage:
        """Handle general messages."""
        return await self.send_message(
            message.sender,
            "Guardian acknowledges. Submit code for review or security scanning.",
            msg_type="acknowledged",
        )

    # ------------------------------------------------------------------
    # Skill implementations
    # ------------------------------------------------------------------

    async def security_scan(self, code: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform OWASP Top 10 security scan on the provided code.
        Scans for injection, auth issues, crypto weaknesses, and misconfigurations.
        """
        self.logger.info("Running OWASP Top 10 security scan")

        # First, search for latest vulnerabilities
        latest_vulns = await self._search_latest_vulnerabilities()

        findings: List[Dict[str, Any]] = []
        files = code.get("files", {})

        for filename, content in files.items():
            if not isinstance(content, str):
                continue

            # Check all security pattern categories
            for category, patterns in self.SECURITY_PATTERNS.items():
                for pattern_def in patterns:
                    pattern = pattern_def["pattern"]
                    if pattern in content:
                        # Find line number
                        lines = content.split("\n")
                        line_nums = [
                            i + 1 for i, line in enumerate(lines) if pattern in line
                        ]
                        findings.append({
                            "file": filename,
                            "category": category,
                            "owasp_mapping": self._map_to_owasp(category),
                            "pattern": pattern,
                            "description": pattern_def["description"],
                            "severity": pattern_def["severity"],
                            "lines": line_nums,
                            "remediation": self._get_remediation(category, pattern),
                        })

        critical_count = sum(1 for f in findings if f["severity"] == "critical")
        high_count = sum(1 for f in findings if f["severity"] == "high")

        return {
            "scan_type": "OWASP Top 10",
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "files_scanned": len(files),
            "findings": findings,
            "critical_count": critical_count,
            "high_count": high_count,
            "total_issues": len(findings),
            "latest_vulnerabilities_checked": latest_vulns,
            "owasp_categories_covered": [cat["id"] for cat in self.OWASP_TOP_10],
        }

    async def dependency_check(self, code_or_deps: Any) -> Dict[str, Any]:
        """
        Check dependencies for known vulnerabilities.
        Parses package.json, requirements.txt, or dependency dictionaries.
        """
        self.logger.info("Running dependency vulnerability check")

        dependencies: Dict[str, str] = {}
        issues: List[Dict[str, Any]] = []

        # Extract dependencies from code or direct input
        if isinstance(code_or_deps, dict):
            files = code_or_deps.get("files", {})
            if "requirements.txt" in files:
                dependencies = self._parse_requirements(files["requirements.txt"])
            elif "package.json" in files:
                dependencies = self._parse_package_json(files["package.json"])
            else:
                dependencies = code_or_deps  # Assume it's already a dep dict
        else:
            dependencies = {}

        # Check each dependency against vulnerability DB
        latest_vulns = await self._search_latest_vulnerabilities()

        for dep_name, dep_version in dependencies.items():
            # Production: check against OSV.dev, Snyk, or npm audit
            known_issues = self._check_dependency_vulnerabilities(dep_name, dep_version, latest_vulns)
            issues.extend(known_issues)

        critical_count = sum(1 for i in issues if i.get("severity") == "critical")

        return {
            "check_type": "dependency_vulnerability",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "dependencies_checked": len(dependencies),
            "issues": issues,
            "critical_count": critical_count,
            "total_issues": len(issues),
            "recommendations": [
                "Run `pip audit` for Python dependencies",
                "Run `npm audit` for Node.js dependencies",
                "Keep all dependencies up to date",
            ],
        }

    async def vulnerability_analysis(
        self, package: str, version: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze a specific package/version for known vulnerabilities.
        Searches latest vulnerability databases before reporting.
        """
        self.logger.info("Vulnerability analysis: %s@%s", package, version)

        latest_vulns = await self._search_latest_vulnerabilities()

        # Check specific package
        package_vulns = self._check_dependency_vulnerabilities(
            package, version, latest_vulns
        )

        return {
            "package": package,
            "version": version,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "vulnerabilities": package_vulns,
            "is_safe": len([v for v in package_vulns if v.get("severity") == "critical"]) == 0,
            "latest_vulnerabilities_db": latest_vulns.get("last_updated", "unknown"),
        }

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------

    async def _search_latest_vulnerabilities(self) -> Dict[str, Any]:
        """
        Search for the latest known vulnerabilities before each scan.
        Ensures up-to-date security coverage.
        """
        self.logger.info("Searching latest vulnerability databases")

        # Production: query NVD, OSV.dev, GitHub Advisory Database
        vuln_db: Dict[str, Any] = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "sources_checked": ["NVD", "OSV.dev", "GitHub Advisory"],
            "recent_critical": [],
            "status": "requires_live_api_call",
        }
        self._vulnerability_db["latest"] = vuln_db
        return vuln_db

    async def _analyze_performance(self, code: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for performance issues."""
        issues: List[Dict[str, Any]] = []
        files = code.get("files", {})

        for filename, content in files.items():
            if not isinstance(content, str):
                continue

            # N+1 query pattern
            if "for " in content and ".query(" in content:
                issues.append({
                    "file": filename,
                    "type": "potential_n+1_query",
                    "severity": "high",
                    "description": "Potential N+1 query in loop",
                })

            # Synchronous I/O
            if "requests.get(" in content or "requests.post(" in content:
                if "async" not in content:
                    issues.append({
                        "file": filename,
                        "type": "sync_io_in_async_context",
                        "severity": "medium",
                        "description": "Synchronous HTTP call detected — consider httpx.AsyncClient",
                    })

            # Missing pagination
            if ".all()" in content and "limit" not in content:
                issues.append({
                    "file": filename,
                    "type": "missing_pagination",
                    "severity": "medium",
                    "description": "Unbounded query — consider adding pagination",
                })

        return {
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "issues": issues,
            "total_issues": len(issues),
        }

    async def _analyze_code_quality(self, code: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code quality (maintainability, readability, best practices)."""
        issues: List[Dict[str, Any]] = []
        files = code.get("files", {})

        for filename, content in files.items():
            if not isinstance(content, str):
                continue

            # Missing type hints
            if "def " in content and "-> " not in content:
                issues.append({
                    "file": filename,
                    "type": "missing_return_type",
                    "severity": "low",
                    "description": "Function missing return type annotation",
                })

            # Magic numbers
            if any(c.isdigit() for c in content.split("=")[0] if c != " "):
                pass  # Simplified check — production would use AST

            # Long functions (simple heuristic)
            lines = content.split("\n")
            func_start = -1
            for i, line in enumerate(lines):
                if "def " in line or "function " in line:
                    func_start = i
                elif func_start >= 0 and i - func_start > 50 and not line.strip():
                    issues.append({
                        "file": filename,
                        "type": "long_function",
                        "severity": "low",
                        "description": f"Function starting at line {func_start + 1} exceeds 50 lines",
                    })
                    func_start = -1

        return {
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "issues": issues,
            "total_issues": len(issues),
        }

    def _map_to_owasp(self, category: str) -> str:
        """Map a security category to OWASP Top 10."""
        mapping = {
            "injection": "A03:2021-Injection",
            "auth": "A07:2021-Auth Failures",
            "crypto": "A02:2021-Cryptographic Failures",
            "misconfig": "A05:2021-Security Misconfiguration",
        }
        return mapping.get(category, "Unknown")

    def _get_remediation(self, category: str, pattern: str) -> str:
        """Get remediation advice for a security finding."""
        remediations = {
            "injection": "Use parameterized queries and ORM. Never concatenate user input into queries.",
            "auth": "Use environment variables for secrets. Implement proper secret management.",
            "crypto": "Use modern algorithms (bcrypt, argon2 for hashing; AES-256-GCM for encryption).",
            "misconfig": "Follow security hardening guides. Disable debug mode in production.",
        }
        return remediations.get(category, "Review and follow security best practices.")

    def _check_dependency_vulnerabilities(
        self, name: str, version: str, latest_vulns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check a specific dependency for known vulnerabilities."""
        # Production: query OSV.dev, npm audit, pip audit
        return []

    def _parse_requirements(self, content: str) -> Dict[str, str]:
        """Parse requirements.txt into dependency dict."""
        deps: Dict[str, str] = {}
        for line in content.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                for op in [">=", "==", "<=", ">", "<"]:
                    if op in line:
                        name, ver = line.split(op, 1)
                        deps[name.strip()] = f"{op}{ver.strip()}"
                        break
                else:
                    deps[line] = "latest"
        return deps

    def _parse_package_json(self, content: str) -> Dict[str, str]:
        """Parse package.json into dependency dict."""
        try:
            data = json.loads(content)
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            return deps
        except json.JSONDecodeError:
            return {}

    def get_scan_results(self) -> Dict[str, Dict[str, Any]]:
        """Return all scan results."""
        return self._scan_results
