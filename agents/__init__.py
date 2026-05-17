"""
LUYMAS AI — Agent Module

This module contains all agents in the Luymas AI multi-agent system.
Each agent is a specialized Python class inheriting from BaseAgent,
with its own system prompt, skills, and message handling logic.

Agents:
    PDGAgent         — CEO / Supreme Orchestrator
    PMAgent          — Product Manager
    ArchitectAgent   — Software Architect
    CoderBackAgent   — Backend Code Generation
    CoderFrontAgent  — Frontend Code Generation
    DesignerAgent    — Design & Visual
    GuardianAgent    — Security & Quality
    TesterAgent      — QA & Testing
    OpsAgent         — DevOps & Deployment
    CaretakerAgent   — Post-Deployment Monitoring
    TalentScoutAgent — Team Building & Agent Discovery

Usage:
    from agents import PDGAgent, PMAgent, ArchitectAgent
    from agents import CoderBackAgent, CoderFrontAgent
    from agents import DesignerAgent, GuardianAgent
    from agents import TesterAgent, OpsAgent, CaretakerAgent, TalentScoutAgent
    from agents import BaseAgent, AgentStatus, AgentMessage
"""

from agents.pdg import PDGAgent
from agents.pm import PMAgent
from agents.architect import ArchitectAgent
from agents.coder_back import CoderBackAgent
from agents.coder_front import CoderFrontAgent
from agents.designer import DesignerAgent
from agents.guardian import GuardianAgent
from agents.tester import TesterAgent
from agents.ops import OpsAgent
from agents.caretaker import CaretakerAgent
from agents.talent_scout import TalentScoutAgent

# Re-export base classes for convenience
from agents.pdg import BaseAgent, AgentStatus, AgentMessage

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentStatus",
    "AgentMessage",
    # Agent classes
    "PDGAgent",
    "PMAgent",
    "ArchitectAgent",
    "CoderBackAgent",
    "CoderFrontAgent",
    "DesignerAgent",
    "GuardianAgent",
    "TesterAgent",
    "OpsAgent",
    "CaretakerAgent",
    "TalentScoutAgent",
]

# Agent registry for dynamic instantiation
AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    "pdg": PDGAgent,
    "pm": PMAgent,
    "architect": ArchitectAgent,
    "coder_back": CoderBackAgent,
    "coder_front": CoderFrontAgent,
    "designer": DesignerAgent,
    "guardian": GuardianAgent,
    "tester": TesterAgent,
    "ops": OpsAgent,
    "caretaker": CaretakerAgent,
    "talent_scout": TalentScoutAgent,
}


def create_agent(agent_type: str, **kwargs) -> BaseAgent:
    """
    Factory function to create an agent by type name.

    Args:
        agent_type: The type key for the agent (e.g. 'pdg', 'coder_back').
        **kwargs: Additional keyword arguments passed to the agent constructor.

    Returns:
        An instance of the requested agent.

    Raises:
        ValueError: If the agent_type is not recognized.
    """
    if agent_type not in AGENT_REGISTRY:
        raise ValueError(
            f"Unknown agent type: '{agent_type}'. "
            f"Available types: {list(AGENT_REGISTRY.keys())}"
        )
    return AGENT_REGISTRY[agent_type](**kwargs)


def list_agents() -> dict[str, str]:
    """
    List all available agent types and their roles.

    Returns:
        A dictionary mapping agent type keys to their role descriptions.
    """
    # Create temporary instances to get role info
    return {
        key: cls().role
        for key, cls in AGENT_REGISTRY.items()
    }
