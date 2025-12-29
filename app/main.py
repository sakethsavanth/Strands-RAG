import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

import streamlit as st
from agents.orchestrator import answer_query

import time
from mcp_server.launcher import start_mcp_server

if "mcp_process" not in st.session_state:
    st.session_state.mcp_process = start_mcp_server()
    time.sleep(1)  # allow MCP server to boot


# ---------------- UI CONFIG ----------------
st.set_page_config(
    page_title="Agentic RAG Explorer",
    layout="wide"
)

st.title("🧠 Agentic RAG System (Strands + Titan + Nova)")
st.caption("Visualizing how multiple agents collaborate to answer your question")
st.sidebar.header("⚙️ RAG Controls")

top_k = st.sidebar.slider(
    "Number of chunks used for answer generation",
    min_value=1,
    max_value=8,
    value=3,
    step=1,
    help="More chunks = more context, but higher chance of noise"
)
# ---------------- INPUT ----------------
query = st.text_input("Ask a question based on the documents:")

if query:
    with st.spinner("Agents are working..."):
        result = answer_query(query)

    # ================= USER QUERY =================
    st.subheader("❓ User Question")
    st.write(result["query"])

    # ================= RETRIEVAL AGENT =================
    with st.expander("🔍 Retrieval Agent — Initial Retrieved Chunks", expanded=True):
        for i, chunk in enumerate(result["retrieved_chunks"], 1):
            st.markdown(f"**Chunk {i} — Source: `{chunk['source']}`**")
            st.write(chunk["text"][:800] + "...")
            st.divider()

    # ================= RERANKING AGENT =================
    with st.expander("🧮 Reranking Agent — Relevance Scoring"):
        for i, chunk in enumerate(result["reranked_chunks"], 1):
            score = round(chunk.get("score", 0.0), 2)
            st.markdown(
                f"**Rank {i} | Score: `{score}` | Source: `{chunk['source']}`**"
            )
            st.progress(score)
            st.write(chunk["text"][:600] + "...")
            st.divider()

    # ================= GENERATION AGENT =================
    st.subheader("✍️ Generation Agent — Final Answer")
    st.success(result["answer"])
    if result["mcp_used"]:
        st.info("⚡ The answer utilized MCP (Model Context Protocol) for external knowledge/tools.")
    
    # ================= MCP ACTIVITY LOG (ADD HERE) =================
    st.subheader("🔌 MCP Activity Log")

    log_path = "mcp_server/mcp.log"

    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            logs = f.read().strip()

        if logs:
            st.code(logs, language="text")
        else:
            st.caption("MCP server running, but no tools called yet.")
    else:
        st.caption("MCP log not found.")
    # MCP context viewer
    if result.get("mcp_context"):
        st.subheader("📥 MCP Retrieved Context")
        st.code(result["mcp_context"], language="text")


    # ================= CITATION CONFIDENCE =================
    st.subheader("📊 Citation Confidence")
    for src, score in result["confidence"].items():
        st.markdown(f"**{src}**")
        st.progress(score / 100)
        st.caption(f"Confidence: {score}%")

    # ================= MCP INFO =================
    with st.expander("🔌 MCP (Model Context Protocol) Status"):
        st.write(
            """
            MCP enables agents to safely access external tools and knowledge.
            
            In this system:
            • MCP is **wired but optional**
            • Core RAG works without MCP
            • MCP can later provide AWS docs, APIs, or compliance tools
            """
        )
