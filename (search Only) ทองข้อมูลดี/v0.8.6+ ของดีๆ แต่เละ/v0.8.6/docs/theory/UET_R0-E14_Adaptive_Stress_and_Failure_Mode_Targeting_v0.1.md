# UET R0-E14 — Adaptive Stress + Failure-Mode Targeting v0.1
**Goal:** ถ้า stress gate (R0-E13) FAIL → ไม่วนมั่ว  
ให้สร้าง stress รอบถัดไปที่ “ยิงตรงจุด” โดยอัตโนมัติ:
- โฟกัสกลุ่มที่ fail เยอะสุด (band×model×integrator×fail_code)
- jitter รอบตัวอย่างที่ fail จริง (local neighborhood)
- ทำ A/B test ด้วย dt scaling เพื่อแยก “dt issue” vs “model/constraint issue”

> ใช้เพื่อปรับ dt presets / band rule / metric thresholds แบบ evidence-driven

---

## 1) Make failure-mode report (เร็ว)
```bash
python scripts/failure_mode_report.py \
  --ledger stress_runs/dt_ladder_ledger.csv
```
Output: `stress_runs/failure_mode_report.json`

---

## 2) Generate adaptive stress matrix (focus on failures)
ต้องมี `stress_matrix.csv` ที่ใช้รันรอบแรก และ `dt_ladder_ledger.csv` ของผล
```bash
python scripts/make_adaptive_stress_matrix.py \
  --stress_matrix_in stress_matrix.csv \
  --stress_ledger stress_runs/dt_ladder_ledger.csv \
  --out adaptive_stress_matrix.csv \
  --top_groups 5 \
  --cases_per_group 5 \
  --jitters_per_case 3 \
  --dt_scales 1.0;0.5
```

สิ่งที่มันทำ:
- เลือก top fail groups
- เลือกเคสที่ fail หลาย seed ก่อน
- สุ่มพารามิเตอร์ใหม่แบบ “ใกล้เคียง” (log jitter)
- สร้าง variant 2 แบบ:
  - dt×1.0 (ดูว่ามันยัง fail ไหม)
  - dt×0.5 (ถ้าหาย fail แปลว่า dt ยังใหญ่ไป)

> Matrix ที่สร้างจะใส่คอลัมน์เพิ่ม: `variant, origin_case_id, origin_fail_code`  
และ `run_dt_ladder.py` จะ carry ลง ledger แล้ว

---

## 3) Run adaptive stress
```bash
python scripts/run_dt_ladder.py --matrix adaptive_stress_matrix.csv --out adaptive_runs --overwrite
python scripts/summarize_stress_test.py --ledger adaptive_runs/dt_ladder_ledger.csv --group band_model_integrator_variant
```

ดูผลแบบ A/B:
- compare `variant` ที่ dt=1 vs dt=0.5
- ถ้า dt=0.5 ผ่านเยอะขึ้น → ปรับ dt preset หรือ cap rule
- ถ้า dt=0.5 ยัง fail → ไปดู fail_code และ constraints/terms ที่เกี่ยวข้อง (ไม่ใช่ dt ล้วน)

---

## 4) Gate (optional)
ใช้ gate เดิมได้:
```bash
python scripts/gate_stress_results.py \
  --summary_csv adaptive_runs/stress_summary/stress_summary.csv \
  --min_pass_rate 0.95 --min_ci_lo 0.90
```

---

## 5) What to change after adaptive
Checklist:
- ถ้า fail เฉพาะ stabilized: ปรับ `stab_scale/margin` หรือ tighten metric thresholds
- ถ้า fail เฉพาะ boundary band: ลด dt preset เฉพาะ band (ไม่ลดทั้งระบบ)
- ถ้า fail_code บอก NaN/overflow: เพิ่ม clamp/regularize ใน solver (audit ก่อน)
- ถ้า fail เพราะ coercivity: กลับไป R0-B2 (เงื่อนไข coercive) แล้ว fix param domain

---

## Next step (R0-E15)
- ทำ “auto-fix proposals”:
  - เสนอ dt scale ใหม่ต่อ band
  - เสนอ threshold ใหม่จากผล A/B
  - ทำ PR checklist เพื่อ lock baseline รอบใหม่
