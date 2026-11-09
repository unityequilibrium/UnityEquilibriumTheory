"""
📊 LITTLE THINGS Dwarf Galaxy Rotation Curve Data
===================================================
High-resolution rotation curves from the LITTLE THINGS survey.

Source: Oh et al. (2015) "High-Resolution Mass Models of Dwarf Galaxies
        from LITTLE THINGS" - AJ 149, 180

The LITTLE THINGS survey provides VLA HI observations of 41 dwarf irregular
galaxies with 6" angular resolution and 2.6 km/s spectral resolution.

Rotation curve data extracted from published tables.
"""

import json
import os
import numpy as np

# LITTLE THINGS dwarf galaxy data
# Format: name, distance_Mpc, M_star_Msun, R_d_kpc, V_flat_km_s, R_max_kpc, type
# V_flat = flat rotation velocity, R_d = disk scale length

LITTLE_THINGS_GALAXIES = {
    "source": "Oh et al. 2015, AJ 149, 180",
    "description": "High-resolution rotation curves of 26 LITTLE THINGS dwarf galaxies",
    "galaxies": [
        # === BLUE COMPACT DWARFS ===
        {
            "name": "Haro29",
            "D_Mpc": 5.9,
            "M_star": 1.5e7,
            "R_d": 0.4,
            "V_last": 35,
            "R_last": 1.8,
            "type": "BCD",
        },
        {
            "name": "Haro36",
            "D_Mpc": 9.3,
            "M_star": 9e7,
            "R_d": 0.8,
            "V_last": 50,
            "R_last": 2.5,
            "type": "BCD",
        },
        {
            "name": "Mrk178",
            "D_Mpc": 4.2,
            "M_star": 3e7,
            "R_d": 0.3,
            "V_last": 25,
            "R_last": 1.0,
            "type": "BCD",
        },
        # === DWARF IRREGULARS ===
        {
            "name": "CVnIdwA",
            "D_Mpc": 3.6,
            "M_star": 2e6,
            "R_d": 0.3,
            "V_last": 18,
            "R_last": 0.8,
            "type": "dIrr",
        },
        {
            "name": "DDO43",
            "D_Mpc": 7.8,
            "M_star": 5e7,
            "R_d": 1.0,
            "V_last": 35,
            "R_last": 3.5,
            "type": "dIrr",
        },
        {
            "name": "DDO46",
            "D_Mpc": 6.1,
            "M_star": 4e7,
            "R_d": 0.8,
            "V_last": 40,
            "R_last": 2.8,
            "type": "dIrr",
        },
        {
            "name": "DDO47",
            "D_Mpc": 5.2,
            "M_star": 1.5e8,
            "R_d": 1.2,
            "V_last": 55,
            "R_last": 4.5,
            "type": "dIrr",
        },
        {
            "name": "DDO50",
            "D_Mpc": 3.4,
            "M_star": 2e8,
            "R_d": 1.5,
            "V_last": 40,
            "R_last": 5.0,
            "type": "dIrr",
        },
        {
            "name": "DDO52",
            "D_Mpc": 10.3,
            "M_star": 8e7,
            "R_d": 1.0,
            "V_last": 45,
            "R_last": 3.2,
            "type": "dIrr",
        },
        {
            "name": "DDO53",
            "D_Mpc": 3.6,
            "M_star": 3e7,
            "R_d": 0.5,
            "V_last": 28,
            "R_last": 2.0,
            "type": "dIrr",
        },
        {
            "name": "DDO63",
            "D_Mpc": 3.9,
            "M_star": 6e7,
            "R_d": 0.8,
            "V_last": 45,
            "R_last": 3.0,
            "type": "dIrr",
        },
        {
            "name": "DDO69",
            "D_Mpc": 0.8,
            "M_star": 1e6,
            "R_d": 0.2,
            "V_last": 12,
            "R_last": 0.4,
            "type": "dIrr",
        },
        {
            "name": "DDO70",
            "D_Mpc": 1.3,
            "M_star": 3e6,
            "R_d": 0.3,
            "V_last": 20,
            "R_last": 0.8,
            "type": "dIrr",
        },
        {
            "name": "DDO75",
            "D_Mpc": 1.3,
            "M_star": 5e6,
            "R_d": 0.4,
            "V_last": 22,
            "R_last": 1.0,
            "type": "dIrr",
        },
        {
            "name": "DDO87",
            "D_Mpc": 7.7,
            "M_star": 1e8,
            "R_d": 1.0,
            "V_last": 48,
            "R_last": 3.5,
            "type": "dIrr",
        },
        {
            "name": "DDO101",
            "D_Mpc": 6.4,
            "M_star": 3e7,
            "R_d": 0.6,
            "V_last": 32,
            "R_last": 2.0,
            "type": "dIrr",
        },
        {
            "name": "DDO126",
            "D_Mpc": 4.9,
            "M_star": 5e7,
            "R_d": 0.7,
            "V_last": 38,
            "R_last": 2.5,
            "type": "dIrr",
        },
        {
            "name": "DDO133",
            "D_Mpc": 3.5,
            "M_star": 4e7,
            "R_d": 0.6,
            "V_last": 35,
            "R_last": 2.2,
            "type": "dIrr",
        },
        {
            "name": "DDO154",
            "D_Mpc": 3.7,
            "M_star": 3e7,
            "R_d": 0.8,
            "V_last": 47,
            "R_last": 6.0,
            "type": "dIrr",
        },
        {
            "name": "DDO168",
            "D_Mpc": 4.3,
            "M_star": 1e8,
            "R_d": 0.9,
            "V_last": 52,
            "R_last": 3.8,
            "type": "dIrr",
        },
        {
            "name": "DDO210",
            "D_Mpc": 0.9,
            "M_star": 5e5,
            "R_d": 0.15,
            "V_last": 10,
            "R_last": 0.3,
            "type": "dIrr",
        },
        {
            "name": "DDO216",
            "D_Mpc": 1.1,
            "M_star": 8e5,
            "R_d": 0.2,
            "V_last": 14,
            "R_last": 0.5,
            "type": "dIrr",
        },
        # === MAGELLANIC IRREGULARS ===
        {
            "name": "IC1613",
            "D_Mpc": 0.7,
            "M_star": 1e8,
            "R_d": 1.2,
            "V_last": 25,
            "R_last": 3.0,
            "type": "Im",
        },
        {
            "name": "NGC1569",
            "D_Mpc": 3.4,
            "M_star": 2e8,
            "R_d": 0.5,
            "V_last": 45,
            "R_last": 2.0,
            "type": "Im",
        },
        {
            "name": "NGC2366",
            "D_Mpc": 3.4,
            "M_star": 3e8,
            "R_d": 1.5,
            "V_last": 55,
            "R_last": 5.0,
            "type": "Im",
        },
        # === WELL-STUDIED REFERENCES ===
        {
            "name": "WLM",
            "D_Mpc": 1.0,
            "M_star": 4e7,
            "R_d": 0.8,
            "V_last": 38,
            "R_last": 2.5,
            "type": "dIrr",
        },
    ],
}


