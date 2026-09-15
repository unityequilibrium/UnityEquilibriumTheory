"""Minimum-variance scalar estimator; covariance cases are hypothetical only."""
import hashlib
import json
from pathlib import Path
import numpy as np
import phonopy
from docs.scripts.audit.audit_topic13_finiteq_scattering_geometry import mode_geometry
from docs.scripts.audit.audit_topic13_mp48_interlayer_mode_residue import LOCKS
from docs.scripts.audit.audit_topic13_mp48_force_constant_harmonic_reconstruction import PHONOPY_PATH, load_force_constants, load_phonopy

ROOT = Path(__file__).resolve().parents[3]


def energy_estimator(a, c, covariance):
    a, c, covariance = map(lambda x: np.asarray(x, float), (a, c, covariance))
    if a.ndim != 2 or c.shape != (a.shape[1],) or covariance.shape != (a.shape[0], a.shape[0]):
        raise ValueError('compatible response, functional and covariance required')
    if not all(np.isfinite(x).all() for x in (a, c, covariance)) or not np.allclose(covariance, covariance.T):
        raise ValueError('finite data and symmetric covariance required')
    lower = np.linalg.cholesky(covariance)
    whitened = np.linalg.solve(lower, a)
    z, _, _, _ = np.linalg.lstsq(whitened.T, c, rcond=1e-10)
    w = np.linalg.solve(lower.T, z)
    residual = np.linalg.norm(a.T @ w-c)/max(np.linalg.norm(c), 1e-300)
    if residual > 1e-8:
        raise ValueError('target is not identifiable; no unbiased estimator')
    return w, float(w @ covariance @ w), float(residual)


def main():
    path = ROOT/'docs/core/07_artifacts/topic13/t13_complementary_geometry_audit.json'
    source = json.loads(path.read_text())
    for relative, expected in source['evidence_hashes'].items():
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() != expected:
            raise ValueError('stale source')
    for p, expected in LOCKS.items():
        if hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            raise ValueError('changed force source')
    model = phonopy.load(str(PHONOPY_PATH), produce_fc=False, symmetrize_fc=False, is_nac=False, lang='C')
    model.force_constants = load_force_constants()[0]
    cell = model.primitive
    rec = 2*np.pi*np.linalg.inv(cell.cell).T
    factor = float(load_phonopy()['phonopy']['frequency_unit_conversion_factor'])
    grid = source['designs']['symmetric_two']
    rows = []
    for old in source['results']:
        q = old['q_fractional']
        matrix = model.run_qpoints([q], with_dynamical_matrices=True).dynamical_matrices[0]
        values, e = np.linalg.eigh(matrix)
        f = np.sign(values)*np.sqrt(abs(values))*factor
        if np.any(f <= 0): raise ValueError('positive gaps required')
        a = np.array([mode_geometry((np.array(g)+q) @ rec, g, cell.scaled_positions, cell.masses, e) for g in grid])/f
        a_scale, c_scale = np.linalg.norm(a, 2), np.linalg.norm(f)
        normalized, c = a/a_scale, f/c_scale
        cases = {}
        for rho in (0., .2):
            cov = (1-rho)*np.eye(len(a))+rho*np.ones((len(a), len(a)))
            w, variance, error = energy_estimator(normalized, c, cov)
            cases[str(rho)] = dict(standard_deviation_per_unit_normalized_noise=float(np.sqrt(variance)),
                                  weights=w.tolist(), unbiasedness_residual=error,
                                  weight_sum=float(w.sum()))
        rows.append(dict(q_fractional=q, response_spectral_scale=float(a_scale), energy_coefficient_norm=float(c_scale), cases=cases))
    files = [path, Path(__file__), ROOT/'docs/core/test/test_topic13_energy_estimator_noise.py',
             ROOT/'docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic13_energy_estimator_addendum.json',
             ROOT/'docs/scripts/audit/audit_topic13_finiteq_scattering_geometry.py',
             ROOT/'docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py']
    result = dict(major_result_id='T13_ENERGY_ESTIMATOR_NOISE_DESIGN', topic='0.13', closure_level='PARTIAL',
        what_is_closed=['Unbiased scalar energy weights and hypothetical covariance sensitivity computed for ideal augmented design'],
        equation_registry_ids=['uet.diagnostic.energy_linear_estimator'],
        equation_or_mapping='min_w w^T Sigma w subject to A^T w=c; E_hat=w^T y',
        units={'computed_noise_gain':'dimensionless after A/||A||_2 and c/||c||_2 normalization'},
        derivation_class='LINEAR_MINIMUM_VARIANCE_ESTIMATOR', observable='normalized fixed-gap energy functional',
        data_role='SOURCE_MODEL_WITH_HYPOTHETICAL_NOISE', verification_status='UNBIASED_WEIGHTS_CHECKED_REAL_NOISE_OPEN',
        covariance_policy='Sigma=(1-rho)I+rho*11^T; rho=0 or 0.2, synthetic design cases, not measured detector noise',
        results=rows, open_blockers=['measured covariance and absolute intensity scale', 'accessible matched geometry', 'Phi coupling'],
        full_core_unlock=False, claim_promotion=False, dependency_unlocked=['noise-aware design only'],
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\', '/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        claim_boundary='No actual error bar or temperature. Real covariance, exposure budget, gain and model error not supplied. No holdout or fit.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_energy_estimator_noise_audit.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps([dict(q=r['q_fractional'], gain={k:v['standard_deviation_per_unit_normalized_noise'] for k,v in r['cases'].items()}) for r in rows], indent=2))


if __name__ == '__main__':
    main()
