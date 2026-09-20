"""Unfitted baseline Bragg-position diagnostics; not geometry calibration."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_topic13_mp48_force_constant_harmonic_reconstruction import load_phonopy,PHONOPY_PATH


def peak_probe(image,center,radius):
    center=np.asarray(center,dtype=float)
    anchor=np.rint(center).astype(int)
    lo=anchor-radius;hi=anchor+radius+1
    if np.any(lo<0) or np.any(hi>image.shape):return dict(status='OUTSIDE')
    patch=image[lo[0]:hi[0],lo[1]:hi[1]]
    if not np.isfinite(patch).all() or np.any(patch<0) or patch.sum()<=0:return dict(status='UNRESOLVED_PATCH')
    yy,xx=np.indices(patch.shape)
    centroid=np.array([np.sum(patch*(yy+lo[0])),np.sum(patch*(xx+lo[1]))])/patch.sum()
    local=np.array(np.unravel_index(np.argmax(patch),patch.shape));peak=local+lo
    return dict(status='MEASURED_NOT_CALIBRATED',peak_yx=peak.tolist(),centroid_yx=centroid.tolist(),
        peak_offset_pixels=float(np.linalg.norm(peak-center)),centroid_offset_pixels=float(np.linalg.norm(centroid-center)),
        peak_on_boundary=bool(np.any(local==0) or np.any(local==2*radius)),
        maximum_over_median=float(patch.max()/np.median(patch)) if np.median(patch)>0 else None)


def main():
    ip=ROOT/'docs/core/07_artifacts/topic13/t13_ued_numeric_inventory_audit.json';ep=ROOT/'docs/core/07_artifacts/topic13/t13_ued_mask_support_audit.json'
    inventory=json.loads(ip.read_text());exports=json.loads(ep.read_text())
    for source in (inventory,exports):
        for p,h in source['evidence_hashes'].items():
            if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('evidence drift')
    rec=2*np.pi*np.linalg.inv(np.array(load_phonopy()['primitive_cell']['lattice'])).T
    b=np.linalg.norm(rec[0,:2]);theta=np.pi/2-np.arctan2(rec[0,1],rec[0,0])
    rotation=np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
    grid=[[h,k,0] for h in range(-2,3) for k in range(-2,3) if (h or k) and np.linalg.norm(np.array([h,k,0])@rec)<=2.05*b]
    rows=[];hashes={}
    for table in inventory['tables']:
        arrays=[];indices=[]
        for i,r in enumerate(table['rows']):
            if r['delay_ps']>=-.5:continue
            entry=exports['array_exports'][r['imgOFF']['sha256']];p=ROOT/entry['path']
            if sha256(p.read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('array drift')
            arrays.append(np.load(p,allow_pickle=False));indices.append(i);hashes[entry['path']]=entry['sha256']
        if not arrays:raise ValueError('empty baseline')
        # Nonfinite values propagate: a missing pixel is never filled by another frame.
        image=np.mean(arrays,axis=0)
        origin=np.array(table['source_zero_order_position']);cal=table['calibration_inverse_angstrom_per_pixel']
        probes=[]
        for g in grid:
            xy=(np.array(g)@rec)[:2]@rotation.T
            center=origin+xy[::-1]/cal
            probes.append(dict(G=g,nominal_yx=center.tolist(),momentum_norm=float(np.linalg.norm(np.array(g)@rec)),
                radii={str(r):peak_probe(image,center,r) for r in (4,8)}))
        rows.append(dict(member=table['member'],baseline_OFF_indices=indices,probes=probes))
    files=[ip,ep,PHONOPY_PATH,Path(__file__),ROOT/'docs/core/test/test_topic13_multibragg_positions.py']
    artifact=dict(major_result_id='T13_MULTIBRAGG_POSITION_DIAGNOSTIC',topic='0.13',closure_level='PARTIAL',
        what_is_closed='Unfitted multi-Bragg baseline offsets measured under existing candidate reciprocal map',
        equation_or_mapping='Intensity maxima and uncorrected centroids in fixed4/8 pixel half-width windows',
        units='pixels; momentum inverse angstrom',derivation_class='external-image coordinate diagnostic',
        observable='baseline OFF diffraction peak positions',data_role='EXTERNAL_DATA_DIAGNOSTIC',rows=rows,
        verification_status='POSITION_PROBES_RECORDED',controlling_blocker='peak_shape_background_and_geometry_uncertainty',
        open_blockers=['reciprocal_index_validation','detector_distortion_covariance','physical_response','UET_mapping'],
        dependency_unlocked=[],full_core_unlock=False,global_claim_promotion=False,
        claim_boundary='No peak fit, image transformation, threshold tuning or holdout. Symmetry-processed Bragg agreement is not independent orientation validation.',
        array_export_hashes=hashes,evidence_artifacts=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha256(p.read_bytes()).hexdigest()) for p in files])
    (ROOT/'docs/core/07_artifacts/topic13/t13_multibragg_positions.json').write_text(json.dumps(artifact,indent=2,allow_nan=False)+'\n')
    print(json.dumps([dict(member=r['member'],probes=[dict(G=p['G'],radii=p['radii']) for p in r['probes']]) for r in rows]))


if __name__=='__main__':main()
