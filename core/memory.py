"""
core/memory.py - Shared Memory (Knowledge Mesh) for Luymas AI

Implements the KNOWLEDGE_MESH concept: a vector-like store for agent memories,
knowledge graph for concept relationships, project history, and experience store.
All data can be persisted to KNOWLEDGE_MESH.md.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

KNOWLEDGE_MESH_PATH = Path.home() / ".luymas" / "KNOWLEDGE_MESH.md"


# ── Data Models ──────────────────────────────────────────────────────────────

class MemoryType(str, Enum):
    FACT = "fact"
    DECISION = "decision"
    EXPERIENCE = "experience"
    PATTERN = "pattern"
    LESSON = "lesson"
    CONTEXT = "context"


@dataclass
class MemoryEntry:
    """A single memory record in the store."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    agent_name: str = ""
    key: str = ""
    value: Any = None
    memory_type: MemoryType = MemoryType.FACT
    embedding: list[float] = field(default_factory=list)  # Vector embedding placeholder
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    accessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0


@dataclass
class GraphNode:
    """A node in the knowledge graph."""
    id: str = ""
    label: str = ""
    node_type: str = "concept"
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """An edge connecting two graph nodes."""
    source: str = ""
    target: str = ""
    relation: str = "related_to"
    weight: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class Experience:
    """A project experience record (what worked, what failed)."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    project_id: str = ""
    what_worked: list[str] = field(default_factory=list)
    what_failed: list[str] = field(default_factory=list)
    context: str = ""
    lessons: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SearchResult:
    """Result from a memory search."""
    entry: MemoryEntry
    score: float = 0.0


# ── Simple Vector Operations ────────────────────────────────────────────────

def _simple_hash_embedding(text: str, dim: int = 64) -> list[float]:
    """Generate a deterministic pseudo-embedding from text using hashing.

    This is a lightweight placeholder for real embedding models (e.g.,
    sentence-transformers). It produces normalized vectors suitable for
    cosine similarity computation.
    """
    vec = [0.0] * dim
    for i in range(dim):
        h = hashlib.md5(f"{text}:{i}".encode()).hexdigest()
        vec[i] = int(h[:8], 16) / 0xFFFFFFFF
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ── Memory Store ─────────────────────────────────────────────────────────────

class MemoryStore:
    """Vector-like store for agent memories with similarity search."""

    def __init__(self, embedding_fn=_simple_hash_embedding) -> None:
        self._entries: dict[str, MemoryEntry] = {}
        self._index_by_key: dict[str, str] = {}  # agent:key -> entry_id
        self._embedding_fn = embedding_fn

    def store(self, agent_name: str, key: str, value: Any,
              memory_type: MemoryType = MemoryType.FACT,
              metadata: Optional[dict] = None) -> str:
        """Store a memory entry with auto-generated embedding."""
        # De-duplicate by agent+key
        idx_key = f"{agent_name}:{key}"
        if idx_key in self._index_by_key:
            old_id = self._index_by_key[idx_key]
            del self._entries[old_id]

        embedding = self._embedding_fn(f"{key} {value}")
        entry = MemoryEntry(
            agent_name=agent_name, key=key, value=value,
            memory_type=memory_type, embedding=embedding,
            metadata=metadata or {},
        )
        self._entries[entry.id] = entry
        self._index_by_key[idx_key] = entry.id
        logger.debug("Stored memory '%s' for %s (type=%s)", key, agent_name, memory_type.value)
        return entry.id

    def retrieve(self, agent_name: str, key: str) -> Optional[Any]:
        """Retrieve a value by agent name and key."""
        idx_key = f"{agent_name}:{key}"
        entry_id = self._index_by_key.get(idx_key)
        if entry_id and entry_id in self._entries:
            entry = self._entries[entry_id]
            entry.accessed_at = datetime.now(timezone.utc)
            entry.access_count += 1
            return entry.value
        return None

    def search(self, query: str, filters: Optional[dict] = None,
               limit: int = 10, threshold: float = 0.3) -> list[SearchResult]:
        """Search memories by semantic similarity and optional filters."""
        query_vec = self._embedding_fn(query)
        results: list[SearchResult] = []

        for entry in self._entries.values():
            if filters:
                if not self._matches_filters(entry, filters):
                    continue
            score = _cosine_similarity(query_vec, entry.embedding)
            if score >= threshold:
                results.append(SearchResult(entry=entry, score=score))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    def _matches_filters(self, entry: MemoryEntry, filters: dict) -> bool:
        for k, v in filters.items():
            if k == "agent_name" and entry.agent_name != v:
                return False
            if k == "memory_type" and entry.memory_type.value != v:
                return False
            if k in entry.metadata and entry.metadata[k] != v:
                return False
        return True

    def delete(self, entry_id: str) -> bool:
        entry = self._entries.pop(entry_id, None)
        if entry:
            idx_key = f"{entry.agent_name}:{entry.key}"
            self._index_by_key.pop(idx_key, None)
            return True
        return False

    def list_all(self) -> list[MemoryEntry]:
        return list(self._entries.values())


# ── Knowledge Graph ──────────────────────────────────────────────────────────

class KnowledgeGraph:
    """Simple in-memory knowledge graph for concept relationships."""

    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}
        self._edges: list[GraphEdge] = []
        self._adjacency: dict[str, list[GraphEdge]] = defaultdict(list)

    def add_node(self, node_id: str, label: str, node_type: str = "concept",
                 properties: Optional[dict] = None) -> GraphNode:
        node = GraphNode(id=node_id, label=label, node_type=node_type,
                         properties=properties or {})
        self._nodes[node_id] = node
        return node

    def add_edge(self, source: str, target: str, relation: str = "related_to",
                 weight: float = 1.0) -> GraphEdge:
        edge = GraphEdge(source=source, target=target, relation=relation, weight=weight)
        self._edges.append(edge)
        self._adjacency[source].append(edge)
        return edge

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self._nodes.get(node_id)

    def get_neighbors(self, node_id: str, relation: Optional[str] = None) -> list[GraphNode]:
        neighbors = []
        for edge in self._adjacency.get(node_id, []):
            if relation and edge.relation != relation:
                continue
            node = self._nodes.get(edge.target)
            if node:
                neighbors.append(node)
        return neighbors

    def find_path(self, start: str, end: str, max_depth: int = 5) -> list[str]:
        """BFS to find shortest path between two nodes."""
        if start not in self._nodes or end not in self._nodes:
            return []
        visited = {start}
        queue = [[start]]
        while queue:
            path = queue.pop(0)
            if len(path) > max_depth:
                break
            current = path[-1]
            if current == end:
                return path
            for edge in self._adjacency.get(current, []):
                if edge.target not in visited:
                    visited.add(edge.target)
                    queue.append(path + [edge.target])
        return []


# ── Project History ──────────────────────────────────────────────────────────

class ProjectHistory:
    """Stores and retrieves past project learnings."""

    def __init__(self) -> None:
        self._projects: dict[str, dict[str, Any]] = {}

    def record_project(self, project_id: str, data: dict[str, Any]) -> None:
        """Record a completed project's data."""
        data["recorded_at"] = datetime.now(timezone.utc).isoformat()
        self._projects[project_id] = data
        logger.info("Recorded project %s", project_id)

    def get_project(self, project_id: str) -> Optional[dict[str, Any]]:
        return self._projects.get(project_id)

    def list_projects(self) -> list[dict[str, Any]]:
        return list(self._projects.values())


