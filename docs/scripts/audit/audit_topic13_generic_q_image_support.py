"""Conditional generic-q detector footprints; finite support is not inversion."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
import phonopy

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_topic13_mp48_force_constant_harmonic_reconstruction import load_phonopy,load_force_constants,PHONOPY_PATH
from docs.scripts.audit.audit_topic13_local_variance_identifiability import target_weights,renamed_null_test
from docs.scripts.audit.audit_topic13_finiteq_scattering_geometry import mode_geometry
from docs.core.uet_interlayer_mode_residue import shear_basis,cell_phase


def footprint(shape,center):
    y,x=np.indices(shape)
    return (abs(y-center[0])<=1.5)&(abs(x-center[1])<=1.5)


def main():
    ip=ROOT/'docs/core/07_artifacts/topic13/t13_ued_numeric_inventory_audit.json'
    ep=ROOT/'docs/core/07_artifacts/topic13/t13_ued_mask_support_audit.json'
    gp=ROOT/'docs/core/07_artifacts/topic13/t13_basal_coverage_extension.json'
    inventory=json.loads(ip.read_text()); exports=json.loads(ep.read_text()); geometry=json.loads(gp.read_text())
    for source in (inventory,exports):
        for path,h in source['evidence_hashes'].items():
            if sha256((ROOT/path).read_bytes()).hexdigest()!=h:raise ValueError('upstream drift '+path)
    for e in geometry['evidence_artifacts']:
        if sha256((ROOT/e['path']).read_bytes()).hexdigest()!=e['sha256']:raise ValueError('geometry drift')
    rec=2*np.pi*np.linalg.inv(np.array(load_phonopy()['primitive_cell']['lattice'])).T
    g1=rec[0,:2]; theta=np.pi/2-np.arctan2(g1[1],g1[0])
    rotation=np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
    grid=geometry['G_grids']['prior24']; rows=[]; files={}
    model=phonopy.load(str(PHONOPY_PATH),produce_fc=False,symmetrize_fc=False,is_nac=False,lang='C')
    model.force_constants=load_force_constants()[0]
    basis,_=shear_basis(model.primitive.masses,[0,1,0,1],[0,0,1],[1,0,0])
    operators={}
    for prior in geometry['rows'][2:]:
        q=np.array(prior['q'])
        matrix=model.run_qpoints([q],with_dynamical_matrices=True).dynamical_matrices[0]
        values,vectors=np.linalg.eigh(matrix)
        if np.any(values<=0):raise ValueError('unstable source')
        f=np.sqrt(values)*float(load_phonopy()['phonopy']['frequency_unit_conversion_factor'])
        overlap=basis.conj().T@(cell_phase(q,model.primitive.scaled_positions)[:,None]*vectors)
        response=np.array([mode_geometry((np.array(g)+q)@rec,g,model.primitive.scaled_positions,model.primitive.masses,vectors) for g in grid])/f[None,:]
        operators[tuple(q)]=(response,target_weights(overlap,f))
    for table in inventory['tables']:
        common=np.ones((512,512),dtype=bool)
        for row in table['rows']:
            for role in ('imgON','imgOFF'):
                entry=exports['array_exports'][row[role]['sha256']]; path=ROOT/entry['path']
                if sha256(path.read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('array drift')
                array=np.load(path,allow_pickle=False)
                if array.shape!=common.shape:raise ValueError('array shape')
                common &= np.isfinite(array)
                files[entry['path']]=entry['sha256']
        origin=np.array(table['source_zero_order_position'])
        cal=table['calibration_inverse_angstrom_per_pixel']
        results=[]
        for prior in geometry['rows'][2:]:
            q=np.array(prior['q'])
            for mirror in (-1,1):
                points=[]
                for g in grid:
                    xy=((np.array(g)+q)@rec)[:2]@rotation.T
                    xy[0]*=mirror
                    center=origin+np.array([xy[1],xy[0]])/cal
                    mask=footprint(common.shape,center)
                    inside=bool(np.all(center-1.5>=0) and np.all(center+1.5<=np.array(common.shape)-1))
                    points.append(dict(G=g,center_yx=center.tolist(),inside_image=inside,
                        geometric_pixels=int(mask.sum()),common_pixels=int((mask&common).sum()),
                        full_finite_footprint=bool(inside and mask.any() and common[mask].all())))
                kept=np.array([p['full_finite_footprint'] for p in points])
                response,target=operators[tuple(q)]
                results.append(dict(q=q.tolist(),mirror=mirror,points=points,
                    full_finite_rows=int(kept.sum()),conditional_ideal_null_test=renamed_null_test(response[kept],target)))
        rows.append(dict(member=table['member'],origin_yx=origin.tolist(),calibration_inverse_angstrom_per_pixel=cal,
            source_peak_momentum=table['source_peak_distance_pixels']*cal,
            model_first_reciprocal_magnitude=float(np.linalg.norm(g1)),results=results))
    paths=[ip,ep,gp,PHONOPY_PATH,Path(__file__),ROOT/'docs/core/test/test_topic13_generic_q_image_support.py',
        ROOT/'docs/scripts/audit/audit_topic13_local_variance_identifiability.py',ROOT/'docs/scripts/audit/audit_topic13_energy_identifiability.py',
        ROOT/'docs/scripts/audit/audit_topic13_finiteq_scattering_geometry.py',ROOT/'docs/core/03_lanes/thermal/uet_interlayer_mode_residue.py']
    output=dict(major_result_id='T13_GENERIC_Q_IMAGE_SUPPORT',topic='0.13',closure_level='PARTIAL',
        what_is_closed='Conditional footprint support against actual finite masks, not indexed detector inversion',
        equation_or_mapping='Model first reciprocal vector aligned to source positive detector y; mirrored x alternatives retained',
        units='detector pixels; reciprocal inverse angstrom',derivation_class='conditional coordinate mapping and mask audit',
        observable='finite detector support only',data_role='EXTERNAL_DATA_MASK_DIAGNOSTIC',rows=rows,
        verification_status='CONDITIONAL_SUPPORT_AND_IDEAL_TARGET_CHECKED',controlling_blocker='full_reciprocal_indexing_and_detector_weighted_identifiability',
        open_blockers=['orientation_and_strain_calibration','independent_row_covariance','Bragg_and_diffuse_separation','UET_normalization'],
        footprint_halfwidth_pixels=1.5,selection_uses_signal=False,smoothing=False,fit=False,
        dependency_unlocked=[],full_core_unlock=False,global_claim_promotion=False,
        claim_boundary='No numerical signal extraction, branch population or alpha. One-vector alignment does not establish complete reciprocal indexing.',
        array_export_hashes=files,evidence_artifacts=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha256(p.read_bytes()).hexdigest()) for p in paths])
    (ROOT/'docs/core/07_artifacts/topic13/t13_generic_q_image_support.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    print(json.dumps([dict(member=r['member'],source_peak=r['source_peak_momentum'],model_peak=r['model_first_reciprocal_magnitude'],
        support=[dict(q=s['q'],mirror=s['mirror'],rows=s['full_finite_rows']) for s in r['results']]) for r in rows]))


if __name__=='__main__':main()
