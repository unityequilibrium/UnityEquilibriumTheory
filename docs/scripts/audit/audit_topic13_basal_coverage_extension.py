"""Generic-q and expanded basal coverage, not a reproduction of a published experiment."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
import phonopy

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_topic13_local_variance_identifiability import target_weights,renamed_null_test
from docs.scripts.audit.audit_topic13_finiteq_scattering_geometry import mode_geometry
from docs.scripts.audit.audit_topic13_mp48_force_constant_harmonic_reconstruction import PHONOPY_PATH,load_phonopy,load_force_constants
from docs.scripts.audit.audit_topic13_mp48_interlayer_mode_residue import LOCKS
from docs.core.uet_interlayer_mode_residue import shear_basis,cell_phase


def main():
    for path,expected in LOCKS.items():
        if sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('source hash mismatch')
    model=phonopy.load(str(PHONOPY_PATH),produce_fc=False,symmetrize_fc=False,is_nac=False,lang='C')
    model.force_constants=load_force_constants()[0]
    cell=model.primitive; rec=2*np.pi*np.linalg.inv(cell.cell).T
    factor=float(load_phonopy()['phonopy']['frequency_unit_conversion_factor'])
    basis,_=shear_basis(cell.masses,[0,1,0,1],[0,0,1],[1,0,0])
    grids={'prior24':[[h,k,0] for h in range(-2,3) for k in range(-2,3) if h or k],
        'radius12':[[h,k,0] for h in range(-8,9) for k in range(-8,9) if (h or k) and np.linalg.norm(np.array([h,k,0])@rec)<=12.]}
    rows=[]
    for q in ([.1,0,0],[.1,.1,0],[.07,.113,0],[.173,.097,0],[.23,.19,0],[.3,.12,0]):
        matrix=model.run_qpoints([q],with_dynamical_matrices=True).dynamical_matrices[0]
        values,vectors=np.linalg.eigh(matrix)
        if np.any(values<=0):raise ValueError('unstable source')
        f=np.sqrt(values)*factor
        c=target_weights(basis.conj().T@(cell_phase(q,cell.scaled_positions)[:,None]*vectors),f)
        result={}
        for name,grid in grids.items():
            a=np.array([mode_geometry((np.array(g)+q)@rec,g,cell.scaled_positions,cell.masses,vectors) for g in grid])/f[None,:]
            result[name]=dict(row_count=len(grid),test=renamed_null_test(a,c),
                tolerance_sweep={str(t):renamed_null_test(a,c,t)['observable_null_fraction'] for t in (1e-9,1e-10,1e-11)})
        rows.append(dict(q=q,q_norm_inverse_angstrom=float(np.linalg.norm(np.array(q)@rec)),designs=result))
    paths=list(LOCKS)+[Path(__file__),ROOT/'docs/scripts/audit/audit_topic13_local_variance_identifiability.py',
        ROOT/'docs/scripts/audit/audit_topic13_energy_identifiability.py',ROOT/'docs/scripts/audit/audit_topic13_finiteq_scattering_geometry.py',
        ROOT/'docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py',ROOT/'docs/core/uet_interlayer_mode_residue.py']
    output=dict(major_result_id='T13_BASAL_COVERAGE_EXTENSION',topic='0.13',closure_level='PARTIAL',
        what_is_closed='Generic-q and expanded basal-row target-identifiability tests in the current MP48 comparator',
        equation_or_mapping='Existing A=S/f and local target c, with only reciprocal coverage and q changed',
        units='q and G magnitude inverse angstrom including2pi',derivation_class='source-model linear observability diagnostic',
        observable='local second-moment population response',data_role='SOURCE_MODEL_NOT_EXPERIMENT',rows=rows,G_grids=grids,
        literature_context=dict(url='https://arxiv.org/pdf/1908.02795',locator='Section III.D, PDF page7; reference46 PDF page14',
            difference='Published experiment uses8 in-plane branches,44 BZ, |k|>.45 inverse angstrom and nonnegative population-change inversion; not this source or12-mode comparator'),
        verification_status='COVERAGE_AND_TOLERANCE_SWEEP_RECORDED',controlling_blocker='source_specific_detector_operator_and_independent_information',
        open_blockers=['model_to_experiment_correspondence','actual_numeric_multigeometry_data','detector_covariance','UET_mapping'],
        dependency_unlocked=[],full_core_unlock=False,global_claim_promotion=False,
        claim_boundary='Does not reproduce or refute the published inversion; common row factors, site-dependent corrections and experimental conditions differ.',
        evidence_artifacts=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha256(p.read_bytes()).hexdigest()) for p in paths])
    (ROOT/'docs/core/07_artifacts/topic13/t13_basal_coverage_extension.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    print(json.dumps(rows))


if __name__=='__main__':main()
