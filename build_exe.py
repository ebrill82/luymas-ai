#!/usr/bin/env python3
"""
Luymas AI - Build Windows Executable

Uses PyInstaller to package the entire Luymas AI application into a
self-contained Windows executable distribution.

Usage:
    python build_exe.py            # Build the executable
    python build_exe.py --clean    # Clean build (removes previous artifacts)
    python build_exe.py --debug    # Debug build with console output

Requirements:
    pip install pyinstaller
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

# ── Project Paths ─────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.resolve()
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
SPEC_FILE = PROJECT_ROOT / "luymas.spec"


def clean_build() -> None:
    """Remove previous build artifacts."""
    print("Cleaning previous build artifacts...")
    for dir_path in [BUILD_DIR, DIST_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed: {dir_path}")
    if SPEC_FILE.exists():
        SPEC_FILE.unlink()
        print(f"  Removed: {SPEC_FILE}")
    print("Clean complete.\n")


def collect_data_files() -> list[str]:
    """Collect all data file paths for PyInstaller --add-data."""
    data_files = []

    # Studio web files
    studio_dir = PROJECT_ROOT / "studio"
    if studio_dir.exists():
        data_files.append(f"{studio_dir}{os.pathsep}studio")

    # Config files
    config_dir = PROJECT_ROOT / "config"
    if config_dir.exists():
        data_files.append(f"{config_dir}{os.pathsep}config")

    # Design files
    design_dir = PROJECT_ROOT / "design"
    if design_dir.exists():
        data_files.append(f"{design_dir}{os.pathsep}design")

    # Templates
    templates_dir = PROJECT_ROOT / "templates"
    if templates_dir.exists():
        data_files.append(f"{templates_dir}{os.pathsep}templates")

    # .env.example
    env_example = PROJECT_ROOT / ".env.example"
    if env_example.exists():
        data_files.append(f"{env_example}{os.pathsep}.")

    # requirements.txt
    req_file = PROJECT_ROOT / "requirements.txt"
    if req_file.exists():
        data_files.append(f"{req_file}{os.pathsep}.")

    return data_files


def get_hidden_imports() -> list[str]:
    """Return all hidden imports that PyInstaller might miss."""
    return [
        # Core dependencies
        "ollama",
        "yaml",
        "flask",
        "dotenv",
        "aiohttp",
        "requests",
        "websockets",
        "PIL",
        "pydantic",
        "numpy",
        "reportlab",
        "schedule",
        "rich",
        "click",
        "huggingface_hub",
        "openai",
        "git",
        "docker",

        # Flask internals
        "flask.json",
        "flask.templating",
        "flask.signals",
        "werkzeug",
        "werkzeug.routing",
        "werkzeug.serving",
        "jinja2",
        "jinja2.ext",
        "markupsafe",

        # Agent modules
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

        # Core modules
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

        # Design modules
        "design",
        "design.image_generator",
        "design.design_plugins",
        "design.design_updater",

        # Standard library modules sometimes missed
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
        "urllib.request",
    ]


def get_excludes() -> list[str]:
    """Return modules to exclude from the build (reduce size)."""
    return [
        "tkinter",
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
        "tcl",
        "tkinter",
        "_tkinter",
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
        "wx",
        "curses",
    ]


def build(debug: bool = False) -> None:
    """Run PyInstaller build."""
    import PyInstaller.__main__

    # Collect data files
    data_files = collect_data_files()
    hidden_imports = get_hidden_imports()
    excludes = get_excludes()

    # Icon file (if exists)
    icon_path = PROJECT_ROOT / "design" / "assets" / "luymas.ico"
    icon_args = []
    if icon_path.exists():
        icon_args = [f"--icon={icon_path}"]

    # Build the command
    cmd = [
        str(PROJECT_ROOT / "launcher.py"),
        f"--name=LuymasAI",
        "--onedir",
        "--noconfirm",

        # Console mode (needed to see logs)
        "--console" if debug else "--console",

        # Data files
        *[f"--add-data={d}" for d in data_files],

        # Hidden imports
        *[f"--hidden-import={m}" for m in hidden_imports],

        # Excludes
        *[f"--exclude-module={m}" for m in excludes],

        # Output directories
        f"--workpath={BUILD_DIR}",
        f"--distpath={DIST_DIR}",
        f"--specpath={PROJECT_ROOT}",

        # Runtime hooks
        "--collect-all=flask",
        "--collect-all=werkzeug",
        "--collect-all=jinja2",

        # Icon
        *icon_args,
    ]

    print("=" * 60)
    print("  LUYMAS AI - Building Windows Executable")
    print("=" * 60)
    print()
    print(f"  Project root: {PROJECT_ROOT}")
    print(f"  Output dir:   {DIST_DIR}")
    print(f"  Build dir:    {BUILD_DIR}")
    print(f"  Data files:   {len(data_files)}")
    print(f"  Hidden imports: {len(hidden_imports)}")
    print(f"  Excludes:     {len(excludes)}")
    print(f"  Debug mode:   {debug}")
    print()

    if icon_args:
        print(f"  Icon: {icon_path}")
    else:
        print("  Icon: (none found, skipping)")
    print()

    print("Running PyInstaller...")
    print("-" * 60)

    PyInstaller.__main__.run(cmd)

    print("-" * 60)
    print()
    print("=" * 60)
    print("  BUILD COMPLETE!")
    print("=" * 60)
    print()
    print(f"  Executable: {DIST_DIR / 'LuymasAI' / 'LuymasAI.exe'}")
    print()
    print("  To distribute, zip the entire 'dist/LuymasAI' folder.")
    print("  Users will need Ollama installed separately.")
    print()


def main() -> None:
    """Main entry point."""
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    if "--clean" in args:
        clean_build()

    debug = "--debug" in args

    build(debug=debug)


if __name__ == "__main__":
    main()
