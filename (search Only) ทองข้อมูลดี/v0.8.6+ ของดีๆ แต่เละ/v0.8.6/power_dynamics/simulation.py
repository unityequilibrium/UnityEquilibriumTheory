"""
Core simulation logic for Power Dynamics.
"""

import random
import numpy as np
from typing import List, Dict
from .agents import Agent, TYPE_PROFILES

class Population:
    def __init__(self, agents: List[Agent]):
        self.agents = agents
        self.history = {'omega': [], 'stats': []}

    def simulate_round(self) -> Dict[str, int]:
        """จำลอง 1 รอบ: ทุกคนพยายาม normalize ใครสักคน"""
        round_stats = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        
        for actor in self.agents:
            # เลือก target แบบ random (ไม่ใช่ตัวเอง)
            possible_targets = [a for a in self.agents if a.id != actor.id]
            if not possible_targets:
                continue
            target = random.choice(possible_targets)
            
            if self.attempt_normalize(actor, target):
                actor.normalized_count += 1
                actor.influence += 0.1
                actor.resources += 0.05
                target.resources -= 0.02
                round_stats[actor.type] += 1
        
        self.history['stats'].append(round_stats)
        self.history['omega'].append(self.calculate_omega())
        return round_stats

    def attempt_normalize(self, actor: Agent, target: Agent) -> bool:
        """Actor พยายาม normalize Target"""
        profile = TYPE_PROFILES[actor.type]
        boldness = profile['decision_boldness']
        altruism = 1 - profile['selfishness']
        success_chance = boldness * altruism * actor.resources
        target_resistance = target.power * 0.5
        net_chance = success_chance - target_resistance
        return random.random() < net_chance

    def calculate_omega(self) -> float:
        """คำนวณ Ω ของระบบ (variance ของ resources)"""
        resources = [a.resources for a in self.agents]
        return float(np.var(resources))

def run_simulation(n_rounds: int = 50, n_per_type: int = 25, seed: int = 42):
    """รัน simulation พร้อมแสดงผลสรุป"""
    random.seed(seed)
    np.random.seed(seed)
    
    from .agents import create_population
    agents = create_population(n_per_type)
    pop = Population(agents)
    
    for r in range(n_rounds):
        pop.simulate_round()
        
    return pop
