# UET R0-E8 — Band-aware dt Presets + Baseline Manifest Integration v0.1
**Goal:** ยกระดับจาก dt preset แบบ global (model × integrator) → เป็น **band-aware**  
เพื่อให้ atlas sweep “เร็วแต่ไม่หลอก” โดยใช้ dt ตามความยากของ regime/band และล็อกหลักฐานลง baseline manifest

---

## 1) Why band-aware matters
ผล dt-ladder มักไม่สม่ำเสมอ:
- demo regimes ผ่าน dt ใหญ่ได้
- boundary regimes ต้อง dt เล็ก (ไม่งั้น backtrack แหลก หรือ fail)

ดังนั้นถ้าใช้ dt เดียวทั้ง atlas:
- ต้องเลือก dt เล็กสุดตาม boundary → เสียเวลามาก
- หรือเลือก dt ใหญ่ → boundary fail แล้ว map แตก

ทางออก: แยก dt ตาม band (หรือ regime class) แล้วใช้ **cap_to_preset** เป็น default

---

## 2) Inputs (minimum)
1) `dt_ladder_runs/dt_ladder_ledger.csv` (R0-E6)
2) `band_map.csv` mapping `base_case_id -> band`  
   (ทำเองจากความรู้ domain ของเรา: demo vs boundary หรือชื่อ band ใน atlas spec)

> วิธีง่ายสุด: ให้ band_map มีแค่ 2 band ก่อน: `DEMO` กับ `BOUNDARY`

---

## 3) Extract band dt presets
```bash
python scripts/extract_band_dt_presets.py \
  --ledger dt_ladder_runs/dt_ladder_ledger.csv \
  --band_map band_map.csv \
  --pass_threshold 1.0
```

Output:
- `dt_ladder_runs/band_dt_presets/band_dt_presets.json`
- `band_dt_presets_selected.csv`
- `band_dt_presets_stats.csv`

---

## 4) Apply band dt presets to atlas matrix
ต้องมีคอลัมน์ `band` ใน atlas matrix (หรือเปลี่ยนชื่อผ่าน `--band_col`)

```bash
python scripts/apply_band_dt_presets_to_matrix.py \
  --matrix_in atlas_stage1.csv \
  --matrix_out atlas_stage1_dt.csv \
  --band_presets_json dt_ladder_runs/band_dt_presets/band_dt_presets.json \
  --global_presets_json dt_ladder_runs/dt_presets/dt_presets.json \
  --mode cap_to_preset
```

**Fallback chain**
1) band preset (band × model × integrator)
2) global preset (model × integrator)
3) default_dt (ถ้ากำหนด)

---

## 5) Freeze evidence into baseline manifest
```bash
python scripts/freeze_baseline_manifest.py \
  --out baseline/baseline_manifest.json \
  --ledger dt_ladder_runs/dt_ladder_ledger.csv \
  --dt_presets dt_ladder_runs/dt_presets/dt_presets.json \
  --band_dt_presets dt_ladder_runs/band_dt_presets/band_dt_presets.json \
  --pass_threshold 1.0 \
  --note "dt presets frozen after ladder run 2025-xx-xx" \
  --overwrite
```

Manifest จะบันทึก:
- dt presets (global + band-aware)
- sha256 ของไฟล์หลักฐาน (ledger/presets) เพื่อ audit

---

## 6) Next step (R0-E9)
- ทำ “Band definition protocol” ที่ไม่อาศัย manual labeling:
  - band จาก metrics (เช่น backtracks density, ΔΩ margin, pattern metric)
- ผูกเข้ากับ Atlas Stage2 boundary refinement (R0-D3)
