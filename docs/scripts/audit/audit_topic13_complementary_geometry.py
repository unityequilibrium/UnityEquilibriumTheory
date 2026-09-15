"""Ideal added reciprocal-plane information; not acquired experimental data."""
import hashlib
import json
from pathlib import Path
import numpy as np
import phonopy
from docs.scripts.audit.audit_topic13_finiteq_scattering_geometry import mode_geometry
from docs.scripts.audit.audit_topic13_energy_identifiability import observable_null_test
from docs.scripts.audit.audit_topic13_mp48_interlayer_mode_residue import LOCKS
from docs.scripts.audit.audit_topic13_mp48_force_constant_harmonic_reconstruction import PHONOPY_PATH, load_force_constants, load_phonopy

ROOT = Path(__file__).resolve().parents[3]


def reciprocal_design(layers):
    return [[h, k, l] for l in layers for h in range(-2, 3) for k in range(-2, 3) if h or k or l]


def main():
    for path, expected in LOCKS.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('changed source')
    source_path = ROOT/'docs/core/07_artifacts/topic13/t13_finiteq_scattering_geometry_audit.json'
    source = json.loads(source_path.read_text())
    for relative, expected in source['evidence_hashes'].items():
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() != expected:
            raise ValueError('stale source evidence')
    model = phonopy.load(str(PHONOPY_PATH), produce_fc=False, symmetrize_fc=False, is_nac=False, lang='C')
    model.force_constants = load_force_constants()[0]
    cell = model.primitive
    rec = 2*np.pi*np.linalg.inv(cell.cell).T
    factor = float(load_phonopy()['phonopy']['frequency_unit_conversion_factor'])
    designs = {'basal': [0], 'basal_plus_one': [0, 1], 'symmetric_one': [-1, 0, 1], 'symmetric_two': [-2, -1, 0, 1, 2]}
    results = []
    for old in source['results']:
        q = old['q_fractional']
        matrix = model.run_qpoints([q], with_dynamical_matrices=True).dynamical_matrices[0]
        values, e = np.linalg.eigh(matrix)
        f = np.sign(values)*np.sqrt(abs(values))*factor
        np.testing.assert_allclose(f, old['signed_frequencies_THz'], atol=1e-10)
        if np.any(f <= 0):
            raise ValueError('nonpositive gap; no clipping allowed')
        comparisons = {}
        for name, layers in designs.items():
            grid = reciprocal_design(layers)
            s = np.array([mode_geometry((np.array(g)+q) @ rec, g, cell.scaled_positions, cell.masses, e) for g in grid])
            a = s/f
            if name == 'basal':
                np.testing.assert_allclose(s, old['geometry'], atol=1e-12, rtol=1e-10)
            test = observable_null_test(a, f)
            singular = np.linalg.svd(a, compute_uv=False)
            condition = float(singular[0]/singular[-1]) if singular[-1] > 0 else None
            comparisons[name] = dict(rows=len(grid), energy_test=test,
                singular_values=singular.tolist(), raw_condition_number=condition,
                tolerance_sweep={str(t): observable_null_test(a, f, t)['observable_null_fraction'] for t in (1e-9, 1e-10, 1e-11)})
        results.append(dict(q_fractional=q, designs=comparisons))
    files = list(LOCKS)+[source_path, Path(__file__),
        ROOT/'docs/scripts/audit/audit_topic13_finiteq_scattering_geometry.py',
        ROOT/'docs/scripts/audit/audit_topic13_energy_identifiability.py',
        ROOT/'docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py',
        ROOT/'docs/core/test/test_topic13_complementary_geometry.py']
    artifact = dict(major_result_id='T13_COMPLEMENTARY_ENERGY_GEOMETRY_DESIGN', topic='0.13', closure_level='PARTIAL',
        what_is_closed=['Ideal extra reciprocal-plane energy information evaluated with unchanged source and response equations'],
        equation_registry_ids=['uet.diagnostic.finiteq_one_phonon_geometry', 'uet.diagnostic.harmonic_energy_identifiability'],
        equation_or_mapping='Same A=S/f and energy row-space test, augmented with G_z != 0 at the same reduced q',
        units={'f': 'THz', 'G': 'fractional reciprocal', 'energy_null_fraction': '1, not physical error'},
        derivation_class='IDEAL_MEASUREMENT_DESIGN', observable='model energy information under added reciprocal-plane coverage',
        data_role='SOURCE_MODEL_DESIGN_NOT_ACQUIRED_DATA', verification_status='COMPLEMENTARY_DESIGNS_EVALUATED',
        designs={k: reciprocal_design(v) for k, v in designs.items()}, results=results,
        assumptions=['same material/populations at same reduced q across all added measurements',
                     'kinematic, common-site atomic and Debye-Waller factors', 'ideal coverage, no noise or resolution'],
        open_blockers=['experimental access to added reciprocal planes', 'matched preparation and orientation',
                       'absolute intensity and noise conditioning', 'independent Phi coupling'],
        full_core_unlock=False, claim_promotion=False, dependency_unlocked=['complementary measurement/source targeting only'],
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        claim_boundary='Not experimental closure or a new dataset. No fit, holdout or physical alpha; added geometry may be inaccessible.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_complementary_geometry_audit.json').write_text(json.dumps(artifact, indent=2, allow_nan=False)+'\n')
    print(json.dumps([dict(q=r['q_fractional'], designs={k:dict(rank=v['energy_test']['rank'], null=v['energy_test']['observable_null_fraction']) for k,v in r['designs'].items()}) for r in results], indent=2))


if __name__ == '__main__':
    main()
