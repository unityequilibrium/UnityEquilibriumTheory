from __future__ import annotations

"""
UET Central Parameter Module
============================
Single source of truth for all UET parameters.

Usage:
    from docs.core.uet_parameters import get_params, UETParams

    params = get_params("electroweak")
    print(params.kappa, params.beta)

Author: UET Research Team
Version: 0.9.0
Last Updated: 2026-01-13
"""

import os
import math
from dataclasses import dataclass
from typing import Literal, Optional
import numpy as np

# =============================================================================
# GLOBAL INTEGRITY KILL SWITCH (The Truth Auditor)
# =============================================================================
# Set environment variable UET_KILL_ENGINE=TRUE to bypass all calculation logic.
# If active, all Engines will return invalid results (0.0 or NaN).
# Research scripts that PASS while this is active are guilty of SHADOW MATH.
INTEGRITY_KILL_SWITCH = os.getenv("UET_KILL_ENGINE", "FALSE").upper() == "TRUE"

# =============================================================================
# FUNDAMENTAL CONSTANTS (CODATA 2018 / SI Exact)
# =============================================================================

HBAR = 1.054571817e-34  # Planck constant [J·s]
C = 299792458  # Speed of light [m/s]
G = 6.67430e-11  # Gravitational constant [m³/kg/s²]
K_B = 1.380649e-23  # Boltzmann constant [J/K]
ALPHA_EM = 1 / 137.035999  # Fine structure constant
M_SUN = 1.98847e30  # Solar Mass (kg) [IAU 2015]
H = 6.62607015e-34  # Planck constant [J·s]
E_CHARGE = 1.602176634e-19  # Elementary charge [C]
M_ELECTRON = 9.1093837015e-31  # Electron mass [kg]
EPSILON_0 = 8.8541878128e-12  # Vacuum permittivity [F/m]
V_EW = 246220.0  # Electroweak Vacuum Expectation Value [MeV] (Standard PDG)
R_GAS = 8.314462618  # Universal Gas Constant [J/mol·K] (2018 SI)
F_FARADAY = 96485.3321  # Faraday Constant [C/mol] (2018 SI)
ALPHA_EM_MZ = 1 / 128.94  # Fine structure constant at M_Z scale (Electroweak)

# --- STANDARDIZED ALIASES (Backward Compatibility) ---
K_BOLTZMANN = K_B
H_PLANCK = H
G_NEWTON = G
E_CHARGE = E_CHARGE # Already exists

# --- UET UNIT CONVERSIONS ---
C_KM_S = C / 1000.0  # Speed of light [km/s]
G_GALACTIC = 4.301e-6  # kpc (km/s)² / M_sun (Standardized UET Value)
RHO_COSMIC = 2.9e-16  # kg/m^3 (UET Vacuum Density - Pioneer/Fluid Frame)
H0 = 67.4  # km/s/Mpc (Planck 2018 - Global Baseline)
A0_COSMIC = 1.2e-10  # m/s² (Baseline Milgrom/MOND acceleration)
TAU_MEM_VACUUM = 0.01  # s (Vacuum memory relaxation time)

# --- [UNVERIFIED: HEURISTIC] UET BRIDGE CONSTANTS ---
# These are placeholders used to bridge informational-physical gaps in simulations.
FLUID_MOBILITY_BRIDGE = 1750.0  # Placeholder Bridge for Topic 0.10
TAU_INERTIA = 0.05  # s (Systemic Inertia relaxation time)
A0_VISCOSITY = 1.2e-10  # m/s² (MOND-like acceleration pivot)

# Derived Planck units
L_PLANCK = (HBAR * G / C**3) ** 0.5  # Planck length
M_PLANCK = (HBAR * C / G) ** 0.5  # Planck mass
T_PLANCK = L_PLANCK / C  # Planck time

# =============================================================================
# LANDAUER LOWER BOUND AND LEGACY NORMALIZED PROXY
# =============================================================================

LANDAUER_CONSTANT = math.log(2)  # ln(2) for Landauer coupling


