"""Frequency attribution of local variance; bins are diagnostics, not branches."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
from scipy.constants import c, physical_constants
import phonopy

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from docs.scripts.audit.audit_topic13_interlayer_thermal_variance import oscillator_variance
from docs.scripts.audit.audit_topic13_mp48_force_constant_harmonic_reconstruction import PHONOPY_PATH, load_phonopy, load_force_constants
from docs.scripts.audit.audit_topic13_mp48_interlayer_mode_residue import LOCKS
from docs.core.uet_interlayer_mode_residue import shear_basis, cell_phase

EDGES = np.array([0., 10., 30., 100., 300., 1000., np.inf])
TEMPERATURES = (0., 100., 200., 300.)


def partition_trace(overlap, omega, temperature, mass):
    overlap = np.asarray(overlap, dtype=complex)
    omega = np.asarray(omega, dtype=float)
    if overlap.ndim != 2 or overlap.shape[1] != omega.size or not np.isfinite(overlap).all():
        raise ValueError('finite overlap and matching frequencies required')
    if not np.isfinite(mass) or mass <= 0:
        raise ValueError('positive mass required')
    weights = np.sum(abs(overlap)**2, axis=0)*oscillator_variance(omega, temperature)/mass
    bins = np.searchsorted(EDGES, omega/(2*np.pi*c*100), side='right')-1
    return np.bincount(bins, weights=weights, minlength=len(EDGES)-1)


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
    np.testing.assert_allclose(positions[:, 2], [.25, .75, .25, .75], atol=1e-12, rtol=0)
    basis, mu = shear_basis(amu*physical_constants['atomic mass constant'][0], [0, 1, 0, 1], [0, 0, 1], [1, 0, 0])
    factor = float(meta['phonopy']['frequency_unit_conversion_factor'])*2*np.pi*1e12
    reference_path = ROOT/'docs/core/07_artifacts/topic13/t13_interlayer_thermal_variance_audit.json'
    reference = json.loads(reference_path.read_text())
    for evidence in reference['evidence_artifacts']:
        if sha256((ROOT/evidence['path']).read_bytes()).hexdigest() != evidence['sha256']:
            raise ValueError('reference evidence drift')
    rows = []
    for n in (8, 12):
        axis = (np.arange(n)+.5)/n-.5
        qs = np.array(np.meshgrid(axis, axis, axis, indexing='ij')).reshape(3, -1).T
        result = model.run_qpoints(qs, with_dynamical_matrices=True)
        sums = {T: np.zeros(len(EDGES)-1) for T in TEMPERATURES}
        for q, matrix in zip(qs, result.dynamical_matrices):
            values, vectors = np.linalg.eigh(matrix)
            if np.any(values <= 0):
                raise ValueError('unstable source: no partial spectrum is emitted')
            overlap = basis.conj().T@(cell_phase(q, positions)[:, None]*vectors)
            for T in TEMPERATURES:
                sums[T] += partition_trace(overlap, np.sqrt(values)*factor, T, mu)/len(qs)
        ref = next(row for row in reference['rows'] if row['mesh'] == n)
        errors = {}
        for T, values in sums.items():
            expected = np.trace(ref['covariance'][str(T)]['real_m2'])
            errors[str(T)] = float(abs(values.sum()/expected-1))
            np.testing.assert_allclose(values.sum(), expected, rtol=1e-11, atol=0)
        row = dict(mesh=n, trace_bins_m2={str(T): values.tolist() for T, values in sums.items()},
                   total_reconstruction_relative_error=errors)
        rows.append(row)
        print(json.dumps(row), flush=True)
    changes = {}
    for T in TEMPERATURES:
        a, b = (np.array(row['trace_bins_m2'][str(T)]) for row in rows)
        delta = b-a
        changes[str(T)] = dict(delta_trace_bins_m2=delta.tolist(), signed_share_of_net_change=(delta/delta.sum()).tolist(),
                              final_trace_fraction=(b/b.sum()).tolist())
    paths = list(LOCKS)+[Path(__file__), reference_path, ROOT/'docs/core/test/test_topic13_thermal_variance_spectrum.py',
        ROOT/'docs/scripts/audit/audit_topic13_interlayer_thermal_variance.py', ROOT/'docs/core/03_lanes/thermal/uet_interlayer_mode_residue.py',
        ROOT/'docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py']
    artifact = dict(major_result_id='T13_LOCAL_VARIANCE_FREQUENCY_ATTRIBUTION', topic='0.13', closure_level='PARTIAL',
        units='covariance trace m^2; frequency cm^-1', derivation_class='source harmonic model spectral decomposition',
        equation_or_mapping='trace_bin=sum_qj_in_bin ||B^dagger phase(q)e_qj||^2 hbar*coth(hbar*w/(2*kB*T))/(2*mu*w*Nq)',
        frequency_bin_edges_cm_inverse=[0, 10, 30, 100, 300, 1000, 'infinity'], interval_policy='left closed, right open',
        rows=rows, refinement_attribution=changes, phonopy_version=phonopy.__version__,
        verification_status='TOTAL_RECONSTRUCTION_CHECKED', data_role='SOURCE_MODEL_NOT_EXPERIMENT',
        what_is_closed='Frequency attribution of the existing mesh8-to12 difference, not continuum convergence',
        controlling_blocker='frequency_resolved_quadrature_convergence_and_physical_mode_mapping',
        open_blockers=['continuum_convergence', 'phase_and_material_observable_mapping', 'anharmonic_corrections'],
        dependency_unlocked=[], full_core_unlock=False, global_claim_promotion=False,
        claim_boundary='Frequency bins are not acoustic/shear branch identities; signed difference shares are not uncertainty estimates. No alpha or holdout use.',
        evidence_artifacts=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha256(p.read_bytes()).hexdigest()) for p in paths])
    (ROOT/'docs/core/07_artifacts/topic13/t13_thermal_variance_spectrum.json').write_text(json.dumps(artifact, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
