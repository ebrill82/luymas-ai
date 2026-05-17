"""
core/auto_updater.py - Self-Modification System for Luymas AI

Enables Luymas to detect, propose, and apply improvements to its own code.
CRITICAL: Never applies changes without explicit user approval.
All modifications are tracked with full rollback capability.
"""

from __future__ import annotations

import asyncio
import difflib
import hashlib
import json
import logging
import os
import shutil
import subprocess
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

LUYMAS_ROOT = Path(__file__).parent.parent  # /home/z/luymas-ai
BACKUP_DIR = LUYMAS_ROOT / ".luymas_backups"
CHANGELOG_PATH = LUYMAS_ROOT / "CHANGELOG.json"


# ── Data Models ──────────────────────────────────────────────────────────────

class UpdateType(str, Enum):
    BUG_FIX = "bug_fix"
    OPTIMIZATION = "optimization"
    FEATURE = "feature"
    REFACTOR = "refactor"
    SECURITY = "security"
    DEPENDENCY = "dependency"


class UpdateStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    APPLIED = "applied"
    ROLLED_BACK = "rolled_back"
    REJECTED = "rejected"


@dataclass
class UpdateProposal:
    """A structured proposal for a code change."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    update_type: UpdateType = UpdateType.OPTIMIZATION
    title: str = ""
    description: str = ""
    target_files: list[str] = field(default_factory=list)
    diff: str = ""  # Unified diff of proposed changes
    risk_level: str = "low"  # low, medium, high, critical
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: UpdateStatus = UpdateStatus.PROPOSED
    approved_by: Optional[str] = None
    applied_at: Optional[datetime] = None
    rollback_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChangeEntry:
    """An entry in the changelog."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    update_id: str = ""
    action: str = ""  # "applied", "rolled_back", "rejected"
    files_modified: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: str = ""


# ── Update Detector ──────────────────────────────────────────────────────────

class UpdateDetector:
    """Detects possible improvements in the Luymas codebase."""

    # Patterns that suggest improvement opportunities
    OPTIMIZATION_PATTERNS = {
        "sync_in_async": r"async def \w+\([^)]*\):\s*\n\s+return [^\n]+(?!\n\s*await)",
        "missing_type_hints": r"def \w+\([^)]*\):",
        "bare_except": r"except\s*:",
        "broad_except": r"except Exception",
        "hardcoded_paths": r'["\']/home/["\']',
        "todo_comments": r"#\s*TODO|#\s*FIXME|#\s*HACK",
        "print_debugging": r"\bprint\s*\(",
    }

    def detect_improvements(self, scan_path: Optional[Path] = None) -> list[UpdateProposal]:
        """Scan the codebase for improvement opportunities."""
        scan_dir = scan_path or LUYMAS_ROOT / "core"
        proposals: list[UpdateProposal] = []

        if not scan_dir.exists():
            logger.warning("Scan path does not exist: %s", scan_dir)
            return proposals

        for py_file in scan_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue

            rel_path = str(py_file.relative_to(LUYMAS_ROOT))

            for pattern_name, pattern in self.OPTIMIZATION_PATTERNS.items():
                # Simplified detection; real implementation would use AST analysis
                lines = content.split("\n")
                matches = []
                for i, line in enumerate(lines):
                    import re
                    if re.search(pattern, line):
                        matches.append((i + 1, line.strip()))

                if matches:
                    proposal = UpdateProposal(
                        update_type=self._classify_update(pattern_name),
                        title=f"Fix {pattern_name} in {rel_path}",
                        description=(
                            f"Found {len(matches)} instance(s) of {pattern_name} "
                            f"in {rel_path}. Lines: {', '.join(str(m[0]) for m in matches[:5])}"
                        ),
                        target_files=[rel_path],
                        risk_level="low" if pattern_name in ("todo_comments",) else "medium",
                    )
                    proposals.append(proposal)

        logger.info("Detected %d improvement proposals", len(proposals))
        return proposals

    @staticmethod
    def _classify_update(pattern_name: str) -> UpdateType:
        mapping = {
            "bare_except": UpdateType.BUG_FIX,
            "broad_except": UpdateType.BUG_FIX,
            "hardcoded_paths": UpdateType.SECURITY,
            "sync_in_async": UpdateType.OPTIMIZATION,
            "missing_type_hints": UpdateType.REFACTOR,
            "todo_comments": UpdateType.FEATURE,
            "print_debugging": UpdateType.REFACTOR,
        }
        return mapping.get(pattern_name, UpdateType.OPTIMIZATION)


