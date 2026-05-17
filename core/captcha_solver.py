"""
core/captcha_solver.py - Anti-Captcha System for Luymas AI

Resolves captchas encountered during web navigation using multiple strategies:
OCR for text captchas, CLIP-based image captchas, Whisper for audio captchas,
Playwright stealth for Cloudflare, and human escalation for complex cases.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


# ── Data Models ──────────────────────────────────────────────────────────────

class CaptchaType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    RECAPTCHA_V2 = "recaptcha_v2"
    RECAPTCHA_V3 = "recaptcha_v3"
    HCAPTCHA = "hcaptcha"
    CLOUDFLARE = "cloudflare_turnstile"
    UNKNOWN = "unknown"


class SolveStatus(str, Enum):
    PENDING = "pending"
    SOLVING = "solving"
    SOLVED = "solved"
    FAILED = "failed"
    HUMAN_REQUIRED = "human_required"


@dataclass
class CaptchaInfo:
    """Detected captcha information."""
    captcha_type: CaptchaType = CaptchaType.UNKNOWN
    page_url: str = ""
    element_selector: str = ""
    image_url: str = ""
    audio_url: str = ""
    site_key: str = ""
    iframe_src: str = ""
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SolveResult:
    """Result of a captcha solving attempt."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    captcha_type: CaptchaType = CaptchaType.UNKNOWN
    status: SolveStatus = SolveStatus.PENDING
    solution: str = ""
    confidence: float = 0.0
    solve_time_ms: float = 0.0
    attempts: int = 1
    method_used: str = ""
    error: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class HelpRequest:
    """A request for human assistance with a captcha."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    captcha_type: CaptchaType = CaptchaType.UNKNOWN
    page_url: str = ""
    screenshot_path: str = ""
    description: str = ""
    status: str = "pending"  # pending, resolved, expired
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    resolution: str = ""


# ── Captcha Detector ─────────────────────────────────────────────────────────

class CaptchaDetector:
    """Detects captchas on web pages using DOM and content analysis."""

    CAPTCHA_SELECTORS = {
        CaptchaType.RECAPTCHA_V2: [
            'iframe[src*="recaptcha"]',
            'div.g-recaptcha',
            '[data-sitekey]',
        ],
        CaptchaType.RECAPTCHA_V3: [
            'script[src*="recaptcha/enterprise"]',
            'grecaptcha.enterprise',
        ],
        CaptchaType.HCAPTCHA: [
            'iframe[src*="hcaptcha"]',
            'div.h-captcha',
        ],
        CaptchaType.CLOUDFLARE: [
            'iframe[src*="challenges.cloudflare.com"]',
            '#challenge-running',
            'div.cf-turnstile',
        ],
        CaptchaType.TEXT: [
            'img[src*="captcha"]',
            'img[alt*="captcha" i]',
            'canvas.captcha',
        ],
    }

    def detect_captcha(self, page_url: str, page_content: str = "",
                       element_selector: str = "") -> Optional[CaptchaInfo]:
        """Detect captcha type and details from page content."""
        if element_selector:
            # Specific element provided — try to classify
            for ctype, selectors in self.CAPTCHA_SELECTORS.items():
                if element_selector in selectors:
                    return CaptchaInfo(
                        captcha_type=ctype,
                        page_url=page_url,
                        element_selector=element_selector,
                        confidence=0.9,
                    )

        # Scan page content for captcha indicators
        content_lower = (page_content or "").lower()

        if "recaptcha" in content_lower or "g-recaptcha" in content_lower:
            site_key = self._extract_site_key(page_content, "recaptcha")
            return CaptchaInfo(
                captcha_type=CaptchaType.RECAPTCHA_V2,
                page_url=page_url,
                site_key=site_key,
                confidence=0.85,
            )

        if "hcaptcha" in content_lower:
            site_key = self._extract_site_key(page_content, "hcaptcha")
            return CaptchaInfo(
                captcha_type=CaptchaType.HCAPTCHA,
                page_url=page_url,
                site_key=site_key,
                confidence=0.85,
            )

        if "challenges.cloudflare.com" in content_lower or "cf-turnstile" in content_lower:
            return CaptchaInfo(
                captcha_type=CaptchaType.CLOUDFLARE,
                page_url=page_url,
                confidence=0.9,
            )

        # Check for simple image captchas
        if "captcha" in content_lower and ("img" in content_lower or "canvas" in content_lower):
            return CaptchaInfo(
                captcha_type=CaptchaType.TEXT,
                page_url=page_url,
                confidence=0.6,
            )

        return None

    @staticmethod
    def _extract_site_key(content: str, captcha_type: str) -> str:
        """Extract site key from page content."""
        import re
        if captcha_type == "recaptcha":
            match = re.search(r'data-sitekey=["\']([^"\']+)', content)
            if match:
                return match.group(1)
        elif captcha_type == "hcaptcha":
            match = re.search(r'data-sitekey=["\']([^"\']+)', content)
            if match:
                return match.group(1)
        return ""


# ── Text Captcha Solver ─────────────────────────────────────────────────────

class TextCaptchaSolver:
    """OCR-based text captcha solver using Tesseract patterns."""

    def __init__(self, tesseract_cmd: Optional[str] = None) -> None:
        self._tesseract_cmd = tesseract_cmd

    async def solve(self, image_path: str) -> SolveResult:
        """Solve a text captcha from an image file."""
        start = datetime.now(timezone.utc)

        # In production: use pytesseract or EasyOCR
        # import pytesseract
        # from PIL import Image
        # img = Image.open(image_path)
        # text = pytesseract.image_to_string(img, config='--psm 7 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz')

        # Preprocessing steps for better OCR:
        # 1. Convert to grayscale
        # 2. Apply thresholding
        # 3. Remove noise lines
        # 4. Increase contrast

        elapsed = (datetime.now(timezone.utc) - start).total_seconds() * 1000

        result = SolveResult(
            captcha_type=CaptchaType.TEXT,
            status=SolveStatus.FAILED,
            method_used="tesseract_ocr",
            solve_time_ms=elapsed,
            error="Tesseract not available in sandbox — requires pytesseract + PIL",
        )
        logger.info("Text captcha solve attempt: %s", result.status.value)
        return result


# ── Image Captcha Solver ─────────────────────────────────────────────────────

class ImageCaptchaSolver:
    """Vision-based image captcha solver using CLIP-like models."""

    LABEL_MAP = {
        "traffic_light": ["traffic light", "traffic signal", "stoplight"],
        "crosswalk": ["crosswalk", "pedestrian crossing", "zebra crossing"],
        "bus": ["bus", "transit bus", "coach"],
        "bicycle": ["bicycle", "bike", "cycle"],
        "fire_hydrant": ["fire hydrant", "fire plug"],
        "stairs": ["stairs", "staircase", "steps"],
        "bridge": ["bridge", "overpass"],
        "mountain": ["mountain", "hill", "peak"],
        "car": ["car", "automobile", "vehicle"],
    }

    async def solve(self, image_path: str, prompt: str = "") -> SolveResult:
        """Solve an image selection captcha (e.g., 'select all traffic lights')."""
        start = datetime.now(timezone.utc)

        # In production: use CLIP or a vision model
        # from transformers import CLIPModel, CLIPProcessor
        # model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        # processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        # Strategy:
        # 1. Split the captcha grid into individual tiles
        # 2. For each tile, compute similarity with the prompt
        # 3. Select tiles above a threshold

        elapsed = (datetime.now(timezone.utc) - start).total_seconds() * 1000

        result = SolveResult(
            captcha_type=CaptchaType.IMAGE,
            status=SolveStatus.FAILED,
            method_used="clip_vision",
            solve_time_ms=elapsed,
            error="CLIP model not available — requires transformers + torch",
        )
        logger.info("Image captcha solve attempt: %s", result.status.value)
        return result


# ── Audio Captcha Solver ─────────────────────────────────────────────────────

class AudioCaptchaSolver:
    """Speech-based audio captcha solver using Whisper."""

    async def solve(self, audio_path: str) -> SolveResult:
        """Solve an audio captcha by transcribing speech."""
        start = datetime.now(timezone.utc)

        # In production: use OpenAI Whisper
        # import whisper
        # model = whisper.load_model("base")
        # result = model.transcribe(audio_path)
        # text = result["text"].strip()

        elapsed = (datetime.now(timezone.utc) - start).total_seconds() * 1000

        result = SolveResult(
            captcha_type=CaptchaType.AUDIO,
            status=SolveStatus.FAILED,
            method_used="whisper_asr",
            solve_time_ms=elapsed,
            error="Whisper not available — requires openai-whisper package",
        )
        logger.info("Audio captcha solve attempt: %s", result.status.value)
        return result


# ── Cloudflare Bypasser ──────────────────────────────────────────────────────

class CloudflareBypasser:
    """Bypasses Cloudflare challenges using Playwright stealth techniques."""

    STEALTH_SETTINGS = {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "viewport": {"width": 1920, "height": 1080},
        "locale": "en-US",
        "timezone_id": "America/New_York",
        "webgl_vendor": "Google Inc. (NVIDIA)",
        "navigator_plugins": True,
        "navigator_languages": ["en-US", "en"],
    }

    async def bypass(self, page_url: str, timeout: int = 30000) -> Any:
        """Attempt to bypass Cloudflare challenge using stealth browser.

        Returns the page object after challenge resolution.
        """
        # In production:
        # from playwright.async_api import async_playwright
        # from playwright_stealth import stealth_async
        #
        # async with async_playwright() as p:
        #     browser = await p.chromium.launch(headless=True)
        #     context = await browser.new_context(**self.STEALTH_SETTINGS)
        #     page = await context.new_page()
        #     await stealth_async(page)
        #     await page.goto(page_url, wait_until="networkidle", timeout=timeout)
        #     # Wait for challenge to resolve
        #     await page.wait_for_url("**", timeout=timeout)
        #     return page

        logger.info("Cloudflare bypass attempt for %s", page_url)
        return None


# ── Human Helper ─────────────────────────────────────────────────────────────

class HumanHelper:
    """Requests human help for complex captchas that auto-solvers cannot handle."""

    def __init__(self) -> None:
        self._pending_requests: dict[str, HelpRequest] = {}
        self._callback: Optional[Callable] = None

    def set_callback(self, callback: Callable) -> None:
        """Set callback for notifying the user about help requests."""
        self._callback = callback

    async def request_human_help(self, captcha_type: CaptchaType,
                                 page_url: str, screenshot_path: str = "",
                                 description: str = "") -> HelpRequest:
        """Request human assistance for a captcha."""
        request = HelpRequest(
            captcha_type=captcha_type,
            page_url=page_url,
            screenshot_path=screenshot_path,
            description=description or f"Unable to solve {captcha_type.value} captcha automatically",
        )
        self._pending_requests[request.id] = request

        # Notify user
        if self._callback:
            try:
                await self._callback(request)
            except Exception as exc:
                logger.error("Human help callback failed: %s", exc)

        logger.info("Human help requested for %s captcha on %s (id=%s)",
                     captcha_type.value, page_url, request.id)
        return request

    def resolve_request(self, request_id: str, solution: str) -> bool:
        """Resolve a human help request with the provided solution."""
        request = self._pending_requests.get(request_id)
        if not request:
            return False
        request.status = "resolved"
        request.resolution = solution
        request.resolved_at = datetime.now(timezone.utc)
        logger.info("Human help request %s resolved", request_id)
        return True

    def get_pending_requests(self) -> list[HelpRequest]:
        return [r for r in self._pending_requests.values() if r.status == "pending"]


# ── Captcha Solver Facade ────────────────────────────────────────────────────

class CaptchaSolver:
    """Unified facade for the anti-captcha system.

    Usage::

        solver = CaptchaSolver()
        info = solver.detect_captcha(page_url, page_html)
        result = await solver.solve_text_captcha("captcha.png")
        result = await solver.bypass_cloudflare("https://example.com")
        help_req = await solver.request_human_help(CaptchaType.HCAPTCHA, page_url)
    """

    def __init__(self) -> None:
        self.detector = CaptchaDetector()
        self.text_solver = TextCaptchaSolver()
        self.image_solver = ImageCaptchaSolver()
        self.audio_solver = AudioCaptchaSolver()
        self.cloudflare_bypasser = CloudflareBypasser()
        self.human_helper = HumanHelper()

    def detect_captcha(self, page_url: str, page_content: str = "",
                       element_selector: str = "") -> Optional[CaptchaInfo]:
        """Detect if a page has a captcha and identify its type."""
        return self.detector.detect_captcha(page_url, page_content, element_selector)

    async def solve_text_captcha(self, image_path: str) -> SolveResult:
        """Solve a text/OCR captcha."""
        return await self.text_solver.solve(image_path)

    async def solve_image_captcha(self, image_path: str, prompt: str = "") -> SolveResult:
        """Solve an image selection captcha."""
        return await self.image_solver.solve(image_path, prompt)

    async def solve_audio_captcha(self, audio_path: str) -> SolveResult:
        """Solve an audio captcha."""
        return await self.audio_solver.solve(audio_path)

    async def bypass_cloudflare(self, page_url: str, timeout: int = 30000) -> Any:
        """Bypass a Cloudflare challenge page."""
        return await self.cloudflare_bypasser.bypass(page_url, timeout)

    async def request_human_help(self, captcha_type: CaptchaType,
                                 page_url: str, screenshot_path: str = "",
                                 description: str = "") -> HelpRequest:
        """Escalate a captcha to human resolution."""
        return await self.human_helper.request_human_help(
            captcha_type, page_url, screenshot_path, description)

    async def auto_solve(self, captcha_info: CaptchaInfo) -> SolveResult:
        """Automatically select and run the appropriate solver."""
        ctype = captcha_info.captcha_type

        if ctype == CaptchaType.TEXT:
            if captcha_info.image_url:
                return await self.text_solver.solve(captcha_info.image_url)
        elif ctype == CaptchaType.IMAGE:
            return await self.image_solver.solve(captcha_info.image_url)
        elif ctype == CaptchaType.AUDIO:
            if captcha_info.audio_url:
                return await self.audio_solver.solve(captcha_info.audio_url)
        elif ctype == CaptchaType.CLOUDFLARE:
            page = await self.cloudflare_bypasser.bypass(captcha_info.page_url)
            if page:
                return SolveResult(
                    captcha_type=ctype, status=SolveStatus.SOLVED,
                    method_used="cloudflare_stealth",
                )

        # Fallback to human help
        help_req = await self.human_helper.request_human_help(
            ctype, captcha_info.page_url,
            description=f"Auto-solver could not handle {ctype.value}",
        )
        return SolveResult(
            captcha_type=ctype, status=SolveStatus.HUMAN_REQUIRED,
            method_used="human_escalation",
            solution=f"Help request {help_req.id} created",
        )
