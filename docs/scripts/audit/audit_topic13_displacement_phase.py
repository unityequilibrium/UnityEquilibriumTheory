"""Independent cell-gauge force matrix and explicit atomic centroid readout."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
from scipy.constants import physical_constants
import phonopy

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from docs.scripts.audit.audit_topic13_mp48_force_constant_harmonic_reconstruction import (
    PHONOPY_PATH, load_phonopy, load_force_constants, build_mapping, representatives, dynamical_matrix)
from docs.scripts.audit.audit_topic13_mp48_interlayer_mode_residue import LOCKS
from docs.scripts.audit.audit_topic13_interlayer_thermal_variance import modal_covariance
from docs.core.uet_interlayer_mode_residue import shear_basis, cell_phase

QS = ((.2,0,0), (.2,.2,.5), (.4,.2,.5), (.4,.4,0))


def centroid_readout(vectors, q, positions, masses, layers):
    """Explicit mass-centroid difference, independent of the shear_basis helper."""
    vectors = np.asarray(vectors).reshape(len(masses),3,-1)
    amplitudes = vectors*np.exp(2j*np.pi*(positions@q))[:,None,None]/np.sqrt(masses)[:,None,None]
    centroids = []
    for label in (0,1):
        selected = np.asarray(layers) == label
        centroids.append(np.sum(masses[selected,None,None]*amplitudes[selected], axis=0)/sum(masses[selected]))
    return (centroids[0]-centroids[1])[:2]


def main():
    for path, expected in LOCKS.items():
        if sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('source hash mismatch')
    meta = load_phonopy()
    fc = load_force_constants()[0]
    mapping,_ = build_mapping(meta)
    reps = representatives(mapping)
    positions = np.array([p['coordinates'] for p in meta['primitive_cell']['points']])
    amu = np.array([p['mass'] for p in meta['primitive_cell']['points']])
    masses = amu*physical_constants['atomic mass constant'][0]
    layers = np.array([0,1,0,1])
    model = phonopy.load(str(PHONOPY_PATH), produce_fc=False, symmetrize_fc=False, is_nac=False, lang='C')
    model.force_constants = fc
    np.testing.assert_allclose(model.primitive.scaled_positions, positions, atol=1e-12, rtol=0)
    np.testing.assert_allclose(model.primitive.masses, amu, atol=1e-10, rtol=0)
    basis,mu = shear_basis(masses,layers,[0,0,1],[1,0,0])
    factor = float(meta['phonopy']['frequency_unit_conversion_factor'])*2*np.pi*1e12
    matrices = model.run_qpoints(QS, with_dynamical_matrices=True).dynamical_matrices
    rows = []
    for q,dp in zip(QS,matrices):
        phase = cell_phase(q,positions)
        dc = dynamical_matrix(q,fc,mapping,reps,amu)
        transformed = phase[:,None]*dp*phase.conj()[None,:]
        residual = float(np.linalg.norm(dc-transformed)/np.linalg.norm(dc))
        np.testing.assert_allclose(dc,transformed,atol=1e-10,rtol=1e-10)
        values,vectors = np.linalg.eigh(dp)
        if np.any(values <= 0):
            raise ValueError('unstable source mode: no covariance emitted')
        explicit = centroid_readout(vectors,np.asarray(q),positions,masses,layers)
        overlap = basis.conj().T@(phase[:,None]*vectors)
        readout_residual = float(np.linalg.norm(explicit-overlap/np.sqrt(mu))/np.linalg.norm(explicit))
        np.testing.assert_allclose(explicit,overlap/np.sqrt(mu),atol=1e-3,rtol=1e-12)
        cov = modal_covariance(overlap,np.sqrt(values)*factor,300.,mu)
        wrong = modal_covariance(basis.conj().T@vectors,np.sqrt(values)*factor,300.,mu)
        rows.append(dict(q=list(q), cell_gauge_matrix_relative_error=residual,
            explicit_readout_relative_error=readout_residual,
            omitted_phase_relative_covariance_difference=float(np.linalg.norm(wrong-cov)/np.linalg.norm(cov))))
    paths = list(LOCKS)+[Path(__file__), ROOT/'docs/core/test/test_topic13_displacement_phase.py',
        ROOT/'docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py',
        ROOT/'docs/scripts/audit/audit_topic13_interlayer_thermal_variance.py',ROOT/'docs/core/uet_interlayer_mode_residue.py']
    artifact = dict(major_result_id='T13_LOCAL_DISPLACEMENT_PHASE_CONVENTION',topic='0.13',closure_level='CLOSED_FOR_LANE',
        what_is_closed='Cell-gauge phase and explicit local mass-centroid readout identity; commensurate source-matrix cross-check',
        equation_or_mapping='P=diag(exp(i*q*r_j)); D_cell=P D_phonopy P^dagger; s=B^dagger P e/sqrt(mu)',
        units='s mode coefficient kg^-1/2; covariance m^2',derivation_class='algebraic gauge/readout identity with source-model checks',
        observable='same-cell local layer-centroid difference, not uniform slip',data_role='SOURCE_MODEL_NOT_EXPERIMENT',
        verification_status='IDENTITY_AND_COMMENSURATE_CHECKS_PASS',rows=rows,
        primary_source='https://phonopy.github.io/phonopy/formulation.html#dynamical-matrix',
        controlling_blocker='continuum_covariance_and_material_to_UET_mapping',
        open_blockers=['off_commensurate_interpolation_not_independently_checked','continuum_convergence','coherent_mode_and_UET_mapping','anharmonicity'],
        dependency_unlocked=[],full_core_unlock=False,global_claim_promotion=False,
        claim_boundary='Only declared same-cell harmonic readout closes. No whole-layer average, local-slip equivalence, alpha or full-topic closure.',
        evidence_artifacts=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha256(p.read_bytes()).hexdigest()) for p in paths])
    (ROOT/'docs/core/07_artifacts/topic13/t13_displacement_phase.json').write_text(json.dumps(artifact,indent=2,allow_nan=False)+'\n')
    print(json.dumps(rows),flush=True)


if __name__ == '__main__':
    main()
