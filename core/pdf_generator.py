"""
core/pdf_generator.py - PDF Report Generator for Luymas AI

PDG-only PDF generation system. Creates professional project reports
with sections for executive summary, architecture, tests, security,
deployment, sources, and lessons learned.
"""

from __future__ import annotations

import io
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Attempt imports for PDF generation; provide graceful fallbacks
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image as RLImage, ListFlowable, ListItem,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

REPORTS_DIR = Path.home() / ".luymas" / "reports"


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class ProjectData:
    """Aggregate project data for report generation."""
    project_name: str = ""
    project_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    description: str = ""
    start_date: str = ""
    end_date: str = ""
    tech_stack: list[str] = field(default_factory=list)
    architecture_decisions: list[dict[str, str]] = field(default_factory=list)
    test_results: dict[str, Any] = field(default_factory=dict)
    security_scan: dict[str, Any] = field(default_factory=dict)
    deployment_info: dict[str, Any] = field(default_factory=dict)
    sources: list[dict[str, str]] = field(default_factory=list)
    lessons_learned: list[str] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)
    agents_involved: list[str] = field(default_factory=list)
    custom_sections: dict[str, str] = field(default_factory=dict)


# ── Section Builders ─────────────────────────────────────────────────────────

class SectionBuilder:
    """Base class for PDF section builders."""

    @staticmethod
    def _title_style() -> Any:
        if not HAS_REPORTLAB:
            return None
        return ParagraphStyle(
            "SectionTitle", parent=getSampleStyleSheet()["Heading2"],
            fontSize=16, spaceAfter=12, textColor=HexColor("#1a1a2e"),
        )

    @staticmethod
    def _body_style() -> Any:
        if not HAS_REPORTLAB:
            return None
        return ParagraphStyle(
            "SectionBody", parent=getSampleStyleSheet()["Normal"],
            fontSize=10, spaceAfter=8, leading=14,
            alignment=TA_JUSTIFY,
        )


class ExecutiveSummary(SectionBuilder):
    """Builds the executive summary section."""

    def build(self, data: ProjectData) -> list[Any]:
        elements: list[Any] = []
        if not HAS_REPORTLAB:
            return elements
        elements.append(Paragraph("Executive Summary", self._title_style()))
        elements.append(Spacer(1, 8))

        summary_text = (
            f"<b>Project:</b> {data.project_name}<br/>"
            f"<b>Period:</b> {data.start_date} — {data.end_date}<br/>"
            f"<b>Team:</b> {', '.join(data.agents_involved)}<br/><br/>"
            f"{data.description}"
        )
        elements.append(Paragraph(summary_text, self._body_style()))

        if data.tech_stack:
            stack_text = "<b>Tech Stack:</b> " + ", ".join(data.tech_stack)
            elements.append(Paragraph(stack_text, self._body_style()))

        return elements


class ArchitectureReport(SectionBuilder):
    """Builds the architecture decisions section."""

    def build(self, data: ProjectData) -> list[Any]:
        elements: list[Any] = []
        if not HAS_REPORTLAB:
            return elements
        elements.append(Paragraph("Architecture Decisions", self._title_style()))
        elements.append(Spacer(1, 8))

        for decision in data.architecture_decisions:
            title = decision.get("title", "Untitled Decision")
            rationale = decision.get("rationale", "No rationale provided.")
            elements.append(Paragraph(f"<b>{title}</b>", self._body_style()))
            elements.append(Paragraph(rationale, self._body_style()))
            elements.append(Spacer(1, 6))

        return elements


