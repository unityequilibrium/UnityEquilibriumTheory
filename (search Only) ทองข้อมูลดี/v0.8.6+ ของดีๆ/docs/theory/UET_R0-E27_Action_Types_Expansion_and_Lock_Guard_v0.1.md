# UET R0-E27 — Action Types Expansion + Lock/Do-Not-Touch Guard v0.1

## Goal
1) ขยาย “ชนิด action” ที่ action_router สามารถแนะนำได้ (ยังไม่บังคับ apply ทุกอย่าง)
2) เพิ่ม **Lock Guard** + **Do-not-touch** เพื่อกันการแก้ presets ที่ถูกล็อกเป็น baseline แล้ว

---

## 1) Action types ที่เพิ่มใน `action_router.py`
- `TUNE_BACKTRACKING`  
  ใช้เมื่อ ENERGY_INCREASE เด่น หรือ backtracking density สูง
- `ENABLE_NUMERIC_GUARDS`  
  ใช้เมื่อ BLOWUP / NAN_INF เด่น (ชี้ว่าควรใช้ caps / safe exp/log / clamp)
> หมายเหตุ: ใน v0.1 executor จะ “บันทึก” actions เหล่านี้เป็น `unapplied_actions`
เพื่อให้มนุษย์ตัดสินใจ/หรือรอ executor รุ่นถัดไปที่รองรับการ apply จริง

---

## 2) Lock/Do-not-touch guard ใน `targeted_action_executor.py`
เพิ่ม args:
- `--baseline_manifest <path>` : ใช้ตรวจ best-effort ว่าไฟล์ presets ถูกล็อกหรือไม่
- `--do_not_touch_json <path>` : ไฟล์กำหนดรายการห้ามแตะ
- `--respect_lock` : เปิด lock guard
- `--allow_modify_locked` : override (อันตราย ใช้เมื่อรู้ว่ากำลังทำอะไร)

รูปแบบ do_not_touch_json (ตัวอย่าง):
```json
{
  "files": [
    "dt_ladder_runs_seeds/dt_presets_strict/dt_presets_strict.json"
  ],
  "groups": [
    "BAND_A|MODEL_X|rk4"
  ]
}
```

Behavior:
- ถ้า group อยู่ใน do-not-touch → `skipped=true`
- ถ้าไฟล์อยู่ใน do-not-touch หรือ baseline_manifest บอกว่าล็อก → จะไม่เขียนทับ (แม้มี --apply)

Outputs เพิ่ม:
- ใน `targeted_actions_applied.json` จะมี `skipped`, `skip_reasons`, `unapplied_actions`

---

## 3) loop_driver params
- `targeted_action_respect_lock` (default true)
- `targeted_action_allow_modify_locked` (default false)
- `targeted_action_do_not_touch_json` (default "")

---

## Next (R0-E28)
- เพิ่ม executor ที่ apply `TUNE_BACKTRACKING` และ `ENABLE_NUMERIC_GUARDS` อย่างปลอดภัย
  (ต้องนิยาม schema ของ solver-policy/caps ชัดก่อน)
