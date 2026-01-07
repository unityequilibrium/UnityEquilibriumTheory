import numpy as np
import matplotlib.pyplot as plt


def calculate_stimulus(lockdown_severity):
    """
    Calculates required Money Supply (M) increase based on Social Disconnection (k).
    Model: M * V = GDP
    UET Constraint: V is proportional to k (Connectivity).
    """

    # 1. Initial State (Pre-Pandemic)
    k_social_initial = 10.0  # Normal connectivity
    M_initial = 100.0  # Initial Money Supply (e.g. Trillions)
    V_initial = k_social_initial  # Velocity follows connectivity
    GDP_initial = M_initial * V_initial

    print(f"--- INITIAL STATE ---")
    print(f"Social Connectivity (k): {k_social_initial}")
    print(f"Money Velocity (V):      {V_initial}")
    print(f"Stable GDP (P*Q):        {GDP_initial}")
    print(f"-" * 30)

    # 2. Pandemic Shock
    # Severity 0.0 to 1.0 (1.0 = Total Isolation)
    k_social_new = k_social_initial * (1.0 - lockdown_severity)

    print(f"--- PANDEMIC SHOCK (Severity {lockdown_severity*100}%) ---")
    print(f"New Connectivity (k):    {k_social_new:.2f}")

    # UET Rule: Velocity drops with Connectivity
    V_new = k_social_new
    print(f"New Velocity (V):        {V_new:.2f} (Slower spending)")

    # 3. The Calculation: How much Money (M) is needed to save GDP?
    # Target: M_new * V_new = GDP_initial
    # M_new = GDP_initial / V_new

    M_new = GDP_initial / V_new
    M_increase = M_new - M_initial

    print(f"-" * 30)
    print(f"--- UET PREDICTION ---")
    print(f"Required Money Supply:   {M_new:.2f}")
    print(f"STIMULUS REQUIRED:       +{M_increase:.2f} (Print this amount!)")
    print(f"Inflation Risk Multiplier: {M_new/M_initial:.2f}x")

    return M_increase


if __name__ == "__main__":
    # Example: 50% Lockdown
    calculate_stimulus(0.5)
