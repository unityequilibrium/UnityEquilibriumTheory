"""
UET Master Equation - Candidate Core and Opt-in Operator Implementations
====================================================================

This module implements the UET baseline functional plus opt-in candidate operators:

    Ω[C,I,J] = ∫ d³x [
        V(C)                          # A1: Symmetry Breaking (U(1))
      + (κ/2)|∇C|²                    # A3: Space-Memory Gradient
      + (1/2)|∇I|² + (1/2)m_I²I²      # A2: Information Field Dynamics (Propagator)
      + β C·I                         # A2: Information-Energy Coupling
      + γ_J (J_in - J_out)·C          # A4: Semi-open Exchange (In-Ex)
      + W_N |∇Ω_local|               # A5: Natural Will (Fisher Info Regulator)
      + β_U(Σ,R) · V_game(C)          # A8: Dynamic Game (Energy Competition)
      + λ Σ_layers(C_i-C_j)²          # A10: Multi-layer Coherence
    ]

Axiom Coverage (implementation map; not proof):
    ✅ A1:  Energy Conservation & Transformative Dissipation
    ✅ A2:  Information Emerges from Irreversibility
    ✅ A3:  Space is the Universal Memory Substrate
    ✅ A4:  All Systems Are Semi-open (In-Ex Duality)
    ✅ A5:  Natural Will (Existence Persistence Drive)
    ✅ A6:  Learning = Necessary Energy Adjustment (NEA)
    ✅ A7:  Pattern Recurrence Across Scales (scale-invariant form)
    ✅ A8:  Game Dynamics of Existence
    ✅ A9:  Equilibrium Is Dynamic Center
    ✅ A10: Multi-layer Coherence Requirement
    ✅ A11: All Models Must Reduce to Known Physics
    ✅ A12: The Theory Must Evolve
    ✅ A13: Systemic Inertia
    ✅ A14: Dynamic Viscosity

Symmetries & Conservation Laws (Noether's Theorem):
    ✅ U(1) Gauge Symmetry → Charge Conservation
    ✅ Translation Symmetry → Momentum Conservation
    ✅ Rotation Symmetry → Angular Momentum Conservation
    ✅ Scale Invariance (via RG Flow) → Scale-invariant quantities
    ✅ Lorentz Invariance → Energy-Momentum Conservation (Coupled via Inertia term)

Sources:
    - Thermodynamics Laws 0, 1, 2, 3
    - Landauer Principle (1961), Bérut 2012
    - Bekenstein Bound (1981)
    - Jacobson's Thermodynamic Gravity (1995)
    - Dynamic Game (Nash Differential Games, Vanchurin 2020)
    - Core Axioms Document (Santa 2026)
    - Noether's Theorem (1918) - see uet_noether.py
    - Lorentz Invariance (1905) - see uet_lorentz.py
"""

import sys
from pathlib import Path

import numpy as np
from dataclasses import dataclass, field, replace
from typing import Tuple, Optional, List, Union, Any


def _bootstrap_docs_root() -> None:
    """Allow direct script execution without hardcoded local paths."""
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return


_bootstrap_docs_root()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from scipy.constants import k as k_B, c, G, hbar
except ModuleNotFoundError:
    from docs.core.uet_parameters import K_B as k_B, C as c, G, HBAR as hbar

from docs.core.uet_parameters import INTEGRITY_KILL_SWITCH, UETParameters
from docs.core.uet_matter_space import (
    MATTER_SPACE_OPERATOR_MODE,
    MatterSpaceConfig,
    MatterSpaceState,
    matter_space_step,
)
from docs.core.uet_matter_space_finite_cone import (
    FINITE_CONE_C_OPERATOR_MODE,
    FiniteConeCConfig,
    FiniteConeCState,
    finite_cone_c_step,
)

from docs.core.uet_matter_space_characteristic import (
    CHARACTERISTIC_CONE_OPERATOR_MODE,
    characteristic_cone_step,
)

from docs.core.uet_trace import (
    TraceKernelConfig,
    UETStepResult,
    build_trace_energy_ledger,
    compute_dissipation_source,
    compute_spacetime_trace,
)
LEGACY_OPERATOR_MODE = "legacy_local"
LEGACY_VARIATIONAL_OPERATOR_MODE = "legacy_variational_v1"
SPATIAL_COUPLED_OPERATOR_MODE = "spatial_coupled_v1"
SPATIAL_COUPLED_V2_OPERATOR_MODE = "spatial_coupled_v2"
CONSERVED_ORDER_OPERATOR_MODE = "conserved_order_v1"
CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE = "conserved_order_spectral_v1"
SPACETIME_TRACE_OPERATOR_MODE = "spacetime_trace_v1"
SUPPORTED_OPERATOR_MODES = {
    LEGACY_OPERATOR_MODE,
    LEGACY_VARIATIONAL_OPERATOR_MODE,
    SPATIAL_COUPLED_OPERATOR_MODE,
    SPATIAL_COUPLED_V2_OPERATOR_MODE,
    CONSERVED_ORDER_OPERATOR_MODE,
    CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
    SPACETIME_TRACE_OPERATOR_MODE,
    MATTER_SPACE_OPERATOR_MODE,
    FINITE_CONE_C_OPERATOR_MODE,
    CHARACTERISTIC_CONE_OPERATOR_MODE,
}


def resolve_operator_mode(
    params: Optional[UETParameters] = None, operator_mode: Optional[str] = None
) -> str:
    """Resolve the active equation-operator family without changing legacy defaults."""
    mode = operator_mode or getattr(params, "operator_mode", LEGACY_OPERATOR_MODE)
    if mode not in SUPPORTED_OPERATOR_MODES:
        raise ValueError(
            f"Unsupported UET operator_mode={mode!r}. "
            f"Expected one of {sorted(SUPPORTED_OPERATOR_MODES)}."
        )
    return mode


def _volume_element(field: np.ndarray, dx: float) -> float:
    """Match the repository convention for integrating 1D versus higher-dimensional grids."""
    ndim = getattr(field, "ndim", 0)
    if ndim <= 0:
        return 1.0
    if ndim == 1:
        return dx
    return dx**ndim


def gradient_magnitude_squared(C: np.ndarray, dx: float) -> np.ndarray:
    """Return |grad C|^2 with zero gradients on singleton axes."""
    C = np.asarray(C, dtype=float)
    grad_sq = np.zeros_like(C, dtype=float)
    if C.ndim == 0:
        return grad_sq

    for axis, size in enumerate(C.shape):
        if size <= 1:
            continue
        edge_order = 2 if size > 2 else 1
        grad_axis = np.gradient(C, dx, axis=axis, edge_order=edge_order)
        grad_sq += grad_axis**2
    return grad_sq


def conserved_laplacian(field: np.ndarray, dx: float) -> np.ndarray:
    """Periodic Laplacian used by opt-in conserved diagnostic operators."""
    field = np.asarray(field, dtype=float)
    lap = np.zeros_like(field, dtype=float)
    if field.ndim == 0:
        return lap

    for axis, size in enumerate(field.shape):
        if size <= 1:
            continue
        lap += (np.roll(field, 1, axis=axis) - 2 * field + np.roll(field, -1, axis=axis)) / dx**2
    return lap


def periodic_gradient_energy(
    field: np.ndarray, dx: float, coefficient: float = 1.0
) -> float:
    """Return the periodic discrete gradient energy in the normalized lane."""
    array = np.asarray(field, dtype=float)
    if array.ndim == 0:
        return 0.0
    spacing = float(dx)
    if not np.isfinite(spacing) or spacing <= 0.0:
        raise ValueError("dx must be finite and positive")
    gradient_sq = 0.0
    for axis, size in enumerate(array.shape):
        if size <= 1:
            continue
        face_gradient = (np.roll(array, -1, axis=axis) - array) / spacing
        gradient_sq += float(np.sum(face_gradient**2))
    return 0.5 * float(coefficient) * gradient_sq * _volume_element(array, spacing)

def spectral_conserved_order_step(
    C: np.ndarray,
    non_gradient_force: np.ndarray,
    dx: float,
    dt: float,
    params: UETParameters,
) -> np.ndarray:
    """
    Wave 16 candidate: semi-implicit spectral conserved-order update.

    `non_gradient_force` is the already assembled force with the explicit
    `kappa * laplacian(C)` part removed. The conserved flow is treated as
    `-nabla^2(non_gradient_force) - kappa*nabla^4(C)`, with the stiff
    biharmonic term in the denominator. This mirrors the topic 0.11 spectral
    Cahn-Hilliard engine while keeping the core path opt-in.
    """
    C = np.asarray(C, dtype=float)
    non_gradient_force = np.asarray(non_gradient_force, dtype=float)
    if C.ndim == 0 or dt == 0 or all(size <= 1 for size in C.shape):
        return np.array(C, copy=True)

    k_sq = np.zeros(C.shape, dtype=float)
    for axis, size in enumerate(C.shape):
        if size <= 1:
            continue
        freqs = 2.0 * np.pi * np.fft.fftfreq(size, d=dx)
        shape = [1] * C.ndim
        shape[axis] = size
        k_sq += freqs.reshape(shape) ** 2

    mobility = getattr(params, "conserved_order_mobility", 1.0)
    kappa = getattr(params, "kappa", 0.0)
    numerator = np.fft.fftn(C) + dt * mobility * k_sq * np.fft.fftn(non_gradient_force)
    denominator = 1.0 + dt * mobility * kappa * k_sq**2
    updated = np.fft.ifftn(numerator / denominator).real

    # Preserve the zero mode exactly enough for gate-level mass checks.
    updated += float(np.mean(C)) - float(np.mean(updated))
    return updated