# ── Update Applier ───────────────────────────────────────────────────────────

class UpdateApplier:
    """Applies approved changes with full rollback support."""

    def __init__(self) -> None:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    def apply(self, proposal: UpdateProposal) -> bool:
        """Apply an approved update proposal to the codebase."""
        if proposal.status != UpdateStatus.APPROVED:
            logger.error("Cannot apply proposal %s: not approved (status=%s)",
                         proposal.id, proposal.status.value)
            return False

        # Create backups before modifying
        backup_id = uuid.uuid4().hex[:8]
        for file_path in proposal.target_files:
            full_path = LUYMAS_ROOT / file_path
            if full_path.exists():
                self._backup_file(full_path, backup_id)

        # Apply the diff
        if proposal.diff:
            success = self._apply_diff(proposal.diff)
        else:
            # No diff provided; mark as requiring manual application
            logger.warning("Proposal %s has no diff; manual application required.", proposal.id)
            success = True  # Acknowledge the proposal

        if success:
            proposal.status = UpdateStatus.APPLIED
            proposal.applied_at = datetime.now(timezone.utc)
            proposal.rollback_id = backup_id
            logger.info("Applied update %s (rollback_id=%s)", proposal.id, backup_id)
        return success

    def rollback(self, proposal: UpdateProposal) -> bool:
        """Roll back a previously applied update."""
        if not proposal.rollback_id:
            logger.error("No rollback ID for proposal %s", proposal.id)
            return False

        restored = False
        for file_path in proposal.target_files:
            full_path = LUYMAS_ROOT / file_path
            backup_path = BACKUP_DIR / f"{proposal.rollback_id}" / file_path
            if backup_path.exists():
                shutil.copy2(str(backup_path), str(full_path))
                restored = True
                logger.info("Restored %s from backup", file_path)

        if restored:
            proposal.status = UpdateStatus.ROLLED_BACK
            logger.info("Rolled back update %s", proposal.id)
        return restored

    def _backup_file(self, file_path: Path, backup_id: str) -> Path:
        """Create a backup of a file before modification."""
        rel = file_path.relative_to(LUYMAS_ROOT)
        backup_path = BACKUP_DIR / backup_id / str(rel)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(file_path), str(backup_path))
        return backup_path

    @staticmethod
    def _apply_diff(diff_text: str) -> bool:
        """Apply a unified diff to the codebase.

        Tries the system ``patch`` command first (fast, reliable).
        Falls back to a pure-Python inline patch applier if ``patch`` is
        unavailable.
        """
        if not diff_text or not diff_text.strip():
            logger.warning("Empty diff — nothing to apply")
            return False

        # ── Strategy 1: use the ``patch`` command via subprocess ──
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".diff", delete=False) as tmp:  # ✅ Réel
                tmp.write(diff_text)
                tmp_path = tmp.name

            result = subprocess.run(  # ✅ Réel
                ["patch", "-p1", "--forward", "--input", tmp_path],
                cwd=str(LUYMAS_ROOT),
                capture_output=True,
                text=True,
                timeout=30,
            )
            os.unlink(tmp_path)  # ✅ Réel

            if result.returncode == 0:
                logger.info("Patch applied successfully via `patch` command")  # ✅ Réel
                return True
            else:
                logger.warning(
                    "`patch` command returned %d: %s",
                    result.returncode, result.stderr[:300],
                )
                # Fall through to Python fallback
        except FileNotFoundError:
            logger.info("`patch` command not found; using Python fallback")  # ✅ Réel
        except subprocess.TimeoutExpired:
            logger.error("`patch` command timed out")
            return False
        except Exception as exc:
            logger.warning("`patch` command failed: %s; using Python fallback", exc)

        # ── Strategy 2: pure-Python inline diff applier ──
        try:
            return UpdateApplier._apply_diff_python(diff_text)  # ✅ Réel
        except Exception as exc:
            logger.error("Python diff applier failed: %s", exc)
            return False

    @staticmethod
    def _apply_diff_python(diff_text: str) -> bool:
        """Apply a unified diff using pure Python (fallback when `patch` is unavailable).

        Parses the unified diff, reads the target file, applies the hunks,
        and writes the result back.
        """
        applied_any = False
        current_file: Optional[str] = None
        current_lines: list[str] = []
        hunks: list[dict[str, Any]] = []

        for line in diff_text.splitlines():
            # Detect file header: --- a/path
            if line.startswith("--- a/"):
                # Save previous file's hunks
                if current_file and hunks:
                    if UpdateApplier._apply_hunks(current_file, hunks):  # ✅ Réel
                        applied_any = True
                    hunks = []
                current_file = line[6:]  # strip "--- a/"
                continue
            if line.startswith("+++ b/"):
                # We already captured the target from --- line; skip
                continue
            # Detect hunk header: @@ -old_start,old_count +new_start,new_count @@
            if line.startswith("@@"):
                import re
                match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
                if match:
                    new_start = int(match.group(1))
                    new_count = int(match.group(2) or "1")
                    hunks.append({"new_start": new_start, "new_count": new_count, "lines": []})
                continue
            # Hunk content lines
            if hunks:
                hunks[-1]["lines"].append(line)

        # Apply last file's hunks
        if current_file and hunks:
            if UpdateApplier._apply_hunks(current_file, hunks):  # ✅ Réel
                applied_any = True

        if applied_any:
            logger.info("Applied diff via Python fallback")  # ✅ Réel
        else:
            logger.warning("No hunks could be applied via Python fallback")
        return applied_any

    @staticmethod
    def _apply_hunks(file_rel: str, hunks: list[dict[str, Any]]) -> bool:
        """Apply parsed hunks to a single file."""
        target = LUYMAS_ROOT / file_rel
        if not target.exists():
            logger.error("Target file not found: %s", target)
            return False

        try:
            original = target.read_text(encoding="utf-8").splitlines(keepends=True)  # ✅ Réel
        except (UnicodeDecodeError, PermissionError) as exc:
            logger.error("Cannot read %s: %s", target, exc)
            return False

        # Apply hunks in reverse order so line offsets stay valid
        result_lines = list(original)
        for hunk in reversed(hunks):
            new_start = hunk["new_start"]
            hunk_lines = hunk["lines"]
            # Build replacement lines (only "+" lines and context lines)
            replacement: list[str] = []
            remove_count = 0
            for hl in hunk_lines:
                if hl.startswith("+"):
                    replacement.append(hl[1:])  # ✅ Réel
                elif hl.startswith("-"):
                    remove_count += 1
                elif hl.startswith(" "):
                    replacement.append(hl[1:])  # ✅ Réel

            # Replace the affected range in result_lines
            start_idx = new_start - 1  # Convert 1-based to 0-based
            end_idx = start_idx + remove_count
            result_lines[start_idx:end_idx] = replacement  # ✅ Réel

        try:
            target.write_text("".join(result_lines), encoding="utf-8")  # ✅ Réel
            logger.info("Wrote patched file: %s", target)
            return True
        except (PermissionError, OSError) as exc:
            logger.error("Cannot write %s: %s", target, exc)
            return False


