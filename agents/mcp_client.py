import requests

MCP_BASE = "http://localhost:3333"

def mcp_post(endpoint: str, payload: dict):
    r = requests.post(f"{MCP_BASE}{endpoint}", json=payload, timeout=5)
    r.raise_for_status()
    return r.json()