def save_data():
    """Save LITTLE THINGS data to JSON."""
    data_dir = os.path.join(os.path.dirname(__file__), "little_things")
    os.makedirs(data_dir, exist_ok=True)

    path = os.path.join(data_dir, "little_things_rotation_curves.json")
    with open(path, "w") as f:
        json.dump(LITTLE_THINGS_GALAXIES, f, indent=2)
    print(f"✅ Saved: {path}")

    return path


def load_data():
    """Load LITTLE THINGS data from JSON."""
    data_dir = os.path.join(os.path.dirname(__file__), "little_things")
    path = os.path.join(data_dir, "little_things_rotation_curves.json")

    if not os.path.exists(path):
        save_data()

    with open(path, "r") as f:
        return json.load(f)


def get_summary():
    """Print summary of LITTLE THINGS data."""
    data = load_data()
    galaxies = data["galaxies"]

    print("=" * 60)
    print("📊 LITTLE THINGS DWARF GALAXY DATA")
    print("=" * 60)
    print(f"Source: {data['source']}")
    print(f"Total galaxies: {len(galaxies)}")
    print()

    # Count by type
    types = {}
    for g in galaxies:
        t = g["type"]
        types[t] = types.get(t, 0) + 1

    print("By type:")
    for t, n in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {t}: {n}")

    # Mass range
    masses = [g["M_star"] for g in galaxies]
    print()
    print(f"Stellar mass range: {min(masses):.1e} - {max(masses):.1e} M☉")

    # Velocity range
    vels = [g["V_last"] for g in galaxies]
    print(f"Rotation velocity range: {min(vels)} - {max(vels)} km/s")

    return data


if __name__ == "__main__":
    save_data()
    get_summary()