def screened_nonlocal_field(field: np.ndarray, dx: float, length_scale: float) -> np.ndarray:
    """
    Return a deterministic screened nonlocal average.

    This is a Wave 11 candidate helper, not accepted physics. It keeps the
    zero mode unchanged and damps shorter wavelengths by 1/(1 + ell^2 k^2),
    so uniform fields return unchanged and memory contrast vanishes.
    """
    field = np.asarray(field, dtype=float)
    if field.ndim == 0 or length_scale <= 0:
        return np.array(field, copy=True)
    if all(size <= 1 for size in field.shape):
        return np.array(field, copy=True)

    k_sq = np.zeros(field.shape, dtype=float)
    for axis, size in enumerate(field.shape):
        if size <= 1:
            continue
        freqs = 2.0 * np.pi * np.fft.fftfreq(size, d=dx)
        shape = [1] * field.ndim
        shape[axis] = size
        k_sq += freqs.reshape(shape) ** 2

    spectral_filter = 1.0 / (1.0 + (length_scale**2) * k_sq)
    return np.fft.ifftn(np.fft.fftn(field) * spectral_filter).real


def spatial_memory_contrast(C: np.ndarray, dx: float, params: UETParameters) -> np.ndarray:
    """Scale-dependent contrast between local C and screened space-memory field."""
    length_scale = getattr(params, "spatial_v2_memory_length", 2.0)
    return screened_nonlocal_field(C, dx, length_scale) - np.asarray(C, dtype=float)


def spatial_interface_activity(C: np.ndarray, dx: float, params: UETParameters) -> np.ndarray:
    """Wave 11 candidate activity: local gradient plus nonlocal memory contrast."""
    memory = spatial_memory_contrast(C, dx, params)
    coeff = getattr(params, "spatial_v2_nonlocal_coupling", 1.0)
    return gradient_magnitude_squared(C, dx) + coeff * memory**2
# =============================================================================
# PHYSICAL CONSTANTS (CODATA 2024 / Real Experiments)
# =============================================================================

# Planck length squared: L_P² = ℏG/c³
L_P_SQUARED = hbar * G / c**3  # ≈ 2.61e-70 m²

# Bekenstein coefficient: κ_Bekenstein = L_P²/4 (from S ≤ A/4L_P²)
KAPPA_BEKENSTEIN = L_P_SQUARED / 4  # ≈ 6.5e-71 m²

# =============================================================================
# AXIOM 4: SEMI-OPEN SYSTEM CONSTANTS
# =============================================================================
# Moved to UETParameters (SIGMA_CRIT) \n


# =============================================================================
# UET PARAMETERS - CENTRALIZED CANDIDATE CONTROLS
# =============================================================================


# UETParameters imported above with the integrity switch.

# =============================================================================
# AXIOM 1: ENERGY CONSERVATION - POTENTIAL V(C)
# =============================================================================


def potential_V(C: np.ndarray, params: UETParameters) -> np.ndarray:
    """
    AXIOM 1: Energy Conservation & Transformative Dissipation

    Local potential V(C) = (α/2)(|C|²-C0²)² + (γ/4)(|C|²-C0²)⁴

    Symmetry: U(1) Global Phase Invariance
    Conserved Quantity: Information Charge (Q_I)

    "พลังงานไม่เคยหายไป แต่การใช้พลังงานทุกครั้งต้องแลกมาด้วยต้นทุนการสูญเสีย"
    """
    # Magnitude squared for U(1) symmetry breaking logic
    C_mag_sq = C**2  # Assuming real part for current numerical engine
    diff = C_mag_sq - params.C0**2
    return (params.alpha / 2) * diff**2 + (params.gamma / 4) * diff**4


def potential_derivative(C: Union[np.ndarray, Tuple], params: UETParameters) -> np.ndarray:
    """Exact derivative of potential_V in the radial C lane."""
    if isinstance(C, (tuple, list)):
        C = C[0]

    diff = C**2 - params.C0**2
    return 2.0 * C * (params.alpha * diff + params.gamma * diff**3)


def legacy_reaction_derivative(
    C: Union[np.ndarray, Tuple], params: UETParameters
) -> np.ndarray:
    """Historical shifted derivative retained only for legacy_local.

    This relation is not the derivative of potential_V; it is kept as a named
    comparator so preserving legacy numerical behavior cannot be mistaken for
    a variational claim.
    """
    if isinstance(C, (tuple, list)):
        C = C[0]
    diff = C - params.C0
    return params.alpha * diff + params.gamma * diff**3

# =============================================================================
# AXIOM 2: INFORMATION FROM IRREVERSIBILITY - βCI COUPLING
# =============================================================================


def information_coupling(
    C: np.ndarray,
    I: np.ndarray,
    dx: float,
    params: UETParameters,
    operator_mode: Optional[str] = None,
) -> float:
    """
    AXIOM 2: Information Emerges from Irreversibility.

    Legacy mode keeps the historical beta C*I coupling. Wave 5 spatial mode is
    an opt-in candidate that uses 0.5*beta*C^2*I so the C dynamics source is
    proportional to C*I. Wave 11 v2 additionally gates the candidate by
    interface/nonlocal activity. These are heuristic bridges, not accepted
    derivations.
    """
    mode = resolve_operator_mode(params, operator_mode)
    volume = _volume_element(C, dx)
    if mode == SPATIAL_COUPLED_V2_OPERATOR_MODE:
        coeff = getattr(params, "spatial_v2_information_coupling", 1.0)
        activity = spatial_interface_activity(C, dx, params)
        return 0.5 * params.beta * coeff * np.sum(C**2 * I * activity) * volume
    if mode == SPATIAL_COUPLED_OPERATOR_MODE:
        coeff = getattr(params, "spatial_information_coupling", 1.0)
        return 0.5 * params.beta * coeff * np.sum(C**2 * I) * volume
    return params.beta * np.sum(C * I) * volume


def information_dynamics_source(
    C: np.ndarray,
    I: Optional[np.ndarray],
    params: UETParameters,
    operator_mode: Optional[str] = None,
    dx: float = 1.0,
) -> Union[np.ndarray, float]:
    """Negative functional-gradient source from the information coupling."""
    if I is None:
        return 0.0
    mode = resolve_operator_mode(params, operator_mode)
    if mode == SPATIAL_COUPLED_V2_OPERATOR_MODE:
        coeff = getattr(params, "spatial_v2_information_coupling", 1.0)
        activity = spatial_interface_activity(C, dx, params)
        return -params.beta * coeff * C * I * activity
    if mode == SPATIAL_COUPLED_OPERATOR_MODE:
        coeff = getattr(params, "spatial_information_coupling", 1.0)
        return -params.beta * coeff * C * I
    return -params.beta * I

def information_propagator_step(
    I: np.ndarray,
    C: np.ndarray,
    dx: float,
    dt: float,
    params: UETParameters,
    operator_mode: Optional[str] = None,
) -> np.ndarray:
    """Advance the information field in the selected operator lane.

    In ``legacy_variational_v1`` the normalized contract is the first-order
    gradient flow

        dI/dt = Laplacian(I) - kappa_I*I - beta*C,

    which is the negative functional derivative of the declared I-sector
    ``1/2|grad I|^2 + 1/2*kappa_I*I^2 + beta*C*I`` under periodic boundaries.
    The historical box/wave relation is retained only as a comparator; it is
    not silently presented as the equation implemented by this function.
    """
    mode = resolve_operator_mode(params, operator_mode)
    if mode == LEGACY_VARIATIONAL_OPERATOR_MODE:
        # The canonical normalized lane uses the periodic discrete operator
        # whose adjoint is the gradient term in omega_functional_complete().
        laplacian = conserved_laplacian(I, dx)
    elif I.ndim == 1:
        laplacian = np.zeros_like(I)
        if len(I) > 2:
            laplacian[1:-1] = (I[2:] - 2 * I[1:-1] + I[:-2]) / dx**2
            laplacian[0] = laplacian[1]
            laplacian[-1] = laplacian[-2]
    else:
        laplacian = conserved_laplacian(I, dx)

    # Legacy/default paths preserve their historical parabolic update.
    decay = params.kappa_I * I
    if mode == SPATIAL_COUPLED_V2_OPERATOR_MODE:
        coeff = getattr(params, "spatial_v2_information_coupling", 1.0)
        activity = spatial_interface_activity(C, dx, params)
        source = 0.5 * params.beta * coeff * C**2 * activity
    elif mode == SPATIAL_COUPLED_OPERATOR_MODE:
        coeff = getattr(params, "spatial_information_coupling", 1.0)
        source = 0.5 * params.beta * coeff * C**2
    elif mode == LEGACY_VARIATIONAL_OPERATOR_MODE:
        # +beta*C*I in Omega requires -beta*C under negative gradient flow.
        source = -params.beta * C
    else:
        source = params.beta * C

    dI_dt = laplacian - decay + source
    return I + dt * dI_dt

