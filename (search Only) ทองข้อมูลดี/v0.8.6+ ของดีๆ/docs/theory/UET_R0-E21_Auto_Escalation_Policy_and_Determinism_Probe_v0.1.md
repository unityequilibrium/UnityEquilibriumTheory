# UET R0-E21 — Auto-Escalation Policy (Persistent BLOCK) + Determinism Probe v0.1
**Goal:** ถ้า monotonic guard (R0-E19) ยัง `BLOCK` แม้ผ่าน resample (R0-E20) แล้ว  
ระบบต้อง “ยกระดับ” การตรวจสอบให้ชัดว่า:
- เป็น **noise (ยัง sample ไม่พอ)** → เพิ่ม evidence แบบหนักขึ้น
- เป็น **solver non-determinism / stochastic bug** → ต้องแก้ระบบก่อน (ห้าม auto-apply presets)
- หรือเป็น **metric/threshold artifact** → ต้องกลับไปปรับ metric/threshold

---

## 1) Fix (สำคัญ)
### `scripts/run_dt_ladder.py`
- แก้เรียก `init_run_folder(...)` ให้ตรง signature: `init_run_folder(out_root, model, case_id, config)`
- เพิ่มรองรับ `probe_tag` (column ใน matrix) → ใส่ใน `config["probe"]` เพื่อให้ run_id แตกต่าง (ใช้กับ determinism probe)

---

## 2) New scripts
### 2.1 `scripts/determinism_probe_matrix.py`
สร้าง matrix สำหรับ “replay” config เดิมด้วย seed เดิมหลายครั้ง:
- input: matrices ที่ใช้รัน adaptive
- groups_json: ใช้ `monotonic_report.json` (เอา blocklist)
- output: `determinism_probe_matrix.csv` ที่เพิ่มคอลัมน์ `probe_tag=rep01..`

### 2.2 `scripts/determinism_report.py`
อ่าน `dt_ladder_ledger.csv` จาก determinism probe runs แล้วสรุปว่า
- กลุ่มเดียวกัน (base_case_id, model, integrator, dt, seed) ให้ผล pass/fail/fail_code “เหมือนกัน” ไหม
- ถ้ามีผลต่างกัน → `status=UNSTABLE`

---

## 3) loop_driver escalation
เพิ่ม params:
- `determinism_probe` (default true)
- `determinism_repeats` (default 5)
- `determinism_max_base_rows` (default 200)
- `escalate_on_persistent_block` (default true)
- `escalate_extra_seeds_multiplier` (default 2)
- `escalate_additional_resample_rounds` (default 1)

Behavior:
1) ทำ adaptive + zoom + resample ตามเดิม
2) ถ้ายัง `BLOCK`:
   - รัน determinism probe → ได้ `determinism_report.json`
   - ทำ “heavier resample” เพิ่ม seeds มากขึ้น (extra_seeds × multiplier) อีก 1–N รอบ
   - merge summary + rerun monotonic check
