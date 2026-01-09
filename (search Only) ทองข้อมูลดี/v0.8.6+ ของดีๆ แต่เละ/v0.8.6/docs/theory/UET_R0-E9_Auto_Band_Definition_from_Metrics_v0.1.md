# UET R0-E9 — Auto Band Definition from Metrics v0.1
**Goal:** ลดการกำหนด band ด้วยมือ โดยให้ band_map มาจาก “หลักฐานตัวเลข” ใน dt-ladder ledger  
แล้วนำไปใช้กับ R0-E8 (band-aware dt presets) และ baseline lock (manifest)

> บทนี้เป็น “protocol/engineering” ไม่ใช่การเพิ่มแก่นทฤษฎีฟิสิกส์

---

## 1) Input data (ขั้นต่ำ)
- `dt_ladder_runs/dt_ladder_ledger.csv` จาก R0-E6  
คีย์สำคัญที่ใช้:
- `base_case_id, integrator, dt, status, dt_backtracks_total, dt_min`

---

## 2) Core metric: dt_max_pass (per case)
สำหรับแต่ละ `base_case_id` และ integrator:
- หา `dt_max_pass` = dt ที่มากที่สุดที่ **PASS**

แล้ว collapse เป็น “robust_dt” ตาม policy:
- `max_over_integrators` (default): robust_dt = max(dt_max_pass_semi, dt_max_pass_stab)
- `min_over_integrators`: conservative (ต้องรอดทั้งคู่โดยนัย)
- `semiimplicit_only` / `stabilized_only`: ใช้ตัวเดียว

---

## 3) Band rule (default)
ให้ thresholds:
- DEMO: robust_dt ≥ 0.05 (และ backtracks ไม่สูงเกิน)
- MID: 0.02 ≤ robust_dt < 0.05
- BOUNDARY: 0.01 ≤ robust_dt < 0.02
- HARD: robust_dt < 0.01
- FAIL: ไม่มี dt ไหน PASS

**Safety tweak:** ถ้า band เป็น DEMO แต่ median backtracks@robust_dt > 1 → ลดเป็น MID (กัน “DEMO ที่จริง stiff”)

---

## 4) Generate band_map.csv (auto)
```bash
python scripts/auto_band_map_from_ledger.py \
  --ledger dt_ladder_runs/dt_ladder_ledger.csv \
  --out band_map.csv \
  --policy max_over_integrators \
  --demo_dt 0.05 --mid_dt 0.02 --hard_dt 0.01
```

Output `band_map.csv` มีคอลัมน์เพิ่ม:
- `robust_dt, dt_max_semi, dt_max_stab, chosen_integrator, median_backtracks_at_robust_dt, notes`

---

## 5) Apply band to atlas matrix
ถ้า atlas matrix ยังไม่มีคอลัมน์ band:
```bash
python scripts/add_band_to_matrix.py \
  --matrix_in atlas_stage1.csv \
  --band_map band_map.csv \
  --matrix_out atlas_stage1_with_band.csv \
  --key_col base_case_id \
  --band_col band
```

ถ้า matrix มีแต่ `case_id` ที่เป็นรูป `base__...`:
```bash
python scripts/add_band_to_matrix.py \
  --matrix_in atlas_stage1.csv \
  --band_map band_map.csv \
  --matrix_out atlas_stage1_with_band.csv \
  --extract_from_case_id
```

---

## 6) Plug into R0-E8 + baseline manifest
1) ใช้ `band_map.csv` ไป extract band_dt_presets (R0-E8)
2) freeze หลักฐานลง manifest:
```bash
python scripts/freeze_baseline_manifest.py \
  --out baseline/baseline_manifest.json \
  --ledger dt_ladder_runs/dt_ladder_ledger.csv \
  --dt_presets dt_ladder_runs/dt_presets/dt_presets.json \
  --band_dt_presets dt_ladder_runs/band_dt_presets/band_dt_presets.json \
  --band_map band_map.csv \
  --pass_threshold 1.0 \
  --overwrite
```

---

## 7) Next step (R0-E10)
- ปรับ auto-band ให้ robust ขึ้นด้วย additional metrics:
  - dt_min collapse ratio
  - ΔΩ margin (how close to violating gate)
  - pattern/structure metrics (ถ้าเพิ่มใน atlas)
- ทำ “band stability check” ว่า label ไม่สวิงง่ายเมื่อเปลี่ยน seed

---