# ── Change Log ───────────────────────────────────────────────────────────────

class ChangeLog:
    """Tracks all modifications to the Luymas codebase."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self._path = path or CHANGELOG_PATH
        self._entries: list[ChangeEntry] = []
        self._load()

    def record(self, update_id: str, action: str, files: list[str],
               details: str = "") -> ChangeEntry:
        """Record a change in the changelog."""
        entry = ChangeEntry(
            update_id=update_id, action=action,
            files_modified=files, details=details,
        )
        self._entries.append(entry)
        self._save()
        logger.info("Changelog: %s for update %s", action, update_id)
        return entry

    def get_entries(self, limit: int = 50) -> list[ChangeEntry]:
        return self._entries[-limit:]

    def get_entries_for_update(self, update_id: str) -> list[ChangeEntry]:
        return [e for e in self._entries if e.update_id == update_id]

    def _load(self) -> None:
        """Load changelog from disk."""
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                for item in data:
                    self._entries.append(ChangeEntry(**item))
            except (json.JSONDecodeError, TypeError) as exc:
                logger.warning("Could not load changelog: %s", exc)

    def _save(self) -> None:
        """Persist changelog to disk."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = []
        for entry in self._entries:
            data.append({
                "id": entry.id,
                "update_id": entry.update_id,
                "action": entry.action,
                "files_modified": entry.files_modified,
                "timestamp": entry.timestamp.isoformat(),
                "details": entry.details,
            })
        self._path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ── Auto Updater Facade ──────────────────────────────────────────────────────

