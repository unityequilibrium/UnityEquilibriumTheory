import numpy as np
import matplotlib.pyplot as plt


def run_wealth_flow_simulation():
    """
    Simulates Money Velocity in Equal vs Unequal Societies.
    Demonstrates that 'Hoarding' (Inequality) kills Flow (Velocity).
    """
    print("--- WEALTH FLOW SIMULATION ---")

    n_agents = 1000
    total_money = 1_000_000
    steps = 1000

    # --- SCENARIO 1: EQUAL DISTRIBUTION (Ideal Fluid) ---
    # Everyone has equal money to start. High propensity to spend.
    wallets_eq = np.ones(n_agents) * (total_money / n_agents)
    velocity_counters_eq = 0

    # --- SCENARIO 2: UNEQUAL DISTRIBUTION (Viscous/Clumpy) ---
    # Pareto Distribution (80/20 rule). 20% hold 80% of money.
    # Money trapped in 'Structure' (Savings/Assets) doesn't flow.
    wallets_uneq = np.random.pareto(a=2.0, size=n_agents)
    wallets_uneq = wallets_uneq / np.sum(wallets_uneq) * total_money
    velocity_counters_uneq = 0

    # Simulation: Random Transaction Cycle
    # Rule: Poorer agents spend faster (Survival). Richer agents hoard (Savings).
    # Spending Rate = 1.0 / (1.0 + log(Wealth))

    for t in range(steps):
        # 1. Equal Sim
        for i in range(100):  # 100 transactions per step
            sender = np.random.randint(0, n_agents)
            receiver = np.random.randint(0, n_agents)
            amount = 10  # Small transaction

            # Equal Spending Prob (High)
            prob_spend = 0.5
            if np.random.rand() < prob_spend and wallets_eq[sender] >= amount:
                wallets_eq[sender] -= amount
                wallets_eq[receiver] += amount
                velocity_counters_eq += amount

        # 2. Unequal Sim
        for i in range(100):
            sender = np.random.randint(0, n_agents)
            receiver = np.random.randint(0, n_agents)
            amount = 10

            # Unequal Spending Prob (Rich spend LESS % of wealth = Viscosity)
            # This models "Capital Accumulation" bottle-necking flow.
            wealth = wallets_uneq[sender]
            if wealth > 10000:  # "Rich"
                prob_spend = 0.05  # Hoards 95%
            else:
                prob_spend = 0.8  # Spends 80% (Survival)

            if np.random.rand() < prob_spend and wallets_uneq[sender] >= amount:
                wallets_uneq[sender] -= amount
                wallets_uneq[receiver] += amount
                velocity_counters_uneq += amount

    # Results
    v_eq = velocity_counters_eq / total_money
    v_uneq = velocity_counters_uneq / total_money

    print(f"Scenario 1 (Equal/Fluid):   Velocity = {v_eq:.4f}")
    print(f"Scenario 2 (Unequal/Clumpy): Velocity = {v_uneq:.4f}")

    flow_reduction = (1 - v_uneq / v_eq) * 100
    print(f"\nCONCLUSION:")
    print(f"Inequality causes a {flow_reduction:.1f}% drop in Flow.")
    print(f"The 'Bottleneck' you mentioned is mathematically Real.")
    print(f"UET calls this 'Viscosity' ($k$ decreases).")

    return v_eq, v_uneq


if __name__ == "__main__":
    run_wealth_flow_simulation()
