"""Source harmonics from the existing quadratic matter forcing, not a new drive."""
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.core.uet_covariant_matter import CovariantMatterConfig, coupled_response_scalar_equation_residual
from docs.core.uet_covariant_response import CovariantResponseConfig


def measure(background, amplitude, epsilon=.5, samples=128):
    response=CovariantResponseConfig(epsilon_nc=epsilon)
    matter=CovariantMatterConfig(response_coupling=.8)
    phase=2*np.pi*np.arange(samples)/samples
    def residual(chi):
        return coupled_response_scalar_equation_residual(0.,0.,response.phi_equilibrium,
            [chi,0.],response,matter)
    reference=residual(background)
    force=np.array([residual(background+amplitude*np.cos(t))-reference for t in phase])
    measured=np.array([force.mean(),2*np.mean(force*np.cos(phase)),2*np.mean(force*np.cos(2*phase))])
    expected=epsilon*matter.response_coupling*np.array([amplitude**2/4,background*amplitude,amplitude**2/4])
    return dict(background=background,amplitude=amplitude,epsilon=epsilon,
                dc_fundamental_second_harmonic=measured.tolist(),expected=expected.tolist(),
                maximum_absolute_error=float(np.max(abs(measured-expected))))


def main():
    rows=[measure(b,a) for b in (0.,.4) for a in (.1,.05,.025)]
    rows.append(measure(.4,.1,epsilon=0.))
    files=["docs/scripts/audit/audit_topic13_matter_actuation_harmonics.py",
           "docs/core/test/test_topic13_matter_actuation_harmonics.py",
           "docs/core/uet_covariant_matter.py","docs/core/uet_covariant_response.py"]
    r=dict(major_result_id="T13_EXISTING_MATTER_ACTUATION_HARMONICS",topic="0.13",closure_level="PARTIAL",
        equation_or_mapping="DeltaJ=epsilon*h*(chi0*A*cos(wt)+A^2*(1+cos(2wt))/4)",
        units="chi0,A energy; h energy; J energy^3; epsilon dimensionless",
        derivation_class="Expansion of existing production response residual",observable="Source harmonics, not measured Phi or temperature harmonics",
        data_role="SYNTHETIC_ACTION_DIAGNOSTIC",rows=rows,
        what_is_closed="Classical zero-background coherent matter actuation has no first-order fundamental Phi source",
        verification_status="PRODUCTION_SOURCE_HARMONICS_CHECKED",
        open_blockers=["physical_preparation_and_measurement_of_matter_amplitude","normal_state_variance_response","response_propagator_and_energy_input","material_SI_mapping"],
        dependency_unlocked=[],full_core_unlock=False,
        claim_boundary="Prescribed chi is a diagnostic, not an on-shell driven solution. A normal thermal variance may respond linearly to another input; this result does not exclude that route. No epsilon division at GR null, no calibration value or holdout.",
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in files])
    (ROOT/"docs/core/07_artifacts/topic13/t13_matter_actuation_harmonics_audit.json").write_text(json.dumps(r,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    for row in rows:print(row)


if __name__=="__main__":main()
