"""Independent solver for the source separable Voigt form; not lmfit replication."""
import gzip
import json
import zipfile
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import least_squares
from scipy.special import voigt_profile
from docs.scripts.audit.ued_pickle_static import read_inert
from docs.scripts.audit.audit_topic13_ued_source_acquisition import digest

ROOT=Path(__file__).resolve().parents[3]
PARAMETERS=['amplitude','row','column','sigma_row','sigma_column','gamma_row','gamma_column','offset']


def profile(p,yy,xx):
    return p[7]+p[0]*voigt_profile(yy-p[1],p[3],p[5])*voigt_profile(xx-p[2],p[4],p[6])


def fit_roi(roi,origin=(227,232),start='source'):
    roi=np.asarray(roi,float)
    if roi.ndim!=2 or min(roi.shape)<3 or not np.isfinite(roi).all() or roi.min()<0 or roi.max()<=0:
        raise ValueError('finite nonnegative nonempty ROI required')
    yy,xx=np.indices(roi.shape,dtype=float); yy+=origin[0];xx+=origin[1]
    scale=float(roi.max());target=roi/scale
    if start=='source': cy,cx=float(yy.mean()),float(xx.mean())
    elif start=='peak':
        iy,ix=np.unravel_index(np.argmax(roi),roi.shape);cy,cx=float(yy[iy,ix]),float(xx[iy,ix])
    else: raise ValueError('unknown initial condition')
    p0=[50.,cy,cx,1.,1.,1.,1.,float(target.min())]
    lower=[0.,yy.min(),xx.min(),0.,0.,0.,0.,0.]
    upper=[np.inf,yy.max(),xx.max(),10.,10.,1e3,1e3,np.inf]
    fit=least_squares(lambda p:(profile(p,yy,xx)-target).ravel(),p0,bounds=(lower,upper),
        method='trf',x_scale='jac',max_nfev=1000,ftol=1e-10,xtol=1e-10,gtol=1e-10)
    return dict(start=start,success=bool(fit.success),termination_status=int(fit.status),message=fit.message,
        nfev=int(fit.nfev),parameters_normalized=dict(zip(PARAMETERS,fit.x.tolist())),intensity_scale=scale,
        centroid_row_col=fit.x[1:3].tolist(),relative_residual_l2=float(np.linalg.norm(fit.fun)/np.linalg.norm(target)),
        active_bounds=fit.active_mask.tolist(),cost=float(fit.cost),optimality=float(fit.optimality))


