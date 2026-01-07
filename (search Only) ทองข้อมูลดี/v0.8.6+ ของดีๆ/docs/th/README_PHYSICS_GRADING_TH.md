# UET Physics Grading Pack — PASS/WARN/FAIL แบบ “ฟิสิกส์จริง”

## ทำไมต้องมีอันนี้
`run_suite.py` ให้ status จาก solver (PASS/FAIL) แต่การพิสูจน์จริงควรแยก:
- FAIL เพราะเครื่องมือพัง (NaN/Inf/blowup/dt collapse/backtracks บ้าๆ)
- FAIL เพราะ violating monotonic Ω (ถ้าตั้งใจให้ Ω เป็น Lyapunov)
- WARN เพราะยังไม่ converge

## วิธีใช้ (PowerShell)
ตัวอย่าง Atlas-A:
```powershell
python .\scripts\grade_runs.py --runs .\runs\atlas_A
```
จะได้ไฟล์:
- runs\atlas_A\grades.csv

## Thresholds default (โหมด “โหดแต่ไม่มั่ว”)
- C_max_fail = 50
- dt_collapse_fail = 1e-6  (dt_min/dt_nom)
- dt_collapse_warn = 1e-3
- backtracks_density_fail = 2.0
- backtracks_density_warn = 0.5
- dOmega_tol_rel = 1e-8, dOmega_tol_abs = 1e-12
- tight_frac_fail = 0.20, tight_frac_warn = 0.60

ถ้าอยากโหดขึ้น:
- ลด dOmega_tol_rel (เช่น 1e-10)
- เพิ่ม tight_frac_fail (เช่น 0.50)
