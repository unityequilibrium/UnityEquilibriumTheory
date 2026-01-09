"""
Run long simulations for Extensions and Archetypes

Priority:
1. Extensions (structural tests) - T=100, N=10000
2. Archetypes (core demos) - T=100, N=10000
"""
import subprocess
import sys

# Extensions (highest priority - fundamental mechanisms)
EXTENSIONS = [
    "test_delays",
    "test_memory", 
    "test_nonlocal",
    "test_stochastic",
]

# Archetypes (second priority - core demos)
ARCHETYPES = [
    "BIAS_C",
    "BIAS_I",
    "SYM",
]

# Long run config
LONG_CONFIG = {
    "T": 100.0,      # 10x longer than default
    "N": 10000,      # 10x more steps
    "save_every": 100,  # save less frequently
}

def run_long_simulation(case_name):
    """Run a single long simulation"""
    print(f"\n{'='*60}")
    print(f"Running: {case_name} (LONG)")
    print(f"Config: T={LONG_CONFIG['T']}, N={LONG_CONFIG['N']}")
    print(f"{'='*60}\n")
    
    cmd = [
        sys.executable,
        "scripts/run_extension.py" if case_name.startswith("test_") else "scripts/run_case.py",
        "--case", case_name,
        "--T", str(LONG_CONFIG["T"]),
        "--N", str(LONG_CONFIG["N"]),
        "--save-every", str(LONG_CONFIG["save_every"]),
        "--output", f"runs_gallery/{case_name}",
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {case_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {case_name} failed:")
        print(e.stderr)
        return False

def main():
    print("="*60)
    print("LONG SIMULATION BATCH RUN")
    print("="*60)
    print(f"Extensions: {len(EXTENSIONS)}")
    print(f"Archetypes: {len(ARCHETYPES)}")
    print(f"Total: {len(EXTENSIONS) + len(ARCHETYPES)}")
    print("="*60)
    
    results = {}
    
    # Run Extensions first (highest priority)
    print("\n🔥 PHASE 1: Extensions (Structural Tests)")
    for ext in EXTENSIONS:
        results[ext] = run_long_simulation(ext)
    
    # Run Archetypes second
    print("\n🎯 PHASE 2: Archetypes (Core Demos)")
    for arch in ARCHETYPES:
        results[arch] = run_long_simulation(arch)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    success = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Completed: {success}/{total}")
    
    for name, status in results.items():
        symbol = "✅" if status else "❌"
        print(f"{symbol} {name}")
    
    print("="*60)

if __name__ == "__main__":
    main()
