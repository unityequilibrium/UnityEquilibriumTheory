"""Test local second moment, not energy, against existing ideal scattering rows."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
import phonopy

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_topic13_energy_identifiability import observable_null_test
from docs.scripts.audit.audit_topic13_finiteq_scattering_geometry import mode_geometry
from docs.scripts.audit.audit_topic13_mp48_force_constant_harmonic_reconstruction import PHONOPY_PATH,load_phonopy,load_force_constants
from docs.scripts.audit.audit_topic13_mp48_interlayer_mode_residue import LOCKS
from docs.core.uet_interlayer_mode_residue import shear_basis,cell_phase


def target_weights(overlap,frequencies):
    overlap=np.asarray(overlap,dtype=complex); f=np.asarray(frequencies,dtype=float)
    if overlap.ndim!=2 or overlap.shape[1]!=f.size or not np.isfinite(overlap).all() or not np.isfinite(f).all() or np.any(f<=0):
        raise ValueError('finite overlaps and strictly positive matching frequencies required')
    return np.sum(abs(overlap)**2,axis=0)/f


def renamed_null_test(a,c,rtol=1e-10):
    result=observable_null_test(a,c,rtol)
    witness=result.get('synthetic_witness')
    if witness:
        witness['target_difference']=witness.pop('energy_difference')
        witness['relative_target_difference_to_unit_population']=witness.pop('relative_energy_difference_to_unit_population')
    return result


def main():
    for path,expected in LOCKS.items():
        if sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('source hash mismatch')
    model=phonopy.load(str(PHONOPY_PATH),produce_fc=False,symmetrize_fc=False,is_nac=False,lang='C')
    model.force_constants=load_force_constants()[0]
    cell=model.primitive
    factor=float(load_phonopy()['phonopy']['frequency_unit_conversion_factor'])
    rec=2*np.pi*np.linalg.inv(cell.cell).T
    basis,mu_amu=shear_basis(cell.masses,[0,1,0,1],[0,0,1],[1,0,0])
    qpoints=[[s,t*s,0] for t in (0,1) for s in (.005,.02,.1)]
    designs={'basal':[0],'complementary':[-2,-1,0,1,2]}
    rows=[]
    for q in qpoints:
        matrix=model.run_qpoints([q],with_dynamical_matrices=True).dynamical_matrices[0]
        values,vectors=np.linalg.eigh(matrix)
        if np.any(values<=0):raise ValueError('no clipping of unstable frequencies')
        f=np.sqrt(values)*factor
        overlap=basis.conj().T@(cell_phase(q,cell.scaled_positions)[:,None]*vectors)
        target=target_weights(overlap,f)
        results={}
        for name,planes in designs.items():
            grid=[[h,k,l] for l in planes for h in range(-2,3) for k in range(-2,3) if h or k]
            response=np.array([mode_geometry((np.array(g)+q)@rec,g,cell.scaled_positions,cell.masses,vectors) for g in grid])/f[None,:]
            results[name]=dict(G_grid=grid,response=response.tolist(),
                null_test=renamed_null_test(response,target),
                tolerance_sweep={str(t):renamed_null_test(response,target,t)['observable_null_fraction'] for t in (1e-9,1e-10,1e-11)})
        row=dict(q=q,frequencies_THz=f.tolist(),target_weights_inverse_THz=target.tolist(),designs=results)
        rows.append(row)
        print(json.dumps(dict(q=q,tests={name:r['null_test'] for name,r in results.items()})),flush=True)
    files=list(LOCKS)+[Path(__file__),ROOT/'docs/core/test/test_topic13_local_variance_identifiability.py',
        ROOT/'docs/scripts/audit/audit_topic13_energy_identifiability.py',ROOT/'docs/scripts/audit/audit_topic13_finiteq_scattering_geometry.py',
        ROOT/'docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py',ROOT/'docs/core/uet_interlayer_mode_residue.py']
    artifact=dict(major_result_id='T13_LOCAL_SECOND_MOMENT_OBSERVABILITY',topic='0.13',closure_level='PARTIAL',
        what_is_closed='Target-specific row-space test for local variance in two ideal geometry designs',
        equation_or_mapping='A=S/f_THz; c_j=||B^dagger P e_j||^2/f_THz; delta trace=hbar/(mu_kg*2*pi*1e12)*c.delta_n per q before BZ weights',
        units='c THz^-1; physical trace m^2 after declared prefactor',reduced_mass_amu=mu_amu,
        derivation_class='linear algebra on harmonic diagonal-occupation comparator',observable='change of same-cell local second moment',
        data_role='SOURCE_MODEL_AND_SYNTHETIC_WITNESSES',rows=rows,
        verification_status='TARGET_NULL_SPACE_TESTED_NOT_EXPERIMENTAL_INVERSION',
        controlling_blocker='physical_detector_geometry_covariance_and_material_operator_matching',
        open_blockers=['physical_detector_response','off_diagonal_mode_coherence','BZ_coverage','independent_UET_normalization'],
        dependency_unlocked=[],full_core_unlock=False,global_claim_promotion=False,
        claim_boundary='Ideal rows are not acquired measurements. Fixed frequencies and diagonal occupations only; no fitting, thermometry, alpha or holdout.',
        evidence_artifacts=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha256(p.read_bytes()).hexdigest()) for p in files])
    (ROOT/'docs/core/07_artifacts/topic13/t13_local_variance_identifiability.json').write_text(json.dumps(artifact,indent=2,allow_nan=False)+'\n')


if __name__=='__main__':main()
