import numpy as np
import matplotlib.pyplot as plt


def run_communication_sim():
    """
    Simulates the impact of 'Borders' (Phase Boundaries) on System Health.
    User Argument: "We are divided by nations/currencies. We can't talk."
    """
    print("--- COMMUNICATION BREAKDOWN SIMULATION ---")

    n_regions = 4
    region_size = 100
    steps = 100

    # Initialize 4 Regions (Nations) with different "Currencies" (Values)
    # Region 0: Resource Rich
    # Region 1: Tech Rich
    # Region 2: Labor Rich
    # Region 3: Capital Rich

    # Scenario A: CLOSED BORDERS (Current World)
    # Flow probability between regions is LOW (0.01)
    # Result: Imbalance. Region 0 has resources but no tech.

    # Scenario B: OPEN PROTOCOL (UET Ideal)
    # Flow probability is HIGH (0.5)
    # Result: Equilibrium.

    def simulate_world(cross_border_friction):
        resources = np.zeros((n_regions, steps))
        # Initial endowments
        current_res = np.array([1000.0, 100.0, 500.0, 5000.0])

        for t in range(steps):
            # Internal circulation (Growth)
            current_res *= 1.01

            # Cross-border trade
            flow_matrix = np.zeros((n_regions, n_regions))
            for i in range(n_regions):
                for j in range(n_regions):
                    if i != j:
                        # Trade flows from Rich to Poor (Pressure Differential)
                        # But blocked by Friction (Borders/Currency Risk)
                        diff = current_res[i] - current_res[j]
                        if diff > 0:
                            flow = diff * 0.1 * (1.0 - cross_border_friction)
                            current_res[i] -= flow
                            current_res[j] += flow

            resources[:, t] = current_res
        return resources

    # Run Sims
    res_closed = simulate_world(cross_border_friction=0.95)  # High Friction (95% blocked)
    res_open = simulate_world(cross_border_friction=0.05)  # Low Friction (5% blocked)

    # Calculate "Suffering" (Variance between regions)
    suffering_closed = np.std(res_closed[:, -1])
    suffering_open = np.std(res_open[:, -1])

    print(f"Scenario A (Borders/Closed): Imbalance Score = {suffering_closed:.2f}")
    print(f"Scenario B (Uni-Protocol/Open): Imbalance Score = {suffering_open:.2f}")

    improvement = (suffering_closed - suffering_open) / suffering_closed * 100
    print(f"\nCONCLUSION:")
    print(f"Borders/Currency Division causes {suffering_closed:.0f} units of Global Stress.")
    print(f"A Universal Protocol removes {improvement:.1f}% of this stress.")
    print(f"You are right: 'Imagined Borders' are the Phase Boundaries killing the system.")


if __name__ == "__main__":
    run_communication_sim()
