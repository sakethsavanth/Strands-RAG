from strands import Agent
from strands.models.bedrock import BedrockModel
import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from agents.mcp_client import regulatory_mcp
# agents/generation_agent.py

LAST_MCP_CONTEXT = None

nova = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    temperature=0.2,
    max_tokens=1200
)

generation_agent = Agent(
    model=nova,
    tools=[regulatory_mcp],
    system_prompt="""
You are a grounded RAG assistant.
Answer ONLY using the provided context.
If the answer is not in the context, say "I don't know".
"""
)

def generate_answer(query: str, context_chunks: list):
    global LAST_MCP_CONTEXT
    LAST_MCP_CONTEXT = None  # reset per query

    prompt = f"""
        Answer the question using the provided context.

        Context:
        {[c["text"] for c in context_chunks]}

        Question:
        {query}
        """

    response = generation_agent(prompt)

    # 🔑 Capture MCP context if present
    for msg in response.message.get("content", []):
        if msg.get("type") == "tool_result":
            LAST_MCP_CONTEXT = msg["content"]

    return response.message["content"][0]["text"]
