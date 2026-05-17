#!/usr/bin/env python3
"""
Luymas AI - Launcher

Main entry point that starts the multi-agent system:
- Detects and starts Ollama server
- Starts Flask web server for Studio on port 5000
- Starts the Orchestrator in a background thread
- Opens the browser to http://localhost:5000
- Handles graceful shutdown (Ctrl+C)
- Checks all dependencies before starting
- Downloads required models if missing
- Logs everything to logs/luymas.log
"""

from __future__ import annotations

import logging
import os
import platform
import signal
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional

# ── Project paths ─────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# ── Logging Setup ─────────────────────────────────────────────────────────────

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "luymas.log", mode="a", encoding="utf-8"),
    ],
)
logger = logging.getLogger("luymas.launcher")

# ── Constants ─────────────────────────────────────────────────────────────────

VERSION = "1.0.0"
STUDIO_PORT = int(os.environ.get("LUYMAS_STUDIO_PORT", "5000"))
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
REQUIRED_MODELS = [
    "deepseek-r1:8b",
    "qwen2.5-coder:7b",
    "gemma3:4b",
    "z-image-turbo",
    "llama3.2:3b",
]

# ── ASCII Art Banner ──────────────────────────────────────────────────────────

BANNER = r"""
  ╔═══════════════════════════════════════════════════════════╗
  ║                                                           ║
  ║     _      _                          __  _               ║
  ║    | |    | |                        / _|| |              ║
  ║    | | ___| | __ _ _ __   __ _  ___ | |_ | |__   __ _     ║
  ║    | |/ _ \ |/ _` | '_ \ / _` |/ _ \|  _|| '_ \ / _` |    ║
  ║    | |  __/ | (_| | | | | (_| | (_) | |  | |_) | (_| |    ║
  ║    |_|\___|_|\__,_|_| |_|\__, |\___/|_|  |_.__/ \__,_|    ║
  ║                           __/ |                           ║
  ║                          |___/                            ║
  ║                                                           ║
  ║       Multi-Agent AI System  v{version}                    ║
  ║       Bienvenue ! Votre equipe vous attend.               ║
  ║                                                           ║
  ╚═══════════════════════════════════════════════════════════╝
""".format(version=VERSION)


# ── Dependency Checks ─────────────────────────────────────────────────────────

def check_python_version() -> bool:
    """Ensure Python 3.10+ is running."""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 10):
        logger.error("Python 3.10+ required, found %d.%d", major, minor)
        return False
    logger.info("Python %d.%d.%d detected", major, minor, sys.version_info.micro)
    return True


def check_python_packages() -> list[str]:
    """Check for required Python packages and return list of missing ones."""
    required = [
        ("ollama", "ollama"),
        ("yaml", "pyyaml"),
        ("flask", "flask"),
        ("dotenv", "python-dotenv"),
        ("aiohttp", "aiohttp"),
        ("requests", "requests"),
        ("PIL", "Pillow"),
        ("pydantic", "pydantic"),
    ]
    missing = []
    for module_name, pip_name in required:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(pip_name)
            logger.warning("Missing Python package: %s (pip install %s)", module_name, pip_name)
    return missing


def check_ollama_installed() -> bool:
    """Check if Ollama binary is available on the system."""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            version_str = result.stdout.strip() or result.stderr.strip()
            logger.info("Ollama installed: %s", version_str)
            return True
    except FileNotFoundError:
        logger.warning("Ollama binary not found in PATH")
    except subprocess.TimeoutExpired:
        logger.warning("Ollama version check timed out")
    except Exception as e:
        logger.warning("Ollama check failed: %s", e)
    return False


def check_ollama_running() -> bool:
    """Check if Ollama server is responding."""
    try:
        import requests
        resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            model_count = len(data.get("models", []))
            logger.info("Ollama server running with %d model(s)", model_count)
            return True
    except ImportError:
        # Fallback without requests
        try:
            import urllib.request
            with urllib.request.urlopen(f"{OLLAMA_HOST}/api/tags", timeout=5) as resp:
                if resp.status == 200:
                    import json
                    data = json.loads(resp.read())
                    model_count = len(data.get("models", []))
                    logger.info("Ollama server running with %d model(s)", model_count)
                    return True
        except Exception:
            pass
    except Exception as e:
        logger.debug("Ollama server not responding: %s", e)
    return False


