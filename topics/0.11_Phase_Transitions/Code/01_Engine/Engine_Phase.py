"""
UET Phase Transition Engine (Spectral Cahn-Hilliard)
====================================================
Implements robust phase separation dynamics using Spectral Methods.
Replacing mock logic with real Cahn-Hilliard physics.

Physics:
    dC/dt = M * ∇²(δF/δC)
    F[C] = ∫ [ f(C) + (κ/2)|∇C|² ] dV
    μ = δF/δC = f'(C) - κ∇²C

Compliance:
    - 5x4 Grid Architecture
    - UETParameters (kappa, alpha, beta)
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


import sys
import numpy as np
from pathlib import Path
from dataclasses import dataclass

try:
    from docs.core.uet_base_solver import UETBaseSolver
    from docs.core.uet_master_equation import UETParameters
except ImportError:
    # Fallback for direct execution testing
    pass


class UETPhaseEngine(UETBaseSolver):
    """
    Spectral Cahn-Hilliard Solver for Phase Transitions.
    Real physics implementation using FFT for spatial derivatives.
    """

    def __init__(
        self,
        nx: int = 64,
        ny: int = 64,
        dt: float = 0.01,
        temperature: float = 0.05,
        name: str = "PhaseEngine_Spectral",
        params: UETParameters = None,
    ):
        # Default Params if None
        if params is None:
            # Alpha < 0 for phase separation (Double Well)
            # Gamma is implicitly 1.0 in V(C) = alpha/2 C^2 + gamma/4 C^4
            # Kappa reduced to 0.002 to allow spinodal decomposition on L=1 grid
            # Critical k_c = sqrt(1/kappa) = 22.3. k_min = 6.28. 6.28 < 22.3 -> Unstable -> Growth.
            params = UETParameters(kappa=0.002, alpha=-1.0, beta=1.0)

        super().__init__(
            nx=nx,
            ny=ny,
            dt=dt,
            params=params,
            name=name,
            topic="0.11_Phase_Transitions",
            pillar="01_Engine",
        )

        self.temperature = temperature
        self.mobility = 1.0
        self.gamma = 1.0  # Coefficient for C^4 term

        # Initialize Field with small noise (Disordered state)
        self.C = np.random.randn(nx, ny) * 0.01

        # Precompute Spectral Operators
        self._setup_spectral()

    def _setup_spectral(self):
        """Prepare FFT wavevectors for Laplacian calculation."""
        # Wavevectors kx, ky
        kx = np.fft.fftfreq(self.nx, d=self.dx) * 2 * np.pi
        ky = np.fft.fftfreq(self.ny, d=self.dy) * 2 * np.pi
        self.Kx, self.Ky = np.meshgrid(kx, ky, indexing="ij")

        # Laplacian Operator in Fourier Space: -k^2
        self.K2 = self.Kx**2 + self.Ky**2
        self.K4 = self.K2**2  # Bi-harmonic operator

    def compute_chemical_potential(self) -> np.ndarray:
        """
        Compute μ = f'(C) - κ∇²C
        f(C) = αC + γC^3
        """
        # 1. Bulk derivative f'(C)
        df_dC = self.params.alpha * self.C + self.gamma * self.C**3

        # 2. Gradient term -κ∇²C
        # FFT(∇²C) = -k² * FFT(C)
        C_hat = np.fft.fft2(self.C)
        lap_C_hat = -self.K2 * C_hat
        lap_C = np.fft.ifft2(lap_C_hat).real

        grad_term = -self.params.kappa * lap_C

        return df_dC + grad_term

    def step(self, step_idx: int = 0):
        """
        Time evolution step using Semi-Implicit Spectral Method.

        Explicit: Non-linear terms (C^3)
        Implicit: Linear terms (Diffusion, Bi-harmonic)

        Equation: dC/dt = M∇²(αC + γC^3 - κ∇²C)
        Fourier: dC_k/dt = -Mk² [ αC_k + γ(C³)_k + κk²C_k ]

        Semi-Implicit Update:
        (1 + dt*M*κ*k⁴) C_new = C_old - dt*M*k² [ αC_old + γ(C³)_old ]
        (Note: We keep αC explicit for simplicity, or could make it implicit)
        """

        # 1. Compute Non-Linear Term in Real Space
        nonlinear_term = self.params.alpha * self.C + self.gamma * self.C**3

        # 2. Transform to Fourier Space
        C_hat = np.fft.fft2(self.C)
        NL_hat = np.fft.fft2(nonlinear_term)

        # 3. Add Thermal Noise (Langevin)
        noise_hat = 0
        if self.temperature > 0:
            noise = np.random.randn(self.nx, self.ny) * np.sqrt(
                2 * self.temperature * self.dt
            )
            noise_hat = np.fft.fft2(noise)

        # 4. Semi-Implicit Update
        # RHS = C_hat - dt * M * k^2 * NL_hat + noise
        # LHS Operator = 1 + dt * M * kappa * k^4

        numerator = C_hat - self.dt * self.mobility * self.K2 * NL_hat + noise_hat
        denominator = 1.0 + self.dt * self.mobility * self.params.kappa * self.K4

        C_new_hat = numerator / denominator

        # 5. Transform back
        self.C = np.fft.ifft2(C_new_hat).real

        # 6. Logging & Admin
        self.time += self.dt
        self.step_count += 1

        if self.logger and step_idx % 10 == 0:
            self._log_current_state(step_idx)

    def compute_bec_tc(self, N: int, omega: float) -> float:
        """
        Compute Critical Temperature for Bose-Einstein Condensate.
        Tc = (hbar * omega / kB) * (N / Zeta(3))^(1/3)
        """
        # Physical constants (UET Standard)
        HBAR = 1.054571817e-34
        K_B = 1.380649e-23
        zeta_3 = 1.2020569

        # Tc Formula for harmonic trap
        Tc = (HBAR * omega / K_B) * (N / zeta_3) ** (1 / 3)
        return float(Tc)

    def get_domain_count(self) -> int:
        """Public API for domain counting."""
        return self._count_domains()

    def get_extra_metrics(self):
        """Phase-specific metrics."""
        return {
            "order_parameter": float(np.mean(np.abs(self.C))),
            "domain_count": self._count_domains(),
            "max_density": float(np.max(self.C)),
        }

    def _count_domains(self) -> int:
        """Estimate domains via zero-crossings."""
        binary = (self.C > 0).astype(int)
        h_cross = np.sum(np.abs(np.diff(binary, axis=0)))
        v_cross = np.sum(np.abs(np.diff(binary, axis=1)))
        return int(h_cross + v_cross)


# =============================================================================
# VERIFICATION DEMO
# =============================================================================
if __name__ == "__main__":
    print("🚀 Running UET Phase Engine Demo (Spectral)...")
    engine = UETPhaseEngine(nx=64, ny=64, dt=0.01)

    print(f"Initial Order: {engine.get_extra_metrics()['order_parameter']:.4f}")

    for i in range(50):
        engine.step(i)
        if i % 10 == 0:
            metrics = engine.get_extra_metrics()
            print(
                f"Step {i}: Order={metrics['order_parameter']:.4f}, Domains={metrics['domain_count']}"
            )

    print("✅ Demo Complete.")
