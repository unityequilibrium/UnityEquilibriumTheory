"""
UET Base Solver
===============
Abstract Base Class for all UET simulations.
Standardizes the interaction between:
1. Physics Engine (UETMasterEquation)
2. Glass Box Logger (UETMetricLogger)
3. Simulation Loop

All Topic Solvers (Fluid, Quantum, Cosmo) must inherit from this.
"""

import numpy as np
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

# Ensure generic imports work if run standalone
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from docs.core.uet_master_equation import (
    FINITE_CONE_C_OPERATOR_MODE,
    MATTER_SPACE_OPERATOR_MODE,
    SPACETIME_TRACE_OPERATOR_MODE,
    UETParameters,
    UETMasterEquation,
)
from docs.core.uet_glass_box import UETMetricLogger
from docs.core.uet_parameters import INTEGRITY_KILL_SWITCH


class UETBaseSolver(ABC):
    """
    Standardizes the UET Simulation Lifecycle:
    Init -> Engine Setup -> Logger Setup -> Run Loop -> Log Step -> Save
    """

    def __init__(
        self,
        # Grid Props
        nx: int = 64,
        ny: int = 64,
        lx: float = 1.0,
        ly: float = 1.0,
        dt: float = 0.001,
        # Physics Props
        params: Optional[UETParameters] = None,
        # Admin Props
        name: str = "UET_Simulation",
        topic: str = "General",  # New: Identify the research topic
        pillar: str = "01_Engine",  # Identify the 5x4 Pillar (e.g. "03_Research")
        stable_path: bool = False,  # Whether to use a fixed folder name (no timestamp)
        log_dir: str = None,  # Deprecated: Let PathManager handle it
        **kwargs,
    ):
        self.nx = nx
        self.ny = ny
        self.lx = lx
        self.ly = ly
        self.dx = lx / nx
        self.dy = ly / ny
        self.dt = dt
        self.stable_path = stable_path
        self.metadata = kwargs  # Store extra research params

        # 1. Parameters (Single Source of Truth)
        if params is None:
            try:
                from docs.core.uet_parameters import get_params

                # Attempt to map topic string to numerical key if possible
                topic_key = topic.split("_")[0] if "_" in topic else topic
                self.params = get_params(topic_key)
            except Exception as e:

                print(f"⚠️ [UETBaseSolver] Warning: Could not load params for topic {topic}: {e}")
                # Fallback to safe defaults
                self.params = UETParameters(
                    kappa=0.1, beta=0.1, scale="fallback", origin="Error_Recovery"
                )
        else:
            self.params = params

        # --- INTEGRITY KILL SWITCH (The Truth Auditor) ---
        if INTEGRITY_KILL_SWITCH:
            print("💀 [UET_KILL_ENGINE] ACTIVE: Sabotaging Solver Integrity...")
            # Sabotage all primary coupling and astrophysical constants
            # Setting to NaN or 0.0 to break all dependent research
            self.params = UETParameters(
                kappa=np.nan,
                beta=np.nan,
                alpha=np.nan,
                C0=np.nan,
                RHO_UNITY=np.nan,
                RATIO_0=np.nan,
                GAMMA_UET=np.nan,
            )

        # 2. Physics Engine (The Core)
        self.engine = UETMasterEquation(params=self.params)

        # 3. Fields (Initialized to Equilibrium)
        self.C = np.ones((ny, nx)) * self.params.C0
        self.I = np.zeros((ny, nx))
        self.trace_observable = np.zeros((ny, nx))
        self.space_response = np.zeros((ny, nx))
        self.space_rate = np.zeros((ny, nx))
        self.matter_rate = np.zeros((ny, nx))

        # State Tracking
        self.time = 0.0
        self.step_count = 0
        self.constraints = None

        # 4. Logger (The Glass Box)
        self.logger = None
        category = kwargs.get("category", "log")
        self._setup_logger(name, topic, pillar, log_dir, category)

    def _setup_logger(self, name: str, topic: str, pillar: str, output_dir: str, category: str = "log"):
        """Initialize the Glass Box Logger."""
        try:
            # Connect to Central Path Manager
            from docs.core.uet_glass_box import UETPathManager

            if output_dir:
                # Custom override (Manual)
                target_path = Path(output_dir)
            else:
                # Standard System Path
                target_path = UETPathManager.get_result_dir(
                    topic, name, pillar, stable=self.stable_path
                )

            self.logger = UETMetricLogger(
                name, output_dir=str(target_path), flat_mode=self.stable_path,
                topic_id=topic, category=category
            )

            # Log Metadata immediately
            self.logger.set_metadata(
                {
                    "nx": self.nx,
                    "ny": self.ny,
                    "dt": self.dt,
                    "kappa": self.params.kappa,
                    "beta": self.params.beta,
                    "alpha": self.params.alpha,
                    "C0": self.params.C0,
                    "phi_loss": self.params.phi_loss,
                }
            )
        except Exception as e:
            print(f"⚠️ [UETBaseSolver] Warning: Logger load failed: {e}")

    def step(self, step_idx: int = 0):
        """
        Execute one generic UET time step.
        """
        # 1. Physics Step (Core)
        # Handle cases where the engine returns coupled fields (tuple)
        active_mode = getattr(self.params, "operator_mode", "legacy_local")
        if active_mode == SPACETIME_TRACE_OPERATOR_MODE:
            result = self.engine.step(
                self.C, dt=self.dt, dx=self.dx, I=None, constraints=self.constraints
            )
        elif active_mode in {MATTER_SPACE_OPERATOR_MODE, FINITE_CONE_C_OPERATOR_MODE}:
            result = self.engine.step(
                self.C,
                dt=self.dt,
                dx=self.dx,
                I=None,
                constraints=None,
                operator_mode=active_mode,
                space_response=self.space_response,
                space_rate=self.space_rate,
                matter_rate=self.matter_rate,
                finite_cone_c_config=getattr(self.engine, "finite_cone_c_config", None),
            )
        else:
            result = self.engine.step(
                self.C, dt=self.dt, dx=self.dx, I=self.I, constraints=self.constraints
            )

        if hasattr(result, "C") and hasattr(result, "trace_observable"):
            self.C = result.C
            self.trace_observable = result.trace_observable
            self.metadata["energy_ledger"] = result.energy_ledger
            self.metadata["diagnostics"] = result.diagnostics
            if result.V is not None:
                self.metadata["V_field"] = result.V
            if getattr(result, "space_response", None) is not None:
                self.space_response = result.space_response
            if getattr(result, "space_rate", None) is not None:
                self.space_rate = result.space_rate
            if active_mode == FINITE_CONE_C_OPERATOR_MODE and getattr(result, "V", None) is not None:
                self.matter_rate = result.V
            self.I = None
        elif isinstance(result, (tuple, list)):
            # Legacy core returns (C, V, I); keep that adapter explicit.
            self.C = result[0]
            if len(result) > 1:
                if len(result) > 2 or self.I is None:
                    self.metadata["V_field"] = result[1]
                else:
                    # Historical I-only tuple is (C, I).
                    self.I = result[1]
            if len(result) > 2:
                self.I = result[2]
        else:
            self.C = result

        # 2. Domain Specific Hooks (Child classes override this)
        self.post_step_physics()

        # 3. Administration
        self.time += self.dt
        self.step_count += 1

        # 4. Logging
        if self.logger:
            self._log_current_state(step_idx)

    def post_step_physics(self):
        """
        Hook for subclasses to apply Boundary Conditions or update derived fields.
        """
        pass

    def _log_current_state(self, step_idx: int):
        """
        Compute standard UET metrics and log them.
        Subclasses can provide extra metrics via `get_extra_metrics()`.
        """
        # Handle cases where Fields are coupled (Tuples)
        C_field = self.C[0] if isinstance(self.C, tuple) else self.C
        active_mode = getattr(self.params, "operator_mode", "legacy_local")
        if active_mode in {SPACETIME_TRACE_OPERATOR_MODE, MATTER_SPACE_OPERATOR_MODE, FINITE_CONE_C_OPERATOR_MODE}:
            I_field = np.zeros_like(C_field, dtype=float)
            if self.trace_observable is not None:
                cell_volume = self.dx if C_field.ndim == 1 else self.dx * self.dy
                self.metadata["trace_observable_integral"] = float(
                    np.sum(self.trace_observable) * cell_volume
                )
            if active_mode in {MATTER_SPACE_OPERATOR_MODE, FINITE_CONE_C_OPERATOR_MODE}:
                self.metadata["space_response_norm"] = float(
                    np.linalg.norm(self.space_response)
                )
                self.metadata["space_rate_norm"] = float(np.linalg.norm(self.space_rate))
            if active_mode == FINITE_CONE_C_OPERATOR_MODE:
                self.metadata["matter_rate_norm"] = float(np.linalg.norm(self.matter_rate))
        else:
            I_field = self.I[0] if isinstance(self.I, tuple) else self.I

        # Calculate Gradients for Omega
        # Robust check: Need at least 2 elements in the dimension to calculate gradient
        grad_sq = np.zeros_like(C_field)
        if C_field.ndim == 2:
            ny_curr, nx_curr = C_field.shape
            if ny_curr > 2 and nx_curr > 2:
                grad_y, grad_x = np.gradient(C_field, self.dy, self.dx)
                grad_sq = grad_x**2 + grad_y**2
            elif nx_curr > 2:
                # 1D Horizontal in 2D shape (1, nx)
                grad_x = np.gradient(C_field[0, :], self.dx)
                grad_sq[0, :] = grad_x**2
            elif ny_curr > 2:
                # 1D Vertical in 2D shape (ny, 1)
                grad_y = np.gradient(C_field[:, 0], self.dy)
                grad_sq[:, 0] = grad_y**2
        elif C_field.ndim == 1:
            if self.nx > 1:
                grad_x = np.gradient(C_field, self.dx)
                grad_sq = grad_x**2
            elif self.ny > 1:
                grad_y = np.gradient(C_field, self.dy)
                grad_sq = grad_y**2

        # Calculate Base Energies (Hamiltonian Components)
        # Potential: V(C) ~ 0.5 * alpha * (C - C0)^2
        term_potential = 0.5 * self.params.alpha * (C_field - self.params.C0) ** 2
        # Gradient: 0.5 * kappa * |grad C|^2
        term_gradient = 0.5 * self.params.kappa * grad_sq
        # Entropy: beta * C * I
        term_entropy = self.params.beta * C_field * I_field

        # Total Omega Density
        omega_density = term_potential + term_gradient + term_entropy

        # Integrated Values
        vol = self.dx * self.dy
        total_omega = np.sum(omega_density) * vol
        total_potential = np.sum(term_potential) * vol
        total_gradient = np.sum(term_gradient) * vol
        total_entropy_interaction = np.sum(term_entropy) * vol

        # Combine with subclass metrics
        metrics = {
            "step": step_idx,
            "time_val": self.time,
            "omega": total_omega,
            "potential": total_potential,
            "gradient_energy": total_gradient,
            "entropy_interaction": total_entropy_interaction,
            "field_c": self.C,  # For snapshotting
        }

        # Add Domain Specifics (e.g., Kinetic Energy)
        metrics.update(self.get_extra_metrics())

        # Dispatch to Logger
        self.logger.log_step(**metrics)

    def get_extra_metrics(self) -> Dict[str, Any]:
        """
        Subclasses should return a dict of extra metrics to log.
        Example: {'kinetic': 10.0}
        """
        return {}

    def log_metric(self, name: str, value: Any):
        """
        Helper to log a single global metric (non-timeseries) to the logger.
        Useful for final experiment results.
        """
        if self.logger:
            # Assuming UETMetricLogger supports this, or we hack it into the final report
            # If UETMetricLogger doesn't have log_metric, we should check uet_glass_box.py
            # But for now, let's assume we can add it to the report metadata or similar.
            # Actually, let's check uet_glass_box.py first, but to safe, I'll print it too.
            if hasattr(self.logger, "log_single_metric"):
                self.logger.log_single_metric(name, value)
            else:
                # Fallback: Just print it (Glass Box needs transparency)
                print(f"   [Metric] {name}: {value}")

    def run(self, steps: int, verbose: bool = True):
        """
        Standard Simulation Loop.
        """
        if verbose:
            print(
                f"🚀 Simulation '{self.logger.simulation_name if self.logger else 'UET'}' Started. Steps: {steps}"
            )

        for i in range(steps):
            self.step(step_idx=i)

            if verbose and (i + 1) % max(1, (steps // 10)) == 0:
                print(f"Step {i+1}/{steps}: Time={self.time:.4f}")

        if self.logger:
            report_path = self.logger.save_report()
            if verbose and report_path:
                print(f"💾 Results saved to: {report_path}")

    def save_results(self):
        """Standard API to save results manually."""
        if self.logger:
            return self.logger.save_report()