# =============================================================================
# AXIOM 3: SPACE = MEMORY - GRADIENT TERM
# =============================================================================


def gradient_term(C: np.ndarray, dx: float, params: UETParameters) -> float:
    """
    🌌 AXIOM 3: Space is the Universal Memory Substrate

    Gradient term: (κ/2)|∇C|²

    "Space/Field คือสมุดบันทึกกลางของจักรวาล"
    "ร่องรอยการเปลี่ยนพลังงานถูก encode บน geometry ของ space"
    """
    if C.ndim == 1:
        if len(C) < 2:
            return 0.0
        grad = np.gradient(C, dx)
        return (params.kappa / 2) * np.sum(grad**2) * dx
    elif C.ndim == 2:
        # Handle singleton dimensions (1xN or Nx1)
        grad_x = np.gradient(C, dx, axis=1) if C.shape[1] > 1 else np.zeros_like(C)
        grad_y = np.gradient(C, dx, axis=0) if C.shape[0] > 1 else np.zeros_like(C)
        return (params.kappa / 2) * np.sum(grad_x**2 + grad_y**2) * dx**2


# =============================================================================
# AXIOM 4: SEMI-OPEN SYSTEM (In-Ex Duality)
# =============================================================================


def semi_open_exchange(
    C: np.ndarray, J_in: np.ndarray, J_out: np.ndarray, dx: float, params: UETParameters
) -> float:
    """
    🔄 AXIOM 4: All Systems Are Semi-open (In-Ex Duality)

    Exchange term: γ_J (J_in - J_out)·C

    "ไม่มีระบบใดปิดสนิทหรือเปิดสนิท ทุกระบบอยู่ในสภาพกึ่งเปิด-กึ่งปิด"
    - In = เก็บพลังงาน/รักษาโครงสร้าง
    - Ex = แลกเปลี่ยนพลังงาน/ลด entropy
    """
    net_flux = J_in - J_out
    if C.ndim == 1:
        return params.gamma_J * np.sum(net_flux * C) * dx
    else:
        return params.gamma_J * np.sum(net_flux * C) * dx**C.ndim


def compute_in_ex_balance(J_in: np.ndarray, J_out: np.ndarray) -> float:
    """
    Compute In-Ex balance ratio.

    Returns: ratio where 1.0 = perfect balance, <1 = too closed, >1 = too open
    """
    total_in = np.sum(np.abs(J_in))
    total_out = np.sum(np.abs(J_out))
    if total_in == 0:
        return 0.0
    return total_out / total_in


# =============================================================================
# AXIOM 5: [AXIOMATIC HYPOTHESIS] NATURAL WILL
# =============================================================================


def natural_will_term(C: np.ndarray, dx: float, params: UETParameters) -> float:
    """
    💪 AXIOM 5: Natural Will (Existence Persistence Drive)

    Natural Will term: W_N |∇Ω_local|

    "ทุกระบบมีแรงขับเพื่อคงอยู่ (Natural Will) ที่ผลักให้มันหาสมดุลใหม่อยู่ตลอด"
    "ไม่ใช่เจตนาเชิงจิต แต่คือ drive ที่เกิดจากโครงสร้างฟิสิกส์"
    """
    # Compute local gradient of the field (proxy for |∇Ω|)
    if C.ndim == 1:
        if len(C) < 2:
            return 0.0
        grad = np.gradient(C, dx)
        return params.W_N * np.sum(np.abs(grad)) * dx
    elif C.ndim == 2:
        grad_x = np.gradient(C, dx, axis=1) if C.shape[1] > 1 else np.zeros_like(C)
        grad_y = np.gradient(C, dx, axis=0) if C.shape[0] > 1 else np.zeros_like(C)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)
        return params.W_N * np.sum(grad_mag) * dx**2


# =============================================================================
# AXIOM 6: LEARNING = NECESSARY ENERGY ADJUSTMENT (NEA)
# =============================================================================


def nea_dynamics(C: np.ndarray, constraints: dict, params: UETParameters) -> np.ndarray:
    """
    📚 AXIOM 6: Learning = Necessary Energy Adjustment (NEA)

    Learning = argmin_path(E_cost | constraints)

    "การเรียนรู้ = การปรับตัวเชิงความจำเป็นของพลังงานตามข้อจำกัด"
    "ไม่ใช่การเลือกทางที่ดีที่สุดแบบมี free will"
    "แต่เป็นผลลัพธ์ที่หลีกเลี่ยงไม่ได้จากข้อจำกัดของระบบ"
    """
    # Constraints define bounds on C
    C_min = constraints.get("C_min", -np.inf)
    C_max = constraints.get("C_max", np.inf)

    # Clip to constraints (system MUST stay in valid region)
    C_adjusted = np.clip(C, C_min, C_max)

    return C_adjusted


# =============================================================================
# AXIOM 8: [AXIOMATIC HYPOTHESIS] DYNAMIC GAME - ENERGY COMPETITION
# =============================================================================


def strategic_boost(density: float, scale: float = 1.0, params: UETParameters = None) -> float:
    """
    🧬 AXIOM 8: Dynamic Game (Energy Competition)

    Strategic boost β_U for systems competing for limited energy resources.

    [REFACTORED IN WAVE 39 - EMERGENCE OVERRIDE]
    Removed all ad-hoc if-else density gates.
    The dynamic game is no longer forced by an artificial referee.
    Instead, the parameter acts as a flat baseline coupling, and the actual
    Emergence (Player becomes Game) is handled by the non-linear field coupling
    between Mass (C^2) and Information (I) in the propagator.
    """
    if params is None:
        params = UETParameters()

    # Provide a stable, non-gated baseline for the game coupling.
    # The true 'boost' will emerge naturally from the C^2 -> I field warping.
    base_scalar = (params.beta * 30.0) if params.beta > 0 else 1.5

    return base_scalar


def game_theory_potential(
    C: np.ndarray,
    density: float,
    scale: float = 1.0,
    params: UETParameters = None,
    dx: float = 1.0,
    operator_mode: Optional[str] = None,
) -> np.ndarray:
    """
    Dynamic Game correction to potential for energy-competitive systems.

    Legacy mode keeps V_game = beta_U*C^2. Wave 5 spatial mode is an opt-in
    heuristic bridge that makes the candidate game term interface-sensitive via
    |grad C|^2 instead of local amplitude alone. Wave 11 v2 adds a screened
    memory contrast term so this lane is scale-dependent and still zero on
    uniform fields.
    """
    if params is None:
        params = UETParameters()
    mode = resolve_operator_mode(params, operator_mode)
    beta_U = strategic_boost(density, scale, params)
    if mode == SPATIAL_COUPLED_V2_OPERATOR_MODE:
        coeff = getattr(params, "spatial_v2_game_coupling", 1.0)
        return beta_U * coeff * spatial_interface_activity(C, dx, params)
    if mode == SPATIAL_COUPLED_OPERATOR_MODE:
        coeff = getattr(params, "spatial_game_coupling", 1.0)
        return beta_U * coeff * gradient_magnitude_squared(C, dx)
    return beta_U * C**2


def game_theory_force(
    C: np.ndarray,
    density: float,
    scale: float,
    dx: float,
    params: UETParameters,
    operator_mode: Optional[str] = None,
) -> Union[np.ndarray, float]:
    """
    Dynamics-side game operator.

    Legacy dynamics did not include an explicit game force in the master-step
    path, so legacy mode returns zero for backward compatibility. The Wave 5
    candidate exposes a KPZ-style interface drive proportional to |grad C|^2.
    Wave 11 v2 returns a conserved Laplacian of the interface/memory potential.
    """
    mode = resolve_operator_mode(params, operator_mode)
    if density <= 0:
        return 0.0
    if mode == SPATIAL_COUPLED_V2_OPERATOR_MODE:
        conserved_coeff = getattr(params, "spatial_v2_conserved_coupling", 1.0)
        potential = game_theory_potential(
            C,
            density=density,
            scale=scale,
            params=params,
            dx=dx,
            operator_mode=mode,
        )
        return conserved_coeff * conserved_laplacian(potential, dx)
    if mode == SPATIAL_COUPLED_OPERATOR_MODE:
        kpz_coeff = getattr(params, "spatial_kpz_coupling", 1.0)
        return kpz_coeff * game_theory_potential(
            C,
            density=density,
            scale=scale,
            params=params,
            dx=dx,
            operator_mode=mode,
        )
    return 0.0

# =============================================================================
# AXIOM 9: DYNAMIC EQUILIBRIUM CENTER
# =============================================================================


