"""
UET Econophysics Engine - 5x4 Grid Compliant
============================================
Axiomatic Market Dynamics via Self-Organized Criticality (SOC).

Standardized to ensure Volatility Clustering stylized fact is reproduced.
Axiom 5 (Natural Will): Temporal persistence of informational flow.
"""

from docs import ROOT_PATH
from pathlib import Path
current_path = Path(__file__).resolve()
root_path = ROOT_PATH
from docs import ROOT_PATH
root_path = ROOT_PATH
import numpy as np
import sys
from pathlib import Path

# Path finding


try:
    from Engine_Complexity import UETComplexityEngine
except ImportError:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "UETComplexityEngine", str(current_path.parent / "Engine_Complexity.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETComplexityEngine = module.UETComplexityEngine


class UETEconophysicsEngine(UETComplexityEngine):
    """
    Market Solver.
    dV = -delta_Omega + Momentum.
    """

    def __init__(self, nx=32, ny=32, initial_price=100.0, **kwargs):
        super().__init__(nx=nx, ny=ny, name="UET_Econ_SOC", **kwargs)
        self.price = initial_price
        self.price_history = [initial_price]
        self.I = np.ones((ny, nx)) * 0.1
        self.momentum = 0.0

    def step(self, step_idx: int = 0):
        # 1. Informational Attraction (Biased news drops)
        weights = np.maximum(self.I.flatten(), 1e-15)
        weights /= weights.sum()
        idx = np.random.choice(len(weights), p=weights)
        ry, rx = divmod(idx, self.nx)
        self.C[ry, rx] += 1.0

        # 2. Run Relaxation (Avalanche)
        omega_pre = self.engine.compute_omega(self.C, dx=self.dx, I=self.I)
        stable, size, iter_count = False, 0, 0
        while not stable and iter_count < 1000:
            unstable = self.C >= self.threshold
            indices = np.argwhere(unstable)
            if len(indices) == 0:
                stable = True
            else:
                size += len(indices)
                for y, x in indices:
                    self.C[y, x] -= 4.0
                    for dy, dx in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < self.ny and 0 <= nx < self.nx:
                            self.C[ny, nx] += 1.0
            iter_count += 1

        if size > 0:
            self.avalanche_sizes.append(size)
        omega_post = self.engine.compute_omega(self.C, dx=self.dx, I=self.I)
        self.current_value = omega_pre - omega_post

        # 3. Axiomatic Return with Momentum (Axiom 5: Persistence)
        # Persistence of information flux creates clustering.
        self.I *= 0.98  # High persistence

        if self.current_value > 0:
            self.I[ry, rx] += self.current_value / 20.0

        # Background coupling + Momentum
        # r = flux + momentum
        background_flux = np.mean(self.I * self.C) * 0.1

        # Total change (Avalanche shock + Background + Momentum)
        # We add self.momentum to sustain high-volatility periods.
        change_pct = (
            (self.current_value * 50.0) + background_flux + (self.momentum * 0.5)
        )

        # Scale to manageable magnitude
        returns = change_pct / 10000.0
        self.price *= 1.0 + returns

        # Update Momentum for next step (Abs returns persistence)
        self.momentum = 0.90 * self.momentum + 0.10 * abs(returns) * 10000.0

        # Housekeeping
        self.time += self.dt
        self.step_count += 1
        self.price_history.append(self.price)
        if self.logger:
            self._log_current_state(step_idx)

    def get_market_price(self):
        return self.price

    def get_market_volatility(self):
        return self.momentum / 10.0

    def get_extra_metrics(self):
        m = super().get_extra_metrics()
        m["price"], m["momentum"], m["value_delta"] = (
            self.price,
            self.momentum,
            self.current_value,
        )
        return m


if __name__ == "__main__":
    solver = UETEconophysicsEngine(nx=20, ny=20)
    for i in range(200):
        solver.step(i)
    print(f"Final Price: {solver.price:.2f}")
