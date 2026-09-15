"""Extract a strict pandas storage layout as inert numeric summaries only."""

import gzip
import hashlib
import json
from pathlib import Path
import zipfile

import numpy as np

from docs.scripts.audit.ued_pickle_static import Node, read_inert, numeric_summary
from docs.scripts.audit.audit_topic13_ued_source_acquisition import digest

ROOT = Path(__file__).resolve().parents[3]


def expect(node, kind, module, symbol):
    modules = (module, 'numpy._core.multiarray') if module == 'numpy.core.multiarray' else (module,)
    if not isinstance(node, Node) or node.kind != kind or node.args[0] not in [Node('GLOBAL', (m, symbol)) for m in modules]:
        raise ValueError('unexpected inert object layout: '+module+'.'+symbol)
    return node.args[1]


def object_items(node, shape):
    expect(node, 'REDUCE', 'numpy.core.multiarray', '_reconstruct')
    version, actual_shape, dtype, fortran, items = node.state
    params = expect(dtype, 'REDUCE', 'numpy', 'dtype')
    if version != 1 or actual_shape != shape or params[0] != 'O8' or fortran or not isinstance(items, list):
        raise ValueError('unexpected object-array layout')
    if len(items) != int(np.prod(shape)):
        raise ValueError('object array item count differs')
    return items


def scalar(node):
    dtype, buffer = expect(node, 'REDUCE', 'numpy.core.multiarray', 'scalar')
    return numeric_summary((buffer, dtype, (1,), 'C')).args['values'][0]


def summarize_table(root, member, *, time_index_base):
    expect(root, 'NEWOBJ', 'pandas.core.frame', 'DataFrame')
    blocks, axes = expect(root.state['_mgr'], 'REDUCE', 'pandas.core.internals.managers', 'BlockManager')
    index_type, column_state = expect(axes[0], 'REDUCE', 'pandas.core.indexes.base', '_new_Index')
    columns = object_items(column_state['data'], (3,))
    if columns != ['imgON', 'imgOFF', 'delay'] or len(blocks) != 3:
        raise ValueError('unexpected columns')
    _, row_state = expect(axes[1], 'REDUCE', 'pandas.core.indexes.base', '_new_Index')
    if row_state['start'] != 0 or row_state['step'] != 1:
        raise ValueError('unexpected row index')
    count = row_state['stop']
    values = {}
    for index, block in enumerate(blocks):
        array, placement, ndim = expect(block, 'REDUCE', 'pandas._libs.internals', '_unpickle_block')
        if expect(placement, 'REDUCE', 'builtins', 'slice') != (index, index+1, 1) or ndim != 2:
            raise ValueError('unexpected block placement')
        if index < 2:
            images = object_items(array, (1, count))
            if any(not isinstance(i, Node) or i.kind != 'NUMERIC' or i.args['shape'] != [512, 512] for i in images):
                raise ValueError('unexpected image representation')
            values[columns[index]] = [i.args for i in images]
        else:
            if array.kind != 'NUMERIC' or array.args['shape'] != [1, count]:
                raise ValueError('unexpected delay array')
            values['delay'] = array.args['values'][0]
    delay = np.asarray(values['delay'])
    if not np.isfinite(delay).all() or np.any(np.diff(delay) <= 0):
        raise ValueError('delay must be finite and strictly increasing')
    attrs = root.state['attrs']
    t0 = attrs['t0_index']
    if time_index_base not in (0, 1) or type(t0) is not int or not 0 <= t0-time_index_base < count:
        raise ValueError('invalid t0 index')
    zero_row = t0-time_index_base
    rows = [dict(row_id=member+':row:'+str(i), row_index=i, delay_ps=float(delay[i]),
                 imgON=values['imgON'][i], imgOFF=values['imgOFF'][i]) for i in range(count)]
    for row in rows:
        row['row_sha256'] = hashlib.sha256(json.dumps(row, sort_keys=True, allow_nan=False).encode()).hexdigest()
    return dict(member=member, row_count=count, columns=columns,
                delay_range_ps=[float(delay.min()), float(delay.max())],
                source_t0_index=t0, source_t0_index_base=time_index_base,
                source_zero_time_row=zero_row, source_delay_at_zero_time_ps=float(delay[zero_row]),
                exact_zero_delay_indices=np.flatnonzero(delay == 0).tolist(),
                time_origin_reconciled=bool(delay[zero_row] == 0),
                calibration_inverse_angstrom_per_pixel=scalar(attrs['calibration']),
                source_peak_distance_pixels=scalar(attrs['peak_dist']),
                source_zero_order_position=attrs['Zorder_pos'].args['values'],
                scan_label=attrs['scan_number'],
                image_nonfinite_count=sum(r[k]['count']-r[k]['finite_count'] for r in rows for k in ('imgON', 'imgOFF')),
                rows=rows)


