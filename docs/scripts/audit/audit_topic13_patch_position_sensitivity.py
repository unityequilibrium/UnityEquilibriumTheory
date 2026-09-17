"""Fixed readout-coordinate stress test; never moves images or optimizes a signal."""
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
OFFSETS=((0,0),(1,0),(-1,0),(0,1),(0,-1),(2,0),(-2,0),(0,2),(0,-2))


def patch_curve(on,off,center,baseline):
    center=np.asarray(center,dtype=float)
    y=np.arange(int(np.ceil(center[0]-1.5)),int(np.floor(center[0]+1.5))+1)
    x=np.arange(int(np.ceil(center[1]-1.5)),int(np.floor(center[1]+1.5))+1)
    if not len(y) or not len(x) or y[0]<0 or x[0]<0 or y[-1]>=on.shape[1] or x[-1]>=on.shape[2]:
        return dict(status='OUTSIDE')
    a=on[:,y[:,None],x].reshape(len(on),-1);b=off[:,y[:,None],x].reshape(len(off),-1)
    if not np.isfinite(a).all() or not np.isfinite(b).all():return dict(status='NONFINITE_PATCH')
    denominator=b.sum(axis=1)
    if np.any(denominator<=0):return dict(status='NONPOSITIVE_DENOMINATOR')
    if not np.any(baseline):raise ValueError('nonempty baseline required')
    ratio=a.sum(axis=1)/denominator
    return dict(status='COMPUTED',ratio=ratio.tolist(),baseline_subtracted=(ratio-ratio[baseline].mean()).tolist(),pixels=len(y)*len(x))


def main():
    sp=ROOT/'docs/core/07_artifacts/topic13/t13_generic_q_image_support.json'
    ip=ROOT/'docs/core/07_artifacts/topic13/t13_ued_numeric_inventory_audit.json'
    ep=ROOT/'docs/core/07_artifacts/topic13/t13_ued_mask_support_audit.json'
    support=json.loads(sp.read_text());inventory=json.loads(ip.read_text());exports=json.loads(ep.read_text())
    for e in support['evidence_artifacts']:
        if sha256((ROOT/e['path']).read_bytes()).hexdigest()!=e['sha256']:raise ValueError('upstream drift')
    rows=[];array_hashes={}
    for table in inventory['tables']:
        stacks={}
        for role in ('imgON','imgOFF'):
            arrays=[]
            for r in table['rows']:
                e=exports['array_exports'][r[role]['sha256']];path=ROOT/e['path']
                if sha256(path.read_bytes()).hexdigest()!=e['sha256']:raise ValueError('array drift')
                arrays.append(np.load(path,allow_pickle=False));array_hashes[e['path']]=e['sha256']
            stacks[role]=np.stack(arrays)
        delay=np.array([r['delay_ps'] for r in table['rows']]);baseline=delay<-.5
        source=next(r for r in support['rows'] if r['member']==table['member'])
        cases=[]
        for s in source['results']:
            probes=[]
            for p in s['points']:
                variations=[dict(offset_yx=list(d),**patch_curve(stacks['imgON'],stacks['imgOFF'],np.array(p['center_yx'])+d,baseline)) for d in OFFSETS]
                complete=all(v['status']=='COMPUTED' for v in variations)
                record=dict(G=p['G'],nominal_center_yx=p['center_yx'],all_offsets_resolved=complete,variations=variations)
                if complete:
                    curves=np.array([v['baseline_subtracted'] for v in variations])
                    record['max_absolute_change_from_nominal']=float(np.max(abs(curves-curves[0])))
                    record['nominal_max_absolute_signal']=float(np.max(abs(curves[0])))
                probes.append(record)
            resolved=[p for p in probes if p['all_offsets_resolved']]
            cases.append(dict(q=s['q'],mirror=s['mirror'],probes=probes,all_offsets_resolved_rows=len(resolved),
                maximum_absolute_curve_change=max((p['max_absolute_change_from_nominal'] for p in resolved),default=None)))
        rows.append(dict(member=table['member'],delay_ps=delay.tolist(),baseline_indices=np.flatnonzero(baseline).tolist(),cases=cases))
    files=[sp,ip,ep,Path(__file__),ROOT/'docs/core/test/test_topic13_patch_position_sensitivity.py']
    result=dict(major_result_id='T13_PATCH_POSITION_SENSITIVITY',topic='0.13',closure_level='PARTIAL',
        what_is_closed='Actual detector ratio sensitivity under nine fixed coordinate offsets measured',
        equation_or_mapping='r=sum ON/sum OFF; delta r=r-mean(r at delay<-.5ps); compare fixed patch offsets',
        units='dimensionless ratios and pixels',derivation_class='external-data deterministic readout stress test',
        observable='patch detector ratio, not phonon population',data_role='EXTERNAL_DATA_DIAGNOSTIC',rows=rows,
        verification_status='FIXED_OFFSET_CURVES_RECORDED',controlling_blocker='registration_response_and_detector_covariance',
        open_blockers=['offsets_not_statistical_error_model','physical_scattering_scale','mode_inversion','UET_mapping'],
        dependency_unlocked=[],full_core_unlock=False,global_claim_promotion=False,
        claim_boundary='Offsets are stress scenarios, not calibrated uncertainty bounds. No optimum selected, pixel filled, image shifted, smoothing, fit or holdout.',
        array_export_hashes=array_hashes,evidence_artifacts=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha256(p.read_bytes()).hexdigest()) for p in files])
    (ROOT/'docs/core/07_artifacts/topic13/t13_patch_position_sensitivity.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps([dict(member=r['member'],cases=[{k:v for k,v in s.items() if k!='probes'} for s in r['cases']]) for r in rows]))


if __name__=='__main__':main()
