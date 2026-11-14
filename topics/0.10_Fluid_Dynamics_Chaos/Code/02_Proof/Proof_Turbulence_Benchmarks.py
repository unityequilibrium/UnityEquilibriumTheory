"""
UET Tier 2 Benchmark: Speed and Stability
=========================================
Head-to-head internal comparison between a simplified Navier-Stokes baseline and the UET
solver. This script is intended for repository benchmark hygiene, not theorem-level claims.
"""

import os
import sys
import time
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt
import numpy as np


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

from docs.core.reproducibility import generate_artifact, hash_dataset, hash_file, save_artifact
from docs.core.uet_master_equation import UETMasterEquation, UETParameters


TOPIC_DIR = Path(__file__).resolve().parents[2]
SOURCE_LOCK_PATH = TOPIC_DIR / "Data" / "03_Research" / "source_lock_manifest.json"


class SimplifiedNSSolver:
    """A minimal vectorized Navier-Stokes-style baseline for benchmarking."""

    def __init__(self, nx=32, ny=32, dt=0.001, nu=0.01):
        self.nx, self.ny = nx, ny
        self.dt, self.nu = dt, nu
        self.dx = 1.0 / nx
        self.dy = 1.0 / ny
        self.u = np.zeros((ny + 2, nx + 2))
        self.v = np.zeros((ny + 2, nx + 2))
        self.p = np.zeros((ny + 2, nx + 2))

    def step(self):
        un = self.u[1:-1, 1:-1]
        vn = self.v[1:-1, 1:-1]

        self.u[1:-1, 1:-1] = un + self.dt * (
            self.nu
            * (
                (self.u[1:-1, 2:] - 2 * un + self.u[1:-1, :-2]) / self.dx**2
                + (self.u[2:, 1:-1] - 2 * un + self.u[:-2, 1:-1]) / self.dy**2
            )
        )
        self.v[1:-1, 1:-1] = vn + self.dt * (
            self.nu
            * (
                (self.v[1:-1, 2:] - 2 * vn + self.v[1:-1, :-2]) / self.dx**2
                + (self.v[2:, 1:-1] - 2 * vn + self.v[:-2, 1:-1]) / self.dy**2
            )
        )

        for _ in range(20):
            self.p[1:-1, 1:-1] = 0.25 * (
                self.p[1:-1, 2:]
                + self.p[1:-1, :-2]
                + self.p[2:, 1:-1]
                + self.p[:-2, 1:-1]
            )

        self.u[1:-1, 1:-1] -= self.dt * (self.p[1:-1, 2:] - self.p[1:-1, 1:-1]) / self.dx
        self.v[1:-1, 1:-1] -= self.dt * (self.p[2:, 1:-1] - self.p[1:-1, 1:-1]) / self.dy


