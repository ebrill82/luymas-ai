#!/usr/bin/env python3
"""
Luymas AI — Constructeur de Clé USB Portable

Prépare une clé USB bootable avec tout le nécessaire pour
exécuter Luymas AI en mode portable :
  - Projet complet (code source)
  - Python portable (téléchargement optionnel)
  - Ollama portable (téléchargement optionnel)
  - Modèles IA adaptés au matériel
  - Scripts de démarrage automatique

Utilisation :
  python core/usb_builder.py D:
  python core/usb_builder.py E: --skip-models
  python core/usb_builder.py /media/usb

Auteur : Luymas AI Team
"""

from __future__ import annotations

import argparse
import logging
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Optional

# Chemin du projet
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

logger = logging.getLogger("luymas.usb_builder")

# ═══════════════════════════════════════════════════════════════════════════════
# STRUCTURE DE LA CLÉ USB
# ═══════════════════════════════════════════════════════════════════════════════

USB_STRUCTURE = [
    "luymas-ai",
    "luymas-ai/agents",
    "luymas-ai/core",
    "luymas-ai/config",
    "luymas-ai/design",
    "luymas-ai/studio",
    "luymas-ai/templates",
    "luymas-ai/templates/web",
    "luymas-ai/templates/mobile",
    "luymas-ai/templates/desktop",
    "luymas-ai/docker",
    "luymas-ai/data",
    "luymas-ai/logs",
    "luymas-ai/models",
    "python_portable",
    "ollama_portable",
]

# Fichiers du projet à copier
PROJECT_FILES = [
    "launcher.py",
    "main.py",
    "requirements.txt",
    "README.md",
    "README_USB.txt",
    "start.bat",
    "autorun.inf",
    "install.bat",
    "install.sh",
    ".env.example",
]

# Dossiers du projet à copier récursivement
PROJECT_DIRS = [
    "agents",
    "core",
    "config",
    "design",
    "studio",
    "templates",
    "docker",
]

# URLs de téléchargement
PYTHON_PORTABLE_URL = "https://github.com/winpython/winpython/releases/download/11.5.20250209/Winpython-3.12.9.0dot.exe"
OLLAMA_WINDOWS_URL = "https://ollama.com/download/OllamaSetup.exe"
OLLAMA_LINUX_URL = "https://ollama.com/install.sh"


# ═══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════════

