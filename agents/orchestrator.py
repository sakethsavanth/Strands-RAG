from rag.retriever import VectorRetriever
from agents.generation_agent import generate_answer
from agents.confidence_agent import compute_confidence
from agents.reranker_agent import rerank
from agents.mcp_client import mcp_post

retriever = VectorRetriever()

def answer_query(query: str):
    trace = []
    agent_events = []

    # ---------------- MCP CLASSIFICATION (LOGICAL) ----------------
    classification = mcp_post("/classify", {"query": query})
    trace.append(f"MCP classified query as {classification['query_type']}")

    agent_events.append({
        "agent": "MCP-Classifier",
        "type": "logical",
        "reason": "Determine intent & governance mode",
        "input": query,
        "output": classification,
        "next_agent": "RetrievalAgent"
    })

    # ---------------- MCP RETRIEVAL STRATEGY (LOGICAL) ----------------
    strategy = mcp_post("/retrieval_strategy", classification)
    trace.append(f"MCP retrieval strategy: {strategy}")

    agent_events.append({
        "agent": "MCP-Router",
        "type": "logical",
        "reason": "Select chunking & retrieval strategy",
        "input": classification,
        "output": strategy,
        "next_agent": "RetrievalAgent"
    })

    # ---------------- RETRIEVAL AGENT (RUNTIME) ----------------
    chunks = []
    if strategy["top_k"] > 0:
        chunks = retriever.retrieve(query, k=strategy["top_k"])
        trace.append(f"Retrieved {len(chunks)} chunks")

        agent_events.append({
            "agent": "RetrievalAgent",
            "type": "runtime",
            "reason": "Fetch relevant chunks from vector store",
            "input": query,
            "output": f"{len(chunks)} chunks",
            "next_agent": "RerankerAgent"
        })

        # ---------------- RERANKER AGENT (RUNTIME) ----------------
        chunks = rerank(query, chunks)

        agent_events.append({
            "agent": "RerankerAgent",
            "type": "runtime",
            "reason": "Reorder chunks by semantic relevance",
            "input": f"{len(chunks)} chunks",
            "output": "Chunks reranked with relevance scores",
            "next_agent": "GenerationAgent"
        })

    # ---------------- MCP NEGOTIATION (LOGICAL) ----------------
    negotiation = mcp_post(
        "/negotiate",
        {
            "agent_proposal": "I want to generate the answer",
            "strict_grounding": classification["strict_grounding"]
        }
    )

    trace.append("Agent negotiated constraints with MCP")

    agent_events.append({
        "agent": "MCP-Negotiator",
        "type": "logical",
        "reason": "Apply grounding & safety constraints",
        "input": classification,
        "output": negotiation,
        "next_agent": "GenerationAgent"
    })

    # ---------------- GENERATION AGENT (RUNTIME) ----------------
    answer = generate_answer(
        query=query,
        chunks=chunks,
        instruction=negotiation["instruction"]
    )

    agent_events.append({
        "agent": "GenerationAgent",
        "type": "runtime",
        "reason": "Synthesize final answer from context",
        "input": f"{len(chunks)} chunks + MCP instruction",
        "output": answer[:300] + ("..." if len(answer) > 300 else ""),
        "next_agent": "MCP-Validator"
    })

    # ---------------- MCP VALIDATION (LOGICAL) ----------------
    validation = mcp_post(
        "/validate",
        {
            "answer": answer,
            "strict_grounding": classification["strict_grounding"]
        }
    )

    trace.append(f"MCP validation: {validation}")

    agent_events.append({
        "agent": "MCP-Validator",
        "type": "logical",
        "reason": "Policy & compliance validation",
        "input": answer[:200],
        "output": validation,
        "next_agent": "ConfidenceAgent"
    })

    # ---------------- CONFIDENCE AGENT (RUNTIME) ----------------
    confidence = compute_confidence(chunks, validation)

    agent_events.append({
        "agent": "ConfidenceAgent",
        "type": "runtime",
        "reason": "Estimate reliability of answer",
        "input": f"{len(chunks)} chunks + validation",
        "output": f"confidence={confidence}",
        "next_agent": None
    })

    # ---------------- MCP NARRATION (LOGICAL) ----------------
    narration = mcp_post(
        "/narrate",
        {
            "classification": classification,
            "strategy": strategy,
            "validation": validation
        }
    )

    return {
        "answer": answer,
        "trace": trace,
        "agent_events": agent_events,
        "chunks": chunks,
        "mcp": {
            "classification": classification,
            "strategy": strategy,
            "negotiation": negotiation,
            "validation": validation,
            "narration": narration
        },
        "confidence": confidence
    }
