"""Natural reversible source work: fixed volume, entropy and O(2) charge."""
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.optimize import root
from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import finite_temperature_o2_state

ROOT = Path(__file__).resolve().parents[3]


def tangent(jacobian, gradient):
    j, g = np.asarray(jacobian, float), np.asarray(gradient, float)
    if j.shape != (2, 2) or g.shape != (2,) or not np.isfinite(j).all() or not np.isfinite(g).all():
        raise ValueError('finite two-constraint Jacobian required')
    return np.linalg.solve(j, -g)


def main():
    source = ROOT/'docs/core/07_artifacts/topic13/t13_uet_o2_action_thermal_observable_bridge_audit.json'
    a = json.loads(source.read_text()); s = a['state']; cfg = natural_bridge_config()
    revisions = []
    for e in a['major_result']['evidence_artifacts']:
        actual = hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()
        revisions.append(dict(path=e['path'], historical_sha256=e['sha256'], current_sha256=actual,
                              matches_historical=actual == e['sha256']))
    base = np.array([s['temperature'], s['chemical_potential'], s['space_response']])
    def state(v):
        r = finite_temperature_o2_state(*v, cfg)
        if r.branch != s['branch']: raise ValueError('branch changed')
        return r
    def vector(r):
        return np.array([r.entropy_density, r.charge_density, r.pressure, r.energy_density])
    target = vector(state(base))[:2]; records = []
    for h in (.001, .0005, .00025):
        gradients = []
        for i in range(3):
            v = base.copy(); v[i] += h; plus = vector(state(v))
            v = base.copy(); v[i] -= h; minus = vector(state(v))
            gradients.append((plus-minus)/(2*h))
        g = np.array(gradients).T; d = tangent(g[:2, :2], g[:2, 2])
        work = -g[2, 2]; chain = g[3, 2]+g[3, :2]@d
        solved = []; residuals = []
        for sign in (-1, 1):
            phi = base[2]+sign*h
            def constraint(tm):
                return (vector(state([*tm, phi]))[:2]-target)/target
            sol = root(constraint, base[:2]+sign*h*d, tol=1e-10)
            residual = float(np.max(np.abs(constraint(sol.x))))
            if residual > 1e-9: raise ValueError('constraint root residual too large')
            solved.append([*sol.x, state([*sol.x, phi]).energy_density])
            residuals.append(dict(success=bool(sol.success), scaled_residual=residual))
        direct = (np.array(solved[1])-solved[0])/(2*h)
        records.append(dict(step=h, dT_dPhi=float(d[0]), dmu_dPhi=float(d[1]),
            direct_dT_dPhi=float(direct[0]), source_work_derivative=float(work),
            chain_energy_derivative=float(chain), direct_energy_derivative=float(direct[2]),
            chain_first_law_relative_error=float(abs(chain-work)/abs(work)),
            direct_first_law_relative_error=float(abs(direct[2]-work)/abs(work)), root_checks=residuals))
    files = [source, Path(__file__), ROOT/'docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py',
        ROOT/'docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py', ROOT/'docs/core/test/test_topic13_isentropic_source_work.py']
    result = dict(major_result_id='T13_NATURAL_ISENTROPIC_SOURCE_WORK', topic='0.13', closure_level='PARTIAL',
        what_is_closed=['Natural reversible source-work balance compared using derivatives and constrained roots'],
        equation_or_mapping='J_(s,n)/(T,mu)*(T_Phi,mu_Phi)=-(s_Phi,n_Phi); d epsilon|s,n = -p_Phi dPhi at fixed volume',
        units='natural EOS units; O(2) charge is not He-4 mass density', derivation_class='IMPLICIT_CONSTRAINT_AND_FIRST_LAW',
        observable='quasistatic natural source response', data_role='INTERNAL_NO_CALIBRATION',
        verification_status='CURRENT_EOS_REVERSIBLE_WORK_NOT_HISTORICAL_REPLICATION', state=base.tolist(), records=records,
        source_revision_comparison=revisions,
        provenance_scope='Historical artifact supplies initial coordinates only. Current source code is hashed separately; EOS changed in bd55dc487. No historical closure or calibration is regenerated.',
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        open_blockers=['physical process and material-variable mapping', 'finite-rate entropy production and relaxation'],
        dependency_unlocked=['natural reversible accounting only'], full_core_unlock=False, claim_promotion=False,
        claim_boundary='Zero reversible heat follows imposed ds=0; not a finite-rate isolation proof, SI alpha or He-4 validation. No holdout, retuning or composition gate change.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_isentropic_source_work_audit.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(records, indent=2))


if __name__ == '__main__': main()
