# UET Core Equation-Family Contract

เอกสารนี้เป็นการลด code surface จาก 1,450 จุดให้เป็นโครงสร้างที่ตรวจได้ระดับโมดูล
โดยไม่ถือว่าทุกบรรทัดในโค้ดเป็นสมการฟิสิกส์

ผล machine-readable อยู่ที่
[`uet_core_equation_family_contract.json`](artifacts/uet_core_equation_family_contract.json)
และสร้างซ้ำได้จาก
[`build_uet_core_equation_family_contract.py`](../scripts/audit/build_uet_core_equation_family_contract.py)

## Coverage

- core code-surface files: `32`
- module paths ที่ถูก assign: `32/32`
- equation families: `9`
- support/contract families: `3`
- contract status: `BLOCKED` เพราะ upstream compatibility และ causal gate ยังไม่ผ่าน

การ assign ครบ 32 โมดูลหมายถึงไม่มี implementation module หลุดจาก ownership แล้ว
แต่ไม่ได้หมายความว่าสมการในทุกโมดูลถูกพิสูจน์แล้ว

## Equation families

| Family | Standard counterpart | Unit lane | Mathematical status | Special-case status |
|---|---|---|---|---|
| Legacy master | effective free-energy/gradient flow | normalized/open | contradiction + conflict | not established |
| Matter-space | Landau-Ginzburg + damped response | normalized v1 | internal gates pass, causal gate fails | conditional only |
| Trace | causal memory convolution | normalized v1 | internal comparator | Markovian limit conditional |
| Covariant response | covariant response/scalar-tensor parent | natural candidate | conditional, not full GR | algebraic/local GR null only |
| Covariant diffusion | relativistic diffusion/Maxwell-Cattaneo | natural/normalized | constitutive conditional | Markovian comparator only |
| Hyperbolic phase | telegraph phase-field | normalized comparator | comparator only | not UET special-case proof |
| O(2) superfluid | relativistic finite-density O(2) | natural units | conditional tree-level | lane-specific only |
| Noether mapping | U(1)/O(2) current + hydrodynamic map | natural + normalized | many-to-one map | does not prove legacy C |
| Lorentz utilities | Lorentz transform/causal cone | normalized/natural | utility checks only | no global invariance claim |

## Non-equation contracts

- `parameter_contract`: mixed normalized/natural/SI policy; beta/Landauer semantics remain open
- `observable_contract`: measurement operator and physical unit mapping remain open
- `support_and_adapters`: solver/proof/validation code cannot make an independent physics claim

## หลักการที่ปิดได้จาก contract นี้

1. `C` ไม่มีความหมายทางกายภาพสากล ต้องเลือก lane เช่น order parameter, density หรือ O(2)
   Noether charge
2. Standard counterpart ไม่เท่ากับ UET derivation
3. Special case ต้องมี explicit limit, ontology/units เดียวกัน และ residual verification
4. Trace `R` เป็น derived observable ไม่ใช่ state ที่เพิ่มพลังงานหรือย้อนกลับไปควบคุม dynamics
5. โมดูล support ไม่สามารถเลื่อน claim ของ equation family ที่เป็นเจ้าของสมการไม่ได้

## ข้อสรุปปัจจุบัน

หลัง assign ครบทุก core module เราพูดได้แม่นขึ้นว่า UET ไม่ได้มี “สมการเดียว” ที่ครอบคลุม
ทุก topic ใน implementation ปัจจุบัน แต่มีหลาย equation families ที่สถานะต่างกันมาก:

- legacy family มี conflict จริง
- matter-space และ covariant/O(2) families เป็น candidate ที่มีบาง gate ผ่าน
- standard formulas ใน topic อื่นเป็น baselines/comparators
- observables และ SI mapping ยังไม่ปิด

ดังนั้นยังไม่ควรสรุปว่า “ทฤษฎีเก่าทั้งหมดเป็นกรณีพิเศษของ UET” จนกว่าจะมี limit proof
แยกตาม family และมี observable test ของ family นั้น

