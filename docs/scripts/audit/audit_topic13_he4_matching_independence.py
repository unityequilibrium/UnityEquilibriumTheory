"""Distinguish a calibration matching identity from an independent prediction."""
import json
import math
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]


def matching(theta, natural_alpha, physical_alpha):
    if not all(math.isfinite(x) and x!=0 for x in (theta,natural_alpha,physical_alpha)):
        raise ValueError('finite nonzero matching inputs required')
    z=theta*natural_alpha/physical_alpha
    return dict(Z=z,reconstructed_alpha=theta*natural_alpha/z)


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    paths={name:ROOT/'docs/core/artifacts'/filename for name,filename in {
        'composition':'t13_he4_core_thermodynamic_bridge_composition_audit.json',
        'alpha':'t13_he4_o2_response_calibration_audit.json',
        'beta':'t13_he4_o2_si_beta_mapping_audit.json',
        'natural':'t13_uet_o2_action_thermal_observable_bridge_audit.json'}.items()}
    docs={k:json.loads(p.read_text()) for k,p in paths.items()}
    for item in docs['composition']['major_result']['evidence_artifacts']:
        if digest(ROOT/item['path'])!=item['sha256']: raise ValueError('stale composition evidence')
    a=docs['alpha']['record'];n=docs['natural']['state'];b=docs['beta']['record']
    theta=a['theta_T_K_per_natural_temperature'];alpha=a['alpha_Phi_K'];nat=n['alpha_phi_temperature_natural']
    base=matching(theta,nat,alpha)
    if not math.isclose(base['Z'],a['Z_Phi_normalized_per_natural_Phi'],rel_tol=1e-12):
        raise ValueError('source matching identity changed')
    probes=[]
    for factor in (.5,1.,2.):
        m=matching(theta,factor*nat,alpha)
        probes.append(dict(synthetic_natural_alpha_factor=factor,rematched_Z=m['Z'],
            alpha_after_rematching=m['reconstructed_alpha'],
            alpha_if_Z_frozen=theta*factor*nat/base['Z']))
    files=list(paths.values())+[ROOT/'docs/core/03_lanes/thermal/he4_o2_response_calibration.py',Path(__file__),ROOT/'docs/core/test/test_topic13_he4_matching_independence.py']
    result=dict(major_result_id='T13_HE4_MATCHING_INDEPENDENCE_BOUNDARY',topic='0.13',closure_level='PARTIAL',
        what_is_closed=['Existing Z matching identity reconstructed; its alpha agreement is algebraic by construction, not an independent physical test'],
        equation_or_mapping='Z = theta_T * alpha_natural / alpha_external; theta_T * alpha_natural / Z = alpha_external',
        units='theta: K per natural temperature; alpha_external: K per normalized response; Z: normalized response per natural Phi',
        derivation_class='AUDIT_OF_EXISTING_CALIBRATION_MATCHING',observable='local normalized He-4 superfluid-fraction coordinate',
        data_role='CALIBRATION_IDENTITY_AUDIT_WITH_SYNTHETIC_RESCALE_PROBES',verification_status='MATCHING_IDENTITY_CONFIRMED_PROTOCOL_MATCH_OPEN',
        recorded_core_status=docs['composition']['status'],recorded_core_status_changed=False,
        external_alpha=alpha,Z=base['Z'],synthetic_probes=probes,
        protocol_comparison=dict(external='equilibrium SVP fraction-versus-temperature finite difference',
            natural='energy Phi derivative at fixed T,mu divided by energy temperature derivative at fixed mu,Phi',
            conclusion='Equality after scale matching does not independently establish that the two perturbation protocols coincide'),
        SI_scale_class=b['record_kind'],natural_branch=n['branch'],
        independence=dict(holdout_independent_calibration_not_disputed=True,independent_action_to_material_prediction_established=False,
                          failure_of_physical_model_proven=False),
        open_blockers=['independent perturbation-protocol and state-variable correspondence beyond matching',
                       'physical validation of an observable not used to set theta,Z,e0',
                       'clarify normal-component versus whole-He-II interpretation'],
        dependency_unlocked=['calibrated interface interpretation only; no new physical unlock'],full_core_unlock=False,claim_promotion=False,
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in files},
        claim_boundary='Does not invalidate external fraction calibration or forbid EFT matching. Synthetic rescaling is not physical data. Retain bounded composition as recorded, but do not call its matching identity an independent validation. No holdout, calibration retune or gate rewrite.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_he4_matching_independence_audit.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(external_alpha=alpha,Z=base['Z'],probes=probes),indent=2))


if __name__=='__main__':main()
