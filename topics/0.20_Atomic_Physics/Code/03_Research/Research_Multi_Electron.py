from docs import ROOT_PATH
from pathlib import Path
current_path = Path(__file__).resolve()
root_path = ROOT_PATH
from docs import ROOT_PATH
root_path = ROOT_PATH
import sys
from pathlib import Path

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


# Import the Atomic Three Body Simulation (Helium Dynamics)
try:
    import Research_Atomic_ThreeBody
except ImportError:
    # Local import if needed
    sys.path.append(str(current_path.parent))
    import Research_Atomic_ThreeBody


def run_multi_electron_simulation():
    """
    Simulate Multi-Electron Atoms (e.g. Helium)
    using the Atomic Three-Body Chaos Engine.
    """
    print("=" * 60)
    print("🔬 Research: Multi-Electron Atom (Helium)")
    print("   Method: UET Atomic Three-Body Dynamics")
    print("=" * 60)

    # Run the Helium Simulation
    Research_Atomic_ThreeBody.run_three_body()

    print("\n✅ Multi-Electron Simulation Complete.")
    return True


if __name__ == "__main__":
    run_multi_electron_simulation()
