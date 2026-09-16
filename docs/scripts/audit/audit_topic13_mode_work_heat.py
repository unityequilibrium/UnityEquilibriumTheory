"""Source pole illustration of protocol separation, not material calorimetry."""

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.constants import Planck, speed_of_light

from docs.core.uet_mode_work_heat import equilibrium, protocol_response

ROOT = Path(__file__).resolve().parents[3]


def main():
    path = ROOT/'docs/core/07_artifacts/topic13/t13_mp48_interlayer_mode_residue_audit.json'
    source = json.loads(path.read_text(encoding='utf-8'))
    for relative, expected in source['evidence_hashes'].items():
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() != expected:
            raise ValueError('stale precursor: '+relative)
    frequencies = source['q_path_results'][0]['frequencies_cm_inverse']
    gaps = Planck*speed_of_light*100*np.asarray(frequencies)
    temperature = 200.
    result = protocol_response(gaps, temperature, gaps, np.ones(len(gaps)))
    state = equilibrium(gaps, temperature)
    files = [path, Path(__file__), ROOT/'docs/core/03_lanes/thermal/uet_mode_work_heat.py',
             ROOT/'docs/core/test/test_topic13_mode_work_heat.py',
             ROOT/'docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic13_mode_heat_addendum.json']
    artifact = dict(
        major_result_id='T13_MODE_WORK_HEAT_PROTOCOL_SEPARATION', topic='0.13',
        closure_level='CLOSED_FOR_LANE', verification_status='PASS_CONDITIONAL_HARMONIC_PROTOCOLS',
        what_is_closed=['Mode energy separates source work and occupation heat',
                        'Equilibrium isentropic gain requires mode-specific source derivatives',
                        'Frozen unequal mode scalings do not define one thermal temperature'],
        equation_or_mapping='dU=sum[(n+1/2)*d_epsilon+epsilon*dn]; dT/dlambda|S=T*sum(C_i*epsilon_i_prime/epsilon_i)/sum(C_i)',
        units={'gaps': 'J', 'capacity': 'J/K for the two-oscillator illustration',
               'work_and_heat_derivatives': 'J per dimensionless log-gap control',
               'isentropic_gain': 'K per dimensionless log-gap control'},
        derivation_class='harmonic_equilibrium_first_law',
        observable='protocol-dependent energy, heat and equilibrium temperature tangent',
        data_role='SOURCE_FREQUENCIES_WITH_SYNTHETIC_CONTROL_NOT_CALIBRATION',
        control={'identity': 'lambda=common log-gap scaling', 'gap_derivative': 'epsilon_i_prime=epsilon_i',
                 'physical_source': False, 'Phi_identified': False},
        gaps_J=gaps.tolist(), temperature_K=temperature,
        population=state['occupation'].tolist(), result=result,
        zero_point_policy='Retained in oscillator energy/work, absent from heat and entropy; not UET vacuum matching.',
        scope='Two Gamma oscillators with unit weights, not Brillouin-zone or sample heat capacity.',
        open_blockers=['physical epsilon_i_prime(Phi)', 'normalization', 'source/bath relaxation',
                       'full dispersion/weights and same-state material match'],
        dependency_unlocked=['protocol-aware thermal mapping design only'],
        full_core_unlock=False, claim_promotion=False, alpha_Phi_K=None,
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        claim_boundary='No temperature prediction for a driven TTG experiment, KMS/bath coefficient or physical alpha.',
    )
    (ROOT/'docs/core/07_artifacts/topic13/t13_mode_work_heat_audit.json').write_text(json.dumps(artifact, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
