from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import datetime

app = FastAPI(title="Advanced RAG Control Plane (FastMCP)")

# -------------------------------------------------
# Models
# -------------------------------------------------
class QueryRequest(BaseModel):
    query: str

class NegotiationRequest(BaseModel):
    agent_proposal: str
    strict_grounding: bool

class ValidationRequest(BaseModel):
    answer: str
    strict_grounding: bool

# -------------------------------------------------
# 1️⃣ QUERY CLASSIFIER & ROUTER
# -------------------------------------------------
@app.post("/classify")
def classify_query(req: QueryRequest):
    q = req.query.lower()

    if any(k in q for k in ["bcbs", "basel", "regulation", "compliance"]):
        return {
            "query_type": "regulatory",
            "strict_grounding": True,
            "allowed_agents": ["generation"]
        }

    if any(k in q for k in ["explain", "what is", "describe"]):
        return {
            "query_type": "document_grounded",
            "strict_grounding": False,
            "allowed_agents": ["retrieval", "generation"]
        }

    return {
        "query_type": "general",
        "strict_grounding": False,
        "allowed_agents": ["generation"]
    }

# -------------------------------------------------
# 2️⃣ RETRIEVAL STRATEGY CONTROLLER
# -------------------------------------------------
@app.post("/retrieval_strategy")
def retrieval_strategy(classification: Dict):
    if classification["query_type"] == "regulatory":
        return {
            "top_k": 0,
            "chunking": [],
            "rerank": False
        }

    if classification["query_type"] == "document_grounded":
        return {
            "top_k": 6,
            "chunking": ["semantic", "paragraph", "hierarchical"],
            "rerank": True
        }

    return {
        "top_k": 3,
        "chunking": ["semantic"],
        "rerank": False
    }

# -------------------------------------------------
# 3️⃣ AGENT ↔ MCP NEGOTIATION
# -------------------------------------------------
@app.post("/negotiate")
def negotiate(req: NegotiationRequest):
    if req.strict_grounding:
        return {
            "approved": True,
            "instruction": "Answer ONLY from provided documents. Say 'I don't know' if unsure."
        }

    return {
        "approved": True,
        "instruction": "You may answer freely but prefer document grounding."
    }

# -------------------------------------------------
# 4️⃣ ANSWER VALIDATOR / POLICY CHECKER
# -------------------------------------------------
@app.post("/validate")
def validate_answer(req: ValidationRequest):
    if req.strict_grounding and "I don't know" not in req.answer and len(req.answer) < 40:
        return {
            "approved": False,
            "reason": "Answer too weak for regulatory question"
        }

    return {
        "approved": True,
        "reason": "Answer approved"
    }

# -------------------------------------------------
# 5️⃣ SYSTEM NARRATOR (FOR UI)
# -------------------------------------------------
@app.post("/narrate")
def narrate_system(data: Dict):
    return {
        "narration": (
            f"Query classified as '{data['classification']['query_type']}'. "
            f"Retrieval used top_k={data['strategy']['top_k']}. "
            f"Strict grounding={data['classification']['strict_grounding']}. "
            f"Validation result={data['validation']['reason']}."
        ),
        "timestamp": str(datetime.datetime.now())
    }
