"""Directional resolution of the existing harmonic local displacement observable."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
from scipy.constants import physical_constants
import phonopy

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from docs.scripts.audit.audit_topic13_thermal_variance_spectrum import partition_trace
from docs.scripts.audit.audit_topic13_mp48_force_constant_harmonic_reconstruction import PHONOPY_PATH, load_phonopy, load_force_constants
from docs.scripts.audit.audit_topic13_mp48_interlayer_mode_residue import LOCKS
from docs.core.uet_interlayer_mode_residue import shear_basis, cell_phase

GRIDS = ((8,8,8), (16,16,8), (32,32,8), (48,48,8), (16,16,16), (16,16,32))


def directional_grid(shape):
    shape = np.asarray(shape)
    if shape.shape != (3,) or not np.issubdtype(shape.dtype, np.integer) or np.any(shape < 2):
        raise ValueError('three integer mesh sizes >=2 required')
    return np.array(np.meshgrid(*[(np.arange(n)+.5)/n-.5 for n in shape], indexing='ij')).reshape(3,-1).T


def main():
    for path, expected in LOCKS.items():
        if sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('source hash mismatch')
    meta = load_phonopy()
    model = phonopy.load(str(PHONOPY_PATH), produce_fc=False, symmetrize_fc=False, is_nac=False, lang='C')
    model.force_constants = load_force_constants()[0]
    points = meta['primitive_cell']['points']
    positions = np.array([p['coordinates'] for p in points])
    amu = np.array([p['mass'] for p in points])
    np.testing.assert_allclose(model.primitive.scaled_positions, positions, atol=1e-12, rtol=0)
    np.testing.assert_allclose(model.primitive.masses, amu, atol=1e-10, rtol=0)
    np.testing.assert_allclose(positions[:,2], [.25,.75,.25,.75], atol=1e-12, rtol=0)
    basis, mu = shear_basis(amu*physical_constants['atomic mass constant'][0], [0,1,0,1], [0,0,1], [1,0,0])
    factor = float(meta['phonopy']['frequency_unit_conversion_factor'])*2*np.pi*1e12
    rows = []
    for shape in GRIDS:
        qs = directional_grid(shape)
        result = model.run_qpoints(qs, with_dynamical_matrices=True)
        bins = np.zeros(6)
        unstable = []
        for q, matrix in zip(qs, result.dynamical_matrices):
            values, vectors = np.linalg.eigh(matrix)
            if np.any(values <= 0):
                unstable.append(dict(q=q.tolist(), minimum_eigenvalue=float(values.min())))
                continue
            overlap = basis.conj().T@(cell_phase(q, positions)[:,None]*vectors)
            bins += partition_trace(overlap, np.sqrt(values)*factor, 300., mu)/len(qs)
        row = dict(shape=list(shape), q_count=len(qs), unstable_points=unstable,
            status='BLOCKED_UNSTABLE_SOURCE' if unstable else 'COMPUTED_NOT_CONVERGED',
            trace_bins_m2=None if unstable else bins.tolist(), total_trace_m2=None if unstable else float(bins.sum()),
            rms_angstrom=None if unstable else float(np.sqrt(bins.sum())*1e10))
        rows.append(row)
        print(json.dumps(row), flush=True)
    comparisons = []
    for a,b in ((0,1),(1,2),(2,3),(1,4),(4,5)):
        if rows[a]['total_trace_m2'] is not None and rows[b]['total_trace_m2'] is not None:
            comparisons.append(dict(from_shape=rows[a]['shape'], to_shape=rows[b]['shape'],
                relative_trace_change=rows[b]['total_trace_m2']/rows[a]['total_trace_m2']-1))
    paths = list(LOCKS)+[Path(__file__), ROOT/'docs/core/test/test_topic13_variance_directional_grid.py',
        ROOT/'docs/scripts/audit/audit_topic13_thermal_variance_spectrum.py', ROOT/'docs/scripts/audit/audit_topic13_interlayer_thermal_variance.py',
        ROOT/'docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py', ROOT/'docs/core/03_lanes/thermal/uet_interlayer_mode_residue.py']
    artifact = dict(major_result_id='T13_VARIANCE_DIRECTIONAL_RESOLUTION', topic='0.13', closure_level='PARTIAL',
        what_is_closed='Directional refinement comparison of source harmonic covariance at300K',
        equation_or_mapping='Existing all-mode covariance trace integrated with separate reciprocal-axis mesh sizes',
        units='trace m^2; RMS angstrom', derivation_class='harmonic source-model quadrature diagnostic',
        observable='local relative-layer mass-centroid covariance', data_role='SOURCE_MODEL_NOT_EXPERIMENT',
        temperature_K=300, rows=rows, comparisons=comparisons, phonopy_version=phonopy.__version__,
        frequency_edges_cm_inverse=[0,10,30,100,300,1000,'infinity'],
        verification_status='DIRECTIONAL_SEQUENCE_RECORDED', controlling_blocker='directional_convergence_and_independent_phase_mapping',
        open_blockers=['no_continuum_error_bound', 'physical_mode_mapping', 'anharmonicity'],
        dependency_unlocked=[], full_core_unlock=False, global_claim_promotion=False,
        claim_boundary='No dimensional reduction, continuum convergence or physical calibration follows from weak mesh dependence along one direction.',
        evidence_artifacts=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha256(p.read_bytes()).hexdigest()) for p in paths])
    (ROOT/'docs/core/07_artifacts/topic13/t13_variance_directional_grid.json').write_text(json.dumps(artifact, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
