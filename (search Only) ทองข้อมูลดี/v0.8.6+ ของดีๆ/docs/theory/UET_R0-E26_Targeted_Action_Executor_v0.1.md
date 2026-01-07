# UET R0-E26 — Targeted Action Executor (Non-evidence) v0.1
**Goal:** เมื่อ triage/action_plan บอกว่า “ต้องลด dt” หรือ “ต้องทำ determinism diagnose”
ให้มีตัว executor ที่ทำงานได้จริงและบันทึก audit trail ชัดเจน โดยไม่ต้องรอ manual edit

## What it does (v0.1)
- อ่าน `action_plan.json`
- สำหรับแต่ละ group ที่มี action `DECREASE_DT_PRESET`:
  - เลือก multiplier ที่ **เข้มที่สุด** (min multiplier ใน actions)
  - พยายาม apply กับ:
    - `band_dt_presets` (per band|model|integrator)
    - `dt_presets` (per model|integrator)
  - รองรับ schema หลายแบบ (nested dict หรือ list of rows)
  - ถ้า `--apply` จะ:
    - สร้าง backup `.bak.<timestamp>`
    - เขียน preset ที่ถูกปรับแล้วกลับไปที่ไฟล์

Outputs ใน run_dir:
- `targeted_actions_applied.json`
- `targeted_actions_applied.md`

## loop_driver integration
Stage 7.62 เรียก executor หลัง action_router และก่อน propose/apply อื่น ๆ

Params:
- `targeted_action_executor` (default true)
- `targeted_action_allow_when_hold` (default false)
  - ถ้า action_router บอก `hold_apply=true` จะไม่ apply โดย default
  - เปิด option นี้เมื่อคุณต้องการ “ลด dt เพื่อความปลอดภัย” แม้ยัง hold
- `targeted_action_min_multiplier` (default 0.1)

## Next step (R0-E27)
- เพิ่ม action type อื่น ๆ: ปรับ backtracking policy / tolerance / caps
- เพิ่ม rule “do-not-touch list” สำหรับ presets ที่ถูก baseline lock แล้ว
