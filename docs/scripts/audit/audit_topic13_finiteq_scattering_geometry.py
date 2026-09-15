"""Finite-q geometric response cross-checked against installed Phonopy amplitude."""
import hashlib
import inspect
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import phonopy
from phonopy.spectrum.dynamic_structure_factor import DynamicStructureFactor
from docs.scripts.audit.audit_topic13_mp48_interlayer_mode_residue import LOCKS
from docs.scripts.audit.audit_topic13_mp48_force_constant_harmonic_reconstruction import PHONOPY_PATH, load_force_constants, load_phonopy

ROOT = Path(__file__).resolve().parents[3]


def mode_geometry(Q_cart, G, fractional_positions, masses, eigenvectors):
    """Q has 2pi/angstrom; G and positions are fractional reciprocal/direct."""
    q, g, p, m, e = map(np.asarray, (Q_cart, G, fractional_positions, masses, eigenvectors))
    if q.shape != (3,) or g.shape != (3,) or p.shape != (len(m), 3) or e.shape != (3*len(m), 3*len(m)):
        raise ValueError('consistent complete eigensystem and geometry required')
    if not all(np.isfinite(a).all() for a in (q, g, p, m, e)) or np.any(m <= 0):
        raise ValueError('finite inputs and positive masses required')
    phase = np.exp(2j*np.pi*(p @ g))
    polar = np.einsum('a,saj->sj', q, e.conj().reshape(len(m), 3, -1))
    return abs(np.sum(phase[:, None]*polar/np.sqrt(m)[:, None], axis=0))**2


def main():
    for path, expected in LOCKS.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('source hash mismatch')
    model = phonopy.load(str(PHONOPY_PATH), produce_fc=False, symmetrize_fc=False, is_nac=False, lang='C')
    model.force_constants = load_force_constants()[0]
    cell = model.primitive
    rec = 2*np.pi*np.linalg.inv(cell.cell).T
    factor = float(load_phonopy()['phonopy']['frequency_unit_conversion_factor'])
    grid = [[h, k, 0] for h in range(-2, 3) for k in range(-2, 3) if h or k]
    qpoints = [[s, t*s, 0] for t in (0, 1) for s in (.005, .02, .1)]
    reference = SimpleNamespace(_primitive=cell, _func_AFF=None, _b={'C': 1.})
    rows = []
    for q in qpoints:
        matrix = model.run_qpoints([q], with_dynamical_matrices=True).dynamical_matrices[0]
        values, vectors = np.linalg.eigh(matrix)
        frequencies = np.sign(values)*np.sqrt(abs(values))*factor
        weights, references = [], []
        for G in grid:
            Q = (np.array(G)+q) @ rec
            weights.append(mode_geometry(Q, G, cell.scaled_positions, cell.masses, vectors))
            # Unit artificial frequency removes the reference's frequency factor;
            # this checks geometry only and does not replace physical frequencies.
            reference_values = [2*abs(DynamicStructureFactor._phonon_structure_factor(
                reference, Q/(2*np.pi), np.array(G), np.ones(len(cell)), 1., vectors[:, j].conj()))**2 for j in range(12)]
            references.append(reference_values)
        weights = np.array(weights)
        err = float(np.max(abs(weights-np.array(references)))/max(float(weights.max()), 1e-30))
        norms = np.linalg.norm(weights, axis=0)
        visibility = norms > norms.max()*1e-12
        normalized = weights[:, visibility]/norms[visibility]
        singular = np.linalg.svd(normalized, compute_uv=False)
        numerical_rank = int(np.sum(singular > singular[0]*1e-10))
        rows.append(dict(q_fractional=q, signed_frequencies_THz=frequencies.tolist(),
                         geometry=weights.tolist(), column_norms=norms.tolist(),
                         resolved_geometry_columns=np.flatnonzero(visibility).tolist(),
                         normalized_singular_values=singular.tolist(), numerical_rank=numerical_rank,
                         reference_relative_error=err))
    files = list(LOCKS)+[Path(__file__), ROOT/'docs/core/test/test_topic13_finiteq_scattering_geometry.py',
        ROOT/'docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py',
        ROOT/'docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic13_finiteq_geometry_addendum.json']
    result = dict(major_result_id='T13_FINITEQ_SCATTERING_GEOMETRY', topic='0.13', closure_level='PARTIAL',
        what_is_closed=['Finite-q amplitude convention cross-checked against installed Phonopy for declared source/grid'],
        equation_registry_ids=['uet.diagnostic.finiteq_one_phonon_geometry'],
        equation_or_mapping='S_j(Q)=|sum_s exp(2pi i G.x_s) Q.conj(e_sj(q))/sqrt(m_s)|^2, Q=(G+q) reciprocal',
        units={'Q': 'angstrom^-1 including 2pi', 'mass': 'atomic mass unit', 'S': 'angstrom^-2/atomic mass unit'},
        derivation_class='IMPORTED_KINEMATIC_GEOMETRY', observable='geometric response columns only', data_role='SOURCE_MODEL_DIAGNOSTIC',
        verification_status='REFERENCE_MATCHED_GEOMETRY_ONLY', G_grid=grid, results=rows,
        numerical_diagnostics={'column_visibility_relative': 1e-12, 'rank_relative': 1e-10,
                               'meaning': 'floating-point diagnostics, not physical resolution or confidence'},
        phonopy_version=phonopy.__version__,
        reference_method_sha256=hashlib.sha256(inspect.getsource(DynamicStructureFactor._phonon_structure_factor).encode()).hexdigest(),
        reference_limit='Amplitude algebra cross-check, not independent force-constant or physical validation',
        assumptions=['common atomic and equal-site Debye-Waller factors omitted', 'kinematic single phonon',
                     'ideal 24 reciprocal vectors, not verified detector coverage', 'no population fit or equal-pair occupation assumption'],
        open_blockers=['experimental response rank with covariance and elastic contamination', 'finite-q branch tracking',
                       'material correspondence', 'independent Phi coupling'], full_core_unlock=False, claim_promotion=False,
        dependency_unlocked=['multi-branch response design only'],
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        claim_boundary='No detector inversion, rates, temperatures or physical alpha. No holdout input; no negative mode clipped.')
    if max(r['reference_relative_error'] for r in rows) > 1e-12:
        raise ValueError('reference disagreement')
    (ROOT/'docs/core/07_artifacts/topic13/t13_finiteq_scattering_geometry_audit.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps([dict(q=r['q_fractional'], columns=len(r['resolved_geometry_columns']), rank=r['numerical_rank'],
                           singular=r['normalized_singular_values'], error=r['reference_relative_error']) for r in rows], indent=2))


if __name__ == '__main__':
    main()