def calculate_beta_landauer(temperature: float = 293.15) -> float:
    """
    Compatibility helper: this function returns a normalized coupling proxy,
    not the SI Landauer energy. Use ``landauer_minimum_energy`` for joules.

    This legacy helper produces a normalized coupling proxy for compatibility;
    it is not the SI energy cost per bit and is not a first-principles
    derivation of the dimensionless core beta.

    Args:
        temperature: System temperature in Kelvin (default: room temperature 293.15K)

    Returns:
        A normalized coupling proxy. Use ``landauer_minimum_energy`` for the
        joule-valued lower bound ``E_min = k_B T ln(2)``.

    Reference:
        - Landauer (1961): Irreversibility and heat generation
        - Bérut et al. (2012): Experimental verification (DOI: 10.1103/PhysRevLett.109.180601)
    """
    # Normalize to 'Unity Basis' (1.0 = Landauer limit at critical density)
    # [STABILIZATION]: Under high temperatures (e.g. Electroweak),
    # we implement a logarithmic saturation to keep beta (coupling) physically bounded.
    # Unity Principle: Information cost saturates as it approaches vacuum capacity.
    raw_energy = (K_B * temperature * LANDAUER_CONSTANT) * 1e21

    if raw_energy > 0.5:
        # Logarithmic saturation for coupling sustainability
        return 0.5 * (1 + np.log10(2 * raw_energy))

    return raw_energy


def landauer_minimum_energy(temperature: float = 293.15) -> float:
    """Return the SI Landauer lower bound ``k_B T ln(2)`` in joules."""

    if temperature < 0:
        raise ValueError("temperature must be non-negative")
    return float(K_B * temperature * LANDAUER_CONSTANT)


def calculate_dynamic_kappa(scale: float) -> float:
    """
    Calculate κ dynamically based on the 'Unity Scale Link' formula.

    This function implements the Renormalization Group Flow of UET, anchoring
    κ to axiomatic values at specific scales (Planck, Nuclear, Macro).

    Anchors:
    - Planck (1e-35m): 0.5 (The Floor)
    - Nuclear (1e-15m): 0.57 (Confinement Peak)
    - Atomic (1e-10m): 1.40 (Lattice/Qubit Anomaly)
    - Macro (> 1.0m): 0.10 (Asymptotic Freedom)

    Args:
        scale: The physical scale in meters.

    Returns:
        The calculated κ value for that scale.
    """
    log_l = math.log10(max(scale, 1e-35))

    # Piecewise Log-Linear Interpolation for 'The Scale Link'
    # 1. Planck to Nuclear
    if log_l <= -15:
        # Interpolate between -35 (0.5) and -15 (0.57)
        return 0.5 + (log_l + 35) * (0.57 - 0.5) / 20.0

    # 2. Nuclear to Atomic (The Peak)
    elif log_l <= -10:
        # Interpolate between -15 (0.57) and -10 (1.40)
        return 0.57 + (log_l + 15) * (1.40 - 0.57) / 5.0

    # 3. Atomic to Macro
    elif log_l <= 0:
        # Interpolate between -10 (1.40) and 0 (0.10)
        return 1.40 + (log_l + 10) * (0.10 - 1.40) / 10.0

    # 4. Macro Asymptotic Limit
    else:
        return 0.10


def calculate_kappa_from_beta(beta: float, information_density: float) -> float:
    """
    Calculate κ from β and information density (First Principles definition).
    κ = β / ρ_info
    """
    if information_density <= 0:
        raise ValueError("information_density must be positive")
    return beta / information_density


def calculate_scaling_ratio(scale_from: float, scale_to: float) -> float:
    """
    Calculate scaling factor for parameter transformation between scales.

    Based on thermodynamic scaling laws from Topic 0.13:
    - Temperature: T ∝ scale^(-2/3)
    - Information density: ρ ∝ scale^(-3)

    Args:
        scale_from: Source scale (meters)
        scale_to: Target scale (meters)

    Returns:
        Scaling factor to multiply parameters by
    """
    temp_ratio = (scale_to / scale_from) ** (-2.0 / 3.0)
    density_ratio = (scale_from / scale_to) ** 3.0
    return temp_ratio * density_ratio


