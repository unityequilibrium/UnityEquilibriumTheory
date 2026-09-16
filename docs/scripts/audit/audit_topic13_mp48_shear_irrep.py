"""Gamma-only crystal representation test on unchanged MP48 force constants."""

import hashlib
import json
from pathlib import Path

import numpy as np
import phonopy
import spglib

from docs.core.uet_interlayer_mode_residue import shear_basis, pair_character
from docs.scripts.audit.audit_topic13_mp48_force_constant_harmonic_reconstruction import (
    PHONOPY_PATH, load_force_constants,
)
from docs.scripts.audit.audit_topic13_mp48_interlayer_mode_residue import LOCKS

ROOT = Path(__file__).resolve().parents[3]


def gamma_action(lattice, positions, masses, rotation, translation, tolerance=1e-8):
    """Active atom permutation and Cartesian vector action; Bloch phase is 1 at Gamma."""
    a, positions, masses = map(np.asarray, (lattice, positions, masses))
    cart = a.T @ rotation @ np.linalg.inv(a.T)
    if not np.allclose(cart.T @ cart, np.eye(3), atol=tolerance, rtol=0):
        raise ValueError('not a Cartesian isometry')
    action = np.zeros((3*len(positions), 3*len(positions)))
    perm, errors = [], []
    for i, position in enumerate(positions):
        delta = positions-(rotation @ position+translation)
        delta -= np.rint(delta)
        distances = np.linalg.norm(delta @ a, axis=1)
        matches = np.flatnonzero(distances < tolerance)
        if len(matches) != 1:
            raise ValueError('unique symmetry-related atom missing')
        j = int(matches[0])
        if not np.isclose(masses[i], masses[j], atol=0, rtol=1e-12):
            raise ValueError('symmetry does not preserve atomic mass')
        perm.append(j)
        errors.append(float(distances[j]))
        action[3*j:3*j+3, 3*i:3*i+3] = cart
    if len(set(perm)) != len(perm):
        raise ValueError('not an atom permutation')
    return action, cart, perm, max(errors)


def expected_e2g_character(cart):
    # Inversion is even. The remaining proper D6 element is axial or basal C2.
    proper = np.linalg.det(cart)*cart
    if np.isclose(proper[2, 2], -1, atol=1e-10):
        return 0.
    if not np.allclose(proper[:, 2], [0, 0, 1], atol=1e-10):
        raise ValueError('operation outside declared D6h orientation')
    angle = np.arctan2(proper[1, 0], proper[0, 0])
    return float(2*np.cos(2*angle))


def main():
    for path, expected in LOCKS.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('changed source hash')
    model = phonopy.load(str(PHONOPY_PATH), produce_fc=False,
                         symmetrize_fc=False, is_nac=False, lang='C')
    model.force_constants = load_force_constants()[0]
    matrix = model.run_qpoints([[0, 0, 0]], with_dynamical_matrices=True).dynamical_matrices[0]
    _, vectors = np.linalg.eigh(matrix)
    cell = model.primitive
    basis, _ = shear_basis(cell.masses, [0, 1, 0, 1], [0, 0, 1], [1, 0, 0])
    pair = pair_character(vectors, basis)['pair_vectors']
    crystal = (cell.cell, cell.scaled_positions, cell.numbers)
    symmetry = spglib.get_symmetry(crystal, symprec=1e-6)
    dataset = spglib.get_symmetry_dataset(crystal, symprec=1e-6)
    rows = []
    for r, t in zip(symmetry['rotations'], symmetry['translations']):
        u, cart, perm, err = gamma_action(cell.cell, cell.scaled_positions, cell.masses, r, t)
        rep = pair.conj().T @ u @ pair
        expected = expected_e2g_character(cart)
        rows.append(dict(fractional_rotation=r.tolist(), fractional_translation=t.tolist(),
                         atom_permutation=perm, atom_mapping_error_angstrom=err,
                         character_real=float(np.trace(rep).real),
                         character_imag=float(np.trace(rep).imag), expected_character=expected,
                         character_error=float(abs(np.trace(rep)-expected)),
                         subspace_leakage=float(np.linalg.norm(u @ pair-pair @ rep)),
                         force_commutator_relative=float(np.linalg.norm(u @ matrix-matrix @ u)/np.linalg.norm(matrix))))
    checks = dict(space_group=int(dataset.number) == 194, operation_count=len(rows) == 24,
                  character_match=max(r['character_error'] for r in rows) < 1e-8,
                  invariant_subspace=max(r['subspace_leakage'] for r in rows) < 1e-8,
                  force_symmetry=max(r['force_commutator_relative'] for r in rows) < 1e-8)
    files = list(LOCKS)+[Path(__file__), ROOT/'docs/core/03_lanes/thermal/uet_interlayer_mode_residue.py',
        ROOT/'docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py',
        ROOT/'docs/scripts/audit/audit_topic13_mp48_interlayer_mode_residue.py']
    result = dict(major_result_id='T13_MP48_GAMMA_E2G_SOURCE_IDENTIFICATION', topic='0.13',
                  closure_level='CLOSED_FOR_LANE' if all(checks.values()) else 'PARTIAL',
                  what_is_closed=['Gamma source doublet tested against all declared D6h characters'] if all(checks.values()) else [],
                  equation_or_mapping='U_g: atom permutation times Cartesian rotation; D_pair=E^dagger*U_g*E',
                  units={'representation': '1', 'atom_mapping_error': 'angstrom'},
                  derivation_class='source_structure_representation_test',
                  observable='material Gamma phonon irrep', data_role='SOURCE_HARMONIC_DIAGNOSTIC',
                  verification_status='PASS_SOURCE_E2G' if all(checks.values()) else 'UNRESOLVED',
                  checks=checks, operations=rows, space_group=int(dataset.number),
                  spglib_version=spglib.__version__, phonopy_version=phonopy.__version__,
                  open_blockers=['Phi representation and coupling', 'same-state strained data', 'thermal occupation/bath map'],
                  dependency_unlocked=['conditional E2g selection rule applies to source Gamma doublet only'],
                  full_core_unlock=False, claim_promotion=False,
                  evidence_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                  claim_boundary='Not finite-q irrep, Raman frequency agreement, full internal O(2) equivalence or Phi normalization.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_mp48_shear_irrep_audit.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(checks=checks, maximum_subspace_leakage=max(r['subspace_leakage'] for r in rows),
                         maximum_character_error=max(r['character_error'] for r in rows)), indent=2))
    if not all(checks.values()):
        raise RuntimeError('source irrep unresolved')


if __name__ == '__main__':
    main()
