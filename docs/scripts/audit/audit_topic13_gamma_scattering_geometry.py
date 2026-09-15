"""Gamma kinematic geometry only; common atomic/Debye-Waller factors omitted."""
import hashlib
import json
from pathlib import Path
import numpy as np
import phonopy
from docs.scripts.audit.audit_topic13_mp48_interlayer_mode_residue import LOCKS
from docs.scripts.audit.audit_topic13_mp48_force_constant_harmonic_reconstruction import PHONOPY_PATH, load_force_constants

ROOT = Path(__file__).resolve().parents[3]


def pair_weight(q, positions, masses, vectors):
    q, positions, masses, vectors = map(np.asarray, (q, positions, masses, vectors))
    if q.shape != (3,) or positions.shape != (len(masses), 3) or vectors.shape[0] != 3*len(masses):
        raise ValueError('Cartesian geometry and mass-weighted eigenvectors required')
    if not all(np.isfinite(a).all() for a in (q, positions, masses, vectors)) or np.any(masses <= 0):
        raise ValueError('finite inputs and positive masses required')
    e = vectors.reshape(len(masses), 3, -1)
    amplitude = np.sum(np.exp(1j*(positions @ q))[:, None]*np.einsum('i,sij->sj', q, e)/np.sqrt(masses)[:, None], axis=0)
    return float(np.sum(abs(amplitude)**2))


def main():
    for path, expected in LOCKS.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('changed source')
    model = phonopy.load(str(PHONOPY_PATH), produce_fc=False, symmetrize_fc=False, is_nac=False, lang='C')
    model.force_constants = load_force_constants()[0]
    matrix = model.run_qpoints([[0, 0, 0]], with_dynamical_matrices=True).dynamical_matrices[0]
    _, vectors = np.linalg.eigh(matrix)
    cell = model.primitive
    reciprocal = 2*np.pi*np.linalg.inv(cell.cell).T
    pairs = [[3, 4], [8, 9]]
    identity_path = ROOT/'docs/core/07_artifacts/topic13/t13_mp48_e2g_multiplicity_audit.json'
    identity = json.loads(identity_path.read_text())
    if [r['indices'] for r in identity['eigenspaces'] if r['e2g']] != pairs:
        raise ValueError('source branch identity changed')
    for relative, expected in identity['evidence_hashes'].items():
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() != expected:
            raise ValueError('stale identity evidence')
    rows = []
    for h, k in ((1, 0), (0, 1), (1, 1), (2, 0), (2, 1), (3, 0)):
        q = np.array([h, k, 0]) @ reciprocal
        weights = [pair_weight(q, cell.positions, cell.masses, vectors[:, p]) for p in pairs]
        rows.append(dict(hkl=[h, k, 0], q_inverse_angstrom=q.tolist(), pair_geometry_weights=weights))
    table = np.array([r['pair_geometry_weights'] for r in rows])
    norms = np.linalg.norm(table, axis=0)
    singular = np.linalg.svd(table/np.where(norms > 0, norms, 1), compute_uv=False)
    evidence = list(LOCKS)+[Path(__file__), identity_path, ROOT/'docs/core/test/test_topic13_gamma_scattering_geometry.py',
                          ROOT/'docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py',
                          ROOT/'docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic13_gamma_geometry_addendum.json']
    artifact = dict(major_result_id='T13_GAMMA_SCATTERING_GEOMETRY', topic='0.13', closure_level='PARTIAL',
        what_is_closed=['Pair-resolved ideal Gamma geometry evaluated at six basal reciprocal vectors'],
        equation_registry_ids=['uet.diagnostic.gamma_one_phonon_geometry'],
        equation_or_mapping='S_pair(Q)=sum_j_in_pair |sum_s exp(i Q.r_s) Q.e_sj/sqrt(m_s)|^2',
        units={'Q': 'angstrom^-1', 'r': 'angstrom', 'mass': 'atomic mass unit', 'S': 'angstrom^-2/atomic mass unit'},
        derivation_class='IMPORTED_KINEMATIC_GEOMETRY_WITH_DECLARED_PHASE_CONVENTION',
        observable='geometric part of one-phonon structure factor, not detector counts', data_role='SOURCE_MODEL_DIAGNOSTIC',
        verification_status='GEOMETRY_ONLY_INVERSION_OPEN', rows=rows, column_norms=norms.tolist(),
        column_normalized_singular_values=singular.tolist(),
        assumptions=['Gamma eigenvectors in atom basis; explicit position phase', 'common carbon form factor factored out',
                     'equal site Debye-Waller factors factored out', 'equal occupation within each degenerate pair for scalar use',
                     'kinematic single-phonon approximation', 'no finite-q, resolution, elastic peak or detector model'],
        open_blockers=['actual finite-q gauge and scattering model', 'Bragg separation and covariance', 'independent Phi coupling'],
        full_core_unlock=False, claim_promotion=False, dependency_unlocked=['finite-q forward-model design only'],
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in evidence},
        claim_boundary='Gamma ideal geometry only; no population inversion or experimental identifiability proof. Original grouping uncertainty retained upstream.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_gamma_scattering_geometry_audit.json').write_text(json.dumps(artifact, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(rows=rows, singular_values=singular.tolist()), indent=2))


if __name__ == '__main__':
    main()
