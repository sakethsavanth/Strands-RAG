import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from rag.retriever import VectorRetriever
from agents.reranker_agent import rerank
from agents.generation_agent import generate_answer
from rag.citation_scoring import compute_citation_confidence
from agents.generation_agent import LAST_MCP_CONTEXT

retriever = VectorRetriever()

def answer_query(query: str, top_k: int = 3):
    # 1️⃣ Retrieval Agent
    retrieved_chunks = retriever.retrieve(query, k=10)

    # 2️⃣ Reranking Agent
    reranked_chunks = rerank(query, retrieved_chunks)

    # 3️⃣ Select top-k AFTER reranking (🔥 configurable)
    top_chunks = reranked_chunks[:top_k]

    # 4️⃣ Generation Agent
    answer = generate_answer(query, top_chunks)
    mcp_used = "MCP" in answer or "external" in answer.lower()

    # 5️⃣ Citation confidence
    confidence = compute_citation_confidence(top_chunks)
    for c in top_chunks:
        print("SOURCE:", c["source"])
        print(c["text"][:300])
        print("-" * 40)


    # Sources (for tests + UI)
    sources = list({c["source"] for c in top_chunks})

    return {
        "query": query,
        "retrieved_chunks": retrieved_chunks,
        "reranked_chunks": reranked_chunks,
        "top_chunks": top_chunks,
        "answer": answer,
        "mcp_used": bool(LAST_MCP_CONTEXT),
        "mcp_context": LAST_MCP_CONTEXT,
        "confidence": confidence,
        "sources": sources,
        "top_k": top_k
    }
