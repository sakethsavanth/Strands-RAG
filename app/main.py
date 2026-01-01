import streamlit as st
import sys
import os
import requests
import pandas as pd

# ---------------------------------------------------------
# Path setup
# ---------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from agents.orchestrator import answer_query
from rag.ingest_titan import ingest_files
   # ✅ NEW

# ---------------------------------------------------------
# Constants
# ---------------------------------------------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------------------------------------
# Page config
# ---------------------------------------------------------
st.set_page_config(
    page_title="Advanced Agentic RAG",
    layout="wide"
)

# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------------------------------------
# MCP Health Check
# ---------------------------------------------------------
def check_mcp_health():
    try:
        r = requests.get("http://localhost:3333/docs", timeout=1)
        return r.status_code == 200
    except Exception:
        return False

mcp_online = check_mcp_health()

# ---------------------------------------------------------
# Header + MCP Health + Clear Chat
# ---------------------------------------------------------
col1, col2, col3 = st.columns([6, 2, 1])

with col1:
    st.title("🤖 Advanced Agentic RAG")
    st.caption("Explainable Agentic RAG with FastMCP Governance")

with col2:
    if mcp_online:
        st.success("🟢 MCP Online")
    else:
        st.error("🔴 MCP Offline")

with col3:
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# =========================================================
# 📂 SIDEBAR — DOCUMENT MANAGEMENT (NEW)
# =========================================================
st.sidebar.header("📂 Documents")

# -------- Upload (+) --------
uploaded = st.sidebar.file_uploader(
    "➕ Add document",
    type=["pdf"]
)

if uploaded:
    save_path = os.path.join(DATA_DIR, uploaded.name)

    with open(save_path, "wb") as f:
        f.write(uploaded.getbuffer())

    status_box = st.sidebar.empty()

    ingest_files(
        status_callback=lambda msg: status_box.info(msg)
    )

    status_box.success("✅ Document ingested & ready for querying")

# -------- Existing documents --------
st.sidebar.subheader("📑 Existing Documents")

pdfs = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf")]

if not pdfs:
    st.sidebar.caption("No documents uploaded yet.")
else:
    for file in pdfs:
        col_a, col_b = st.sidebar.columns([4, 1])
        col_a.write(file)

        if col_b.button("🗑️", key=f"delete_{file}"):
            os.remove(os.path.join(DATA_DIR, file))

            status_box = st.sidebar.empty()
            status_box.warning("Rebuilding index after deletion...")

            ingest_files(
                status_callback=lambda msg: status_box.info(msg)
            )

            status_box.success("Index rebuilt")
            st.rerun()

# ---------------------------------------------------------
# Styling
# ---------------------------------------------------------
st.markdown("""
<style>
.chat-wrapper {
    max-width: 950px;
    margin: auto;
}
.user-bubble {
    background-color: #DCF8C6;
    padding: 12px 16px;
    border-radius: 18px;
    margin: 10px 0;
    text-align: right;
}
.assistant-bubble {
    background-color: #F1F0F0;
    padding: 12px 16px;
    border-radius: 18px;
    margin: 10px 0;
}
.badge-runtime {
    background-color: #2ecc71;
    color: white;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 12px;
}
.badge-logical {
    background-color: #3498db;
    color: white;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 12px;
}
.timeline-bar {
    height: 14px;
    border-radius: 6px;
    margin: 6px 0;
}
.runtime-bar {
    background-color: #2ecc71;
}
.logical-bar {
    background-color: #3498db;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Chat Rendering
# ---------------------------------------------------------
with st.container():
    st.markdown("<div class='chat-wrapper'>", unsafe_allow_html=True)

    for msg_idx, msg in enumerate(st.session_state.chat_history):
        if msg["role"] == "user":
            st.markdown(
                f"<div class='user-bubble'>{msg['content']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='assistant-bubble'>{msg['content']}</div>",
                unsafe_allow_html=True
            )

            with st.expander("🔍 How this answer was produced", expanded=False):

                # -------------------------------------------------
                # Agent Execution Timeline
                # -------------------------------------------------
                st.subheader("⏱ Agent Execution Timeline")

                for ev in msg.get("agent_events", []):
                    bar_class = "runtime-bar" if ev["type"] == "runtime" else "logical-bar"
                    badge = (
                        "<span class='badge-runtime'>Runtime</span>"
                        if ev["type"] == "runtime"
                        else "<span class='badge-logical'>Logical</span>"
                    )

                    st.markdown(
                        f"""
                        <div>
                            <strong>{ev['agent']}</strong> {badge}<br>
                            <small>{ev['reason']}</small>
                            <div class="timeline-bar {bar_class}"></div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # -------------------------------------------------
                # Agent Participation Table
                # -------------------------------------------------
                st.subheader("🧩 Agent Participation Summary")

                agent_events = msg.get("agent_events", [])
                if agent_events:
                    df = pd.DataFrame(agent_events)

                    summary = (
                        df.groupby(["agent", "type"])
                        .size()
                        .reset_index(name="calls")
                        .sort_values("calls", ascending=False)
                    )

                    def format_type(t):
                        return "🟢 Runtime" if t == "runtime" else "🔵 Logical"

                    summary["Agent Type"] = summary["type"].apply(format_type)

                    st.dataframe(
                        summary[["agent", "Agent Type", "calls"]],
                        use_container_width=True,
                        hide_index=True
                    )

                # -------------------------------------------------
                # Retrieved Chunks
                # -------------------------------------------------
                st.subheader("📚 Retrieved Chunks")

                chunks = msg.get("chunks", [])
                if not chunks:
                    st.info("No chunks retrieved.")
                else:
                    for i, c in enumerate(chunks, 1):
                        st.text_area(
                        f"Chunk {i}",
                        c.get("text", ""),
                        height=130,
                        key=f"chunk_{msg_idx}_{i}"


                        )

                # -------------------------------------------------
                # MCP Governance
                # -------------------------------------------------
                st.subheader("🧠 MCP Governance")

                if "mcp" in msg:
                    st.json(msg["mcp"]["classification"])
                    st.json(msg["mcp"]["strategy"])
                    st.json(msg["mcp"]["negotiation"])
                    st.json(msg["mcp"]["validation"])
                    st.info(msg["mcp"]["narration"]["narration"])
                else:
                    st.info("MCP governance data not available.")

                # -------------------------------------------------
                # Confidence
                # -------------------------------------------------
                st.subheader("📊 Agent Confidence")
                st.progress(msg.get("confidence", 0.0))
                st.caption(f"Confidence Score: {msg.get('confidence')}")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Chat Input
# ---------------------------------------------------------
query = st.chat_input("Ask a question about your documents...")

if query:
    st.session_state.chat_history.append({
        "role": "user",
        "content": query
    })

    with st.spinner("Thinking..."):
        result = answer_query(query)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": result["answer"],
        "trace": result["trace"],
        "agent_events": result["agent_events"],
        "chunks": result["chunks"],
        "mcp": result["mcp"],
        "confidence": result["confidence"]
    })

    st.rerun()