def start_ollama_server() -> Optional[subprocess.Popen]:
    """Start Ollama server as a background process."""
    logger.info("Starting Ollama server...")
    try:
        # On Windows, use CREATE_NEW_PROCESS_GROUP for proper background process
        kwargs = {}
        if platform.system() == "Windows":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
            proc = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **kwargs,
            )
        else:
            proc = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

        # Wait for Ollama to be ready
        logger.info("Waiting for Ollama server to start...")
        for attempt in range(30):
            time.sleep(1)
            if check_ollama_running():
                logger.info("Ollama server started successfully")
                return proc
            if attempt % 5 == 4:
                logger.info("Still waiting for Ollama... (%d/30)", attempt + 1)

        logger.warning("Ollama server did not respond within 30 seconds")
        return proc
    except FileNotFoundError:
        logger.error("Cannot start Ollama: 'ollama' not found in PATH")
        return None
    except Exception as e:
        logger.error("Failed to start Ollama server: %s", e)
        return None


def check_and_download_models() -> None:
    """Check for required models and offer to download missing ones."""
    try:
        import ollama
        client = ollama.Client(host=OLLAMA_HOST)
        models_data = client.list()
        installed = {m.get("name", "").split(":")[0] + ":" + m.get("name", "").split(":")[-1]
                     if ":" in m.get("name", "") else m.get("name", "")
                     for m in models_data.get("models", [])}

        # Also build a simpler set for matching
        installed_simple = set()
        for m in models_data.get("models", []):
            name = m.get("name", "")
            installed_simple.add(name)
            # Also add without tag
            if ":" in name:
                installed_simple.add(name.split(":")[0])

        missing = []
        for model in REQUIRED_MODELS:
            if model not in installed_simple and model not in installed:
                missing.append(model)

        if not missing:
            logger.info("All required models are installed")
            return

        logger.warning("Missing models: %s", ", ".join(missing))
        logger.info("Downloading missing models...")

        for model in missing:
            logger.info("Pulling model: %s ...", model)
            try:
                client.pull(model)
                logger.info("Model %s downloaded successfully", model)
            except Exception as e:
                logger.warning("Failed to download %s: %s", model, e)
                logger.info("You can download it later: ollama pull %s", model)

    except ImportError:
        logger.warning("Ollama Python client not available, skipping model check")
    except Exception as e:
        logger.warning("Could not check/download models: %s", e)


# ── Flask Studio Server ───────────────────────────────────────────────────────

