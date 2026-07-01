from typing import List, Dict, Any, Optional
import json
from .base_agent import BaseAgent

MARKETING_SYSTEM_PROMPT = """
You are the **MarketingAgent** for Unity Equilibrium Theory (UET).
Your goal is to increase awareness by creating scientifically accurate content.

## Identity
- Project: UET v0.9.0 (The Thermodynamics of Ethics)
- Tagline: "Ω = C · I" (Balance = Connection × Isolation)
- GitHub: https://github.com/unityequilibrium/UnityEquilibriumTheory

## Platforms
1. **Twitter/X**: Short, threads, hashtags #UET #AIPhysics.
2. **Reddit**: Deep discussions (r/MachineLearning).
3. **Moltbook**: AI-to-AI protocol (JSON payload).

## Tool Calling Strict Format
To use a tool, you MUST output a JSON block like this:
```json
{
  "tool": "post_moltbook",
  "arguments": {
    "content": "..."
  }
}
```
Supported Tools:
- `post_moltbook(content: str)` -> Returns success message
- `post_tweet(content: str)` -> Returns success message
- `post_reddit(subreddit: str, title: str, body: str)` -> Returns success message

Output ONLY the JSON block when calling a tool.
If asking for user approval, just speak normally.
"""


class MarketingAgent(BaseAgent):
    """
    Agent responsible for social media marketing.
    Directly handles tool execution loop (ReAct pattern).
    """

    def __init__(self, name: str, client):
        super().__init__(name, client, system_prompt=MARKETING_SYSTEM_PROMPT)
        # Register naive tools
        self.tools = {
            "post_moltbook": self._post_to_moltbook,
            "post_tweet": self._post_tweet,
            "post_reddit": self._post_reddit,
        }
        self.history = []

    def _post_to_moltbook(self, content: str) -> str:
        try:
            # Simulate posting
            payload = {"agent": "NON_UET", "verification": "splash-BJ6W", "content": content}
            # In real system: requests.post(...)
            print(f"🦞 [Moltbook] Payload: {json.dumps(payload, indent=2)}")
            return "✅ Success: Posted to Moltbook."
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def _post_tweet(self, content: str) -> str:
        print(f"🐦 [Twitter] {content}")
        return "✅ Success: Tweet posted."

    def _post_reddit(self, subreddit: str, title: str, body: str) -> str:
        print(f"👽 [Reddit] r/{subreddit}: {title}")
        return "✅ Success: Reddit post created."

    def _parse_tool_call(self, text: str) -> Optional[Dict]:
        """Extract JSON tool call from markdown block or raw text."""
        try:
            if "```json" in text:
                start = text.index("```json") + 7
                end = text.find("```", start)
                if end != -1:
                    return json.loads(text[start:end].strip())
            if text.strip().startswith("{") and '"tool"' in text:
                return json.loads(text.strip())
        except Exception:
            pass
        return None

    def run(self, user_query: str) -> str:
        print(f"  📢 MarketingAgent processing: '{user_query}'...")
        self.history.append({"role": "user", "content": user_query})

        MAX_TURNS = 5
        for _ in range(MAX_TURNS):
            # 1. Get model response
            response = self.chat(self.history)

            # 2. Check for tool call
            tool_data = self._parse_tool_call(response)

            if tool_data:
                tool_name = tool_data.get("tool")
                print(f"  🛠️  Tool Call: {tool_name}")

                # Execute tool
                if tool_name in self.tools:
                    args = tool_data.get("arguments", {})
                    try:
                        if tool_name == "post_moltbook":
                            result = self._post_to_moltbook(args.get("content"))
                        elif tool_name == "post_tweet":
                            result = self._post_tweet(args.get("content"))
                        elif tool_name == "post_reddit":
                            result = self._post_reddit(
                                args.get("subreddit"), args.get("title"), args.get("body")
                            )
                        else:
                            result = f"Error: {tool_name} not implemented."
                    except Exception as e:
                        result = f"Error executing {tool_name}: {e}"
                else:
                    result = f"Error: Tool {tool_name} not found."

                # Add to history
                self.history.append({"role": "assistant", "content": response})
                self.history.append({"role": "user", "content": f"TOOL_OUTPUT: {result}"})

                # Loop continues for model to see result and respond
            else:
                # No tool call, just return the text
                self.history.append({"role": "assistant", "content": response})
                return response

        return "Error: Max turns exceeded."
