"""
core/experience_learner.py - Learning by Experience for Luymas AI

Post-project learning system that analyzes completed projects, detects
success/failure patterns, extracts actionable lessons, updates the
KNOWLEDGE_MESH.md, and provides pre-project advisory based on past experience.
"""

from __future__ import annotations

import json
import logging
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

EXPERIENCE_DB_PATH = Path.home() / ".luymas" / "experience_db.json"


# ── Data Models ──────────────────────────────────────────────────────────────

class ProjectOutcome(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    CANCELLED = "cancelled"


class PatternType(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    ANTI_PATTERN = "anti_pattern"
    BEST_PRACTICE = "best_practice"


@dataclass
class Retrospective:
    """Post-project retrospective analysis."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    project_id: str = ""
    project_name: str = ""
    outcome: ProjectOutcome = ProjectOutcome.SUCCESS
    duration_hours: float = 0.0
    what_went_well: list[str] = field(default_factory=list)
    what_went_wrong: list[str] = field(default_factory=list)
    what_to_improve: list[str] = field(default_factory=list)
    key_decisions: list[dict[str, str]] = field(default_factory=list)
    tech_stack_used: list[str] = field(default_factory=list)
    agent_performance: dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Pattern:
    """A detected success or failure pattern."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    pattern_type: PatternType = PatternType.BEST_PRACTICE
    name: str = ""
    description: str = ""
    frequency: int = 1
    confidence: float = 0.0
    examples: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class Lesson:
    """An actionable lesson extracted from experience."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    description: str = ""
    category: str = ""
    severity: str = "info"  # info, warning, critical
    source_project: str = ""
    actionable: bool = True
    tags: list[str] = field(default_factory=list)


@dataclass
class Recommendation:
    """A pre-project recommendation based on past experience."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    description: str = ""
    confidence: float = 0.0
    based_on_projects: list[str] = field(default_factory=list)
    based_on_patterns: list[str] = field(default_factory=list)
    priority: str = "medium"  # low, medium, high
    category: str = ""


# ── Retrospective Analyzer ───────────────────────────────────────────────────

class RetrospectiveAnalyzer:
    """Analyzes completed projects for retrospective insights."""

    def analyze_project(self, project_data: dict[str, Any]) -> Retrospective:
        """Create a retrospective from project data."""
        retro = Retrospective(
            project_id=project_data.get("project_id", ""),
            project_name=project_data.get("project_name", ""),
            outcome=ProjectOutcome(project_data.get("outcome", "success")),
            duration_hours=project_data.get("duration_hours", 0.0),
            what_went_well=project_data.get("what_went_well", []),
            what_went_wrong=project_data.get("what_went_wrong", []),
            what_to_improve=project_data.get("what_to_improve", []),
            key_decisions=project_data.get("key_decisions", []),
            tech_stack_used=project_data.get("tech_stack_used", []),
            agent_performance=project_data.get("agent_performance", {}),
        )

        # Auto-generate improvements if not provided
        if not retro.what_to_improve and retro.what_went_wrong:
            retro.what_to_improve = [
                f"Address: {issue}" for issue in retro.what_went_wrong
            ]

        # Calculate overall performance score
        score = self._calculate_performance_score(retro)
        retro.agent_performance["_overall"] = score

        logger.info("Retrospective for %s: outcome=%s, score=%.2f",
                     retro.project_name, retro.outcome.value, score)
        return retro

    @staticmethod
    def _calculate_performance_score(retro: Retrospective) -> float:
        """Calculate a 0-1 performance score from retrospective data."""
        score = 0.5  # Start neutral

        if retro.outcome == ProjectOutcome.SUCCESS:
            score += 0.3
        elif retro.outcome == ProjectOutcome.FAILURE:
            score -= 0.3

        # More things going well = higher score
        if retro.what_went_well:
            score += min(len(retro.what_went_well) * 0.05, 0.2)

        # More things going wrong = lower score
        if retro.what_went_wrong:
            score -= min(len(retro.what_went_wrong) * 0.05, 0.2)

        return max(0.0, min(1.0, score))


# ── Pattern Detector ─────────────────────────────────────────────────────────

class PatternDetector:
    """Identifies success and failure patterns across projects."""

    def __init__(self) -> None:
        self._retrospectives: list[Retrospective] = []

    def add_retrospective(self, retro: Retrospective) -> None:
        """Add a retrospective for pattern detection."""
        self._retrospectives.append(retro)

    def detect_patterns(self) -> list[Pattern]:
        """Detect recurring patterns across all retrospectives."""
        patterns: list[Pattern] = []

        # 1. Detect success patterns (things that went well repeatedly)
        well_counter: Counter[str] = Counter()
        for retro in self._retrospectives:
            for item in retro.what_went_well:
                well_counter[item.lower().strip()] += 1

        for item, count in well_counter.most_common(20):
            if count >= 2:  # Appeared at least twice
                confidence = min(count / max(len(self._retrospectives), 1), 1.0)
                patterns.append(Pattern(
                    pattern_type=PatternType.BEST_PRACTICE,
                    name=f"Repeated success: {item[:50]}",
                    description=item,
                    frequency=count,
                    confidence=confidence,
                    tags=["success", "repeated"],
                ))

        # 2. Detect failure patterns (things that went wrong repeatedly)
        wrong_counter: Counter[str] = Counter()
        for retro in self._retrospectives:
            for item in retro.what_went_wrong:
                wrong_counter[item.lower().strip()] += 1

        for item, count in wrong_counter.most_common(20):
            if count >= 2:
                confidence = min(count / max(len(self._retrospectives), 1), 1.0)
                patterns.append(Pattern(
                    pattern_type=PatternType.ANTI_PATTERN,
                    name=f"Repeated failure: {item[:50]}",
                    description=item,
                    frequency=count,
                    confidence=confidence,
                    tags=["failure", "repeated"],
                ))

        # 3. Detect tech stack correlations with outcomes
        tech_outcomes: dict[str, list[ProjectOutcome]] = defaultdict(list)
        for retro in self._retrospectives:
            for tech in retro.tech_stack_used:
                tech_outcomes[tech.lower()].append(retro.outcome)

        for tech, outcomes in tech_outcomes.items():
            success_rate = sum(1 for o in outcomes if o == ProjectOutcome.SUCCESS) / len(outcomes)
            if success_rate >= 0.8 and len(outcomes) >= 2:
                patterns.append(Pattern(
                    pattern_type=PatternType.SUCCESS,
                    name=f"High-success tech: {tech}",
                    description=f"Technology '{tech}' has {success_rate:.0%} success rate across {len(outcomes)} projects",
                    frequency=len(outcomes),
                    confidence=success_rate,
                    tags=["tech_stack", "success"],
                ))
            elif success_rate <= 0.3 and len(outcomes) >= 2:
                patterns.append(Pattern(
                    pattern_type=PatternType.ANTI_PATTERN,
                    name=f"Low-success tech: {tech}",
                    description=f"Technology '{tech}' has only {success_rate:.0%} success rate across {len(outcomes)} projects",
                    frequency=len(outcomes),
                    confidence=1.0 - success_rate,
                    tags=["tech_stack", "failure"],
                ))

        logger.info("Detected %d patterns across %d retrospectives",
                     len(patterns), len(self._retrospectives))
        return patterns


# ── Lesson Extractor ─────────────────────────────────────────────────────────

class LessonExtractor:
    """Extracts actionable lessons from project data."""

    def extract_lessons(self, project_data: dict[str, Any]) -> list[Lesson]:
        """Extract lessons from a single project's data."""
        lessons: list[Lesson] = []
        project_name = project_data.get("project_name", "unknown")

        # Extract from what went wrong → critical lessons
        for item in project_data.get("what_went_wrong", []):
            lessons.append(Lesson(
                title=f"Avoid: {item[:60]}",
                description=item,
                category="failure_prevention",
                severity="warning",
                source_project=project_name,
                tags=["failure", "prevention"],
            ))

        # Extract from what went well → best practice lessons
        for item in project_data.get("what_went_well", []):
            lessons.append(Lesson(
                title=f"Best practice: {item[:60]}",
                description=item,
                category="best_practice",
                severity="info",
                source_project=project_name,
                tags=["success", "best_practice"],
            ))

        # Extract from improvements → actionable recommendations
        for item in project_data.get("what_to_improve", []):
            lessons.append(Lesson(
                title=f"Improve: {item[:60]}",
                description=item,
                category="improvement",
                severity="info",
                source_project=project_name,
                actionable=True,
                tags=["improvement"],
            ))

        logger.info("Extracted %d lessons from project '%s'", len(lessons), project_name)
        return lessons


# ── Knowledge Updater ────────────────────────────────────────────────────────

class KnowledgeUpdater:
    """Updates KNOWLEDGE_MESH.md with new lessons and patterns."""

    MESH_PATH = Path.home() / ".luymas" / "KNOWLEDGE_MESH.md"

    def update_knowledge_mesh(self, lessons: list[Lesson],
                              patterns: Optional[list[Pattern]] = None) -> bool:
        """Append new lessons and patterns to the knowledge mesh."""
        self.MESH_PATH.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = []
        if self.MESH_PATH.exists():
            existing = self.MESH_PATH.read_text(encoding="utf-8")
            lines = existing.splitlines()

        # Add new lessons section
        lines.append("\n## Lessons Learned — Auto-Generated\n")
        for lesson in lessons:
            lines.append(f"### {lesson.title}")
            lines.append(f"- **Category**: {lesson.category}")
            lines.append(f"- **Severity**: {lesson.severity}")
            lines.append(f"- **Source**: {lesson.source_project}")
            lines.append(f"- **Description**: {lesson.description}")
            if lesson.tags:
                lines.append(f"- **Tags**: {', '.join(lesson.tags)}")
            lines.append("")

        # Add patterns if provided
        if patterns:
            lines.append("## Detected Patterns\n")
            for pattern in patterns:
                emoji = "✅" if pattern.pattern_type in (PatternType.SUCCESS, PatternType.BEST_PRACTICE) else "⚠️"
                lines.append(f"- {emoji} **{pattern.name}** (confidence: {pattern.confidence:.0%})")
                lines.append(f"  - {pattern.description}")
            lines.append("")

        self.MESH_PATH.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Updated KNOWLEDGE_MESH.md with %d lessons", len(lessons))
        return True


# ── Pre-Project Advisor ──────────────────────────────────────────────────────

class PreProjectAdvisor:
    """Advises on new projects based on past experience."""

    def __init__(self, pattern_detector: PatternDetector) -> None:
        self._pattern_detector = pattern_detector

    def advise_on_project(self, context: str,
                          tech_stack: Optional[list[str]] = None) -> list[Recommendation]:
        """Generate recommendations for a new project based on experience."""
        recommendations: list[Recommendation] = []
        patterns = self._pattern_detector.detect_patterns()

        context_lower = context.lower()

        # Match patterns to the current context
        for pattern in patterns:
            # Simple keyword matching
            pattern_words = set(pattern.description.lower().split())
            context_words = set(context_lower.split())
            overlap = len(pattern_words & context_words)

            if overlap > 0 or (tech_stack and any(
                t.lower() in pattern.description.lower() for t in tech_stack
            )):
                if pattern.pattern_type in (PatternType.ANTI_PATTERN, PatternType.FAILURE):
                    rec = Recommendation(
                        title=f"Avoid: {pattern.name}",
                        description=f"Based on {pattern.frequency} past occurrences: {pattern.description}",
                        confidence=pattern.confidence,
                        based_on_patterns=[pattern.id],
                        priority="high" if pattern.confidence > 0.7 else "medium",
                        category="risk_mitigation",
                    )
                    recommendations.append(rec)

                elif pattern.pattern_type in (PatternType.BEST_PRACTICE, PatternType.SUCCESS):
                    rec = Recommendation(
                        title=f"Adopt: {pattern.name}",
                        description=f"Proven successful {pattern.frequency} times: {pattern.description}",
                        confidence=pattern.confidence,
                        based_on_patterns=[pattern.id],
                        priority="medium",
                        category="best_practice",
                    )
                    recommendations.append(rec)

        # Sort by confidence
        recommendations.sort(key=lambda r: r.confidence, reverse=True)

        # General recommendations if few context-specific ones
        if len(recommendations) < 2:
            recommendations.append(Recommendation(
                title="Start with thorough planning phase",
                description="Historical data shows projects with detailed planning have higher success rates",
                confidence=0.8,
                priority="medium",
                category="process",
            ))

        logger.info("Generated %d recommendations for new project", len(recommendations))
        return recommendations


# ── Experience Learner Facade ────────────────────────────────────────────────

class ExperienceLearner:
    """Unified facade for the learning-by-experience system.

    Usage::

        learner = ExperienceLearner()
        retro = learner.analyze_project(project_data)
        patterns = learner.detect_patterns()
        lessons = learner.extract_lessons(project_data)
        learner.update_knowledge_mesh(lessons, patterns)
        recs = learner.advise_on_project("Build a SaaS dashboard", ["React", "Node"])
    """

    def __init__(self) -> None:
        self.retrospective_analyzer = RetrospectiveAnalyzer()
        self.pattern_detector = PatternDetector()
        self.lesson_extractor = LessonExtractor()
        self.knowledge_updater = KnowledgeUpdater()
        self.pre_project_advisor = PreProjectAdvisor(self.pattern_detector)

    def analyze_project(self, project_data: dict[str, Any]) -> Retrospective:
        """Analyze a completed project and create a retrospective."""
        retro = self.retrospective_analyzer.analyze_project(project_data)
        self.pattern_detector.add_retrospective(retro)
        self._save_experience(retro)
        return retro

    def detect_patterns(self) -> list[Pattern]:
        """Detect patterns across all analyzed projects."""
        return self.pattern_detector.detect_patterns()

    def extract_lessons(self, project_data: dict[str, Any]) -> list[Lesson]:
        """Extract actionable lessons from project data."""
        return self.lesson_extractor.extract_lessons(project_data)

    def update_knowledge_mesh(self, lessons: list[Lesson],
                              patterns: Optional[list[Pattern]] = None) -> bool:
        """Update KNOWLEDGE_MESH.md with new insights."""
        return self.knowledge_updater.update_knowledge_mesh(lessons, patterns)

    def advise_on_project(self, context: str,
                          tech_stack: Optional[list[str]] = None) -> list[Recommendation]:
        """Get recommendations for a new project based on experience."""
        return self.pre_project_advisor.advise_on_project(context, tech_stack)

    def _save_experience(self, retro: Retrospective) -> None:
        """Persist retrospective to disk."""
        EXPERIENCE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        data: list[dict] = []
        if EXPERIENCE_DB_PATH.exists():
            try:
                data = json.loads(EXPERIENCE_DB_PATH.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, TypeError):
                pass
        data.append({
            "id": retro.id,
            "project_id": retro.project_id,
            "project_name": retro.project_name,
            "outcome": retro.outcome.value,
            "what_went_well": retro.what_went_well,
            "what_went_wrong": retro.what_went_wrong,
            "what_to_improve": retro.what_to_improve,
            "tech_stack_used": retro.tech_stack_used,
            "created_at": retro.created_at.isoformat(),
        })
        EXPERIENCE_DB_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
