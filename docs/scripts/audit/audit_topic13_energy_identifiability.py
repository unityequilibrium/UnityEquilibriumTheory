"""Linear observable identifiability, not population fitting or thermometry."""
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]


def observable_null_test(response, energy, rtol=1e-10):
    a, c = np.asarray(response, float), np.asarray(energy, float)
    if a.ndim != 2 or c.shape != (a.shape[1],) or not np.isfinite(a).all() or not np.isfinite(c).all():
        raise ValueError('finite response and matching observable required')
    if not 0 < rtol < 1 or np.linalg.norm(c) == 0:
        raise ValueError('nonzero observable and relative tolerance required')
    _, singular, vh = np.linalg.svd(a, full_matrices=True)
    rank = int(np.sum(singular > (singular[0]*rtol if len(singular) else 0)))
    null_component = c-vh[:rank].T @ (vh[:rank] @ c)
    relative = float(np.linalg.norm(null_component)/np.linalg.norm(c))
    result = dict(rank=rank, observable_null_fraction=relative, relative_rank_tolerance=rtol,
                  identifiable_at_numerical_tolerance=relative <= 1e-8)
    if relative > 1e-8:
        shift = .25*null_component/np.max(abs(null_component))
        plus, minus = np.ones(len(c))+shift, np.ones(len(c))-shift
        difference = plus-minus
        result['synthetic_witness'] = dict(n_plus=plus.tolist(), n_minus=minus.tolist(),
            normalized_response_difference=float(np.linalg.norm(a @ difference)/(max(np.linalg.norm(a), 1e-300)*np.linalg.norm(difference))),
            energy_difference=float(c @ difference),
            relative_energy_difference_to_unit_population=float((c @ difference)/np.sum(c)) if np.sum(c) != 0 else None,
            interpretation='Constructed positive occupations, not observed data, fit, equilibrium or source preparation')
    return result


def main():
    source_path = ROOT/'docs/core/07_artifacts/topic13/t13_finiteq_scattering_geometry_audit.json'
    source = json.loads(source_path.read_text())
    for relative, expected in source['evidence_hashes'].items():
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() != expected:
            raise ValueError('stale source evidence')
    rows = []
    for row in source['results']:
        f = np.asarray(row['signed_frequencies_THz'])
        if np.any(f <= 0):
            raise ValueError('positive gaps required, no frequency clipping')
        geometry = np.asarray(row['geometry'])
        response = geometry/f[None, :]
        visible = np.array(row['resolved_geometry_columns'])
        rows.append(dict(q_fractional=row['q_fractional'],
            full_energy=observable_null_test(response, f),
            visible_energy=observable_null_test(response[:, visible], f[visible]),
            tolerance_sweep={str(t): observable_null_test(response, f, t)['observable_null_fraction'] for t in (1e-9, 1e-10, 1e-11)},
            visible_indices=visible.tolist()))
    files = [source_path, Path(__file__), ROOT/'docs/core/test/test_topic13_energy_identifiability.py',
        ROOT/'docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic13_energy_identifiability_addendum.json']
    result = dict(major_result_id='T13_HARMONIC_ENERGY_OBSERVABILITY', topic='0.13', closure_level='PARTIAL',
        what_is_closed=['Energy functional tested against the declared frequency-weighted response null space'],
        equation_registry_ids=['uet.diagnostic.harmonic_energy_identifiability'],
        equation_or_mapping='A=S/f; deltaI=A delta_n up to common factors; deltaU/(h*1e12 Hz)=sum f_THz delta_n; c identifiable iff c in row(A)',
        units={'f': 'THz', 'A': 'angstrom^-2/(atomic mass unit*THz)', 'energy_witness': 'h*1e12 Hz per declared q-mode set'},
        derivation_class='LINEAR_ALGEBRA_ON_FIXED_HARMONIC_RESPONSE', observable='population energy at fixed frequencies and fixed q',
        data_role='SOURCE_MODEL_PLUS_SYNTHETIC_COUNTEREXAMPLE', verification_status='NULL_SPACE_TESTED_NOT_THERMOMETRY',
        results=rows, assumptions=['fixed source gaps and scattering factors', 'no work from changing frequencies',
                                  'no equilibrium population constraint', 'no Brillouin-zone integration or material temperature'],
        open_blockers=['independent energy-sensitive data or justified closure', 'detector/covariance response', 'independent Phi coupling'],
        full_core_unlock=False, claim_promotion=False, dependency_unlocked=['energy-sensitive observable design only'],
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        claim_boundary='Conditional numerical counterexamples, not observed populations or a universal no-go. No holdout read, fit or calibration.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_energy_identifiability_audit.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps([dict(q=r['q_fractional'], full_null=r['full_energy']['observable_null_fraction'],
        visible_null=r['visible_energy']['observable_null_fraction'],
        response_residual=r['full_energy'].get('synthetic_witness', {}).get('normalized_response_difference')) for r in rows], indent=2))


if __name__ == '__main__':
    main()