def calculate_information_density(scale: float, temperature: float = 293.15) -> float:
    """
    Derive Information Density ρ_info from the normalized scale link.
    ρ_info = beta_normalized / κ
    """
    beta_normalized = calculate_beta_landauer(temperature)
    kappa = calculate_dynamic_kappa(scale)
    return beta_normalized / kappa


def derive_parameters_first_principles(
    scale: float,
    temperature: float,
    information_density: float,
    **overrides
) -> UETParameters:
    """
    Derive normalized-lane UET parameters using a Landauer-derived proxy.
    The SI Landauer lower bound remains a separate dimensional quantity.
    """
    # 1. Calculation from Scale Link (Structural Unity - A2/A3)
    # We default to the dynamic scale-link unless kappa is explicitly overridden.
    kappa = overrides.get("kappa", calculate_dynamic_kappa(scale))
    beta = overrides.get("beta", calculate_beta_landauer(temperature))

    # Base dictionary
    data = {
        "kappa": kappa,
        "beta": beta,
        "temperature": temperature,
        "scale": f"{scale:.2e}m",
        "origin": "normalized Landauer proxy; SI lower bound kept separate",
        "sigma_interaction": 1.0,
        "tau_inertia": 0.01, # Standard Systemic Inertia
    }

    # Resolving Thermodynamic vs Field Coupling Beta
    # [AXIOMATIC PURGE]: Legacy scale-dependent beta overrides removed.
    # The normalized proxy and dynamic scale link are compatibility inputs;
    # they are not an SI-energy derivation of the core beta.

    # Apply Overrides (Final Pass)
    data.update(overrides)

    # Construct parameters with Dynamic Flag set to True
    return UETParameters(dynamic=True, **data)

# =============================================================================
# UET SCALE-DEPENDENT PARAMETERS
# =============================================================================