def main():
    inventory=ROOT/'docs/core/07_artifacts/topic13/t13_ued_raw_structure_audit.json'
    acquisition=ROOT/'docs/core/07_artifacts/topic13/t13_ued_raw_archive_audit.json'
    moments=ROOT/'docs/core/07_artifacts/topic13/t13_ued_beam_position_audit.json'
    helper=ROOT/'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ued_find_peak_7f7036b.py'
    for p in (inventory,acquisition,moments):
        for f,h in json.loads(p.read_text())['evidence_hashes'].items():
            if digest(ROOT/f)!=h: raise ValueError('stale evidence')
    text=helper.read_text()
    if not all(t in text for t in ('def voigt_2d(', 'def fit_voigt_2d(', 'voigt_model.fit(z_data.ravel()', 'offset + amplitude * voigt_x * voigt_y')):
        raise ValueError('unreviewed source form')
    tables=json.loads(inventory.read_text())['tables'][:2]
    wanted={r[k]['sha256'] for t in tables for r in t['rows'] for k in ('imagesON','imagesOFF')}
    rois={}
    def sink(image,record):
        if record['sha256'] in wanted: rois[record['sha256']]=image[227:257,232:262].copy()
    raw=ROOT/'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ued_14760926_raw_sorted.zip'
    with zipfile.ZipFile(raw) as z:
        for t in tables:
            with z.open(t['member']) as f:
                with gzip.GzipFile(fileobj=f) as g:
                    read_inert(g,numeric_sink=sink)
                    if g.read(1): raise ValueError('trailing pickle data')
                if f.read(1): raise ValueError('trailing gzip data')
    if set(rois)!=wanted: raise ValueError('missing ROI')
    fitted={}
    for i,(h,roi) in enumerate(rois.items()):
        fitted[h]=[fit_roi(roi,start=s) for s in ('source','peak')]
        if (i+1)%20==0: print('ROI comparisons completed',i+1,flush=True)
    rows=[dict(member=t['member'],rows=[dict(row_id=r['row_id'],ON=fitted[r['imagesON']['sha256']],OFF=fitted[r['imagesOFF']['sha256']]) for r in t['rows']]) for t in tables]
    old=json.loads(moments.read_text())['rows']
    deviations=[];start_delta=[]
    for t,ot in zip(rows,old):
        for r,o in zip(t['rows'],ot['rows']):
            if r['row_id']!=o['row_id']: raise ValueError('moment row mismatch')
            for k in ('ON','OFF'):
                deviations.append(float(np.linalg.norm(np.array(r[k][0]['centroid_row_col'])-o[k]['15']['centroid_row_col'])))
                start_delta.append(float(np.linalg.norm(np.array(r[k][0]['centroid_row_col'])-r[k][1]['centroid_row_col'])))
    summary=dict(roi_count=len(fitted),fit_count=2*len(fitted),failed_optimizer_count=sum(not f['success'] for fs in fitted.values() for f in fs),
        max_start_position_disagreement_px=max(start_delta),max_source_start_vs_raw_moment_distance_px=max(deviations),
        relative_residual_l2_range=[min(f['relative_residual_l2'] for fs in fitted.values() for f in fs),max(f['relative_residual_l2'] for fs in fitted.values() for f in fs)])
    for k in ('ON','OFF'):
        centers=np.array([[r[k][0]['centroid_row_col'] for r in t['rows']] for t in rows])
        summary['max_between_cut_'+k+'_distance_px']=float(np.linalg.norm(centers[0]-centers[1],axis=1).max())
    files=[inventory,acquisition,moments,helper,Path(__file__),ROOT/'docs/scripts/audit/ued_pickle_static.py',ROOT/'docs/core/test/test_topic13_ued_voigt_position.py']
    artifact=dict(major_result_id='T13_VOIGT_POSITION_METHOD_COMPARISON',topic='0.13',closure_level='PARTIAL',
        what_is_closed=['Source separable Voigt form compared with raw moments using independent optimizer and two initial positions'],
        equation_or_mapping='offset + amplitude * V(row-center_row) * V(column-center_column)',
        units='pixels; normalized detector intensity; amplitude normalization is not physical calibration',
        derivation_class='INSTRUMENT_PROFILE_COMPARATOR',observable='nominal zero-order detector profile',data_role='EXTERNAL_COMPARISON_NOT_CALIBRATION',
        verification_status='METHOD_COMPARISON_REGISTRATION_OPEN',summary=summary,rows=rows,
        solver=dict(name='scipy least_squares TRF',version=scipy.__version__,weights='uniform',source_solver='lmfit default; not executed',
                    normalization='divide ROI by its maximum, preserving relative residual objective and rescaling amplitude/offset',
                    selection='source initial position retained for summaries; peak initial result also retained, no best-fit selection'),
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in files},
        open_blockers=['profile misspecification/background and covariance','independent geometry/registration accuracy','physical observable and Phi calibration'],
        dependency_unlocked=['profile residual/model comparison only'],full_core_unlock=False,claim_promotion=False,
        claim_boundary='Optimizer success is not physical accuracy. No uncertainty intervals, image shifting, exact source replication, heat, alpha or holdout. Both starts retained even if disagreeing.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_ued_voigt_position_audit.json').write_text(json.dumps(artifact,indent=2,allow_nan=False)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__': main()