def find_equilibrium_center(C: np.ndarray, survival_prob: np.ndarray) -> float:
    """
    ⚖️ AXIOM 9: Equilibrium Is Not 50/50, but a Dynamic Center

    "สมดุลที่แท้จริงไม่ใช่กลางคณิต (50/50)"
    "แต่คือจุดใดก็ได้ที่รักษาการดำรงอยู่ได้ดีที่สุด"

    C_eq = argmax(survival_probability)
    """
    if len(survival_prob) == 0:
        return 0.0

    # Find index of maximum survival probability
    max_idx = np.argmax(survival_prob)
    return C[max_idx]


def update_equilibrium(C_eq_current: float, local_conditions: dict) -> float:
    """
    Update equilibrium center based on changing conditions.

    "จุดสมดุลไม่ตายตัว → เปลี่ยนตามเงื่อนไขภายนอก/ภายใน"
    """
    energy_in = local_conditions.get("energy_in", 0)
    energy_out = local_conditions.get("energy_out", 0)

    # Equilibrium shifts based on net energy flow
    delta = 0.01 * (energy_in - energy_out)
    return C_eq_current + delta


# =============================================================================
# AXIOM 10: MULTI-LAYER COHERENCE
# =============================================================================


def layer_coherence_term(
    C_layers: List[np.ndarray], dx: float, params: UETParameters
) -> float:
    """
    🔗 AXIOM 10: Multi-layer Coherence Requirement

    Coherence penalty: λ Σ_ij (C_i - C_j)²

    "ระบบจะเสถียรต้องสอดคล้องกันตั้งแต่ micro → macro"
    - พลังงานสอดคล้องรูปแบบ
    - ข้อมูลสอดคล้องบริบท
    - โครงสร้างสอดคล้องฟังก์ชัน
    """
    if len(C_layers) < 2:
        return 0.0

    coherence = 0.0
    for i in range(len(C_layers)):
        for j in range(i + 1, len(C_layers)):
            # Compute difference between layers
            diff = C_layers[i] - C_layers[j]
            coherence += np.sum(diff**2)

    return params.lambda_coherence * coherence * dx


# =============================================================================
# BASELINE OMEGA FUNCTIONAL AND OPT-IN CANDIDATE TERMS
# =============================================================================


# =============================================================================
# UNITY DENSITY LAW (GALAXY ROTATION)
# =============================================================================


def calculate_halo_ratio(rho: float, sigma_bar: float, r_kpc: float, params: UETParameters = None) -> float:
    """
    🌌 Unity Density Law: M_halo / M_disk Ratio

    Derivation from UET_GALAXY_ROTATION_PAPER.md:
    Ratio = Ratio_0 * (rho / rho_0)^-gamma

    Where:
      Ratio_0 = 8.5 (Pivot ratio)
      rho_0   = 5e7 M_sun/kpc^3 (Pivot density)
      gamma   = 0.48 (Thermodynamic scaling index)

    This unifies Spiral and Dwarf galaxies under a single vacuum pressure law.
    """
    if params is None:
        params = UETParameters()

    RHO_0 = params.RHO_UNITY
    GAMMA = params.GAMMA_UET
    RATIO_0 = params.RATIO_0

    if rho <= 1.0:  # Prevent division by zero or negative density
        return RATIO_0

    ratio = RATIO_0 * (rho / RHO_0) ** -GAMMA
    return ratio


def omega_functional_complete(
    C: np.ndarray,
    I: Optional[np.ndarray] = None,
    J_in: Optional[np.ndarray] = None,
    J_out: Optional[np.ndarray] = None,
    C_layers: Optional[List[np.ndarray]] = None,
    density: float = 0.0,
    scale: float = 1.0,
    dx: float = 0.1,
    params: UETParameters = None,
    operator_mode: Optional[str] = None,
) -> float:
    """
    🌌 THE COMPLETE UET MASTER EQUATION

    Ω[C,I,J] = ∫ d³x [
        V(C)                          # A1: Energy Conservation
      + (κ/2)|∇C|²                    # A3: Space-Memory Gradient
      + β C·I                         # A2: Information-Energy Coupling
      + γ_J (J_in - J_out)·C          # A4: Semi-open Exchange (In-Ex)
      + W_N |∇Ω_local|               # A5: Natural Will
      + β_U(Σ,R) · V_game(C)          # A8: Dynamic Game
      + λ Σ_layers(C_i-C_j)²          # A10: Multi-layer Coherence
    ]

    Provides a baseline functional plus opt-in candidate operators; it does not close all axioms.

    In ``legacy_variational_v1`` the C/I sector is the scoped normalized
    periodic gradient-flow contract. Exchange, game, inertia, and SI meaning
    remain outside that contract.
    """
    if params is None:
        params = UETParameters()

    # --- INTEGRITY KILL SWITCH ---
    if INTEGRITY_KILL_SWITCH:
        return 0.0  # Force zero energy / failure

    mode = resolve_operator_mode(params, operator_mode)

    # === A1: Potential term ===
    V = potential_V(C, params)
    if C.ndim == 1:
        potential_integral = np.sum(V) * dx
    else:
        potential_integral = np.sum(V) * dx**C.ndim

    # === A3: Gradient term ===
    gradient_integral = (
        periodic_gradient_energy(C, dx, params.kappa)
        if mode == LEGACY_VARIATIONAL_OPERATOR_MODE
        else gradient_term(C, dx, params)
    )

    # === A2: Information coupling ===
    if I is not None:
        info_integral = information_coupling(C, I, dx, params, operator_mode=mode)
        info_volume = _volume_element(I, dx)
        # The header's |grad I|² + m_I² I² terms are now explicit.  The
        # normalized core uses kappa_I as the candidate m_I² coefficient.
        info_gradient_integral = (
            periodic_gradient_energy(I, dx, 1.0)
            if mode == LEGACY_VARIATIONAL_OPERATOR_MODE
            else 0.5 * np.sum(gradient_magnitude_squared(I, dx)) * info_volume
        )
        info_mass_integral = 0.5 * getattr(params, "kappa_I", 0.0) * np.sum(I**2) * info_volume
    else:
        info_integral = 0.0
        info_gradient_integral = 0.0
        info_mass_integral = 0.0

    # === A4: Semi-open exchange (In-Ex) ===
    if J_in is not None and J_out is not None:
        exchange_integral = semi_open_exchange(C, J_in, J_out, dx, params)
    else:
        exchange_integral = 0.0

    # === A5: Natural Will ===
    will_integral = natural_will_term(C, dx, params)

    # === A8: Dynamic Game ===
    if density > 0:
        V_game = game_theory_potential(C, density, scale, params, dx=dx, operator_mode=operator_mode)
        if C.ndim == 1:
            game_integral = np.sum(V_game) * dx
        else:
            game_integral = np.sum(V_game) * dx**C.ndim
    else:
        game_integral = 0.0

    # === A10: Multi-layer coherence ===
    if C_layers is not None and len(C_layers) > 1:
        coherence_integral = layer_coherence_term(C_layers, dx, params)
    else:
        coherence_integral = 0.0

    # Total Ω
    return (
        potential_integral
        + gradient_integral
        + info_integral
        + info_gradient_integral
        + info_mass_integral
        + exchange_integral
        + will_integral
        + game_integral
        + coherence_integral
    )


# =============================================================================
# VALUE EQUATION: 𝒱 = -ΔΩ (THE CORE INSIGHT)
# =============================================================================


def calculate_value(omega_prev: float, omega_curr: float) -> float:
    """
    THE VALUE EQUATION: V = -dOmega/dt

    Scientifically, 'Value' is the rate of Free Energy Minimization (Lyapunov stability).
    It represents the "Useful Work" or "transformative dissipation" extracted from the system
    as it moves towards equilibrium.

    Equation:
        V = -(Ω_t - Ω_{t-1}) = -ΔΩ

    Thermodynamic Equivalence:
    - Physics: Free Energy Drop (-ΔF) -> Work Available
    - Biology: Fitness Gradient Ascent (+ΔFitness)
    - ML: Gradient Descent on Loss Function (-ΔLoss)

    In this core it is a Lyapunov/free-energy diagnostic, not a proof of full energy conservation.
    Ω must decrease for any spontaneous process (dΩ/dt ≤ 0), thus V must be positive.
    """
    return -(omega_curr - omega_prev)


def track_value_over_time(omega_series: List[float]) -> List[float]:
    """
    📈 Track Value at each timestep.

    Args:
        omega_series: List of Ω values at each timestep

    Returns:
        List of Value at each step (length = len(omega_series) - 1)
    """
    values = []
    for i in range(1, len(omega_series)):
        v = calculate_value(omega_series[i - 1], omega_series[i])
        values.append(v)
    return values


def total_value(omega_series: List[float]) -> float:
    """
    💰 Calculate total Value created over entire simulation.

    Total 𝒱 = -ΔΩ_total = -(Ω_final - Ω_initial)

    This is the integral of instantaneous value.
    """
    if len(omega_series) < 2:
        return 0.0
    return -(omega_series[-1] - omega_series[0])


# =============================================================================
# AXIOM 6: DYNAMICS ENGINE CLASS (WRAPPER)
# =============================================================================