# ── Experience Store ─────────────────────────────────────────────────────────

class ExperienceStore:
    """Stores what worked and what failed across projects."""

    def __init__(self) -> None:
        self._experiences: dict[str, Experience] = {}

    def add_experience(self, project_id: str, what_worked: list[str],
                       what_failed: list[str], context: str = "",
                       lessons: Optional[list[str]] = None) -> str:
        """Record a project experience."""
        exp = Experience(
            project_id=project_id, what_worked=what_worked,
            what_failed=what_failed, context=context,
            lessons=lessons or [],
        )
        self._experiences[exp.id] = exp
        logger.info("Added experience for project %s", project_id)
        return exp.id

    def get_relevant_experience(self, context: str, limit: int = 5) -> list[Experience]:
        """Find experiences relevant to a given context using keyword matching."""
        context_lower = context.lower()
        scored: list[tuple[float, Experience]] = []
        context_words = set(context_lower.split())

        for exp in self._experiences.values():
            exp_words = set(exp.context.lower().split())
            overlap = len(context_words & exp_words)
            if overlap > 0:
                scored.append((overlap, exp))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [exp for _, exp in scored[:limit]]

    def list_all(self) -> list[Experience]:
        return list(self._experiences.values())


# ── Knowledge Mesh Exporter ──────────────────────────────────────────────────