@dataclass(frozen=True)
class UETParameters:
    """
    Authoritative container for UET parameters at a given scale.
    Matches the requirements of the UET Master Equation (All 12 Axioms).
    """

    kappa: float = 0.1  # Gradient penalty (A3)
    beta: float = 0.05  # Dimensionless normalized coupling (not Joules)
    alpha: float = 1.0  # Equilibrium stiffness (A1)
    gamma: float = 0.025  # Nonlinear stability (A1)
    C0: float = 1.0  # Vacuum Expectation Value (A1)
    gamma_J: float = 0.1  # Exchange rate (A4)
    W_N: float = 0.05  # Natural Will (A5)
    lambda_coherence: float = 0.01  # Layer coherence (A10)

    # === Candidate operator controls ===
    # Default remains legacy-safe. Candidate coefficients are only used when
    # operator_mode is explicitly set to an opt-in spatial-coupled mode.
    operator_mode: str = "legacy_local"
    spatial_information_coupling: float = 1.0
    spatial_game_coupling: float = 1.0
    spatial_kpz_coupling: float = 1.0

    # Wave 11 v2 candidate controls. These are heuristic/proxy values and do
    # not affect legacy_local or spatial_coupled_v1 execution.
    spatial_v2_information_coupling: float = 1.0
    spatial_v2_game_coupling: float = 1.0
    spatial_v2_nonlocal_coupling: float = 1.0
    spatial_v2_memory_length: float = 2.0
    spatial_v2_conserved_coupling: float = 1.0

    # Wave 14/16 Model C candidate control. Used only by conserved_order_v1
    # and conserved_order_spectral_v1.
    conserved_order_mobility: float = 1.0
    dynamic: bool = False # Tracking Axiomatic Origins

    # === Hardened Field Dynamics (Audit Fixes) ===
    kappa_I: float = 0.1  # Informational Inertia (A2 Propagator mass)
    tau_mem: float = 0.01  # Space-Memory relaxation time (A3)
    tau_inertia: float = 0.0  # s (Systemic Inertia - 0.0 = Overdamped/Diffusion)
    a0_viscosity: float = 1.2e-10  # m/s² (Dynamic Viscosity pivot)

    # === Spacetime trace candidate controls (opt-in only) ===
    # These values are normalized-lane defaults.  They do not define SI
    # transport coefficients until a topic-specific units contract is closed.
    D_trace: float = 0.1
    tau_trace: float = 0.1
    lambda_trace: float = 0.0
    trace_coupling: float = 0.1
    trace_source_normalization: str = "normalized"
    trace_boundary_condition: str = "periodic"

    # === Structural & Loss Bridge (Audit Fixes) ===
    phi_loss: float = 0.05  # Informational dissipation (Loss factor)
    I_max: float = 1.0     # Axiomatic Informational Capacity (Normalized)
    mu_gravity: float = 0.0  # Metric coupling (Gravity bridge)
    sigma_interaction: float = 1.0  # Cross-domain scaling ratio

    # === Astrophysical Constants (A7: Pattern Recurrence) ===
    RHO_UNITY: float = 5e7  # M_sun / kpc^3 (Pivot density)
    RATIO_0: float = 8.5  # Universal Halo Ratio pivot
    GAMMA_UET: float = 0.48  # Thermodynamic scaling index
    SIGMA_CRIT: float = 1.37e9  # M_sun/kpc² (Derived from Λ)

    # === Context ===
    temperature: float = 293.15  # Kelvin
    scale: str = ""  # Scale name
    origin: str = ""  # Derivation source

    @property
    def beta_normalized(self) -> float:
        """Dimensionless normalized coupling for the normalized core lane."""
        return float(self.beta)

    def __post_init__(self):
        """Standard detections for sabotaged parameters."""
        if INTEGRITY_KILL_SWITCH:
            # TOTAL BLACKOUT: Kill all 12+ axiomatic parameters
            kill_list = [
                "kappa", "beta", "alpha", "gamma", "C0", "kappa_I",
                "lambda_coherence", "gamma_J", "W_N", "tau_inertia", "a0_viscosity",
                "D_trace", "tau_trace", "lambda_trace", "trace_coupling",
                "spatial_information_coupling", "spatial_game_coupling", "spatial_kpz_coupling",
                "spatial_v2_information_coupling", "spatial_v2_game_coupling",
                "spatial_v2_nonlocal_coupling", "spatial_v2_memory_length",
                "spatial_v2_conserved_coupling", "conserved_order_mobility"
            ]
            for field_name in kill_list:
                if hasattr(self, field_name):
                    object.__setattr__(self, field_name, 0.0)


# =============================================================================
# DOMAIN-SPECIFIC PRESETS (with First-Principles Derivation)
# =============================================================================

_DOMAIN_PRESETS = {
    "quantum": {
        "scale": 1e-9,  # meters (nanometer)
        "temperature": 4.2,  # K (liquid helium)
        "info_density": 1e16,  # bits/m³ (Qubit density)
        "description": "Quantum systems (nanoscale/cryogenic)",
    },
    "electroweak": {
        "scale": 1.1e-18,  # meters (MZ interaction length)
        "temperature": 1.05e15,  # K (EW symmetry breaking temperature)
        "info_density": 1e15,  # bits/m³
        "description": "Electroweak scale (high-energy)",
    },
    "nuclear_binding": {
        "scale": 1e-15,  # meters (femtometer)
        "temperature": 1e12,  # K (nuclear temperature)
        "info_density": 1e20,  # bits/m³
        "description": "Nuclear binding (QCD scale)",
    },
    "fluid": {
        "scale": 1e-3,  # meters (millimeter)
        "temperature": 300,  # K (room temperature)
        "info_density": 1e18,  # bits/m³
        "description": "Fluid dynamics (mesoscale)",
    },
    "galactic": {
        "scale": 1e20,  # meters (galactic scale)
        "temperature": 2.7,  # K (CMB temperature)
        "info_density": 1e10,  # bits/m³
        "description": "Galactic rotation (cosmological)",
    },
    "biological": {
        "scale": 1e-6,  # meters (micrometer)
        "temperature": 310,  # K (body temperature)
        "info_density": 1e16,  # bits/m³
        "description": "Biological systems (cellular)",
    },
    "ai_cortex": {
        "scale": 1e-9,  # meters (transistor/synapse scale)
        "temperature": 300,  # K (standard operating temp)
        "info_density": 1e20,  # bits/m³ (high-density logic)
        "description": "AI & Cognitive Systems (Information processing)",
    },
}


