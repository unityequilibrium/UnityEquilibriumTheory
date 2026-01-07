# UET R0-E22 — Metric Triage (Blocklist ↔ Fail Codes ↔ Metrics) v0.1
Goal: ระบุ “BLOCK มาจากอะไร” โดยเชื่อม 3 ชั้น:
1) monotonic_report (BLOCK + violations)
2) fail_codes_json (จาก summarize_stress_test)
3) run-level metrics (จาก run_dir/summary.json)

Outputs:
- metric_triage_report.json
- metric_triage_report.md

Patch:
- run_case.py + run_dt_ladder.py เติม summary['fail_code'] จาก fail_reasons[0] เพื่อให้ fail_codes_json ใช้งานได้จริง

Integration:
- loop_driver รัน metric_triage อัตโนมัติก่อน propose/apply presets

Optional thresholds template:
- docs/UET_R0-E22_metric_thresholds_optional_template.json
