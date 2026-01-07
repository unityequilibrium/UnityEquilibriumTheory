# UET R0-E20 — Auto-Resample for Blocked Groups + Targeted Rerun v0.1
**Goal:** ถ้า monotonic guard (R0-E19) ตัดสินว่า evidence “ไม่นิ่ง” (BLOCK)  
อย่าหยุดนิ่ง — ให้ระบบเพิ่มหลักฐาน (n) อัตโนมัติ โดย rerun เฉพาะกลุ่มที่โดน blocklist

---

## 1) New script
### `scripts/resample_blocked_groups.py`
สร้าง matrix เพิ่มเติมจาก matrix ที่ใช้สร้าง adaptive variants แล้ว:
- เลือกเฉพาะ rows ในกลุ่มที่อยู่ใน `blocklist_band_model_integrator`
- clone rows พร้อมสร้าง seed ใหม่เพิ่ม `extra_seeds` ต่อ row
- เลี่ยง duplicate seeds ถ้าให้ `--dedupe_ledger`

Output: `resample_matrix.csv`

---

## 2) loop_driver behavior
เพิ่ม params:
- `resample_on_block` (default true)
- `resample_rounds` (default 2)
- `resample_extra_seeds` (default 10)
- `resample_seed_start` (default 200000)
- `resample_max_rows` (default 20000)

Workflow:
1) ทำ adaptive (grid/zoom) ตามเดิม → ได้ `adaptive_summary` (merged)
2) ทำ monotonic check → ได้ `monotonic_report.json`
3) ถ้า `status == "BLOCK"` และเปิด resample:
   - สร้าง `resample_matrix_roundXX.csv`
   - รัน `run_dt_ladder.py`
   - สรุปเป็น summary (variant grouping)
   - merge เข้า `adaptive_summary`
   - rerun monotonic check
   - วนซ้ำจน `OK` หรือครบ `resample_rounds`

**ผลลัพธ์**: ลด false block จาก noise และทำให้การ apply presets ปลอดภัยขึ้น

---

## 3) Recommended defaults
- `resample_rounds: 2`
- `resample_extra_seeds: 10`
- ถ้า model stochastic มาก → เพิ่ม extra_seeds เป็น 20

---

## Next step (R0-E21)
- Auto “escalation”: ถ้ายัง BLOCK หลัง resample
  - เพิ่ม jitters_per_case / เพิ่ม cases_per_group เฉพาะกลุ่มนั้น
  - หรือสลับไปตรวจ metric thresholds / solver determinism
