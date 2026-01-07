# UET Master Evidence Tools

This pack adds a single script:

- scripts/make_master_evidence_report.py

It reads a run ledger (e.g. runs_tier1_fail_hard/ledger.csv), extracts a 1-page evidence table,
auto-finds run directories by run_id, and generates key FAIL plots.

## Quick start (PowerShell)

From the harness root (where `scripts/` and `uet_core/` exist):

```powershell
python scripts\make_master_evidence_report.py --runs_dir runs_tier1_fail_hard --out_dir reports\master_evidence
```

Outputs:
- reports/master_evidence/evidence_table.csv
- reports/master_evidence/plots/*.png
- reports/master_evidence/UET_v0_8_5_master_evidence.md
- (optional) reports/master_evidence/UET_v0_8_5_master_evidence.pdf if reportlab is installed

To enable PDF:
```powershell
python -m pip install reportlab
```
