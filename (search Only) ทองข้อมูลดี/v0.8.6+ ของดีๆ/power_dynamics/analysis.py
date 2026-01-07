"""
Analysis and Analytics for Power Dynamics.
Detects equilibrium, cost-benefit ratios, and win rates.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from .agents import Agent, TYPE_PROFILES

def analyze_cost_benefits(agents: List[Agent]) -> Dict[str, Any]:
    """
    Analyzes efficiency (normalizations per person) and influence.
    """
    type_totals = {}
    type_counts = {}
    type_influence = {}
    
    for agent in agents:
        t = agent.type
        type_totals[t] = type_totals.get(t, 0) + agent.normalized_count
        type_counts[t] = type_counts.get(t, 0) + 1
        type_influence[t] = type_influence.get(t, 0) + agent.influence

    efficiency = {}
    for t in type_counts:
        efficiency[t] = type_totals[t] / type_counts[t] if type_counts[t] > 0 else 0
        
    winner = max(efficiency, key=efficiency.get) if efficiency else None
    
    return {
        "efficiency": efficiency,
        "totals": type_totals,
        "influence": type_influence,
        "winner": winner
    }

def detect_equilibrium(omega_history: List[float], window: int = 10, epsilon: float = 1e-5) -> Optional[int]:
    """
    Detects if the system has reached a stable Ω state.
    """
    if len(omega_history) < window + 1:
        return None
        
    d_omega = np.abs(np.diff(omega_history))
    
    for i in range(len(d_omega) - window + 1):
        if np.mean(d_omega[i:i+window]) < epsilon:
            return i + 1
            
    return None
