"""Noncommutation of spatial averaging and the existing quadratic source."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.core.uet_covariant_matter import CovariantMatterConfig, coupled_response_scalar_equation_residual
from docs.core.uet_covariant_response import CovariantResponseConfig


def source_average(chi,weights,epsilon=.5,h=.8):
    chi=np.asarray(chi,dtype=float); weights=np.asarray(weights,dtype=float)
    if chi.ndim!=2 or chi.shape[1]!=2 or weights.shape!=(len(chi),) or not np.isfinite(chi).all() or not np.isfinite(weights).all():
        raise ValueError('finite two-component field and matching weights required')
    if np.any(weights<0) or not np.isclose(weights.sum(),1.,atol=1e-14,rtol=0):
        raise ValueError('nonnegative normalized averaging weights required')
    response=CovariantResponseConfig(epsilon_nc=epsilon)
    matter=CovariantMatterConfig(response_coupling=h)
    def residual(field):
        return coupled_response_scalar_equation_residual(0.,0.,response.phi_equilibrium,field,response,matter)
    zero=residual([0.,0.])
    mean=weights@chi
    local_average=float(weights@np.array([residual(field)-zero for field in chi]))
    source_of_mean=float(residual(mean)-zero)
    variance=float(weights@np.sum((chi-mean)**2,axis=1))
    expected_gap=epsilon*h*variance/2
    return dict(local_source_average=local_average,source_of_mean=source_of_mean,
        unresolved_variance=variance,expected_gap=expected_gap,
        identity_error=abs(local_average-source_of_mean-expected_gap))


def main():
    fixtures=[('opposed_zero_mean',[[1.,0.],[-1.,0.]],[.5,.5]),
        ('uniform',[[.4,.2],[.4,.2]],[.5,.5]),
        ('unequal_weights',[[.1,.3],[-.2,.4],[.8,-.1]],[.2,.3,.5])]
    rows=[dict(case=name,**source_average(chi,w)) for name,chi,w in fixtures]
    rows.append(dict(case='GR_null',**source_average([[1.,0.],[-1.,0.]],[.5,.5],epsilon=0)))
    paths=[Path(__file__),ROOT/'docs/core/test/test_topic13_quadratic_source_averaging.py',
           ROOT/'docs/core/02_equations/covariant/uet_covariant_matter.py',ROOT/'docs/core/02_equations/covariant/uet_covariant_response.py']
    artifact=dict(major_result_id='T13_QUADRATIC_SOURCE_SPATIAL_AVERAGING',topic='0.13',closure_level='CLOSED_FOR_LANE',
        what_is_closed='Exact finite positive-weight averaging identity of the existing quadratic source',
        equation_or_mapping='sum w_i J(chi_i)-J(sum w_i chi_i)=epsilon*h/2 * sum w_i |chi_i-chi_bar|^2',
        units='chi energy; h energy; J energy^3; weights dimensionless',
        derivation_class='algebraic identity checked against production residual',
        observable='spatially averaged source, not detector temperature',data_role='SYNTHETIC_ACTION_DIAGNOSTIC',
        rows=rows,verification_status='PRODUCTION_RESIDUAL_IDENTITY_CHECKED',
        controlling_blocker='physical_local_second_moment_and_UET_operator_normalization',
        open_blockers=['material_to_chi_map','dynamic_susceptibility','calibration_source_and_uncertainty'],
        dependency_unlocked=[],full_core_unlock=False,global_claim_promotion=False,
        claim_boundary='Not an on-shell experiment or a new effective closure. Signed Fourier weights and renormalized quantum composites require separate treatment.',
        evidence_artifacts=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha256(p.read_bytes()).hexdigest()) for p in paths])
    (ROOT/'docs/core/07_artifacts/topic13/t13_quadratic_source_averaging.json').write_text(json.dumps(artifact,indent=2,allow_nan=False)+'\n')
    print(json.dumps(rows))


if __name__=='__main__':main()