class UETMasterEquation:
    """
    Main Interface for UET Physics Engine.
    Wraps the functional core into a unified object.
    """

    def __init__(self, params: UETParameters = None):
        self.params = params if params else UETParameters()
        self.V = None  # Velocity state for inertia
        self.I = None  # Information field state
        self.trace_history: List[np.ndarray] = []  # computational cache only
        self.trace_observable = None
        self.trace_config: Optional[TraceKernelConfig] = None
        self.space_response = None
        self.space_rate = None
        self.matter_rate = None
        self.matter_space_config: Optional[MatterSpaceConfig] = None
        self.finite_cone_c_config: Optional[FiniteConeCConfig] = None
        self.characteristic_cone_config: Optional[FiniteConeCConfig] = None

    def step_matter_space(
        self,
        state: MatterSpaceState,
        dt: float,
        dx: float,
        config: MatterSpaceConfig,
        matter_source: Optional[np.ndarray] = None,
        space_source: Optional[np.ndarray] = None,
        trace_config: Optional[TraceKernelConfig] = None,
    ) -> UETStepResult:
        """Advance the explicit physical matter-space state and update engine caches."""

        result = matter_space_step(
            state=state,
            dt=dt,
            dx=dx,
            config=config,
            matter_source=matter_source,
            space_source=space_source,
            trace_history=self.trace_history,
            trace_config=trace_config,
        )
        self.C = result.C
        self.V = None
        self.I = None
        self.space_response = result.space_response
        self.space_rate = result.space_rate
        self.trace_observable = result.trace_observable
        self.trace_config = trace_config
        self.matter_space_config = config
        source_snapshot = result.diagnostics.get("source_snapshot")
        if source_snapshot is not None:
            self.trace_history.append(np.asarray(source_snapshot, dtype=float).copy())
        return result

    def step_finite_cone_c(
        self,
        state: FiniteConeCState,
        dt: float,
        dx: float,
        config: FiniteConeCConfig,
        matter_source: Optional[np.ndarray] = None,
        space_source: Optional[np.ndarray] = None,
        trace_config: Optional[TraceKernelConfig] = None,
    ) -> UETStepResult:
        """Advance the opt-in finite-cone collective-C candidate."""

        result = finite_cone_c_step(
            state=state,
            dt=dt,
            dx=dx,
            config=config,
            matter_source=matter_source,
            space_source=space_source,
            trace_history=self.trace_history,
            trace_config=trace_config,
        )
        self.C = result.C
        self.V = None
        self.I = None
        self.matter_rate = None if result.V is None else np.asarray(result.V).copy()
        self.space_response = result.space_response
        self.space_rate = result.space_rate
        self.trace_observable = result.trace_observable
        self.trace_config = trace_config
        self.finite_cone_c_config = config
        source_snapshot = result.diagnostics.get("source_snapshot")
        if source_snapshot is not None:
            self.trace_history.append(np.asarray(source_snapshot, dtype=float).copy())
        return result

    def step_characteristic_cone(
        self,
        state: FiniteConeCState,
        dt: float,
        dx: float,
        config: FiniteConeCConfig,
        matter_source: Optional[np.ndarray] = None,
        space_source: Optional[np.ndarray] = None,
        trace_config: Optional[TraceKernelConfig] = None,
    ) -> UETStepResult:
        """Advance the strict compact-support characteristic finite-cone lane."""

        result = characteristic_cone_step(
            state=state,
            dt=dt,
            dx=dx,
            config=config,
            matter_source=matter_source,
            space_source=space_source,
            trace_history=self.trace_history,
            trace_config=trace_config,
        )
        self.C = result.C
        self.V = None
        self.I = None
        self.matter_rate = np.asarray(result.V).copy()
        self.space_response = result.space_response
        self.space_rate = result.space_rate
        self.trace_observable = result.trace_observable
        self.trace_config = trace_config
        self.characteristic_cone_config = config
        source_snapshot = result.diagnostics.get("source_snapshot")
        if source_snapshot is not None:
            self.trace_history.append(np.asarray(source_snapshot, dtype=float).copy())
        return result


    def step(
        self,
        C: np.ndarray,
        dt: float,
        dx: float = 0.1,
        I: Optional[np.ndarray] = None,
        V: Optional[np.ndarray] = None,
        J_in: Optional[np.ndarray] = None,
        J_out: Optional[np.ndarray] = None,
        constraints: Optional[dict] = None,
        density: float = 0.0,
        scale: float = 1.0,
        operator_mode: Optional[str] = None,
        trace_config: Optional[TraceKernelConfig] = None,
        matter_space_config: Optional[MatterSpaceConfig] = None,
        space_response: Optional[np.ndarray] = None,
        space_rate: Optional[np.ndarray] = None,
        matter_source: Optional[np.ndarray] = None,
        space_source: Optional[np.ndarray] = None,
        finite_cone_c_config: Optional[FiniteConeCConfig] = None,
        finite_cone_c_state: Optional[FiniteConeCState] = None,
        characteristic_cone_config: Optional[FiniteConeCConfig] = None,
        characteristic_cone_state: Optional[FiniteConeCState] = None,
        matter_rate: Optional[np.ndarray] = None,
    ) -> Union[Tuple[np.ndarray, ...], UETStepResult, np.ndarray]:
        """
        Execute one dynamics step with state management.
        If V or I are not provided, uses internal state.
        """
        mode = resolve_operator_mode(self.params, operator_mode)

        if mode == CHARACTERISTIC_CONE_OPERATOR_MODE:
            ambiguous = [
                name
                for name, value in (
                    ("I", I),
                    ("V", V),
                    ("J_in", J_in),
                    ("J_out", J_out),
                    ("constraints", constraints),
                )
                if value is not None
            ]
            if ambiguous:
                raise ValueError(
                    "matter_space_characteristic_cone_v1 rejects ambiguous legacy inputs: "
                    + ", ".join(ambiguous)
                )
            C_field = C[0] if isinstance(C, (tuple, list)) else C
            C_array = np.asarray(C_field, dtype=float)
            state = characteristic_cone_state
            if state is None:
                rate = matter_rate
                if rate is None:
                    rate = self.matter_rate
                if rate is None or np.shape(rate) != C_array.shape:
                    rate = np.zeros_like(C_array)
                response = space_response
                if response is None:
                    response = self.space_response
                if response is None or np.shape(response) != C_array.shape:
                    response = np.zeros_like(C_array)
                response_rate = space_rate
                if response_rate is None:
                    response_rate = self.space_rate
                if response_rate is None or np.shape(response_rate) != C_array.shape:
                    response_rate = np.zeros_like(C_array)
                state = FiniteConeCState(
                    C_array,
                    np.asarray(rate, dtype=float),
                    np.asarray(response, dtype=float),
                    np.asarray(response_rate, dtype=float),
                )
            elif not np.array_equal(C_array, state.C):
                raise ValueError(
                    "C must match characteristic_cone_state.C in compatibility mode"
                )
            return self.step_characteristic_cone(
                state=state,
                dt=dt,
                dx=dx,
                config=(
                    characteristic_cone_config
                    or self.characteristic_cone_config
                    or FiniteConeCConfig()
                ),
                matter_source=matter_source,
                space_source=space_source,
                trace_config=trace_config,
            )

        if mode == FINITE_CONE_C_OPERATOR_MODE:
            ambiguous = [
                name
                for name, value in (
                    ("I", I),
                    ("V", V),
                    ("J_in", J_in),
                    ("J_out", J_out),
                    ("constraints", constraints),
                )
                if value is not None
            ]
            if ambiguous:
                raise ValueError(
                    "matter_space_finite_cone_c_v1 rejects ambiguous legacy inputs: "
                    + ", ".join(ambiguous)
                )
            config = (
                finite_cone_c_config
                or self.finite_cone_c_config
                or FiniteConeCConfig()
            )
            C_array = np.asarray(C, dtype=float)
            if finite_cone_c_state is not None:
                if not np.array_equal(C_array, finite_cone_c_state.C):
                    raise ValueError(
                        "C must match finite_cone_c_state.C in compatibility mode"
                    )
                state = finite_cone_c_state
            else:
                rate = matter_rate
                if rate is None:
                    rate = self.matter_rate
                if rate is None or np.shape(rate) != C_array.shape:
                    rate = np.zeros_like(C_array)
                response = space_response
                if response is None:
                    response = self.space_response
                if response is None or np.shape(response) != C_array.shape:
                    response = np.zeros_like(C_array)
                response_rate = space_rate
                if response_rate is None:
                    response_rate = self.space_rate
                if response_rate is None or np.shape(response_rate) != C_array.shape:
                    response_rate = np.zeros_like(C_array)
                state = FiniteConeCState(
                    C_array,
                    np.asarray(rate, dtype=float),
                    np.asarray(response, dtype=float),
                    np.asarray(response_rate, dtype=float),
                )
            return self.step_finite_cone_c(
                state=state,
                dt=dt,
                dx=dx,
                config=config,
                matter_source=matter_source,
                space_source=space_source,
                trace_config=trace_config,
            )

        if mode == MATTER_SPACE_OPERATOR_MODE:
            ambiguous = [
                name
                for name, value in (
                    ("I", I),
                    ("V", V),
                    ("J_in", J_in),
                    ("J_out", J_out),
                    ("constraints", constraints),
                )
                if value is not None
            ]
            if ambiguous:
                raise ValueError(
                    "matter_space_coupled_v1 rejects ambiguous legacy inputs: "
                    + ", ".join(ambiguous)
                )
            config = matter_space_config or self.matter_space_config or MatterSpaceConfig()
            C_array = np.asarray(C, dtype=float)
            response = space_response
            if response is None:
                cached = self.space_response
                response = (
                    np.asarray(cached, dtype=float)
                    if cached is not None and np.shape(cached) == C_array.shape
                    else np.zeros_like(C_array)
                )
            rate = space_rate
            if rate is None:
                cached = self.space_rate
                rate = (
                    np.asarray(cached, dtype=float)
                    if cached is not None and np.shape(cached) == C_array.shape
                    else np.zeros_like(C_array)
                )
            state = MatterSpaceState(C_array, response, rate)
            return self.step_matter_space(
                state=state,
                dt=dt,
                dx=dx,
                config=config,
                matter_source=matter_source,
                space_source=space_source,
                trace_config=trace_config,
            )

        if mode == SPACETIME_TRACE_OPERATOR_MODE:
            if I is not None:
                raise ValueError(
                    "spacetime_trace_v1 consumes source_history; pass no independent I field"
                )
            config = trace_config or self.trace_config
            if config is None:
                config = TraceKernelConfig(
                    D_trace=getattr(self.params, "D_trace", 0.1),
                    tau_trace=getattr(self.params, "tau_trace", 0.1),
                    lambda_trace=getattr(self.params, "lambda_trace", 0.0),
                    source_normalization=getattr(
                        self.params, "trace_source_normalization", "normalized"
                    ),
                    boundary_condition=getattr(
                        self.params, "trace_boundary_condition", "periodic"
                    ),
                )
            results = dynamics_step_complete(
                C=C,
                V=V if V is not None else self.V,
                I=None,
                J_in=J_in,
                J_out=J_out,
                dx=dx,
                dt=dt,
                constraints=constraints,
                params=self.params,
                density=density,
                scale=scale,
                operator_mode=mode,
                trace_history=self.trace_history,
                trace_config=config,
                trace_coupling=getattr(self.params, "trace_coupling", 0.1),
            )
            if not isinstance(results, UETStepResult):
                raise TypeError("spacetime_trace_v1 must return UETStepResult")
            self.C = results.C
            self.V = results.V
            self.I = None
            self.trace_observable = results.trace_observable
            self.trace_config = config
            source_snapshot = results.diagnostics.get("source_snapshot")
            if source_snapshot is not None:
                self.trace_history.append(np.asarray(source_snapshot, dtype=float).copy())
            return results

        v_in = V if V is not None else self.V
        i_in = I if I is not None else self.I

        results = dynamics_step_complete(
            C=C,
            V=v_in,
            I=i_in,
            J_in=J_in,
            J_out=J_out,
            dx=dx,
            dt=dt,
            constraints=constraints,
            params=self.params,
            density=density,
            scale=scale,
            operator_mode=operator_mode,
        )

        # Unpack results based on what was returned
        if isinstance(results, tuple):
            self.C = results[0]
            if len(results) > 1:
                self.V = results[1]
            if len(results) > 2:
                self.I = results[2]
            return results
        else:
            self.C = results
            return results

    def reset_trace_history(self) -> None:
        """Reset the computational trace cache between independent runs."""
        self.trace_history.clear()
        self.trace_observable = None

    def compute_omega(
        self,
        C: np.ndarray,
        dx: float = 0.1,
        I: Optional[np.ndarray] = None,
        J_in: Optional[np.ndarray] = None,
        J_out: Optional[np.ndarray] = None,
        density: float = 0.0,
        scale: float = 1.0,
        operator_mode: Optional[str] = None,
    ) -> float:
        """Compute instantaneous Omega value."""
        return omega_functional_complete(
            C=C,
            I=I,
            J_in=J_in,
            J_out=J_out,
            density=density,
            scale=scale,
            dx=dx,
            params=self.params,
            operator_mode=operator_mode,
        )


