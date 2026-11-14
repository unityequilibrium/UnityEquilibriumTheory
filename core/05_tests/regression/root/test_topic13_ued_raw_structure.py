from docs.scripts.audit.audit_topic13_ued_raw_structure import compare_cuts, summarize
import pytest
import io
import pickle
import numpy as np
import pandas as pd
from docs.scripts.audit.ued_pickle_static import read_inert
from docs.scripts.audit.audit_topic13_ued_raw_structure import COLUMNS


def test_raw_numeric_rows_preserved_without_sensor_interpretation():
    frame = pd.DataFrame()
    for c in COLUMNS[:19]: frame[c] = [1., 2.]
    frame['notes'] = ['', '']
    for c in COLUMNS[20:]: frame[c] = [np.ones((512,512)), np.full((512,512),2.)]
    root, _ = read_inert(io.BytesIO(pickle.dumps(frame, protocol=5)))
    result = summarize(root,'trusted-test-fixture')
    assert result['row_count'] == 2
    assert result['rows'][1]['Temperature_B'] == 2.
    assert result['rows'][1]['imagesON']['mean'] == 2.
    assert not result['explicit_repeat_axis']
    assert result['rows'][0]['row_sha256'] != result['rows'][1]['row_sha256']


def test_aligned_cuts_are_not_declared_independent():
    row = dict(LTS_position=1, Delay_ps=6.666, imagesON={'sha256':'a'}, imagesOFF={'sha256':'b'})
    table = dict(row_count=1,rows=[row])
    result = compare_cuts(table,table)
    assert result['aligned'] and result['equal_image_pairs'] == 1
    assert result['independence'] == 'UNVERIFIED'
    assert not result['covariance_estimable_from_labels_alone']


def test_unknown_layout_rejected():
    with pytest.raises(ValueError): summarize({},'fixture')


def test_mismatched_row_counts_not_aligned():
    assert compare_cuts({'row_count':1},{'row_count':2}) == {'aligned':False}
