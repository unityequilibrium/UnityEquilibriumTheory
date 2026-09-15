"""Exploratory whole-detector cut sensitivity; not a thermal observable."""
import json
from pathlib import Path
import numpy as np
from docs.scripts.audit.audit_topic13_ued_source_acquisition import digest

ROOT = Path(__file__).resolve().parents[3]


def compare(on, off, delay):
    on,off,delay = np.asarray(on,float),np.asarray(off,float),np.asarray(delay,float)
    if on.shape != off.shape or on.ndim != 2 or on.shape[0] != 2 or delay.shape != (on.shape[1],):
        raise ValueError('two paired cuts and one delay axis required')
    if not all(np.isfinite(x).all() for x in (on,off,delay)) or np.any(off <= 0):
        raise ValueError('finite data and positive denominators required')
    baseline=delay < 0
    if not baseline.any() or not (~baseline).any() or np.any(np.diff(delay)<=0):
        raise ValueError('ordered pre/post rows required')
    ratio=on/off
    pooled=on.sum(axis=0)/off.sum(axis=0)
    response=ratio-ratio[:,baseline].mean(axis=1)[:,None]
    pooled_response=pooled-pooled[baseline].mean()
    diff=response[0]-response[1]
    return dict(delay_ps=delay.tolist(),baseline_rule='all strictly negative source-relative delays; exploratory, not author fit',
        baseline_rows=np.flatnonzero(baseline).tolist(),raw_ratio=ratio.tolist(),baseline_subtracted_ratio=response.tolist(),
        pooled_baseline_subtracted_ratio=pooled_response.tolist(),
        cut_difference=diff.tolist(),max_abs_cut_difference=float(abs(diff).max()),
        rms_cut_difference=float(np.sqrt(np.mean(diff**2))),
        cut_response_peak_to_peak=np.ptp(response,axis=1).tolist(),
        max_abs_pooling_departure_from_each_cut=np.max(abs(response-pooled_response),axis=1).tolist(),
        max_abs_pooled_vs_unweighted_ratio=float(abs(pooled-ratio.mean(axis=0)).max()))


def main():
    source=ROOT/'docs/core/07_artifacts/topic13/t13_ued_raw_structure_audit.json'
    pooling=ROOT/'docs/core/07_artifacts/topic13/t13_ued_cut_pooling_audit.json'
    for path in (source,pooling):
        for file,h in json.loads(path.read_text())['evidence_hashes'].items():
            if digest(ROOT/file)!=h: raise ValueError('stale evidence')
    tables=json.loads(source.read_text())['tables'][:2]
    on,off,delays=[],[],[]
    for table in tables:
        rows=table['rows']
        for r in rows:
            for role in ('imagesON','imagesOFF'):
                s=r[role]
                if s['shape'] != [512,512] or s['finite_count'] != s['count']:
                    raise ValueError('whole-detector summaries require common complete support')
        on.append([r['imagesON']['mean'] for r in rows])
        off.append([r['imagesOFF']['mean'] for r in rows])
        delays.append((np.array([r['LTS_position'] for r in rows])-rows[7]['LTS_position'])*6.666)
    if not np.array_equal(*delays): raise ValueError('unaligned time axes')
    result=compare(on,off,delays[0])
    files=[source,pooling,Path(__file__),ROOT/'docs/core/test/test_topic13_ued_cut_signal.py']
    artifact=dict(major_result_id='T13_RAW_CUT_SIGNAL_SENSITIVITY',topic='0.13',closure_level='PARTIAL',
        what_is_closed=['Whole-detector ON/OFF ratios compared separately and under source-style image pooling'],
        equation_or_mapping='Arithmetic detector mean ratios and pre-zero baseline subtraction; no new physical equation',
        units='dimensionless intensity ratios; delay ps from pinned source conversion',derivation_class='EXPLORATORY_DESCRIPTIVE_DATA_ANALYSIS',
        observable='whole raw detector intensity; mixes direct beam, Bragg and diffuse components',data_role='EXTERNAL_COMPARISON_NOT_CALIBRATION',
        verification_status='CUT_DIFFERENCE_MEASURED_CAUSE_UNRESOLVED',result=result,
        open_blockers=['acquisition independence/gain/drift','cut-resolved geometric processing and mode observable','independent Phi calibration'],
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in files},
        dependency_unlocked=['cut-resolved robustness analysis only'],full_core_unlock=False,claim_promotion=False,
        claim_boundary='No hypothesis threshold or significance claim. Not covariance, error bars, causal leakage, TTG response, temperature or heat. Baseline selected for exploratory inspection; no fit or holdout read.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_ued_cut_signal_audit.json').write_text(json.dumps(artifact,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k.startswith(('max_','rms_','cut_response'))},indent=2))


if __name__=='__main__': main()
