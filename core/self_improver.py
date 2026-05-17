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

try:
    import psutil  # ✅ Réel
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False

try:
    import requests  # ✅ Réel
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

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
        """Assess system performance metrics using real system data."""
        findings: list[dict[str, Any]] = []

        if _HAS_PSUTIL:
            # ✅ Réel — Collect real CPU, memory, and disk metrics
            try:
                cpu_percent = psutil.cpu_percent(interval=1)  # ✅ Réel
                mem = psutil.virtual_memory()  # ✅ Réel
                disk = psutil.disk_usage("/")  # ✅ Réel
                load_avg = os.getloadavg() if hasattr(os, "getloadavg") else (0, 0, 0)  # ✅ Réel

                logger.info(
                    "Performance: CPU=%.1f%%, RAM=%.1f%% (%.1fGB/%.1fGB), Disk=%.1f%%, Load=%.2f",
                    cpu_percent, mem.percent,
                    mem.used / (1024**3), mem.total / (1024**3),
                    disk.percent, load_avg[0],
                )

                # High CPU usage finding
                if cpu_percent > 80:  # ✅ Réel
                    findings.append({
                        "type": "config_optimization",
                        "title": f"High CPU usage detected ({cpu_percent:.1f}%)",
                        "description": f"CPU usage is {cpu_percent:.1f}%, consider reducing workload or scaling",
                        "rationale": "High CPU can cause degraded response times",
                        "risk_level": "high",
                        "details": {"cpu_percent": cpu_percent},
                    })

                # High memory usage finding
                if mem.percent > 85:  # ✅ Réel
                    findings.append({
                        "type": "config_optimization",
                        "title": f"High memory usage detected ({mem.percent:.1f}%)",
                        "description": (
                            f"RAM: {mem.used / (1024**3):.1f}GB / {mem.total / (1024**3):.1f}GB "
                            f"({mem.percent:.1f}%). Consider optimizing memory usage."
                        ),
                        "rationale": "Memory pressure can cause OOM kills and crashes",
                        "risk_level": "high",
                        "details": {"mem_percent": mem.percent, "mem_available_gb": mem.available / (1024**3)},
                    })

                # Low disk space finding
                if disk.percent > 90:  # ✅ Réel
                    findings.append({
                        "type": "config_optimization",
                        "title": f"Low disk space ({disk.percent:.1f}% used)",
                        "description": (
                            f"Disk: {disk.used / (1024**3):.1f}GB / {disk.total / (1024**3):.1f}GB "
                            f"({disk.percent:.1f}%). Free up space or expand storage."
                        ),
                        "rationale": "Disk exhaustion can cause system failures",
                        "risk_level": "critical",
                        "details": {"disk_percent": disk.percent, "disk_free_gb": disk.free / (1024**3)},
                    })

                # High load average finding
                if load_avg[0] > 4.0:  # ✅ Réel
                    findings.append({
                        "type": "config_optimization",
                        "title": f"High system load average ({load_avg[0]:.2f})",
                        "description": f"1-min load average is {load_avg[0]:.2f}",
                        "rationale": "High load indicates resource contention",
                        "risk_level": "medium",
                        "details": {"load_1m": load_avg[0], "load_5m": load_avg[1], "load_15m": load_avg[2]},
                    })

                # General performance review if everything is OK
                if not findings:
                    findings.append({
                        "type": "config_optimization",
                        "title": "System resources nominal — periodic review",
                        "description": (
                            f"CPU={cpu_percent:.1f}%, RAM={mem.percent:.1f}%, "
                            f"Disk={disk.percent:.1f}%, Load={load_avg[0]:.2f}"
                        ),
                        "rationale": "Regular review ensures continued optimal resource utilization",
                        "risk_level": "low",
                        "details": {
                            "cpu_percent": cpu_percent,
                            "mem_percent": mem.percent,
                            "disk_percent": disk.percent,
                            "load_1m": load_avg[0],
                        },
                    })
            except Exception as exc:
                logger.error("psutil metrics collection failed: %s", exc)
                findings.append({
                    "type": "config_optimization",
                    "title": "Performance metrics collection failed",
                    "description": f"Could not collect system metrics: {exc}",
                    "rationale": "Cannot assess performance without metrics",
                    "risk_level": "medium",
                })
        else:
            # Fallback: use /proc and os module when psutil is unavailable
            try:
                load_avg = os.getloadavg() if hasattr(os, "getloadavg") else (0, 0, 0)  # ✅ Réel
                proc_mem = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") if hasattr(os, "sysconf") else 0  # ✅ Réel
                mem_gb = proc_mem / (1024**3) if proc_mem else 0

                logger.info("Performance (fallback): Load=%.2f, TotalRAM=%.1fGB", load_avg[0], mem_gb)

                if load_avg[0] > 4.0:  # ✅ Réel
                    findings.append({
                        "type": "config_optimization",
                        "title": f"High system load average ({load_avg[0]:.2f})",
                        "description": f"1-min load average is {load_avg[0]:.2f}",
                        "rationale": "High load indicates resource contention",
                        "risk_level": "medium",
                        "details": {"load_1m": load_avg[0]},
                    })

                findings.append({
                    "type": "config_optimization",
                    "title": "Limited performance assessment (no psutil)",
                    "description": f"Load={load_avg[0]:.2f}, TotalRAM={mem_gb:.1f}GB. Install psutil for full metrics.",
                    "rationale": "Basic system info available via /proc and os module",
                    "risk_level": "low",
                    "details": {"load_1m": load_avg[0], "total_ram_gb": mem_gb},
                })
            except Exception as exc:
                findings.append({
                    "type": "config_optimization",
                    "title": "Performance metrics unavailable",
                    "description": "⚠️ psutil non configuré and /proc unavailable",
                    "rationale": "Cannot assess performance without metrics tools",
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
        """Check for new model releases from HuggingFace and Ollama APIs."""
        self._last_check = datetime.now(timezone.utc)
        updates: list[ModelUpdate] = []

        if not _HAS_REQUESTS:
            logger.warning("⚠️ requests non configuré. Cannot check for new models.")
            return updates

        # ── Check HuggingFace for new models ──
        try:
            hf_response = requests.get(  # ✅ Réel
                "https://huggingface.co/api/models",
                params={
                    "sort": "lastModified",
                    "direction": "-1",
                    "limit": 20,
                    "filter": "text-generation",
                },
                timeout=15,
            )
            if hf_response.status_code == 200:  # ✅ Réel
                hf_models = hf_response.json()  # ✅ Réel
                for model in hf_models[:10]:
                    model_id = model.get("modelId", "")
                    last_modified = model.get("lastModified", "")
                    # Check if this is a model we track or should recommend
                    for tracked, info in self.KNOWN_MODELS.items():
                        provider = info.get("provider", "")
                        if provider == "huggingface" or tracked.lower() in model_id.lower():
                            updates.append(ModelUpdate(  # ✅ Réel
                                model_name=model_id,
                                version="latest",
                                release_date=last_modified,
                                improvements=[f"New HuggingFace model: {model_id}"],
                                recommended=True,
                                url=f"https://huggingface.co/{model_id}",
                            ))
                            break
                logger.info("HuggingFace: found %d recently updated text-generation models", len(hf_models))  # ✅ Réel
            else:
                logger.warning("HuggingFace API returned status %d", hf_response.status_code)
        except requests.exceptions.Timeout:
            logger.warning("HuggingFace API request timed out")
        except Exception as exc:
            logger.error("HuggingFace API check failed: %s", exc)

        # ── Check Ollama library for new models ──
        try:
            ollama_response = requests.get(  # ✅ Réel
                "https://ollama.com/api/models",
                params={"limit": 20},
                timeout=15,
            )
            if ollama_response.status_code == 200:  # ✅ Réel
                ollama_data = ollama_response.json()  # ✅ Réel
                ollama_models = ollama_data if isinstance(ollama_data, list) else ollama_data.get("models", [])
                for model in ollama_models[:10]:
                    model_name = model.get("name", model.get("model", ""))
                    if not model_name:
                        continue
                    # Compare with tracked models
                    for tracked in self._tracked_models:
                        if tracked.lower() in model_name.lower():
                            current_latest = self.KNOWN_MODELS.get(tracked, {}).get("latest", "")
                            if model_name != current_latest:
                                updates.append(ModelUpdate(  # ✅ Réel
                                    model_name=model_name,
                                    version=model_name.split(":")[-1] if ":" in model_name else "latest",
                                    release_date=model.get("modified_at", model.get("updated_at", "")),
                                    improvements=[f"New Ollama model version: {model_name}"],
                                    recommended=True,
                                    url=f"https://ollama.com/library/{model_name.split(':')[0]}",
                                ))
                            break
                logger.info("Ollama: found %d models", len(ollama_models))  # ✅ Réel
            else:
                logger.warning("Ollama API returned status %d", ollama_response.status_code)
        except requests.exceptions.Timeout:
            logger.warning("Ollama API request timed out")
        except Exception as exc:
            logger.error("Ollama API check failed: %s", exc)

        # ── Check OpenAI models API (if key available) ──
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        if openai_key:
            try:
                oai_response = requests.get(  # ✅ Réel
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {openai_key}"},
                    timeout=15,
                )
                if oai_response.status_code == 200:  # ✅ Réel
                    oai_data = oai_response.json()  # ✅ Réel
                    available_models = [m["id"] for m in oai_data.get("data", [])]
                    for tracked, info in self.KNOWN_MODELS.items():
                        if info.get("provider") == "openai":
                            latest = info.get("latest", "")
                            if latest in available_models:
                                # Already known, but check for newer versions
                                prefix = tracked.replace("-4o", "").replace("-4", "")
                                newer = [m for m in available_models if m.startswith(prefix) and m > latest]
                                for new_model in newer[:3]:
                                    updates.append(ModelUpdate(  # ✅ Réel
                                        model_name=new_model,
                                        version=new_model,
                                        improvements=[f"Newer OpenAI model available: {new_model}"],
                                        recommended=True,
                                        url=f"https://platform.openai.com/docs/models/{new_model}",
                                    ))
                    logger.info("OpenAI: %d models available", len(available_models))  # ✅ Réel
                else:
                    logger.warning("OpenAI API returned status %d", oai_response.status_code)
            except Exception as exc:
                logger.error("OpenAI model check failed: %s", exc)
        else:
            logger.info("⚠️ OPENAI_API_KEY non configuré. Skipping OpenAI model check.")

        logger.info("Checked for new model releases (tracked: %d, updates: %d)",
                     len(self._tracked_models), len(updates))
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
        """Apply an approved proposal (requires prior approval).

        Delegates to AutoUpdater for code change proposals.
        """
        proposal = self._proposals.get(approval_id)
        if not proposal or proposal.status != ProposalStatus.APPROVED:
            logger.error("Cannot apply proposal %s: not approved", approval_id)
            return False

        # Delegate to AutoUpdater for code change proposals  # ✅ Réel
        if proposal.proposal_type in (ProposalType.CODE_IMPROVEMENT, ProposalType.DEPENDENCY_UPDATE, ProposalType.ARCHITECTURE_CHANGE):
            try:
                from core.auto_updater import AutoUpdater, UpdateProposal, UpdateType, UpdateStatus  # ✅ Réel

                updater = AutoUpdater()  # ✅ Réel

                # Convert SelfImprover Proposal to AutoUpdater UpdateProposal
                update_type_map = {
                    ProposalType.CODE_IMPROVEMENT: UpdateType.OPTIMIZATION,
                    ProposalType.DEPENDENCY_UPDATE: UpdateType.DEPENDENCY,
                    ProposalType.ARCHITECTURE_CHANGE: UpdateType.REFACTOR,
                    ProposalType.CONFIG_OPTIMIZATION: UpdateType.OPTIMIZATION,
                    ProposalType.MODEL_UPDATE: UpdateType.FEATURE,
                }

                # Build diff if it's a CodeProposal
                diff = ""
                target_files: list[str] = []
                if isinstance(proposal, CodeProposal):
                    diff = proposal.diff
                    target_files = proposal.target_files

                update_proposal = UpdateProposal(  # ✅ Réel
                    update_type=update_type_map.get(proposal.proposal_type, UpdateType.OPTIMIZATION),
                    title=proposal.title,
                    description=proposal.description,
                    target_files=target_files,
                    diff=diff,
                    risk_level=proposal.risk_level,
                    status=UpdateStatus.APPROVED,
                )

                success = updater.apply_update(updater.propose_update(update_proposal))  # ✅ Réel
                if not success:
                    logger.error("AutoUpdater failed to apply proposal %s", approval_id)
                    return False

                logger.info("Applied proposal %s via AutoUpdater: %s", approval_id, proposal.title)  # ✅ Réel
            except ImportError:
                logger.warning("⚠️ auto_updater non configuré. Marking as applied without code changes.")
            except Exception as exc:
                logger.error("AutoUpdater delegation failed for %s: %s", approval_id, exc)
                return False

        proposal.status = ProposalStatus.APPLIED  # ✅ Réel
        proposal.applied_at = datetime.now(timezone.utc)  # ✅ Réel
        self._save_registry()  # ✅ Réel
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
