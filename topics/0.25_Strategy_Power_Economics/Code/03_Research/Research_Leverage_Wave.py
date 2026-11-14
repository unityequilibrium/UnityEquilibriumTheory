"""
Research_Leverage_Wave.py - UET Topic 0.25
==========================================
"""

import sys
import numpy as np
import random
from pathlib import Path

# Fix depth: 6 levels up to see 'docs' as a package
root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
sys.path.append(str(root))

# Local engine
engine_dir = Path(__file__).resolve().parent.parent / "01_Engine"
sys.path.append(str(engine_dir))

from Engine_Power_Dynamics import StrategicAgent


def run_leverage_experiment():
    print("📈 Research: The Wave of Influence (The Leverage Metaphor)")
    whale = StrategicAgent(
        id=0, agent_type="D", power=0.8, resources=10.0, boldness=0.9, selfishness=0.9
    )
    auditor = StrategicAgent(
        id=1, agent_type="C", power=0.3, resources=1.0, boldness=0.9, selfishness=0.1
    )

    print(f"Initial -> Whale: {whale.resources:.2f}, Auditor: {auditor.resources:.2f}")
    for _ in range(100):
        chance = auditor.boldness * (1.0 - auditor.selfishness) * auditor.resources
        if random.random() < (chance - whale.power * 0.4):
            transfer = whale.resources * 0.05
            whale.resources -= transfer
            auditor.resources += transfer * 0.4

    print(f"Final   -> Whale: {whale.resources:.2f}, Auditor: {auditor.resources:.2f}")
    if whale.resources < 5.0:
        print("\n✅ LEVERAGE SUCCESS!")


if __name__ == "__main__":
    run_leverage_experiment()
