# UET R0-E25 — Auto-Evidence Budgeter + Stop Rules v0.1

## Goal
เมื่อ action_router แนะนำ `INCREASE_EVIDENCE` เราไม่อยาก “เพิ่ม seed ไปเรื่อย ๆ” แบบไร้เพดาน
R0-E25 เพิ่มตัว **budgeter** เพื่อ:
- กำหนดจำนวน evidence ที่เหมาะสมต่อกลุ่ม (band|model|integrator)
- มี **stop rules** ชัดเจนว่าเมื่อไร “ควรหยุดเพิ่มหลักฐาน” แล้วหันไปแก้ solver/สมการ/พารามิเตอร์แทน

---

## New script
### `scripts/evidence_budgeter.py`

**Inputs**
- `--action_plan_json` (required): `action_plan.json` จาก R0-E23
- `--variant_summary_csv` (required): `adaptive_variant_summary_merged.csv` หรือไฟล์ merged ล่าสุด
- `--triage_json` (optional): `metric_triage_report.json`
- `--monotonic_report_json` (optional): `monotonic_report.json`
- `--determinism_report_json` (optional): `determinism_report.json`

**Outputs**
- `evidence_budget.json`
- `evidence_budget.md`

---

## Stop rules (conservative defaults)
- STOP ถ้า determinism report = `UNSTABLE` (optional flag)
- STOP ถ้า n_total ของกลุ่ม >= `max_n_for_evidence` (default 500) แล้วยัง BLOCK → “ไม่ใช่เรื่อง sample แล้ว”
- STOP ถ้า blowup/nan_inf rate สูง (default >= 0.02) → ต้องลด dt/แก้ stability ไม่ใช่เพิ่มหลักฐาน
- มี **global cap** ของ extra seeds รวมทั้งระบบ (`max_total_extra_seeds`)

---

## loop_driver integration
เพิ่ม stage:
- **7.65 Evidence budgeter** → สร้าง evidence_budget.*
- Evidence executor (7.7) จะ:
  - ถ้า evidence_budget มี → ทำ evidence แบบ **per-group schedule**
  - ถ้าไม่มี → fallback ไป schedule เดิม (global)

เพิ่ม params:
- `evidence_budgeter` (default true)
- `evidence_budget_max_n` (default 500)
- `evidence_budget_total_extra_seeds` (default 200)
- `evidence_budget_max_rounds` (default 3)
- `evidence_budget_stop_on_unstable` (default true)

---

## Why it matters
- ทำให้ loop “ไม่เผา compute” แบบไร้เพดาน
- ทำให้เรารู้ว่าจุดไหนต้องแก้ **สมการ/solver** จริง ๆ ไม่ใช่เพิ่ม sample
- ลดโอกาส drift ของ baseline เพราะ evidence บางกลุ่มไม่คุ้มค่า

---

## Next step (R0-E26)
- “Executor for actions” ขั้นต่อไป: ถ้า budgeter บอก STOP เพราะ blowup/nan_inf → ออก proposal ลด dt preset/เพิ่ม stability caps แบบ targeted
