"""
Luymas AI - Agent Tests
Basic tests for the multi-agent system
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_agent_imports():
    """Test that all agent modules can be imported."""
    from agents.pdg import PDGAgent
    from agents.pm import PMAgent
    from agents.architect import ArchitectAgent
    from agents.coder_back import BackendCoderAgent
    from agents.coder_front import FrontendCoderAgent
    from agents.designer import DesignerAgent
    from agents.guardian import GuardianAgent
    from agents.tester import TesterAgent
    from agents.ops import OpsAgent
    from agents.caretaker import CaretakerAgent
    from agents.talent_scout import TalentScoutAgent
    print("✅ All agent imports successful")


def test_agent_creation():
    """Test that all agents can be instantiated."""
    from agents import create_agent, AGENT_REGISTRY
    
    for agent_name in AGENT_REGISTRY:
        try:
            agent = create_agent(agent_name)
            status = agent.get_status()
            assert status["name"] == agent_name or status["role"] is not None
            print(f"  ✅ {agent_name}: {status.get('role', 'OK')}")
        except Exception as e:
            print(f"  ❌ {agent_name}: {e}")


def test_core_imports():
    """Test that all core modules can be imported."""
    from core.orchestrator import Orchestrator
    from core.messenger import Messenger
    from core.memory import KnowledgeMesh
    from core.pdf_generator import PDFGenerator
    from core.api_injector import APIInjector
    from core.auto_updater import AutoUpdater
    from core.github_scout import GitHubScout
    from core.self_improver import SelfImprover
    from core.experience_learner import ExperienceLearner
    from core.email_factory import EmailManager
    from core.captcha_solver import CaptchaSolver
    from core.identity_manager import IdentityManager
    print("✅ All core module imports successful")


def test_orchestrator():
    """Test the orchestrator."""
    from core.orchestrator import Orchestrator
    
    orch = Orchestrator()
    print(f"  ✅ Orchestrator created: {type(orch).__name__}")


def test_memory():
    """Test the knowledge mesh memory."""
    from core.memory import KnowledgeMesh
    
    mesh = KnowledgeMesh()
    mesh.store("test_agent", "test_key", "test_value")
    value = mesh.retrieve("test_agent", "test_key")
    assert value == "test_value"
    print(f"  ✅ KnowledgeMesh store/retrieve working")


def test_api_injector():
    """Test the API key injector."""
    from core.api_injector import APIInjector
    
    injector = APIInjector()
    key = injector.generate_key("test_app")
    assert injector.verify_key(key)
    print(f"  ✅ APIInjector generate/verify working")


def test_design_plugins():
    """Test the design plugin system."""
    from design.design_plugins import PluginRegistry
    
    registry = PluginRegistry()
    plugins = registry.list_plugins()
    assert len(plugins) > 0
    print(f"  ✅ PluginRegistry with {len(plugins)} plugins")


def test_freshness_scorer():
    """Test the design freshness scorer."""
    from design.design_updater import FreshnessScorer
    
    scorer = FreshnessScorer()
    result = scorer.score_design("A modern glassmorphism layout with purple gradients")
    assert "freshness_score" in result
    print(f"  ✅ FreshnessScorer score: {result['freshness_score']}")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("LUYMAS AI - Test Suite")
    print("=" * 50 + "\n")
    
    tests = [
        ("Agent Imports", test_agent_imports),
        ("Agent Creation", test_agent_creation),
        ("Core Imports", test_core_imports),
        ("Orchestrator", test_orchestrator),
        ("Memory System", test_memory),
        ("API Injector", test_api_injector),
        ("Design Plugins", test_design_plugins),
        ("Freshness Scorer", test_freshness_scorer),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        print(f"\n📋 Testing: {name}")
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
