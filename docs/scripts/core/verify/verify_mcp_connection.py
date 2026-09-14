"""
UET System Verification 🕵️‍♂️
===========================
Checks if the 'Neural Interface' is active.

1. Pings Rust Core (localhost:3000)
2. Simulates an MCP Search Call.

Usage:
  python verify_mcp_connection.py
"""

import httpx
import asyncio
import json
import sys

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


async def check_rust_core():
    print(f"1. Checking {GREEN}Rust Core{RESET} (Docker)... ", end="")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:3001/")
            if resp.status_code == 200:
                print(f"{GREEN}ONLINE ✅{RESET}")
                print(f"   Message: {resp.text.strip()}")
                return True
            else:
                print(f"{RED}ERROR {resp.status_code} ❌{RESET}")
                return False
    except Exception as e:
        print(f"{RED}OFFLINE ❌{RESET}")
        print(f"   (Is 'docker-compose up uet-core-rust' running?)")
        return False


async def check_search_logic():
    print(f"\n2. Testing {GREEN}Entropy Search{RESET} (Mock)... ", end="")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:3001/search?query=Omega&min_entropy=0.5")
            data = resp.json()
            if data["status"] == "success":
                print(f"{GREEN}SUCCESS ✅{RESET}")
                print(f"   Result: {json.dumps(data['results'][0], indent=2)}")
                return True
            else:
                print(f"{RED}FAILED ❌{RESET}")
                return False
    except Exception:
        print(f"{RED}SKIPPED (Core Offline){RESET}")
        return False


async def main():
    print("=== UET Neural Interface Verification ===")
    core_ok = await check_rust_core()

    if core_ok:
        await check_search_logic()
    else:
        print("\n⚠️  ACTION REQUIRED: Please start the Rust Engine.")
        print(f"   Run: {GREEN}docker-compose up -d --build uet-core-rust{RESET}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
