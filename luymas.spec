# -*- mode: python ; coding: utf-8 -*-
"""
Luymas AI - PyInstaller Spec File

This spec file defines how Luymas AI is packaged into a Windows executable.
It specifies all data files, hidden imports, exclusions, and EXE metadata.

Usage:
    pyinstaller luymas.spec          # Build from spec
    pyinstaller luymas.spec --clean  # Clean build from spec
"""

import os
import sys
from pathlib import Path

# ── Project root detection ────────────────────────────────────────────────────

PROJECT_ROOT = Path(SPECPATH).resolve() if 'SPECPATH' in dir() else Path(__file__).parent.resolve()

# ── Helper: Collect data tree ─────────────────────────────────────────────────

def collect_tree(directory, prefix=None):
    """Recursively collect all files in a directory as (source, dest) tuples."""
    datas = []
    dir_path = Path(directory)
    if not dir_path.exists():
        return datas
    dest = prefix or dir_path.name
    for item in dir_path.rglob("*"):
        if item.is_file():
            rel = item.relative_to(dir_path)
            datas.append((str(item), str(Path(dest) / rel.parent)))
    return datas


# ── Collect all data files ────────────────────────────────────────────────────

datas = []

# Studio web interface (HTML, CSS, JS)
datas += collect_tree(PROJECT_ROOT / "studio", "studio")

# Configuration files (YAML)
datas += collect_tree(PROJECT_ROOT / "config", "config")

# Design modules and assets
datas += collect_tree(PROJECT_ROOT / "design", "design")

# Project templates (web, mobile, desktop)
datas += collect_tree(PROJECT_ROOT / "templates", "templates")

# Environment template
env_example = PROJECT_ROOT / ".env.example"
if env_example.exists():
    datas.append((str(env_example), "."))

# Requirements file
req_file = PROJECT_ROOT / "requirements.txt"
if req_file.exists():
    datas.append((str(req_file), "."))

# Install scripts
for script_name in ["install.bat", "install.sh", "launcher.bat"]:
    script_path = PROJECT_ROOT / script_name
    if script_path.exists():
        datas.append((str(script_path), "."))

# ── Hidden Imports ────────────────────────────────────────────────────────────

hiddenimports = [
    # Core AI / LLM
    "ollama",
    "openai",
    "huggingface_hub",

    # Configuration & Environment
    "yaml",
    "dotenv",

    # HTTP & Networking
    "requests",
    "aiohttp",
    "websockets",
    "urllib.request",

    # Browser Automation
    "playwright",

    # Audio & OCR
    "whisper",
    "pytesseract",

    # Image Processing
    "PIL",

    # Document Generation
    "reportlab",
    "reportlab.lib",
    "reportlab.lib.pagesizes",
    "reportlab.lib.styles",
    "reportlab.platypus",

    # Messaging
    "telegram",

    # Web Framework
    "flask",
    "flask.json",
    "flask.templating",
    "flask.signals",
    "werkzeug",
    "werkzeug.routing",
    "werkzeug.serving",
    "werkzeug.middleware",
    "jinja2",
    "jinja2.ext",
    "markupsafe",

    # Infrastructure
    "docker",
    "git",
    "git.repo",

    # Scheduling
    "schedule",

    # CLI & Display
    "rich",
    "click",

    # Data
    "numpy",
    "pydantic",

    # ── Agent Modules ──────────────────────────────────────────────────────
    "agents",
    "agents.pdg",
    "agents.pm",
    "agents.architect",
    "agents.coder_back",
    "agents.coder_front",
    "agents.designer",
    "agents.guardian",
    "agents.tester",
    "agents.ops",
    "agents.caretaker",
    "agents.talent_scout",

    # ── Core Modules ──────────────────────────────────────────────────────
    "core",
    "core.orchestrator",
    "core.messenger",
    "core.memory",
    "core.pdf_generator",
    "core.api_injector",
    "core.auto_updater",
    "core.github_scout",
    "core.self_improver",
    "core.experience_learner",
    "core.email_factory",
    "core.captcha_solver",
    "core.identity_manager",

    # ── Design Modules ────────────────────────────────────────────────────
    "design",
    "design.image_generator",
    "design.design_plugins",
    "design.design_updater",

    # ── Standard Library (sometimes missed) ───────────────────────────────
    "asyncio",
    "heapq",
    "dataclasses",
    "enum",
    "uuid",
    "secrets",
    "json",
    "logging",
    "threading",
    "subprocess",
    "signal",
    "webbrowser",
    "http",
    "http.server",
    "email",
    "email.mime",
    "email.mime.text",
    "email.mime.multipart",
    "smtpd",
    "smtplib",
    "imaplib",
]

# ── Excludes (reduce bundle size) ─────────────────────────────────────────────

excludes = [
    "tkinter",
    "_tkinter",
    "tcl",
    "matplotlib",
    "scipy",
    "pandas",
    "IPython",
    "notebook",
    "pytest",
    "setuptools",
    "pip",
    "wheel",
    "distutils",
    "lib2to3",
    "pydoc",
    "doctest",
    "unittest",
    "test",
    "tests",
    "PyQt5",
    "PyQt6",
    "PySide2",
    "PySide6",
    "wx",
    "curses",
    "pytz",
    "dateutil",
]

# ── Icon ──────────────────────────────────────────────────────────────────────

icon_path = PROJECT_ROOT / "design" / "assets" / "luymas.ico"
if not icon_path.exists():
    icon_path = None

# ── Analysis ──────────────────────────────────────────────────────────────────

a = Analysis(
    [str(PROJECT_ROOT / "launcher.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

# ── PYZ (Python ZIP archive) ─────────────────────────────────────────────────

pyz = PYZ(a.pure)

# ── EXE ───────────────────────────────────────────────────────────────────────

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="LuymasAI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,           # Console mode - needed to see logs and Ctrl+C
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path else None,
)

# ── COLLECT (single-folder distribution) ──────────────────────────────────────

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="LuymasAI",
)
