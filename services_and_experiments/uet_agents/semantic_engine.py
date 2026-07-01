import re
import math
import json
import os
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any, Optional
from .response_composer import UETResponseComposer

class UETSemanticEngine:
    def __init__(self, order: int = 3, state_file: str = "uet_knowledge_state.json"):
        self.order = order
        self.state_file = state_file
        # The Semantic Manifold (Graph of connections)
        self.field = defaultdict(lambda: defaultdict(float))
        self.vocab = set()
        self.knowledge_chunks = []
        self.response_composer = UETResponseComposer()
        self.load_state()

    def load_state(self):
        """Load persistent knowledge state if it exists"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.knowledge_chunks = data.get("chunks", [])
                    for chunk in self.knowledge_chunks:
                        chunk.setdefault("metadata", {})
                    self.vocab = set(data.get("vocab", []))

                    # Reconstruct field (N-grams)
                    field_data = data.get("field", {})
                    for ctx_str, targets in field_data.items():
                        ctx = tuple(ctx_str.split("|||")) if ctx_str else ()
                        for target, val in targets.items():
                            self.field[ctx][target] = val

                print(f"Loaded {len(self.knowledge_chunks)} chunks from {self.state_file}")
            except Exception as e:
                print(f"Error loading state: {e}")

    def save_state(self):
        """Save knowledge state to disk"""
        # Convert tuple keys to strings for JSON
        field_serializable = {}
        for ctx, targets in self.field.items():
            ctx_str = "|||".join(ctx) if ctx else ""
            field_serializable[ctx_str] = dict(targets)

        data = {
            "chunks": [
                {
                    "doc_id": c["doc_id"],
                    "chunk_id": c["chunk_id"],
                    "text": c["text"],
                    "tokens": list(c["tokens"]), # Set to List
                    "vector_magnitude": c["vector_magnitude"],
                    "metadata": c.get("metadata", {})
                }
                for c in self.knowledge_chunks
            ],
            "vocab": list(self.vocab),
            "field": field_serializable
        }
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def tokenize(self, text: str) -> List[str]:
        """Normalize and tokenize text, preserving Thai/English structure."""
        text = re.sub(r"\s+", " ", text.lower())
        tokens = text.split(" ")
        return [t for t in tokens if t.strip()]

    def build_temp_chunks(self, doc_context: Optional[str]) -> List[Dict[str, Any]]:
        temp_chunks = []
        if not doc_context:
            return temp_chunks

        raw_paragraphs = doc_context.split("\n")
        for i, p in enumerate(raw_paragraphs):
            p = p.strip()
            if len(p) > 30:
                p_tokens = set(self.tokenize(p))
                temp_chunks.append({
                    "doc_id": "temp",
                    "chunk_id": f"temp_p{i}",
                    "text": p,
                    "tokens": p_tokens,
                    "vector_magnitude": len(p_tokens),
                    "metadata": {
                        "source_type": "runtime_context",
                        "project_scope": "runtime_session",
                        "doc_version": None,
                        "tags": ["runtime", "context"],
                        "ingest_mode": "ephemeral",
                        "paragraph_index": i,
                        "char_count": len(p),
                        "created_at": datetime.utcnow().isoformat(),
                    }
                })
        return temp_chunks

    def build_search_space(self, doc_context: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.knowledge_chunks + self.build_temp_chunks(doc_context)

    def calculate_equilibrium_path_from_search_space(
        self,
        prompt: str,
        search_space: List[Dict[str, Any]],
        top_k: int = 3,
    ) -> Dict[str, Any]:
        prompt_tokens = set(self.tokenize(prompt.lower()))

        scored = []
        for chunk in search_space:
            chunk_tokens = set(chunk["tokens"]) if isinstance(chunk["tokens"], list) else chunk["tokens"]

            overlap = len(prompt_tokens & chunk_tokens)
            if overlap > 0:
                score = overlap / (math.log(chunk["vector_magnitude"] + 1) + 1)
                scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_chunks = scored[:top_k]

        best_score = top_chunks[0][0] if top_chunks else 0.0
        best_chunk = top_chunks[0][1] if top_chunks else None

        work_done = len(search_space) * len(prompt_tokens) * 0.001

        return {
            "best_chunk": best_chunk,
            "top_chunks": [c for _, c in top_chunks],
            "resonance_score": best_score,
            "equilibrium_found": best_score > 0.05,
            "work_computed": work_done
        }

    def ingest_document(
        self,
        doc_id: str,
        text: str,
        source_type: str = "text",
        project_scope: Optional[str] = None,
        doc_version: Optional[str] = None,
        tags: Optional[List[str]] = None,
        ingest_mode: str = "manual",
    ):
        """Train the manifold on a new document."""
        text = re.sub(r"[\r\n]+", "\n", text)
        tokens = self.tokenize(text)
        self.vocab.update(tokens)

        # 1. Build N-Gram Lattice (The C parameter - Connection)
        for i in range(len(tokens) - self.order):
            context = tuple(tokens[i : i + self.order])
            target = tokens[i + self.order]
            self.field[context][target] += 1.0

        # 2. Build Resonance Index (The I parameter - Information chunks)
        raw_paragraphs = text.split("\n")
        new_chunks = 0
        for i, p in enumerate(raw_paragraphs):
            p = p.strip()
            if len(p) > 30:  # Ignore noise
                p_tokens = set(self.tokenize(p))
                self.knowledge_chunks.append({
                    "doc_id": doc_id,
                    "chunk_id": f"{doc_id}_p{i}_{len(self.knowledge_chunks)}",
                    "text": p,
                    "tokens": p_tokens,
                    "vector_magnitude": len(p_tokens),
                    "metadata": {
                        "source_type": source_type,
                        "project_scope": project_scope,
                        "doc_version": doc_version,
                        "tags": tags or [],
                        "ingest_mode": ingest_mode,
                        "paragraph_index": i,
                        "char_count": len(p),
                        "created_at": datetime.utcnow().isoformat(),
                    }
                })
                new_chunks += 1

        self.save_state()
        return new_chunks

    def calculate_equilibrium_path(self, prompt: str, doc_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Instead of just generation, this calculates the "Path of Least Resistance"
        This mimics solving the UET equation.
        """
        search_space = self.build_search_space(doc_context)
        return self.calculate_equilibrium_path_from_search_space(prompt, search_space)

    def generate_response(
        self,
        prompt: str,
        equilibrium_data: Dict[str, Any],
        task_type: str = "chat",
        recent_episodes: Optional[List[Dict[str, Any]]] = None,
        procedure_hint: str = "",
    ) -> str:
        return self.response_composer.compose(
            prompt=prompt,
            equilibrium_data=equilibrium_data,
            task_type=task_type,
            recent_episodes=recent_episodes,
            procedure_hint=procedure_hint,
        )
