# UET R0-E15 — Auto-fix Proposals + Baseline Refresh Loop v0.1
**Goal:** ปิด loop จาก R0-E13/R0-E14 ให้กลายเป็น “ระบบปรับปรุงแบบ evidence-driven”  
โดยไม่ต้องเดา: ใช้ผล A/B (dt scaling variants) → สร้างข้อเสนอปรับ dt presets → apply → re-run → freeze baseline

---

## 1) Inputs
- Adaptive run summary (จาก R0-E14):
  - `adaptive_runs/stress_summary/stress_summary.csv` **(ต้อง group = band_model_integrator_variant)**
- (optional) current presets:
  - `band_dt_presets_strict.json` (หรือ band_dt_presets.json)
- (optional) gate report:
  - `adaptive_runs/stress_summary/stress_gate_report.json`

---

## 2) Generate preset update proposals (from variants)
> เลือก “dt scale ที่เล็กสุดที่ผ่าน gate” ต่อ (band×model×integrator)

```bash
python scripts/propose_preset_updates_from_variant_summary.py \
  --variant_summary_csv adaptive_runs/stress_summary/stress_summary.csv \
  --band_presets_json dt_ladder_runs_seeds/band_dt_presets_strict/band_dt_presets_strict.json \
  --min_pass_rate 0.95 --min_ci_lo 0.90 \
  --out preset_update_proposals.csv
```

Output:
- `preset_update_proposals.csv`

**Interpretation**
- `gate_pass_at_recommended_scale=1` → scale นี้ควร “พอ” (ตาม evidence)
- ถ้าเป็น 0 → ไม่มี variant ไหนผ่าน; เลือก scale ที่เล็กสุดที่มี → ชี้ว่า “ต้องแก้เชิงโมเดล/constraint หรือเพิ่ม scale ต่ำกว่าเดิม”

---

## 3) Render report (อ่านง่าย)
```bash
python scripts/render_preset_update_report.py \
  --updates_csv preset_update_proposals.csv \
  --out_md preset_update_report.md \
  --only_changes
```

---

## 4) Apply proposals to presets
### 4.1 band-aware presets
```bash
python scripts/apply_preset_updates.py \
  --presets_in dt_ladder_runs_seeds/band_dt_presets_strict/band_dt_presets_strict.json \
  --updates_csv preset_update_proposals.csv \
  --presets_out band_dt_presets_strict_updated.json \
  --mode band \
  --apply_only_gate_pass
```

### 4.2 global presets (ถ้าต้องการ)
```bash
python scripts/apply_preset_updates.py \
  --presets_in dt_ladder_runs_seeds/dt_presets_strict/dt_presets_strict.json \
  --updates_csv preset_update_proposals.csv \
  --presets_out dt_presets_strict_updated.json \
  --mode global \
  --apply_only_gate_pass
```

---

## 5) Re-run stress with updated presets (sanity loop)
1) Generate new stress matrix from spec (R0-E13) แต่ใช้ presets_updated  
2) Run + gate  
3) ถ้าผ่าน → freeze baseline

---

## 6) Freeze baseline (lock evidence)
ใช้ `freeze_baseline_manifest.py` บันทึก:
- presets updated
- stress_spec + stress_report
- metric_thresholds + band_map + stability (ถ้ามี)

> แนวคิด: baseline คือ “ชุด configuration + evidence hash” ที่ repeatable

---

## 7) When proposals are not enough
ถ้า adaptive A/B dt scaling (1.0 vs 0.5) ยัง FAIL ทั้งคู่:
- นี่คือสัญญาณว่า “ไม่ใช่ dt อย่างเดียว”
- ต้องไปดู fail_code และกลับไปแก้:
  - coercivity/domain constraints (R0-B2)
  - solver numerical guards (clamps, NaN detection, boundary conditions)
  - band rule / thresholds (R0-E11/E12)

---

## Next step (R0-E16)
- ทำ “auto-run loop driver” (single command):
  - run adaptive → summarize → propose → apply → rerun → freeze
- เพิ่ม dt_scales grid (1.0, 0.7, 0.5, 0.35, 0.25) แบบ adaptive
