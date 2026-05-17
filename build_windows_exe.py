#!/usr/bin/env python3
"""
Luymas AI - Windows EXE Builder

This script creates a Windows .exe using PyInstaller.
On Linux, it uses Wine to cross-compile for Windows.
On Windows, it builds natively.

Usage:
    python build_windows_exe.py           # Build Windows .exe
    python build_windows_exe.py --native  # Build for current platform
    python build_windows_exe.py --wine    # Force Wine cross-compilation
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
RELEASES_DIR = PROJECT_ROOT / "releases"
BUILD_DIR = PROJECT_ROOT / "build_windows"
DIST_DIR = PROJECT_ROOT / "dist_windows"


def check_wine() -> bool:
    """Check if Wine is available for cross-compilation."""
    try:
        result = subprocess.run(
            ["wine", "--version"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f"  ✅ Wine found: {result.stdout.strip()}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    print("  ❌ Wine not found")
    return False


def install_wine_python() -> bool:
    """Install Python in Wine for cross-compilation."""
    print("\n📦 Setting up Wine + Python for cross-compilation...")
    
    # Download Python for Windows
    python_url = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
    python_installer = BUILD_DIR / "python_installer.exe"
    
    if not python_installer.exists():
        print(f"  Downloading Python 3.12 for Windows...")
        BUILD_DIR.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                ["curl", "-L", "-o", str(python_installer), python_url],
                check=True, timeout=300
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("  ❌ Failed to download Python installer")
            return False
    
    # Install Python in Wine
    print("  Installing Python in Wine...")
    try:
        subprocess.run(
            [
                "wine", str(python_installer),
                "/quiet", "InstallAllUsers=0",
                "PrependPath=1", "Include_pip=1",
            ],
            check=True, timeout=600,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  ❌ Failed to install Python in Wine")
        return False
    
    return True


def build_windows_exe() -> Path | None:
    """Build LuymasAI.exe for Windows."""
    print("\n" + "=" * 60)
    print("  LUYMAS AI - Building Windows Executable")
    print("=" * 60)
    
    system = platform.system()
    print(f"\n  Current OS: {system}")
    
    if system == "Windows":
        return build_native()
    else:
        print("\n  ⚠️ Not running on Windows.")
        print("  Options:")
        print("    1. Use Wine cross-compilation (if Wine is installed)")
        print("    2. Build natively on Windows")
        print("    3. Use GitHub Actions CI/CD")
        
        if check_wine():
            print("\n  🍷 Wine detected! Attempting cross-compilation...")
            return build_with_wine()
        else:
            print("\n  ❌ Cannot build Windows .exe on this system.")
            print("  To build LuymasAI.exe, you need to:")
            print("    1. Run this script on a Windows machine, OR")
            print("    2. Install Wine: apt install wine64, OR")
            print("    3. Use GitHub Actions (see .github/workflows/build.yml)")
            return None


def build_native() -> Path | None:
    """Build natively on Windows."""
    print("\n  🔨 Building native Windows executable...")
    
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    RELEASES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Install PyInstaller
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pyinstaller"],
        check=True,
    )
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=LuymasAI",
        "--onefile",
        "--console",
        "--noconfirm",
        f"--add-data=studio{os.pathsep}studio",
        f"--add-data=config{os.pathsep}config",
        f"--add-data=templates{os.pathsep}templates",
        f"--add-data=.env.example{os.pathsep}.",
        "--hidden-import=agents.base",
        "--hidden-import=agents.pdg",
        "--hidden-import=agents.pm",
        "--hidden-import=agents.architect",
        "--hidden-import=agents.coder_back",
        "--hidden-import=agents.coder_front",
        "--hidden-import=agents.designer",
        "--hidden-import=agents.guardian",
        "--hidden-import=agents.tester",
        "--hidden-import=agents.ops",
        "--hidden-import=agents.caretaker",
        "--hidden-import=agents.talent_scout",
        "--hidden-import=core.orchestrator",
        "--hidden-import=core.messenger",
        "--hidden-import=core.memory",
        "--hidden-import=core.pdf_generator",
        "--hidden-import=core.api_injector",
        "--hidden-import=core.auto_updater",
        "--hidden-import=core.github_scout",
        "--hidden-import=core.self_improver",
        "--hidden-import=core.experience_learner",
        "--hidden-import=core.email_factory",
        "--hidden-import=core.captcha_solver",
        "--hidden-import=core.identity_manager",
        "--hidden-import=design.image_generator",
        "--hidden-import=design.design_plugins",
        "--hidden-import=design.design_updater",
        "--hidden-import=ollama",
        "--hidden-import=yaml",
        "--hidden-import=flask",
        "--hidden-import=dotenv",
        "--hidden-import=aiohttp",
        "--hidden-import=reportlab",
        "--hidden-import=PIL",
        "--hidden-import=pydantic",
        "--collect-all=flask",
        "--collect-all=werkzeug",
        "--collect-all=jinja2",
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        f"--workpath={BUILD_DIR}",
        f"--distpath={DIST_DIR}",
        "launcher.py",
    ]
    
    print(f"\n  Running PyInstaller...")
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    
    if result.returncode != 0:
        print("  ❌ Build failed!")
        return None
    
    exe_path = DIST_DIR / "LuymasAI.exe"
    if exe_path.exists():
        # Copy to releases
        release_path = RELEASES_DIR / "LuymasAI.exe"
        shutil.copy2(exe_path, release_path)
        size_mb = release_path.stat().st_size / (1024 * 1024)
        print(f"\n  ✅ Build successful!")
        print(f"  📁 Output: {release_path}")
        print(f"  📦 Size: {size_mb:.1f} MB")
        return release_path
    else:
        print("  ❌ LuymasAI.exe not found in dist/")
        return None


def build_with_wine() -> Path | None:
    """Build using Wine cross-compilation."""
    print("\n  🍷 Building with Wine cross-compilation...")
    print("  ⚠️ This is experimental and may not work perfectly.")
    
    # This would require installing Python + PyInstaller in Wine
    # For now, return None and suggest alternatives
    print("  ❌ Wine cross-compilation is not fully automated yet.")
    print("  Please use one of these alternatives:")
    print("    1. Build on a Windows machine")
    print("    2. Use GitHub Actions CI/CD")
    print("    3. Use a Windows VM or Docker container")
    return None


def main() -> None:
    args = sys.argv[1:]
    
    if "--native" in args:
        build_native()
    elif "--wine" in args:
        if check_wine():
            build_with_wine()
        else:
            print("❌ Wine not available")
    else:
        build_windows_exe()


if __name__ == "__main__":
    main()
