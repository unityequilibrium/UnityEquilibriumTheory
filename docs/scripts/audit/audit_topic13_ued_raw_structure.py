"""Inspect published raw table structure without invoking serialized callables."""
import gzip
import hashlib
import json
import zipfile
import numpy as np
from docs.scripts.audit.ued_pickle_static import Node, read_inert
from docs.scripts.audit.audit_topic13_ued_numeric_inventory import expect, object_items
from docs.scripts.audit.audit_topic13_ued_raw_archive import ROOT
from docs.scripts.audit.audit_topic13_ued_source_acquisition import digest

COLUMNS = ['LTS_position', 'Exposure_time_ms', 'Frame_time', 'PHI_DEG', 'PHI_RAW',
           'Pressure', 'RF_Cavity_phase', 'RF_Cavity_power', 'Sensor_A_Ohm',
           'Sensor_B_Ohm', 'Temperature_A', 'Temperature_B', 'UV_power',
           'incident_energy', 'nimages', 'pump_area', 'pump_power', 'shutter',
           'Delay_ps', 'notes', 'imagesON', 'imagesOFF']


def summarize(root, member):
    expect(root, 'NEWOBJ', 'pandas.core.frame', 'DataFrame')
    blocks, axes = expect(root.state['_mgr'], 'REDUCE', 'pandas.core.internals.managers', 'BlockManager')
    _, col = expect(axes[0], 'REDUCE', 'pandas.core.indexes.base', '_new_Index')
    if object_items(col['data'], (22,)) != COLUMNS:
        raise ValueError('unreviewed raw columns')
    _, idx = expect(axes[1], 'REDUCE', 'pandas.core.indexes.base', '_new_Index')
    if idx['start'] != 0 or idx['step'] != 1 or idx['stop'] <= 0:
        raise ValueError('unreviewed row index')
    count, values = idx['stop'], {}
    for block in blocks:
        array, placement, ndim = expect(block, 'REDUCE', 'pandas._libs.internals', '_unpickle_block')
        start, stop, step = expect(placement, 'REDUCE', 'builtins', 'slice')
        if ndim != 2 or step != 1 or not 0 <= start < stop <= 22:
            raise ValueError('unreviewed placement')
        if array.kind == 'NUMERIC':
            if array.args['shape'] != [stop-start, count] or array.args['finite_count'] != array.args['count']:
                raise ValueError('invalid numeric metadata')
            items = array.args['values']
        else:
            flat = object_items(array, (stop-start, count))
            items = [flat[i*count:(i+1)*count] for i in range(stop-start)]
        for column, entries in zip(COLUMNS[start:stop], items):
            if column in values: raise ValueError('duplicate column placement')
            values[column] = entries
    if set(values) != set(COLUMNS): raise ValueError('missing columns')
    for column in ('imagesON', 'imagesOFF'):
        if any(not isinstance(a, Node) or a.kind != 'NUMERIC' or a.args['shape'] != [512, 512] for a in values[column]):
            raise ValueError('unreviewed image shape or extra repeat axis')
        values[column] = [a.args for a in values[column]]
    rows = []
    for i in range(count):
        row = {c: values[c][i] for c in COLUMNS if c != 'notes'}
        row['row_id'] = member+':row:'+str(i)
        row['row_sha256'] = hashlib.sha256(json.dumps(row, sort_keys=True, allow_nan=False).encode()).hexdigest()
        rows.append(row)
    return dict(member=member, row_count=count, columns=COLUMNS, rows=rows,
                scalar_ranges={c:[float(min(values[c])), float(max(values[c]))] for c in COLUMNS[:19]},
                image_shape=[512,512], explicit_repeat_axis=False,
                source_attrs_empty=not bool(root.state.get('attrs')))


def compare_cuts(a, b):
    if a['row_count'] != b['row_count']: return {'aligned':False}
    aligned = all(x['LTS_position'] == y['LTS_position'] and x['Delay_ps'] == y['Delay_ps']
                  for x,y in zip(a['rows'],b['rows']))
    return dict(aligned=aligned, equal_image_pairs=sum(
        all(x[c]['sha256'] == y[c]['sha256'] for c in ('imagesON','imagesOFF'))
        for x,y in zip(a['rows'],b['rows'])),
        independence='UNVERIFIED', covariance_estimable_from_labels_alone=False)


def main():
    source = ROOT/'docs/core/07_artifacts/topic13/t13_ued_raw_archive_audit.json'
    acquisition = json.loads(source.read_text())
    for p,h in acquisition['evidence_hashes'].items():
        if digest(ROOT/p) != h: raise ValueError('stale source evidence')
    tables = []
    archive_path = ROOT/'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ued_14760926_raw_sorted.zip'
    with zipfile.ZipFile(archive_path) as archive:
        for info in acquisition['archive_members']:
            if info['is_directory']: continue
            with archive.open(info['name']) as stream:
                with gzip.GzipFile(fileobj=stream) as g:
                    root, references = read_inert(g)
                    if g.read(1): raise ValueError('trailing pickle bytes')
                if stream.read(1): raise ValueError('trailing gzip bytes')
            table = summarize(root, info['name'])
            table['inert_global_references'] = references
            tables.append(table)
    files = [source, __file__, ROOT/'docs/scripts/audit/ued_pickle_static.py',
             ROOT/'docs/scripts/audit/audit_topic13_ued_numeric_inventory.py',
             ROOT/'docs/core/test/test_topic13_ued_raw_structure.py']
    from pathlib import Path
    result = dict(major_result_id='T13_RAW_ACQUISITION_STRUCTURE_IDENTIFIED', topic='0.13', closure_level='PARTIAL',
        what_is_closed=['Three raw table layouts and numeric row identities decoded inertly; archive members read to CRC-checked EOF'],
        equation_or_mapping='Source metadata and ON/OFF detector images only',
        units={'Exposure_time_ms':'ms by source column label; acquisition semantics unverified',
               'Delay_ps':'ps by source label; absolute stage-derived coordinate, not pump-relative zero',
               'Temperature_A/B':'UNVERIFIED sensor meaning, unit and calibration',
               'PHI_DEG/PHI_RAW':'instrument columns, NOT UET Phi', 'images':'detector units UNVERIFIED'},
        derivation_class='SOURCE_STRUCTURE_INSPECTION', observable='raw-sorted detector image pairs',
        data_role='EXTERNAL_SOURCE_NOT_CALIBRATION', verification_status='ROWS_DECODED_REPEAT_INDEPENDENCE_OPEN',
        tables=tables, cut_comparison=compare_cuts(tables[0],tables[1]), member_crc_verified=True,
        evidence_hashes={str(Path(p).relative_to(ROOT)).replace('\\','/'):digest(Path(p)) for p in files},
        open_blockers=['cut acquisition independence and exposure aggregation semantics', 'detector noise/gain and covariance',
                       'sensor location/units/calibration; no independent transient thermometry', 'Phi coupling'],
        dependency_unlocked=['source-specific acquisition and sensor provenance research only'],
        full_core_unlock=False, claim_promotion=False, untrusted_callables_invoked=False,
        claim_boundary='No shot-level claim, physical covariance, alpha calibration or holdout access. nimages metadata alone does not expose individual frames.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_ued_raw_structure_audit.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(tables=[{k:t[k] for k in ('member','row_count','scalar_ranges')} for t in tables], cut_comparison=result['cut_comparison']),indent=2))


if __name__ == '__main__': main()
