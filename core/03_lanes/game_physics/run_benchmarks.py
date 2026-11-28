"""Reproduce the game-physics lane benchmarks (core/03_lanes/game_physics/README.md).

Usage: python core/03_lanes/game_physics/run_benchmarks.py OUT.json   (about 15 minutes on one CPU core)
"""

from __future__ import annotations

import importlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

db = importlib.import_module("core.03_lanes.game_physics.debris_bath")
eb = importlib.import_module("core.03_lanes.game_physics.energy_budget")


def debris(out):
    sc = db.Scene()
    out["drag_law_fixed_speed"] = {}
    for V in (0.5, 1.0, 2.0, 3.0):
        Fs = [sc.full_run(V, 300, 0.01, 10 * k + int(V * 7), fixed_velocity=True) for k in range(6)]
        out["drag_law_fixed_speed"][str(V)] = {"F_sim": float(np.mean(Fs)), "F_se": float(np.std(Fs) / math.sqrt(6)),
                                               "F_theory": sc.drag_fast(V, sc.T) * -1.0}
    steps, dt = 5000, 0.01
    out["debris_bath"] = {}
    for V0 in (0.25, 1.0, 2.0, 3.0):
        t1 = time.perf_counter()
        full = np.array([sc.full_run(V0, steps, dt, 700 + k) for k in range(16)])
        tf = (time.perf_counter() - t1) / 16
        t2 = time.perf_counter()
        red = np.array([sc.reduced_run(V0, steps, dt, 3000 + k) for k in range(200)])
        tr = (time.perf_counter() - t2) / 200
        lin = np.array([sc.linear_langevin_run(V0, steps, dt, 5000 + k) for k in range(200)])
        fm, rm, lm = full[:, :, 0].mean(0), red[:, :, 0].mean(0), lin[:, :, 0].mean(0)
        tail = slice(4000, 5000)
        out["debris_bath"][str(V0)] = {
            "rms_err_mean_V_over_V0_reduced": float(np.sqrt(np.mean((fm - rm) ** 2)) / V0),
            "rms_err_mean_V_over_V0_linear": float(np.sqrt(np.mean((fm - lm) ** 2)) / V0),
            "sampling_se_over_V0": float(np.mean(full[:, :, 0].std(0) / 4.0) / V0),
            "late_V2_full_reduced_linear": [float((full[:, tail] ** 2).sum(2).mean()),
                                            float((red[:, tail] ** 2).sum(2).mean()),
                                            float((lin[:, tail] ** 2).sum(2).mean())],
            "late_V2_equilibrium": sc.equilibrium_V2(V0),
            "wall_speedup": tf / tr, "work_ratio_per_step": sc.N,
        }


def budget(out):
    out["energy_budget"] = {}
    for seed in (1, 2, 3):
        ref = eb.run(300, seed, 1 / 480, "reference")
        r = {}
        for mode in ("baseline", "budget"):
            o = eb.run(300, seed, 1 / 120, mode)
            err = np.sqrt(((o["x"] - ref["x"]) ** 2).sum(1))
            r[mode] = {"updates": o["updates"], "pair_tests": o["tests"], "work": o["updates"] + o["tests"],
                       "wall_s": o["wall"], "settled_s": o["t_settled"], "err_mean": float(err.mean())}
        out["energy_budget"][f"seed{seed}"] = r


def main():
    out = {}
    debris(out)
    budget(out)
    json.dump(out, open(sys.argv[1], "w", encoding="utf-8", newline="\n"), indent=1)


if __name__ == "__main__":
    main()
