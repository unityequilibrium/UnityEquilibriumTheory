"""Reuse frozen Voigt solvers on baseline outer-shell Bragg patches; no warp."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_topic13_ued_voigt_position import fit_roi
from docs.scripts.audit.audit_topic13_ued_rotated_position import fit_rotated


def main():
    pp=ROOT/'docs/core/07_artifacts/topic13/t13_multibragg_positions.json'
    ip=ROOT/'docs/core/07_artifacts/topic13/t13_ued_numeric_inventory_audit.json'
    ep=ROOT/'docs/core/07_artifacts/topic13/t13_ued_mask_support_audit.json'
    positions=json.loads(pp.read_text());inventory=json.loads(ip.read_text());exports=json.loads(ep.read_text())
    for source in (positions,):
        for e in source['evidence_artifacts']:
            if sha256((ROOT/e['path']).read_bytes()).hexdigest()!=e['sha256']:raise ValueError('upstream drift')
    rows=[];hashes={}
    for table in inventory['tables']:
        previous=next(t for t in positions['rows'] if t['member']==table['member'])
        arrays=[]
        for i in previous['baseline_OFF_indices']:
            row=table['rows'][i];entry=exports['array_exports'][row['imgOFF']['sha256']];path=ROOT/entry['path']
            if sha256(path.read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('array drift')
            arrays.append(np.load(path,allow_pickle=False));hashes[entry['path']]=entry['sha256']
        image=np.mean(arrays,axis=0);probes=[]
        for point in previous['probes']:
            h,k,_=point['G']
            if h*h+k*k+h*k!=4:continue
            fits={}
            for radius in (4,8):
                anchor=np.rint(point['nominal_yx']).astype(int);lo=anchor-radius;hi=anchor+radius+1
                roi=image[lo[0]:hi[0],lo[1]:hi[1]]
                if roi.shape!=(2*radius+1,2*radius+1):raise ValueError('truncated ROI')
                source=fit_roi(roi,origin=tuple(lo),start='source')
                peak=fit_roi(roi,origin=tuple(lo),start='peak')
                rotated=fit_rotated(roi,source['parameters_normalized'],origin=tuple(lo))
                fits[str(radius)]=dict(unrotated_source=source,unrotated_peak=peak,rotated_primary=rotated,
                    start_center_difference_pixels=float(np.linalg.norm(np.array(source['centroid_row_col'])-peak['centroid_row_col'])),
                    rotated_minus_moment_pixels=float(np.linalg.norm(np.array(rotated['center_row_col'])-point['radii'][str(radius)]['centroid_yx'])))
            probes.append(dict(G=point['G'],nominal_yx=point['nominal_yx'],fits=fits,
                rotated_window_center_difference_pixels=float(np.linalg.norm(np.array(fits['4']['rotated_primary']['center_row_col'])-fits['8']['rotated_primary']['center_row_col']))))
            print(table['member'],point['G'],'completed',flush=True)
        rows.append(dict(member=table['member'],probes=probes))
    allfits=[v[name] for t in rows for p in t['probes'] for v in p['fits'].values() for name in ('unrotated_source','unrotated_peak','rotated_primary')]
    summary=dict(fit_count=len(allfits),failed_optimizer_count=sum(not f['success'] for f in allfits),
        rotated_relative_residual_range=[min(v['rotated_primary']['relative_residual_l2'] for t in rows for p in t['probes'] for v in p['fits'].values()),max(v['rotated_primary']['relative_residual_l2'] for t in rows for p in t['probes'] for v in p['fits'].values())],
        max_unrotated_start_center_difference_pixels=max(v['start_center_difference_pixels'] for t in rows for p in t['probes'] for v in p['fits'].values()),
        max_rotated_window_center_difference_pixels=max(p['rotated_window_center_difference_pixels'] for t in rows for p in t['probes']))
    files=[pp,ip,ep,Path(__file__),ROOT/'docs/scripts/audit/audit_topic13_ued_voigt_position.py',ROOT/'docs/scripts/audit/audit_topic13_ued_rotated_position.py',
        ROOT/'docs/core/test/test_topic13_ued_voigt_position.py',ROOT/'docs/core/test/test_topic13_ued_rotated_position.py']
    output=dict(major_result_id='T13_OUTER_BRAGG_PROFILE_COMPARISON',topic='0.13',closure_level='PARTIAL',
        what_is_closed='Frozen source-style and rotated Voigt fits evaluated on actual baseline outer-shell patches',
        equation_or_mapping='Existing separable/rotated Voigt plus constant background; uniform weighting and bounds unchanged',
        units='centers pixels; normalized intensity residual',derivation_class='empirical baseline profile comparison',
        observable='baseline outer Bragg profile centers',data_role='EXTERNAL_BASELINE_DIAGNOSTIC',rows=rows,summary=summary,
        verification_status='FIT_DIAGNOSTICS_RECORDED_NOT_ACCURACY',controlling_blocker='profile_background_adequacy_and_coordinate_uncertainty',
        open_blockers=['no_measured_noise_floor','rotated_start_sensitivity','processing_correlation','finite_patch_response','UET_mapping'],
        dependency_unlocked=[],full_core_unlock=False,global_claim_promotion=False,
        claim_boundary='No optimizer outcome, small residual or window agreement defines physical accuracy. No image correction, alpha fitting or holdout.',
        array_export_hashes=hashes,evidence_artifacts=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha256(p.read_bytes()).hexdigest()) for p in files])
    (ROOT/'docs/core/07_artifacts/topic13/t13_outer_bragg_profiles.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    print(json.dumps(summary))


if __name__=='__main__':main()
