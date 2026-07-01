from typing import List, Dict, Type
import json
from .base_agent import BaseAgent


class OrchestratorAgent(BaseAgent):
    """
    Central router for the UET Multi-Agent System.
    Analyzes user intent and routes to:
    - ResearchAgent (for knowledge based queries)
    - EquationExpert (for math/equation analysis)
    - Direct response (for simple greetings/meta questions)
    """

    def __init__(
        self,
        name: str,
        client,
        research_agent: BaseAgent,
        equation_agent: BaseAgent,
        marketing_agent: BaseAgent,
    ):
        system_prompt = (
            "You are the UET Orchestrator. Your role is to route user queries to the best specialist.\n"
            "Your available agents are:\n"
            "1. ResearchAgent: Can search the UET Knowledge Base (papers, code, theory). Use for 'Find', 'What is', 'Explain', 'Search'.\n"
            "2. EquationExpert: Can analyze raw UET equations and math. Use for 'Solve', 'Calculate', 'Check equation'.\n"
            "3. MarketingAgent: Can draft and post to social media. Use for 'Tweet', 'Post', 'Draft', 'Promote', 'Moltbook'.\n"
            "4. Self: Answer simple greetings, meta-questions about the system directly.\n\n"
            "If the query requires knowledge from the database, choose ResearchAgent.\n"
            "If the query is purely mathematical verification, choose EquationExpert.\n"
            "If the query is about social media or posting, choose MarketingAgent.\n"
            "Output ONLY the name of the agent to route to: 'ResearchAgent', 'EquationExpert', 'MarketingAgent', or 'Self'."
        )
        super().__init__(name, client, system_prompt=system_prompt)
        self.research_agent = research_agent
        self.equation_agent = equation_agent
        self.marketing_agent = marketing_agent

    def run(self, user_query: str) -> str:
        # 1. Decide intent
        # Use a cheap/fast model call to classify, or just use the main Orchestrator model.
        print(f"  🧠 Orchestrator analyzing: '{user_query}'...")

        # We need a robust classification. Even a simple prompt works.
        decision = self.chat(
            [{"role": "user", "content": f"Query: {user_query}\nTarget Agent:"}], temperature=0.1
        ).strip()

        print(f"  👉 Routing to: {decision}")

        if "ResearchAgent" in decision:
            return self.research_agent.run(user_query)
        elif "EquationExpert" in decision:
            return self.equation_agent.run(user_query)
        elif "MarketingAgent" in decision:
            return self.marketing_agent.run(user_query)

        else:
            # Handle directly
            return self.chat(
                [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant for the UET project.",
                    },
                    {"role": "user", "content": user_query},
                ]
            )
