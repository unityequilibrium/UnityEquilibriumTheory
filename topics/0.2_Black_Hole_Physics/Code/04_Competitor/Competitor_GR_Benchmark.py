"""
Standard General Relativity Black Hole Benchmark
================================================
Calculates standard BH metrics for comparison with UET.
- Schwarzschild Radius
- Hawking Temperature
- Bekenstein-Hawking Entropy
- Evaporation Time
- Photon Sphere

Acts as the "Control Group" or "Null Hypothesis".
"""

import numpy as np
import csv
from pathlib import Path

# Constants (SI)
c = 2.998e8
G = 6.674e-11
h_bar = 1.054e-34
k_B = 1.38e-23
M_sun = 1.989e30


def calculate_gr_metrics(mass_msun):
    M = mass_msun * M_sun

    # Schwarzschild Radius (Rs = 2GM/c^2)
    Rs = 2 * G * M / c**2

    # Photon Sphere (R_ph = 1.5 Rs)
    R_ph = 1.5 * Rs

    # Hawking Temperature (T_H = hbar c^3 / 8 pi G M k_B)
    T_H = (h_bar * c**3) / (8 * np.pi * G * M * k_B)

    # Entropy (S = k_B * A / 4 L_p^2) -> S_bits ~ A
    # Standard formula: S = 4 pi G M^2 k_B / h_bar c
    S = 4 * np.pi * G * M**2 * k_B / (h_bar * c)

    # Evaporation Time (t ~ 5120 pi G^2 M^3 / h_bar c^4)
    # Approx: t (years) ~ 6.6e74 * (M/M_sun)^3 (Page 1976)
    t_evap_yr = 6.6e74 * mass_msun**3

    return {
        "Mass_Msun": mass_msun,
        "Rs_m": Rs,
        "R_photon_m": R_ph,
        "Temp_K": T_H,
        "Entropy_J_K": S,
        "Life_Years": t_evap_yr,
    }


def run_benchmark():
    print("=" * 60)
    print("STANDARD GR BLACK HOLE BENCHMARK (COMPETITOR)")
    print("=" * 60)

    test_cases = [1.0, 10.0, 1e6, 4e6, 6.5e9]  # Sun, GW150914, SMBH, Sgr A*, M87*
    results = []

    for m in test_cases:
        res = calculate_gr_metrics(m)
        results.append(res)
        print(f"\n[Mass: {m:.1e} M_sun]")
        print(f"  Rs (Event Horizon): {res['Rs_m']:.2e} m")
        print(f"  Temp (Hawking):     {res['Temp_K']:.2e} K")
        print(f"  Life (Evaporation): {res['Life_Years']:.2e} Years")

    # Save
    result_dir = Path(__file__).parents[2] / "Result" / "04_Competitor"
    result_dir.mkdir(parents=True, exist_ok=True)
    output_path = result_dir / "results_GR_benchmark.csv"
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Benchmark saved to: {output_path}")


if __name__ == "__main__":
    run_benchmark()
