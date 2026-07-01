import sys
from pathlib import Path

# Add project root to path
# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from docs.knowledge_base.config import CONFIG
from docs.knowledge_base.api_client import OpenRouterClient, CostTracker
from docs.knowledge_base.vector_store import VectorStore
from docs.knowledge_base.tensorizer import UetTensorizer
from docs.knowledge_base.omega_search import OmegaSearch
from uet_agents.base_agent import BaseAgent
from uet_agents.research_agent import ResearchAgent
from uet_agents.marketing_agent import MarketingAgent
from uet_agents.orchestrator import OrchestratorAgent


def main():
    print("=" * 60)
    print("  UET MULTI-AGENT SYSTEM (v0.9.0)")
    print("  Initializing components...")
    print("=" * 60)

    # 1. Load Config & Client
    client_config = CONFIG["openrouter"]
    keys = client_config.get("keys", {})
    cost_tracker = CostTracker(Path(CONFIG["cost_tracking"]["log_file"]))

    api_client = OpenRouterClient(
        base_url=client_config["base_url"],
        keys=keys,
        agents=CONFIG["agents"],
        cost_tracker=cost_tracker,
    )
    print("  ✅ API Client & Cost Tracker ready.")

    # 2. Load Knowledge Base
    db_path = Path(CONFIG["vector_db"]["path"])
    store = VectorStore(db_path)
    tensorizer = UetTensorizer(grid_size=CONFIG["tensorizer"]["grid_size"])
    search_engine = OmegaSearch(store, tensorizer)
    print(f"  ✅ Knowledge Base loaded ({store.count()} docs).")

    # 3. Initialize Agents
    # Research Agent
    researcher = ResearchAgent(
        name="web_research",  # Mapping to config agent name, maybe "web_research" or "local_data"?
        # config.toml has "local_data" for "Searches local research data". Let's use that.
        # But wait, local_data uses glm-4.7-flash.
        # Let's map ResearchAgent to "local_data" in config.
        client=api_client,
        search_engine=search_engine,
        # system_prompt passed in constructor or default
    )
    # Re-map name to match config key strictly
    researcher.name = "local_data"

    # Equation Expert
    equation_expert = BaseAgent(
        name="equation_expert",
        client=api_client,
        system_prompt="You are an expert in UET (Unified Energy Theory) mathematics. Analyze equations for dimensional consistency, symmetry, and physical validity.",
    )

    # Marketing Agent
    marketing_agent = MarketingAgent(
        name="marketing",
        client=api_client,
    )

    # Orchestrator
    orchestrator = OrchestratorAgent(
        name="orchestrator",
        client=api_client,
        research_agent=researcher,
        equation_agent=equation_expert,
        marketing_agent=marketing_agent,
    )
    print(
        "  ✅ Agents initialized: Orchestrator, Researcher (local_data), EquationExpert, MarketingAgent."
    )
    print("-" * 60)
    print("  Type your query below (or 'exit' to quit).")

    # 4. Interactive Loop
    while True:
        try:
            print("\n>> ", end="")
            query = input().strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit"):
                break

            # Run Orchestrator
            response = orchestrator.run(query)
            print(f"\nUET Agent: {response}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

    print("\nExiting. Cost report available via `cost_dashboard`.")


if __name__ == "__main__":
    main()
