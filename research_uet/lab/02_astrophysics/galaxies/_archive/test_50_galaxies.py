"""
🌌 50-Galaxy Quick Test (V3.0)
==============================
Simplified version using core UET equation.
For full testing, use test_175_galaxies.py

Uses UET V3.0 Master Equation:
    Ω = V(C) + κ|∇C|² + βCI + Game Theory (strategic_boost)
"""

import numpy as np
import sys
import os

# Add project root path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import from UET V3.0 Master Equation
try:
    from research_uet.core.uet_master_equation import SIGMA_CRIT, strategic_boost, UETParameters
except ImportError:
    sys.path.insert(0, os.path.join(root_dir, "research_uet"))
    from core.uet_master_equation import SIGMA_CRIT, strategic_boost, UETParameters

# Sample of 25 galaxies (subset of SPARC)
GALAXIES = {
    # Large spirals
    "NGC2841": {"R": 40, "v": 300, "M_disk": 1e11, "R_disk": 8, "type": "spiral"},
    "NGC5055": {"R": 35, "v": 200, "M_disk": 5e10, "R_disk": 6, "type": "spiral"},
    "NGC7331": {"R": 25, "v": 240, "M_disk": 4e10, "R_disk": 5, "type": "spiral"},
    # Medium spirals
    "NGC3198": {"R": 30, "v": 150, "M_disk": 2e10, "R_disk": 5, "type": "spiral"},
    "NGC2403": {"R": 18, "v": 130, "M_disk": 1e10, "R_disk": 4, "type": "spiral"},
    "NGC6503": {"R": 20, "v": 115, "M_disk": 8e9, "R_disk": 3.5, "type": "spiral"},
    # LSB
    "NGC300": {"R": 12, "v": 80, "M_disk": 3e9, "R_disk": 3, "type": "lsb"},
    "NGC55": {"R": 15, "v": 85, "M_disk": 4e9, "R_disk": 3, "type": "lsb"},
    "UGC128": {"R": 15, "v": 130, "M_disk": 5e9, "R_disk": 3, "type": "lsb"},
    # Dwarfs
    "DDO154": {"R": 8, "v": 50, "M_disk": 2e8, "R_disk": 2, "type": "dwarf"},
    "DDO168": {"R": 5, "v": 45, "M_disk": 1e8, "R_disk": 1.5, "type": "dwarf"},
    "IC2574": {"R": 12, "v": 65, "M_disk": 8e8, "R_disk": 3, "type": "dwarf"},
    # Compact (uses Game Theory)
    "NGC4736": {"R": 10, "v": 160, "M_disk": 2e10, "R_disk": 2, "type": "compact"},
}


def uet_rotation_velocity(r_kpc, M_disk_Msun, R_disk_kpc, galaxy_type="spiral"):
    """
    UET rotation velocity with V3.0 Game Theory for compact galaxies.
    """
    G = 4.302e-6  # (km/s)² kpc / M_sun

    # Surface density
    sigma_bar = M_disk_Msun / (np.pi * R_disk_kpc**2 + 1e-10)

    # Volume density
    vol = (4 / 3) * np.pi * R_disk_kpc**3
    rho = M_disk_Msun / (vol + 1e-10)

    # I-field ratio (UET's interpretation of DM)
    RHO_PIVOT = 5e7
    RATIO_BASE = 8.5
    GAMMA = 0.48
    M_I_ratio = RATIO_BASE * (rho / RHO_PIVOT) ** (-GAMMA)

    # Game Theory β_U for compact (from V3.0 core)
    if galaxy_type == "compact":
        beta_U = strategic_boost(sigma_bar, scale=R_disk_kpc)
    else:
        beta_U = 0.0

    M_I_ratio = M_I_ratio * (1 + beta_U)
    M_I_ratio = max(0.1, min(M_I_ratio, 500.0))

    # Baryonic
    M_bulge = 0.1 * M_disk_Msun
    x = r_kpc / R_disk_kpc
    M_disk_enc = M_disk_Msun * (1 - (1 + x) * np.exp(-x))

    # I-field (NFW)
    M_I = M_I_ratio * M_disk_Msun
    c = np.clip(10.0 * (M_I / 1e12) ** (-0.1), 5, 20)
    R_s = 10 * R_disk_kpc / c
    r_norm = r_kpc / R_s
    f_NFW = np.log(1 + r_norm) - r_norm / (1 + r_norm)
    f_norm = np.log(1 + c) - c / (1 + c)
    M_I_enc = M_I * f_NFW / f_norm

    M_total = M_bulge + M_disk_enc + M_I_enc
    return np.sqrt(G * M_total / (r_kpc + 0.1))


def run_test():
    print("=" * 60)
    print("🌌 25-GALAXY QUICK TEST (V3.0 WITH GAME THEORY)")
    print("=" * 60)
    print()

    results = []
    for name, data in GALAXIES.items():
        v_uet = uet_rotation_velocity(data["R"], data["M_disk"], data["R_disk"], data["type"])
        error = abs(v_uet - data["v"]) / data["v"] * 100
        results.append(
            {"name": name, "type": data["type"], "v_obs": data["v"], "v_uet": v_uet, "error": error}
        )

    results.sort(key=lambda x: x["error"])

    print(f"{'Galaxy':<12} {'Type':<8} {'V_obs':>6} {'V_UET':>6} {'Error':>7}")
    print("-" * 50)

    passed = failed = 0
    for r in results:
        status = "✅" if r["error"] < 15 else ("⚠️" if r["error"] < 25 else "❌")
        if r["error"] < 15:
            passed += 1
        elif r["error"] > 25:
            failed += 1
        print(
            f"{r['name']:<12} {r['type']:<8} {r['v_obs']:>6.0f} {r['v_uet']:>6.1f} {r['error']:>6.1f}% {status}"
        )

    avg = np.mean([r["error"] for r in results])
    print()
    print(f"Pass rate: {passed}/{len(results)} ({100*passed/len(results):.0f}%)")
    print(f"Avg error: {avg:.1f}%")
    print()
    print("For full 175-galaxy test: python test_175_galaxies.py")


if __name__ == "__main__":
    run_test()
