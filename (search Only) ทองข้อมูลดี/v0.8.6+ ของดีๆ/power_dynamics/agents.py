"""
Agent definitions for Power Dynamics simulation.
"""

from dataclasses import dataclass
import random
from typing import List

@dataclass
class Agent:
    id: int
    type: str  # A, B, C, D
    power: float  # ศักยภาพ (0-1)
    resources: float  # ทรัพยากร
    influence: float  # อิทธิพลต่อคนอื่น
    normalized_count: int = 0  # จำนวนครั้งที่ normalize คนอื่นได้

# Type definitions based on UET Theory
TYPE_PROFILES = {
    'A': {'power_init': 0.3, 'decision_boldness': 0.2, 'selfishness': 0.3, 'name': 'ธรรมดา+ปกติ'},
    'B': {'power_init': 0.8, 'decision_boldness': 0.2, 'selfishness': 0.5, 'name': 'ไม่ธรรมดา+ปกติ'},
    'C': {'power_init': 0.3, 'decision_boldness': 0.9, 'selfishness': 0.1, 'name': 'ธรรมดา+ไม่ปกติ ★'},
    'D': {'power_init': 0.8, 'decision_boldness': 0.9, 'selfishness': 0.8, 'name': 'ไม่ธรรมดา+ไม่ปกติ'},
}

def create_population(n_per_type: int = 25) -> List[Agent]:
    """สร้างประชากร (25 คนต่อ type โดยพื้นฐาน)"""
    agents = []
    id_counter = 0
    for t in ['A', 'B', 'C', 'D']:
        profile = TYPE_PROFILES[t]
        for _ in range(n_per_type):
            agent = Agent(
                id=id_counter,
                type=t,
                power=profile['power_init'] + random.uniform(-0.1, 0.1),
                resources=1.0,
                influence=0.0
            )
            agents.append(agent)
            id_counter += 1
    return agents
