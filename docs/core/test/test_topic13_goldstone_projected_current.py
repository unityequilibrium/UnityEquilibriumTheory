"""Independent checks for the projected-current research candidate."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from docs.scripts.audit import audit_topic13_goldstone_projected_current as audit


def test_residues_reconstruct_euclidean_propagator():
    for k in (0.01, 0.1, 0.5):
        energies, vectors = audit.modes(k)
        assert np.all(energies > 0)
        for nu in (0.03, 0.7):
            v = nu**2 + k**2
            matrix = np.array([[v + 8, -2*np.sqrt(5)*nu, -2],
                               [2*np.sqrt(5)*nu, v, 0], [-2, 0, v + 4]])
            reconstructed = sum(
                np.outer(r, r.conj())/(e-1j*nu)
                + np.outer(r.conj(), r)/(e+1j*nu)
                for e, r in zip(energies, vectors)
            )
            np.testing.assert_allclose(reconstructed, np.linalg.inv(matrix), rtol=1e-10, atol=1e-10)


def test_energy_shell_has_physical_momentum_triangle():
    p, q = 0.04, 0.013
    ep, _ = audit.gold(p)
    eq, _ = audit.gold(q)
    r = audit.momentum_at_energy(ep-eq)
    er, _ = audit.gold(r)
    assert abs(p-q) < r < p+q
    assert abs(ep-eq-er) < 1e-14


def test_current_matches_canonical_repository_modules():
    rows = audit.canonical_current_checks()
    assert len(rows) == 12
    assert max(row['relative_error'] for row in rows) < 1e-8


def test_quadrature_and_variational_basis_are_distinct_checks():
    coarse = audit.assemble(.01, 24, 24, .8, N=3)
    refined = audit.assemble(.01, 40, 40, .8, N=3)
    values = [r['response'] for r in refined['results']]
    assert all(b >= a for a, b in zip(values, values[1:]))
    assert abs(coarse['results'][-1]['response']/values[-1]-1) < 1e-5
    assert values[-1]/values[0] > 1.05
    assert 0 < refined['projected_current_fraction'] < 1
    assert all(r['min_rate'] > 0 for r in refined['results'])


@pytest.mark.parametrize('T,order,cutoff,N', [
    (0., 24, .8, 3), (float('nan'), 24, .8, 3),
    (.01, 7, .8, 3), (.01, True, .8, 3),
    (.01, 24, 2., 3), (.01, 24, .8, 11),
])
def test_out_of_contract_inputs_are_rejected(T, order, cutoff, N):
    with pytest.raises(ValueError):
        audit.assemble(T, order, 24, cutoff, N=N)


def test_report_reads_only_declared_code_hashes_and_never_promotes(monkeypatch):
    original = Path.read_bytes
    accesses = []

    def code_only(path):
        assert path.suffix == '.py', 'Source/holdout payload must not be read'
        accesses.append(path)
        return original(path)

    monkeypatch.setattr(Path, 'read_bytes', code_only)
    report = audit.build_report(quick=True)
    json.dumps(report, allow_nan=False)
    assert all(report['checks'].values())
    assert len(accesses) == 3
    assert report['closure_level'] == 'PARTIAL'
    assert report['open_blockers']
    for key in ('full_core_unlock', 'claim_promotion', 'holdout_access', 'parameter_fitting'):
        assert report[key] is False
    for path, digest in report['source_hashes'].items():
        assert hashlib.sha256(original(audit.ROOT/path)).hexdigest() == digest
