import subprocess
import sys
import os

def start_mcp_server():
    return subprocess.Popen(
        [sys.executable, os.path.join("mcp_server", "server.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
