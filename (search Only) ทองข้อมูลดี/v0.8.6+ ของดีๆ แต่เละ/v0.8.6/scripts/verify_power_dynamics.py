"""
Verification script for the new power_dynamics module.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from power_dynamics import run_simulation, analyze_cost_benefits, generate_full_report, solve_wave_equation

def main():
    print("Verifying power_dynamics package...")
    
    # 1. Test basic simulation
    print("\n[TEST 1] Running basic simulation...")
    pop = run_simulation(n_rounds=20, n_per_type=10, seed=42)
    print(f"  Simulation completed with {len(pop.agents)} agents.")
    
    # 2. Test analysis
    print("\n[TEST 2] Analyzing results...")
    analysis = analyze_cost_benefits(pop.agents)
    print(f"  Winner detected: {analysis['winner']}")
    
    # 3. Test wave function
    print("\n[TEST 3] Testing wave function effect...")
    actor = pop.agents[0]
    others = pop.agents[1:]
    successes = solve_wave_equation(actor, others)
    print(f"  Wave normalization successes: {successes}")
    
    # 4. Test reporting
    print("\n[TEST 4] Generating report...")
    report = generate_full_report(pop.history, analysis)
    print("\n" + report)
    
    print("\n✅ power_dynamics verification PASSED!")

if __name__ == "__main__":
    main()
