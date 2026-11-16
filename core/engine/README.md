# UET engine (`core/engine`)

> สถานะ: **ร่าง** (2026-11-16) รอผู้เขียนตรวจ เป็น infrastructure ไม่เพิ่มฟิสิกส์ใหม่ ไม่เปลี่ยนระดับหลักฐานของ claim ใด
> ทุกฟังก์ชันห่อโมดูลที่ derive แล้วและมี physics test อยู่แล้ว (`core/03_lanes`, `core/02_equations`)

## ทำไมต้องมี

ก่อนหน้านี้ topic ทุกตัวใช้ engine ของตัวเอง (`Engine_*.py` ราว 70 ไฟล์) ส่วนการ import จาก core ส่วนใหญ่มีไว้หา path (`core.core_paths` 166 ครั้ง)
ไม่มี topic ไหนเรียกสมการของ parent action เลย ผลของ topic จึงยังไม่ใช่หลักฐานของ UET engine นี้คือทางเข้าเดียวจาก topic ไปยังสมการแกน

หมายเหตุ: `core/__init__.py` (v0.9) ยังส่งออก `get_params(topic)` ที่ให้ κ, β แยกตาม topic ซึ่งเป็นระบบ parameter เดิม และขัดกับหลัก "กฎเดียวทุกสเกล"
engine ไม่ใช้ระบบนั้น

## วิธีใช้

```python
from core.engine import layer1, layer23, lanes

p = layer1.CanonicalParameters(m_psi_ev=5.1e-3, g_c_ev=5.1e-10, xi_c=0.0)
layer1.portal_alpha(p)                      # แรงที่ห้าเทียบกับแรงโน้มถ่วง
layer23.lifetime(f0, p0, n, f_min)          # τ = ∫dF/P(F)
layer23.abundance_ratio(tau_a, tau_b)       # N_a/N_b = τ_a/τ_b
```

| โมดูล | สิ่งที่มี | มาจาก |
|---|---|---|
| `layer1` | canonical parameter, แรงที่ห้า (α, λ, ศักย์สองวัตถุใน SI), DEF/PPN, Bose fluid (λ = 8πam, ความเร็วเสียง, n a³), แรงเสียดทานของ ψ | B1b, W5, SI-1, B6 |
| `layer23` | burn law P(F), lifetime, abundance (Little's law), R*, coexistence, invasion fitness, bits ที่เขียน | A4, B7, path-A, T002/T007/T008/T009 |
| `lanes` | lane card และตัวตรวจ | ใหม่ |

ขอบเขตที่ลงทะเบียนแล้ว (`layer1.REGISTERED_LIMITS`): T005 (g_c), T001 (ξ_c), T015 (He II อยู่นอก action) ห้าม topic ตั้งค่าเหล่านี้เอง

## Lane card

แต่ละ topic ที่จะใช้ engine ต้องมีไฟล์ lane card (แม่แบบ: [`LANE_CARD_TEMPLATE.json`](LANE_CARD_TEMPLATE.json)) ระบุ:
- `reach`: `LAYER1`, `LAYER23`, `LAYER1_AND_LAYER23` หรือ `OUTSIDE_ACTION`
- ใน topic นั้น χ, ψ, F, P, b คืออะไร (นิยามจากฟิสิกส์มาตรฐานของระบบนั้น)
- ฟังก์ชันของ engine ที่ใช้
- ทุกตัวเลขต้องมีที่มา: `DERIVED`, `MEASURED_INDEPENDENT`, `REGISTERED_LIMIT` หรือ `CALIBRATION` (ห้าม calibrate บนข้อมูลชุดที่ใช้เทียบ) **ไม่มีค่า fit เฉพาะ topic**
- engine เดิมของ topic เก็บไว้เป็น `LEGACY_UNREVIEWED`

`lanes.validate_lane_card(card)` ตรวจรูปแบบเท่านั้น ไม่ได้ตัดสินว่าฟิสิกส์ถูก ส่วนนั้นเป็นงานของ physics test และ Test Card
การบังคับให้ topic ทุกตัวต้องมี lane card จะเป็น gate ใหม่ ต้องให้ผู้เขียนอนุมัติก่อน (ยังไม่ได้เพิ่ม)

## แผนที่ topic (AI ประเมินจาก screen 2026-11-16 ยังไม่ได้เขียน lane card)

| reach ที่คาด | topic | หมายเหตุ |
|---|---|---|
| LAYER1 | 0.19 GR, 0.2 black hole, 0.3 Hubble, 0.1/0.15 dark matter, 0.4 superconductivity (GL), 0.26 | ψ, แรงที่ห้า, DEF, ξψ²R |
| LAYER23 | ดาว (T002/T008/T014), 0.22 biophysics, 0.11 phase transitions บางส่วน, ระบบนิเวศ/chemostat, laser | ต้องมี F และ P จากฟิสิกส์ของระบบ |
| OUTSIDE_ACTION | 0.5, 0.6, 0.7, 0.8, 0.16, 0.17, 0.20, 0.21, 0.9 | action ไม่มี fermion และ gauge field ต้องให้ผู้เขียนตัดสินใจขยาย action ก่อน |
| OUTSIDE_ACTION (ตัดสินแล้ว) | 0.13 He-4 Φ | phenomenological closure (ผู้เขียน 2026-11-16, หลัง T015) |
| ต้องดูเพิ่ม | 0.0, 0.10, 0.12, 0.14, 0.18, 0.23–0.25 | integration, คณิตศาสตร์ หรือ proxy data |

## ถัดไป

1. ผู้เขียนตรวจ API และรูปแบบ lane card
2. นำร่องหนึ่ง topic: เขียน lane card แล้วคำนวณผลหลักของ topic ด้วย engine เทียบกับผลเดิม ผลที่เปลี่ยนหรือตกต้องบันทึกตรง ๆ
3. ฟังก์ชันใหม่ใน engine ต้อง derive และมี physics test ใน `core/03_lanes` ก่อนเสมอ engine เป็นแค่ทางเข้า
