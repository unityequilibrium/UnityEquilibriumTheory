# UET R0-E16 — One-Command Loop Driver + Adaptive dt Grid v0.1
**Goal:** รวม R0-E13→E15 ให้ “สั่งครั้งเดียว” แล้วระบบทำ:
1) stress test (generalization)
2) gate
3) ถ้า FAIL → adaptive stress targeting + A/B dt scales
4) propose dt preset updates
5) apply updates
6) วนซ้ำจน PASS หรือถึง max_iters
7) freeze baseline manifest พร้อม evidence hashes

> มุ่งให้ pipeline “repeatable + audit-able” มากกว่าทำ manual ทีละคำสั่ง

---

## 1) New
- `scripts/loop_driver.py`
- `freeze_baseline_manifest.py` เพิ่ม `--extra_files` (semicolon-separated) เพื่อ hash artifacts เพิ่ม

---

## 2) Config template
ใช้ `loop_config.json` (ดู template ที่ให้)

**paths**
- `stress_spec`
- `band_dt_presets`
- `dt_presets` (optional)
- `baseline_manifest`
- `work_dir`
- `scripts_dir` (default: `scripts`)

**params**
- `max_iters`
- `min_pass_rate`, `min_ci_lo`
- `dt_scales_grid` เช่น `1.0;0.7;0.5;0.35;0.25`
- `top_groups`, `cases_per_group`, `jitters_per_case`
- `prefer_keep_if_pass` (dt×1 ผ่านแล้วไม่ลด)
- `apply_only_gate_pass` (apply เฉพาะ proposal ที่ gate ผ่าน)
- `freeze_extra_files` (optional)

---

## 3) Run (one command)
```bash
python scripts/loop_driver.py --config loop_config.json
```

**Dry-run (ดู command plan)**
```bash
python scripts/loop_driver.py --config loop_config.json --dry
```

---

## 4) How it decides dt scale
Adaptive stress สร้าง variant ตาม `dt_scales_grid`:
- ถ้า dt×1 ยัง FAIL แต่ dt×0.5 ผ่าน → proposal จะเลือก 0.5
- ถ้าผ่านหลาย scale → default เลือก scale เล็กสุดที่ผ่าน (robust)
- ถ้า `prefer_keep_if_pass=true` → ถ้า dt×1 ผ่าน จะไม่ลด (คง efficiency)

---

## 5) Evidence + Baseline
ทุก iteration จะบันทึก evidence hash ลง `baseline_manifest.json` (best-effort) เช่น:
- stress gate report
- adaptive summary
- proposals
- updated presets
- และไฟล์ extra ที่กำหนดเพิ่ม

---

## Next step (R0-E17)
- ทำ dt_scales “adaptive search” (binary/zoom) แทน grid คงที่
- ทำ auto “band-aware scale” (บาง band ลด, บาง band คง)
