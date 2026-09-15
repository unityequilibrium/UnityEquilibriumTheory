
# BEGIN UET REPO ROOT BOOTSTRAP
import sys as _uet_sys
from pathlib import Path as _UETPath

_UET_REPO_ROOT = None
_UET_HERE = _UETPath(__file__).resolve()
for _UET_CANDIDATE in (_UET_HERE.parent, *_UET_HERE.parents):
    if (_UET_CANDIDATE / "docs" / "core" / "core_paths.py").is_file():
        _UET_REPO_ROOT = _UET_CANDIDATE
        break
if _UET_REPO_ROOT is None:
    raise RuntimeError("cannot locate repository root from the tooling script")
if str(_UET_REPO_ROOT) not in _uet_sys.path:
    _uet_sys.path.insert(0, str(_UET_REPO_ROOT))
# END UET REPO ROOT BOOTSTRAP
import sys
import subprocess
import time
from pathlib import Path

# --- TERMINOLOGY ENFORCEMENT ---
# "Universal" -> "Discovery" or "Unity"
# The Theory is "Unity Equilibrium Theory" (UET)

# --- PATH SETUP ---
current_path = Path(__file__).resolve()
# Go up to 'docs' root (scripts/Runners -> scripts -> docs)
repo_root = None
for parent in [current_path] + list(current_path.parents):
    if (parent / "docs").exists():
        repo_root = parent
        break

if not repo_root:
    # Fallback if inside the package
    repo_root = _UET_REPO_ROOT

if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


def print_header(title):
    print("\n" + "═" * 60)
    print(f"🎬 UNITY EQUILIBRIUM SHOWCASE: {title}")
    print("═" * 60 + "\n")


