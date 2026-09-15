"""Source-centered raw-image moments; no fitting, shifting or thermal mapping."""
import gzip
import json
import zipfile
from pathlib import Path
import numpy as np
from docs.scripts.audit.ued_pickle_static import read_inert
from docs.scripts.audit.audit_topic13_ued_source_acquisition import digest

ROOT = Path(__file__).resolve().parents[3]


def position(image, radius, center=(242,247)):
    if image.shape != (512,512) or not np.isfinite(image).all() or np.any(image<0):
        raise ValueError('finite nonnegative raw image required')
    y,x=center
    if type(radius) is not int or radius<=0 or not (radius<=y<=512-radius and radius<=x<=512-radius):
        raise ValueError('invalid ROI')
    roi=image[y-radius:y+radius,x-radius:x+radius]
    total=roi.sum(dtype=float)
    if total<=0: raise ValueError('empty beam ROI')
    yy,xx=np.indices(roi.shape)
    cy=float((roi*(yy+y-radius)).sum()/total)
    cx=float((roi*(xx+x-radius)).sum()/total)
    py,px=np.unravel_index(np.argmax(image),image.shape)
    boundary=np.zeros(roi.shape,bool);boundary[[0,-1],:]=True;boundary[:,[0,-1]]=True
    return dict(centroid_row_col=[cy,cx],roi_sum=float(total),
        boundary_intensity_fraction=float(roi[boundary].sum()/total),
        global_argmax_row_col=[int(py),int(px)],global_argmax_in_roi=bool(y-radius<=py<y+radius and x-radius<=px<x+radius))


def main():
    source=ROOT/'docs/core/07_artifacts/topic13/t13_ued_raw_structure_audit.json'
    acquisition=ROOT/'docs/core/07_artifacts/topic13/t13_ued_raw_archive_audit.json'
    notebook=ROOT/'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ued_treat_pickle_7f7036b.ipynb'
    for p in (source,acquisition):
        for f,h in json.loads(p.read_text())['evidence_hashes'].items():
            if digest(ROOT/f)!=h: raise ValueError('stale evidence')
    cells=json.loads(notebook.read_text())['cells']
    if 'np.array([242,247])' not in ''.join(cells[1]['source']) or 's_roi=15' not in ''.join(cells[13]['source']):
        raise ValueError('source ROI changed')
    tables=json.loads(source.read_text())['tables'][:2]
    required={r[k]['sha256'] for t in tables for r in t['rows'] for k in ('imagesON','imagesOFF')}
    metrics={}
    def sink(image,record):
        if record['sha256'] in required:
            metrics[record['sha256']]={str(radius):position(image,radius) for radius in (10,15,20)}
    raw=ROOT/'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ued_14760926_raw_sorted.zip'
    with zipfile.ZipFile(raw) as z:
        for t in tables:
            with z.open(t['member']) as f:
                with gzip.GzipFile(fileobj=f) as g:
                    read_inert(g,numeric_sink=sink)
                    if g.read(1): raise ValueError('trailing pickle data')
                if f.read(1): raise ValueError('trailing gzip data')
    if set(metrics)!=required: raise ValueError('missing image metrics')
    rows=[dict(member=t['member'],rows=[dict(row_id=r['row_id'],source_row_sha256=r['row_sha256'],
          ON=metrics[r['imagesON']['sha256']],OFF=metrics[r['imagesOFF']['sha256']]) for r in t['rows']]) for t in tables]
    summary={}
    for radius in ('10','15','20'):
        on=np.array([[r['ON'][radius]['centroid_row_col'] for r in t['rows']] for t in rows])
        off=np.array([[r['OFF'][radius]['centroid_row_col'] for r in t['rows']] for t in rows])
        summary[radius]=dict(max_between_cut_OFF_distance_px=float(np.linalg.norm(off[0]-off[1],axis=1).max()),
            max_between_cut_ON_distance_px=float(np.linalg.norm(on[0]-on[1],axis=1).max()),
            max_ON_OFF_distance_px_by_cut=np.linalg.norm(on-off,axis=2).max(axis=1).tolist(),
            all_global_maxima_in_roi=all(r[k][radius]['global_argmax_in_roi'] for t in rows for r in t['rows'] for k in ('ON','OFF')),
            max_boundary_intensity_fraction=max(r[k][radius]['boundary_intensity_fraction'] for t in rows for r in t['rows'] for k in ('ON','OFF')))
    files=[source,acquisition,notebook,Path(__file__),ROOT/'docs/scripts/audit/ued_pickle_static.py',ROOT/'docs/core/test/test_topic13_ued_beam_position.py']
    artifact=dict(major_result_id='T13_SOURCE_CENTERED_POSITION_SENSITIVITY',topic='0.13',closure_level='PARTIAL',
        what_is_closed=['Raw intensity centroids measured near source nominal zero-order position, with fixed ROI sensitivity'],
        equation_or_mapping='Intensity-weighted raw pixel coordinates, not source Voigt fit or physical beam displacement',
        units='pixels and dimensionless boundary intensity fraction',derivation_class='EXPLORATORY_IMAGE_MOMENTS',
        observable='raw detector intensity distribution near source nominal beam center',data_role='EXTERNAL_COMPARISON_NOT_CALIBRATION',
        verification_status='MOMENTS_MEASURED_REGISTRATION_OPEN',nominal_center_row_col=[242,247],
        radius_policy='15 from source; 10/20 exploratory sensitivity declared before running; all retained',rows=rows,summary=summary,
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in files},
        open_blockers=['centroid/background/shape ambiguity','source Voigt registration replication and uncertainty','reciprocal geometry and Phi mapping'],
        dependency_unlocked=['registration-method comparison only'],full_core_unlock=False,claim_promotion=False,
        claim_boundary='Moment differences can reflect shape/background, not pure translation. No image shifted, no background removed or fit, no holdout, physical alignment correction, heat or alpha claim.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_ued_beam_position_audit.json').write_text(json.dumps(artifact,indent=2,allow_nan=False)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__': main()
