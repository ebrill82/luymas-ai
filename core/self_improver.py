"""
core/self_improver.py - System Self-Improvement for Luymas AI

Manages the self-improvement cycle: periodic self-assessment, watching for
new model releases, detecting code improvements, and generating proposals.
All changes require user approval via PDG.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

LUYMAS_ROOT = Path(__file__).parent.parent
IMPROVEMENT_REGISTRY = LUYMAS_ROOT / ".luymas_improvements.json"


# ── Data Models ──────────────────────────────────────────────────────────────

class ProposalType(str, Enum):
    CODE_IMPROVEMENT = "code_improvement"
    MODEL_UPDATE = "model_update"
    CONFIG_OPTIMIZATION = "config_optimization"
    DEPENDENCY_UPDATE = "dependency_update"
    ARCHITECTURE_CHANGE = "architecture_change"


class ProposalStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    APPLIED = "applied"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"


@dataclass
class Proposal:
    """Base improvement proposal."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    proposal_type: ProposalType = ProposalType.CODE_IMPROVEMENT
    title: str = ""
    description: str = ""
    rationale: str = ""
    risk_level: str = "low"  # low, medium, high, critical
    estimated_effort: str = "low"  # low, medium, high
    status: ProposalStatus = ProposalStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    approved_by: Optional[str] = None
    applied_at: Optional[datetime] = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelUpdate:
    """Information about a new model release."""
    model_name: str = ""
    version: str = ""
    release_date: str = ""
    improvements: list[str] = field(default_factory=list)
    breaking_changes: list[str] = field(default_factory=list)
    recommended: bool = False
    url: str = ""


@dataclass
class CodeProposal(Proposal):
    """A code-specific improvement proposal."""
    target_files: list[str] = field(default_factory=list)
    diff: str = ""
    test_instructions: str = ""


# ── Improvement Cycle ────────────────────────────────────────────────────────

class ImprovementCycle:
    """Periodic self-assessment of the Luymas AI system."""

    def __init__(self) -> None:
        self._last_cycle: Optional[datetime] = None
        self._cycle_count: int = 0
        self._findings: list[dict[str, Any]] = []

    async def run(self) -> list[Proposal]:
        """Run a full improvement assessment cycle."""
        self._cycle_count += 1
        self._last_cycle = datetime.now(timezone.utc)
        proposals: list[Proposal] = []

        logger.info("Starting improvement cycle #%d", self._cycle_count)

        # 1. Assess system performance
        perf_findings = self._assess_performance()
        self._findings.extend(perf_findings)

        # 2. Assess code quality
        code_findings = self._assess_code_quality()
        self._findings.extend(code_findings)

        # 3. Assess configuration
        config_findings = self._assess_configuration()
        self._findings.extend(config_findings)

        # Convert findings to proposals
        for finding in self._findings:
            proposal = Proposal(
                proposal_type=ProposalType(finding.get("type", "code_improvement")),
                title=finding.get("title", "Untitled"),
                description=finding.get("description", ""),
                rationale=finding.get("rationale", ""),
                risk_level=finding.get("risk_level", "low"),
            )
            proposals.append(proposal)

        logger.info("Improvement cycle #%d found %d proposals", self._cycle_count, len(proposals))
        return proposals

    def _assess_performance(self) -> list[dict[str, Any]]:
        """Assess system performance metrics."""
        findings: list[dict[str, Any]] = []

        # Check memory usage patterns
        # Check response times
        # Check error rates
        # In production: collect real metrics from running system

        findings.append({
            "type": "config_optimization",
            "title": "Review system resource allocation",
            "description": "Periodic review of memory and CPU usage patterns",
            "rationale": "Ensures optimal resource utilization",
            "risk_level": "low",
        })
        return findings

    def _assess_code_quality(self) -> list[dict[str, Any]]:
        """Assess code quality across modules."""
        findings: list[dict[str, Any]] = []

        core_dir = LUYMAS_ROOT / "core"
        if core_dir.exists():
            for py_file in core_dir.glob("*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8")
                    lines = content.splitlines()

                    # Check for missing docstrings
                    if '"""' not in content[:200]:
                        findings.append({
                            "type": "code_improvement",
                            "title": f"Add module docstring to {py_file.name}",
                            "description": f"{py_file.name} is missing a module-level docstring",
                            "rationale": "Documentation improves maintainability",
                            "risk_level": "low",
                        })

                    # Check for long functions (heuristic)
                    max_line_length = max(len(line) for line in lines) if lines else 0
                    if max_line_length > 120:
                        findings.append({
                            "type": "code_improvement",
                            "title": f"Long lines in {py_file.name}",
                            "description": f"Maximum line length is {max_line_length}",
                            "rationale": "Readability and PEP 8 compliance",
                            "risk_level": "low",
                        })

                except (UnicodeDecodeError, PermissionError):
                    continue

        return findings

    def _assess_configuration(self) -> list[dict[str, Any]]:
        """Assess configuration settings."""
        findings: list[dict[str, Any]] = []

        # Check for hardcoded values
        # Check for outdated dependencies
        # Check for security settings
        findings.append({
            "type": "config_optimization",
            "title": "Review environment configuration",
            "description": "Check for hardcoded values and ensure all config is env-driven",
            "rationale": "Security and flexibility",
            "risk_level": "medium",
        })
        return findings


