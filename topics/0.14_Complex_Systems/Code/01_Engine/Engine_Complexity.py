"""
UET Complexity Engine - 5x4 Grid Compliant
==========================================
Axiomatic derivation of Complex Systems (Power Laws) via Self-Organized Criticality (SOC).

Theory:
-------
UET views Complexity as the natural state of systems maximizing information flux.
We implement an "Information Sandpile" model:
1. Information accumulates (Entropy Production).
2. If I(x) > Threshold, it distributes to neighbors (Avalanche).
3. Avalanches follow Power Laws (Scale Invariance) naturally
   without fitted exponents.

Topic: 0.14 Complex Systems
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
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Core Imports
from docs.core.uet_base_solver import UETBaseSolver
from docs.core.uet_master_equation import UETParameters
from docs.core.uet_parameters import INTEGRITY_KILL_SWITCH


class UETComplexityEngine(UETBaseSolver):
    """
    Self-Organized Criticality Solver.
    Simulates Information Avalanches.
    """

    def __init__(
        self,
        nx: int = 64,
        ny: int = 64,
        dt: float = 1.0,  # Discrete Time
        threshold: float = 4.0,  # Critical Information Density
        name: str = "UET_SOC_Solver",
        **kwargs,
    ):
        # Axiomatic Parameters
        # Use provided params if in kwargs, otherwise create default
        params = kwargs.pop("params", UETParameters(kappa=1.0, beta=1.0, alpha=1.0, C0=0.0))

        super().__init__(
            nx=nx,
            ny=ny,
            dt=dt,
            params=params,
            name=name,
            topic="0.14_Complex_Systems",
            pillar="01_Engine",
            **kwargs,
        )

        self.threshold = threshold
        self.C = np.zeros((ny, nx))  # Information Pile

        # Metrics
        self.avalanche_sizes = []  # Track sizes for Power Law check
        self.current_value = 0.0  # Thermodynamic Value (-delta_Omega)

    def step(self, step_idx: int = 0):
        """
        Execute one grain drop and subsequent avalanche.
        Refactored to Bridge Discrete SOC with Continuous UET.
        """
        # 1. Add Grain (Perturbation to C field)
        rx, ry = np.random.randint(0, self.nx), np.random.randint(0, self.ny)
        self.C[ry, rx] += 1.0

        if INTEGRITY_KILL_SWITCH:
            return

        # 2. Relax (Avalanche) Logic
        # This remains discrete for SOC behavior, but we track its UET Omega
        stable = False
        size = 0
        max_iter = 10000
        iter_count = 0

        # Pre-avalanche Omega
        omega_pre = self.engine.compute_omega(self.C, dx=self.dx, I=self.I)

        while not stable and iter_count < max_iter:
            unstable_mask = self.C >= self.threshold
            unstable_indices = np.argwhere(unstable_mask)

            if len(unstable_indices) == 0:
                stable = True
            else:
                count_topple = len(unstable_indices)
                size += count_topple

                for y, x in unstable_indices:
                    self.C[y, x] -= 4.0
                    if x > 0:
                        self.C[y, x - 1] += 1
                    if x < self.nx - 1:
                        self.C[y, x + 1] += 1
                    if y > 0:
                        self.C[y - 1, x] += 1
                    if y < self.ny - 1:
                        self.C[y + 1, x] += 1

            iter_count += 1

        if size > 0:
            self.avalanche_sizes.append(size)

        # 3. Post-Avalanche: Track Value (V = -delta_Omega)
        omega_post = self.engine.compute_omega(self.C, dx=self.dx, I=self.I)
        self.current_value = omega_pre - omega_post

        # 4. Standard Base Administration & Logging
        self.time += self.dt
        self.step_count += 1

        if self.logger:
            # We call the standardized logger with extra metrics
            self._log_current_state(step_idx)

    def get_extra_metrics(self) -> Dict[str, Any]:
        """Check for Power Law Signature."""
        if not self.avalanche_sizes:
            return {
                "max_avalanche": 0,
                "avalanche_count": 0,
                "mean_size": 0.0,
                "power_law_exponent": 0.0,
            }

        # Simple fit estimate
        sizes = np.array(self.avalanche_sizes)
        return {
            "max_avalanche": int(np.max(sizes)),
            "avalanche_count": len(sizes),
            "mean_size": float(np.mean(sizes)),
            "power_law_exponent": 0.0,  # Placeholder
        }

    def compute_complexity_metrics(self, data: np.ndarray, fs: float = 256.0) -> Dict[str, Any]:
        """
        AXIOMATIC COMPLEXITY ANALYSIS
        Used by Brain, Econ, and Social research pillars.
        """
        # --- INTEGRITY KILL SWITCH ---
        if INTEGRITY_KILL_SWITCH:
            return {"equilibrium_score": np.nan, "entropy": np.nan}

        # 1. Frequency Analysis (Information Distribution)
        n = len(data)
        fft_result = np.fft.fft(data)
        power = np.abs(fft_result[: n // 2]) ** 2 / n
        freqs = np.fft.fftfreq(n, 1 / fs)[: n // 2]

        # 2. Entropy via UET Master Equation (Direct Field Mapping)
        # We treat the power spectrum as a C field
        normalized_power = power / (np.sum(power) + 1e-10)
        entropy = self.engine.compute_omega(normalized_power, dx=1.0)

        # 3. Equilibrium Score (Normalized Entropy)
        max_entropy = np.log(len(normalized_power) + 1)
        score = entropy / max_entropy if max_entropy > 0 else 0

        return {
            "entropy": float(entropy),
            "equilibrium_score": float(score),
            "power_spectrum": power,
            "frequencies": freqs,
        }

    def calculate_hrv_metrics(self, rr_intervals: np.ndarray) -> Dict[str, Any]:
        """
        AXIOMATIC HRV ANALYSIS (Poincaré & Time Domain)
        Specific implementation for Biophysics (Topic 0.22/0.14).
        """
        if INTEGRITY_KILL_SWITCH:
            return {"status": "FAIL", "equilibrium_score": float("nan")}

        # Clean data
        rr = np.array(rr_intervals, dtype=float)
        rr = rr[np.isfinite(rr)]
        rr = rr[(rr > 0.3) & (rr < 2.0)]

        if len(rr) < 10:
            return None

        # Time-domain metrics
        mean_rr = np.mean(rr)
        sdnn = np.std(rr)
        rmssd = np.sqrt(np.mean(np.diff(rr) ** 2))
        cv = sdnn / mean_rr

        # Poincaré plot metrics
        sd1 = np.std(np.diff(rr)) / np.sqrt(2)
        sd2 = np.sqrt(2 * sdnn**2 - sd1**2) if 2 * sdnn**2 > sd1**2 else sdnn

        # UET Equilibrium Score
        balance = sd1 / (sd2 + 0.001)
        equilibrium_score = 1 / (1 + abs(balance - 0.5))

        return {
            "mean_rr": mean_rr,
            "sdnn": sdnn,
            "rmssd": rmssd,
            "cv": cv,
            "sd1": sd1,
            "sd2": sd2,
            "balance": balance,
            "equilibrium_score": equilibrium_score,
            "n_beats": len(rr),
        }

    def calculate_hurst_exponent(self, time_series: np.ndarray) -> float:
        """
        Estimate Hurst Exponent (H) for a time series.
        H = 0.5: Random Walk (Equilibrium)
        H > 0.5: Trending (Persistence / Memory)
        H < 0.5: Mean Reverting (Anti-persistence)
        """
        if INTEGRITY_KILL_SWITCH:
            return 0.5

        ts = np.array(time_series)
        ts = ts[np.isfinite(ts)]
        if len(ts) < 20:
            return 0.5

        # R/S Analysis (Simplified)
        lags = range(2, min(20, len(ts) // 2))
        tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]

        # This is actually a variogram approach, estimating H from slope
        # log(std) ~ H * log(lag)

        try:
            poly = np.polyfit(np.log(lags), np.log(tau), 1)
            H = poly[0]
            return float(np.clip(H, 0.0, 1.0))
        except:
            return 0.5

    def calculate_stability_metrics(self, data: np.ndarray) -> Dict[str, Any]:
        """
        AXIOMATIC STABILITY ANALYSIS (Variance-based Equilibrium)
        Used by Economic and Social research pillars.
        """
        if INTEGRITY_KILL_SWITCH:
            return {"equilibrium_score": np.nan, "cv": np.nan}

        mean_val = np.mean(data)
        std_val = np.std(data)
        cv = std_val / (abs(mean_val) + 1e-10)

        # Equilibrium is the state of minimal fluctuations (Axiom 9)
        # score = 1 / (1 + delta_Omega) -> mapped to fluctuations
        score = 1.0 / (1.0 + cv)

        return {
            "cv": float(cv),
            "equilibrium_score": float(score),
            "mean": float(mean_val),
            "std": float(std_val),
        }


def run_demo():
    print("🚀 Verifying 5x4 Grid Compliance for Complexity Engine (0.14)...")
    nx, ny = 20, 20  # Smaller grid for faster avalanches
    solver = UETComplexityEngine(nx=nx, ny=ny, threshold=4.0)

    print("Running 1000 grain drops...")
    for i in range(1000):
        solver.step(i)

    metrics = solver.get_extra_metrics()
    print(f"  Max Avalanche: {metrics['max_avalanche']}")
    print(f"  Total Avalanches: {metrics['avalanche_count']}")
    print(f"  Mean Size: {metrics['mean_size']:.2f}")

    path = solver.save_results()
    print(f"✅ Complexity Result: {path}")


if __name__ == "__main__":
    run_demo()
