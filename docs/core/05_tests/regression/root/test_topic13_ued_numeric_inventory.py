import io
import pickle

import numpy as np
import pandas as pd
import pytest

from docs.scripts.audit.ued_pickle_static import read_inert
from docs.scripts.audit.audit_topic13_ued_numeric_inventory import summarize_table


def table(columns=None):
    on = np.ones((512, 512), dtype='<f8')
    off = 2*on
    on[0, 0] = np.nan
    # Match the source's separate storage block per column, not a general pandas layout.
    frame = pd.DataFrame()
    frame['imgON'] = [on, on.copy()]
    frame['imgOFF'] = [off, off.copy()]
    frame['delay'] = [0., 1.]
    if columns:
        frame.columns = columns
    frame.attrs.update(t0_index=1, calibration=np.float64(.03), peak_dist=np.float64(90.),
                       scan_number='synthetic', Zorder_pos=np.array([256., 256.]))
    return read_inert(io.BytesIO(pickle.dumps(frame, protocol=5)))[0]


def test_preserves_pairing_nan_and_one_based_time_origin():
    summary = summarize_table(table(), 'synthetic', time_index_base=1)
    assert summary['row_count'] == 2
    assert summary['image_nonfinite_count'] == 2
    assert summary['source_t0_index'] == 1
    assert summary['exact_zero_delay_indices'] == [0]
    assert summary['time_origin_reconciled']
    assert summary['source_zero_time_row'] == 0
    assert summary['rows'][0]['imgOFF']['mean'] == 2
    assert 'mean' not in summary['rows'][0]['imgON']
    assert summary['rows'][0]['row_id'] == 'synthetic:row:0'


def test_unexpected_columns_rejected():
    with pytest.raises(ValueError):
        summarize_table(table(['imgOFF', 'imgON', 'delay']), 'synthetic', time_index_base=1)


def test_wrong_index_base_does_not_silently_shift_delay():
    result = summarize_table(table(), 'synthetic', time_index_base=0)
    assert not result['time_origin_reconciled']
    assert result['rows'][0]['delay_ps'] == 0
    assert result['rows'][1]['delay_ps'] == 1
