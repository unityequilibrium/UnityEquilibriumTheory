"""Trace feedback in a real system: the switch glucose level of cooperative yeast growth on sucrose.

Question: C_L3_TRACE_FEEDBACK says a trace written in proportion to resource use changes the environment of
later growth. In yeast on sucrose the trace is the glucose that invertase releases outside the cells: almost all
of it diffuses away and is shared (Gore et al. 2009 report that about 1 percent is captured privately). Dai et al.
(2012) describe growth in 2 percent sucrose with a two-phase law: per-capita rate gamma_low below a density N_c
and gamma_high above it; N_c was fitted, not measured. Which shared-glucose level G* does the trace model
assign to that switch, from independently measured enzyme kinetics?

Derivation [AI derivation; well-mixed batch culture, uptake of the released glucose neglected before the switch]:
1. Trace writing per cell (Michaelis-Menten, Koschwanez et al. 2011):
       h = Vmax S / (Km + S)       (glucose molecules per second per cell)
   with S the sucrose concentration (2 percent w/v = 58.4 mM, far above Km = 11 mM, so h is close to Vmax).
2. Below the switch the culture grows at gamma_low: dN/dt = gamma_low N, and the shared trace accumulates as
       dG/dt = (1 - eps) h N    =>    G(t) = (1 - eps) h (N(t) - N0) / gamma_low.
3. The density switch N_c therefore corresponds to a shared glucose level
       G* = (1 - eps) h (N_c - N0) / gamma_low  ~  (1 - eps) h N_c / gamma_low    (N0 << N_c).
   With the registered values this is about 1.6 mM (0.028 percent glucose).
4. Prediction: an independent measurement of yeast per-capita growth rate against glucose concentration must
   show the rise from gamma_low to gamma_high near G*. Uptake of glucose before the switch would lower the free
   glucose, so G* is an upper estimate for the free concentration.

What the trace model adds: the density threshold of a public-goods Allee effect becomes a resource level that
can be checked in a separate experiment. Nearest known theory: public-goods (snowdrift) models of yeast
cooperation (Gore et al. 2009) and Allee effects. Not UET-distinct: the trace here is set by enzyme kinetics,
not by energy use. The value eps = 0.01 is quoted from memory of Gore et al. (2009) and is not yet checked
against the paper; it changes G* by 1 percent.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/biology/yeast_sucrose/yeast_sucrose_parameters.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "YEAST_SUCROSE_PARAMETERS"
AVOGADRO = 6.02214076e23
SUCROSE_MOLAR_MASS = 342.30  # g/mol
CAPTURE_EPS = 0.01           # Gore et al. 2009 (from memory; see docstring)


def parameters() -> dict[str, float]:
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return {r["quantity"]: float(r["value"]) for r in csv.DictReader(lines)}


def sucrose_mM(percent_w_v: float) -> float:
    return percent_w_v * 10.0 / SUCROSE_MOLAR_MASS * 1e3


def hydrolysis_rate(vmax: float, km_mM: float, s_mM: float) -> float:
    return vmax * s_mM / (km_mM + s_mM)


def trace_at_density(n: float, n0: float, h: float, gamma_per_s: float, eps: float = CAPTURE_EPS) -> float:
    """Shared glucose (molecules per microlitre) when the culture has grown from n0 to n at rate gamma."""
    return (1.0 - eps) * h * (n - n0) / gamma_per_s


def simulate(n0: float, h: float, gamma_per_s: float, t_end: float, eps: float = CAPTURE_EPS,
             uptake: float = 0.0) -> tuple[float, float]:
    """Integrate dN/dt = gamma N, dG/dt = (1-eps) h N - uptake G N; returns (N, G) at t_end."""
    sol = solve_ivp(lambda _t, y: [gamma_per_s * y[0], (1.0 - eps) * h * y[0] - uptake * y[1] * y[0]],
                    (0.0, t_end), [n0, 0.0], method="LSODA", rtol=1e-11, atol=1e-6)
    return float(sol.y[0, -1]), float(sol.y[1, -1])


def molecules_per_ul_to_mM(x: float) -> float:
    return x * 1e6 / AVOGADRO * 1e3


def switch_glucose() -> dict[str, float]:
    p = parameters()
    s = sucrose_mM(p["sucrose_concentration"])
    h = hydrolysis_rate(p["invertase_vmax_per_cell"], p["invertase_km_sucrose"], s)
    g = p["gamma_low"] / 3600.0
    G = trace_at_density(p["switch_density_Nc"], 0.0, h, g)
    return {"sucrose_mM": s, "h_per_cell_per_s": h, "G_star_molecules_per_ul": G,
            "G_star_mM": molecules_per_ul_to_mM(G), "G_star_percent_w_v": molecules_per_ul_to_mM(G) * 180.16 / 1e4}


if __name__ == "__main__":
    print(json.dumps(switch_glucose(), indent=2))