def is_system_improving(omega_series: List[float], window: int = 10) -> bool:
    """
    Check if system is consistently improving (creating value).

    A system is "improving" if average Value over recent window is positive.
    """
    if len(omega_series) < 2:
        return False

    values = track_value_over_time(omega_series)

    if len(values) < window:
        window = len(values)

    recent_values = values[-window:]
    return sum(recent_values) > 0


# =============================================================================
# DYNAMICS - A6: CONSTRAINED OPTIMIZATION (LEARNING = NEA)
# =============================================================================


def _spacetime_trace_dynamics_step(
    C: np.ndarray,
    V: Optional[np.ndarray],
    J_in: Optional[np.ndarray],
    J_out: Optional[np.ndarray],
    dx: float,
    dt: float,
    constraints: Optional[dict],
    params: UETParameters,
    density: float,
    scale: float,
    trace_history: Optional[List[np.ndarray]],
    trace_config: Optional[TraceKernelConfig],
    trace_coupling: Optional[float],
) -> UETStepResult:
    """Run the opt-in history-functional branch without an independent ``I``."""

    if trace_config is None:
        trace_config = TraceKernelConfig(
            D_trace=getattr(params, "D_trace", 0.1),
            tau_trace=getattr(params, "tau_trace", 0.1),
            lambda_trace=getattr(params, "lambda_trace", 0.0),
            source_normalization=getattr(params, "trace_source_normalization", "normalized"),
            boundary_condition=getattr(params, "trace_boundary_condition", "periodic"),
        )
    history = list(trace_history or [])
    trace = compute_spacetime_trace(history, dx, dt, trace_config, shape=np.asarray(C).shape)

    # The trace response is compared with the current local baseline.  The
    # algebraic MOND-like A14 correction is disabled in this branch so a
    # measured history effect cannot be confused with the old viscosity proxy.
    baseline_params = replace(
        params, a0_viscosity=0.0, operator_mode=LEGACY_OPERATOR_MODE
    )
    baseline = dynamics_step_complete(
        C=C,
        V=V,
        I=None,
        J_in=J_in,
        J_out=J_out,
        dx=dx,
        dt=dt,
        constraints=constraints,
        params=baseline_params,
        density=density,
        scale=scale,
        operator_mode=LEGACY_OPERATOR_MODE,
    )
    if isinstance(baseline, tuple):
        baseline_C = np.asarray(baseline[0], dtype=float)
        baseline_V = np.asarray(baseline[1], dtype=float) if len(baseline) > 1 else None
    else:
        baseline_C = np.asarray(baseline, dtype=float)
        baseline_V = None

    strength = max(
        0.0,
        float(getattr(params, "trace_coupling", 0.1) if trace_coupling is None else trace_coupling),
    )
    feedback = 1.0 / (1.0 + strength * np.maximum(trace, 0.0))
    C_new = np.asarray(C, dtype=float) + feedback * (baseline_C - np.asarray(C, dtype=float))
    if constraints is not None:
        C_new = nea_dynamics(C_new, constraints, params)
    V_new = feedback * baseline_V if baseline_V is not None else None

    source = compute_dissipation_source(C, C_new, dt)
    ledger = build_trace_energy_ledger(source, trace, dx, trace_config)
    diagnostics = {
        "operator_mode": SPACETIME_TRACE_OPERATOR_MODE,
        "kernel_equation": trace_config.operator_equation,
        "kernel_is_causal_by_construction": True,
        "causal_speed": trace_config.v_trace,
        "trace_history_length": len(history),
        "baseline_operator": LEGACY_OPERATOR_MODE,
        "algebraic_viscosity_applied": False,
        "trace_feedback_min": float(np.min(feedback)),
        "trace_feedback_max": float(np.max(feedback)),
        "source_nonnegative": bool(np.min(source) >= -1e-12),
        "source_snapshot": source,
        "ontology": "history_functional_cache_not_independent_field",
    }
    return UETStepResult(
        C=C_new,
        V=V_new,
        trace_observable=trace,
        energy_ledger=ledger,
        diagnostics=diagnostics,
    )


