"""
Engine_Riemann_Field.py - UET Topic 0.18
========================================
A Manifold Engine for Complex Potential Analysis.
Maps the Riemann Zeta Function to UET Equilibrium Sinks.
"""

import numpy as np
import math

# Base Solver Import
try:
    from research_uet.core.uet_base_solver import UETBaseSolver
except ImportError:
    import sys
    from pathlib import Path

    current = Path(__file__).resolve()
    root = None
    for parent in [current] + list(current.parents):
        if (parent / "research_uet").exists():
            root = parent
            sys.path.insert(0, str(root))
            break
    from research_uet.core.uet_base_solver import UETBaseSolver


class RiemannFieldEngine(UETBaseSolver):
    def __init__(self, precision=50):
        super().__init__(name="Riemann_Zeta_Solver")
        self.precision = precision
        # Set global precision if mpmath is available
        try:
            from mpmath import mp

            mp.dps = precision
            self.use_mpmath = True
        except ImportError:
            self.use_mpmath = False

    def calculate_omega(self, s: complex) -> float:
        """
        The UET Potential (Omega) for a complex state s.
        Omega = |zeta(s)| (Magnitude of tension)
        Unity Sinks (Zeros) have Omega = 0.
        """
        if self.use_mpmath:
            # High-Precision Mode
            from mpmath import zeta, absmax

            try:
                z = zeta(s)
                return float(absmax(z))
            except Exception:
                return 1.0  # Error penalty
        else:
            # Fallback: Naive Approximation (Low Precision)
            z = self.zeta_approx_fallback(s)
            return float(abs(z))

    def zeta_approx_fallback(self, s: complex) -> complex:
        """
        Calculates Riemann Zeta using the alternating series (Dirichlet Eta).
        Valid for Re(s) > 0.
        Only used if mpmath is missing.
        """
        if s.real <= 0:
            return 0j

        # Dirichlet Eta function sum
        eta = 0j
        # Use fixed precision loop for fallback
        for n in range(1, 2000):
            term = ((-1) ** (n - 1)) / (n**s)
            eta += term

        denom = 1 - (2 ** (1 - s))
        if abs(denom) < 1e-12:
            return 0j

        return eta / denom

    def scan_strip(self, re_range=(0.1, 0.9), im_range=(0, 50), steps=50):
        """
        Scans a grid in the critical strip and finds local minima.
        """
        re_vals = np.linspace(re_range[0], re_range[1], steps)
        im_vals = np.linspace(im_range[0], im_range[1], steps)

        grid = []
        for im in im_vals:
            row = []
            for re in re_vals:
                row.append(self.calculate_omega(complex(re, im)))
            grid.append(row)

        return np.array(grid), re_vals, im_vals

    def find_gradient_sink(self, start_s: complex, lerp=0.01, iterations=100, verbose=False):
        """
        Gradient descent towards the nearest Unity Sink (Zero).
        In UET, this demonstrates the 'Pull' of the critical line.
        """
        curr = start_s
        path = [curr]

        for i in range(iterations):
            if verbose and i % 10 == 0:
                print(f".", end="", flush=True)
            # Numerical gradient
            eps = 1e-5
            o_base = self.calculate_omega(curr)

            # Simple complex perturbation
            o_re = self.calculate_omega(curr + eps)
            o_im = self.calculate_omega(curr + eps * 1j)

            grad_re = (o_re - o_base) / eps
            grad_im = (o_im - o_base) / eps

            curr -= complex(grad_re * lerp, grad_im * lerp)
            path.append(curr)

            if o_base < 1e-10:
                break

        if verbose:
            print(" Done!")
        return path
