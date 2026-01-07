"""
Reporting and Visualization for Power Dynamics.
Generates comprehensive simulation reports and summaries.
"""

from typing import List, Dict, Any
from .agents import TYPE_PROFILES
from .analysis import analyze_cost_benefits

def generate_full_report(pop_history: Dict[str, Any], efficiency_data: Dict[str, Any]) -> str:
    """
    Generates a text-based summary report of the simulation.
    """
    lines = []
    lines.append("="*60)
    lines.append(" UET POWER DYNAMICS - SIMULATION REPORT ".center(60))
    lines.append("="*60)
    
    lines.append("\nFinal Efficiency (Normalizations per Person):")
    eff = efficiency_data["efficiency"]
    for t in ['A', 'B', 'C', 'D']:
        if t in eff:
            bar = '█' * int(eff[t] / 10)
            lines.append(f"  {t} ({TYPE_PROFILES[t]['name']:<20}): {eff[t]:6.1f} {bar}")

    winner = efficiency_data["winner"]
    lines.append("\n" + "-"*60)
    lines.append(f"🏆 WINNER: Type {winner} ({TYPE_PROFILES[winner]['name']})")
    lines.append("-"*60)
    
    if winner == 'C':
        lines.append("\n✅ Theory Validated: Type C (Normal+Extraordinary) Dominates!")
    else:
        lines.append(f"\n⚠️ Result: Type {winner} wins. Consider parameter adjustments.")

    omega_final = pop_history['omega'][-1]
    omega_init = pop_history['omega'][0]
    lines.append(f"\nΩ Change: {omega_init:.4f} -> {omega_final:.4f}")
    if omega_final < omega_init:
        lines.append("  → System reached higher stability (Ω decreased)")
    
    return "\n".join(lines)

def summarize_batch_results(results: List[str]) -> Dict[str, int]:
    """
    Summarizes a list of winners from multiple seeds.
    """
    from collections import Counter
    return dict(Counter(results))
