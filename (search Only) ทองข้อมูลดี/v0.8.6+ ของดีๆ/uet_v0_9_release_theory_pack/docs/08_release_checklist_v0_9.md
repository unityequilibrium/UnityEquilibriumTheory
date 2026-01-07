# UET v0.9 Release Checklist (Public Repo) — Draft
Date: 2025-12-19

> เป้าหมาย: ทำให้ release เป็น **reproducible + reviewable + public-friendly**  
> หลักการ: **Layer A ต้อง “รันได้จริง”** และมี artifacts ครบ / Layer B–D เป็น roadmap+tests

---

## 0) Definition of Done (DoD) สำหรับ v0.9
Release v0.9 ถือว่า “ผ่าน” เมื่อ:

### A. Reproducibility (ต้องทำได้ทุกเครื่อง)
- [ ] มี `requirements.txt` หรือ `pyproject.toml` + วิธีติดตั้ง (Windows/Linux)
- [ ] `run_all.ps1` / `run_all.sh` ที่ “รัน 1 คำสั่ง” แล้วได้ผลครบ:
  - run → validate → aggregate → phase_prob → plots → gallery
- [ ] มี example “fast regression” (grid เล็ก + seeds น้อย) รันจบได้ไว

### B. Scientific/Operational Artifacts (ต้องตรวจย้อนกลับได้)
- [ ] ทุก suite มี:
  - `UET_final_summary.csv`
  - `validation_transient_*.json`
  - `validation_bias_*.json`
  - `phase_prob.csv` + `Strength`
  - `Strength_heatmap.png`
  - `MeanGrade_heatmap.png` (optional แต่แนะนำ)
- [ ] ทุก figure มี caption/metadata (axes ranges, seeds, validator versions)

### C. Documentation (คนใหม่เข้าใจใน 15 นาที)
- [ ] README มี:
  - repo ทำอะไร
  - วิธีรัน 3 คำสั่งหลัก
  - “อ่านผล” ด้วย Strength
- [ ] docs มี:
  - Overview / Quickstart / Matrices / Validators / Outputs
  - MI Card spec + example 1–2 อัน (อย่างน้อย TH-ECO prototype)
- [ ] Glossary ครบคำที่คนงง (phase, bias, seed, sweep, Strength)

### D. Stability & Regression
- [ ] รัน baseline sweep (เล็ก) แล้ว “รูปเฟส” ไม่เปลี่ยนผิดปกติเมื่อเทียบกับ v0.8.5+
- [ ] Validator thresholds ไม่เปลี่ยนโดยไม่ bump version
- [ ] Aggregator ไม่ทำให้คอลัมน์สำคัญเป็น NaN (delta/s extraction ต้องผ่าน)

---

## 1) Freeze List (สิ่งที่ต้อง lock ก่อน tag)
- [ ] `scripts/run_suite.py` (API/CLI)
- [ ] `scripts/aggregate_final_summary.py` (schema ของ summary)
- [ ] `scripts/validate_bias_v2.py` + thresholds
- [ ] `scripts/validate_transient_v3.py` + thresholds
- [ ] Plot scripts ที่ใช้ใน release (Strength/MeanGrade)
- [ ] Example matrices ที่เป็น canonical:
  - beta×s, beta×k_ratio, beta×delta (seed10)
- [ ] Docs: MI spec + Outputs interpretation

---

## 2) Release Suites ที่แนะนำให้ “เป็นมาตรฐาน” ใน v0.9
> เน้น cross-sweep 2 แกน + seeds เพื่อ phase statistics

### Suite A: beta × s (canonical)
- Purpose: lock-in vs tilt (symmetry breaking)
- Output: Strength heatmap เป็น figure หลักของ release

### Suite B: beta × k_ratio
- Purpose: balance mechanisms (C vs I strength)

### Suite C: beta × delta
- Purpose: landscape depth / inertia proxy (hysteresis proxy)

**Optional**
- s × delta (phase-boundary hunting)

---

## 3) Quality Gates (ต้องผ่านก่อนปล่อย public tag)
### Gate G1: Run integrity
- [ ] ไม่มี missing run directories/partial outputs
- [ ] accepted==1 ใน summary (หรือไม่มี status fail)

### Gate G2: Phase sanity
- [ ] Strength shift ตาม s แบบ “ถูกทิศ” (s>0 → BIAS_C มากขึ้น, s<0 → BIAS_I มากขึ้น)
- [ ] Seeds ≥ 10 สำหรับ release figures

### Gate G3: Plot completeness
- [ ] มี Strength + MeanGrade maps ทุก suite
- [ ] มี gallery (`figs/.../index.md`) รวมรูปทั้งหมด

### Gate G4: Public readiness
- [ ] License (MIT/Apache-2.0 ฯลฯ) + citation policy
- [ ] CODE_OF_CONDUCT + CONTRIBUTING
- [ ] Issue templates (Bug / Feature / New MI Card)

---

## 4) Release Artifact Bundle (แนะนำ)
สร้าง `release_artifacts/v0.9/` แล้ว zip แนบใน GitHub release:
- matrices/ (canonical)
- scripts/ (รุ่นที่ใช้สร้างผล)
- runs_*/ (อย่างน้อย summary + validation + phase_prob + figs)
- docs/ (รุ่นที่อธิบายตรงกับผล)
