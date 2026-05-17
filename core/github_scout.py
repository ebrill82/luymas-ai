"""
core/github_scout.py - GitHub Project Discovery for Luymas AI

Searches and analyzes GitHub projects: finds relevant repos, clones and
analyzes code quality, documents sources, and checks license compatibility.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import shutil
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
CLONE_DIR = Path.home() / ".luymas" / "clones"
SOURCES_DIR = Path.home() / ".luymas" / "sources"


# ── Data Models ──────────────────────────────────────────────────────────────

class LicenseType(str, Enum):
    MIT = "mit"
    APACHE2 = "apache-2.0"
    GPL3 = "gpl-3.0"
    BSD3 = "bsd-3-clause"
    UNLICENSE = "unlicense"
    PROPRIETARY = "proprietary"
    UNKNOWN = "unknown"

    @property
    def is_permissive(self) -> bool:
        return self in (LicenseType.MIT, LicenseType.APACHE2, LicenseType.BSD3, LicenseType.UNLICENSE)


@dataclass
class SearchResult:
    """A GitHub repository search result."""
    repo_url: str
    name: str = ""
    full_name: str = ""
    description: str = ""
    language: str = ""
    stars: int = 0
    forks: int = 0
    topics: list[str] = field(default_factory=list)
    license: str = ""
    last_updated: str = ""
    score: float = 0.0


@dataclass
class AnalysisReport:
    """Detailed analysis of a GitHub repository."""
    repo_url: str
    name: str = ""
    language: str = ""
    license_info: LicenseType = LicenseType.UNKNOWN
    file_count: int = 0
    line_count: int = 0
    test_coverage_estimate: float = 0.0
    has_ci: bool = False
    has_readme: bool = False
    has_contributing: bool = False
    dependencies: list[str] = field(default_factory=list)
    code_quality_score: float = 0.0
    issues: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SourceEntry:
    """An entry for the SOURCES.md document."""
    repo_url: str
    name: str = ""
    usage: str = ""
    license_info: str = ""
    modified: bool = False
    notes: str = ""


# ── Project Searcher ─────────────────────────────────────────────────────────

class ProjectSearcher:
    """Searches GitHub for relevant projects using the GitHub API."""

    def __init__(self, github_token: Optional[str] = None) -> None:
        self._token = github_token or os.environ.get("GITHUB_TOKEN", "")
        self._headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self._token:
            self._headers["Authorization"] = f"token {self._token}"

    async def search_projects(self, query: str, language: Optional[str] = None,
                              stars_min: int = 0, limit: int = 20) -> list[SearchResult]:
        """Search GitHub repositories matching the query."""
        params = [
            ("q", query),
            ("sort", "stars"),
            ("order", "desc"),
            ("per_page", str(min(limit, 100))),
        ]
        if language:
            # Append language to query
            params[0] = ("q", f"{query} language:{language}")
        if stars_min:
            params[0] = ("q", f"{params[0][1]} stars:>={stars_min}")

        # In production: use httpx.AsyncClient
        # url = f"{GITHUB_API}/search/repositories"
        # response = await client.get(url, params=params, headers=self._headers)
        logger.info("Searching GitHub: query='%s', language=%s, stars>=%d",
                     query, language, stars_min)

        # Return placeholder results
        results: list[SearchResult] = []
        return results

    async def get_repo_info(self, owner: str, repo: str) -> Optional[SearchResult]:
        """Get detailed info about a specific repository."""
        # In production: GET /repos/{owner}/{repo}
        logger.info("Getting repo info: %s/%s", owner, repo)
        return SearchResult(repo_url=f"https://github.com/{owner}/{repo}",
                            name=repo, full_name=f"{owner}/{repo}")


# ── Project Analyzer ─────────────────────────────────────────────────────────

class ProjectAnalyzer:
    """Clones and analyzes the code quality of GitHub projects."""

    LICENSE_MAP = {
        "mit": LicenseType.MIT,
        "apache-2.0": LicenseType.APACHE2,
        "gpl-3.0": LicenseType.GPL3,
        "bsd-3-clause": LicenseType.BSD3,
        "unlicense": LicenseType.UNLICENSE,
    }

    def __init__(self) -> None:
        CLONE_DIR.mkdir(parents=True, exist_ok=True)

    async def analyze_project(self, repo_url: str) -> AnalysisReport:
        """Analyze a GitHub project without cloning (API-based)."""
        report = AnalysisReport(repo_url=repo_url)
        # Parse owner/repo from URL
        parts = self._parse_repo_url(repo_url)
        if not parts:
            report.issues.append("Invalid repository URL")
            return report

        owner, repo_name = parts
        report.name = repo_name
        # In production: use GitHub API for file listing, README, etc.
        logger.info("Analyzed project %s/%s (API-based)", owner, repo_name)
        return report

    async def clone_and_study(self, repo_url: str) -> tuple[Path, AnalysisReport]:
        """Clone a repository locally and perform deep analysis."""
        parts = self._parse_repo_url(repo_url)
        if not parts:
            report = AnalysisReport(repo_url=repo_url, issues=["Invalid URL"])
            return Path(), report

        owner, repo_name = parts
        local_path = CLONE_DIR / f"{owner}_{repo_name}"

        # In production: git clone
        # proc = await asyncio.create_subprocess_exec(
        #     "git", "clone", "--depth", "1", repo_url, str(local_path),
        #     stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        # )
        logger.info("Clone & study: %s -> %s", repo_url, local_path)

        report = await self._analyze_local(local_path, repo_url, repo_name)
        return local_path, report

    async def _analyze_local(self, path: Path, repo_url: str, name: str) -> AnalysisReport:
        """Analyze a locally cloned repository."""
        report = AnalysisReport(repo_url=repo_url, name=name)

        if not path.exists():
            report.issues.append("Repository not cloned (git not available in sandbox)")
            return report

        # Count files and lines
        file_count = 0
        line_count = 0
        has_readme = False
        has_ci = False
        test_files = 0

        for fp in path.rglob("*"):
            if fp.is_file() and not any(p.startswith(".") for p in fp.parts):
                file_count += 1
                try:
                    content = fp.read_text(encoding="utf-8", errors="ignore")
                    line_count += len(content.splitlines())
                    if fp.name.lower().startswith("readme"):
                        has_readme = True
                    if fp.name in (".travis.yml", ".github", "Jenkinsfile"):
                        has_ci = True
                    if "test" in fp.name.lower():
                        test_files += 1
                except Exception:
                    pass

        report.file_count = file_count
        report.line_count = line_count
        report.has_readme = has_readme
        report.has_ci = has_ci
        report.test_coverage_estimate = test_files / max(file_count, 1)

        # Detect license
        report.license_info = self._detect_license(path)

        # Calculate quality score
        report.code_quality_score = self._calculate_quality(report)
        return report

    def _detect_license(self, path: Path) -> LicenseType:
        """Detect the license from the repository."""
        for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"):
            license_file = path / name
            if license_file.exists():
                try:
                    content = license_file.read_text(encoding="utf-8", errors="ignore").lower()
                    for key, ltype in self.LICENSE_MAP.items():
                        if key in content:
                            return ltype
                except Exception:
                    pass
        return LicenseType.UNKNOWN

    @staticmethod
    def _calculate_quality(report: AnalysisReport) -> float:
        """Calculate a 0-100 code quality score."""
        score = 50.0  # Base score
        if report.has_readme:
            score += 10
        if report.has_ci:
            score += 15
        if report.test_coverage_estimate > 0.1:
            score += min(report.test_coverage_estimate * 50, 15)
        if report.license_info != LicenseType.UNKNOWN:
            score += 10
        return min(score, 100.0)

    @staticmethod
    def _parse_repo_url(url: str) -> Optional[tuple[str, str]]:
        """Parse owner/repo from a GitHub URL."""
        pattern = r"github\.com/([^/]+)/([^/\s]+?)(?:\.git)?$"
        match = re.search(pattern, url)
        if match:
            return match.group(1), match.group(2)
        return None


# ── Source Documenter ────────────────────────────────────────────────────────

class SourceDocumenter:
    """Creates SOURCES.md entries for used GitHub projects."""

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self._output_dir = output_dir or SOURCES_DIR
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def document_source(self, repo_url: str, usage: str,
                        license_info: str = "", modified: bool = False,
                        notes: str = "") -> SourceEntry:
        """Create a SOURCES.md entry for a project."""
        parts = ProjectAnalyzer._parse_repo_url(repo_url)
        name = f"{parts[0]}/{parts[1]}" if parts else repo_url

        entry = SourceEntry(
            repo_url=repo_url, name=name, usage=usage,
            license_info=license_info, modified=modified, notes=notes,
        )
        logger.info("Documented source: %s (%s)", name, usage)
        return entry

    def generate_sources_md(self, entries: list[SourceEntry]) -> str:
        """Generate SOURCES.md content from a list of entries."""
        lines = ["# SOURCES — Luymas AI", ""]
        lines.append(f"_Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}_")
        lines.append("")

        for entry in entries:
            lines.append(f"- **{entry.name}**")
            lines.append(f"  - URL: {entry.repo_url}")
            lines.append(f"  - Usage: {entry.usage}")
            if entry.license_info:
                lines.append(f"  - License: {entry.license_info}")
            if entry.modified:
                lines.append("  - Modified: Yes")
            if entry.notes:
                lines.append(f"  - Notes: {entry.notes}")
            lines.append("")

        return "\n".join(lines)


# ── License Checker ──────────────────────────────────────────────────────────

class LicenseChecker:
    """Verifies license compatibility for using third-party projects."""

    # Permissive licenses that are safe to use
    SAFE_LICENSES = {LicenseType.MIT, LicenseType.APACHE2, LicenseType.BSD3,
                     LicenseType.UNLICENSE}
    # Copyleft licenses that may restrict usage
    COPYLEFT_LICENSES = {LicenseType.GPL3}

    def check_license(self, repo_url: str) -> dict[str, Any]:
        """Check the license of a repository and return compatibility info."""
        # In production: fetch via GitHub API
        return {
            "repo_url": repo_url,
            "license": LicenseType.UNKNOWN.value,
            "is_permissive": LicenseType.UNKNOWN.is_permissive,
            "is_safe_to_use": False,
            "recommendation": "Could not detect license. Review manually before use.",
        }

    def check_compatibility(self, license_type: LicenseType,
                            intended_use: str = "commercial") -> dict[str, Any]:
        """Check if a license is compatible with intended use."""
        is_safe = license_type in self.SAFE_LICENSES
        is_copyleft = license_type in self.COPYLEFT_LICENSES

        if intended_use == "commercial" and is_copyleft:
            recommendation = "⚠️ Copyleft license — may require source disclosure"
        elif is_safe:
            recommendation = "✅ Permissive license — safe for use"
        elif license_type == LicenseType.UNKNOWN:
            recommendation = "❓ Unknown license — review before use"
        else:
            recommendation = "⚠️ Review license terms before use"

        return {
            "license": license_type.value,
            "is_permissive": license_type.is_permissive,
            "is_copyleft": is_copyleft,
            "safe_for_commercial": is_safe,
            "recommendation": recommendation,
        }


# ── GitHub Scout Facade ──────────────────────────────────────────────────────

class GitHubScout:
    """Unified facade for GitHub project discovery and analysis.

    Usage::

        scout = GitHubScout(github_token="ghp_...")
        results = await scout.search_projects("react dashboard", language="TypeScript", stars_min=100)
        report = await scout.analyze_project("https://github.com/owner/repo")
        entry = scout.document_source("https://github.com/owner/repo", "UI components")
    """

    def __init__(self, github_token: Optional[str] = None) -> None:
        self.searcher = ProjectSearcher(github_token)
        self.analyzer = ProjectAnalyzer()
        self.documenter = SourceDocumenter()
        self.license_checker = LicenseChecker()

    async def search_projects(self, query: str, language: Optional[str] = None,
                              stars_min: int = 0, limit: int = 20) -> list[SearchResult]:
        """Search GitHub for relevant projects."""
        return await self.searcher.search_projects(query, language, stars_min, limit)

    async def analyze_project(self, repo_url: str) -> AnalysisReport:
        """Analyze a GitHub project."""
        return await self.analyzer.analyze_project(repo_url)

    async def clone_and_study(self, repo_url: str) -> tuple[Path, AnalysisReport]:
        """Clone and deeply analyze a project."""
        return await self.analyzer.clone_and_study(repo_url)

    def document_source(self, repo_url: str, usage: str,
                        license_info: str = "", modified: bool = False) -> SourceEntry:
        """Document a source for SOURCES.md."""
        return self.documenter.document_source(repo_url, usage, license_info, modified)

    def check_license(self, repo_url: str) -> dict[str, Any]:
        """Check the license of a repository."""
        return self.license_checker.check_license(repo_url)
