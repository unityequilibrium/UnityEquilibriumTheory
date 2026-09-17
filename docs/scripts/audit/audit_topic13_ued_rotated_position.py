"""Controlled rotation comparator with unchanged uniform residual weighting."""
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
from docs.scripts.audit.audit_topic13_ued_voigt_position import PARAMETERS

ROOT=Path(__file__).resolve().parents[3]


def rotated_profile(p,yy,xx):
    dy,dx=yy-p[1],xx-p[2];c,s=np.cos(p[8]),np.sin(p[8])
    return p[7]+p[0]*voigt_profile(c*dy+s*dx,p[3],p[5])*voigt_profile(-s*dy+c*dx,p[4],p[6])


def fit_rotated(roi,base,angle=np.pi,origin=(227,232)):
    roi=np.asarray(roi,float)
    if roi.ndim!=2 or min(roi.shape)<3 or not np.isfinite(roi).all() or roi.min()<0 or roi.max()<=0:
        raise ValueError('finite nonnegative ROI required')
    yy,xx=np.indices(roi.shape,dtype=float);yy+=origin[0];xx+=origin[1]
    scale=float(roi.max());target=roi/scale
    p0=[base[k] for k in PARAMETERS]+[float(angle)]
    fit=least_squares(lambda p:(rotated_profile(p,yy,xx)-target).ravel(),p0,
        bounds=([0,yy.min(),xx.min(),0,0,0,0,0,0],[np.inf,yy.max(),xx.max(),10,10,1e3,1e3,np.inf,2*np.pi]),
        method='trf',x_scale='jac',max_nfev=1000,ftol=1e-10,xtol=1e-10,gtol=1e-10)
    return dict(initial_angle_rad=float(angle),success=bool(fit.success),termination_status=int(fit.status),nfev=int(fit.nfev),
        parameters_normalized=dict(zip(PARAMETERS+['angle_rad'],fit.x.tolist())),intensity_scale=scale,
        center_row_col=fit.x[1:3].tolist(),relative_residual_l2=float(np.linalg.norm(fit.fun)/np.linalg.norm(target)),
        active_bounds=fit.active_mask.tolist(),cost=float(fit.cost))


def main():
    basepath=ROOT/'docs/core/07_artifacts/topic13/t13_ued_voigt_position_audit.json'
    inventory=ROOT/'docs/core/07_artifacts/topic13/t13_ued_raw_structure_audit.json'
    acquisition=ROOT/'docs/core/07_artifacts/topic13/t13_ued_raw_archive_audit.json'
    for path in (basepath,inventory,acquisition):
        for f,h in json.loads(path.read_text())['evidence_hashes'].items():
            if digest(ROOT/f)!=h: raise ValueError('stale evidence')
    base=json.loads(basepath.read_text());tables=json.loads(inventory.read_text())['tables'][:2]
    required={r[k]['sha256'] for t in tables for r in t['rows'] for k in ('imagesON','imagesOFF')}
    rois={}
    def sink(image,record):
        if record['sha256'] in required: rois[record['sha256']]=image[227:257,232:262].copy()
    raw=ROOT/'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ued_14760926_raw_sorted.zip'
    with zipfile.ZipFile(raw) as z:
        for t in tables:
            with z.open(t['member']) as f:
                with gzip.GzipFile(fileobj=f) as g:
                    read_inert(g,numeric_sink=sink)
                    if g.read(1): raise ValueError('trailing pickle')
                if f.read(1): raise ValueError('trailing gzip')
    if set(rois)!=required: raise ValueError('missing ROI')
    rows=[];allfits=[];center_changes=[];residual_ratios=[];start_spreads=[]
    for t,bt in zip(tables,base['rows']):
        out=[]
        for r,b in zip(t['rows'],bt['rows']):
            if r['row_id']!=b['row_id']: raise ValueError('unpaired base fits')
            row=dict(row_id=r['row_id'])
            for name,role in [('ON','imagesON'),('OFF','imagesOFF')]:
                prior=b[name][0]
                fits=[fit_rotated(rois[r[role]['sha256']],prior['parameters_normalized'],angle=a) for a in (np.pi,np.pi-.2,np.pi+.2)]
                row[name]=fits;allfits.extend(fits)
                center_changes.append(float(np.linalg.norm(np.array(fits[0]['center_row_col'])-prior['centroid_row_col'])))
                residual_ratios.append(fits[0]['relative_residual_l2']/prior['relative_residual_l2'])
                start_spreads.extend(float(np.linalg.norm(np.array(f['center_row_col'])-fits[0]['center_row_col'])) for f in fits[1:])
            out.append(row)
            if len(out)%10==0: print(t['member'],'rows',len(out),flush=True)
        rows.append(dict(member=t['member'],rows=out))
    summary=dict(fit_count=len(allfits),failed_optimizer_count=sum(not f['success'] for f in allfits),
        primary_relative_residual_l2_range=[min(r[k][0]['relative_residual_l2'] for t in rows for r in t['rows'] for k in ('ON','OFF')),max(r[k][0]['relative_residual_l2'] for t in rows for r in t['rows'] for k in ('ON','OFF'))],
        rotated_to_unrotated_residual_ratio_range=[min(residual_ratios),max(residual_ratios)],
        max_center_change_from_unrotated_px=max(center_changes),max_angle_start_center_disagreement_px=max(start_spreads))
    for k in ('ON','OFF'):
        c=np.array([[r[k][0]['center_row_col'] for r in t['rows']] for t in rows])
        summary['max_between_cut_'+k+'_distance_px']=float(np.linalg.norm(c[0]-c[1],axis=1).max())
    files=[basepath,inventory,acquisition,Path(__file__),ROOT/'docs/scripts/audit/audit_topic13_ued_voigt_position.py',ROOT/'docs/scripts/audit/ued_pickle_static.py',ROOT/'docs/core/test/test_topic13_ued_rotated_position.py']
    result=dict(major_result_id='T13_CONTROLLED_ROTATION_PROFILE_COMPARISON',topic='0.13',closure_level='PARTIAL',
        what_is_closed=['Effect of adding a rotation degree of freedom tested while preserving uniform residual weighting'],
        equation_or_mapping='Separable Voigt profiles in rotated centered pixel coordinates plus constant offset',
        units='pixels/radians and normalized detector intensity',derivation_class='INSTRUMENT_MODEL_COMPARATOR',
        observable='nominal zero-order detector profile',data_role='EXTERNAL_COMPARISON_NOT_CALIBRATION',verification_status='ROTATION_COMPARISON_PHYSICAL_ACCURACY_OPEN',
        rows=rows,summary=summary,solver=dict(name='SciPy least_squares TRF',version=scipy.__version__,weights='uniform unchanged',
          primary_start='unrotated solution with angle pi; pi-.2 and pi+.2 retained as checks',
          source_difference='Published rotated helper uses weights 1/sqrt(1+raw intensity); not used here to isolate rotation'),
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in files},
        open_blockers=['remaining profile/background residual','detector covariance and physical registration accuracy','geometry and independent Phi calibration'],
        dependency_unlocked=['instrument model comparison only'],full_core_unlock=False,claim_promotion=False,
        claim_boundary='Nested-model in-sample improvement alone is not validation. No physical angles inferred, fit uncertainty, image shifting, weighted source replication, holdout or thermal claim.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_ued_rotated_position_audit.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
