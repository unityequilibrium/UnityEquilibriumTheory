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
    result = subprocess.run([sys.executable, str(full_path)], capture_output=True, text=True)
    end_time = time.time()

    if result.returncode == 0:
        print(f"✅ PASS ({end_time - start_time:.2f}s)")
        print("\n".join(["    " + line for line in result.stdout.splitlines() if line.strip()]))
    else:
        print(f"❌ FAIL")
        print(result.stderr)
    print("-" * 60)


def main():
    print_header("NUCLEAR POWER & THE STRONG FORCE")

    # 1. Competitor Baseline (The Standard - now verified)
    run_script(
        "research_uet/topics/0.5_Nuclear_Binding_Hadrons/Code/04_Competitor/Competitor_Nuclear_Baseline.py",
        "Nuclear Binding Energy (H-2 to U-238)",
    )

    # 2. Strong Force & Color Confinement
    run_script(
        "research_uet/topics/0.5_Nuclear_Binding_Hadrons/Code/03_Research/Research_Strong_Force.py",
        "Strong Force: Confinement & Alpha_s Running",
    )

    # 3. Heavy Nuclei (Island of Stability)
    run_script(
        "research_uet/topics/0.16_Heavy_Nuclei_Fission/Code/01_Engine/Engine_Heavy_Nuclei.py",
        "Heavy Nuclei Stability (Predicting Z=126)",
    )

    print("\n[CONCLUSION] Nuclear Forces are Geometry. Energy is Information.")


if __name__ == "__main__":
    main()
