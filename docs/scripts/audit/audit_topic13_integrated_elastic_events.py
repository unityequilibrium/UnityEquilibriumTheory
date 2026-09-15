"""Integrate existing action-normalized tagged loss over the independent tag leg.

This counts elastic events, not the linearized collision response. The factor
one half removes the two incoming tags per event; outgoing counting is already
inside differential_cross_section and must not be applied again here.
"""
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from docs.scripts.audit.audit_topic13_action_normalized_elastic_scattering import (
    ActionInputs, bose, tagged_loss_rates,
)


def integrate(n, angular, cfg=ActionInputs(), temperature=.25, mu=.2, cutoff=12.):
    if isinstance(n, bool) or not isinstance(n, int) or n < 4:
        raise ValueError("integer radial order >=4 required")
    x, w = np.polynomial.legendre.leggauss(n)
    p, dp = cutoff*(x+1)/2, cutoff*w/2
    matrix = np.zeros((2,2))
    balance = 0.
    for k, wk in zip(p, dp):
        result = tagged_loss_rates(cfg, temperature=temperature, mu=mu, momentum=float(k),
                                  radial_order=n, incoming_order=angular, outgoing_order=angular,
                                  azimuth_order=angular, cutoff=cutoff)
        occupations = bose(np.sqrt(k*k+cfg.mass**2)-np.array([-1,1])*mu, temperature)
        matrix += wk*k*k/(2*np.pi**2)*occupations[:,None]*np.array(result["rates_by_tag_and_target"])
        balance = max(balance, result["max_detailed_balance_relative_error"])
    return dict(radial_order=n, angular_order=angular, cutoff=cutoff,
                ordered_tag_density=matrix.tolist(), event_density=float(matrix.sum()/2),
                incoming_exchange_relative_error=float(abs(matrix[0,1]-matrix[1,0])/max(matrix[0,1],matrix[1,0])),
                detailed_balance_relative_error=balance)


def main():
    cfg = ActionInputs()
    # Fixed sequence: radial refinement followed by angular refinement, same cutoff.
    rows = [integrate(n, a, cfg) for n,a in ((8,8),(16,8),(24,8),(24,12))]
    files = ["docs/scripts/audit/audit_topic13_integrated_elastic_events.py",
             "docs/scripts/audit/audit_topic13_action_normalized_elastic_scattering.py",
             "docs/core/test/test_topic13_action_normalized_elastic_scattering.py"]
    artifact = dict(major_result_id="T13_ACTION_NORMALIZED_INTEGRATED_ELASTIC_EVENTS", topic="0.13",
        closure_level="PARTIAL", what_is_closed="Independent double-radial integration connected to the existing tree elastic amplitude",
        equation_or_mapping="R_event=1/2 sum_q integral d^3k/(2*pi)^3 f_q(k) Gamma_q(k)",
        units="Natural energy^4 (events per volume per time)", derivation_class="TREE_ELASTIC_QUASIPARTICLE_DIAGNOSTIC",
        observable="Equilibrium elastic event density, not relaxation eigenvalue or conductivity",
        data_role="SYNTHETIC_ACTION_INPUTS_NO_FIT", config=asdict(cfg), temperature=.25, mu=.2,
        rows=rows, successive_relative_changes=[abs(b["event_density"]/a["event_density"]-1) for a,b in zip(rows,rows[1:])],
        verification_status="MEASURED_REFINEMENT_NOT_PHYSICAL_CLOSURE", dependency_unlocked=[], full_core_unlock=False,
        open_blockers=["cutoff_and_joint_resolution_control", "linearized_collision_gain_loss_and_conserved_projection", "material_calibration"],
        claim_boundary="Uses existing nonresonant tree amplitude and species factors. Does not replace legacy channels, infer full transport, or access external data/holdout.",
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in files])
    (ROOT/"docs/core/07_artifacts/topic13/t13_integrated_elastic_events_audit.json").write_text(json.dumps(artifact,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps(dict(rows=rows,changes=artifact["successive_relative_changes"])))


if __name__ == "__main__":
    main()
