from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class WorkingMemorySnapshot:
    prompt: str
    doc_context_present: bool
    active_source_count: int
    task_type: str
    updated_at: str


@dataclass
class EpisodeRecord:
    prompt: str
    response: str
    task_type: str
    equilibrium_found: bool
    resonance_score: float
    work_computed: float
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticEvidenceBundle:
    prompt: str
    search_space: List[Dict[str, Any]]
    persistent_chunk_count: int
    temporary_chunk_count: int
    total_chunk_count: int
    task_type: str
    best_chunk_preview: Optional[str]
    created_at: str


class WorkingMemoryStore:
    def __init__(self):
        self._sessions: Dict[str, WorkingMemorySnapshot] = {}

    def update(
        self,
        session_id: str,
        prompt: str,
        doc_context: Optional[str],
        task_type: str,
    ) -> WorkingMemorySnapshot:
        active_source_count = 0
        if doc_context:
            active_source_count = len([line for line in doc_context.split("\n") if line.strip()])

        snapshot = WorkingMemorySnapshot(
            prompt=prompt,
            doc_context_present=bool(doc_context and doc_context.strip()),
            active_source_count=active_source_count,
            task_type=task_type,
            updated_at=datetime.utcnow().isoformat(),
        )
        self._sessions[session_id] = snapshot
        return snapshot

    def get(self, session_id: str) -> Optional[WorkingMemorySnapshot]:
        return self._sessions.get(session_id)

    def debug_snapshot(self, session_id: str) -> Dict[str, Any]:
        snapshot = self.get(session_id)
        if snapshot is None:
            return {}
        return {
            "prompt": snapshot.prompt,
            "doc_context_present": snapshot.doc_context_present,
            "active_source_count": snapshot.active_source_count,
            "task_type": snapshot.task_type,
            "updated_at": snapshot.updated_at,
        }


class EpisodicMemoryStore:
    def __init__(self, max_episodes_per_session: int = 25):
        self.max_episodes_per_session = max_episodes_per_session
        self._episodes: Dict[str, List[EpisodeRecord]] = {}

    def append(self, session_id: str, record: EpisodeRecord) -> None:
        history = self._episodes.setdefault(session_id, [])
        history.append(record)
        if len(history) > self.max_episodes_per_session:
            del history[0 : len(history) - self.max_episodes_per_session]

    def recent(self, session_id: str, limit: int = 3) -> List[EpisodeRecord]:
        return self._episodes.get(session_id, [])[-limit:]

    def debug_recent(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        return [
            {
                "prompt": record.prompt,
                "response": record.response,
                "task_type": record.task_type,
                "equilibrium_found": record.equilibrium_found,
                "resonance_score": record.resonance_score,
                "work_computed": record.work_computed,
                "created_at": record.created_at,
                "metadata": record.metadata,
            }
            for record in self.recent(session_id, limit)
        ]


class SemanticMemoryStore:
    def __init__(self):
        self._last_bundle_by_session: Dict[str, SemanticEvidenceBundle] = {}

    def build_evidence_bundle(
        self,
        session_id: str,
        prompt: str,
        task_type: str,
        persistent_chunks: List[Dict[str, Any]],
        temporary_chunks: List[Dict[str, Any]],
    ) -> SemanticEvidenceBundle:
        search_space = persistent_chunks + temporary_chunks
        bundle = SemanticEvidenceBundle(
            prompt=prompt,
            search_space=search_space,
            persistent_chunk_count=len(persistent_chunks),
            temporary_chunk_count=len(temporary_chunks),
            total_chunk_count=len(search_space),
            task_type=task_type,
            best_chunk_preview=search_space[0]["text"][:160] if search_space else None,
            created_at=datetime.utcnow().isoformat(),
        )
        self._last_bundle_by_session[session_id] = bundle
        return bundle

    def debug_bundle(self, session_id: str) -> Dict[str, Any]:
        bundle = self._last_bundle_by_session.get(session_id)
        if bundle is None:
            return {}
        return {
            "prompt": bundle.prompt,
            "task_type": bundle.task_type,
            "persistent_chunk_count": bundle.persistent_chunk_count,
            "temporary_chunk_count": bundle.temporary_chunk_count,
            "total_chunk_count": bundle.total_chunk_count,
            "best_chunk_preview": bundle.best_chunk_preview,
            "created_at": bundle.created_at,
        }


class ProceduralMemoryStore:
    def __init__(self):
        self._policies: Dict[str, str] = {
            "chat": "Use semantic retrieval first, then compose a grounded response.",
            "ingest": "Normalize source text, add it to semantic memory, and persist the new state.",
            "fallback": "If no evidence is strong enough, return a grounded insufficiency message instead of hallucinating.",
        }

    def get(self, key: str) -> str:
        return self._policies.get(key, "")

    def all(self) -> Dict[str, str]:
        return dict(self._policies)
