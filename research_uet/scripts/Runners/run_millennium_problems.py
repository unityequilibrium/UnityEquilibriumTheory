import subprocess
import os
import sys

# Define the 7 Millennium Problem scripts
MILLENNIUM_SCRIPTS = [
    ("Navier-Stokes", "research_uet/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Legacy_Comparison.py"),
    ("Yang-Mills", "research_uet/topics/0.21_Yang_Mills_Mass_Gap/Code/01_Engine/Engine_Mass_Gap.py"),
    ("Riemann Hypothesis", "research_uet/topics/0.18_Quantum_Computing/Code/03_Research/Research_Riemann_Zeta_UET.py"),
    ("P vs NP", "research_uet/topics/0.18_Quantum_Computing/Code/03_Research/Research_P_vs_NP_Scaling.py"),
    ("BSD Conjecture", "research_uet/topics/0.18_Quantum_Computing/Code/03_Research/Research_BSD_Elliptic_Unity.py"),
    ("Hodge Conjecture", "research_uet/topics/0.18_Quantum_Computing/Code/03_Research/Hodge_Lattice_Topography.py"),
    ("Poincaré (3D Smoothness)", "research_uet/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_3D_Turbulence_Limits.py")
]

def run_script(name, path):
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING: {name}")
    print(f"Path: {path}")
    print(f"{'='*60}\n")
    
    # Run the script and capture output
    try:
        result = subprocess.run([sys.executable, path], check=True, text=True)
        print(f"\n✅ {name} COMPLETED SUCCESSFULLY.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {name} FAILED with exit code {e.returncode}")
    except Exception as e:
        print(f"\n❌ ERROR running {name}: {str(e)}")

def main():
    print("🏆 UET MILLENNIUM PRIZE PROBLEMS: UNIFIED RUNNER")
    print("Running all 7 mathematical challenges using the Master Equation...\n")
    
    for name, path in MILLENNIUM_SCRIPTS:
        run_script(name, path)
        
    print(f"\n{'='*60}")
    print("🏁 ALL MILLENNIUM SESSIONS COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
