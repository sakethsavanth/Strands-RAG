from fastmcp import FastMCP
import datetime

mcp = FastMCP("Regulatory Knowledge MCP")

LOG_FILE = "mcp_server/mcp.log"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.datetime.now()} | {msg}\n")

@mcp.tool()
def regulatory_lookup(topic: str) -> str:
    log(f"MCP tool called with topic: {topic}")

    topic_lower = topic.lower()

    if "bcbs" in topic_lower or "239" in topic_lower:
        response = (
            "BCBS 239 refers to Basel Committee principles for "
            "risk data aggregation and risk reporting. "
            "It focuses on accuracy, completeness, timeliness, "
            "and governance of risk data in banks."
        )

    elif "data aggregation" in topic_lower:
        response = (
            "Risk data aggregation refers to the ability of banks "
            "to collect, process, and aggregate risk data accurately "
            "and efficiently across business lines."
        )

    elif "explainability" in topic_lower:
        response = (
            "Model explainability refers to the ability to understand "
            "and interpret how a model produces its outputs, which is "
            "critical for trust, governance, and regulatory compliance."
        )

    # ✅ ADD YOUR BLOCK RIGHT HERE
    elif "project" in topic_lower:
        response = (
            "This project demonstrates an advanced Agentic RAG system "
            "built using Strands SDK, Amazon Titan embeddings for retrieval, "
            "Amazon Nova for generation, and MCP for secure external tool access."
        )

    else:
        response = "No external regulatory information found."

    log(f"MCP response: {response}")
    return response

if __name__ == "__main__":
    log("MCP server started")
    mcp.run()
    log("MCP server stopped")