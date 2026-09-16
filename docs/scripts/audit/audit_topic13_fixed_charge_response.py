"""Natural-lane ensemble derivative check; O(2) charge is not He-4 mass density."""
import json
import hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import finite_temperature_o2_state

ROOT=Path(__file__).resolve().parents[3]


def constrained_derivative(e_x,e_mu,n_x,n_mu):
    if not np.isfinite([e_x,e_mu,n_x,n_mu]).all() or n_mu<=0:
        raise ValueError('finite derivatives and positive charge susceptibility required')
    return e_x-e_mu*n_x/n_mu


def main():
    source=ROOT/'docs/core/07_artifacts/topic13/t13_uet_o2_action_thermal_observable_bridge_audit.json'
    a=json.loads(source.read_text());s=a['state']
    base=np.array([s['temperature'],s['chemical_potential'],s['space_response']])
    cfg=natural_bridge_config()
    def state(v):
        r=finite_temperature_o2_state(*v,cfg)
        if r.branch!=s['branch']: raise ValueError('branch changed')
        return r
    ref=state(base);records=[]
    for h in (.001,.0005,.00025):
        e=[];n=[]
        for i in range(3):
            v=base.copy();v[i]+=h;plus=state(v)
            v=base.copy();v[i]-=h;minus=state(v)
            e.append((plus.energy_density-minus.energy_density)/(2*h))
            n.append((plus.charge_density-minus.charge_density)/(2*h))
        constrained=[constrained_derivative(e[i],e[1],n[i],n[1]) for i in (0,2)]
        direct=[];charge_errors=[];mus=[]
        for i in (0,2):
            energy=[]
            for sign in (-1,1):
                v=base.copy();v[i]+=sign*h
                def residual(mu):
                    v[1]=mu
                    return state(v).charge_density-ref.charge_density
                mu=brentq(residual,base[1]-.03,base[1]+.03,xtol=1e-12)
                v[1]=mu;r=state(v);mus.append(mu)
                charge_errors.append(abs(r.charge_density-ref.charge_density))
                energy.append(r.energy_density)
            direct.append((energy[1]-energy[0])/(2*h))
        records.append(dict(step=h,energy_derivatives_T_mu_Phi=e,charge_derivatives_T_mu_Phi=n,
            fixed_mu_thermal_susceptibility=e[0],fixed_charge_thermal_susceptibility=constrained[0],
            fixed_charge_Phi_response=constrained[1],fixed_charge_alpha=constrained[1]/constrained[0],
            fixed_mu_alpha=e[2]/e[0],direct_fixed_charge_derivatives_T_Phi=direct,
            absolute_chain_vs_direct_disagreement=np.abs(np.array(constrained)-direct).tolist(),
            max_charge_constraint_residual=max(charge_errors),solved_mu_values=mus))
    files=[source,Path(__file__),ROOT/'docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py',
           ROOT/'docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py',ROOT/'docs/core/test/test_topic13_fixed_charge_response.py']
    result=dict(major_result_id='T13_NATURAL_FIXED_CHARGE_RESPONSE',topic='0.13',closure_level='PARTIAL',
        what_is_closed=['Fixed-charge response evaluated by chain-rule derivatives and direct charge-constrained roots at three steps'],
        equation_or_mapping='(d epsilon/dx)_n = epsilon_x - epsilon_mu*n_x/n_mu, x=T or Phi',
        units='natural lane only; n is O(2) charge density, not He-4 atom or mass density',
        derivation_class='IMPLICIT_FUNCTION_CHAIN_RULE_AND_NUMERICAL_CROSSCHECK',observable='natural energy susceptibility under declared constraints',
        data_role='INTERNAL_DERIVATIVE_COMPARISON',verification_status='ENSEMBLE_COMPARISON_NOT_PHYSICAL_CALIBRATION',
        state=base.tolist(),branch=s['branch'],records=records,
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        open_blockers=['O(2) charge to material density correspondence','physical thermodynamic path and uncertainty','independent material observable'],
        dependency_unlocked=['ensemble-specific natural response comparison only'],full_core_unlock=False,claim_promotion=False,
        claim_boundary='No parameter or calibration retuning. This does not identify either susceptibility as physical c_v or SVP response. Existing Core composition remains unchanged; no holdout read.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_fixed_charge_response_audit.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(records,indent=2))


if __name__=='__main__':main()
