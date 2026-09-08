import io
import pickle

import numpy as np
import pytest

from docs.scripts.audit.ued_pickle_static import Node, read_inert


def test_numeric_protocol5_without_global_execution():
    array = np.arange(12., dtype='<f8').reshape(3, 4)
    result, _ = read_inert(io.BytesIO(pickle.dumps(array, protocol=5)))
    assert result.kind == 'NUMERIC'
    assert result.args['values'] == array.tolist()
    assert result.args['mean'] == 5.5


def test_arbitrary_reduce_is_inert():
    class Attempt:
        def __reduce__(self):
            return eval, ('1/0',)
    result, seen = read_inert(io.BytesIO(pickle.dumps(Attempt(), protocol=5)))
    assert isinstance(result, Node) and result.kind == 'REDUCE'
    assert ('builtins', 'eval') in seen


def test_container_values_and_shared_reference():
    shared = ['delay', 1.5]
    result, _ = read_inert(io.BytesIO(pickle.dumps({'a': shared, 'b': shared}, protocol=5)))
    assert result['a'] is result['b']


def test_truncated_payload_fails():
    with pytest.raises((ValueError, EOFError)):
        read_inert(io.BytesIO(pickle.dumps(np.arange(5.), protocol=5)[:-9]))