def create_flask_app():
    """Create and configure the Flask application for Studio."""
    from flask import Flask, send_from_directory, jsonify, request
    from dotenv import load_dotenv

    # Load .env
    load_dotenv(PROJECT_ROOT / ".env")

    app = Flask(
        __name__,
        static_folder=str(PROJECT_ROOT / "studio"),
        static_url_path="/static",
    )

    # Global reference to orchestrator
    app.config["ORCHESTRATOR"] = None

    @app.route("/")
    def index():
        """Serve the Studio SPA."""
        return send_from_directory(str(PROJECT_ROOT / "studio"), "index.html")

    @app.route("/<path:filename>")
    def studio_files(filename):
        """Serve Studio static files."""
        return send_from_directory(str(PROJECT_ROOT / "studio"), filename)

    @app.route("/api/status")
    def api_status():
        """System status endpoint."""
        orch = app.config.get("ORCHESTRATOR")
        status = {
            "version": VERSION,
            "status": "running",
            "ollama_host": OLLAMA_HOST,
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.system(),
        }
        if orch:
            status["project"] = orch.get_project_status()
        return jsonify(status)

    @app.route("/api/agents")
    def api_agents():
        """List registered agents."""
        orch = app.config.get("ORCHESTRATOR")
        if orch:
            agents = orch.registry.list_all()
            return jsonify([
                {
                    "name": a.name,
                    "role": a.role,
                    "status": a.status.value,
                    "capabilities": a.capabilities,
                    "current_task": a.current_task,
                }
                for a in agents
            ])
        return jsonify([])

    @app.route("/api/models")
    def api_models():
        """List available Ollama models."""
        try:
            import ollama
            client = ollama.Client(host=OLLAMA_HOST)
            models = client.list()
            return jsonify(models.get("models", []))
        except Exception as e:
            return jsonify({"error": str(e)}), 503

    @app.route("/api/workflow", methods=["POST"])
    def api_start_workflow():
        """Start a new workflow."""
        import asyncio
        data = request.get_json(force=True)
        description = data.get("description", "")
        if not description:
            return jsonify({"error": "description is required"}), 400

        orch = app.config.get("ORCHESTRATOR")
        if orch:
            try:
                loop = asyncio.new_event_loop()
                workflow_id = loop.run_until_complete(orch.start_workflow(description))
                loop.close()
                return jsonify({"workflow_id": workflow_id, "status": "started"})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        return jsonify({"error": "Orchestrator not initialized"}), 503

    @app.route("/api/approvals")
    def api_approvals():
        """List pending approval requests."""
        orch = app.config.get("ORCHESTRATOR")
        if orch:
            pending = orch.approval_pipeline.get_pending()
            return jsonify([
                {
                    "id": r.id,
                    "agent_name": r.agent_name,
                    "action": r.action,
                    "details": r.details,
                    "created_at": r.created_at.isoformat(),
                }
                for r in pending
            ])
        return jsonify([])

    @app.route("/api/approvals/<request_id>/approve", methods=["POST"])
    def api_approve(request_id):
        """Approve a pending request."""
        import asyncio
        orch = app.config.get("ORCHESTRATOR")
        if orch:
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(orch.approval_pipeline.approve(request_id))
            loop.close()
            return jsonify({"approved": result})
        return jsonify({"error": "Orchestrator not initialized"}), 503

    @app.route("/api/approvals/<request_id>/reject", methods=["POST"])
    def api_reject(request_id):
        """Reject a pending request."""
        import asyncio
        orch = app.config.get("ORCHESTRATOR")
        if orch:
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(orch.approval_pipeline.reject(request_id))
            loop.close()
            return jsonify({"rejected": result})
        return jsonify({"error": "Orchestrator not initialized"}), 503

    @app.route("/api/health")
    def api_health():
        """Health check endpoint."""
        return jsonify({"status": "ok", "version": VERSION})

    return app


# ── Orchestrator Thread ───────────────────────────────────────────────────────

