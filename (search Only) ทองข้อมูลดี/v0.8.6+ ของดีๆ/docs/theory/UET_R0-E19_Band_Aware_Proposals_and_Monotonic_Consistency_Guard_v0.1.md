# UET R0-E19 — Band-aware dt Proposals + Monotonic Consistency Guard v0.1
**Goal:** ทำให้การ “อัปเดต presets” ปลอดภัยขึ้นและไม่ลด dt เกินจำเป็น
1) **Band-aware proposals**: ปรับ dt เฉพาะ (band×model×integrator) ที่ “fail จริง” จาก stress gate
2) **Monotonic consistency guard**: ถ้า dt เล็กลงแต่ผล “แย่ลงอย่างมีนัย” → ถือว่า evidence ยังไม่เสถียร  
   → block การ apply อัตโนมัติสำหรับกลุ่มนั้น (ต้องเพิ่ม sample/ปรับ metric ก่อน)

---

## 1) New scripts
### 1.1 `scripts/failing_groups_from_gate_report.py`
- Input: `stress_gate_report.json`
- Output: `failing_groups.json` มี `groups: ["band|model|integrator", ...]`
- ใช้เป็น filter ให้ proposal script แนะนำ update เฉพาะกลุ่มที่ fail ใน stress gate

### 1.2 `scripts/monotonic_consistency_check.py`
- Input: variant summary (group = `band_model_integrator_variant`) ซึ่งอาจ merge มาหลาย zoom rounds
- ตรวจว่าเมื่อ `dt_scale` ลดลง (dt เล็กลง) **pass_rate ไม่ควรลดลง**
- Flag **violation** เมื่อ:
  - `pass_rate_lo + delta < pass_rate_hi` และทั้งคู่มี `n >= min_n`
  - ถ้า “มีนัย” โดย `ci_hi_lo < ci_lo_hi` → ใส่ลง `blocklist_band_model_integrator`

Output: `monotonic_report.json`
- `status`: OK/BLOCK
- `blocklist_band_model_integrator`: รายชื่อ group ที่ควร “หยุด apply อัตโนมัติ”
- `violations`: รายละเอียด pair ที่ผิด monotonic

---

## 2) Update scripts
### 2.1 `propose_preset_updates_from_variant_summary.py`
เพิ่ม `--only_groups_json failing_groups.json`
- ถ้าให้มา จะ output proposals เฉพาะ group ที่อยู่ใน list

### 2.2 `apply_preset_updates.py`
เพิ่ม `--blocklist_json monotonic_report.json`
- ถ้า group อยู่ใน blocklist จะ skip update

---

## 3) loop_driver behavior (อัตโนมัติ)
เพิ่ม params:
- `band_aware_updates` (default true)
- `monotonic_check` (default true)
- `monotonic_min_n` (default 50)
- `monotonic_delta` (default 0.05)

ในลูป:
1) หลัง stress gate FAIL → สร้าง `failing_groups.json`
2) หลังได้ `adaptive_summary` → สร้าง `monotonic_report.json`
3) proposal จะ filter ด้วย failing_groups (ถ้าเปิด band_aware_updates)
4) apply จะใช้ blocklist (ถ้าเปิด monotonic_check)

---

## 4) Recommended defaults
- `band_aware_updates: true` (กันลด dt ทั้งระบบ)
- `monotonic_check: true`
- `monotonic_min_n: 50` (ถ้า n น้อยอาจไม่เสถียร)
- `monotonic_delta: 0.05`

---

## Next step (R0-E20)
- Auto “resample policy”: ถ้าโดน blocklist ให้เพิ่ม `jitters_per_case` หรือเพิ่ม seeds / n_per_case อัตโนมัติ แล้ว rerun เฉพาะกลุ่มนั้น
- Add metric-level diagnosis mapping: violation ที่เกิดมักสัมพันธ์กับ fail_code ใด → แนะนำแก้ metric/threshold เฉพาะจุด
