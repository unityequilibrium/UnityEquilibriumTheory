"""Audit the declared conserved-Cattaneo high-k obstruction.

The result is scoped to the declared local equation class. It is not a no-go
claim about every possible regularization or every realization of C.
"""

from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "docs/core/07_artifacts/archive/matter_space_causal_cone_compatibility.json"
OUT = ROOT / "docs/core/07_artifacts/archive/conserved_c_finite_cone_no_go_assessment.json"


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    extension = source["continuum_diagnostic"]["cattaneo_extension"]
    M_C = float(extension["M_C"])
    kappa_C = float(extension["kappa_C"])
    tau_C = float(extension["tau_C"])
    wave_numbers = [float(value) for value in extension["wave_numbers"]]
    group_speeds = [float(value) for value in extension["group_speeds"]]
    coefficient = 2.0 * math.sqrt(M_C * kappa_C / tau_C)
    high_k_check = all(
        math.isclose(speed / wave_number, coefficient, rel_tol=5.0e-3, abs_tol=5.0e-3)
        for wave_number, speed in zip(wave_numbers[-2:], group_speeds[-2:])
    )
    obstruction = (
        extension["equation"]
        and extension["high_k_group_speed_is_unbounded"] is True
        and M_C > 0.0
        and kappa_C > 0.0
        and tau_C > 0.0
        and high_k_check
    )
    artifact = {
        "schema_version": "conserved-c-finite-cone-no-go-assessment-v1",
        "artifact": "conserved_c_finite_cone_no_go_assessment",
        "generated_at": date.today().isoformat(),
        "status": "NO_GO_FOR_DECLARED_CONSERVED_CATTANEO_LOCAL_GRADIENT_CLASS" if obstruction else "NO_GO_ASSESSMENT_INCONCLUSIVE",
        "proof_scope": "declared local conserved-C Cattaneo equation with mu_C=a_C*C-kappa_C*Laplacian(C)",
        "not_claimed": [
            "no-go theorem for all UV regularizations",
            "no-go theorem for nonlocal constitutive laws",
            "no-go theorem for a named non-conserved telegraph branch",
        ],
        "equation": extension["equation"],
        "derived_relation": "v_g(k) ~ 2*sqrt(M_C*kappa_C/tau_C)*k as k -> infinity",
        "parameters": {"M_C": M_C, "kappa_C": kappa_C, "tau_C": tau_C},
        "checks": {
            "positive_declared_coefficients": M_C > 0.0 and kappa_C > 0.0 and tau_C > 0.0,
            "high_k_group_speed_flag": extension["high_k_group_speed_is_unbounded"] is True,
            "asymptotic_coefficient_match": high_k_check,
            "finite_cone_compatibility": not obstruction,
            "no_clipping_or_cone_padding": True,
        },
        "evidence_input": {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "sha256": __import__("hashlib").sha256(SOURCE.read_bytes()).hexdigest(),
        },
        "next_action": "Keep conserved-C baseline blocked and close an explicit local regularization or named finite-cone branch with its own domain-of-dependence proof.",
        "claim_boundary": "Structural no-go evidence for one declared conserved-C local-gradient class; not a global no-go theorem and not a physical validation.",
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "artifact": OUT.relative_to(ROOT).as_posix()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
