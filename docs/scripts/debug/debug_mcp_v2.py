import subprocess
import json
import time
import sys
import threading


def read_stream(stream, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for line in iter(stream.readline, ""):
            f.write(line)
            f.flush()


def run():
    print("Starting MCP Server...")
    cmd = ["c:\\Users\\santa\\Desktop\\lad\\Lab_uet_harness_v0.8.7\\start_mcp_server.bat"]

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    t1 = threading.Thread(target=read_stream, args=(process.stdout, "mcp_stdout.txt"), daemon=True)
    t2 = threading.Thread(target=read_stream, args=(process.stderr, "mcp_stderr.txt"), daemon=True)
    t1.start()
    t2.start()

    # 1. Initialize
    init_req = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",  # Updated protocol version
            "capabilities": {},
            "clientInfo": {"name": "debug-script", "version": "1.0"},
        },
        "id": 1,
    }

    print(f"Sending Init...")
    process.stdin.write(json.dumps(init_req) + "\n")
    process.stdin.flush()

    time.sleep(2)

    # 2. Tools List
    tools_req = {"jsonrpc": "2.0", "method": "tools/list", "id": 2}
    print(f"Sending Tools List...")
    process.stdin.write(json.dumps(tools_req) + "\n")
    process.stdin.flush()

    time.sleep(2)

    process.terminate()
    print("Done. Check mcp_stdout.txt and mcp_stderr.txt")


if __name__ == "__main__":
    run()