# ── Model Updater ────────────────────────────────────────────────────────────

class ModelUpdater:
    """Watches for new model releases and creates update proposals."""

    KNOWN_MODELS = {
        "gpt-4": {"provider": "openai", "latest": "gpt-4-turbo"},
        "gpt-4o": {"provider": "openai", "latest": "gpt-4o"},
        "claude-3.5": {"provider": "anthropic", "latest": "claude-3.5-sonnet"},
        "gemini-pro": {"provider": "google", "latest": "gemini-1.5-pro"},
    }

    def __init__(self) -> None:
        self._tracked_models: list[str] = list(self.KNOWN_MODELS.keys())
        self._last_check: Optional[datetime] = None

    async def check_new_models(self) -> list[ModelUpdate]:
        """Check for new model releases."""
        self._last_check = datetime.now(timezone.utc)
        updates: list[ModelUpdate] = []

        # In production: query provider APIs for model availability
        # For now, return empty — real implementation would:
        # 1. Call OpenAI /v1/models
        # 2. Call Anthropic API
        # 3. Call Google AI API
        # 4. Compare with known versions
        logger.info("Checked for new model releases (tracked: %d)", len(self._tracked_models))
        return updates

    def track_model(self, model_name: str) -> None:
        """Add a model to the tracking list."""
        if model_name not in self._tracked_models:
            self._tracked_models.append(model_name)
            logger.info("Now tracking model: %s", model_name)

    def get_tracked_models(self) -> list[str]:
        return list(self._tracked_models)


# ── Code Optimizer ───────────────────────────────────────────────────────────

class CodeOptimizer:
    """Detects code improvement opportunities in the Luymas codebase."""

    PATTERNS = {
        "missing_error_handling": {
            "check": lambda c: "try:" not in c and "await" in c,
            "message": "Async code without error handling",
        },
        "sync_io_in_async": {
            "check": lambda c: "open(" in c and "async def" in c,
            "message": "Synchronous I/O in async context — consider aiofiles",
        },
        "missing_logging": {
            "check": lambda c: "raise" in c and "logger" not in c,
            "message": "Exception raised without logging",
        },
        "hardcoded_secrets": {
            "check": lambda c: any(kw in c.lower() for kw in ["password", "secret", "api_key"])
                               and '""' in c and "os.environ" not in c,
            "message": "Potential hardcoded secret — use environment variables",
        },
    }

    def check_code_improvements(self, scan_path: Optional[Path] = None) -> list[CodeProposal]:
        """Scan for code improvement opportunities."""
        scan_dir = scan_path or LUYMAS_ROOT / "core"
        proposals: list[CodeProposal] = []

        if not scan_dir.exists():
            return proposals

        for py_file in scan_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue

            rel_path = str(py_file.relative_to(LUYMAS_ROOT))

            for name, config in self.PATTERNS.items():
                if config["check"](content):
                    proposal = CodeProposal(
                        proposal_type=ProposalType.CODE_IMPROVEMENT,
                        title=f"{config['message']} in {py_file.name}",
                        description=f"Pattern '{name}' detected in {rel_path}",
                        rationale=config["message"],
                        risk_level="medium",
                        target_files=[rel_path],
                    )
                    proposals.append(proposal)

        logger.info("Found %d code improvement proposals", len(proposals))
        return proposals


