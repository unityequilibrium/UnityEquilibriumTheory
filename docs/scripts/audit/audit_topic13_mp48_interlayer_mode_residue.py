"""Source-locked harmonic diagnostic; no calibration or physical unlock."""

import hashlib
import json
from pathlib import Path

import numpy as np
import phonopy
from scipy.constants import physical_constants

from docs.core.uet_interlayer_mode_residue import (
    cell_phase, pair_character, projected_resolvent, shear_basis,
)
from docs.scripts.audit.audit_topic13_mp48_force_constant_harmonic_reconstruction import (
    PHONOPY_PATH, FORCE_CONSTANTS_PATH, load_phonopy, load_force_constants,
    build_mapping, representatives, dynamical_matrix,
)

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'docs/core/07_artifacts/topic13/t13_mp48_interlayer_mode_residue_audit.json'
LOCKS = {
    FORCE_CONSTANTS_PATH: 'a410f36fd34e8603aec0dde48c1f8cb47fbf0a237ca911437f744fb7cbf02763',
    PHONOPY_PATH: '00be787d0fbe986304ffdfa51a917b9aa0038deb6d31a563979afe42a7a2b5f8',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for path, expected in LOCKS.items():
        if digest(path) != expected:
            raise ValueError('source hash mismatch: '+str(path))
    meta = load_phonopy()
    fc = load_force_constants()[0]
    model = phonopy.load(str(PHONOPY_PATH), produce_fc=False,
                         symmetrize_fc=False, is_nac=False, lang='C')
    model.force_constants = fc
    points = meta['primitive_cell']['points']
    positions = np.array([row['coordinates'] for row in points])
    masses = np.array([row['mass'] for row in points])
    np.testing.assert_allclose(model.primitive.scaled_positions, positions, atol=1e-12)
    np.testing.assert_allclose(model.primitive.masses, masses, atol=1e-12)
    np.testing.assert_allclose(positions[:, 2], [.25, .75, .25, .75], atol=1e-12)
    atomic_mass, _, atomic_mass_error = physical_constants['atomic mass constant']
    basis, mu = shear_basis(masses*atomic_mass, [0, 1, 0, 1], [0, 0, 1], [1, 0, 0])
    factor = float(meta['phonopy']['frequency_unit_conversion_factor'])
    qpoints = [[0., 0., 0.]]
    for axis in (0, 2):
        for length in (.005, .01, .02):
            for sign in (-1, 1):
                q = [0., 0., 0.]
                q[axis] = sign*length
                qpoints.append(q)
    result = model.run_qpoints(qpoints, with_eigenvectors=True, with_dynamical_matrices=True)
    rows, spectra = [], []
    for q, matrix in zip(qpoints, result.dynamical_matrices):
        values, vectors = np.linalg.eigh(matrix)
        frequencies = np.sign(values)*np.sqrt(abs(values))*factor
        character = pair_character(vectors, basis, cell_phase(q, positions))
        pair = character['indices']
        other = np.setdiff1d(np.arange(len(values)), pair)
        separation = float(np.min(abs(frequencies[pair, None]-frequencies[other])))
        residual = float(np.linalg.norm(matrix @ vectors-vectors*values)/np.linalg.norm(matrix))
        rows.append(dict(q_fractional=q, selected_indices=pair.tolist(),
                         frequencies_cm_inverse=(frequencies[pair]*1e12/299792458/100).tolist(),
                         principal_weights=character['principal_weights'].tolist(),
                         isolation_THz=separation, eigenpair_relative_residual=residual))
        spectra.append(frequencies)
    gamma = result.dynamical_matrices[0]
    mapping, mapping_error = build_mapping(meta)
    independent = dynamical_matrix((0, 0, 0), fc, mapping, representatives(mapping), masses)
    gamma_error = float(np.linalg.norm(gamma-independent)/np.linalg.norm(gamma))
    omega2 = gamma*(2*np.pi*1e12*factor)**2
    values, vectors = np.linalg.eigh(omega2)
    overlaps = basis.T @ vectors
    errors = []
    for s in (1e12+2e12j, 3e12+1e12j):
        direct = projected_resolvent(omega2, basis, mu, s)
        spectral = (overlaps/(values+s*s)) @ overlaps.conj().T/mu
        errors.append(float(np.linalg.norm(direct-spectral)/np.linalg.norm(direct)))
    character = pair_character(vectors, basis)
    residue = character['weight_matrix']/mu
    parity_error = max(float(np.max(abs(spectra[i]-spectra[i+1]))) for i in range(1, 13, 2))
    checks = {
        'source_hashes': True,
        'independent_gamma': gamma_error <= 1e-10,
        'mapping': mapping_error <= 1e-10,
        'spectral_resolvent': max(errors) <= 1e-10,
        'q_parity': parity_error <= 1e-8,
        'eigenpairs': max(r['eigenpair_relative_residual'] for r in rows) <= 1e-12,
        'predeclared_pair_weight': min(min(r['principal_weights']) for r in rows) >= .98,
        'predeclared_isolation': min(r['isolation_THz'] for r in rows) >= 1e-5,
    }
    evidence = list(LOCKS)+[Path(__file__), ROOT/'docs/core/uet_interlayer_mode_residue.py',
        ROOT/'docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py']
    artifact = dict(
        major_result_id='T13_MP48_INTERLAYER_MODE_SHAPE_AND_MATERIAL_RESIDUE',
        topic='0.13', closure_level='PARTIAL', verification_status='PASS' if all(checks.values()) else 'UNRESOLVED',
        what_is_closed=['Mass-centroid kinematic formula and full spectral response identity within source harmonic model.'],
        equation_or_mapping='mu=M_A*M_B/(M_A+M_B); Z_pair=B^dagger*P_pair*B/mu',
        units={'mu': 'kg', 'Z_pair': 'kg^-1', 'susceptibility': 's^2/kg'},
        derivation_class='derived_relation', observable='material relative-layer displacement per generalized force',
        data_role='SOURCE_HARMONIC_COMPARISON_NOT_CALIBRATION',
        checks=checks, q_path_results=rows, reduced_mass_kg=mu,
        gamma_residue_kg_inverse_real=residue.real.tolist(),
        gamma_residue_kg_inverse_imag=residue.imag.tolist(),
        signed_gamma_frequencies_THz=spectra[0].tolist(),
        gamma_assembly_relative_error=gamma_error, resolvent_relative_errors=errors,
        parity_max_error_THz=parity_error,
        source_frequency_factor=factor, runtime_frequency_factor=model.unit_conversion_factor,
        phonopy_version=phonopy.__version__, atomic_mass_constant_kg=atomic_mass,
        atomic_mass_constant_uncertainty_kg=atomic_mass_error,
        primitive_lattice_angstrom=model.primitive.cell.tolist(),
        uncertainty_status='No force-constant model-error or sample-isotope uncertainty closure.',
        open_blockers=['Raman/source-state equivalence', 'independent strain response', 'UET mode and Phi normalization'],
        dependency_unlocked=[], full_core_unlock=False, claim_promotion=False,
        holdout_access='No TTG or holdout file inputs; source readers consume force constants and structure only.',
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in evidence},
        claim_boundary='Short-path material diagnostic only; no Phi identification, heat transport, causal proof or full Topic 13 closure.',
    )
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps(dict(checks=checks, reduced_mass_kg=mu, gamma=rows[0],
                          min_weight=min(min(r['principal_weights']) for r in rows)), indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
