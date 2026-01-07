"""
Wave function implementation for Power Dynamics.
Handles influence spreading and multi-target normalization.
"""

import random
from typing import List
from .agents import Agent, TYPE_PROFILES

def solve_wave_equation(actor: Agent, targets: List[Agent], decay_factor: float = 1.0) -> int:
    """
    Wave function effect: Actor affects multiple targets based on influence radius.
    """
    profile = TYPE_PROFILES[actor.type]
    boldness = min(profile['power_init' if 'power_init' in profile else 'power'], 1.0)
    # Note: decision_boldness is used in agents.py, but wave script used 'boldness'
    # Use profile from agents.py for consistency
    boldness = profile.get('decision_boldness', profile.get('boldness', 0.5))
    altruism = 1 - profile.get('selfishness', 0.5)
    
    # Radius grows with success
    wave_radius = 5 + int(actor.normalized_count / 10)
    n_targets = min(wave_radius, len(targets))
    
    if n_targets == 0:
        return 0
    
    selected = random.sample(targets, n_targets)
    success_count = 0
    
    for target in selected:
        # Wave decay with distance (simulated)
        distance = random.uniform(0.5, 1.5) * decay_factor
        success_chance = boldness * altruism * actor.resources / distance
        resistance = target.power * 0.3
        
        if random.random() < (success_chance - resistance):
            success_count += 1
            actor.normalized_count += 1
            actor.resources = min(2.0, actor.resources + 0.02)
            target.resources = max(0.1, target.resources - 0.01)
            
    return success_count
