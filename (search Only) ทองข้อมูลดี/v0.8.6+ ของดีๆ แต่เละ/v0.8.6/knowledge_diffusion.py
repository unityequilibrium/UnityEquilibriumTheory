"""
KNOWLEDGE DIFFUSION SIMULATION
How far does a theory spread? Who learns it?
Example: Newton created F=ma → how many people understand it today?
"""
import numpy as np
from dataclasses import dataclass, field
from typing import List, Set
import random

@dataclass
class Agent:
    id: int
    type: str
    intelligence: float  # ability to understand
    openness: float  # willingness to learn
    learned: bool = False  # has learned the theory?
    spread_count: int = 0  # how many people they taught

# Population types
TYPES = {
    'Scholar': {'pop_pct': 0.01, 'intelligence': 0.9, 'openness': 0.9},  # นักวิชาการ
    'Educated': {'pop_pct': 0.10, 'intelligence': 0.7, 'openness': 0.6},  # คนมีการศึกษา
    'Average': {'pop_pct': 0.60, 'intelligence': 0.4, 'openness': 0.4},   # คนทั่วไป
    'Resistant': {'pop_pct': 0.20, 'intelligence': 0.3, 'openness': 0.1}, # คนต่อต้าน
    'Creator': {'pop_pct': 0.00, 'intelligence': 1.0, 'openness': 1.0},   # คนสร้างทฤษฎี (C)
}

def create_population(total: int, n_creators: int = 1) -> List[Agent]:
    agents = []
    id_counter = 0
    
    # Create regular population
    remaining = total - n_creators
    for t, props in TYPES.items():
        if t == 'Creator':
            continue
        n = int(remaining * props['pop_pct'])
        for _ in range(n):
            agents.append(Agent(
                id=id_counter, type=t,
                intelligence=props['intelligence'] + random.uniform(-0.1, 0.1),
                openness=props['openness'] + random.uniform(-0.1, 0.1)
            ))
            id_counter += 1
    
    # Create the creator(s) - they already know
    for _ in range(n_creators):
        agents.append(Agent(
            id=id_counter, type='Creator',
            intelligence=1.0, openness=1.0,
            learned=True
        ))
        id_counter += 1
    
    return agents

def attempt_teach(teacher, student):
    """Teacher tries to teach student"""
    # Success depends on teacher's ability + student's intelligence + openness
    teach_skill = 0.5 if teacher.type == 'Creator' else 0.3
    understand_chance = student.intelligence * student.openness * teach_skill
    return random.random() < understand_chance

def run_simulation(total: int, n_creators: int, generations: int, seed: int = 42):
    random.seed(seed)
    agents = create_population(total, n_creators)
    
    history = []
    
    for gen in range(generations):
        # Each person who knows tries to teach
        knowers = [a for a in agents if a.learned]
        not_knowers = [a for a in agents if not a.learned]
        
        if not not_knowers:
            break  # Everyone knows!
        
        for teacher in knowers:
            # WAVE FUNCTION: affects multiple people, not just 1!
            # Number of people reached = based on influence
            influence_radius = 5 + teacher.spread_count  # grows over time
            n_reached = min(influence_radius, len(not_knowers))
            
            # Try to teach multiple people
            targets = random.sample(not_knowers, min(n_reached, len(not_knowers)))
            
            for student in targets:
                # Probability decreases with "distance" (random factor)
                distance = random.uniform(0.3, 1.0)  # wave decay
                adjusted_chance = student.intelligence * student.openness * 0.5 / distance
                
                if random.random() < adjusted_chance:
                    student.learned = True
                    teacher.spread_count += 1
                    not_knowers.remove(student)
        
        # Count by type
        learned_by_type = {}
        for t in TYPES.keys():
            pop = [a for a in agents if a.type == t]
            learned = [a for a in pop if a.learned]
            learned_by_type[t] = len(learned) / len(pop) if pop else 0
        
        total_learned = len([a for a in agents if a.learned])
        history.append({
            'generation': gen,
            'total_pct': total_learned / total * 100,
            'by_type': learned_by_type
        })
    
    return agents, history

def main():
    print("="*70)
    print("KNOWLEDGE DIFFUSION SIMULATION")
    print("How far does a theory spread over generations?")
    print("="*70)
    print()
    print("Population types:")
    for t, p in TYPES.items():
        if t != 'Creator':
            print(f"  {t}: {p['pop_pct']*100:.0f}% (IQ={p['intelligence']}, open={p['openness']})")
    print()
    
    # Simulate Newton's theory over 300 years (~10 generations)
    total = 1000
    n_creators = 1
    generations = 50
    
    print(f"Scenario: {n_creators} creator(s), {total} people, {generations} generations")
    print("="*70)
    
    agents, history = run_simulation(total, n_creators, generations)
    
    # Print progress
    print()
    print("Progress over generations:")
    print(f"{'Gen':>5} | {'Total%':>8} | {'Scholar':>10} | {'Educated':>10} | {'Average':>10} | {'Resistant':>10}")
    print("-"*70)
    
    for h in history[::5]:  # Every 5 generations
        gen = h['generation']
        total_pct = h['total_pct']
        by_type = h['by_type']
        print(f"{gen:>5} | {total_pct:>7.1f}% | {by_type['Scholar']*100:>9.1f}% | {by_type['Educated']*100:>9.1f}% | {by_type['Average']*100:>9.1f}% | {by_type['Resistant']*100:>9.1f}%")
    
    # Final results
    print()
    print("="*70)
    print("FINAL RESULTS")
    print("="*70)
    
    final = history[-1] if history else None
    if final:
        print(f"\nAfter {generations} generations:")
        print(f"  Total learned: {final['total_pct']:.1f}%")
        print()
        print("By type:")
        for t in ['Scholar', 'Educated', 'Average', 'Resistant']:
            pct = final['by_type'].get(t, 0) * 100
            bar = '█' * int(pct / 5)
            print(f"  {t:>10}: {pct:>5.1f}% {bar}")
    
    print()
    print("="*70)
    print("INSIGHT")
    print("="*70)
    print()
    print("ทฤษฎีแพร่กระจายตาม intelligence × openness:")
    print("  - Scholar: เข้าใจเร็วและกว้าง")
    print("  - Educated: เข้าใจได้แต่ช้ากว่า")
    print("  - Average: เข้าใจได้บางส่วน")
    print("  - Resistant: แทบไม่เข้าใจเลย (openness ต่ำ)")
    print()
    print("แม้ทฤษฎีจะถูกต้อง 100%")
    print("  → ไม่ใช่ทุกคนจะเข้าใจ")
    print("  → ขึ้นอยู่กับ 'ผู้รับ' ไม่ใช่แค่ 'ผู้ส่ง'")

if __name__ == "__main__":
    main()