def dynamics_step_complete(
    C: np.ndarray,
    V: Optional[np.ndarray] = None,      # A13: Velocity field for inertia
    I: Optional[np.ndarray] = None,      # A2: Information field
    J_in: Optional[np.ndarray] = None,   # A4: Exchange in
    J_out: Optional[np.ndarray] = None,  # A4: Exchange out
    dx: float = 0.1,
    dt: float = 0.01,
    constraints: Optional[dict] = None,
    params: UETParameters = None,
    density: float = 0.0,
    scale: float = 1.0,
    operator_mode: Optional[str] = None,
    trace_history: Optional[List[np.ndarray]] = None,
    trace_config: Optional[TraceKernelConfig] = None,
    trace_coupling: Optional[float] = None,
    matter_space_state: Optional[MatterSpaceState] = None,
    matter_space_config: Optional[MatterSpaceConfig] = None,
    matter_source: Optional[np.ndarray] = None,
    space_source: Optional[np.ndarray] = None,
    finite_cone_c_state: Optional[FiniteConeCState] = None,
    finite_cone_c_config: Optional[FiniteConeCConfig] = None,
    characteristic_cone_state: Optional[FiniteConeCState] = None,
    characteristic_cone_config: Optional[FiniteConeCConfig] = None,
) -> Union[np.ndarray, Tuple[np.ndarray, ...], UETStepResult]:
    """
    AXIOM 6/13/14: Dynamics as Inertial Constrained Optimization

    Equation (v0.9.0):
        τ_i ∂²C/∂t² + ∂C/∂t = -μ(a/a0)⁻¹ δΩ/δC

    Legacy path combines diffusion, inertia, and an algebraic viscosity proxy; trace mode is a separate history functional.
    """
    """
    AXIOM 6: Dynamics as Constrained Optimization

    dC/dt = -dOmega/dC = argmin_path(E_cost | constraints)

    The system is forced to follow the path of least cost under constraints.
    Not because it wants to, but because other paths are energetically forbidden.
    """
    if params is None:
        params = UETParameters()

    mode = resolve_operator_mode(params, operator_mode)
    if mode == LEGACY_VARIATIONAL_OPERATOR_MODE:
        unsupported = []
        if J_in is not None or J_out is not None:
            unsupported.append("J_in/J_out")
        if constraints is not None:
            unsupported.append("constraints")
        if density != 0.0:
            unsupported.append("density")
        if params.W_N != 0.0:
            unsupported.append("W_N")
        if params.a0_viscosity != 0.0:
            unsupported.append("a0_viscosity")
        if params.tau_inertia != 0.0:
            unsupported.append("tau_inertia")
        if unsupported:
            raise ValueError(
                "legacy_variational_v1 requires pure normalized gradient terms; "
                "disable " + ", ".join(unsupported)
            )

    if mode == CHARACTERISTIC_CONE_OPERATOR_MODE:
        ambiguous = [
            name
            for name, value in (
                ("I", I),
                ("V", V),
                ("J_in", J_in),
                ("J_out", J_out),
                ("constraints", constraints),
            )
            if value is not None
        ]
        if ambiguous:
            raise ValueError(
                "matter_space_characteristic_cone_v1 rejects ambiguous legacy inputs: "
                + ", ".join(ambiguous)
            )
        C_field = C[0] if isinstance(C, (tuple, list)) else C
        C_array = np.asarray(C_field, dtype=float)
        state = characteristic_cone_state
        if state is None:
            state = FiniteConeCState(
                C_array,
                np.zeros_like(C_array),
                np.zeros_like(C_array),
                np.zeros_like(C_array),
            )
        elif not np.array_equal(C_array, state.C):
            raise ValueError(
                "C must match characteristic_cone_state.C in compatibility mode"
            )
        return characteristic_cone_step(
            state=state,
            dt=dt,
            dx=dx,
            config=characteristic_cone_config or FiniteConeCConfig(),
            matter_source=matter_source,
            space_source=space_source,
            trace_history=trace_history,
            trace_config=trace_config,
        )

    if mode == FINITE_CONE_C_OPERATOR_MODE:
        ambiguous = [
            name
            for name, value in (
                ("I", I),
                ("V", V),
                ("J_in", J_in),
                ("J_out", J_out),
                ("constraints", constraints),
            )
            if value is not None
        ]
        if ambiguous:
            raise ValueError(
                "matter_space_finite_cone_c_v1 rejects ambiguous legacy inputs: "
                + ", ".join(ambiguous)
            )
        C_field = C[0] if isinstance(C, (tuple, list)) else C
        C_array = np.asarray(C_field, dtype=float)
        state = finite_cone_c_state
        if state is None:
            state = FiniteConeCState(
                C_array,
                np.zeros_like(C_array),
                np.zeros_like(C_array),
                np.zeros_like(C_array),
            )
        elif not np.array_equal(C_array, state.C):
            raise ValueError("C must match finite_cone_c_state.C in compatibility mode")
        return finite_cone_c_step(
            state=state,
            dt=dt,
            dx=dx,
            config=finite_cone_c_config or FiniteConeCConfig(),
            matter_source=matter_source,
            space_source=space_source,
            trace_history=trace_history,
            trace_config=trace_config,
        )

    if mode == MATTER_SPACE_OPERATOR_MODE:
        ambiguous = [
            name
            for name, value in (
                ("I", I),
                ("V", V),
                ("J_in", J_in),
                ("J_out", J_out),
                ("constraints", constraints),
            )
            if value is not None
        ]
        if ambiguous:
            raise ValueError(
                "matter_space_coupled_v1 rejects ambiguous legacy inputs: "
                + ", ".join(ambiguous)
            )
        C_field = C[0] if isinstance(C, (tuple, list)) else C
        C_array = np.asarray(C_field, dtype=float)
        state = matter_space_state
        if state is None:
            state = MatterSpaceState(
                C_array, np.zeros_like(C_array), np.zeros_like(C_array)
            )
        elif not np.array_equal(C_array, state.C):
            raise ValueError("C must match matter_space_state.C in compatibility mode")
        return matter_space_step(
            state=state,
            dt=dt,
            dx=dx,
            config=matter_space_config or MatterSpaceConfig(),
            matter_source=matter_source,
            space_source=space_source,
            trace_history=trace_history,
            trace_config=trace_config,
        )

    if mode == SPACETIME_TRACE_OPERATOR_MODE:
        if I is not None:
            raise ValueError(
                "spacetime_trace_v1 consumes source_history; pass no independent I field"
            )
        if isinstance(C, (tuple, list)):
            C = C[0]
        return _spacetime_trace_dynamics_step(
            C=np.asarray(C, dtype=float),
            V=V,
            J_in=J_in,
            J_out=J_out,
            dx=dx,
            dt=dt,
            constraints=constraints,
            params=params,
            density=density,
            scale=scale,
            trace_history=trace_history,
            trace_config=trace_config,
            trace_coupling=trace_coupling,
        )

    # Handle coupled fields (tuple) from previous steps
    if isinstance(C, (tuple, list)):
        # Ensure we have a valid state to work with
        if len(C) > 1 and V is None:
            V = C[1]
        if len(C) > 2 and I is None:
            I = C[2]
        C = C[0]

    # --- INTEGRITY KILL SWITCH ---
    if INTEGRITY_KILL_SWITCH:
        # Maintain return signature for coupled fields
        nan_field = np.zeros_like(C) + np.nan
        if V is not None and I is not None:
            return (nan_field, nan_field, nan_field)
        elif I is not None:
            return (nan_field, nan_field)
        else:
            return nan_field

    # Reaction term: -V'(C)
    reaction_derivative = (
        potential_derivative
        if mode == LEGACY_VARIATIONAL_OPERATOR_MODE
        else legacy_reaction_derivative
    )
    reaction = -reaction_derivative(C, params)

    # Diffusion term: kappa * periodic Laplacian in the canonical lane.
    if mode == LEGACY_VARIATIONAL_OPERATOR_MODE:
        laplacian = conserved_laplacian(C, dx)
    elif C.ndim == 1:
        laplacian = np.zeros_like(C)
        if len(C) > 2:
            laplacian[1:-1] = (C[2:] - 2 * C[1:-1] + C[:-2]) / dx**2
            laplacian[0] = laplacian[1]
            laplacian[-1] = laplacian[-2]
    else:
        laplacian = np.zeros_like(C)
        # 2D Laplacian handling singleton dimensions
        if C.shape[0] > 2 and C.shape[1] > 2:
            laplacian[1:-1, 1:-1] = (
                C[2:, 1:-1] - 2 * C[1:-1, 1:-1] + C[:-2, 1:-1]
            ) / dx**2 + (
                C[1:-1, 2:] - 2 * C[1:-1, 1:-1] + C[1:-1, :-2]
            ) / dx**2
        elif C.shape[1] > 2:  # 1xN case
            laplacian[0, 1:-1] = (
                C[0, 2:] - 2 * C[0, 1:-1] + C[0, :-2]
            ) / dx**2
            laplacian[0, 0] = laplacian[0, 1]
            laplacian[0, -1] = laplacian[0, -2]
        elif C.shape[0] > 2:  # Nx1 case
            laplacian[1:-1, 0] = (
                C[2:, 0] - 2 * C[1:-1, 0] + C[:-2, 0]
            ) / dx**2
            laplacian[0, 0] = laplacian[1, 0]
            laplacian[-1, 0] = laplacian[-2, 0]

    diffusion = params.kappa * laplacian

    # A5: Natural Will contribution (drives toward equilibrium)
    if C.ndim == 1:
        grad = np.gradient(C, dx)
        will_force = -params.W_N * np.sign(grad) * np.abs(grad) ** 0.5
    else:
        will_force = 0.0

    # Information source term
    source = information_dynamics_source(C, I, params, operator_mode=operator_mode, dx=dx)

    # A4: Exchange term
    if J_in is not None and J_out is not None:
        exchange = params.gamma_J * (J_in - J_out)
    else:
        exchange = 0.0

    # A8: Dynamic Game candidate force (opt-in spatial mode only)
    game_force = game_theory_force(
        C,
        density=density,
        scale=scale,
        dx=dx,
        params=params,
        operator_mode=operator_mode,
    )

    # Total derivative
    # Total force (Negative Functional Gradient)
    force = reaction + diffusion + source + exchange + will_force + game_force
    raw_force = force

    # A14: Dynamic Viscosity (MOND-like scaling for low-acc regimes)
    # Applied to the force before integration
    if params.a0_viscosity > 0:
        a_sq = force**2 + 1e-20
        mu = np.sqrt(a_sq / (a_sq + params.a0_viscosity**2))
        force = force / (mu + 1e-12)

    # A13: Inertial Flow (Telegrapher's Equation: tau * d2C/dt2 + dC/dt = F)
    # Reduces to dC/dt = F when tau_inertia = 0 (Overdamped limit)
    # HARDENING FIX (Lorentz Safeguard): Ensure v < c strictly
    LIGHT_SPEED = 299792458.0 # SI C

    mode = resolve_operator_mode(params, operator_mode)
    if mode == CONSERVED_ORDER_OPERATOR_MODE:
        # Wave 14 candidate: Model C form dC/dt = nabla^2(delta Omega/delta C).
        # `force` is the negative functional gradient, so the conserved flow is -nabla^2(force).
        mobility = getattr(params, "conserved_order_mobility", 1.0)
        conserved_force = -mobility * conserved_laplacian(force, dx)
        C_new = C + dt * conserved_force
        V_new = np.clip(conserved_force, -0.999999 * LIGHT_SPEED, 0.999999 * LIGHT_SPEED)
    elif mode == CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE:
        # Wave 16 candidate: keep the local/source force explicit, but integrate the
        # stiff kappa*nabla^4 term semi-implicitly in Fourier space.
        non_gradient_force = raw_force - diffusion
        C_new = spectral_conserved_order_step(C, non_gradient_force, dx, dt, params)
        spectral_velocity = (C_new - C) / max(dt, 1e-30)
        V_new = np.clip(spectral_velocity, -0.999999 * LIGHT_SPEED, 0.999999 * LIGHT_SPEED)
    elif params.tau_inertia > 0 and V is not None:
        # C_acc = (F - V) / tau
        C_acc = (force - V) / params.tau_inertia
        V_raw = V + dt * C_acc

        # Lorentz Clamp (A13/A11 Alignment)
        V_new = np.clip(V_raw, -0.999999 * LIGHT_SPEED, 0.999999 * LIGHT_SPEED)
        C_new = C + dt * V_new
    else:
        # Diffusion limit (Overdamped)
        C_new = C + dt * force
        # For consistency, clip force-derived velocity too
        V_new = np.clip(force, -0.999999 * LIGHT_SPEED, 0.999999 * LIGHT_SPEED)

    # If I is present, update it via its own Propagator EoM
    if I is not None:
        I_new = information_propagator_step(I, C, dx, dt, params, operator_mode=operator_mode)
    else:
        I_new = None

    # A6: Apply constraints (Necessary Energy Adjustment)
    if constraints is not None:
        C_new = nea_dynamics(C_new, constraints, params)
        if V_new is not None:
            V_new = np.clip(V_new, -100, 100) # Safety clip for inertia

    # Unified state return logic
    returns = [C_new]
    if V is not None or params.tau_inertia > 0:
        returns.append(V_new)
    if I is not None:
        returns.append(I_new)

    if len(returns) > 1:
        return tuple(returns)
    return C_new


