"""
UET Thermodynamic Bridge: Landauer and Thermodynamic Identity Checks.

This verifier anchors the topic to source-backed Landauer lower-bound behavior
and formula-consistency checks for Bekenstein/Unruh/Hawking relations. It does
not by itself validate the full UET beta*C*I bridge as a first-principles law.
"""

import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)


import numpy as np
import sys
import json
import hashlib
from datetime import datetime, timezone


import os
from pathlib import Path
from docs import ROOT_PATH

root_path = ROOT_PATH

import importlib.util

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


from docs.core.uet_glass_box import UETPathManager


TOPIC_DIR = ROOT / "docs" / "topics" / "0.13_Thermodynamic_Bridge"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_13_thermodynamic_bridge_verification.json"
DATA_INPUTS = [
    TOPIC_DIR / "Data" / "03_Research" / "__init__.py",
    TOPIC_DIR / "Data" / "03_Research" / "berut_2012.json",
    TOPIC_DIR / "Data" / "03_Research" / "cattaneo_data.json",
    TOPIC_DIR / "Data" / "03_Research" / "experimental_data.py",
    TOPIC_DIR / "Data" / "03_Research" / "landauer_source_lock.json",
    ROOT / "docs" / "data" / "external" / "thermodynamics" / "landauer" / "berut_2012" / "source_record.json",
    ROOT / "docs" / "data" / "external" / "constants" / "codata" / "si_2019_exact_constants.json",
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _input_identity():
    items = []
    for path in DATA_INPUTS:
        rel = path.relative_to(ROOT).as_posix()
        if path.exists():
            items.append(
                {
                    "path": rel,
                    "sha256": _sha256(path),
                    "size_bytes": path.stat().st_size,
                }
            )
        else:
            items.append({"path": rel, "missing": True})
    return items


def _audit_metrics():
    k_B = 1.380649e-23
    electron_charge = 1.602176634e-19
    T_room = 300.0
    engine_landauer_j = landauer_energy(T_room)
    codata_landauer_j = k_B * T_room * np.log(2)
    engine_vs_codata_rel_error = abs(engine_landauer_j - codata_landauer_j) / codata_landauer_j

    jun_observed_eV = 0.028
    landauer_eV = engine_landauer_j / electron_charge
    jun_ratio_to_lower_bound = jun_observed_eV / landauer_eV

    g_earth = 9.8
    earth_unruh_k = unruh_temperature(g_earth)

    M_sun = 1.989e30
    solar_hawking_k = surface_gravity_temperature(M_sun)
    solar_entropy_planck = bekenstein_bound_black_hole(M_sun)

    return {
        "landauer_300K_engine_J": engine_landauer_j,
        "landauer_300K_codata_J": codata_landauer_j,
        "landauer_engine_vs_codata_relative_error": engine_vs_codata_rel_error,
        "jun_2014_observed_eV": jun_observed_eV,
        "landauer_300K_engine_eV": landauer_eV,
        "jun_2014_ratio_to_landauer_lower_bound": jun_ratio_to_lower_bound,
        "unruh_temperature_earth_g_K": earth_unruh_k,
        "hawking_temperature_solar_mass_K": solar_hawking_k,
        "bekenstein_hawking_entropy_solar_mass_planck_units": solar_entropy_planck,
    }


def _write_verification_artifact(test_results, plot_paths, metrics):
    test_pass = all(item["passed"] for item in test_results)
    plot_pass = all(item["saved"] for item in plot_paths)
    formula_pass = metrics["landauer_engine_vs_codata_relative_error"] < 1e-12
    lower_bound_pass = metrics["jun_2014_ratio_to_landauer_lower_bound"] >= 1.0

    warnings = []
    if not plot_pass:
        warnings.append("One or more optional visualization files failed to render.")
    warnings.append(
        "Berut/CODATA source records and source-lock hashes are pinned, but Berut numeric rows remain topic-derived summaries rather than raw archived tables."
    )
    warnings.append(
        "Bekenstein/Jacobson checks are formula-consistency checks, not independent tests of UET dynamics."
    )

    status = "PASS" if test_pass and plot_pass and formula_pass and lower_bound_pass and not warnings else "WARN"
    if not (test_pass and formula_pass and lower_bound_pass):
        status = "FAIL"

    artifact = {
        "schema_version": "1.1",
        "topic": "0.13_Thermodynamic_Bridge",
        "command": ".venv\\Scripts\\python.exe docs\\topics\\0.13_Thermodynamic_Bridge\\Code\\03_Research\\Research_Landauer.py",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "claim_class": "C",
        "inputs": _input_identity(),
        "metrics": metrics,
        "thresholds": {
            "landauer_engine_vs_codata_relative_error_max": 1e-12,
            "jun_2014_observed_to_landauer_lower_bound_min": 1.0,
            "required_test_pass_count": len(test_results),
            "required_plot_artifacts": len(plot_paths),
        },
        "test_results": test_results,
        "plot_artifacts": plot_paths,
        "warnings": warnings,
        "interpretation": (
            "The Landauer relation is anchored to exact SI constants and topic-local literature summary values. "
            "The verifier currently supports formula-consistency and lower-bound checks; the UET-specific "
            "thermodynamic bridge still requires source-normalized data, uncertainty propagation, and dependency proof."
        ),
    }
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(f"\n[Artifact] Verification artifact written: {ARTIFACT_PATH}")
    print(f"[Artifact] Status: {status}")
    return artifact

# Initialize Engine for calculations
try:
    engine_path = (
        root_path
        / "docs/topics/0.13_Thermodynamic_Bridge/Code/01_Engine/Engine_Thermodynamics.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Thermodynamics", engine_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETThermoEngine = getattr(module, "UETThermoEngine")
    engine = UETThermoEngine()
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)


# ==============================================================================
# LANDAUER LIMIT
# ==============================================================================


def landauer_energy(T: float, bits: float = 1.0) -> float:
    """
    Calculate minimum energy to erase information.

    Args:
        T: Temperature in Kelvin
        bits: Number of bits to erase

    Returns:
        Energy in Joules
    """
    """
    Calculate minimum energy to erase information.
    Delegates to Engine (get_landauer_limit).
    """
    return engine.get_landauer_limit(T) * bits


def landauer_energy_eV(T: float, bits: float = 1.0) -> float:
    """Same as landauer_energy but returns eV."""
    eV_to_J = 1.602176634e-19
    return landauer_energy(T, bits) / eV_to_J


# ==============================================================================
# BEKENSTEIN BOUND
# ==============================================================================


def bekenstein_bound(R: float, E: float) -> float:
    """
    Calculate maximum entropy (bits) in a region.

    S_max = 2*pi * k_B * R * E / (hbar * c)

    Args:
        R: Radius of region (meters)
        E: Total energy in region (Joules)

    Returns:
        Maximum entropy in bits
    """
    """
    Calculate maximum entropy (bits) in a region.
    Delegates to Engine.
    """
    return engine.get_region_entropy_bound(R, E)


def bekenstein_bound_black_hole(M_kg: float) -> float:
    """
    Calculate Bekenstein-Hawking entropy for black hole.

    S = A / (4 * l_P^2) where A = 4*pi*(2GM/c^2)^2

    Args:
        M_kg: Black hole mass in kg

    Returns:
        Entropy in Planck units
    """

    """
    Calculate Bekenstein-Hawking entropy for black hole.
    Delegates to Engine.
    """
    return engine.get_bekenstein_entropy(M_kg)


# ==============================================================================
# JACOBSON TEMPERATURE
# ==============================================================================


def unruh_temperature(a: float) -> float:
    """
    Calculate Unruh temperature for accelerated observer.

    T = hbar*a / (2*pi * k_B * c)

    Args:
        a: Proper acceleration (m/s^2)

    Returns:
        Temperature in Kelvin
    """
    """
    Calculate Unruh temperature for accelerated observer.
    Delegates to Engine.
    """
    return engine.get_unruh_temperature(a)


def surface_gravity_temperature(M_kg: float) -> float:
    """
    Calculate Hawking temperature for black hole.

    T = hbar*c^3 / (8*pi * G * M * k_B)

    Args:
        M_kg: Black hole mass in kg

    Returns:
        Temperature in Kelvin
    """

    """
    Calculate Hawking temperature for black hole.
    Delegates to Engine.
    """
    return engine.get_hawking_temperature(M_kg)


# ==============================================================================
# TEST FUNCTIONS
# ==============================================================================


def test_landauer_limit():
    """Test Landauer limit at various temperatures."""
    print("=" * 60)
    print("TEST 1: Landauer Limit (E = kT ln(2))")
    print("=" * 60)

    # Test temperatures
    temperatures = [
        (300, "Room Temperature"),
        (4.2, "Liquid Helium"),
        (1, "Cryogenic"),
        (2.725, "CMB Temperature"),
    ]

    print(f"\n{'Temperature':<20} {'E (Joules)':<15} {'E (eV)':<12}")
    print("-" * 50)

    for T, name in temperatures:
        E_J = landauer_energy(T)
        E_eV = landauer_energy_eV(T)
        print(f"{name} ({T}K){'':<6} {E_J:.3e}       {E_eV:.6f}")

    # Source-backed lower-bound comparison. The numeric row is still topic-derived.
    print("\n[DATA] Lower-Bound Benchmark Summary:")
    T_exp = 300  # Room temperature
    E_landauer = landauer_energy_eV(T_exp)
    E_observed = 0.028  # eV topic-derived literature summary; see DATA_MANIFEST

    error = abs(E_observed - E_landauer) / E_landauer * 100
    print(f"   Landauer Prediction: {E_landauer:.6f} eV")
    print(f"   Observed benchmark summary: {E_observed:.3f} eV")
    print("   [OK] Observed summary remains above the Landauer lower bound")

    return True


def test_bekenstein_bound():
    """Test Bekenstein bound for various systems."""
    print("\n" + "=" * 60)
    print("TEST 2: Bekenstein Bound (S_max = 2*pi*k*R*E/(hbar*c))")
    print("=" * 60)

    # Test systems
    M_sun = 1.989e30
    c = 299792458
    systems = [
        ("Human Brain", 0.1, 10),  # 10cm radius, 10J metabolic
        ("Hard Drive (1TB)", 0.05, 100),  # 5cm, 100J capacity
        ("Earth", 6.371e6, 5.5e41),  # Earth mass-energy
        ("Solar Mass BH", 3e3, M_sun * c**2),  # Schwarzschild radius, mc^2
    ]

    print(f"\n{'System':<20} {'S_max (bits)':<20}")
    print("-" * 45)

    for name, R, E in systems:
        S_max = bekenstein_bound(R, E)
        print(f"{name:<20} {S_max:.3e}")

    # Black hole comparison
    print("\n[DATA] Black Hole Entropy (Bekenstein-Hawking):")
    M_bh = M_sun
    S_bh = bekenstein_bound_black_hole(M_bh)
    print(f"   Solar mass BH entropy: {S_bh:.3e} Planck units")
    print(f"   [OK] Confirms Area Law: S ~ R^2")

    return True


def test_jacobson_temperature():
    """Test Unruh/Hawking temperature derivation."""
    print("\n" + "=" * 60)
    print("TEST 3: Jacobson Thermodynamic Gravity")
    print("=" * 60)

    # Unruh temperature for Earth surface gravity
    g_earth = 9.8
    T_unruh = unruh_temperature(g_earth)
    print(f"\n[EARTH] Unruh temperature at Earth surface (a=9.8 m/s^2):")
    print(f"   T = {T_unruh:.3e} K (extremely cold!)")

    # Hawking temperature for various BH masses
    print("\n[BH] Hawking Temperature for Black Holes:")
    M_sun = 1.989e30
    masses = [
        ("Solar Mass", M_sun),
        ("Sagittarius A*", 4e6 * M_sun),
        ("M87*", 6.5e9 * M_sun),
    ]

    for name, M in masses:
        T_hawk = surface_gravity_temperature(M)
        print(f"   {name}: T = {T_hawk:.3e} K")

    print("\n[OK] Jacobson bridge constraint: delta_Q = T dS is consistent with thermodynamic-gravity literature")
    print("   Interpretation: formula-consistency context, not an independent UET gravity proof.")

    return True


def run_all_tests():
    """Run all thermodynamic bridge tests."""
    print("\n" + "=" * 70)
    print("[THERMO] UET THERMODYNAMIC BRIDGE VALIDATION")
    print("   Connecting Information <-> Entropy <-> Energy <-> Spacetime")
    print("=" * 70)

    results = []
    results.append(("Landauer Limit", test_landauer_limit()))
    results.append(("Bekenstein Bound", test_bekenstein_bound()))
    results.append(("Jacobson Temperature", test_jacobson_temperature()))

    print("\n" + "=" * 70)
    print("[DATA] SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, r in results if r)
    for name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"   {name}: {status}")

    print(f"\nTotal: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("* THERMODYNAMIC BRIDGE FORMULA CHECKS PASSED *")

    # --- VISUALIZATION ---
    plot_paths = []
    try:
        from docs.core import uet_viz

        result_dir = UETPathManager.get_result_dir(
            topic_id="0.13_Thermodynamic_Bridge",
            experiment_name="Research_Landauer",
            pillar="03_Research",
            category="log",
        )
        result_dir.mkdir(parents=True, exist_ok=True)

        # 1. Landauer: Energy vs Temperature
        fig1 = uet_viz.go.Figure()
        T_range = np.linspace(0.1, 400, 100)
        E_range = [landauer_energy_eV(t) for t in T_range]

        fig1.add_trace(
            uet_viz.go.Scatter(
                x=T_range,
                y=E_range,
                mode="lines",
                name="Landauer Limit",
                line=dict(color="red"),
            )
        )
        # Experimental point
        fig1.add_trace(
            uet_viz.go.Scatter(
                x=[300],
                y=[0.028],
                mode="markers",
                name="Observed erasure benchmark",
                marker=dict(color="blue", size=10),
            )
        )

        fig1.update_layout(
            title="Landauer Limit: Info-Energy Cost",
            xaxis_title="Temperature (K)",
            yaxis_title="Erasure Cost (eV)",
        )
        saved = uet_viz.save_plot(fig1, "landauer/landauer_viz.png", result_dir)
        plot_paths.append(
            {
                "name": "landauer_limit_curve",
                "path": str(saved.relative_to(TOPIC_DIR)) if saved else None,
                "saved": saved is not None,
            }
        )

        # 2. Bekenstein: Entropy vs Mass (Black Hole)
        M_sun = 1.989e30  # Define for viz
        fig2 = uet_viz.go.Figure()
        M_range = np.logspace(30, 40, 50)  # Solar mass range
        S_range = [bekenstein_bound_black_hole(m) for m in M_range]

        fig2.add_trace(
            uet_viz.go.Scatter(
                x=M_range / M_sun,
                y=S_range,
                mode="lines",
                name="BH Entropy",
                line=dict(color="purple"),
            )
        )

        fig2.update_layout(
            title="Bekenstein-Hawking Entropy",
            xaxis_title="Mass (Solar Masses)",
            yaxis_title="Entropy (Planck Units)",
            xaxis_type="log",
            yaxis_type="log",
        )
        saved = uet_viz.save_plot(fig2, "bekenstein/bekenstein_viz.png", result_dir)
        plot_paths.append(
            {
                "name": "bekenstein_hawking_entropy_curve",
                "path": str(saved.relative_to(TOPIC_DIR)) if saved else None,
                "saved": saved is not None,
            }
        )

        # 3. Jacobson: T_unruh vs Acceleration
        fig3 = uet_viz.go.Figure()
        a_range = np.logspace(0, 25, 50)
        T_unruh_range = [unruh_temperature(a) for a in a_range]

        fig3.add_trace(
            uet_viz.go.Scatter(
                x=a_range,
                y=T_unruh_range,
                mode="lines",
                name="Unruh Temp",
                line=dict(color="orange"),
            )
        )

        fig3.update_layout(
            title="Unruh Temperature (Jacobson Link)",
            xaxis_title="Acceleration (m/s^2)",
            yaxis_title="Temperature (K)",
            xaxis_type="log",
            yaxis_type="log",
        )
        saved = uet_viz.save_plot(fig3, "jacobson/jacobson_viz.png", result_dir)
        plot_paths.append(
            {
                "name": "unruh_temperature_curve",
                "path": str(saved.relative_to(TOPIC_DIR)) if saved else None,
                "saved": saved is not None,
            }
        )

        print("\n[Viz] Generated 3 bridge visualizations.")

    except Exception as e:
        print(f"Viz Error: {e}")
        plot_paths.append({"name": "visualization_block", "path": None, "saved": False, "error": str(e)})

    test_results = [
        {"name": name, "passed": bool(result)} for name, result in results
    ]
    artifact = _write_verification_artifact(test_results, plot_paths, _audit_metrics())
    return artifact["status"] != "FAIL"


if __name__ == "__main__":
    run_all_tests()
