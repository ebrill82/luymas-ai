#!/usr/bin/env python3
"""
Luymas AI — Détecteur de Matériel Automatique

Détecte le matériel disponible (CPU, RAM, GPU, VRAM, disque),
classe le système dans un tier de performance, et recommande
les modèles IA adaptés.

Modules utilisés :
  - psutil pour CPU, RAM, disque
  - nvidia-smi / torch.cuda / GPUtil pour GPU
  - subprocess pour les commandes système

Auteur : Luymas AI Team
"""

from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
from typing import Any, Dict, Optional

logger = logging.getLogger("luymas.hardware_detector")

# ═══════════════════════════════════════════════════════════════════════════════
# GRILLE DE TIERS
# ═══════════════════════════════════════════════════════════════════════════════

TIERS: Dict[str, Dict[str, Any]] = {
    "ultra-light": {
        "ram_max": 12,
        "gpu_required": False,
        "description": "PC bureautique, 8-12 Go RAM",
        "max_models": 1,
        "emoji": "🟢",
    },
    "light": {
        "ram_max": 24,
        "gpu_required": False,
        "description": "PC portable performant, 16-24 Go RAM",
        "max_models": 1,
        "emoji": "🟡",
    },
    "standard": {
        "ram_max": 48,
        "gpu_required": "optional",
        "description": "Station de travail, 32-48 Go RAM ou GPU 8 Go",
        "max_models": 2,
        "emoji": "🟠",
    },
    "pro": {
        "ram_max": 96,
        "gpu_required": True,
        "description": "Station pro, 64-96 Go RAM, GPU 24 Go+",
        "max_models": 3,
        "emoji": "🔴",
    },
    "ultra": {
        "ram_max": 192,
        "gpu_required": True,
        "description": "Serveur local, 128-192 Go RAM, GPU 48 Go+",
        "max_models": 4,
        "emoji": "🟣",
    },
    "enterprise": {
        "ram_max": float("inf"),
        "gpu_required": True,
        "description": "Data center, 256 Go+ RAM, multi-GPU 80 Go+",
        "max_models": -1,  # illimité
        "emoji": "💎",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# GRILLE DE MODÈLES PAR TIER
# ═══════════════════════════════════════════════════════════════════════════════

MODEL_GRID: Dict[str, Dict[str, str]] = {
    "ultra-light": {
        "reasoning": "gemma3:4b",
        "code": "qwen2.5-coder:3b",
        "image": "z-image-turbo",
        "fast": "llama3.2:3b",
    },
    "light": {
        "reasoning": "deepseek-r1:8b",
        "code": "qwen2.5-coder:7b",
        "image": "stable-diffusion-3-medium",
        "fast": "gemma3:4b",
    },
    "standard": {
        "reasoning": "qwen3.6:30b",
        "code": "deepseek-v4:16b",
        "image": "flux.1-pro",
        "fast": "llama3.3:8b",
    },
    "pro": {
        "reasoning": "qwen3.6:72b",
        "code": "deepseek-v4:70b",
        "image": "flux.1-pro-max",
        "fast": "qwen3.6:30b",
    },
    "ultra": {
        "reasoning": "kimi-k2.6",
        "code": "deepseek-v4-pro",
        "image": "flux.1-ultra",
        "fast": "qwen3.6:72b",
    },
    "enterprise": {
        "reasoning": "glm-5.1",
        "code": "deepseek-v4-pro-x4",
        "image": "flux.1-ultra-x2",
        "fast": "all-parallel",
    },
}

# Taille estimée des modèles en Go (pour vérification d'espace)
MODEL_SIZES_GB: Dict[str, float] = {
    "gemma3:4b": 2.6,
    "qwen2.5-coder:3b": 2.0,
    "z-image-turbo": 3.8,
    "llama3.2:3b": 2.0,
    "deepseek-r1:8b": 4.7,
    "qwen2.5-coder:7b": 4.5,
    "stable-diffusion-3-medium": 5.0,
    "qwen3.6:30b": 18.0,
    "deepseek-v4:16b": 9.5,
    "flux.1-pro": 12.0,
    "llama3.3:8b": 4.9,
    "qwen3.6:72b": 42.0,
    "deepseek-v4:70b": 40.0,
    "flux.1-pro-max": 24.0,
    "kimi-k2.6": 50.0,
    "deepseek-v4-pro": 45.0,
    "flux.1-ultra": 30.0,
    "glm-5.1": 60.0,
    "deepseek-v4-pro-x4": 180.0,
    "flux.1-ultra-x2": 60.0,
    "all-parallel": 0.0,
}


# ═══════════════════════════════════════════════════════════════════════════════
# FONCTIONS DE DÉTECTION
# ═══════════════════════════════════════════════════════════════════════════════

def detect_hardware() -> Dict[str, Any]:
    """
    Détecte le matériel disponible sur la machine.

    Retourne un dictionnaire avec :
      - cpu_model : modèle du processeur
      - cpu_cores : nombre de cœurs logiques
      - ram_total_gb : RAM totale en Go
      - ram_available_gb : RAM disponible en Go
      - gpu_present : booléen
      - gpu_name : nom du GPU (ou None)
      - gpu_vram_gb : VRAM du GPU en Go (ou 0)
      - gpu_count : nombre de GPU
      - disk_free_gb : espace disque disponible en Go
      - os_name : système d'exploitation
      - os_version : version de l'OS
    """
    info: Dict[str, Any] = {
        "cpu_model": "Inconnu",
        "cpu_cores": 1,
        "ram_total_gb": 0.0,
        "ram_available_gb": 0.0,
        "gpu_present": False,
        "gpu_name": None,
        "gpu_vram_gb": 0.0,
        "gpu_count": 0,
        "disk_free_gb": 0.0,
        "os_name": platform.system(),
        "os_version": platform.release(),
    }

    # ── CPU ──
    try:
        import psutil  # ✅ Réel
        info["cpu_model"] = platform.processor() or "Inconnu"
        info["cpu_cores"] = psutil.cpu_count(logical=True) or 1
    except ImportError:
        logger.warning("⚠️ psutil non installé — détection CPU limitée")
        info["cpu_model"] = platform.processor() or "Inconnu"
        info["cpu_cores"] = os.cpu_count() or 1

    # ── RAM ──
    try:
        import psutil  # ✅ Réel
        mem = psutil.virtual_memory()
        info["ram_total_gb"] = round(mem.total / (1024 ** 3), 1)
        info["ram_available_gb"] = round(mem.available / (1024 ** 3), 1)
    except ImportError:
        # Fallback lecture /proc/meminfo sur Linux
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        info["ram_total_gb"] = round(int(line.split()[1]) / 1024 / 1024, 1)
                    elif line.startswith("MemAvailable:"):
                        info["ram_available_gb"] = round(int(line.split()[1]) / 1024 / 1024, 1)
        except (FileNotFoundError, ValueError):
            logger.warning("⚠️ Impossible de détecter la RAM")

    # ── GPU ──
    # Méthode 1 : nvidia-smi (le plus fiable)
    gpu_detected = _detect_gpu_nvidia_smi(info)
    # Méthode 2 : torch.cuda
    if not gpu_detected:
        gpu_detected = _detect_gpu_torch(info)
    # Méthode 3 : GPUtil
    if not gpu_detected:
        gpu_detected = _detect_gpu_gputil(info)

    # ── Disque ──
    try:
        import psutil  # ✅ Réel
        disk = psutil.disk_usage("/")
        info["disk_free_gb"] = round(disk.free / (1024 ** 3), 1)
    except ImportError:
        try:
            result = subprocess.run(
                ["df", "-h", "/"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 4:
                    free_str = parts[3]
                    if free_str.endswith("G"):
                        info["disk_free_gb"] = round(float(free_str[:-1]), 1)
                    elif free_str.endswith("T"):
                        info["disk_free_gb"] = round(float(free_str[:-1]) * 1024, 1)
        except Exception:
            logger.warning("⚠️ Impossible de détecter l'espace disque")

    return info


def _detect_gpu_nvidia_smi(info: Dict[str, Any]) -> bool:
    """Détection GPU via nvidia-smi. ✅ Réel"""
    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        return False

    try:
        result = subprocess.run(
            [nvidia_smi, "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return False

        lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
        if not lines:
            return False

        # Premier GPU
        first = lines[0]
        parts = [p.strip() for p in first.split(",")]
        if len(parts) >= 2:
            info["gpu_present"] = True
            info["gpu_name"] = parts[0]
            try:
                info["gpu_vram_gb"] = round(float(parts[1]) / 1024, 1)
            except ValueError:
                info["gpu_vram_gb"] = 0.0
            info["gpu_count"] = len(lines)
            logger.info("GPU détecté via nvidia-smi : %s (%s Go VRAM)", parts[0], info["gpu_vram_gb"])
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        logger.debug("nvidia-smi échoué : %s", e)

    return False


def _detect_gpu_torch(info: Dict[str, Any]) -> bool:
    """Détection GPU via torch.cuda. ✅ Réel"""
    try:
        import torch  # ✅ Réel
        if torch.cuda.is_available():
            info["gpu_present"] = True
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_vram_gb"] = round(torch.cuda.get_device_properties(0).total_mem / (1024 ** 3), 1)
            info["gpu_count"] = torch.cuda.device_count()
            logger.info("GPU détecté via torch.cuda : %s", info["gpu_name"])
            return True
    except ImportError:
        logger.debug("torch non installé, détection GPU torch ignorée")
    except Exception as e:
        logger.debug("Erreur torch.cuda : %s", e)
    return False


def _detect_gpu_gputil(info: Dict[str, Any]) -> bool:
    """Détection GPU via GPUtil. ✅ Réel"""
    try:
        import GPUtil  # ✅ Réel
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            info["gpu_present"] = True
            info["gpu_name"] = gpu.name
            info["gpu_vram_gb"] = round(gpu.memoryTotal / 1024, 1)
            info["gpu_count"] = len(gpus)
            logger.info("GPU détecté via GPUtil : %s", gpu.name)
            return True
    except ImportError:
        logger.debug("GPUtil non installé, détection GPU GPUtil ignorée")
    except Exception as e:
        logger.debug("Erreur GPUtil : %s", e)
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION & RECOMMANDATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def classify_tier(info: Dict[str, Any]) -> str:
    """
    Classe le matériel dans un tier de performance.

    Règles :
      - Si GPU présent avec VRAM >= 8 Go → au moins "standard"
      - Si GPU présent avec VRAM >= 24 Go → au moins "pro"
      - Sinon, basé uniquement sur la RAM
    """
    ram = info.get("ram_total_gb", 0)
    gpu_present = info.get("gpu_present", False)
    vram = info.get("gpu_vram_gb", 0)

    # GPU boost : un GPU avec assez de VRAM monte le tier
    if gpu_present and vram >= 48:
        # Au moins ultra
        if ram >= 128:
            return "ultra"
        return "pro"
    if gpu_present and vram >= 24:
        if ram >= 64:
            return "pro"
        if ram >= 32:
            return "standard"
        return "standard"
    if gpu_present and vram >= 8:
        if ram >= 32:
            return "standard"
        return "light"

    # Pas de GPU : classification par RAM seule
    for tier_name, tier_info in TIERS.items():
        if ram <= tier_info["ram_max"]:
            return tier_name

    # Fallback : enterprise
    return "enterprise"


def get_recommended_models(tier: str) -> Dict[str, str]:
    """Retourne les modèles recommandés pour un tier donné."""
    return MODEL_GRID.get(tier, MODEL_GRID["ultra-light"])


def get_max_models(tier: str) -> int:
    """Retourne le nombre maximum de modèles simultanés pour un tier."""
    tier_info = TIERS.get(tier, TIERS["ultra-light"])
    return tier_info.get("max_models", 1)


def check_model_fits(model_name: str, available_ram_gb: float) -> bool:
    """
    Vérifie si un modèle peut tenir dans la RAM disponible.

    Utilise la table MODEL_SIZES_GB ou une estimation par défaut
    basée sur le nom du modèle.
    """
    size = MODEL_SIZES_GB.get(model_name)
    if size is None:
        # Estimation heuristique : extraire le nombre de paramètres du nom
        # ex: "deepseek-r1:8b" → 8 milliards → ~4.7 Go en Q4
        try:
            for part in model_name.split(":"):
                if part.endswith("b"):
                    params_b = float(part[:-1])
                    size = params_b * 0.6  # Q4 quantization ≈ 0.6 Go par milliard
                    break
        except (ValueError, IndexError):
            size = 5.0  # estimation prudente par défaut

    if size is None:
        size = 5.0

    # On garde 2 Go de marge pour le système
    return (size + 2.0) <= available_ram_gb


# ═══════════════════════════════════════════════════════════════════════════════
# RAPPORT DE DÉTECTION
# ═══════════════════════════════════════════════════════════════════════════════

def print_hardware_report(info: Optional[Dict[str, Any]] = None) -> str:
    """
    Affiche un rapport de détection matériel coloré dans le terminal.
    Retourne le rapport en texte brut.
    """
    if info is None:
        info = detect_hardware()

    tier = classify_tier(info)
    models = get_recommended_models(tier)
    tier_info = TIERS[tier]

    # ANSI couleurs
    B = "\033[1m"
    R = "\033[0m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"
    BLUE = "\033[34m"
    DIM = "\033[2m"

    gpu_str = f"{info['gpu_name']} ({info['gpu_vram_gb']} Go VRAM)" if info["gpu_present"] else "❌ Aucun GPU détecté"

    report = f"""
{CYAN}{B}╔══════════════════════════════════════════════╗{R}
{CYAN}{B}║        🖥️ LUYMAS AI - RAPPORT MATÉRIEL      ║{R}
{CYAN}{B}╠══════════════════════════════════════════════╣{R}
{CYAN}{B}║{R} 💻 CPU         : {GREEN}{info['cpu_model']}{R}
{CYAN}{B}║{R} 🔢 Cœurs       : {GREEN}{info['cpu_cores']}{R}
{CYAN}{B}║{R} 🧠 RAM Total   : {GREEN}{info['ram_total_gb']} Go{R}
{CYAN}{B}║{R} 🧠 RAM Libre   : {GREEN}{info['ram_available_gb']} Go{R}
{CYAN}{B}║{R} 🎮 GPU         : {GREEN if info['gpu_present'] else RED}{gpu_str}{R}
{CYAN}{B}║{R} 🎮 Nombre GPU  : {GREEN}{info['gpu_count']}{R}
{CYAN}{B}║{R} 💾 Disque      : {GREEN}{info['disk_free_gb']} Go libre{R}
{CYAN}{B}║{R} 🖥️ OS          : {BLUE}{info['os_name']} {info['os_version']}{R}
{CYAN}{B}╠══════════════════════════════════════════════╣{R}
{CYAN}{B}║{R} 📊 TIER        : {MAGENTA}{B}{tier.upper()}{R} {tier_info['emoji']}
{CYAN}{B}║{R} 📝 Description : {YELLOW}{tier_info['description']}{R}
{CYAN}{B}║{R} 🔢 Modèles max : {YELLOW}{get_max_models(tier) if get_max_models(tier) != -1 else '∞ (illimité)'}{R}
{CYAN}{B}╠══════════════════════════════════════════════╣{R}
{CYAN}{B}║{R} 🧠 Modèles recommandés :{R}
{CYAN}{B}║{R}   Raisonnement : {GREEN}{models.get('reasoning', 'N/A')}{R}
{CYAN}{B}║{R}   Code         : {GREEN}{models.get('code', 'N/A')}{R}
{CYAN}{B}║{R}   Design       : {GREEN}{models.get('image', 'N/A')}{R}
{CYAN}{B}║{R}   Rapide       : {GREEN}{models.get('fast', 'N/A')}{R}
{CYAN}{B}╚══════════════════════════════════════════════╝{R}
"""
    print(report)

    # Version texte brut (sans ANSI)
    plain_report = f"""
╔══════════════════════════════════════════════╗
║        🖥️ LUYMAS AI - RAPPORT MATÉRIEL      ║
╠══════════════════════════════════════════════╣
║ 💻 CPU         : {info['cpu_model']}
║ 🔢 Cœurs       : {info['cpu_cores']}
║ 🧠 RAM Total   : {info['ram_total_gb']} Go
║ 🧠 RAM Libre   : {info['ram_available_gb']} Go
║ 🎮 GPU         : {gpu_str}
║ 🎮 Nombre GPU  : {info['gpu_count']}
║ 💾 Disque      : {info['disk_free_gb']} Go libre
║ 🖥️ OS          : {info['os_name']} {info['os_version']}
╠══════════════════════════════════════════════╣
║ 📊 TIER        : {tier.upper()} {tier_info['emoji']}
║ 📝 Description : {tier_info['description']}
║ 🔢 Modèles max : {get_max_models(tier) if get_max_models(tier) != -1 else '∞ (illimité)'}
╠══════════════════════════════════════════════╣
║ 🧠 Modèles recommandés :
║   Raisonnement : {models.get('reasoning', 'N/A')}
║   Code         : {models.get('code', 'N/A')}
║   Design       : {models.get('image', 'N/A')}
║   Rapide       : {models.get('fast', 'N/A')}
╚══════════════════════════════════════════════╝
"""
    return plain_report


# ═══════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
    hw = detect_hardware()
    print_hardware_report(hw)
