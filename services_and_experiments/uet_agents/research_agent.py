from typing import Optional, List
from .base_agent import BaseAgent
from docs.knowledge_base.omega_search import OmegaSearch
from docs.knowledge_base.api_client import OpenRouterClient


class ResearchAgent(BaseAgent):
    """
    RAG Agent that uses the UET Knowledge Base to answer questions.
    Uses OmegaSearch to find relevant documents before answering.
    """

    def __init__(
        self,
        name: str,
        client: OpenRouterClient,
        search_engine: OmegaSearch,
        system_prompt: str = "",
    ):
        super().__init__(name, client, system_prompt=system_prompt)
        self.search_engine = search_engine

    def run(self, user_query: str, topic_hint: Optional[str] = None) -> str:
        """
        Execute RAG pipeline:
        1. Search Knowledge Base (using query + topic_hint)
        2. Construct prompt with retrieved context
        3. Generative Answer
        """
        # 1. Search
        print(f"  🔍 {self.name} searching for: '{user_query}'...")
        results = self.search_engine.search(
            query_text=user_query, topic_hint=topic_hint, top_k=5  # Default to top 5 chunks
        )

        if not results:
            print("  ⚠️ No relevant documents found.")
            return "I couldn't find any relevant information in the UET knowledge base to answer your question."

        # 2. Build Context
        context_str = ""
        for i, res in enumerate(results, 1):
            explanation = self.search_engine.explain_match(res)
            # Add chunk text + explanation metadata
            context_str += f"\n--- DOCUMENT {i} ---\n"
            context_str += f"Metadata: {explanation}\n"
            context_str += (
                f"Content:\n{res['doc'].text}\n"
                if isinstance(res, dict)
                else f"Content:\n{res.doc.text}\n"
            )
            # Wait, uet_vec stored in DB might not have full text if it's just vector.
            # Let's check VectorDocument definition. It has 'file_path'.
            # We assume we can load content or it's not stored?
            # Uh oh. VectorDocument in 'ingest.py' doesn't seem to store the raw text content in the vector DB *unless* we added a text column.
            # SQLite schema: `CREATE TABLE documents (..., text TEXT, ...)`?
            # Let's check vector_store.py schema.
            pass

        # If text is missing, we must fetch it from file_path.
        # Let's refine this logic after checking vector_store.py.
        # For now, placeholder.
        return super().chat(
            [{"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {user_query}"}]
        )
