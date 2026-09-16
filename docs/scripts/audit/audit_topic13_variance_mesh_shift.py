"""Fixed shifted-grid comparison, not an uncertainty estimate or UET mapping."""
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

MESHES = (8, 12, 16)
SHIFTS = ((.5, .5, .5), (.25, .25, .25), (.75, .75, .75), (.5, .5, .25), (.25, .25, .5))


def shifted_grid(n, shift):
    shift = np.asarray(shift, dtype=float)
    if not isinstance(n, int) or n < 2 or shift.shape != (3,) or not np.isfinite(shift).all() or np.any(shift <= 0) or np.any(shift >= 1):
        raise ValueError('mesh integer >=2 and three open-unit shifts required')
    axes = [(np.arange(n)+s)/n-.5 for s in shift]
    return np.array(np.meshgrid(*axes, indexing='ij')).reshape(3, -1).T


def main():
    for path, expected in LOCKS.items():
        if sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('source hash mismatch')
    meta = load_phonopy()
    model = phonopy.load(str(PHONOPY_PATH), produce_fc=False, symmetrize_fc=False, is_nac=False, lang='C')
    model.force_constants = load_force_constants()[0]
    points = meta['primitive_cell']['points']
    positions = np.array([p['coordinates'] for p in points])
    masses_amu = np.array([p['mass'] for p in points])
    np.testing.assert_allclose(model.primitive.scaled_positions, positions, atol=1e-12, rtol=0)
    np.testing.assert_allclose(model.primitive.masses, masses_amu, atol=1e-10, rtol=0)
    np.testing.assert_allclose(positions[:, 2], [.25, .75, .25, .75], atol=1e-12, rtol=0)
    basis, mu = shear_basis(masses_amu*physical_constants['atomic mass constant'][0], [0, 1, 0, 1], [0, 0, 1], [1, 0, 0])
    factor = float(meta['phonopy']['frequency_unit_conversion_factor'])*2*np.pi*1e12
    rows = []
    for n in MESHES:
        for shift in SHIFTS:
            qs = shifted_grid(n, shift)
            result = model.run_qpoints(qs, with_dynamical_matrices=True)
            bins = np.zeros(6)
            unstable = []
            for q, matrix in zip(qs, result.dynamical_matrices):
                values, vectors = np.linalg.eigh(matrix)
                if np.any(values <= 0):
                    unstable.append(dict(q=q.tolist(), minimum_eigenvalue=float(values.min())))
                    continue
                overlap = basis.conj().T@(cell_phase(q, positions)[:, None]*vectors)
                bins += partition_trace(overlap, np.sqrt(values)*factor, 300., mu)/len(qs)
            row = dict(mesh=n, shift=list(shift), unstable_points=unstable,
                status='BLOCKED_UNSTABLE_SOURCE' if unstable else 'COMPUTED_NOT_CONVERGED',
                trace_bins_m2=None if unstable else bins.tolist(),
                total_trace_m2=None if unstable else float(bins.sum()),
                rms_angstrom=None if unstable else float(np.sqrt(bins.sum())*1e10))
            rows.append(row)
            print(json.dumps(row), flush=True)
    summaries = []
    for n in MESHES:
        group = [r for r in rows if r['mesh'] == n]
        if any(r['unstable_points'] for r in group):
            summaries.append(dict(mesh=n, status='BLOCKED_UNSTABLE_SOURCE'))
            continue
        traces = np.array([r['total_trace_m2'] for r in group])
        summaries.append(dict(mesh=n, range_over_midpoint_trace=float(np.ptp(traces)/((traces.max()+traces.min())/2)),
            inversion_pair_relative_difference=float(abs(traces[1]/traces[2]-1)),
            min_rms_angstrom=min(r['rms_angstrom'] for r in group), max_rms_angstrom=max(r['rms_angstrom'] for r in group)))
    paths = list(LOCKS)+[Path(__file__), ROOT/'docs/core/test/test_topic13_variance_mesh_shift.py',
        ROOT/'docs/scripts/audit/audit_topic13_thermal_variance_spectrum.py',
        ROOT/'docs/scripts/audit/audit_topic13_interlayer_thermal_variance.py',
        ROOT/'docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py', ROOT/'docs/core/03_lanes/thermal/uet_interlayer_mode_residue.py']
    artifact = dict(major_result_id='T13_VARIANCE_SHIFT_SENSITIVITY', topic='0.13', closure_level='PARTIAL',
        what_is_closed='Fixed grid-shift sensitivity measurement at300K, not convergence',
        equation_or_mapping='Equal-weight BZ quadrature of the existing source-model local covariance trace',
        units='trace m^2; RMS angstrom', derivation_class='harmonic source-model quadrature diagnostic',
        observable='local relative-layer mass-centroid covariance', data_role='SOURCE_MODEL_NOT_EXPERIMENT',
        temperature_K=300, rows=rows, mesh_summaries=summaries, phonopy_version=phonopy.__version__,
        frequency_edges_cm_inverse=[0,10,30,100,300,1000,'infinity'],
        verification_status='SHIFT_SEQUENCE_RECORDED', controlling_blocker='quadrature_convergence_and_material_observable_mapping',
        open_blockers=['no_continuum_error_bound', 'phase_and_mode_mapping', 'anharmonicity'],
        dependency_unlocked=[], full_core_unlock=False, global_claim_promotion=False,
        claim_boundary='Shift range is not a statistical uncertainty. No clipping, fitting, threshold changes or UET identification.',
        evidence_artifacts=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha256(p.read_bytes()).hexdigest()) for p in paths])
    (ROOT/'docs/core/07_artifacts/topic13/t13_variance_mesh_shift.json').write_text(json.dumps(artifact, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
