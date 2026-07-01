from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from .memory_store import EpisodeRecord, EpisodicMemoryStore, ProceduralMemoryStore, SemanticMemoryStore, WorkingMemoryStore
from .semantic_engine import UETSemanticEngine


@dataclass
class ExecutiveResult:
    response: str
    equilibrium_data: Dict[str, Any]
    work_computed: float
    task_type: str
    session_id: str


class ExecutiveRouter:
    def __init__(self, semantic_engine: UETSemanticEngine):
        self.semantic_engine = semantic_engine
        self.working_memory = WorkingMemoryStore()
        self.episodic_memory = EpisodicMemoryStore()
        self.semantic_memory = SemanticMemoryStore()
        self.procedural_memory = ProceduralMemoryStore()

    def ingest_document(
        self,
        doc_id: str,
        text: str,
        source_type: str = "text",
        project_scope: Optional[str] = None,
        doc_version: Optional[str] = None,
        tags: Optional[list[str]] = None,
        ingest_mode: str = "manual",
    ) -> int:
        return self.semantic_engine.ingest_document(
            doc_id=doc_id,
            text=text,
            source_type=source_type,
            project_scope=project_scope,
            doc_version=doc_version,
            tags=tags,
            ingest_mode=ingest_mode,
        )

    def handle_chat(
        self,
        prompt: str,
        doc_context: Optional[str] = None,
        session_id: Optional[str] = None,
        project_scope: Optional[str] = None,
        source_tags: Optional[list[str]] = None,
    ) -> ExecutiveResult:
        resolved_session_id = session_id or self._make_session_id()
        task_type = self._classify_task(prompt)

        self.working_memory.update(
            session_id=resolved_session_id,
            prompt=prompt,
            doc_context=doc_context,
            task_type=task_type,
        )

        evidence_bundle = self.semantic_memory.build_evidence_bundle(
            session_id=resolved_session_id,
            prompt=prompt,
            task_type=task_type,
            persistent_chunks=self.semantic_engine.knowledge_chunks,
            temporary_chunks=self.semantic_engine.build_temp_chunks(doc_context),
        )

        equilibrium_data = self._execute_task_path(
            task_type=task_type,
            prompt=prompt,
            evidence_bundle=evidence_bundle,
        )
        recent_episodes = self.episodic_memory.recent(resolved_session_id)
        response = self.semantic_engine.generate_response(
            prompt=prompt,
            equilibrium_data=equilibrium_data,
            task_type=task_type,
            recent_episodes=[self._episode_to_dict(record) for record in recent_episodes],
            procedure_hint=self.procedural_memory.get(task_type),
        )

        self.episodic_memory.append(
            resolved_session_id,
            EpisodeRecord(
                prompt=prompt,
                response=response,
                task_type=task_type,
                equilibrium_found=bool(equilibrium_data.get("equilibrium_found", False)),
                resonance_score=float(equilibrium_data.get("resonance_score", 0.0)),
                work_computed=float(equilibrium_data.get("work_computed", 0.0)),
                created_at=datetime.utcnow().isoformat(),
                metadata={
                    "best_chunk_id": self._best_chunk_id(equilibrium_data),
                    "doc_context_present": bool(doc_context and doc_context.strip()),
                    "project_scope": project_scope,
                    "source_tags": source_tags or [],
                    "semantic_total_chunk_count": evidence_bundle.total_chunk_count,
                    "semantic_persistent_chunk_count": evidence_bundle.persistent_chunk_count,
                    "semantic_temporary_chunk_count": evidence_bundle.temporary_chunk_count,
                },
            ),
        )

        return ExecutiveResult(
            response=response,
            equilibrium_data=equilibrium_data,
            work_computed=float(equilibrium_data.get("work_computed", 0.0)),
            task_type=task_type,
            session_id=resolved_session_id,
        )

    def _classify_task(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        calculation_signals = [
            "equation",
            "calculate",
            "solve",
            "formula",
            "สมการ",
            "คำนวณ",
            "พิสูจน์",
            "หาค่า",
        ]
        if any(signal in prompt_lower for signal in calculation_signals):
            return "calculation"
        return "chat"

    def _execute_task_path(
        self,
        task_type: str,
        prompt: str,
        evidence_bundle,
    ) -> Dict[str, Any]:
        equilibrium_data = self.semantic_engine.calculate_equilibrium_path_from_search_space(
            prompt=prompt,
            search_space=evidence_bundle.search_space,
        )

        if task_type == "calculation":
            equilibrium_data["calculation_mode"] = True
            equilibrium_data["path_strategy"] = "calculation"
            equilibrium_data["work_computed"] = equilibrium_data["work_computed"] * 1.25
            return equilibrium_data

        equilibrium_data["calculation_mode"] = False
        equilibrium_data["path_strategy"] = "chat"
        return equilibrium_data

    def _make_session_id(self) -> str:
        return f"session-{uuid4()}"

    def _best_chunk_id(self, equilibrium_data: Dict[str, Any]) -> Optional[str]:
        best_chunk = equilibrium_data.get("best_chunk")
        if isinstance(best_chunk, dict):
            return best_chunk.get("chunk_id")
        return None

    def _episode_to_dict(self, record: EpisodeRecord) -> Dict[str, Any]:
        return {
            "prompt": record.prompt,
            "response": record.response,
            "task_type": record.task_type,
            "equilibrium_found": record.equilibrium_found,
            "resonance_score": record.resonance_score,
            "work_computed": record.work_computed,
            "created_at": record.created_at,
            "metadata": record.metadata,
        }

    def debug_session(self, session_id: str) -> Dict[str, Any]:
        return {
            "session_id": session_id,
            "working_memory": self.working_memory.debug_snapshot(session_id),
            "recent_episodes": self.episodic_memory.debug_recent(session_id),
            "semantic_bundle": self.semantic_memory.debug_bundle(session_id),
        }