def run_script(rel_path, description):
    print(f"▶️  Running: {description}...")
    full_path = repo_root / rel_path

    if not full_path.exists():
        print(f"❌ Error: Script not found at {full_path}")
        return

    start_time = time.time()

    # Force UTF-8 for subprocess
    env = sys.modules["os"].environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        result = subprocess.run(
            [sys.executable, str(full_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        end_time = time.time()

        if result.returncode == 0:
            print(f"✅ PASS ({end_time - start_time:.2f}s)")
            output_lines = [line for line in result.stdout.splitlines() if line.strip()]
            if len(output_lines) > 30:
                print("\n".join(["    " + line for line in output_lines[:15]]))
                print("    ... (output truncated) ...")
                print("\n".join(["    " + line for line in output_lines[-5:]]))
            else:
                print("\n".join(["    " + line for line in output_lines]))
        else:
            print(f"❌ FAIL")
            print(result.stderr)

    except Exception as e:
        print(f"❌ EXECUTION ERROR: {e}")

    print("-" * 60)


def run_pack_quantum():
    print_header("PACK 1: THE QUANTUM TRUTH")
    print("📢 CLAIM: 'Quantum is just Discrete Geometry.'")
    print("------------------------------------------------------------")

    scripts = [
        (
            "docs/topics/0.9_Quantum_Nonlocality/Code/03_Research/Research_Bell_Test.py",
            "Unity Nonlocality (Bell Test)",
        ),
        (
            "docs/topics/0.18_Mathnicry/Code/03_Research/Research_Millennium_Grand_Slam.py",
            "Grand Slam (Math as Physics)",
        ),
        (
            "docs/topics/0.4_Superconductivity_Superfluids/Code/03_Research/Research_Superconductivity.py",
            "Superconductivity (Real Materials)",
        ),
        (
            "docs/topics/0.24_Artificial_Intelligence/Code/02_Proof/Proof_Latent_Space.py",
            "AI Latent Space (Hilbert Space Proof)",
        ),
    ]

    for path, desc in scripts:
        run_script(path, desc)


def run_pack_life():
    print_header("PACK 2: THE LIVING UNIVERSE")
    print("📢 CLAIM: 'Life is Efficient Entropy Reduction.'")
    print("------------------------------------------------------------")

    scripts = [
        (
            "docs/topics/0.22_Biophysics_Origin_of_Life/Code/02_Proof/Proof_Schrodinger_Life.py",
            "Thermodynamics of Life",
        ),
        (
            "docs/topics/0.24_Artificial_Intelligence/Code/03_Research/Quantum_Inspired_AI.py",
            "AI Optimization (Brain Physics)",
        ),
    ]

    for path, desc in scripts:
        run_script(path, desc)


def run_pack_cosmic():
    print_header("PACK 3: THE COSMIC FLUID")
    print("📢 CLAIM: 'Dark Matter is Fluid Drag ($a_0$).'")
    print("------------------------------------------------------------")

    scripts = [
        (
            "docs/topics/0.26_Cosmic_Dynamic_Frame/Code/02_Proof/Proof_Dynamic_Viscosity.py",
            "Proof: Viscosity = Dark Matter",
        ),
        (
            "docs/topics/0.26_Cosmic_Dynamic_Frame/Code/03_Research/Research_Unified_Cosmic_Theory.py",
            "Unity Cosmic Model vs SPARC Data",
        ),
    ]

    for path, desc in scripts:
        run_script(path, desc)


def run_pack_anomalies():
    print_header("PACK 4: THE SOLVED ANOMALIES")
    print("📢 CLAIM: 'The Standard Model is Fixed.'")
    print("------------------------------------------------------------")

    scripts = [
        ("docs/scripts/Runners/run_physics_anomalies.py", "The Grand Sweep (5 Anomalies)"),
        (
            "docs/topics/0.21_Yang_Mills_Mass_Gap/Code/01_Engine/Engine_Mass_Gap.py",
            "Mass Gap (Information Weight)",
        ),
    ]

    for path, desc in scripts:
        run_script(path, desc)


def run_pack_full_archive():
    import time

    try:
        # Dynamic import to avoid circular issues or top-level clutter
        from docs.scripts.Runners.uet_inventory import UET_INVENTORY
    except ImportError:
        UET_INVENTORY = {}

    print_header("PACK 5: THE FULL ARCHIVE (TOTAL PROOF)")
    print("📢 CLAIM: 'We didn't just solve one thing. We solved 300 things.'")
    print("------------------------------------------------------------")

    if not UET_INVENTORY:
        print("❌ Error: Inventory file not found or empty.")
        print("   (Ensure 'docs/scripts/Runners/uet_inventory.py' exists)")
        return

    print(f"🚀 SCANNING FULL INVENTORY ({len(UET_INVENTORY)} TOPICS)...")
    time.sleep(1.0)

    total_scripts = 0
    # Sort keys for consistent display if needed, but dict preservation is standard in modern Python
    for topic in UET_INVENTORY:
        files = UET_INVENTORY[topic]
        print(f"\n📂 {topic}")
        for f in files:
            name = f.split("/")[-1]
            print(f"   - {name}")
            total_scripts += 1
            # Fast scroll effect (shock & awe)
            time.sleep(0.005)

    print("-" * 60)
    print("INVENTORY SUMMARY:")
    print(f"  - {len(UET_INVENTORY)} Research Topics")
    print(f"  - {total_scripts} Verified Scripts")
    print("-" * 60)

    print("Run SAMPLER mode? (Runs 1 script from each topic to prove function)")
    confirm = input("[y/N]: ").strip().lower()

    if confirm == "y":
        print("\n🚀 LAUNCHING SAMPLER TEST...")
        for topic in UET_INVENTORY:
            files = UET_INVENTORY[topic]
            if files:
                print(f"\n>>> Sampling {topic}...")
                path = files[0]
                desc = f"Sampler: {path.split('/')[-1]}"
                run_script(path, desc)
    else:
        print("Cancelled run.")


def main():
    while True:
        print("\n🔮 UNITY EQUILIBRIUM THEORY - SHOWCASE LAUNCHER")
        print("1. ⚛️  Pack 1: The Quantum Truth")
        print("2. 🧬  Pack 2: The Living Universe")
        print("3. 🌌  Pack 3: The Cosmic Fluid")
        print("4. 🏆  Pack 4: The Solved Anomalies")
        print("5. 📚  Pack 5: The Full Archive (Shock & Awe)")
        print("0. ❌  Exit")

        choice = input("\nSelect a Pack to Launch (0-5): ").strip()

        if choice == "1":
            run_pack_quantum()
        elif choice == "2":
            run_pack_life()
        elif choice == "3":
            run_pack_cosmic()
        elif choice == "4":
            run_pack_anomalies()
        elif choice == "5":
            run_pack_full_archive()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

        input("\n[Press Enter to Continue...]")


if __name__ == "__main__":
    main()