class TestResultsReport(SectionBuilder):
    """Builds the test outcomes section."""

    def build(self, data: ProjectData) -> list[Any]:
        elements: list[Any] = []
        if not HAS_REPORTLAB:
            return elements
        elements.append(Paragraph("Test Results", self._title_style()))
        elements.append(Spacer(1, 8))

        results = data.test_results
        if not results:
            elements.append(Paragraph("No test results available.", self._body_style()))
            return elements

        rows = [["Metric", "Value"]]
        for key, val in results.items():
            rows.append([key, str(val)])

        table = Table(rows, colWidths=[3 * inch, 3 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        return elements


class SecurityReport(SectionBuilder):
    """Builds the security scan results section."""

    def build(self, data: ProjectData) -> list[Any]:
        elements: list[Any] = []
        if not HAS_REPORTLAB:
            return elements
        elements.append(Paragraph("Security Scan Results", self._title_style()))
        elements.append(Spacer(1, 8))

        scan = data.security_scan
        if not scan:
            elements.append(Paragraph("No security scan data available.", self._body_style()))
            return elements

        vulnerabilities = scan.get("vulnerabilities", [])
        if vulnerabilities:
            for vuln in vulnerabilities:
                severity = vuln.get("severity", "unknown")
                desc = vuln.get("description", "")
                color = {"high": "#e74c3c", "medium": "#f39c12", "low": "#27ae60"}.get(severity, "#95a5a6")
                elements.append(Paragraph(
                    f'<font color="{color}"><b>[{severity.upper()}]</b></font> {desc}',
                    self._body_style(),
                ))
        else:
            elements.append(Paragraph("✅ No vulnerabilities detected.", self._body_style()))

        return elements


class DeploymentReport(SectionBuilder):
    """Builds the deployment details section."""

    def build(self, data: ProjectData) -> list[Any]:
        elements: list[Any] = []
        if not HAS_REPORTLAB:
            return elements
        elements.append(Paragraph("Deployment Details", self._title_style()))
        elements.append(Spacer(1, 8))

        deploy = data.deployment_info
        if not deploy:
            elements.append(Paragraph("No deployment information available.", self._body_style()))
            return elements

        rows = [["Detail", "Value"]]
        for key, val in deploy.items():
            rows.append([key.replace("_", " ").title(), str(val)])

        table = Table(rows, colWidths=[3 * inch, 3 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))
        elements.append(table)
        return elements


class SourcesReport(SectionBuilder):
    """Builds the GitHub sources section."""

    def build(self, data: ProjectData) -> list[Any]:
        elements: list[Any] = []
        if not HAS_REPORTLAB:
            return elements
        elements.append(Paragraph("Sources & References", self._title_style()))
        elements.append(Spacer(1, 8))

        if not data.sources:
            elements.append(Paragraph("No external sources documented.", self._body_style()))
            return elements

        for source in data.sources:
            name = source.get("name", "Unnamed")
            url = source.get("url", "")
            usage = source.get("usage", "")
            elements.append(Paragraph(
                f'<b>{name}</b><br/><a href="{url}" color="blue">{url}</a><br/><i>{usage}</i>',
                self._body_style(),
            ))
            elements.append(Spacer(1, 4))

        return elements


class LessonsLearned(SectionBuilder):
    """Builds the retrospective section."""

    def build(self, data: ProjectData) -> list[Any]:
        elements: list[Any] = []
        if not HAS_REPORTLAB:
            return elements
        elements.append(Paragraph("Lessons Learned", self._title_style()))
        elements.append(Spacer(1, 8))

        if not data.lessons_learned:
            elements.append(Paragraph("No lessons recorded for this project.", self._body_style()))
            return elements

        for lesson in data.lessons_learned:
            elements.append(Paragraph(f"• {lesson}", self._body_style()))

        return elements


# ── PDF Generator ────────────────────────────────────────────────────────────

class PDFGenerator:
    """Generates professional PDF reports for Luymas AI projects.

    Usage::

        gen = PDFGenerator()
        pdf_path = gen.generate_project_report(project_data)
        gen.send_report("user@example.com", pdf_path)
    """

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self.output_dir = output_dir or REPORTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._section_builders = [
            ExecutiveSummary(),
            ArchitectureReport(),
            TestResultsReport(),
            SecurityReport(),
            DeploymentReport(),
            SourcesReport(),
            LessonsLearned(),
        ]

    def generate_project_report(self, data: ProjectData) -> Path:
        """Generate a full project report PDF and return its path."""
        if not HAS_REPORTLAB:
            logger.warning("reportlab not installed; generating text report instead.")
            return self._generate_text_report(data)

        filename = f"{data.project_name.replace(' ', '_')}_{data.project_id}.pdf"
        pdf_path = self.output_dir / filename

        doc = SimpleDocTemplate(
            str(pdf_path), pagesize=A4,
            leftMargin=0.75 * inch, rightMargin=0.75 * inch,
            topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        )

        styles = getSampleStyleSheet()
        elements: list[Any] = []

        # Title page
        title_style = ParagraphStyle(
            "ReportTitle", parent=styles["Title"],
            fontSize=28, textColor=HexColor("#1a1a2e"),
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle", parent=styles["Normal"],
            fontSize=14, textColor=HexColor("#666666"), alignment=TA_CENTER,
        )

        elements.append(Spacer(1, 2 * inch))
        elements.append(Paragraph(data.project_name, title_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Luymas AI — Project Report", subtitle_style))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            subtitle_style,
        ))
        elements.append(PageBreak())

        # Build each section
        for builder in self._section_builders:
            section_elements = builder.build(data)
            elements.extend(section_elements)
            elements.append(Spacer(1, 16))

        # Add screenshots
        if data.screenshots:
            elements.append(Paragraph("Screenshots", self._section_builders[0]._title_style()))
            for screenshot_path in data.screenshots:
                if os.path.exists(screenshot_path):
                    img = RLImage(screenshot_path, width=6 * inch, height=4 * inch)
                    elements.append(img)
                    elements.append(Spacer(1, 12))

        # Custom sections
        for section_title, section_content in data.custom_sections.items():
            elements.append(Paragraph(section_title, self._section_builders[0]._title_style()))
            elements.append(Paragraph(section_content, self._section_builders[0]._body_style()))

        doc.build(elements)
        logger.info("Generated PDF report: %s", pdf_path)
        return pdf_path

    def add_screenshots(self, data: ProjectData, screenshots: list[str]) -> None:
        """Add screenshot paths to project data."""
        data.screenshots.extend(screenshots)

    def add_sources(self, data: ProjectData, sources_md_content: str) -> None:
        """Parse SOURCES.md content and add to project data."""
        for line in sources_md_content.strip().split("\n"):
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                # Simple markdown list parsing
                parts = line[2:].split(" - ", 1)
                name = parts[0].strip()
                url_or_usage = parts[1].strip() if len(parts) > 1 else ""
                data.sources.append({"name": name, "url": url_or_usage, "usage": ""})

    def send_report(self, recipient: str, pdf_path: Path) -> bool:
        """Send the PDF report to a recipient (placeholder for email integration)."""
        if not pdf_path.exists():
            logger.error("PDF file not found: %s", pdf_path)
            return False
        # In production: integrate with email_factory or messaging
        logger.info("Report %s sent to %s", pdf_path.name, recipient)
        return True

    def _generate_text_report(self, data: ProjectData) -> Path:
        """Fallback text report when reportlab is unavailable."""
        filename = f"{data.project_name.replace(' ', '_')}_{data.project_id}.txt"
        path = self.output_dir / filename
        lines = [
            f"Luymas AI — Project Report: {data.project_name}",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "=" * 60,
            f"\nDescription: {data.description}",
            f"\nTech Stack: {', '.join(data.tech_stack)}",
            f"\nAgents: {', '.join(data.agents_involved)}",
            f"\nLessons: " + "\n".join(f"  - {l}" for l in data.lessons_learned),
        ]
        path.write_text("\n".join(lines), encoding="utf-8")
        return path
