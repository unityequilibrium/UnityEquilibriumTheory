"""Export numeric arrays and quantify changing-support effects; no population fit."""

import gzip
import hashlib
import json
from pathlib import Path
import zipfile

import numpy as np

from docs.scripts.audit.ued_pickle_static import read_inert
from docs.scripts.audit.audit_topic13_ued_numeric_inventory import summarize_table
from docs.scripts.audit.audit_topic13_ued_source_acquisition import digest

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT/'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw'


def support_signals(on, off, baseline):
    on, off = np.asarray(on), np.asarray(off)
    baseline = np.asarray(baseline, dtype=bool)
    if on.shape != off.shape or on.ndim != 3 or baseline.shape != (len(on),) or not baseline.any():
        raise ValueError('paired image stack and nonempty baseline required')
    masks = np.isfinite(on) & np.isfinite(off)
    common = masks.all(axis=0)
    if not common.any():
        raise ValueError('no common finite support')
    dynamic, fixed = [], []
    for a, b, mask in zip(on, off, masks):
        if not mask.any() or b[mask].sum() <= 0 or b[common].sum() <= 0:
            raise ValueError('positive resolved denominator required')
        dynamic.append(float(a[mask].sum()/b[mask].sum()))
        fixed.append(float(a[common].sum()/b[common].sum()))
    dynamic, fixed = np.asarray(dynamic), np.asarray(fixed)
    return common, masks, dict(
        pairwise_finite_counts=masks.sum(axis=(1, 2)).tolist(), common_finite_count=int(common.sum()),
        dynamic_ratio=dynamic.tolist(), common_ratio=fixed.tolist(),
        dynamic_baseline_subtracted=(dynamic-dynamic[baseline].mean()).tolist(),
        common_baseline_subtracted=(fixed-fixed[baseline].mean()).tolist(),
        baseline_indices=np.flatnonzero(baseline).tolist(),
        support_choice_max_difference=float(np.max(abs((dynamic-dynamic[baseline].mean())-(fixed-fixed[baseline].mean())))))


def main():
    previous_path = ROOT/'docs/core/07_artifacts/topic13/t13_ued_numeric_inventory_audit.json'
    previous = json.loads(previous_path.read_text(encoding='utf-8'))
    for relative, expected in previous['evidence_hashes'].items():
        if digest(ROOT/relative) != expected:
            raise ValueError('numeric inventory must be regenerated: '+relative)
    acquisition = json.loads((ROOT/'docs/core/07_artifacts/topic13/t13_ued_source_acquisition_audit.json').read_text(encoding='utf-8'))
    for relative, expected in acquisition['evidence_hashes'].items():
        if digest(ROOT/relative) != expected:
            raise ValueError('source acquisition mismatch')
    destination = RAW/'ued_numeric_arrays'
    destination.mkdir(exist_ok=True)
    exported = {}

    def save_array(array, record):
        if array.shape != (512, 512):
            return
        name = record['sha256']
        path = destination/(name+'.npy')
        if path.exists():
            loaded = np.load(path, allow_pickle=False)
            if loaded.shape != array.shape or loaded.dtype != array.dtype or loaded.tobytes(order=record['order']) != array.tobytes(order=record['order']):
                raise ValueError('existing export differs from source')
        else:
            np.save(path, array, allow_pickle=False)
        exported[name] = dict(path=str(path.relative_to(ROOT)).replace('\\', '/'), sha256=digest(path))

    results = []
    with zipfile.ZipFile(RAW/'ued_14760926_processed.zip') as archive:
        for old in previous['tables']:
            member = old['member']
            with archive.open(member) as stream:
                with gzip.GzipFile(fileobj=stream) as g:
                    root, _ = read_inert(g, numeric_sink=save_array)
                    if g.read(1): raise ValueError('trailing data')
                if stream.read(1): raise ValueError('trailing gzip data')
            table = summarize_table(root, member, time_index_base=1)
            if [r['row_sha256'] for r in table['rows']] != [r['row_sha256'] for r in old['rows']]:
                raise ValueError('row identity changed during export')
            on = np.stack([np.load(ROOT/exported[r['imgON']['sha256']]['path'], allow_pickle=False) for r in table['rows']])
            off = np.stack([np.load(ROOT/exported[r['imgOFF']['sha256']]['path'], allow_pickle=False) for r in table['rows']])
            delay = np.asarray([r['delay_ps'] for r in table['rows']])
            common, masks, signals = support_signals(on, off, delay < -.5)
            mask_path = destination/(table['scan_label']+'_validity.npz')
            np.savez_compressed(mask_path, common=common, pairwise=masks, delay_ps=delay)
            results.append(dict(member=member, signals=signals,
                                row_ids=[r['row_id'] for r in table['rows']], delay_ps=delay.tolist(),
                                mask_export={'path': str(mask_path.relative_to(ROOT)).replace('\\', '/'), 'sha256': digest(mask_path)}))
    files = [previous_path, Path(__file__), ROOT/'docs/scripts/audit/ued_pickle_static.py',
             ROOT/'docs/core/test/test_topic13_ued_mask_support.py']
    artifact = dict(major_result_id='T13_UED_NUMERIC_EXPORT_AND_SUPPORT_SENSITIVITY', topic='0.13', closure_level='PARTIAL',
                    what_is_closed=['Lossless numeric image export with source-byte identity', 'Common and pairwise masks with support-sensitivity diagnostic'],
                    equation_or_mapping='R(t)=sum_ON(mask)/sum_OFF(mask); baseline mean removed separately for each fixed mask rule',
                    units={'ratio': '1', 'delay': 'ps'}, derivation_class='detector_support_diagnostic',
                    observable='whole-detector ratio, not diffuse-only or mode population', data_role='EXTERNAL_DATA_DIAGNOSTIC',
                    verification_status='EXPORTED_WITH_SUPPORT_DEPENDENCE_DISCLOSED',
                    policy={'baseline': 'delay < -0.5 ps, from pinned author plotting convention',
                            'region': 'all finite pixels; includes Bragg peaks', 'common_mask': 'intersection across all ON/OFF frames per scan',
                            'fitting': False, 'pixel_fill': False, 'uncertainty': 'Not supplied by deterministic support spread'},
                    results=results, array_exports=exported,
                    open_blockers=['physical region/forward scattering map', 'preprocessing covariance', 'unobserved modes', 'Phi source coefficient'],
                    dependency_unlocked=['mask-aware detector analysis only'], full_core_unlock=False, claim_promotion=False,
                    evidence_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in files},
                    claim_boundary='Support comparison is not a heat signal, confidence interval, lifetime, mode occupation or alpha calibration.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_ued_mask_support_audit.json').write_text(json.dumps(artifact, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps([dict(member=r['member'], common_pixels=r['signals']['common_finite_count'],
                           pairwise_min=min(r['signals']['pairwise_finite_counts']), pairwise_max=max(r['signals']['pairwise_finite_counts']),
                           support_difference=r['signals']['support_choice_max_difference']) for r in results], indent=2))


if __name__ == '__main__':
    main()
