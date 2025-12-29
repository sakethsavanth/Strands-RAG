from strands.tools.mcp import MCPClient
import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from mcp import StdioServerParameters, stdio_client

regulatory_mcp = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="python",
            args=["mcp_server/server.py"]
        )
    )
)