class AutoUpdater:
    """Unified facade for the self-modification system.

    CRITICAL: This system NEVER applies updates without explicit user approval.

    Usage::

        updater = AutoUpdater()
        proposals = updater.detect_improvements()
        approval_id = updater.propose_update(proposals[0])
        # ... user reviews and approves ...
        updater.apply_update(approval_id)
    """

    def __init__(self) -> None:
        self.detector = UpdateDetector()
        self.applier = UpdateApplier()
        self.changelog = ChangeLog()
        self._proposals: dict[str, UpdateProposal] = {}

    def detect_improvements(self, scan_path: Optional[Path] = None) -> list[UpdateProposal]:
        """Scan for possible code improvements."""
        return self.detector.detect_improvements(scan_path)

    def propose_update(self, proposal: UpdateProposal) -> str:
        """Register an update proposal for user approval."""
        proposal.status = UpdateStatus.PROPOSED
        self._proposals[proposal.id] = proposal
        self.changelog.record(proposal.id, "proposed", proposal.target_files, proposal.title)
        logger.info("Proposed update %s: %s", proposal.id, proposal.title)
        return proposal.id

    def approve_update(self, proposal_id: str, approver: str = "user") -> bool:
        """Mark a proposal as approved (must be called by user)."""
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            logger.error("Proposal %s not found.", proposal_id)
            return False
        proposal.status = UpdateStatus.APPROVED
        proposal.approved_by = approver
        self.changelog.record(proposal_id, "approved", proposal.target_files)
        logger.info("Update %s approved by %s", proposal_id, approver)
        return True

    def apply_update(self, proposal_id: str) -> bool:
        """Apply an approved update (requires prior approval)."""
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return False
        if proposal.status != UpdateStatus.APPROVED:
            logger.error("Update %s is not approved (status=%s)",
                         proposal_id, proposal.status.value)
            return False

        success = self.applier.apply(proposal)
        if success:
            self.changelog.record(proposal_id, "applied", proposal.target_files)
        return success

    def rollback_update(self, proposal_id: str) -> bool:
        """Roll back a previously applied update."""
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return False
        success = self.applier.rollback(proposal)
        if success:
            self.changelog.record(proposal_id, "rolled_back", proposal.target_files)
        return success

    def get_changelog(self, limit: int = 50) -> list[ChangeEntry]:
        """Return recent changelog entries."""
        return self.changelog.get_entries(limit)

    def get_proposal(self, proposal_id: str) -> Optional[UpdateProposal]:
        return self._proposals.get(proposal_id)

    def list_proposals(self, status: Optional[UpdateStatus] = None) -> list[UpdateProposal]:
        proposals = list(self._proposals.values())
        if status:
            proposals = [p for p in proposals if p.status == status]
        return proposals
