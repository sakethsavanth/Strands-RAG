import json
import sys
import os
from strands import Agent
from strands.models.bedrock import BedrockModel

# Ensure project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0",
    temperature=0.0,
    max_tokens=200
)

mcp_router_agent = Agent(
    model=model,
    system_prompt="""
Decide whether external MCP tools are REQUIRED.

Use MCP if:
- The query mentions regulations, standards, frameworks
- The query asks about BCBS, Basel, compliance, governance
- The answer is NOT directly present in the document context

Do NOT use MCP if:
- The question is purely about uploaded documents
- The answer can be directly retrieved from chunks

Return ONLY JSON:
{"use_mcp": true, "reason": "..."}
OR
{"use_mcp": false, "reason": "..."}
"""
)

def should_use_mcp(query: str):
    try:
        response = mcp_router_agent(query)

        raw = response.message["content"][0].get("text", "").strip()

        # 🔒 HARD GUARD
        if not raw:
            return _fallback("Empty MCP router response")

        # 🔍 Extract JSON safely
        start = raw.find("{")
        end = raw.rfind("}") + 1

        if start == -1 or end == -1:
            return _fallback(f"Non-JSON MCP output: {raw}")

        parsed = json.loads(raw[start:end])
        return parsed

    except Exception as e:
        return _fallback(str(e))


def _fallback(reason):
    return {
        "use_mcp": False,
        "reason": f"Fallback used: {reason}"
    }
