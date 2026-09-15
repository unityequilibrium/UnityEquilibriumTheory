"""Local relative-layer harmonic variance from all BZ modes; no UET mapping."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
from scipy.constants import hbar,k,physical_constants
import phonopy

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.core.uet_interlayer_mode_residue import shear_basis,cell_phase
from docs.scripts.audit.audit_topic13_mp48_interlayer_mode_residue import LOCKS
from docs.scripts.audit.audit_topic13_mp48_force_constant_harmonic_reconstruction import PHONOPY_PATH,load_phonopy,load_force_constants


def oscillator_variance(omega,temperature):
    omega=np.asarray(omega,dtype=float)
    if np.any(~np.isfinite(omega)) or np.any(omega<=0) or not np.isfinite(temperature) or temperature<0:
        raise ValueError("positive finite frequencies and nonnegative T required")
    return hbar/(2*omega) if temperature==0 else hbar/(2*omega)/np.tanh(hbar*omega/(2*k*temperature))


def modal_covariance(overlap,omega,temperature,reduced_mass):
    if not np.isfinite(reduced_mass) or reduced_mass<=0:
        raise ValueError("positive reduced mass required")
    overlap=np.asarray(overlap,dtype=complex)
    if overlap.ndim!=2 or overlap.shape[1]!=len(omega) or not np.all(np.isfinite(overlap)):
        raise ValueError("finite overlap with one column per mode required")
    return (overlap*oscillator_variance(omega,temperature))@overlap.conj().T/reduced_mass


def main():
    for path,expected in LOCKS.items():
        if sha256(path.read_bytes()).hexdigest()!=expected: raise ValueError("source hash mismatch")
    meta=load_phonopy(); fc=load_force_constants()[0]
    model=phonopy.load(str(PHONOPY_PATH),produce_fc=False,symmetrize_fc=False,is_nac=False,lang='C')
    model.force_constants=fc
    points=meta['primitive_cell']['points']
    positions=np.array([p['coordinates'] for p in points])
    np.testing.assert_allclose(model.primitive.scaled_positions,positions,atol=1e-12)
    np.testing.assert_allclose(positions[:,2],[.25,.75,.25,.75],atol=1e-12)
    masses=np.array([p['mass'] for p in points])*physical_constants['atomic mass constant'][0]
    basis,mu=shear_basis(masses,[0,1,0,1],[0,0,1],[1,0,0])
    factor=float(meta['phonopy']['frequency_unit_conversion_factor'])*2*np.pi*1e12
    rows=[]
    for n in (2,4,6,8,12):
        axis=(np.arange(n)+.5)/n-.5
        qs=np.array(np.meshgrid(axis,axis,axis,indexing='ij')).reshape(3,-1).T
        result=model.run_qpoints(qs,with_dynamical_matrices=True)
        cov={T:np.zeros((2,2),dtype=complex) for T in (0.,100.,200.,300.)}
        unstable=[]; minimum=float('inf')
        for index,(q,matrix) in enumerate(zip(qs,result.dynamical_matrices)):
            values,vectors=np.linalg.eigh(matrix)
            minimum=min(minimum,float(values.min()))
            if np.any(values<=0):
                unstable.append(dict(q_index=index,q=q.tolist(),minimum_eigenvalue=float(values.min())))
                continue
            overlap=basis.conj().T@(cell_phase(q,positions)[:,None]*vectors)
            omega=np.sqrt(values)*factor
            for T in cov:
                cov[T]+=modal_covariance(overlap,omega,T,mu)/len(qs)
        row=dict(mesh=n,q_count=len(qs),minimum_raw_eigenvalue=minimum,unstable_points=unstable,
                 status="BLOCKED_UNSTABLE_HARMONIC_SOURCE" if unstable else "HARMONIC_COVARIANCE_COMPUTED")
        # Never emit the positive-subset sum when even one point was excluded.
        row['covariance']=None if unstable else {str(T):dict(real_m2=C.real.tolist(),imaginary_norm=float(np.linalg.norm(C.imag)),
            radial_rms_angstrom=float(np.sqrt(np.trace(C).real)*1e10)) for T,C in cov.items()}
        rows.append(row)
        print(json.dumps(row),flush=True)
    r=dict(major_result_id="T13_MP48_LOCAL_INTERLAYER_THERMAL_VARIANCE",topic="0.13",closure_level="PARTIAL",
        equation_or_mapping="Cov(s)=1/Nq sum_q O_q diag[hbar*coth(hbar*w/(2*kB*T))/(2*mu*w)] O_q^dagger; O_q=B^dagger phase(q) e_q",
        units="m^2; mass-centroid layer-relative local displacement",derivation_class="Harmonic source-model equilibrium covariance",
        data_role="SOURCE_HARMONIC_MODEL_NOT_EXPERIMENTAL_AMPLITUDE",rows=rows,
        what_is_closed="All-mode shifted-mesh variance attempted without replacing local motion by one coherent Gamma oscillator",
        verification_status="MEASURED_MESH_SEQUENCE",dependency_unlocked=[],full_core_unlock=False,
        open_blockers=["mesh_convergence_and_source_stability","anharmonic_state_and_displacement_mapping","same_state_Fourier_model_transfer"],
        claim_boundary="No clipping negative modes; no direct transfer to Popov potential or UET alpha. RMS fluctuation is not coherent pump amplitude.",
        evidence_artifacts=[dict(path=str(p.relative_to(ROOT)).replace('\\','/'),sha256=sha256(p.read_bytes()).hexdigest()) for p in list(LOCKS)+[Path(__file__),ROOT/'docs/core/test/test_topic13_interlayer_thermal_variance.py',ROOT/'docs/core/uet_interlayer_mode_residue.py',ROOT/'docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py']])
    (ROOT/'docs/core/07_artifacts/topic13/t13_interlayer_thermal_variance_audit.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n',encoding='utf-8')


if __name__=='__main__':main()
