# UET R0-E7 — Atlas dt Presets from dt-Ladder v0.1
**Goal:** ทำให้ atlas sweep ใช้ dt ที่ “พิสูจน์แล้วว่ารอด” จาก dt-ladder  
โดยแยกตาม **(model × integrator)** และทำเป็น workflow ที่ audit-friendly

> แนวคิด: อย่าเดา dt. ให้ dt มาจาก evidence (ledger) แล้วค่อย freeze baseline

---

## 1) Inputs / Outputs
**Input**
- `dt_ladder_runs/dt_ladder_ledger.csv` (จาก R0-E6)

**Outputs**
- `dt_presets/dt_presets.json` : mapping `{model: {integrator: dt}}`
- `dt_presets/dt_presets_selected.csv` : ตารางเลือก dt
- `dt_presets/dt_presets_stats.csv` : pass-rate/backtracks ต่อ dt
- atlas matrix ใหม่ที่ถูก apply dt แล้ว

---

## 2) Extract dt presets (from ladder ledger)
```bash
python scripts/extract_dt_presets.py \
  --ledger dt_ladder_runs/dt_ladder_ledger.csv \
  --pass_threshold 1.0
```

จะได้ folder `dt_ladder_runs/dt_presets/` ที่มี `dt_presets.json`

> ถ้า boundary zones ทำให้ 1.0 เข้มเกิน: ใช้ 0.9 แต่ต้อง mark ว่า “boundary risk” (อย่า overclaim)

---

## 3) Apply dt presets to any matrix
ตัวอย่างกับ atlas stage1:
```bash
python scripts/apply_dt_presets_to_matrix.py \
  --matrix_in atlas_stage1.csv \
  --presets_json dt_ladder_runs/dt_presets/dt_presets.json \
  --matrix_out atlas_stage1_dt.csv \
  --mode overwrite
```

### Modes
- `overwrite` : เซ็ต dt ตาม preset ทุกแถวที่มี preset
- `fill_missing` : ใส่ dt เฉพาะแถวที่ dt ว่าง/0
- `cap_to_preset` : จำกัด dt ไม่ให้เกิน preset (dt = min(dt_old, dt_preset))

---

## 4) Recommended operational rule
- ใช้ `cap_to_preset` สำหรับ matrix ที่ dt ถูกตั้งไว้แล้ว (กัน “เผลอเพิ่ม dt”)
- ใช้ `overwrite` สำหรับ matrix generated ใหม่ที่อยากให้ “ทั้งชุด” ใช้ dt จาก evidence

---

## 5) Next step (R0-E8)
- ผูก dt presets เข้ากับ atlas band-map (บาง band อาจต้อง dt เล็กกว่า global)
- เพิ่ม “preset card” ลง baseline manifest (R0-D7) เพื่อ freeze baseline อย่างมีหลักฐาน

---
