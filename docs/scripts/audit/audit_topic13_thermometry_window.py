"""Check a source-specific late-time assumption against acquired delays."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def eligible_delays(delays, lower_bound_ps):
    return [i for i, delay in enumerate(delays) if delay > lower_bound_ps]


def main():
    path = ROOT/'docs/core/07_artifacts/topic13/t13_ued_numeric_inventory_audit.json'
    source = json.loads(path.read_text())
    for relative, expected in source['evidence_hashes'].items():
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() != expected:
            raise ValueError('stale inventory')
    rows = []
    for table in source['tables']:
        delays = [r['delay_ps'] for r in table['rows']]
        rows.append(dict(member=table['member'], rows=len(delays), maximum_delay_ps=max(delays),
                         eligible_row_indices=eligible_delays(delays, 100.)))
    files = [path, Path(__file__), ROOT/'docs/core/test/test_topic13_thermometry_window.py']
    result = dict(major_result_id='T13_LATE_THERMOMETRY_TRANSFER_BOUNDARY', topic='0.13', closure_level='PARTIAL',
        what_is_closed=['Acquired UED delays do not overlap the reviewed source-specific >100 ps equilibrium window'],
        equation_or_mapping='source eligibility comparison only, not a universal thermalization threshold',
        units={'delay': 'ps'}, derivation_class='SOURCE_SCOPE_COMPARISON', observable='time-window eligibility',
        data_role='METADATA_AUDIT_NOT_CALIBRATION', verification_status='NO_OVERLAP_NO_CALIBRATION_TRANSFER',
        literature={'url':'https://arxiv.org/pdf/1709.02805', 'locator':'Main text Figure 3 discussion; SI 5',
                    'late_time_condition_ps':100., 'comparison':'>',
                    'temperature_origin':'Debye-Waller model inference under quasi-equilibrium, not an independently measured calibration table',
                    'numeric_calibration_acquired':False},
        acquired_scans=rows, full_core_unlock=False, claim_promotion=False,
        open_blockers=['same-sample equilibrium evidence', 'independent numeric calibration', 'Phi coupling'],
        dependency_unlocked=['reject this unsupported calibration transfer only'],
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\', '/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        claim_boundary='Different samples may equilibrate differently. Nonoverlap rejects the proposed justification, not equilibrium itself or all thermometry routes. No holdout, fit or invented rows.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_thermometry_window_audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(rows, indent=2))


if __name__ == '__main__':
    main()
