import sys
import subprocess
import time
from pathlib import Path

# --- PATH SETUP ---
current_path = Path(__file__).resolve()
repo_root = current_path.parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


def print_header(title):
    print("\n" + "=" * 60)
    print(f"🎬 UET LIVE SHOWCASE: {title}")
    print("=" * 60 + "\n")


def run_script(rel_path, description):
    print(f"▶️  Running: {description}...")
    full_path = repo_root / rel_path
    if not full_path.exists():
        print(f"❌ Error: Script not found at {full_path}")
        return

    start_time = time.time()
    # Force UTF-8 for subprocess to handle emojis
    env = sys.modules["os"].environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, str(full_path)], capture_output=True, text=True, encoding="utf-8", env=env
    )
    end_time = time.time()

    if result.returncode == 0:
        print(f"✅ PASS ({end_time - start_time:.2f}s)")
        print("\n".join(["    " + line for line in result.stdout.splitlines() if line.strip()]))
    else:
        print(f"❌ FAIL")
        print(result.stderr)
    print("-" * 60)


def main():
    print_header("THE QUANTUM FUTURE & MATHEMATICAL FOUNDATION")

    # 1. QUANTUM PHYSICS (Topic 0.9)
    # The true home of Quantum Mechanics in UET
    print("\n[SECTION 1] QUANTUM FUNDAMENTALS (Nonlocality & Entanglement)")
    run_script(
        "topics/0.9_Quantum_Nonlocality/Code/03_Research/Research_Bell_Test.py",
        "Bell's Inequality Test (Universal Connectivity)",
    )

    # 2. QUANTUM HARDWARE (Topic 0.4)
    print("\n[SECTION 2] QUANTUM HARDWARE (Room Temp Superconductors)")
    run_script(
        "topics/0.4_Superconductivity_Superfluids/Code/04_Competitor/Competitor_Standard_Model_Super.py",
        "Material Correctness: Pb, Hg, Nb",
    )

    # 3. MATHEMATICAL ENGINE (Topic 0.18)
    # The Logic Core - Separated from Quantum Physics
    print("\n[SECTION 3] MATHEMATICAL PROOFS (The 'Mathnicry' Core)")
    run_script(
        "topics/0.18_Mathnicry/Code/03_Research/Research_Millennium_Grand_Slam.py",
        "Millennium Prize Problems (Grand Slam Resolution)",
    )

    # 4. ARTIFICIAL INTELLIGENCE (Topic 0.24)
    print("\n[SECTION 4] ARTIFICIAL INTELLIGENCE (The Cortex)")
    run_script(
        "topics/0.24_Artificial_Intelligence/Code/03_Research/Quantum_Inspired_AI.py",
        "Physics-Based Learning System (Quantum Inspired AI)",
    )

    print("\n" + "=" * 60)
    print("[CONCLUSION] Physics (0.9/0.4) + Math (0.18) + AI (0.24) = THE FUTURE")
    print("=" * 60)


if __name__ == "__main__":
    main()
