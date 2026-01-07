# UET R0-E18 — Band-Priority Zoom Policy + Monotonic Smoothing v0.1
**Goal:** ทำให้ zoom dt search (R0-E17) “ฉลาดขึ้น + เสถียรขึ้น”
1) **Band-priority policy**: band ต่างกันควร zoom ต่างกัน (HARD ต้อง conservative กว่า DEMO)
2) **Monotonic smoothing**: ในเชิงตรรกะ เมื่อ dt เล็กลงควร “ไม่แย่ลง” แต่ข้อมูลจริงมี noise  
   → ใช้ isotonic regression (PAVA) บังคับให้ `pass_rate` และ/หรือ `ci_lo` เป็น monotone กับ `-log(dt_scale)`

---

## 1) New script
### `scripts/monotonic_smooth_variant_summary.py`
Input: merged variant summary CSV  
Output: CSV เดิม + เพิ่มคอลัมน์:
- `smoothed_pass_rate`
- `smoothed_ci_lo`

วิธี: ทำ PAVA ต่อกลุ่ม `band|model|integrator|code` โดย x = `-log(scale)` (scale เล็ก → x ใหญ่) แล้วบังคับ y(x) ไม่ลดลง

> ใช้เพื่อ “ตัด noise” ตอนตัดสิน bracket ใน zoom, ไม่ใช่แทน gate หลักของ stress

---

## 2) Update: `scripts/suggest_zoom_scales.py`
เพิ่มความสามารถ:
- `--band_policy_json` : กำหนด policy ต่อ band เช่น min_scale/eps_ratio/step_down/mid_weight
- `--use_smoothed` : ใช้ `smoothed_pass_rate/smoothed_ci_lo` ถ้ามี

**mid_weight (สำคัญ)**
- 0.0 = เลือกใกล้ fail (scale เล็กกว่า → conservative)
- 1.0 = เลือกใกล้ pass (scale ใหญ่กว่า → aggressive)

---

## 3) Template policy
ไฟล์: `UET_R0-E18_band_zoom_policy_template.json`  
ตัวอย่าง:
- DEMO: aggressive (step_down 0.7, mid_weight 0.65, min_scale 0.2)
- HARD: conservative (step_down 0.4, mid_weight 0.35, min_scale 0.05, max_new_scales_per_group 2)

---

## 4) loop_driver รองรับ smoothing + policy
เพิ่ม params ใน `loop_config.json`:
- `zoom_use_smoothing`: true/false (default true)
- `zoom_band_policy_json`: path to policy json (optional)

ใน zoom round:
1) merge summary
2) (ถ้าเปิด smoothing) run `monotonic_smooth_variant_summary.py`
3) run `suggest_zoom_scales.py --use_smoothed --band_policy_json ...`

---

## 5) Recommended defaults
- `zoom_use_smoothing: true`
- ใช้ policy template แล้วปรับตามผลจริง
- `zoom_rounds: 2` เริ่มต้น

---

## Next step (R0-E19)
- ทำ “band-aware proposal” ต่อ dt presets: ลดเฉพาะ band ที่ fail และคง band ที่ผ่าน
- เพิ่ม monotonic check ว่า “scale ลดแล้วไม่ควร fail มากขึ้น” ถ้าผิด → flag ว่า stochastic/metric issue
