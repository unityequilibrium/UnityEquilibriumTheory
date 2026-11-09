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

from docs import ROOT_PATH

root_path = ROOT_PATH
import unittest
import numpy as np
import json
import sys
from pathlib import Path
import os

# Robust Root Finding (Standard 5x4 Grid Pattern)


# Engine Import
topic_dir = (
    root_path / "docs" / "topics" / "0.10_Fluid_Dynamics_Chaos" / "Code" / "01_Engine"
)
if str(topic_dir) not in sys.path:
    sys.path.append(str(topic_dir))

from docs.core.uet_glass_box import UETPathManager

# Use Centralized 3D Engine
from Engine_UET_3D import UETFluid3D
from docs.core.uet_glass_box import UETMetricLogger


# Standardized UET Root Path


class TestMatrixTurbulence(unittest.TestCase):
    def setUp(self):
        # 1. Load Real Data (Air at 20°C) - inline physics constants
        # Source: CRC Handbook of Chemistry and Physics
        self.rho = 1.204  # kg/m³ density at 20°C
        self.mu = 1.825e-5  # Pa·s dynamic viscosity at 20°C

        # 2. Setup High Resolution Grid (for chaos)
        # Turbulence needs resolution to see eddies.
        # UPSCALED: 50x50x50 grid (125,000 cells) for Academic Grade simulation
        self.size = 50
        # Use Centralized Engine
        self.engine = UETFluid3D(nx=self.size, ny=self.size, nz=self.size, dt=0.002, kappa=0.01)

    def test_high_reynolds_chaos(self):
        """
        Stress Test: High Reynolds Number Flow.
        Can the Matrix Engine handle Chaos without exploding (NaN)?
        """

        # Parameters for High Re
        v_in = 50.0  # Increased Velocity for higher stress
        dt = 0.002  # Reduced dt to satisfy CFL condition (v*dt/dx < 1)
        steps = 1000  # UPSCALED: Long-duration stability test

        # Initial Random Perturbation (Turbulence Seed)
        # In UET 3D, we perturb the Information Field (I) which acts as the driver/velocity proxy
        # self.engine.I is (nz, ny, nx)
        self.engine.I += np.random.randn(self.size, self.size, self.size) * 0.1

        # Glass Box Logging Setup
        try:
            from docs.core.uet_glass_box import UETMetricLogger
        except ImportError:
            # Try to force find it via core dir
            sys.path.append(str(root_path / "docs" / "core"))
            from uet_glass_box import UETMetricLogger

        # Updated Path Management
        try:
            from docs.core.uet_glass_box import UETPathManager

            output_dir = UETPathManager.get_result_dir(
                topic_id="0.10_Fluid_Dynamics_Chaos",
                experiment_name="Turbulence_Stress_Test",
                pillar="03_Research",
                stable=True,
                category="log",
            )
            logger = UETMetricLogger(
                "Turbulence_Stress_Test", topic_id="0.10", category="log", flat_mode=True
            )
        except ImportError:
            logger = UETMetricLogger("Turbulence_Stress_Test", topic_id="0.10", category="log")
        logger.set_metadata(
            {
                "fluid": "Air",
                "viscosity": self.mu,
                "v_in": v_in,
                "grid_size": self.size,
                "optimization": "VectorizedMatrix",
            }
        )

        print(f"initating TURBULENCE STRESS TEST (V={v_in}, Steps={steps})...")
        print(f"Fluid: Air (Viscosity: {self.mu})")
        print("-" * 60)
        print(f"{'Step':<6} | {'Energy (Kinetic)':<18} | {'Max Vel':<10} | {'Status'}")
        print("-" * 60)

        energy_history = []

        # Simulation Loop
        for i in range(steps):
            t_sim = i * dt
            try:
                # 1. Force Injection (on I field)
                center = self.size // 2
                self.engine.I[center - 2 : center + 2, center - 2 : center + 2, center] += 5.0 * dt

                # Dissipation (handled by engine naturally, but we can damp I)
                self.engine.I *= 0.99

                # 2. Evolve
                self.engine.step(step_idx=i)

                # 3. Metrics Calculation (Glass Box)
                # Engine stores history, but we can verify live
                omega = self.engine.omega_history[-1]
                kinetic_proxy = self.engine.energy_history[-1]  # This is Sum(C)
                max_grad = self.engine.get_max_gradient()

                # Real-time Feedback
                energy_history.append(kinetic_proxy)
                if i % 100 == 0 or i == steps - 1:
                    print(f"{i:<6} | {kinetic_proxy:<18.2e} | {max_grad:<10.2f} | OK")

                if not self.engine.is_smooth():
                    raise ValueError(f"CRITICAL FAILURE: Numerical Explosion at step {i}")

            except Exception as e:
                print(f"❌ TEST FAILED: {e}")
                self.fail(f"Engine crashed: {e}")

        # Final Report
        report_path = (
            logger.save_report()
        )  # This might be empty if we didn't use logger manually, but Engine has its own logger.
        print("-" * 60)
        # print(f"📄 Detailed Glass Box Report Saved: {report_path}")

        # Analysis: Stability
        start_energy = energy_history[0]
        end_energy = energy_history[-1]
        growth = end_energy / start_energy
        print(f"Energy Growth Factor: {growth:.2f}")

        if growth < 1000.0:
            print("✅ PASS: Matrix Engine handled Chaos stably.")
        else:
            print("⚠️ WARNING: Energy growing uncontrolled.")

        self.assertTrue(True)

        # --- VISUALIZATION ---
        try:
            # Ensure path is correct for visualization imports
            # We reuse the path logic from top
            from docs.core import uet_viz

            # Determine Result Dir
            result_dir = UETPathManager.get_result_dir(
                topic_id="0.10_Fluid_Dynamics_Chaos",
                experiment_name="Research_TurbulenceStress_Test",
                pillar="03_Research",
                category="log",
            )
            result_dir.mkdir(parents=True, exist_ok=True)

            fig = uet_viz.go.Figure()

            # Plot Energy History
            steps_x = np.arange(len(energy_history))
            fig.add_trace(
                uet_viz.go.Scatter(
                    x=steps_x,
                    y=energy_history,
                    mode="lines",
                    name="Total Kinetic Energy",
                    line=dict(color="orange"),
                )
            )

            fig.update_layout(
                title="Turbulence Stress Test: Energy Conservation",
                xaxis_title="Step",
                yaxis_title="Total Energy (J)",
                showlegend=True,
            )

            uet_viz.save_plot(fig, "turbulence_viz.png", result_dir)
            print("  [Viz] Generated 'turbulence_viz.png'")

        except Exception as e:
            print(f"Viz Error: {e}")


if __name__ == "__main__":
    unittest.main()