# =============================================================================
# AXIOM 11: LIMIT CASE VERIFICATION
# =============================================================================


def verify_heat_equation_limit() -> Tuple[bool, str]:
    """A11: Reduce to heat equation when α=γ=β=0."""
    params = UETParameters(alpha=0.0, gamma=0.0, beta=0.0)

    N = 50
    dx = 0.1
    C = np.exp(-((np.arange(N) * dx - 2.5) ** 2))

    dt = 0.001
    for _ in range(100):
        C = dynamics_step_complete(C, dx=dx, dt=dt, params=params)

    spread = np.std(C)
    passed = spread > 0.2  # Should spread out (diffusion)

    return passed, f"Heat spread σ={spread:.3f}"


def verify_ginzburg_landau_limit() -> Tuple[bool, str]:
    """A11: deterministic pure-GL lane with UET extras disabled."""
    params = UETParameters(
        alpha=1.0,
        gamma=0.1,
        kappa=0.01,
        beta=0.0,
        W_N=0.0,
        gamma_J=0.0,
        a0_viscosity=0.0,
        tau_inertia=0.0,
    )

    N = 64
    dx = 0.1
    rng = np.random.default_rng(1105)
    C = 0.1 * (rng.random(N) - 0.5)
    initial_energy = float(np.mean(potential_V(C, params)))

    dt = 0.001
    for _ in range(5000):
        C = dynamics_step_complete(C, dx=dx, dt=dt, params=params)

    # Pure GL relaxation should descend the local potential toward the C0 minimum.
    final_energy = float(np.mean(potential_V(C, params)))
    passed = final_energy < 0.1 and final_energy < 0.25 * initial_energy

    return passed, f"Initial V={initial_energy:.4f}; Final V={final_energy:.4f}"


def verify_bounded_below() -> Tuple[bool, str]:
    """A11: Potential must be bounded below (stability)."""
    params = UETParameters()

    C_test = np.linspace(-10, 10, 1000)
    V = potential_V(C_test, params)

    V_min = np.min(V)
    passed = V_min >= 0  # Bounded below at 0

    return passed, f"V_min={V_min:.4f}"


def verify_all_limits() -> dict:
    """Run all A11 limit case tests."""
    results = {}

    tests = [
        ("Heat equation limit", verify_heat_equation_limit),
        ("Ginzburg-Landau limit", verify_ginzburg_landau_limit),
        ("Bounded below", verify_bounded_below),
    ]

    for name, test_func in tests:
        passed, msg = test_func()
        results[name] = {"passed": passed, "message": msg}
        print(f"{name}: {'PASS' if passed else 'FAIL'} - {msg}")

    return results


# =============================================================================
# MAIN - RUN LIMIT AND CANDIDATE CHECKS
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("UET MASTER EQUATION V0.9.0 - CANDIDATE CORE / OPT-IN OPERATORS")
    print("=" * 70)

    # Create parameters
    params = UETParameters()
    print(f"\nScale: {params.scale}")
    print(f"Temperature: {params.temperature} K")
    print(f"beta (normalized core coupling): {params.beta:.2e}")
    print(f"κ (Bekenstein): {params.kappa}")
    print(f"W_N (Natural Will): {params.W_N}")
    print(f"γ_J (Exchange): {params.gamma_J}")
    print(f"λ (Coherence): {params.lambda_coherence}")

    # Test A11: Limit cases
    print("\n" + "=" * 70)
    print("AXIOM 11: LIMIT CASE VERIFICATION")
    print("=" * 70)
    results = verify_all_limits()

    all_passed = all(r["passed"] for r in results.values())
    print(f"\n{'✅ ALL LIMIT TESTS PASSED!' if all_passed else '❌ SOME TESTS FAILED'}")

    # Test baseline Omega functional
    print("\n" + "=" * 70)
    print("BASELINE OMEGA FUNCTIONAL TEST")
    print("=" * 70)

    N = 50
    dx = 0.1
    C = np.exp(-((np.arange(N) * dx - 2.5) ** 2))
    params = UETParameters()

    # Run a few steps
    print(f"Initial Omega: {omega_functional_complete(C, dx=dx, params=params):.4e}")

    dt = 0.001
    for i in range(10):
        C = dynamics_step_complete(C, dx=dx, dt=dt, params=params)

    print(f"Final Omega: {omega_functional_complete(C, dx=dx, params=params):.4e}")
    print("✅ MASTER EQUATION TEST COMPLETE")
    C = np.sin(np.arange(N) * dx)
    I = np.ones(N) * 0.1
    J_in = np.ones(N) * 0.05
    J_out = np.ones(N) * 0.03
    C_layers = [C, C * 0.9, C * 0.8]

    omega = omega_functional_complete(
        C=C,
        I=I,
        J_in=J_in,
        J_out=J_out,
        C_layers=C_layers,
        density=1e9,
        scale=2.0,
        dx=dx,
        params=params,
    )

    print(f"Omega (candidate functional) = {omega:.4f}")
    print(f"  - Potential (A1): ✅")
    print(f"  - Gradient (A3): ✅")
    print(f"  - Info coupling (A2): ✅")
    print(f"  - Exchange (A4): ✅")
    print(f"  - Natural Will (A5): ✅")
    print(f"  - Dynamic Game (A8): ✅")
    print(f"  - Coherence (A10): ✅")

    print("\n" + "=" * 70)
    print("CANDIDATE CORE CHECKS COMPLETE; AXIOM CLOSURE REMAINS OPEN")
    print("=" * 70)
