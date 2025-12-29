from strands import Agent
from strands.models.bedrock import BedrockModel
import json

rerank_model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0",
    temperature=0.0,
    max_tokens=400
)

reranker_agent = Agent(
    model=rerank_model,
    system_prompt="""
You are a reranking agent.

You MUST return ONLY valid JSON.
Do not include markdown, explanations, or extra text.

Output format:
[
  {"index": 0, "score": 0.85},
  {"index": 1, "score": 0.12}
]
"""
)

def rerank(query: str, chunks: list):
    prompt = f"""
Query:
{query}

Chunks:
{[
    {"index": i, "text": c["text"][:500]}
    for i, c in enumerate(chunks)
]}
"""

    response = reranker_agent(prompt)
    raw = response.message["content"][0]["text"]

    # --- Robust JSON extraction ---
    try:
        json_start = raw.find("[")
        json_end = raw.rfind("]") + 1
        parsed = json.loads(raw[json_start:json_end])
    except Exception as e:
        raise ValueError(
            f"Reranker returned invalid JSON.\n\nRAW OUTPUT:\n{raw}"
        ) from e

    # ✅ STEP 1: Initialize default score for ALL chunks
    for c in chunks:
        c["score"] = 0.0

    # ✅ STEP 2: Apply reranker scores where provided
    for item in parsed:
        idx = item["index"]
        score = item["score"]
        if 0 <= idx < len(chunks):
            chunks[idx]["score"] = score

    # ✅ STEP 3: Sort safely
    return sorted(chunks, key=lambda x: x["score"], reverse=True)
