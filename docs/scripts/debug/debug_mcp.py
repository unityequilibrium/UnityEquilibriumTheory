import subprocess
import json
import time
import sys
import threading


def read_stream(stream, prefix):
    for line in iter(stream.readline, ""):
        print(f"{prefix}: {line.strip()}")


def run():
    print("Starting MCP Server...")
    # Use the batch file directly
    cmd = ["c:\\Users\\santa\\Desktop\\lad\\Lab_uet_harness_v0.8.7\\start_mcp_server.bat"]

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # Line buffered
    )

    # Start threads to read stdout/stderr without blocking
    threading.Thread(target=read_stream, args=(process.stdout, "STDOUT"), daemon=True).start()
    threading.Thread(target=read_stream, args=(process.stderr, "STDERR"), daemon=True).start()

    # 1. Initialize
    init_req = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "debug-script", "version": "1.0"},
        },
        "id": 1,
    }

    print(f"Sending Init: {json.dumps(init_req)}")
    process.stdin.write(json.dumps(init_req) + "\n")
    process.stdin.flush()

    time.sleep(2)

    # 2. Tools List (This is where it fails for the user)
    tools_req = {"jsonrpc": "2.0", "method": "tools/list", "id": 2}
    print(f"Sending Tools List: {json.dumps(tools_req)}")
    process.stdin.write(json.dumps(tools_req) + "\n")
    process.stdin.flush()

    time.sleep(2)

    # Terminate
    process.terminate()


if __name__ == "__main__":
    run()
