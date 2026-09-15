"""Compare fixed profile residuals with observed baseline frame scatter, not a noise test."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_topic13_ued_rotated_position import rotated_profile
from docs.scripts.audit.audit_topic13_ued_voigt_position import PARAMETERS


def compare_residual(frames,model):
    frames=np.asarray(frames,dtype=float);model=np.asarray(model,dtype=float)
    if frames.ndim!=3 or len(frames)<2 or frames.shape[1:]!=model.shape or not np.isfinite(frames).all() or not np.isfinite(model).all():
        raise ValueError('at least two finite matching image patches required')
    mean=frames.mean(axis=0);residual=mean-model
    residual_norm=float(np.linalg.norm(residual))
    scatter=float(np.sqrt(np.sum((frames-mean)**2)/(len(frames)-1)))
    scale=float(np.linalg.norm(mean))
    if scale<=0:raise ValueError('nonzero baseline required')
    return dict(baseline_frame_count=len(frames),relative_mean_profile_residual=residual_norm/scale,
        relative_observed_frame_scatter=scatter/scale,
        residual_to_frame_scatter=residual_norm/scatter if scatter>0 else None,
        zero_observed_scatter=bool(scatter==0),
        interpretation='Sample frame scatter includes drift and processing; no independence assumption or division by sqrt(N)')


def main():
    fp=ROOT/'docs/core/07_artifacts/topic13/t13_outer_bragg_profiles.json';ip=ROOT/'docs/core/07_artifacts/topic13/t13_ued_numeric_inventory_audit.json';ep=ROOT/'docs/core/07_artifacts/topic13/t13_ued_mask_support_audit.json'
    fits=json.loads(fp.read_text());inventory=json.loads(ip.read_text());exports=json.loads(ep.read_text())
    for e in fits['evidence_artifacts']:
        if sha256((ROOT/e['path']).read_bytes()).hexdigest()!=e['sha256']:raise ValueError('fit/source drift')
    rows=[];hashes={}
    for table in inventory['tables']:
        arrays=[];indices=[]
        for i,r in enumerate(table['rows']):
            if r['delay_ps']>=-.5:continue
            entry=exports['array_exports'][r['imgOFF']['sha256']];path=ROOT/entry['path']
            if sha256(path.read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('array drift')
            arrays.append(np.load(path,allow_pickle=False));indices.append(i);hashes[entry['path']]=entry['sha256']
        stack=np.stack(arrays);source=next(r for r in fits['rows'] if r['member']==table['member']);probes=[]
        for point in source['probes']:
            for radius in (4,8):
                fit=point['fits'][str(radius)]['rotated_primary']
                if not fit['success']:raise ValueError('failed frozen fit')
                anchor=np.rint(point['nominal_yx']).astype(int);lo=anchor-radius;hi=anchor+radius+1
                frames=stack[:,lo[0]:hi[0],lo[1]:hi[1]]/fit['intensity_scale']
                yy,xx=np.indices(frames.shape[1:],dtype=float);yy+=lo[0];xx+=lo[1]
                parameters=[fit['parameters_normalized'][k] for k in PARAMETERS+['angle_rad']]
                result=compare_residual(frames,rotated_profile(parameters,yy,xx))
                np.testing.assert_allclose(result['relative_mean_profile_residual'],fit['relative_residual_l2'],rtol=1e-10,atol=1e-12)
                probes.append(dict(G=point['G'],radius=radius,**result))
        rows.append(dict(member=table['member'],baseline_OFF_indices=indices,probes=probes))
    files=[fp,ip,ep,Path(__file__),ROOT/'docs/core/test/test_topic13_profile_residual_baseline_scatter.py',ROOT/'docs/scripts/audit/audit_topic13_ued_rotated_position.py']
    output=dict(major_result_id='T13_PROFILE_RESIDUAL_BASELINE_SCATTER',topic='0.13',closure_level='PARTIAL',
        what_is_closed='Frozen profile residual compared with actual baseline frame scatter at every outer patch',
        equation_or_mapping='||mean(I)-model|| versus sqrt(sum_t ||I_t-mean(I)||^2/(N-1)); no standard-error scaling',
        units='normalized intensity norms and dimensionless ratios',derivation_class='descriptive baseline residual comparison',
        observable='profile discrepancy and baseline frame variation',data_role='EXTERNAL_BASELINE_DIAGNOSTIC',rows=rows,
        verification_status='FROZEN_RESIDUAL_AND_SCATTER_MEASURED',controlling_blocker='profile_background_adequacy_and_detector_error_model',
        open_blockers=['frame_dependence_and_drift','model_bias_vs_processing','physical_coordinate_uncertainty','UET_mapping'],
        dependency_unlocked=[],full_core_unlock=False,global_claim_promotion=False,
        claim_boundary='Not a chi-square test, p-value, independent noise-floor estimate or physical calibration. No refit, pixel fill, holdout or image transformation.',
        array_export_hashes=hashes,evidence_artifacts=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha256(p.read_bytes()).hexdigest()) for p in files])
    (ROOT/'docs/core/07_artifacts/topic13/t13_profile_residual_baseline_scatter.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    print(json.dumps(rows))


if __name__=='__main__':main()
