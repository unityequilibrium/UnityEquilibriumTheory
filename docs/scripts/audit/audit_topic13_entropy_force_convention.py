"""Independent heat-only entropy-current check; preserves historical evidence."""
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from docs.core.uet_o2_covariant_entropy_heat_flux_balance import (
    covariant_entropy_heat_flux, covariant_entropy_heat_flux_balance_state,
)
from docs.scripts.audit.audit_topic13_eos_revision_impact import compare_states


def witness(temperature, gradient=-0.01, coefficient=1.0):
    """Local constant-q, no-work/no-diffusion counterexample, not material data.

    For constant q, energy conservation gives ds/dt=0. The spatial entropy
    current q/T has divergence -q*T_x/T^2. No collision identity is used.
    """
    force = -gradient / temperature
    state = covariant_entropy_heat_flux(np.diag([-1., 1., 1., 1.]),
        np.array([1., 0., 0., 0.]), temperature, 1., coefficient,
        np.array([0., force, 0., 0.]))
    q = float(state["heat_flux_contravariant"][1])
    expected = -q * gradient / temperature**2
    estimates = []
    for relative_step in (.01, .005, .0025):
        h = relative_step * temperature / abs(gradient)
        derivative = (q / (temperature + gradient*h)
                      - q / (temperature - gradient*h)) / (2*h)
        estimates.append({"relative_temperature_step": relative_step,
                          "divergence": derivative,
                          "relative_error": abs(derivative/expected - 1)})
    reported = float(state["entropy_production"])
    return {"temperature": temperature, "gradient": gradient, "q": q,
            "reported_entropy_production": reported,
            "entropy_current_divergence": expected,
            "reported_over_divergence": reported/expected,
            "reported_divided_by_T": reported/temperature,
            "direct_current_difference": estimates}


def main():
    historical_path = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_covariant_entropy_heat_flux_balance_audit.json"
    old = json.loads(historical_path.read_text(encoding="utf-8"))["state"]
    current = asdict(covariant_entropy_heat_flux_balance_state(.22, .35, .15))
    witnesses = [witness(t) for t in (.22, .5, 1., 2.)]
    normalized = all(abs(r["reported_over_divergence"]-1.) < 1.e-10 for r in witnesses)
    result = {
        "major_result_id": "T13_ENTROPY_FORCE_NORMALIZATION_COUNTEREXAMPLE",
        "closure_level": "PARTIAL", "status": "NORMALIZATION_REPAIRED_PHYSICAL_MAPPING_OPEN" if normalized else "BLOCKED_PHYSICAL_ENTROPY_INTERPRETATION",
        "what_is_closed": "Current implementation tested against independent entropy-current divergence; historical X.q counterexample remains in the frozen artifact.",
        "equation_or_mapping": "Heat-only rest limit: T ds/dt=-d_x q; sigma=ds/dt+d_x(q/T)=-q*d_x(T)/T^2=X.q/T.",
        "units": "Natural k_B=1; X.q has one extra temperature factor relative to entropy production.",
        "derivation_class": "Independent product-rule and local energy-balance diagnostic",
        "observable": "Formal entropy-current divergence, not material heat transport",
        "data_role": "ANALYTIC_MANUFACTURED_CONTROL_NO_CALIBRATION",
        "witnesses": witnesses,
        "current_reference_comparison": compare_states(old, current),
        "reference_scope": "Existing entropy default EOS config, NOT action_bridge_config; equal T/mu/Phi alone does not establish identical action parameters.",
        "verification_status": "CURRENT_DIVERGENCE_AGREES" if normalized else "CURRENT_DIVERGENCE_DISAGREES",
        "open_blockers": ["thermal_force_flux_entropy_normalization", "hydrodynamic_frame_and_charge_diffusion_map", "action_configuration_correspondence"],
        "repair_options_not_applied": [
            "Keep X and q conventions; identify X.q as temperature-weighted dissipation and derive physical sigma plus kinetic normalization coherently.",
            "Use entropy-conjugate Y=X/T and rederive the coefficient/source response, not merely swap the force label."
        ],
        "dependency_unlocked": [], "claim_promotion": False,
        "claim_boundary": "No core equation changed, no historical gate replaced, no SI/Kubo or He4 validation. Finite-cutoff positivity can remain true while physical entropy interpretation is blocked.",
        "source": {"url": "https://arxiv.org/pdf/2602.20254v3", "locator": "Lemma 4, equations 73-74, printed page 11", "role": "Primary correspondence cross-check; independent local derivation used for test"},
        "holdout_policy": "No holdout file or calibration data read; no claim of pristine historical context.",
        "evidence_artifacts": [{"path": p, "sha256": sha256((ROOT/p).read_bytes()).hexdigest()} for p in (
            "docs/scripts/audit/audit_topic13_entropy_force_convention.py",
            "docs/core/test/test_topic13_entropy_force_convention.py",
            "docs/core/uet_o2_covariant_entropy_heat_flux_balance.py",
            "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py",
            "docs/core/uet_o2_continuum_collision_operator.py",
            "docs/core/07_artifacts/topic13/t13_uet_o2_covariant_entropy_heat_flux_balance_audit.json")],
    }
    target = ROOT / "docs/core/07_artifacts/topic13/t13_entropy_force_convention_audit.json"
    target.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "witnesses": result["witnesses"],
                      "kappa_comparison": result["current_reference_comparison"]["kappa_natural"]}, indent=2))


if __name__ == "__main__":
    main()