def main():
    precursor_path = ROOT/'docs/core/07_artifacts/topic13/t13_ued_source_acquisition_audit.json'
    precursor = json.loads(precursor_path.read_text(encoding='utf-8'))
    for relative, expected in precursor['evidence_hashes'].items():
        if digest(ROOT/relative) != expected:
            raise ValueError('stale acquisition evidence')
    archive_path = ROOT/'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ued_14760926_processed.zip'
    tables = []
    preprocessing_path = ROOT/'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ued_treat_pickle_7f7036b.ipynb'
    notebook = json.loads(preprocessing_path.read_text(encoding='utf-8'))
    code = '\n'.join(''.join(c.get('source', [])) for c in notebook['cells'] if c['cell_type'] == 'code')
    if not all(token in code for token in ('t0_num = 8 #start from one', 'delay[t0_num-1]', "df.attrs['t0_index'] = t0_num")):
        raise ValueError('reviewed source time convention changed')
    with zipfile.ZipFile(archive_path) as archive:
        for member in ('PROCESSED/PROC_400nm', 'PROCESSED/PROC_800nm'):
            with archive.open(member) as stream:
                with gzip.GzipFile(fileobj=stream) as g:
                    root, globals_seen = read_inert(g)
                    if g.read(1): raise ValueError('trailing pickle payload')
                if stream.read(1): raise ValueError('trailing gzip payload')
            table = summarize_table(root, member, time_index_base=1)
            table['inert_global_references'] = globals_seen
            tables.append(table)
    files = [precursor_path, preprocessing_path, Path(__file__), ROOT/'docs/scripts/audit/ued_pickle_static.py',
             ROOT/'docs/core/test/test_topic13_ued_pickle_static.py',
             ROOT/'docs/core/test/test_topic13_ued_numeric_inventory.py']
    artifact = dict(major_result_id='T13_UED_NUMERIC_ROWS_AND_METADATA', topic='0.13', closure_level='PARTIAL',
                    what_is_closed=['Inert numeric image summaries, row identities, delays and source calibration extracted'],
                    equation_or_mapping='Source image-pair rows versus delay; no population inversion',
                    units={'delay': 'ps from author notebook', 'calibration': 'inverse angstrom/pixel from author notebook',
                           'image': 'processed intensity, absolute counts unverified'},
                    derivation_class='data_only_storage_interpretation', observable='processed UED images',
                    data_role='EXTERNAL_COMPARISON_CANDIDATE', verification_status='NUMERIC_ROWS_EXTRACTED_MAPPING_OPEN',
                    tables=tables, source_license='CC-BY-4.0', source_doi='10.5281/zenodo.14760926',
                    untrusted_callables_invoked=False, full_images_exported=False,
                    time_origin='Source one-based index reconciled without shifting any delay; physical timing uncertainty remains open.',
                    preprocessing='Author notebook cell 20 masks rotated pixels below 100 and shares NaN masks across ON/OFF before nanmean. No threshold reapplied here.',
                    uncertainty='Raw repeats, processing covariance, intensity-dependent missingness and physical timing uncertainty open',
                    open_blockers=['uncertainty and mask geometry', 'pixel/geometry-to-mode inversion', 'Phi source coefficient'],
                    dependency_unlocked=['processed row inspection only'], full_core_unlock=False, claim_promotion=False,
                    evidence_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in files},
                    claim_boundary='Image statistics are not heat, phonon occupations or physical alpha. No holdout used.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_ued_numeric_inventory_audit.json').write_text(json.dumps(artifact, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps([{k: t[k] for k in ('member', 'row_count', 'delay_range_ps', 'source_t0_index', 'source_zero_time_row', 'time_origin_reconciled', 'calibration_inverse_angstrom_per_pixel', 'image_nonfinite_count')} for t in tables], indent=2))


if __name__ == '__main__':
    main()