def run_benchmarks():
    print("=" * 60)
    print("UET TIER 2: SPEED AND STABILITY BENCHMARK")
    print("=" * 60)

    grid_size = 128
    steps = 100
    trials = 5

    def time_ns_once():
        ns = SimplifiedNSSolver(nx=grid_size, ny=grid_size, dt=0.001)
        t0 = time.perf_counter()
        for _ in range(steps):
            ns.step()
        return time.perf_counter() - t0

    params = UETParameters(kappa=0.01, beta=1.0, alpha=0.0, gamma=0.0, W_N=0.0)

    def time_uet_once():
        solver = UETMasterEquation(params)
        c_field = np.zeros((grid_size, grid_size))
        i_field = np.zeros((grid_size, grid_size))
        t0 = time.perf_counter()
        for _ in range(steps):
            result = solver.step(c_field, dt=0.001, dx=1.0 / grid_size, I=i_field)
            if isinstance(result, tuple):
                if len(result) == 3:
                    c_field, i_field, _ = result
                else:
                    c_field, i_field = result
            else:
                c_field = result
        return time.perf_counter() - t0

    # Warm-up removes first-call import/allocation jitter without changing the threshold.
    time_ns_once()
    time_uet_once()
    ns_trials = [time_ns_once() for _ in range(trials)]
    uet_trials = [time_uet_once() for _ in range(trials)]
    t_ns = median(ns_trials)
    t_uet = median(uet_trials)

    speedup = t_ns / t_uet

    solver = UETMasterEquation(params)
    c_stress = np.zeros((grid_size, grid_size))
    i_field = np.zeros((grid_size, grid_size))
    c_stress[grid_size // 2, grid_size // 2] = 1e6
    try:
        for _ in range(50):
            result = solver.step(c_stress, dt=0.001, dx=1.0 / grid_size, I=i_field)
            if isinstance(result, tuple):
                if len(result) == 3:
                    c_stress, i_field, _ = result
                else:
                    c_stress, i_field = result
            else:
                c_stress = result
        is_stable = bool(np.isfinite(c_stress).all())
    except Exception:
        is_stable = False

    print(f"NS Runtime: {t_ns:.4f}s")
    print(f"UET Runtime: {t_uet:.4f}s")
    print(f"Speedup: {speedup:.1f}x")
    print(f"Stable: {is_stable}")

    fig_dir = Path(__file__).resolve().parents[2] / "Result" / "02_Proof"
    fig_dir.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.bar(["Navier-Stokes", "UET"], [t_ns, t_uet], color=["gray", "red"])
    plt.yscale("log")
    plt.ylabel("Runtime (s) - Log Scale")
    plt.title("Speed Comparison")
    plt.grid(True, axis="y", alpha=0.3)

    plt.subplot(1, 2, 2)
    plt.imshow(c_stress, cmap="hot")
    plt.title(f"Stability stress test\n(Peak bound: {np.max(c_stress):.2e})")
    plt.colorbar(label="Field Intensity")
    plt.tight_layout()
    plt.savefig(fig_dir / "benchmarks_tier2.png")
    plt.close()

    passed = speedup > 2.0 and is_stable
    artifact = generate_artifact(
        topic="0.10_Fluid_Dynamics_Chaos",
        dataset_hash=hash_dataset({
            "grid_size": grid_size,
            "steps": steps,
            "trials": trials,
            "source_lock_sha256": hash_file(SOURCE_LOCK_PATH) if SOURCE_LOCK_PATH.exists() else None,
        }),
        results={
            "status": "PASS" if passed else "FAIL",
            "navier_stokes_runtime_seconds": float(t_ns),
            "uet_runtime_seconds": float(t_uet),
            "navier_stokes_runtime_trials_seconds": [float(v) for v in ns_trials],
            "uet_runtime_trials_seconds": [float(v) for v in uet_trials],
            "speedup": float(speedup),
            "stable": is_stable,
        },
        config={
            "grid_size": grid_size,
            "steps": steps,
            "trials": trials,
            "timing_statistic": "median",
            "source_lock_manifest": str(SOURCE_LOCK_PATH.relative_to(ROOT)),
            "comparator": "SimplifiedNSSolver embedded in Proof_Turbulence_Benchmarks.py",
        },
        metrics={"speedup": float(speedup), "stable": is_stable},
        thresholds={"min_speedup": 2.0, "requires_stability": True},
        notes="Internal implementation benchmark artifact using the repository comparator script; not an external CFD validation result.",
    )
    artifact["input_hashes"] = {
        "source_lock_manifest": hash_file(SOURCE_LOCK_PATH) if SOURCE_LOCK_PATH.exists() else None,
        "benchmark_script": hash_file(Path(__file__).resolve()),
        "uet_master_equation": hash_file(ROOT / "docs" / "core" / "uet_master_equation.py"),
    }
    artifact["claim_boundary"] = (
        "PASS means the UET implementation beat the embedded simplified comparator under this "
        "grid/timing/stability gate. It does not establish external CFD accuracy or a "
        "Navier-Stokes theorem result."
    )
    artifact_path = Path(__file__).resolve().parents[2] / "Result" / "artifacts" / "fluid_benchmark_validation.json"
    save_artifact(artifact, artifact_path)
    print(f"Artifact saved to {artifact_path}")

    return passed


if __name__ == "__main__":
    success = run_benchmarks()
    sys.exit(0 if success else 1)