def start_orchestrator(app, stop_event: threading.Event) -> None:
    """Initialize and run the orchestrator in the background."""
    try:
        from dotenv import load_dotenv
        load_dotenv(PROJECT_ROOT / ".env")

        from core.orchestrator import Orchestrator
        from core.memory import KnowledgeMesh
        from core.messenger import Messenger
        from agents import create_agent, AGENT_REGISTRY

        logger.info("Initializing Orchestrator...")
        orchestrator = Orchestrator()

        logger.info("Initializing Knowledge Mesh...")
        memory = KnowledgeMesh()

        logger.info("Initializing Messenger...")
        messenger = Messenger()

        # Register all agents
        logger.info("Registering %d agents...", len(AGENT_REGISTRY))
        for agent_name in AGENT_REGISTRY:
            try:
                agent = create_agent(agent_name)
                orchestrator.register_agent(agent)
                logger.info("  ✅ Registered: %s", agent_name)
            except Exception as e:
                logger.error("  ❌ Failed to register %s: %s", agent_name, e)

        # Store orchestrator in Flask app config for API access
        app.config["ORCHESTRATOR"] = orchestrator

        logger.info("Orchestrator initialized with %d agents", len(AGENT_REGISTRY))

        # Keep the orchestrator alive until stop event
        while not stop_event.is_set():
            stop_event.wait(timeout=5)

        logger.info("Orchestrator shutting down...")

    except ImportError as e:
        logger.error("Failed to import core modules: %s", e)
        logger.info("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        logger.error("Orchestrator error: %s", e, exc_info=True)


# ── Main Launcher ─────────────────────────────────────────────────────────────

class LuymasLauncher:
    """Main launcher class managing the full system lifecycle."""

    def __init__(self):
        self.flask_app = None
        self.ollama_process: Optional[subprocess.Popen] = None
        self.orchestrator_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self._shutting_down = False

    def run(self) -> None:
        """Run the complete launcher sequence."""
        # Print banner
        print(BANNER)

        # ── Pre-flight checks ────────────────────────────────────────────
        logger.info("=" * 60)
        logger.info("  LUYMAS AI - Multi-Agent System v%s", VERSION)
        logger.info("=" * 60)

        # 1. Python version
        if not check_python_version():
            sys.exit(1)

        # 2. Python packages
        missing = check_python_packages()
        if missing:
            logger.warning("Missing packages: %s", ", ".join(missing))
            logger.info("Install them with: pip install %s", " ".join(missing))
            answer = input("Continue anyway? (y/N): ").strip().lower()
            if answer != "y":
                sys.exit(1)

        # 3. Load .env
        try:
            from dotenv import load_dotenv
            env_path = PROJECT_ROOT / ".env"
            if env_path.exists():
                load_dotenv(env_path)
                logger.info("Loaded .env from %s", env_path)
            else:
                logger.warning(".env file not found, using defaults")
        except ImportError:
            logger.warning("python-dotenv not installed, skipping .env")

        # 4. Ollama
        ollama_installed = check_ollama_installed()
        ollama_running = False

        if ollama_installed:
            ollama_running = check_ollama_running()
            if not ollama_running:
                self.ollama_process = start_ollama_server()
                if self.ollama_process:
                    ollama_running = check_ollama_running()
        else:
            logger.warning("Ollama is not installed. Some features will be limited.")
            logger.info("Install Ollama: https://ollama.com/download")

        # 5. Check/download models
        if ollama_running:
            check_and_download_models()

        # 6. Create Flask app
        try:
            self.flask_app = create_flask_app()
        except ImportError as e:
            logger.error("Flask not available: %s", e)
            logger.info("Install Flask: pip install flask")
            sys.exit(1)
        except Exception as e:
            logger.error("Failed to create Flask app: %s", e)
            sys.exit(1)

        # ── Start subsystems ─────────────────────────────────────────────

        # Start Orchestrator in background thread
        logger.info("Starting Orchestrator in background thread...")
        self.orchestrator_thread = threading.Thread(
            target=start_orchestrator,
            args=(self.flask_app, self.stop_event),
            name="luymas-orchestrator",
            daemon=True,
        )
        self.orchestrator_thread.start()
        logger.info("Orchestrator thread started")

        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Open browser after a short delay
        studio_url = f"http://localhost:{STUDIO_PORT}"
        threading.Thread(
            target=self._open_browser,
            args=(studio_url,),
            daemon=True,
        ).start()

        # Start Flask server (this blocks until shutdown)
        logger.info("Starting Studio web server on port %d...", STUDIO_PORT)
        logger.info("Studio URL: %s", studio_url)
        logger.info("")
        logger.info("🚀 Luymas AI is running!")
        logger.info("   Press Ctrl+C to shut down")
        logger.info("")

        try:
            self.flask_app.run(
                host="0.0.0.0",
                port=STUDIO_PORT,
                debug=False,
                use_reloader=False,
                threaded=True,
            )
        except KeyboardInterrupt:
            pass
        except Exception as e:
            logger.error("Flask server error: %s", e)

        self._shutdown()

    def _open_browser(self, url: str) -> None:
        """Open browser after a short delay."""
        time.sleep(2.5)
        try:
            webbrowser.open(url)
            logger.info("Browser opened to %s", url)
        except Exception as e:
            logger.warning("Could not open browser: %s", e)
            logger.info("Open manually: %s", url)

    def _signal_handler(self, signum, frame) -> None:
        """Handle Ctrl+C and termination signals."""
        if self._shutting_down:
            return
        self._shutting_down = True
        logger.info("")
        logger.info("Shutdown signal received (signal %d)", signum)
        self._shutdown()
        sys.exit(0)

    def _shutdown(self) -> None:
        """Gracefully shut down all subsystems."""
        if self._shutting_down:
            return
        self._shutting_down = True

        logger.info("Shutting down Luymas AI...")

        # Stop orchestrator thread
        self.stop_event.set()
        if self.orchestrator_thread and self.orchestrator_thread.is_alive():
            self.orchestrator_thread.join(timeout=5)
            logger.info("Orchestrator thread stopped")

        # Stop Ollama server if we started it
        if self.ollama_process and self.ollama_process.poll() is None:
            logger.info("Stopping Ollama server...")
            try:
                self.ollama_process.terminate()
                self.ollama_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ollama_process.kill()
            except Exception as e:
                logger.warning("Error stopping Ollama: %s", e)
            logger.info("Ollama server stopped")

        logger.info("Luymas AI shut down complete. Au revoir !")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    launcher = LuymasLauncher()
    launcher.run()