def get_disk_free_gb(path: Path) -> float:
    """Retourne l'espace disque disponible en Go pour un chemin donné."""
    try:
        import psutil  # ✅ Réel
        usage = psutil.disk_usage(str(path))
        return round(usage.free / (1024 ** 3), 1)
    except ImportError:
        pass

    # Fallback via os.statvfs (Unix)
    try:
        stat = os.statvfs(str(path))
        return round((stat.f_bavail * stat.f_frsize) / (1024 ** 3), 1)
    except (AttributeError, OSError):
        pass

    # Fallback via subprocess
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["fsutil", "volume", "diskfree", str(path)],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.split("\n"):
                if "free" in line.lower():
                    bytes_free = int(line.split(":")[-1].strip())
                    return round(bytes_free / (1024 ** 3), 1)
        else:
            result = subprocess.run(
                ["df", "-h", str(path)],
                capture_output=True, text=True, timeout=10
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 4:
                    free_str = parts[3]
                    if free_str.endswith("G"):
                        return round(float(free_str[:-1]), 1)
                    elif free_str.endswith("T"):
                        return round(float(free_str[:-1]) * 1024, 1)
    except Exception:
        pass

    return -1  # Impossible à déterminer


def download_file(url: str, dest: Path, description: str = "") -> bool:
    """Télécharge un fichier avec barre de progression basique."""
    if dest.exists():
        logger.info("✅ %s déjà présent : %s", description, dest.name)
        return True

    logger.info("📥 Téléchargement de %s...", description or url)
    try:
        # Utiliser urllib pour éviter les dépendances supplémentaires
        urllib.request.urlretrieve(url, str(dest))
        logger.info("✅ %s téléchargé avec succès", description)
        return True
    except Exception as e:
        logger.error("❌ Échec du téléchargement de %s : %s", description, e)
        # Supprimer le fichier partiel
        if dest.exists():
            dest.unlink()
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRUCTION DE LA CLÉ USB
# ═══════════════════════════════════════════════════════════════════════════════

class USBBuiler:
    """Constructeur de clé USB portable pour Luymas AI."""

    def __init__(self, drive_path: str, skip_models: bool = False,
                 skip_python: bool = False, skip_ollama: bool = False):
        self.drive = Path(drive_path)
        self.skip_models = skip_models
        self.skip_python = skip_python
        self.skip_ollama = skip_ollama
        self.total_copied = 0
        self.total_size_mb = 0.0

    def build(self) -> bool:
        """Exécute la construction complète de la clé USB."""
        # Vérifier que le lecteur existe
        if not self.drive.exists():
            logger.error("❌ Le lecteur %s n'existe pas", self.drive)
            logger.info("Insérez la clé USB et relancez le script.")
            return False

        # Vérifier l'espace disque
        free_gb = get_disk_free_gb(self.drive)
        if free_gb < 0:
            logger.warning("⚠️ Impossible de déterminer l'espace disponible")
        elif free_gb < 10:
            logger.error("❌ Espace insuffisant : %.1f Go libre (minimum 10 Go requis)", free_gb)
            return False
        elif free_gb < 30:
            logger.warning("⚠️ Espace limité : %.1f Go libre. Les modèles ne pourront pas tous être copiés.", free_gb)
        else:
            logger.info("💾 Espace disponible : %.1f Go", free_gb)

        print()
        print("╔══════════════════════════════════════════════╗")
        print("║    💾 LUYMAS AI - CRÉATION CLÉ USB PORTABLE  ║")
        print("╠══════════════════════════════════════════════╣")
        print(f"║  Lecteur cible : {str(self.drive):<30} ║")
        print(f"║  Espace libre  : {free_gb:.1f} Go{' ' * (24 - len(f'{free_gb:.1f}'))}║")
        print("╚══════════════════════════════════════════════╝")
        print()

        # Étape 1 : Créer la structure de dossiers
        logger.info("📁 Étape 1/5 : Création de la structure de dossiers...")
        self._create_structure()

        # Étape 2 : Copier les fichiers du projet
        logger.info("📋 Étape 2/5 : Copie des fichiers du projet...")
        self._copy_project_files()

        # Étape 3 : Python portable (optionnel)
        if not self.skip_python:
            logger.info("🐍 Étape 3/5 : Téléchargement de Python portable...")
            self._download_python_portable()
        else:
            logger.info("🐍 Étape 3/5 : Python portable ignoré (--skip-python)")

        # Étape 4 : Ollama portable (optionnel)
        if not self.skip_ollama:
            logger.info("🦙 Étape 4/5 : Téléchargement d'Ollama portable...")
            self._download_ollama_portable()
        else:
            logger.info("🦙 Étape 4/5 : Ollama portable ignoré (--skip-ollama)")

        # Étape 5 : Modèles (optionnel)
        if not self.skip_models:
            logger.info("🧠 Étape 5/5 : Téléchargement des modèles adaptés...")
            self._download_models()
        else:
            logger.info("🧠 Étape 5/5 : Modèles ignorés (--skip-models)")

        # Résumé
        print()
        print("╔══════════════════════════════════════════════╗")
        print("║          ✅ CLÉ USB PRÊTE !                  ║")
        print("╠══════════════════════════════════════════════╣")
        print(f"║  Fichiers copiés  : {self.total_copied:<24} ║")
        print(f"║  Taille totale    : {self.total_size_mb:.1f} Mo{' ' * (20 - len(f'{self.total_size_mb:.1f}'))}║")
        print("╠══════════════════════════════════════════════╣")
        print("║  Pour lancer Luymas AI :                     ║")
        print("║  1. Branchez la clé USB                      ║")
        print("║  2. Double-cliquez sur start.bat             ║")
        print("║  3. Le Studio s'ouvre dans le navigateur     ║")
        print("╚══════════════════════════════════════════════╝")
        print()

        return True

    def _create_structure(self):
        """Crée tous les dossiers nécessaires sur la clé USB."""
        for rel_path in USB_STRUCTURE:
            dir_path = self.drive / rel_path
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug("  📁 %s", rel_path)

        # Dossiers supplémentaires
        for extra in ["luymas-ai/releases", "luymas-ai/tests",
                       "luymas-ai/.github/workflows"]:
            (self.drive / extra).mkdir(parents=True, exist_ok=True)

        logger.info("  ✅ Structure de dossiers créée")

    def _copy_project_files(self):
        """Copie les fichiers et dossiers du projet vers la clé USB."""
        dest_root = self.drive / "luymas-ai"

        # Fichiers individuels
        for filename in PROJECT_FILES:
            src = PROJECT_ROOT / filename
            if src.exists():
                dst = dest_root / filename
                shutil.copy2(str(src), str(dst))
                self.total_copied += 1
                size_mb = src.stat().st_size / (1024 * 1024)
                self.total_size_mb += size_mb
                logger.debug("  📄 %s (%.1f Ko)", filename, size_mb * 1024)

        # Dossiers récursifs
        for dirname in PROJECT_DIRS:
            src_dir = PROJECT_ROOT / dirname
            dst_dir = dest_root / dirname
            if src_dir.exists():
                count = 0
                for src_file in src_dir.rglob("*"):
                    if src_file.is_file():
                        rel = src_file.relative_to(src_dir)
                        dst_file = dst_dir / rel
                        dst_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(str(src_file), str(dst_file))
                        count += 1
                        self.total_copied += 1
                        self.total_size_mb += src_file.stat().st_size / (1024 * 1024)
                logger.debug("  📂 %s/ (%d fichiers)", dirname, count)

        logger.info("  ✅ %d fichiers copiés (%.1f Mo)", self.total_copied, self.total_size_mb)

    def _download_python_portable(self):
        """Télécharge Python portable pour Windows."""
        if platform.system() != "Windows":
            logger.info("  ⏭️ Python portable disponible uniquement pour Windows")
            return

        dest = self.drive / "python_portable" / "WinPython.exe"
        download_file(PYTHON_PORTABLE_URL, dest, "Python Portable (WinPython)")

    def _download_ollama_portable(self):
        """Télécharge l'installateur Ollama."""
        if platform.system() == "Windows":
            dest = self.drive / "ollama_portable" / "OllamaSetup.exe"
            download_file(OLLAMA_WINDOWS_URL, dest, "Ollama (Windows)")
        else:
            dest = self.drive / "ollama_portable" / "install.sh"
            download_file(OLLAMA_LINUX_URL, dest, "Ollama (Linux)")

    def _download_models(self):
        """Télécharge les modèles IA adaptés au matériel."""
        try:
            from core.hardware_detector import detect_hardware, classify_tier, get_recommended_models
        except ImportError:
            sys.path.insert(0, str(PROJECT_ROOT))
            from core.hardware_detector import detect_hardware, classify_tier, get_recommended_models

        info = detect_hardware()
        tier = classify_tier(info)
        models = get_recommended_models(tier)

        logger.info("  📊 Tier détecté : %s", tier)
        logger.info("  🧠 Modèles recommandés : %s", list(models.values()))

        # Vérifier si ollama est disponible
        ollama_path = shutil.which("ollama")
        if not ollama_path:
            logger.warning("  ⚠️ Ollama non installé — les modèles ne peuvent pas être téléchargés")
            logger.info("  Installez Ollama puis exécutez : ollama pull <modèle>")
            return

        for category, model_name in models.items():
            if model_name == "all-parallel":
                continue
            logger.info("  📥 Téléchargement du modèle %s (%s)...", model_name, category)
            try:
                result = subprocess.run(
                    ["ollama", "pull", model_name],
                    capture_output=True, text=True, timeout=600
                )
                if result.returncode == 0:
                    logger.info("  ✅ %s téléchargé", model_name)
                else:
                    logger.warning("  ⚠️ Échec du téléchargement de %s : %s", model_name, result.stderr[:100])
            except subprocess.TimeoutExpired:
                logger.warning("  ⚠️ Timeout lors du téléchargement de %s", model_name)
            except Exception as e:
                logger.warning("  ⚠️ Erreur lors du téléchargement de %s : %s", model_name, e)


# ═══════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Luymas AI — Créateur de clé USB portable",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python core/usb_builder.py D:
  python core/usb_builder.py E: --skip-models
  python core/usb_builder.py /media/usb --skip-python
        """
    )
    parser.add_argument(
        "drive",
        help="Lettre du lecteur USB (ex: D:) ou chemin du point de montage (ex: /media/usb)"
    )
    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="Ne pas télécharger les modèles IA"
    )
    parser.add_argument(
        "--skip-python",
        action="store_true",
        help="Ne pas télécharger Python portable"
    )
    parser.add_argument(
        "--skip-ollama",
        action="store_true",
        help="Ne pas télécharger Ollama"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Afficher les messages de debug"
    )

    args = parser.parse_args()

    # Configuration du logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    builder = USBBuiler(
        drive_path=args.drive,
        skip_models=args.skip_models,
        skip_python=args.skip_python,
        skip_ollama=args.skip_ollama,
    )
    success = builder.build()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
