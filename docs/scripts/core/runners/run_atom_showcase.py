
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

# --- PATH SETUP ---
current_path = Path(__file__).resolve()
# Go up to 'docs' root
repo_root = _UET_REPO_ROOT
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
        # Indent output for cleaner display
        print("\n".join(["    " + line for line in result.stdout.splitlines() if line.strip()]))
    else:
        print(f"❌ FAIL")
        print(result.stderr)
    print("-" * 60)


def main():
    print_header("THE ATOM (Structure & Light)")

    # 1. Hydrogen Spectrum (Atomic Structure)
    run_script(
        "docs/topics/0.20_Atomic_Physics_Spectroscopy/Code/03_Research/Research_Hydrogen_Spectrum.py",
        "Hydrogen Spectral Series (Lyman, Balmer, Paschen)",
    )

    # 2. Light Nuclei (The Core)
    run_script(
        "docs/topics/0.5_Nuclear_Binding_Hadrons/Code/01_Engine/Engine_Light_Nuclei.py",
        "Light Nuclei Solver (H-2, He-4 Stability)",
    )

    print("\n[CONCLUSION] The Atom is structured by UET Information Geometry.")


if __name__ == "__main__":
    main()
