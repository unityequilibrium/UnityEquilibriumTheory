"""
Strict-mode solver for UET core models.
Implements R0-C1.2: semi-implicit diffusion + explicit reaction/coupling
with accept/reject + dt backtracking enforcing monotone Ω.
"""
from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Dict, Any, Tuple
from uet_core.metrics import record
import numpy as np

from .operators import spectral_laplacian, _kgrid_1d
from .energy import omega_C, omega_CI
from .coercivity import check_C_only, check_CI
from .potentials import from_dict
from .auto_scale import compute_safe_dt, validate_parameters

@dataclass
class StrictSettings:
    tol_abs: float = 1e-10
    tol_rel: float = 1e-10
    backtrack_factor: float = 0.5
    max_backtracks: int = 20
    dt_min_floor: float = 1e-12
    cap_abs_C: float = 1e6
    cap_abs_I: float = 1e6

def _semiimplicit_solve_spectral(rhs: np.ndarray, L: float, alpha: float) -> np.ndarray:
    """
    Solve (I - alpha Δ) u = rhs on periodic domain using FFT.
    Since Δ̂ = -|k|^2, operator becomes (1 + alpha |k|^2) in Fourier.
    """
    N = rhs.shape[0]
    k = _kgrid_1d(N, L)
    kx, ky = np.meshgrid(k, k, indexing="ij")
    k2 = kx*kx + ky*ky
    rhat = np.fft.fftn(rhs)
    uhat = rhat / (1.0 + alpha*k2)
    return np.fft.ifftn(uhat).real


def _semiimplicit_solve_spectral_shift(rhs: np.ndarray, L: float, alpha: float, shift: float) -> np.ndarray:
    """
    Solve ( (1+shift)I - alpha Δ ) u = rhs on periodic domain using FFT.
    denom = (1+shift) + alpha |k|^2
    """
    N = rhs.shape[0]
    k = _kgrid_1d(N, L)
    kx, ky = np.meshgrid(k, k, indexing="ij")
    k2 = kx*kx + ky*ky
    rhat = np.fft.fftn(rhs)
    uhat = rhat / ((1.0 + shift) + alpha*k2)
    return np.fft.ifftn(uhat).real

def _quartic_Lipschitz_bound(pot, u: np.ndarray) -> float:
    """
    Conservative bound for L = sup |V''(u)| on current grid.
    For QuarticPotential: V''(u) = a + 3*delta*u^2.
    """
    try:
        a = float(getattr(pot, "a"))
        delta = float(getattr(pot, "delta"))
    except Exception:
        return 0.0
    u2max = float(np.max(u*u))
    vmax = a + 3.0*delta*u2max
    vmin = a
    return float(max(abs(vmin), abs(vmax)))
def _energy_threshold(Omega_n: float, settings: StrictSettings) -> float:
    return settings.tol_abs + settings.tol_rel * max(1.0, abs(Omega_n))

def _blowup_check(C: np.ndarray, I: np.ndarray | None, settings: StrictSettings) -> tuple[bool,str]:
    if not np.isfinite(C).all():
        return True, "NAN_INF"
    if np.max(np.abs(C)) > settings.cap_abs_C:
        return True, "BLOWUP"
    if I is not None:
        if (not np.isfinite(I).all()):
            return True, "NAN_INF"
        if np.max(np.abs(I)) > settings.cap_abs_I:
            return True, "BLOWUP"
    return False, ""