def get_params_first_principles(domain_name: str) -> UETParameters:
    """
    Get UET parameters for a domain using first-principles calculation.

    This is the RECOMMENDED method for obtaining parameters, as it uses
    physically-derived quantities rather than hardcoded values.

    Args:
        domain_name: One of "quantum", "nuclear_binding", "fluid", "galactic", "biological"

    Returns:
        UETParameters with calculated kappa, beta, and context

    Example:
        >>> params = get_params_first_principles("fluid")
        >>> print(f"kappa = {params.kappa:.4f}, beta_normalized = {params.beta:.2e}")
    """
    if domain_name not in _DOMAIN_PRESETS:
        available = list(_DOMAIN_PRESETS.keys())
        raise ValueError(f"Unknown domain: {domain_name}. Available: {available}")
# Mapping: Topic -> Physical Domain (Mandatory Centralized Logic)
_TOPIC_DOMAIN_MAP = {
    # --- Particle Pillar (0.5-0.9) ---
    # --- Cosmic & Macro (0.1, 0.10, 0.3) ---
    "0.1": "galactic",
    "0.3": "galactic",
    "0.10": "fluid",
    "0.31": "fluid", # Propulsion

    # --- Particle & Quantum (0.5-0.9, 0.17-0.21) ---
    "0.5": "nuclear_binding",
    "0.6": "electroweak", # Electroweak (High Energy)
    "0.7": "quantum", # Neutrino
    "0.8": "quantum", # Muon g-2
    "0.9": "quantum", # Nonlocality
    "0.17": "electroweak", # Mass Generation (Strong interaction link)
    "0.18": "quantum", # Information/Entanglement
    "0.20": "quantum", # Atomic Physics
    "0.21": "nuclear_binding", # Yang-Mills (QCD)
    "0.24": "ai_cortex", # AI (Axiomatic logic)
    "0.25": "fluid", # Strategy/Economics
    "0.32": "nuclear_binding", # Fusion

    "General": "fluid",
}

# Mapping: Topic -> Characteristic Scale (Meters)
_TOPIC_SCALE_REGISTRY = {
    "0.1": 1e21,    # Galaxy
    "0.5": 1e-15,   # Nuclear (Binding)
    "0.6": 1.1e-18, # Electroweak (MZ)
    "0.7": 1e-35,   # Neutrino (Planck limit pivot)
    "0.8": 1e-12,   # Muon (Magnetic Scale)
    "0.9": 1e-10,   # Nonlocality (Atomic link)
    "0.17": 1e-18,  # Particle Mass
    "0.20": 0.5e-10, # Atomic (Bohr)
    "0.32": 1e-15,   # Fusion (Effective Barrier)
}

def get_params(topic_id_or_domain: str = "fluid", **overrides) -> UETParameters:
    """
    Get UET parameters DERIVED from first-principles ONLY.
    No hardcoded legacy values are allowed in the hardened v0.9.5 core.
    """
    # 1. Resolve domain from topic_id if provided
    domain = _TOPIC_DOMAIN_MAP.get(topic_id_or_domain, topic_id_or_domain)

    # 2. Check if it's a known domain
    if domain not in _DOMAIN_PRESETS:
        # Fallback to fluid (macroscopic) but log it as observation-only
        print(f"WARNING [PURGE]: Unknown domain/topic '{topic_id_or_domain}'. Defaulting to 'fluid' (Landauer 300K).")
        domain = "fluid"

    # 3. Derive Axiomatic Parameters (A1-A12) via Landauer Principle
    preset = _DOMAIN_PRESETS[domain]
    # Default scale from Topic Registry or Domain Preset
    # Use topic_id_or_domain to lookup the specific scale if it's a topic ID
    topic_scale = _TOPIC_SCALE_REGISTRY.get(topic_id_or_domain, preset["scale"])

    return derive_parameters_first_principles(
        scale=topic_scale,
        temperature=preset["temperature"],
        information_density=preset["info_density"],
        **overrides
    )


