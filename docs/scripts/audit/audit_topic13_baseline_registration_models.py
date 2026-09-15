"""Baseline-only coordinate fits with leave-one-peak-out diagnostics; no image warp."""
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]


def design(points,kind):
    p=np.asarray(points,dtype=float)-256.
    if p.ndim!=2 or p.shape[1]!=2 or not np.isfinite(p).all():raise ValueError('finite row-column points required')
    count={'translation':2,'similarity':4,'affine':6}[kind]
    a=np.zeros((len(p)*2,count));a[::2,0]=1;a[1::2,1]=1
    if kind=='similarity':
        a[::2,2]=p[:,0];a[::2,3]=-p[:,1];a[1::2,2]=p[:,1];a[1::2,3]=p[:,0]
    if kind=='affine':
        a[::2,2:4]=p;a[1::2,4:6]=p
    return a


def fit_map(nominal,measured,kind):
    nominal=np.asarray(nominal,dtype=float);measured=np.asarray(measured,dtype=float)
    if nominal.shape!=measured.shape or not np.isfinite(measured).all():raise ValueError('matching finite points required')
    a=design(nominal,kind);values=np.linalg.lstsq(a,(measured-nominal).ravel(),rcond=None)
    if values[2]!=a.shape[1]:raise ValueError('unidentified coordinate model')
    return values[0]


def predict(points,parameters,kind):
    p=np.asarray(points,dtype=float)
    return p+(design(p,kind)@parameters).reshape(-1,2)


def main():
    source_path=ROOT/'docs/core/07_artifacts/topic13/t13_multibragg_positions.json'
    source=json.loads(source_path.read_text())
    for e in source['evidence_artifacts']:
        if sha256((ROOT/e['path']).read_bytes()).hexdigest()!=e['sha256']:raise ValueError('upstream drift')
    rows=[]
    for table in source['rows']:
        p=np.array([r['nominal_yx'] for r in table['probes']]);results={}
        for radius in ('4','8'):
            if any(r['radii'][radius]['status']!='MEASURED_NOT_CALIBRATED' for r in table['probes']):raise ValueError('incomplete peak set')
            observed=np.array([r['radii'][radius]['centroid_yx'] for r in table['probes']]);models={}
            for kind in ('translation','similarity','affine'):
                parameters=fit_map(p,observed,kind)
                residuals=observed-predict(p,parameters,kind)
                loo=[]
                for i in range(len(p)):
                    keep=np.arange(len(p))!=i
                    loo.append((observed[i]-predict(p[i:i+1],fit_map(p[keep],observed[keep],kind),kind)[0]).tolist())
                norms=np.linalg.norm(loo,axis=1)
                models[kind]=dict(parameters=parameters.tolist(),training_residual_yx=residuals.tolist(),
                    training_rms_pixels=float(np.sqrt(np.mean(np.sum(residuals**2,axis=1)))),
                    leave_one_peak_out_residual_yx=loo,loo_rms_pixels=float(np.sqrt(np.mean(norms**2))),loo_max_pixels=float(norms.max()))
            results[radius]=models
        disagreement={kind:float(np.max(np.linalg.norm(predict(p,np.array(results['4'][kind]['parameters']),kind)-predict(p,np.array(results['8'][kind]['parameters']),kind),axis=1))) for kind in results['4']}
        rows.append(dict(member=table['member'],models_by_radius=results,radius_model_disagreement_max_pixels=disagreement))
    files=[source_path,Path(__file__),ROOT/'docs/core/test/test_topic13_baseline_registration_models.py']
    output=dict(major_result_id='T13_BASELINE_REGISTRATION_MODEL_COMPARISON',topic='0.13',closure_level='PARTIAL',
        what_is_closed='Baseline-only translation/similarity/affine centroid fits and leave-one-peak-out residuals measured',
        equation_or_mapping='measured pixel position=nominal+linear coordinate correction; centered at(256,256)',
        units='translations/residuals pixels; linear slopes dimensionless',derivation_class='empirical baseline detector-coordinate diagnostic',
        observable='baseline centroid coordinates, not thermal target',data_role='EXTERNAL_BASELINE_DIAGNOSTIC_FIT_NOT_ALPHA',rows=rows,
        verification_status='MODELS_AND_INTERNAL_LOO_RECORDED',controlling_blocker='centroid_shape_bias_and_physical_registration_uncertainty',
        open_blockers=['symmetry_processing_dependence','nonindependent_peak_residuals','finite_patch_forward_model','UET_mapping'],
        dependency_unlocked=[],full_core_unlock=False,global_claim_promotion=False,
        claim_boundary='No model automatically selected or applied. Leave-one-peak-out is internal, not independent external validation or a statistical uncertainty bound. No holdout read.',
        evidence_artifacts=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha256(p.read_bytes()).hexdigest()) for p in files])
    (ROOT/'docs/core/07_artifacts/topic13/t13_baseline_registration_models.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    print(json.dumps([dict(member=r['member'],radii={rad:{m:(v['loo_rms_pixels'],v['loo_max_pixels']) for m,v in ms.items()} for rad,ms in r['models_by_radius'].items()},disagreement=r['radius_model_disagreement_max_pixels']) for r in rows]))


if __name__=='__main__':main()