def run_case(config: dict, rng: np.random.Generator, strict: StrictSettings | None = None) -> tuple[dict, list[dict]]:
    """
    Run a single case in strict mode, returning (summary, timeseries_rows).
    config must include:
      - model: C_only or C_I
      - domain: {L, dim=2, bc=periodic}
      - grid: {N}
      - time: {dt, T, max_steps, tol_abs, tol_rel, backtrack:{factor,max_backtracks}}
      - params: model-specific parameters already parsed into numeric form
    """
    settings = strict or StrictSettings()
    # Allow overrides from config.time
    tcfg = config["time"]
    settings.tol_abs = float(tcfg.get("tol_abs", settings.tol_abs))
    settings.tol_rel = float(tcfg.get("tol_rel", settings.tol_rel))
    bt = tcfg.get("backtrack", {})
    settings.backtrack_factor = float(bt.get("factor", settings.backtrack_factor))
    settings.max_backtracks = int(bt.get("max_backtracks", settings.max_backtracks))

    model = config["model"]
    L = float(config["domain"]["L"])
    N = int(config["grid"]["N"])
    dt0 = float(config["time"]["dt"])
    T = float(config["time"]["T"])
    max_steps = int(config["time"]["max_steps"])
    
    # SMART AUTO-DT: Compute safe timestep based on parameters
    params = config["params"]
    dx = L / N
    auto_dt_enabled = config.get("time", {}).get("auto_dt", True)  # Default enabled
    auto_scale_warnings = []
    
    if auto_dt_enabled:
        try:
            auto_result = compute_safe_dt(params, dx, dt0)
            if auto_result.was_adjusted:
                dt0 = auto_result.dt_recommended
                auto_scale_warnings = auto_result.warnings
        except Exception:
            pass  # Fallback to user's dt if auto-scale fails
    
    # Optional safety / UX controls (debug)
    wall_timeout_s = float((config.get("time", {}) or {}).get("wall_timeout_s", 0.0) or 0.0)
    progress_every_s = float((config.get("time", {}) or {}).get("progress_every_s", 0.0) or 0.0)
    progress_every_steps = int((config.get("time", {}) or {}).get("progress_every_steps", 0) or 0)
    t_wall0 = time.time()
    t_last_progress = t_wall0

    # init fields (dimensionless): random small noise
    C = rng.normal(0.0, 0.1, size=(N,N))
    I = None
    if model == "C_I":
        I = 0.5*C + rng.normal(0.0, 0.1, size=(N,N))

    params = config["params"]
    # Coercivity / boundedness precheck (expected to FAIL for delta<0 cases)
    try:
        if model == "C_only":
            cres = check_C_only(params)
        else:
            cres = check_CI(params)
        if cres.status == "FAIL":
            return {
                "case_id": config.get("case_id",""),
                "run_id": config.get("run_id",""),
                "model": model,
                "status": "FAIL",
                "fail_reasons": [cres.code],
                "warnings": [],
                "Omega0": float("nan"),
                "OmegaT": float("nan"),
                "Omega0_density": float("nan"),
                "OmegaT_density": float("nan"),
                "max_energy_increase": 0.0,
                "energy_increase_count": 0,
                "nan_inf_detected": False,
                "blowup_detected": False,
                "max_abs_C": 0.0,
                "max_abs_I": 0.0,
                "max_L4_C": 0.0,
                "max_L4_I": 0.0,
                "steps_total": 0,
                "steps_accepted": 0,
                "dt_min": float(config.get("time",{}).get("dt", 0.0)),
                "dt_max": float(config.get("time",{}).get("dt", 0.0)),
                "dt_backtracks_total": 0,
                "runtime_s": 0.0,
                "config_hash": config.get("config_hash",""),
                "code_hash": config.get("code_hash","unknown"),
            }, []
    except Exception:
        # If coercivity check fails unexpectedly, continue simulation (do not crash)
        pass

    rows = []
    t = 0.0

    # Energy at n
    if model == "C_only":
        Omega = omega_C(C, params["pot"], params["kappa"], L)
    else:
        Omega = omega_CI(C, I, params["potC"], params["potI"], params["beta"], params["kC"], params["kI"], L)
    # Record initial Omega0 if run_dir provided in config
    run_dir = config.get("run_dir")
    if run_dir:
        record("Omega0", float(Omega), run_dir)

    nan_inf = False
    blowup = False
    status = "PASS"
    fail_reasons = []
    warnings = []

    energy_increase_count = 0
    max_energy_increase = 0.0
    dt_min = dt0
    dt_max = dt0
    dt_backtracks_total = 0
    steps_accepted = 0

    for step in range(max_steps):
        if wall_timeout_s > 0.0 and (time.time() - t_wall0) > wall_timeout_s:
            status = "FAIL"
            fail_reasons.append("WALL_TIMEOUT")
            break
        if progress_every_s > 0.0 and (time.time() - t_last_progress) >= progress_every_s:
            print(f"[progress] step={step} t={t:.6g}/{T:.6g} dt={dt0:.3g} Omega={Omega:.6g} backtracks_total={dt_backtracks_total}", flush=True)
            t_last_progress = time.time()
        if progress_every_steps > 0 and (step % progress_every_steps == 0):
            print(f"[progress] step={step} t={t:.6g}/{T:.6g} dt={dt0:.3g} Omega={Omega:.6g} backtracks_total={dt_backtracks_total}", flush=True)

        # Use epsilon tolerance for floating-point comparison to avoid dt_min_floor failures
        if t >= T - 1e-10:
            break

        # blowup precheck
        bad, code = _blowup_check(C, I, settings)
        if bad:
            status = "FAIL"
            fail_reasons.append(code)
            nan_inf = (code == "NAN_INF")
            blowup = (code == "BLOWUP")
            break

        dt_try = min(dt0, T - t)
        backtracks = 0
        accepted = 0

        # backtracking loop
        while True:
            if dt_try < settings.dt_min_floor:
                status = "FAIL"
                fail_reasons.append("ENERGY_INCREASE")
                break

            # choose integrator
            integ = (config.get("integrator", {}) or {}).get("name", "semiimplicit").lower()
            stab_cfg = (config.get("integrator", {}) or {}).get("stabilization", {}) or {}
            stab_scale = float(stab_cfg.get("scale", 0.5))
            stab_margin = float(stab_cfg.get("margin", 0.0))
            stab_min = float(stab_cfg.get("min", 0.0))
            stab_max = float(stab_cfg.get("max", 1e9))

            if model == "C_only":
                M = float(params["M"])
                kappa = float(params["kappa"])
                pot = from_dict(params["pot"]) if isinstance(params["pot"], dict) else params["pot"]

                if integ in ("semiimplicit", "semi-implicit"):
                    rhs = C - dt_try*M*pot.dV(C)
                    alpha = dt_try*M*kappa
                    Ccand = _semiimplicit_solve_spectral(rhs, L, alpha)
                    Omegacand = omega_C(Ccand, pot, kappa, L)
                    S_C = 0.0
                elif integ in ("stabilized", "stab_semiimplicit", "stabilized_semiimplicit"):
                    Lbound = _quartic_Lipschitz_bound(pot, C)
                    S = min(stab_max, max(stab_min, stab_scale*Lbound + stab_margin))
                    rhs = C - dt_try*M*(pot.dV(C) - S*C)
                    alpha = dt_try*M*kappa
                    Ccand = _semiimplicit_solve_spectral_shift(rhs, L, alpha, dt_try*M*S)
                    Omegacand = omega_C(Ccand, pot, kappa, L)
                    S_C = S
                else:
                    raise ValueError(f"Unknown integrator: {integ}")

            else:
                MC = float(params["MC"]); MI = float(params["MI"])
                kC = float(params["kC"]); kI = float(params["kI"])
                beta = float(params["beta"])
                potC = from_dict(params["potC"]) if isinstance(params["potC"], dict) else params["potC"]
                potI = from_dict(params["potI"]) if isinstance(params["potI"], dict) else params["potI"]

                if integ in ("semiimplicit", "semi-implicit"):
                    rhsC = C - dt_try*MC*(potC.dV(C) - beta*I)
                    rhsI = I - dt_try*MI*(potI.dV(I) - beta*C)
                    Ccand = _semiimplicit_solve_spectral(rhsC, L, dt_try*MC*kC)
                    Icand = _semiimplicit_solve_spectral(rhsI, L, dt_try*MI*kI)
                    Omegacand = omega_CI(Ccand, Icand, potC, potI, beta, kC, kI, L)
                    S_C = 0.0
                    S_I = 0.0
                elif integ in ("stabilized", "stab_semiimplicit", "stabilized_semiimplicit"):
                    LC = _quartic_Lipschitz_bound(potC, C)
                    LI = _quartic_Lipschitz_bound(potI, I)
                    SC = min(stab_max, max(stab_min, stab_scale*LC + stab_margin))
                    SI = min(stab_max, max(stab_min, stab_scale*LI + stab_margin))

                    rhsC = C - dt_try*MC*((potC.dV(C) - beta*I) - SC*C)
                    rhsI = I - dt_try*MI*((potI.dV(I) - beta*C) - SI*I)

                    Ccand = _semiimplicit_solve_spectral_shift(rhsC, L, dt_try*MC*kC, dt_try*MC*SC)
                    Icand = _semiimplicit_solve_spectral_shift(rhsI, L, dt_try*MI*kI, dt_try*MI*SI)
                    Omegacand = omega_CI(Ccand, Icand, potC, potI, beta, kC, kI, L)
                    S_C = SC
                    S_I = SI
                else:
                    raise ValueError(f"Unknown integrator: {integ}")
            dOmega = Omegacand - Omega
            thr = _energy_threshold(Omega, settings)
            if dOmega <= thr:
                accepted = 1
                break
            else:
                backtracks += 1
                dt_backtracks_total += 1
                dt_try *= settings.backtrack_factor
                if backtracks > settings.max_backtracks:
                    status = "FAIL"
                    fail_reasons.append("ENERGY_INCREASE")
                    max_energy_increase = max(max_energy_increase, float(dOmega)) # Capture the fail reason
                    break

        if status == "FAIL":
            # log last attempt if available
            rows.append({
                "step": step, "t": t, "Omega": Omega, "dOmega": float(max_energy_increase),
                "mean_C": float(np.mean(C)),
                "mean_I": float(np.mean(I)) if I is not None else "",
                "bias_CI": float(np.mean(C) - np.mean(I)) if I is not None else "",
                "L2_C": float(np.linalg.norm(C)), "L4_C": float(np.mean(C**4)**0.25),
                "min_C": float(np.min(C)), "max_C": float(np.max(C)),
                "L2_I": float(np.linalg.norm(I)) if I is not None else "",
                "L4_I": float(np.mean(I**4)**0.25) if I is not None else "",
                "min_I": float(np.min(I)) if I is not None else "",
                "max_I": float(np.max(I)) if I is not None else "",
                "dt": dt_try, "accepted": 0, "backtracks": backtracks, "S_C": float(S_C) if "S_C" in locals() else "", "S_I": float(S_I) if "S_I" in locals() else ""
            })
            break

        # Accept
        if model == "C_only":
            C = Ccand
            Omega_next = Omegacand
        else:
            C = Ccand
            I = Icand
            Omega_next = Omegacand

        dOmega = Omega_next - Omega
        if dOmega > _energy_threshold(Omega, settings):
            # should not happen due to accept gate, but keep as diagnostic
            energy_increase_count += 1
            max_energy_increase = max(max_energy_increase, float(dOmega))
        else:
            max_energy_increase = max(max_energy_increase, float(dOmega))

        dt_min = min(dt_min, dt_try)
        dt_max = max(dt_max, dt_try)
        steps_accepted += 1

        rows.append({
            "step": step, "t": t, "Omega": float(Omega),
            "dOmega": float(dOmega),
            "mean_C": float(np.mean(C)),
            "mean_I": float(np.mean(I)) if I is not None else "",
            "bias_CI": float(np.mean(C) - np.mean(I)) if I is not None else "",
            "L2_C": float(np.linalg.norm(C)), "L4_C": float(np.mean(C**4)**0.25),
            "min_C": float(np.min(C)), "max_C": float(np.max(C)),
            "L2_I": float(np.linalg.norm(I)) if I is not None else "",
            "L4_I": float(np.mean(I**4)**0.25) if I is not None else "",
            "min_I": float(np.min(I)) if I is not None else "",
            "max_I": float(np.max(I)) if I is not None else "",
            "dt": float(dt_try), "accepted": int(accepted), "backtracks": int(backtracks)
        })
    # Record metrics after each accepted step
    if run_dir:
        record("OmegaT", float(Omega_next), run_dir)
        record("dt", float(dt_try), run_dir)
        record("energy", float(Omega_next), run_dir)

        Omega = Omega_next
        t += dt_try

    # Post-run blowup check
    bad, code = _blowup_check(C, I, settings)
    if bad and status != "FAIL":
        status = "FAIL"
        fail_reasons.append(code)
        nan_inf = (code == "NAN_INF")
        blowup = (code == "BLOWUP")

    if status == "PASS":
        # warn if heavy backtracking
        if dt_backtracks_total > 100:
            warnings.append("DT_BACKTRACK_HEAVY")
            status = "WARN" if status == "PASS" else status

    # Compute density (per unit area) for grid-independent comparison
    L2 = L * L
    Omega0_total = float(rows[0]["Omega"]) if rows else float(Omega)
    OmegaT_total = float(Omega)
    
    summary = {
        "case_id": config["case_id"],
        "run_id": config.get("run_id",""),
        "model": model,
        "status": status,
        "fail_reasons": fail_reasons,
        "warnings": warnings,
        "Omega0": Omega0_total,
        "OmegaT": OmegaT_total,
        "Omega0_density": Omega0_total / L2,
        "OmegaT_density": OmegaT_total / L2,
        "max_energy_increase": float(max_energy_increase),
        "energy_increase_count": int(energy_increase_count),
        "nan_inf_detected": bool(nan_inf),
        "blowup_detected": bool(blowup),
        "max_abs_C": float(np.max(np.abs(C))),
        "max_abs_I": float(np.max(np.abs(I))) if I is not None else 0.0,
        "max_L4_C": float(np.max([r["L4_C"] for r in rows])) if rows else float(np.mean(C**4)**0.25),
        "max_L4_I": float(np.max([r["L4_I"] for r in rows if r.get("L4_I","")!=""])) if (rows and I is not None) else 0.0,
        "steps_total": int(len(rows)),
        "steps_accepted": int(steps_accepted),
        "dt_min": float(dt_min),
        "dt_max": float(dt_max),
        "dt_backtracks_total": int(dt_backtracks_total),
        "runtime_s": 0.0,  # filled by runner
        "config_hash": config.get("config_hash",""),
        "code_hash": config.get("code_hash","unknown"),
    }
    return summary, rows