class KnowledgeMeshExporter:
    """Exports the full knowledge mesh to a persistent markdown file."""

    @staticmethod
    def export(memory_store: MemoryStore, knowledge_graph: KnowledgeGraph,
               experience_store: ExperienceStore,
               path: Optional[Path] = None) -> Path:
        """Export all knowledge to KNOWLEDGE_MESH.md."""
        target = path or KNOWLEDGE_MESH_PATH
        target.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "# KNOWLEDGE_MESH — Luymas AI Shared Knowledge Base\n",
            f"_Last updated: {datetime.now(timezone.utc).isoformat()}_\n",
            "## Memories\n",
        ]

        for entry in memory_store.list_all():
            lines.append(f"### {entry.key} ({entry.memory_type.value})")
            lines.append(f"- **Agent**: {entry.agent_name}")
            lines.append(f"- **Value**: {json.dumps(entry.value, default=str)[:200]}")
            lines.append(f"- **Created**: {entry.created_at.isoformat()}")
            lines.append("")

        lines.append("## Knowledge Graph\n")
        for node in knowledge_graph._nodes.values():
            lines.append(f"- **{node.label}** ({node.node_type})")
        for edge in knowledge_graph._edges:
            src = knowledge_graph._nodes.get(edge.source)
            tgt = knowledge_graph._nodes.get(edge.target)
            lines.append(f"  - {src.label if src else edge.source} "
                         f"--[{edge.relation}]--> "
                         f"{tgt.label if tgt else edge.target}")

        lines.append("\n## Experiences\n")
        for exp in experience_store.list_all():
            lines.append(f"### Project {exp.project_id}")
            lines.append(f"- **Context**: {exp.context}")
            lines.append(f"- **What Worked**: {', '.join(exp.what_worked)}")
            lines.append(f"- **What Failed**: {', '.join(exp.what_failed)}")
            lines.append(f"- **Lessons**: {', '.join(exp.lessons)}")
            lines.append("")

        target.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Exported KNOWLEDGE_MESH to %s", target)
        return target


# ── Knowledge Mesh Facade ────────────────────────────────────────────────────

class KnowledgeMesh:
    """Unified facade for the Luymas AI knowledge mesh.

    Usage::

        mesh = KnowledgeMesh()
        mesh.store("PDG", "architecture", "microservices", MemoryType.DECISION)
        mesh.add_experience("proj_1", ["fast deploy"], ["flaky tests"], "SaaS dashboard")
        results = mesh.search("architecture decisions")
        mesh.export_knowledge_mesh()
    """

    def __init__(self, persist_path: Optional[Path] = None) -> None:
        self.memory_store = MemoryStore()
        self.knowledge_graph = KnowledgeGraph()
        self.project_history = ProjectHistory()
        self.experience_store = ExperienceStore()
        self._exporter = KnowledgeMeshExporter()
        self._persist_path = persist_path or KNOWLEDGE_MESH_PATH

    def store(self, agent_name: str, key: str, value: Any,
              memory_type: MemoryType = MemoryType.FACT,
              metadata: Optional[dict] = None) -> str:
        return self.memory_store.store(agent_name, key, value, memory_type, metadata)

    def retrieve(self, agent_name: str, key: str) -> Optional[Any]:
        return self.memory_store.retrieve(agent_name, key)

    def search(self, query: str, filters: Optional[dict] = None,
               limit: int = 10) -> list[SearchResult]:
        return self.memory_store.search(query, filters, limit)

    def add_experience(self, project_id: str, what_worked: list[str],
                       what_failed: list[str], context: str = "",
                       lessons: Optional[list[str]] = None) -> str:
        return self.experience_store.add_experience(
            project_id, what_worked, what_failed, context, lessons)

    def get_relevant_experience(self, context: str, limit: int = 5) -> list[Experience]:
        return self.experience_store.get_relevant_experience(context, limit)

    def export_knowledge_mesh(self) -> Path:
        """Persist all knowledge to KNOWLEDGE_MESH.md."""
        return self._exporter.export(
            self.memory_store, self.knowledge_graph,
            self.experience_store, self._persist_path,
        )
