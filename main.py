"""
Luymas AI - Main Entry Point
Starts the multi-agent system
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(PROJECT_ROOT / "logs" / "luymas.log", mode="a"),
    ],
)
logger = logging.getLogger("luymas")


async def main():
    """Main entry point for Luymas AI."""
    logger.info("=" * 60)
    logger.info("  LUYMAS AI - Multi-Agent System")
    logger.info("  Version: 1.0.0")
    logger.info("=" * 60)

    # Import core modules
    from core.orchestrator import Orchestrator
    from core.messenger import Messenger
    from core.memory import KnowledgeMesh

    # Initialize the orchestrator
    logger.info("Initializing Orchestrator...")
    orchestrator = Orchestrator()

    # Initialize memory
    logger.info("Initializing Knowledge Mesh...")
    memory = KnowledgeMesh()

    # Initialize messenger
    logger.info("Initializing Messenger...")
    messenger = Messenger()

    # Register agents
    from agents import create_agent, AGENT_REGISTRY

    logger.info(f"Registering {len(AGENT_REGISTRY)} agents...")
    for agent_name in AGENT_REGISTRY:
        try:
            agent = create_agent(agent_name)
            orchestrator.register_agent(agent)
            logger.info(f"  ✅ Registered: {agent_name}")
        except Exception as e:
            logger.error(f"  ❌ Failed to register {agent_name}: {e}")

    # Check Ollama connection
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    logger.info(f"Checking Ollama at {ollama_host}...")
    try:
        import ollama
        client = ollama.Client(host=ollama_host)
        models = client.list()
        logger.info(f"  ✅ Ollama connected with {len(models.get('models', []))} models")
        for model in models.get("models", []):
            logger.info(f"     - {model.get('name', 'unknown')}")
    except Exception as e:
        logger.warning(f"  ⚠️ Ollama not available: {e}")
        logger.warning("  Some features will be limited. Start Ollama: ollama serve")

    # Startup complete
    logger.info("")
    logger.info("🎉 Luymas AI is ready!")
    logger.info("")
    logger.info("Available commands:")
    logger.info("  - Type a project description to start a workflow")
    logger.info("  - 'status' to see agent status")
    logger.info("  - 'models' to list available models")
    logger.info("  - 'quit' to exit")
    logger.info("")

    # Interactive mode
    while True:
        try:
            user_input = input("\n🤖 Luymas> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                logger.info("Shutting down Luymas AI...")
                break
            elif user_input.lower() == "status":
                status = orchestrator.get_system_status()
                for agent_name, agent_status in status.items():
                    print(f"  {agent_name}: {agent_status}")
            elif user_input.lower() == "models":
                try:
                    import ollama
                    client = ollama.Client(host=ollama_host)
                    models = client.list()
                    for model in models.get("models", []):
                        print(f"  - {model.get('name', 'unknown')} ({model.get('size', 'unknown')})")
                except Exception as e:
                    print(f"  Error listing models: {e}")
            else:
                # Start a workflow
                logger.info(f"Starting workflow for: {user_input[:100]}...")
                try:
                    result = await orchestrator.start_workflow(user_input)
                    logger.info(f"Workflow started: {result}")
                except Exception as e:
                    logger.error(f"Workflow error: {e}")
        except KeyboardInterrupt:
            logger.info("\nShutting down Luymas AI...")
            break
        except EOFError:
            break


if __name__ == "__main__":
    asyncio.run(main())
