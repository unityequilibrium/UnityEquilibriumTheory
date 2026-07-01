# UET Agents Package

# Standalone components (no external dependencies beyond requirements.txt)
from .semantic_engine import UETSemanticEngine
from .executive_router import ExecutiveRouter
from .memory_store import (
    WorkingMemoryStore,
    EpisodicMemoryStore,
    SemanticMemoryStore,
    ProceduralMemoryStore,
)

# Components that depend on docs.knowledge_base (optional)
try:
    from .base_agent import BaseAgent
    from .research_agent import ResearchAgent
    from .orchestrator import OrchestratorAgent
except ImportError:
    pass