# ── Proposal Generator ───────────────────────────────────────────────────────

class ProposalGenerator:
    """Creates structured improvement proposals from findings."""

    def create_proposal(self, title: str, description: str,
                        proposal_type: ProposalType = ProposalType.CODE_IMPROVEMENT,
                        risk_level: str = "low", **kwargs: Any) -> Proposal:
        """Create a new improvement proposal."""
        proposal = Proposal(
            proposal_type=proposal_type,
            title=title,
            description=description,
            rationale=kwargs.get("rationale", description),
            risk_level=risk_level,
            details=kwargs,
        )
        return proposal


# ── Self Improver Facade ─────────────────────────────────────────────────────

class SelfImprover:
    """Unified facade for the self-improvement system.

    All changes require user approval via PDG.

    Usage::

        improver = SelfImprover()
        proposals = await improver.run_improvement_cycle()
        models = await improver.check_new_models()
        code_improvements = improver.check_code_improvements()
        approval_id = improver.submit_proposal(proposals[0])
        improver.apply_approved(approval_id)
    """

    def __init__(self) -> None:
        self.cycle = ImprovementCycle()
        self.model_updater = ModelUpdater()
        self.code_optimizer = CodeOptimizer()
        self.proposal_generator = ProposalGenerator()
        self._proposals: dict[str, Proposal] = {}
        self._load_registry()

    async def run_improvement_cycle(self) -> list[Proposal]:
        """Run a full self-improvement assessment."""
        proposals = await self.cycle.run()
        for p in proposals:
            self._proposals[p.id] = p
        return proposals

    async def check_new_models(self) -> list[ModelUpdate]:
        """Check for new model releases."""
        return await self.model_updater.check_new_models()

    def check_code_improvements(self) -> list[CodeProposal]:
        """Check for code improvement opportunities."""
        return self.code_optimizer.check_code_improvements()

    def submit_proposal(self, proposal: Proposal) -> str:
        """Submit a proposal for user approval."""
        proposal.status = ProposalStatus.SUBMITTED
        self._proposals[proposal.id] = proposal
        self._save_registry()
        logger.info("Submitted proposal %s: %s", proposal.id, proposal.title)
        return proposal.id

    def approve_proposal(self, proposal_id: str, approver: str = "user") -> bool:
        """Approve a submitted proposal."""
        proposal = self._proposals.get(proposal_id)
        if not proposal or proposal.status != ProposalStatus.SUBMITTED:
            return False
        proposal.status = ProposalStatus.APPROVED
        proposal.approved_by = approver
        self._save_registry()
        return True

    def apply_approved(self, approval_id: str) -> bool:
        """Apply an approved proposal (requires prior approval)."""
        proposal = self._proposals.get(approval_id)
        if not proposal or proposal.status != ProposalStatus.APPROVED:
            logger.error("Cannot apply proposal %s: not approved", approval_id)
            return False

        # In production: delegate to auto_updater for code changes
        proposal.status = ProposalStatus.APPLIED
        proposal.applied_at = datetime.now(timezone.utc)
        self._save_registry()
        logger.info("Applied proposal %s: %s", approval_id, proposal.title)
        return True

    def get_proposals(self, status: Optional[ProposalStatus] = None) -> list[Proposal]:
        proposals = list(self._proposals.values())
        if status:
            proposals = [p for p in proposals if p.status == status]
        return proposals

    def _load_registry(self) -> None:
        """Load proposals from persistent storage."""
        if IMPROVEMENT_REGISTRY.exists():
            try:
                data = json.loads(IMPROVEMENT_REGISTRY.read_text(encoding="utf-8"))
                for item in data:
                    self._proposals[item.get("id", "")] = Proposal(**item)
            except (json.JSONDecodeError, TypeError):
                pass

    def _save_registry(self) -> None:
        """Persist proposals to storage."""
        data = []
        for p in self._proposals.values():
            data.append({
                "id": p.id,
                "proposal_type": p.proposal_type.value,
                "title": p.title,
                "description": p.description,
                "status": p.status.value,
                "risk_level": p.risk_level,
                "approved_by": p.approved_by,
            })
        IMPROVEMENT_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
        IMPROVEMENT_REGISTRY.write_text(json.dumps(data, indent=2), encoding="utf-8")
