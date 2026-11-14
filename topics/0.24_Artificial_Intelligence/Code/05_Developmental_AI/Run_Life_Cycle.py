"""
Script: Run Life Cycle (The "Game of Life" for AI)
Topic: 0.24 Artificial Intelligence
Folder: 05_Developmental_AI

Runs the full simulation of an AI growing from Infant to Adult.
"""

from docs import ROOT_PATH
from pathlib import Path
current_path = Path(__file__).resolve()
root_path = ROOT_PATH
from docs import ROOT_PATH
root_path = ROOT_PATH
import sys
import time
from pathlib import Path

# --- ROBUST PATH FINDER ---


# Add current directory to sys.path to allow importing siblings
if str(current_path.parent) not in sys.path:
    sys.path.insert(0, str(current_path.parent))

from Developmental_Agent import DevelopmentalAgent


def run_simulation(max_age=25):
    print("=" * 60)
    print("🧬  AI DEVELOPMENTAL SIMULATION: 'PROJECT GENESIS'")
    print("=" * 60)

    # 1. Birth
    agent = DevelopmentalAgent(name="UET_Child_v1")
    time.sleep(1)

    # 2. Growth Loop
    while agent.age < max_age:
        print(f"\n--- Year {agent.age} ---")

        # A. Learn
        # Amount of learning depends on age (Adults learn more/faster)
        learning_cycles = 2 if agent.age < 5 else 5
        for _ in range(learning_cycles):
            agent.learn()

        # B. Take Exam (if needed for the stage)
        # We try to pass the exam every year, but typically only pass at end of stage
        passed = agent.take_exam()

        # C. Grow
        agent.grow_one_year()

        # Pause for effect
        time.sleep(0.2)

        if agent.current_stage.name == "Adult" and passed:
            print("\n🎓  GRADUATION: The Agent has reached Adulthood and Mastery!")
            break

    print("=" * 60)
    print("🏁  SIMULATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_simulation()
