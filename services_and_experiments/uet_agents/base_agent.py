from typing import List, Dict, Optional, Any
import logging
from docs.knowledge_base.api_client import OpenRouterClient, CostTracker


class BaseAgent:
    """
    Base class for all UET Agents.
    Handles configuration, API client connection, and common utilities.
    """

    def __init__(
        self,
        name: str,
        client: OpenRouterClient,
        system_prompt: str = "",
        model_override: Optional[str] = None,
    ):
        self.name = name
        self.client = client
        self.system_prompt = system_prompt
        self.model_override = model_override

        # Load agent config
        self.agent_config = self.client.agents.get(name, {})
        self.model = model_override or self.agent_config.get("model")

        if not self.model:
            # Fallback if config is missing or incomplete
            self.model = "qwen/qwen3-coder-next"
            logging.warning(f"Agent '{name}' has no model in config. Defaulting to {self.model}")

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Send a chat request to the LLM.
        Automatically prepends system prompt if not present in history (optional strategy).
        For now, we assume 'messages' includes what is needed, or we prepend system prompt here.
        """
        # Prepend system message if provided and not already there
        msgs_to_send = []
        if self.system_prompt:
            msgs_to_send.append({"role": "system", "content": self.system_prompt})

        msgs_to_send.extend(messages)

        return self.client.chat(agent_id=self.name, messages=msgs_to_send, temperature=temperature)

    def run(self, user_query: str) -> str:
        """
        Simple synchronous run: User Query -> Answer.
        Override this for more complex loops (e.g. ResearchAgent).
        """
        return self.chat([{"role": "user", "content": user_query}])
