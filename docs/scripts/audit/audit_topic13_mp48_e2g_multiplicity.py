"""Distinguish same-irrep source eigenspaces; no detector inversion or Phi map."""
import hashlib
import json
from pathlib import Path

import numpy as np
import phonopy
import spglib

from docs.core.uet_interlayer_mode_residue import shear_basis
from docs.scripts.audit.audit_topic13_mp48_shear_irrep import gamma_action, expected_e2g_character
from docs.scripts.audit.audit_topic13_mp48_interlayer_mode_residue import LOCKS
from docs.scripts.audit.audit_topic13_mp48_force_constant_harmonic_reconstruction import PHONOPY_PATH, load_force_constants, load_phonopy

ROOT = Path(__file__).resolve().parents[3]


def frequency_groups(frequencies, tolerance=1e-6):
    frequencies = np.asarray(frequencies)
    if frequencies.ndim != 1 or not np.isfinite(frequencies).all() or tolerance <= 0:
        raise ValueError('finite frequency vector and positive tolerance required')
    groups = []
    for index in np.argsort(frequencies):
        if not groups or abs(frequencies[index]-frequencies[groups[-1][0]]) > tolerance:
            groups.append([])
        groups[-1].append(int(index))
    return groups


def representation_errors(pair, actions, characters):
    if len(actions) != len(characters) or not actions:
        raise ValueError('matched nonempty symmetry list required')
    residuals, errors = [], []
    for action, expected in zip(actions, characters):
        representation = pair.conj().T @ action @ pair
        residuals.append(float(np.linalg.norm(action @ pair-pair @ representation)))
        errors.append(float(abs(np.trace(representation)-expected)))
    return max(residuals), max(errors)


def main():
    for path, expected in LOCKS.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('changed source')
    model = phonopy.load(str(PHONOPY_PATH), produce_fc=False, symmetrize_fc=False, is_nac=False, lang='C')
    model.force_constants = load_force_constants()[0]
    matrix = model.run_qpoints([[0, 0, 0]], with_dynamical_matrices=True).dynamical_matrices[0]
    values, vectors = np.linalg.eigh(matrix)
    factor = float(load_phonopy()['phonopy']['frequency_unit_conversion_factor'])
    frequencies = np.sign(values)*np.sqrt(abs(values))*factor
    cell = model.primitive
    np.testing.assert_allclose(cell.scaled_positions[:, 2], [.25, .75, .25, .75], atol=1e-12)
    basis, _ = shear_basis(cell.masses, [0, 1, 0, 1], [0, 0, 1], [1, 0, 0])
    symmetry = spglib.get_symmetry((cell.cell, cell.scaled_positions, cell.numbers), symprec=1e-6)
    actions, characters = [], []
    for r, t in zip(symmetry['rotations'], symmetry['translations']):
        action, cart, _, _ = gamma_action(cell.cell, cell.scaled_positions, cell.masses, r, t)
        actions.append(action)
        characters.append(expected_e2g_character(cart))
    rows = []
    for indices in frequency_groups(frequencies):
        pair = vectors[:, indices]
        leakage, error = representation_errors(pair, actions, characters)
        rows.append(dict(indices=indices, frequencies_cm_inverse=(frequencies[indices]*1e12/299792458/100).tolist(),
                         dimension=len(indices), e2g=len(indices) == 2 and leakage < 1e-8 and error < 1e-8,
                         subspace_leakage=leakage, e2g_character_error=error,
                         rigid_shear_weight=float(np.linalg.norm(basis.conj().T @ pair)**2/len(indices))))
    pairs = [r for r in rows if r['e2g']]
    checks = dict(two_separate_e2g_pairs=len(pairs) == 2,
                  grouping_stable=frequency_groups(frequencies, 1e-7) == frequency_groups(frequencies, 1e-5),
                  all_modes_accounted=sum(r['dimension'] for r in rows) == 12,
                  force_symmetry=bool(max(np.linalg.norm(a @ matrix-matrix @ a)/np.linalg.norm(matrix) for a in actions) < 1e-8))
    evidence = list(LOCKS)+[Path(__file__), ROOT/'docs/core/test/test_topic13_mp48_e2g_multiplicity.py',
        ROOT/'docs/core/uet_interlayer_mode_residue.py', ROOT/'docs/scripts/audit/audit_topic13_mp48_shear_irrep.py',
        ROOT/'docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py']
    artifact = dict(major_result_id='T13_MP48_SAME_IRREP_DISTINCT_BRANCHES', topic='0.13',
                    closure_level='CLOSED_FOR_LANE' if all(checks.values()) else 'PARTIAL',
                    what_is_closed=['Source Gamma E2g multiplicity and separate rigid-shear projections'] if all(checks.values()) else [],
                    equation_or_mapping='Project each distinct source eigenspace onto crystal characters and existing rigid-shear basis',
                    units={'frequency': 'cm^-1', 'weights': '1'}, derivation_class='source_harmonic_representation_diagnostic',
                    observable='source mode symmetry and shape, not measured populations', data_role='SOURCE_MODEL_DIAGNOSTIC',
                    verification_status='SAME_IRREP_NOT_SAME_MODE' if all(checks.values()) else 'UNRESOLVED',
                    checks=checks, eigenspaces=rows, grouping_tolerance_THz=1e-6,
                    signed_frequencies_THz=frequencies.tolist(),
                    grouping_sweep={str(t): frequency_groups(frequencies, t) for t in (1e-7, 1e-6, 1e-5)},
                    negative_frequencies_preserved=True, full_core_unlock=False, claim_promotion=False,
                    open_blockers=['experimental branch weights and detector inversion', 'material/source frequency correspondence', 'independent Phi coupling'],
                    dependency_unlocked=['branch-aware source selection only'],
                    evidence_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in evidence},
                    claim_boundary='Source Gamma identification only; does not prove which mode dominates UED, equate Phi to a phonon, or transfer fitted EELS temperatures.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_mp48_e2g_multiplicity_audit.json').write_text(json.dumps(artifact, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(checks=checks, e2g_pairs=pairs), indent=2))
    if not all(checks.values()):
        raise RuntimeError('source multiplicity unresolved')


if __name__ == '__main__':
    main()
