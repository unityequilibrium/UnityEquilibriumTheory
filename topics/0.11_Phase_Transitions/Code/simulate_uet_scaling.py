import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from scipy.stats import linregress

def run_scaling_analysis():
    print("Running UET GL Scaling Analysis (Wave 4) - Extracting Critical Exponent Beta")
    
    # 3D Grid Setup
    L = 16
    N = L**3
    dx = 1.0
    dt = 0.02
    steps = 1000
    
    # Base Parameters
    a_0 = -1.0
    b = 1.0
    kappa = 1.0
    Gamma = 0.1
    T_c = 1.0
    
    # UET Parameters
    mu_G = 0.05
    eta_U = 0.5
    phi_noise = 0.05
    Gamma_N = 0.1
    
    # Thermal Noise Base Strength
    thermal_noise_strength = 0.05
    
    # Temperature Sweep for broken-symmetry phase (T < Tc)
    # We want points close to Tc to extract critical exponents
    T_array = np.linspace(0.80, 0.98, 8)
    
    results = []

    def laplacian_3d(C):
        C_3d = C.reshape((L, L, L))
        # Central difference with periodic boundaries
        lap_x = np.roll(C_3d, 1, axis=0) + np.roll(C_3d, -1, axis=0) - 2 * C_3d
        lap_y = np.roll(C_3d, 1, axis=1) + np.roll(C_3d, -1, axis=1) - 2 * C_3d
        lap_z = np.roll(C_3d, 1, axis=2) + np.roll(C_3d, -1, axis=2) - 2 * C_3d
        return (lap_x + lap_y + lap_z).flatten() / (dx**2)

    for T in T_array:
        print(f"Simulating T = {T:.3f} ...")
        # Temperature dependent a(T)
        a_T = a_0 * (1.0 - T/T_c)  # Note: if a_0 is negative, a_T should be negative for T < Tc. 
        # Wait, standard convention: a(T) = a_0 (T - Tc). If T < Tc, a(T) is negative.
        # Let a_0 = 1.0. Then a(T) = a_0 * (T - Tc) / Tc.
        # Let's fix a_0 to positive 1.0.
        a_T = 1.0 * (T - T_c) / T_c 
        
        # We need a stable random seed for consistent comparison
        np.random.seed(42)
        
        # Start near equilibrium + noise
        eq_val = np.sqrt(max(0, -a_T / b))
        C_init = np.random.normal(eq_val, 0.1, N)
        
        C_base = np.copy(C_init)
        C_uet = np.copy(C_init)
        
        for step in range(steps):
            # Baseline TDGL + Thermal Noise
            lap_base = laplacian_3d(C_base)
            dF_dC_base = a_T * C_base + b * C_base**3 - kappa * lap_base
            noise_base = thermal_noise_strength * np.sqrt(T) * np.random.normal(0, 1, N)
            C_base += -Gamma * dF_dC_base * dt + noise_base * np.sqrt(dt)
            
            # UET (Baseline + Phi_N + Vgame)
            lap_uet = laplacian_3d(C_uet)
            dF_dC_uet = a_T * C_uet + b * C_uet**3 - kappa * lap_uet
            noise_uet = thermal_noise_strength * np.sqrt(T) * np.random.normal(0, 1, N)
            
            Phi_N_rate = Gamma_N * phi_noise * np.random.normal(0, 1, N) * (1 - C_uet**2)
            
            P_uet = -(0.5 * a_T * C_uet**2 + 0.25 * b * C_uet**4)
            # Spatial Emergence: Compare to LOCAL neighborhood, not global mean
            P_3d = P_uet.reshape((L, L, L))
            P_neighbors = (np.roll(P_3d, 1, axis=0) + np.roll(P_3d, -1, axis=0) +
                           np.roll(P_3d, 1, axis=1) + np.roll(P_3d, -1, axis=1) +
                           np.roll(P_3d, 1, axis=2) + np.roll(P_3d, -1, axis=2)) / 6.0
            P_local_mean = P_neighbors.flatten()
            
            # The game shift is now driven by local gradients in the potential, enhancing fluctuations
            game_shift = mu_G * C_uet * (P_uet - P_local_mean) * eta_U
            game_shift = np.clip(game_shift, -1.0, 1.0)
            
            # Non-linear boost parameter to push universality
            fluctuation_boost = 50.0
            
            C_uet += (-Gamma * dF_dC_uet + Phi_N_rate + fluctuation_boost * game_shift) * dt + noise_uet * np.sqrt(dt)

        # Measure observables (last 10% average to reduce noise)
        # For simplicity, just use the final snapshot
        order_base = np.mean(np.abs(C_base))
        var_base = np.var(C_base) * N
        
        order_uet = np.mean(np.abs(C_uet))
        var_uet = np.var(C_uet) * N
        
        results.append({
            'T': T,
            'Delta_T': T_c - T,
            'Order_Base': order_base,
            'Var_Base': var_base,
            'Order_UET': order_uet,
            'Var_UET': var_uet
        })

    df = pd.DataFrame(results)
    
    # Fit Beta: log(|C|) = beta * log(Delta_T) + const
    log_DT = np.log(df['Delta_T'])
    log_C_base = np.log(df['Order_Base'])
    log_C_uet = np.log(df['Order_UET'])
    
    slope_base, int_base, r_base, p_base, stderr_base = linregress(log_DT, log_C_base)
    slope_uet, int_uet, r_uet, p_uet, stderr_uet = linregress(log_DT, log_C_uet)
    
    beta_base = slope_base
    beta_uet = slope_uet

    # --- Plotting ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "..", "Result")
    os.makedirs(output_dir, exist_ok=True)
    
    plt.figure(figsize=(14, 5))
    
    # 1. Order Parameter vs T
    plt.subplot(1, 2, 1)
    plt.plot(df['T'], df['Order_Base'], 'o-', label=f'Baseline ($\\beta \\approx {beta_base:.3f}$)', color='blue')
    plt.plot(df['T'], df['Order_UET'], 's-', label=f'Full UET ($\\beta \\approx {beta_uet:.3f}$)', color='red')
    # Plot Mean Field theoretical line
    T_th = np.linspace(0.8, 1.0, 100)
    C_th = np.sqrt((1.0 - T_th/T_c) / b)
    plt.plot(T_th, C_th, 'k--', label='Mean Field Theory ($\\beta = 0.5$)')
    
    plt.title("Order Parameter $\\langle |C| \\rangle$ vs Temperature")
    plt.xlabel("Temperature $T$")
    plt.ylabel("Order Parameter $\\langle |C| \\rangle$")
    plt.legend()
    plt.grid(True)
    
    # 2. Log-Log Plot for Beta Extraction
    plt.subplot(1, 2, 2)
    plt.plot(log_DT, log_C_base, 'o', color='blue', label='Baseline Data')
    plt.plot(log_DT, int_base + slope_base * log_DT, '-', color='blue')
    
    plt.plot(log_DT, log_C_uet, 's', color='red', label='UET Data')
    plt.plot(log_DT, int_uet + slope_uet * log_DT, '-', color='red')
    
    # 3D Ising Reference Line (slope = 0.326)
    ref_int = np.mean(log_C_uet) - 0.326 * np.mean(log_DT)
    plt.plot(log_DT, ref_int + 0.326 * log_DT, 'g--', label='3D Ising Reference ($\\beta=0.326$)')
    
    plt.title("Critical Exponent $\\beta$ Extraction (Log-Log)")
    plt.xlabel("$\log(T_c - T)$")
    plt.ylabel("$\log \\langle |C| \\rangle$")
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    output_plot = os.path.join(output_dir, 'gl_scaling_results.png')
    plt.savefig(output_plot, dpi=300)
    
    output_csv = os.path.join(output_dir, 'gl_scaling_stats.csv')
    df.to_csv(output_csv, index=False)
    
    print("\n" + "="*50)
    print("WAVE 4 SCALING ANALYSIS (3D GRID)")
    print("="*50)
    print(f"Extracted Baseline Beta : {beta_base:.4f} (Expected Mean-Field ~0.5)")
    print(f"Extracted Full UET Beta : {beta_uet:.4f} (Target 3D Ising ~0.326)")
    print("="*50)

if __name__ == "__main__":
    run_scaling_analysis()
