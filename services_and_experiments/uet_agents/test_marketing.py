import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to path
# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from uet_agents.marketing_agent import MarketingAgent


def test_marketing_agent():
    print("🧪 Testing MarketingAgent...")

    # Mock Client
    mock_client = MagicMock()
    # Mock chat response to simulate tool call
    mock_client.chat.side_effect = [
        # Turn 1: Thoughts -> Tool Call
        'I should post this to Twitter.\n```json\n{\n  "tool": "post_tweet",\n  "arguments": {\n    "content": "Exciting news! UET v0.9.0 is here. #AIPhysics"\n  }\n}\n```',
        # Turn 2: Final response
        "I have posted the update to Twitter.",
    ]

    agent = MarketingAgent("marketing", mock_client)

    print("  👉 Sending query: 'Tweet about update'")
    response = agent.run("Tweet about update")

    print(f"  📝 Agent Response: {response}")

    # Verify tool call was attempted (by checking if _post_tweet printed)
    # Since we can't easily capture stdout of the method without more mocking,
    # we relies on the fact that if it parsed correctly, it calls the method.
    # We can inspect the history.

    print("  🔍 Inspecting history for tool execution...")
    tool_output_found = False
    for msg in agent.history:
        if "TOOL_OUTPUT" in msg.get("content", ""):
            print(f"    ✅ Tool Output found: {msg['content']}")
            tool_output_found = True

    if tool_output_found:
        print("✅ TEST PASSED: MarketingAgent executed tool loop.")
    else:
        print("❌ TEST FAILED: No tool output in history.")


if __name__ == "__main__":
    test_marketing_agent()