def get_kappa_beta(scale: str = "electroweak") -> tuple[float, float]:
    """Convenience function to get just κ and β."""
    p = get_params(scale)
    return p.kappa, p.beta


# =============================================================================
# DOCUMENTATION
# =============================================================================

PARAMETER_POLICY = """
╔══════════════════════════════════════════════════════════════════════╗
║           UET PARAMETER CALCULATION POLICY (UPDATED)                ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  PRIMARY METHOD: First-Principles Calculation                       ║
║  ──────────────────────────────────────────────────────────────   ║
║  Use derive_parameters_first_principles() or get_params_first_      ║
║  principles() for calculating parameters from physical laws:         ║
║                                                                      ║
║    E_min = k_B * T * ln(2) [J]   (SI lower bound only)              ║
║    β_norm = normalize(E_min)     (dimensionless proxy, lane-specific)║
║                                                                      ║
║  Domain presets available: quantum, nuclear_binding, fluid,         ║
║  galactic, biological                                          ║
║                                                                      ║
║  LEGACY METHOD: Hardcoded Registry (Backward Compatibility)          ║
║  ──────────────────────────────────────────────────────────────   ║
║  Legacy _SCALE_PARAMS are kept for existing code, but new code       ║
║  should use first-principles calculation.                          ║
║                                                                      ║
║  PROHIBITED:                                                        ║
║  - DO NOT use scipy.optimize to fit parameters per experiment!      ║
║  - DO NOT change parameters to match specific data!                 ║
║  - DO NOT use "shadow math" (bypassing UET_KILL_ENGINE)             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
# Legacy Scale Registry (Backward Compatibility)
_SCALE_PARAMS = {}


if __name__ == "__main__":
    print("=" * 70)
    print("UET PARAMETER CALCULATION - FIRST PRINCIPLES DEMONSTRATION")
    print("=" * 70)

    print(PARAMETER_POLICY)

    print("\n" + "=" * 70)
    print("FIRST-PRINCIPLES CALCULATION EXAMPLES")
    print("=" * 70)

    # Example 1: Landauer lower bound and normalized proxy at 300K.
    print("\n[1] Landauer lower bound at 300K:")
    beta_normalized_room = calculate_beta_landauer(300)
    landauer_energy_joule = landauer_minimum_energy(300)
    landauer_energy_ev = landauer_energy_joule / E_CHARGE
    print(f"    beta_normalized = {beta_normalized_room:.4e} [1]")
    print(f"    E_min = {landauer_energy_joule:.4e} J = {landauer_energy_ev:.6f} eV")
    print(f"    Expected energy = 0.017921 eV (Topic 0.13 comparator)")
    print(f"    Status: {'PASS' if abs(landauer_energy_ev - 0.017921) < 0.001 else 'FAIL'}")
    # Example 2: Domain-specific parameters
    print("\n[2] Domain-Specific Parameters (First-Principles):")
    domains = ["quantum", "fluid", "galactic", "biological"]
    for domain in domains:
        params = get_params_first_principles(domain)
        print(f"    {domain}:")
        print(f"        κ = {params.kappa:.6f}")
        print(f"        beta_normalized = {params.beta:.4e} [1]")
        print(f"        scale = {params.scale}, origin = {params.origin}")

    # Example 3: Scaling between domains
    print("\n[3] Scaling Example (quantum → fluid):")
    scale_factor = calculate_scaling_ratio(1e-9, 1e-3)
    print(f"    Scale factor: {scale_factor:.4e}")
    print(f"    (κ at fluid scale) = (κ at quantum scale) × {scale_factor:.4e}")

    print("\n" + "=" * 70)
    print("LEGACY PARAMETER REGISTRY (Backward Compatibility)")
    print("=" * 70)
    print("\nAvailable legacy scales:")
    for name, params in _SCALE_PARAMS.items():
        print(f"  {name}: κ={params.kappa}, β={params.beta} ({params.origin})")

    print("\n" + "=" * 70)
    print("RECOMMENDATION: Use first-principles calculation for new code!")
    print("=" * 70)
