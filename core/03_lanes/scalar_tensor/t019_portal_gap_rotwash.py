"""Test Card T019 prediction method: Eot-Wash Rot-Wash bound on the UET portal in the 1 cm - 1e5 m gap (topic 0.23).

Lane (as in T016): chi = nucleon, portal charge per mass eps = k (B/mu), k = m_N/u, so the portal force
between bodies i and A is alpha eps_i eps_A relative to gravity. Smith et al. (2000) bound a Yukawa force
coupled to q = B with Delta a / g' = alpha_B S(lambda), S = Delta(B/mu) <(B/mu)_A I_A(lambda)> (Table X).
Hence alpha_B = k^2 alpha_UET and

    alpha_max(lambda) = |Delta a|_95 / (g' k^2 S(lambda)),   g_c_max = 5.1198e-10 eV sqrt(alpha_max)

at the 15 tabulated ranges 0.01 - 50 m. For 1e2 - 1e5 m (inside the 1 m - 1e6 m validity stated by the source)
S is held at its 50 m value; the omitted Earth term I_E (q/mu)_E is at most 1.4 percent of S there and the
omitted centrifugal term 0.16 percent.
PASS if every alpha_max is positive and finite (g_c = 0 admissible). FAILED only if the data required
Delta a != 0 beyond 2 sigma while the lane fixes the portal non-zero (not the case: 1.0 +- 2.8).

Do not run against the data before the card is APPROVED by the author.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/gravity/ep_short_range/smith2000_rotwash_baryon.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
DATA_ID = "SMITH2000_ROTWASH_BARYON"
G_C_FOR_ALPHA_1_EV = 5.119820210530964e-10  # T005 producer, m_chi = mean nucleon mass
M_NUCLEON_EV = 0.9389e9  # T005 producer
U_EV = 931.49410242e6
HBAR_C_EV_M = 1.973269804e-7
EXTENDED_LAMBDAS_M = (1e2, 1e3, 1e4, 1e5)


def _rows() -> list[dict]:
    entry = next(e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"] if e["data_id"] == DATA_ID)
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != entry["sha256"]:
        raise RuntimeError(f"{DATA_ID}: sha256 mismatch")
    lines = [ln for ln in DATA.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return list(csv.DictReader(lines))


def compute() -> dict:
    rows = _rows()
    scalar = {r["quantity"]: float(r["value"]) for r in rows if not r["lambda_m"]}
    s_table = [(float(r["lambda_m"]), float(r["value"])) for r in rows if r["quantity"] == "S_B"]
    s_table += [(lam, s_table[-1][1]) for lam in EXTENDED_LAMBDAS_M]
    k2 = (M_NUCLEON_EV / U_EV) ** 2
    out = []
    for lam, s in s_table:
        a_max = scalar["delta_a_95"] / (scalar["g_attractor"] * k2 * s)
        out.append({"lambda_m": lam, "m_psi_eV": HBAR_C_EV_M / lam, "S_B": s, "alpha_max": a_max,
                    "g_c_max_eV": G_C_FOR_ALPHA_1_EV * a_max ** 0.5, "extended": lam in EXTENDED_LAMBDAS_M})
    finite = all(0.0 < r["alpha_max"] < float("inf") for r in out)
    z_signal = scalar["delta_a_central"] / (scalar["delta_a_stat"] ** 2 + scalar["delta_a_syst"] ** 2) ** 0.5
    return {"k_squared": k2, "rows": out, "signal_z": z_signal, "outcome": "PASS" if finite and abs(z_signal) <= 2 else "FAIL"}


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
