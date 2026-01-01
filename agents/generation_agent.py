from strands import Agent
from strands.models.bedrock import BedrockModel

# ---------------- MODEL ----------------
model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    temperature=0.2,
    max_tokens=1200
)

# ---------------- AGENT ----------------
agent = Agent(
    model=model,
    system_prompt="""
You are an intelligent assistant in an Agentic RAG system.

Rules:
- Follow MCP instructions strictly.
- Use document context when provided.
- NEVER hallucinate.
- If context is insufficient, say "I don't know".
"""
)

# ---------------- GENERATION ----------------
def generate_answer(query: str, chunks: list, instruction: str) -> str:
    """
    Generates the final answer.
    MCP is NOT called here.
    MCP instructions are passed in as text.
    """

    context = "\n\n".join(c["text"] for c in chunks)

    prompt = f"""
Instruction from MCP:
{instruction}

Context:
{context}

Question:
{query}
"""

    response = agent(prompt)

    return response.message["content"][0]["text"]
