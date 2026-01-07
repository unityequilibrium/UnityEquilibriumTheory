# UET R0-E17 — Adaptive dt Search (Zoom/Binary) + Band-Aware Scaling v0.1
**Goal:** ลดจำนวน dt variants ที่ต้องทดลอง (เร็วขึ้น) แต่ยังหาค่า dt “พอดี” ได้  
แทนที่จะยิง grid หนาๆ ทุกครั้ง → ใช้ zoom (binary search ใน log-scale) ต่อกลุ่มที่พังจริง

---

## 1) New scripts
- `scripts/suggest_zoom_scales.py`
  - อ่าน summary ที่ group = `band_model_integrator_variant`
  - จัดกลุ่มด้วย key: `band|model|integrator|code`
  - หา bracket (fail vs pass) แล้วเสนอ scale ใหม่ (geometric mid) จน bracket “แคบพอ”
  - Output: `zoom_scale_plan.json` (field `dt_scales_plan`)

- `scripts/merge_variant_summaries.py`
  - merge summary หลายรอบโดยรวม `n/pass/fail_codes` แล้วคำนวณ Wilson CI ใหม่
  - ใช้รวม evidence จากหลาย zoom rounds

> NOTE: `code` ถูกดึงจาก `variant` (pattern `_code..._dt...`) ที่ adaptive matrix สร้างไว้

---

## 2) make_adaptive_stress_matrix รองรับ plan
`make_adaptive_stress_matrix.py` เพิ่ม `--dt_scales_plan`
- ถ้ามี plan จะใช้ scales เฉพาะกลุ่มนั้น
- ถ้าไม่มี จะ fallback ไป `--dt_scales`

---

## 3) loop_driver รองรับ adaptive_mode=zoom
`loop_driver.py` อ่าน params เพิ่ม:
- `adaptive_mode`: `"grid"` หรือ `"zoom"`
- `zoom_rounds`: จำนวนรอบ zoom (default 2)
- `zoom_eps_ratio`: หยุดเมื่อ `s_hi_pass / s_lo_fail <= eps_ratio` (default 1.15)
- `zoom_min_scale`
- `zoom_max_new_scales_per_group`

**Behavior**
- ทำ adaptive รอบแรกด้วย grid (`dt_scales_grid`)
- ถ้า zoom mode:
  - สร้าง merged variant summary
  - วน `suggest_zoom_scales` → ได้ plan
  - รัน adaptive “เฉพาะ scale ใหม่” (targeted)
  - merge summary เพิ่ม evidence
  - ทำซ้ำจนหมด zoom_rounds หรือไม่มี scale ใหม่

สุดท้ายใช้ `adaptive_summary` ที่ merge แล้วไปทำ proposals (R0-E15)

---

## 4) Manual usage (ถ้าจะลอง zoom ทีละรอบ)
```bash
python scripts/suggest_zoom_scales.py \
  --variant_summary_csv adaptive_runs/stress_summary/stress_summary.csv \
  --out_plan zoom_scale_plan.json \
  --min_pass_rate 0.95 --min_ci_lo 0.90 \
  --eps_ratio 1.15

python scripts/make_adaptive_stress_matrix.py \
  --stress_matrix_in stress_matrix.csv \
  --stress_ledger stress_runs/dt_ladder_ledger.csv \
  --out adaptive_zoom_matrix.csv \
  --dt_scales_plan zoom_scale_plan.json
```

---

## Next step (R0-E18)
- ทำ zoom ที่ “aware ของ band” จริงๆ:
  - ถ้า FAIL ใน HARD band → zoom ลดเยอะกว่า
  - ถ้า FAIL ใน DEMO band → zoom ลดน้อย
- ทำ monotonic smoothing / Bayesian estimate ของ pass probability ต่อ scale
