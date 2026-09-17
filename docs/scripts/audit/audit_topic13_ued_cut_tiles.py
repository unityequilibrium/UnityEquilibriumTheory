"""Fixed-grid raw detector sensitivity without geometric/thermal relabeling."""
import gzip
import json
import zipfile
from pathlib import Path
import numpy as np
from docs.scripts.audit.ued_pickle_static import read_inert
from docs.scripts.audit.audit_topic13_ued_source_acquisition import digest
from docs.scripts.audit.audit_topic13_ued_cut_signal import compare

ROOT = Path(__file__).resolve().parents[3]
# Fixed before inspecting tile results; zero-based [row, column], half-open bounds.
BOUNDS = [(y,y+128,x,x+128) for y in range(0,512,128) for x in range(0,512,128)]


def tile_totals(image):
    if image.shape != (512,512) or not np.isfinite(image).all():
        raise ValueError('complete finite 512x512 support required')
    totals=np.array([image[a:b,c:d].sum(dtype=np.float64) for a,b,c,d in BOUNDS])
    if not np.isclose(totals.sum(),image.sum(dtype=np.float64),rtol=1e-12,atol=0):
        raise ValueError('partition did not conserve detector sum')
    return totals


def main():
    inventory=ROOT/'docs/core/07_artifacts/topic13/t13_ued_raw_structure_audit.json'
    previous=ROOT/'docs/core/07_artifacts/topic13/t13_ued_cut_signal_audit.json'
    acquisition=ROOT/'docs/core/07_artifacts/topic13/t13_ued_raw_archive_audit.json'
    for p in (inventory,previous,acquisition):
        for f,h in json.loads(p.read_text())['evidence_hashes'].items():
            if digest(ROOT/f)!=h: raise ValueError('stale evidence')
    tables=json.loads(inventory.read_text())['tables'][:2]
    required={r[role]['sha256'] for t in tables for r in t['rows'] for role in ('imagesON','imagesOFF')}
    metrics={}
    def sink(image,record):
        if record['sha256'] in required:
            metrics[record['sha256']]=tile_totals(image)
    archive_path=ROOT/'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ued_14760926_raw_sorted.zip'
    with zipfile.ZipFile(archive_path) as z:
        for t in tables:
            with z.open(t['member']) as f:
                with gzip.GzipFile(fileobj=f) as g:
                    read_inert(g,numeric_sink=sink)
                    if g.read(1): raise ValueError('trailing pickle payload')
                if f.read(1): raise ValueError('trailing gzip payload')
    if set(metrics)!=required: raise ValueError('missing required source arrays')
    on=np.array([[metrics[r['imagesON']['sha256']] for r in t['rows']] for t in tables])
    off=np.array([[metrics[r['imagesOFF']['sha256']] for r in t['rows']] for t in tables])
    delay=np.array([(np.array([r['LTS_position'] for r in t['rows']])-t['rows'][7]['LTS_position'])*6.666 for t in tables])
    if not np.array_equal(delay[0],delay[1]): raise ValueError('unaligned cuts')
    whole=compare(on.sum(axis=2),off.sum(axis=2),delay[0])
    old=json.loads(previous.read_text())['result']
    if not np.allclose(whole['raw_ratio'],old['raw_ratio'],rtol=1e-12,atol=0):
        raise ValueError('tile sums fail whole-detector reconstruction')
    results=[]
    for i,bounds in enumerate(BOUNDS):
        entry=dict(tile_id=i,bounds_y0_y1_x0_x1=list(bounds),
                   off_intensity_fraction_by_cut=(off[:,:,i].sum(axis=1)/off.sum(axis=(1,2))).tolist())
        if np.any(off[:,:,i]<=0):
            entry.update(status='UNDEFINED_NONPOSITIVE_DENOMINATOR',result=None)
        else:
            entry.update(status='DESCRIPTIVE_ONLY',result=compare(on[:,:,i],off[:,:,i],delay[0]))
        results.append(entry)
    files=[inventory,previous,acquisition,Path(__file__),ROOT/'docs/scripts/audit/ued_pickle_static.py',
           ROOT/'docs/scripts/audit/audit_topic13_ued_cut_signal.py',ROOT/'docs/core/test/test_topic13_ued_cut_tiles.py']
    artifact=dict(major_result_id='T13_RAW_SPATIAL_CUT_SENSITIVITY',topic='0.13',closure_level='PARTIAL',
        what_is_closed=['Fixed 4x4 raw-pixel partition compared for both cuts; whole-detector sums reconstructed'],
        equation_or_mapping='Disjoint detector sums and ON/OFF ratios only; no physical mode attribution',
        units='pixel coordinates and dimensionless ratios; raw intensity units unverified',
        derivation_class='EXPLORATORY_FIXED_GRID_DIAGNOSTIC',observable='mixed raw detector regions',data_role='EXTERNAL_COMPARISON_NOT_CALIBRATION',
        verification_status='SPATIAL_DIFFERENCES_MEASURED_PHYSICAL_ATTRIBUTION_OPEN',tiles=results,
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in files},
        open_blockers=['cut-dependent alignment/detector response','mode-resolving geometry','acquisition independence','independent Phi coupling'],
        dependency_unlocked=['geometry-aware cut comparison only'],full_core_unlock=False,claim_promotion=False,
        claim_boundary='Not Bragg/diffuse separation, thermal response, covariance, significance, causal leakage or calibration. All 16 tiles reported, no selected-region fit, clipping, interpolation or holdout.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_ued_cut_tiles_audit.json').write_text(json.dumps(artifact,indent=2,allow_nan=False)+'\n')
    print(json.dumps([dict(tile=t['tile_id'],bounds=t['bounds_y0_y1_x0_x1'],off_fraction=t['off_intensity_fraction_by_cut'],max_difference=None if t['result'] is None else t['result']['max_abs_cut_difference']) for t in results],indent=2))


if __name__=='__main__': main()
