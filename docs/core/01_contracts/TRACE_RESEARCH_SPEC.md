# UET Spacetime Thermodynamic Trace

สถานะเอกสาร: candidate mathematical model / open constitutive mechanism

เอกสารนี้ล็อก ontology และลำดับการทดสอบของ trace lane โดยไม่ยกระดับ
ข้อสรุปของหัวข้อ 0.13, 0.26 หรือ 0.1 เกิน artifact ที่รองรับ

## 1. Ontology

- C คือสถานะเชิงสสารหรือโครงสร้างที่ระบบกำลังวิวัฒน์ เช่น density,
  order parameter หรือ matter state
- sigma_C คือ source เชิง diagnostic ของการเปลี่ยนแปลง:
  sigma_C(x,t) = |partial_t C|^2 / M0 >= 0
- I_trace คือ functional ของ source history:
  I_trace(x,t) = integral G_ret(x-x',t-t') sigma_C(x',t') dx' dt'
- I_trace ไม่ใช่สสารใหม่ ไม่ใช่ mass state และไม่ถูกส่งเข้า operator ใหม่
  ในฐานะ field อิสระ
- source_history เป็น cache เชิงคำนวณเท่านั้น
- อินฟราเรดหรือ heat map เป็น observable proxy ที่ใช้ได้ในบางระบบ ไม่ใช่
  universal definition ของ I_trace

## 2. Baseline functional

Baseline lane ใช้

Omega_0[C] = integral [V(C) + kappa/2 |grad C|^2] dx

ใน implementation เดิม information-field terms จะถูกคำนวณเพิ่มเฉพาะเมื่อ
ผู้เรียกส่ง I ใน legacy lane:

1/2 |grad I|^2 + 1/2 m_I^2 I^2

normalized core ใช้ kappa_I เป็น candidate coefficient ของ m_I^2;
จุดนี้ยังไม่ใช่ SI derivation

การลดลงของ Omega ใน baseline เป็น gradient-flow/Lyapunov diagnostic
ไม่ใช่หลักฐานว่า energy รวมของระบบปิดอนุรักษ์ครบทุกช่องทาง

## 3. Causal kernel

trace lane ใช้ retarded telegraph-diffusion constitutive ansatz:

(tau_m partial_t^2 + partial_t - D_m laplacian + lambda_m) G_ret
= delta(x) delta(t)

ข้อกำหนดของ config:

- D_trace > 0
- tau_trace > 0
- lambda_trace >= 0
- v_trace = sqrt(D_trace/tau_trace)
- ถ้าเป็น SI lane ต้องตรวจ v_trace <= c
- G_ret = 0 ก่อน source และนอก discrete propagation cone
- boundary condition ต้องประกาศเป็น periodic หรือ zero

docs/core/uet_trace.py::compute_spacetime_trace เป็น finite-support
discrete approximation ของ ansatz นี้ ไม่ใช่ closed-form Green function
และไม่ควรถูกเรียกว่า derivation ที่พิสูจน์แล้ว

## 4. State interface

spacetime_trace_v1 คืน:

UETStepResult:
  C
  V
  trace_observable
  energy_ledger
  diagnostics

legacy modes ยังทำงานด้วย compatibility adapter เดิมและ canonical tuple
order คือ (C, V, I). Trace mode ไม่รับ I เป็น input state

## 5. Accounting สองชั้น

### Normalized lane

รายงาน source production, trace storage และ trace decay เป็น proxy พร้อม
ระบุ closure_status = proxy_only_open_SI_accounting. ห้ามเรียก proxy เหล่านี้
ว่า Joule หรือบอกว่า energy หายไป

### SI lane

ต้องล็อกหน่วยตามระบบก่อน:

- heat lane: T เป็น K, heat flux เป็น W/m2, entropy production เป็น
  W/(K m3)
- galaxy lane: ประกาศ convention ของ C และ uncertainty ต่อจุด
- I_trace ต้องเลือกว่าจะเป็น normalized trace หรือ dimensional energy/entropy
  trace ต่อ lane
- Landauer E_min = k_B T ln(2) เป็น external lower-bound constraint เท่านั้น
  และไม่ใช่ derivation ของ dimensionless core beta

## 6. Wave 4 benchmark: Cattaneo

ทดสอบกับ synthetic/analytical control system:

tau_q partial_t q + q = -k grad T

เทียบ Fourier instantaneous response, Cattaneo delayed response และ
UET trace observable โดยเก็บ:

- lag time
- phase shift
- hysteresis-loop area
- propagation speed
- source sign
- energy-ledger closure

gate เบื้องต้น:

- analytical residual <= 1e-10
- causal leakage <= 1e-8 ของ peak
- source negativity <= 1e-12
- lag/hysteresis ต่างจาก analytical reference ไม่เกิน 5%
- ผล converge เมื่อเปลี่ยน dt และ dx

ข้อมูล Cattaneo ใน wave นี้เป็น simulation-only จนกว่าจะมี source-backed
external benchmark

## 7. Return path to topics

### Topic 0.1

ต้องมีสาม baseline: baryonic/Newtonian, instantaneous UET และ
history-dependent trace. ก่อนใช้ galaxy claim ต้องผ่าน full curve, uncertainty,
competitor baseline, parameter lock และ holdout. Summary rows ปัจจุบันยังไม่
ปิดประวัติของกาแล็กซี จึงมีเพียง readiness manifest

### Topic 0.26

ใช้คำว่า causal history-dependent response of the dynamic frame แทน
dynamic information-fluid. หัวข้อนี้ยังเป็น candidate mechanism layer และ
ห้ามใช้ FAIL/WARN ของ 0.1 เป็นหลักฐานยืนยันตัวเอง

### Topic 0.13
