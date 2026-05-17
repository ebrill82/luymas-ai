# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('studio', 'studio'), ('config', 'config'), ('templates', 'templates'), ('.env.example', '.')]
binaries = []
hiddenimports = ['agents', 'agents.base', 'agents.pdg', 'agents.pm', 'agents.architect', 'agents.coder_back', 'agents.coder_front', 'agents.designer', 'agents.guardian', 'agents.tester', 'agents.ops', 'agents.caretaker', 'agents.talent_scout', 'core', 'core.orchestrator', 'core.messenger', 'core.memory', 'core.pdf_generator', 'core.api_injector', 'core.auto_updater', 'core.github_scout', 'core.self_improver', 'core.experience_learner', 'core.email_factory', 'core.captcha_solver', 'core.identity_manager', 'design', 'design.image_generator', 'design.design_plugins', 'design.design_updater', 'ollama', 'yaml', 'flask', 'dotenv', 'aiohttp', 'reportlab', 'PIL', 'pydantic']
tmp_ret = collect_all('flask')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('werkzeug')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('jinja2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'pandas', 'pytest', 'IPython'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LuymasAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
