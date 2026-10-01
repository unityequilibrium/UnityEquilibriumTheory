# แผนวิจัยร่วม Topic 0.10–0.13 และ Core

วันที่: 2026-09-26 · สถานะ: **แผนวิจัยเริ่มดำเนินการแล้ว; J01 มีผลตรวจแบบจำกัดขอบเขต**

## เป้าหมายและขอบเขต

พัฒนา Topic 0.10 ให้ตอบได้ว่าแบบจำลอง UET แทนการไหลชนิดใดได้จริง เชื่อมสมดุลมวล โมเมนตัม พลังงาน และเอนโทรปีกับ Topic 0.13 ได้ภายใต้เงื่อนไขใด และต่างจากแบบจำลองมาตรฐานอย่างไร โดยใช้ Core เป็นเจ้าของ ontology, equation registry และ dependency admission การปิดงานอาจเป็นผลผ่านเฉพาะขอบเขต ผล no-go หรือการจำกัดแบบจำลองอย่างมีหลักฐาน ไม่จำเป็นต้องได้คำตอบสนับสนุน UET ทุกข้อ

เอกสารนี้เป็นแผนหลักของงานร่วม มี [รายการงานที่เครื่องอ่านได้](Data/03_Research/fluid_thermal_joint_research_plan.json) เป็นตัวควบคุมลำดับงาน **ไม่ใช่ physical acceptance gate ใหม่** ณ 2026-09-26 มีการรัน J01 แบบ representability audit แล้ว; J02 partially completed at source/protocol-candidate level; J03-J09 remain not started การรัน audit ไม่เลื่อน readiness, ไม่เปลี่ยน gate เดิม และไม่ปลด Core dependency

ฐานเผยแพร่ที่ตรวจ: `d069507651964c0f963d1568667e2a9218400e42` บน `origin/main` หลัง fetch วันที่ข้างต้น ตรวจ working tree เดิมประกอบด้วย แต่ไม่ย้ายผลที่ยังไม่ commit มาปะปนกับหลักฐานบน main รายการ evidence ใน manifest บันทึก SHA-256 ของไฟล์บนฐานเผยแพร่และระบุว่าต่างจาก working tree เดิมหรือไม่ ต้องอ่านสถานะใหม่เมื่อเริ่มแต่ละ wave

## 1. สถานะตั้งต้นและสิ่งที่ต้องต่อยอด

| งานเดิม / แหล่งควบคุม | สิ่งที่ใช้ต่อได้ | สิ่งที่ยังห้ามสรุป |
| --- | --- | --- |
| Topic 10 [speed artifact](Result/artifacts/fluid_benchmark_validation.json) | gate เดิม FAIL, speedup 1.914085 เทียบเกณฑ์ >2; finite-output diagnostic | ไม่ใช่ความแม่นยำ CFD ไม่ใช่ข้อพิสูจน์ smoothness |
| Topic 10 [chaos method](Result/artifacts/chaos_method_validation.json) | QR/tangent และ shadow ผ่าน standard controls | ยังไม่พบหลักฐาน physical fluid chaos ของ UET |
| Topic 13 [normalized pilot](../0.13_Thermodynamic_Bridge/Result/artifacts/t13_thermal_dynamical_regime_audit.json) | มี pilot แล้ว ไม่ต้องเริ่ม control เดิมใหม่โดยไม่มีเหตุผล | ไม่ใช่ SI chaos หรือ transport ที่วัดจริง |
| Topic 13 [closure matrix](../../core/07_artifacts/topic13/t13_topic13_closure_matrix.json), `core_ready_track` | O(2)/He-4 bounded composition CLOSED_FOR_CORE | ไม่ครอบคลุม graphite, complete two-fluid transport หรือ global UET |
| He-4 [matching independence](../../core/03_lanes/topic13_support/T13_HE4_MATCHING_INDEPENDENCE.md) | ใช้ calibrated effective interface โดยประกาศ protocol | equality หลัง matching ไม่ใช่ independent validation; ต้องทดสอบ observable ที่ไม่ใช้สร้าง Z/alpha |
| He-4 [shear Kubo](../../core/07_artifacts/topic13/t13_he4_normal_viscosity_kubo_audit.json) | external normal-component shear-viscosity input กับ scoped stress/FDT/entropy channel | ไม่ใช่ UET-predicted viscosity, bulk thermal conductivity หรือทั้ง transport tensor |
| Topic 13 [graphite full gate](../0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json) | แยกสาม input packages ที่ขาดได้ | ยัง BLOCKED_OPEN_T13_FULL_BRIDGE; shape fit ไม่ตรึง absolute Phi/temperature scale |
| Core [curved parent](../../core/07_artifacts/gates/core_curved_3p1_parent_gate.json) | infrastructure และ prescribed-source interfaces เฉพาะขอบเขต | parent PARTIAL; boundary และ dimensional-observable mapping ยังควบคุม |
| Core [research-room contract](../../core/00_governance/UET_RESEARCH_ROOM_BRIEF.md) | เจ้าของงานและการส่งต่อเดิม | full Topic 10 constitutive transport ต้องผ่าน relevant Core admission ก่อน |

มี drift ที่ต้องเก็บไว้ให้เห็น: topic index/metadata ยังพูดถึง latest speed pass หรือรายการงานเก่า ขณะที่ artifact ที่อ่านเป็น FAIL; report เก่าบางไฟล์ใช้คำว่า full bridge แม้ขอบเขตจริงแยก He-4/graphite ห้ามใช้ชื่อ status หรือค่า unlock ตัวเดียวตัดสินทั้งหมด แผนนี้อ่าน lane, claim boundary และ underlying evidence ประกอบ และไม่ regenerate canonical gates เพียงเพื่อให้ข้อความตรงกัน

## 2. คำถามวิจัยที่กำหนดลำดับงาน

1. **Representability:** state และ velocity map ของ Topic 10 แทน rotational/incompressible flow ได้หรือเป็นเพียง scalar relaxation/gradient-flow model?
2. **Correspondence:** ถ้าจำเป็นต้องมี momentum/phase/current state เพิ่ม จะ derive หรือประกาศ constitutive ansatz อย่างไร และเชื่อมกับ Core โดยไม่เปลี่ยนความหมาย C/Phi?
3. **Thermodynamic consistency:** coupling ให้การแลกเปลี่ยนพลังงานครบทั้งสองทิศทางและ entropy production ที่ถูกต้องหรือไม่?
4. **Independent physics:** เมื่อตรึง coefficient/normalization แล้ว ยังอธิบาย response ที่ไม่ได้ใช้ปรับเทียบได้หรือไม่?
5. **Fluid/chaos evidence:** หลังผ่าน numerical verification แล้ว dynamics เป็น stable, unresolved หรือ chaotic และสถิติต่างจาก baseline อย่างมีนัยต่อ uncertainty หรือไม่?
6. **Efficiency:** ที่ปัญหาและ error budget เดียวกัน ค่าใช้จ่าย เวลา และหน่วยความจำดีกว่าหรือไม่?

**ตัวควบคุมงานวิจัย Topic 10 ที่เสนอ:** `fluid_state_and_velocity_observable_correspondence_unestablished` ไม่ใช่การพยายามทำให้ speedup เกิน 2 ก่อนตรวจว่าสองโปรแกรมแก้โจทย์เดียวกัน

## 3. ข้อค้นพบจาก code review ที่ทำให้ต้องเริ่มตรงนี้

[Engine_UET_2D.py](Code/01_Engine/Engine_UET_2D.py) ใช้ `u=-M grad(C)` โดย M เป็น spatial scalar คงที่ใน run นั้น ใน continuum ที่ C เรียบจึงได้ `curl(u)=0` และ `div(u)=-M Laplacian(C)` โดยทั่วไปไม่เท่ากับศูนย์ นี่เป็นข้ออนุมานทางคณิตศาสตร์จาก mapping ที่เห็น ไม่ใช่ผล benchmark ที่รันแล้ว และไม่ใช่ no-go ของทุก UET realization กรณี M แปรตามตำแหน่ง singular phase หรือขอบเขตต้องวิเคราะห์แยก

การไหล periodic ที่มีวอร์ทิซิตีไม่เป็นศูนย์จึงเป็น falsification control ที่เหมาะกว่าการดูภาพ vortex ต้องตรวจ stencil/ขอบเขตว่าค่า curl ที่เห็นเป็น truncation หรือ boundary artifact หรือไม่ และตรวจการแทน initial velocity field ก่อน integration

ยังพบจุด audit เฉพาะที่ต้องเก็บเป็น counterexample tests ใน wave แรก:

- `_derive_uet_parameters` ตั้ง mobility จาก property แต่ constructor ตั้ง `mobility_M=0.5` ภายหลัง: ตรวจ actual value และเส้นทาง params/physical ทั้งสองแบบก่อนกล่าวว่าใช้ physical mobility
- `kappa=min(mu/rho, stability_limit)` อาจเปลี่ยน physical coefficient ตาม grid/time step: physical lane ต้องลด dt หรือใช้วิธีที่เหมาะสม; ห้าม cap coefficient แล้วนับว่าเป็นวัสดุเดิม
- `C=np.maximum(C,0.01)` ต้องบันทึก clip events; numerical acceptance ต้องไม่ใช้ clipping ปกปิด instability
- benchmark comparator มี diffusion, pressure sweeps แบบ homogeneous และ zero initial fields; ไม่มี full nonlinear momentum/advection และ pressure RHS จาก divergence แบบ matched incompressible solver ความเร็วเดิมจึงเป็น implementation timing เท่านั้น
- benchmark เรียก `UETMasterEquation` ไม่ใช่ `UETFluidSolver` ตัวเดียวกับ physical-property path ห้ามใช้ผล timing รับรอง engine อีกตัว
- legacy `I` ต้องระบุว่าเป็น legacy state หรือ derived trace ให้ชัด ห้ามตีความเป็น `R_gen` แล้วป้อนกลับโดยเงียบ

ทางออกที่ยอมรับได้คือ (ก) จำกัด legacy engine เป็น gradient-flow comparator หรือ (ข) ลงทะเบียน candidate state/current/momentum extension แยกต่างหากและผ่าน F0–F8 ก่อน claim การพบ no-go ของ mapping เดิมยังเป็นความคืบหน้าที่มีคุณค่า

## J01 execution checkpoint (2026-09-26)

- [Verifier](Code/03_Research/Research_Fluid_State_Velocity_Representability.py) ผ่าน periodic manufactured controls ที่กริด 16, 32 และ 64; ลำดับการลู่เข้าของ vorticity เทียบค่าต่อเนื่องเท่ากับ 1.9917 และ 1.9979
- สำหรับ mapping 2D u=-M grad(C) เมื่อ M เป็น scalar คงที่: curl ของความเร็วที่ได้ใกล้ศูนย์ ขณะที่เป้าหมายหมุนวนมี discrete divergence เป็นศูนย์และ vorticity ไม่เป็นศูนย์; การฉาย onto gradient subspace มีสัดส่วน 0 และ relative best-fit L2 residual เท่ากับ 1 ทุกกริด จึงเป็น scoped no-go สำหรับ nonzero periodic incompressible vortical targets
- การตรวจ source พบว่าค่า mobility ที่คำนวณจาก bridge ประมาณ 1749.656 ถูกเขียนทับเป็น 0.5 หลังเริ่ม base solver; PhysicalProperties.mobility=1.0 ไม่ถูกใช้ในการ derive ส่วนค่าเริ่มต้น kappa=mu/rho≈1.00381×10^-6 m²/s ต่ำกว่า stability cap 0.0488281 m²/s
- Engine 3D เก็บ/วิวัฒน์ C,I โดยไม่กำหนด state ความเร็ว/โมเมนตัม/ความดันแบบเวกเตอร์ การตรวจนี้ไม่แก้โค้ด solver และไม่สรุป no-go ของ UET ทุกแบบ
- ยังไม่ได้รัน trajectory หรือวัดจำนวน clipping events: runtime import ของ Core หยุดที่ dependency scipy ซึ่งไม่มีใน Python runtime ที่ใช้ตรวจ; source แสดง floor C>=0.01 ทั้งสอง engine จำนวน clip จึงยังไม่ทราบ
- ตัวควบคุมถัดไปของ Topic 10 คือปิดหน่วย/ontology/derivation ของ state ความเร็วใหม่กับ Core ก่อน J04 physical-flow acceptance; J02 He-4 response-source/protocol candidate (partial) และ J03 graphite package ยังคงเป็นสายงาน Topic 13 แยกกัน

ผลและ source hashes อยู่ใน [J01 artifact](Result/artifacts/fluid_state_velocity_representability_audit.json) ผลนี้ไม่เปลี่ยน speed FAIL, chaos-method PASS, readiness, Topic 13 closures หรือ dependency admission

## J02 second-sound response source/protocol checkpoint (2026-09-26)

A new source package and protocol card record the 1998 NIST review's recommended He-II second-sound phase speed along the SVP path: 20.33 m/s at T90 = 1.700 K, with 20.37 m/s at 1.650 K and 20.18 m/s at 1.750 K. The local slope (-1.9 m/s/K) is only a finite difference of rounded recommended rows. The response observable was not used to construct alpha, theta_T, Z_Phi or e0; all remain frozen. The review compiles both equilibrium anchors and sound data, so statistical independence is not claimed.

The protocol audit passes 15/15 source, constants, status and claim-boundary checks. It does not run a UET model. The recommended rows lack mapped row-level uncertainty, covariance, primary-record frequency, mode geometry and local perturbation constraints. The distinct 1947 resonance result is recorded as a cross-check only because its abstract does not establish the same pressure and temperature-scale state. The values were inspected during protocol design and are not a blind holdout; J06 needs a fresh uninspected source or must label any later comparison retrospective.

Topic 10 currently cannot predict this full-He-II thermal/entropy-wave eigenmode from its scalar C/I state or scalar-gradient velocity mapping. A coupled normal/superfluid response operator and state must first pass Core F0–F8. OpenAI's Navier–Stokes and unforced Euler work remains useful for theorem scope, norms, vorticity and residual discipline in a future incompressible-flow subproblem; neither supplies a second-sound model or validation. See the [Topic 10 applicability assessment](OPENAI_NAVIER_STOKES_APPLICABILITY_2026-09-26.md). The J01 legacy-map no-go scope and all Core/Topic 13 status labels remain unchanged.

- Protocol card: [He-4 second-sound response protocol](../0.13_Thermodynamic_Bridge/HE4_SECOND_SOUND_PROTOCOL_CARD.md)
- Source package: [machine-readable response source](../0.13_Thermodynamic_Bridge/Data/03_Research/he4_svp_second_sound_response_source_package.json)
- Audit artifact: [J02 protocol audit](../../core/07_artifacts/topic13/t13_he4_second_sound_response_protocol_audit.json)

## 4. โครงสร้างงานที่พัฒนาไปพร้อมกัน

```mermaid
flowchart TD
  A["J00 ล็อกสถานะ แหล่งข้อมูล และ admission"] --> B["J01 Topic 10: state/velocity/vorticity audit"]
  A --> C["J02 Topic 13: He-4 protocol และ observable อิสระ"]
  A --> D["J03 Graphite: สาม input packages"]
  B --> E["J04 baseline และ convergence ที่โจทย์เดียวกัน"]
  B --> F["J05 สัญญา interface จาก Core และสมดุลร่วม"]
  C --> F
  E --> G["J06 coupled He-4 pilot"]
  F --> G
  E --> H["J07 fluid-chaos diagnostic"]
  F --> H
  E --> I["J08 runtime ที่ error เท่ากัน"]
  G --> K["J09 validation / claim / dependency review"]
  H --> K
  I --> K
  D -. "graphite claim ต้องผ่าน input gates ของตน" .-> K
```

ลูกศรคือ dependency ของการ **ยอมรับผล** อนุญาตให้เตรียม source, comparator และ specification ล่วงหน้าได้ แต่ห้ามรัน candidate full constitutive lane ก่อน Core admission ที่เกี่ยวข้อง การเตรียม ordinary-fluid comparator ไม่ต้องรอ curved GR ทั้งหมด ส่วนการอ้าง self-consistent curved evolution ต้องรอ parent จริง

| ID / เจ้าของตามหน้าที่ | ผลส่งมอบที่ต้องได้ | เกณฑ์ปิดเฉพาะงาน / ทางออกเมื่อไม่ผ่าน |
| --- | --- | --- |
| J00 · Core + ทั้งสอง topic | source/hash inventory, lane map, F0–F8 obligation table, acceptance configuration และรายชื่อ gate ที่ต้องผ่านต่อ lane | ทุก dependency มี source locator, scope, status, hash; unresolved thresholds/source rows แสดง BLOCKED; ไม่ใช้ global boolean unlock |
| J01 · Topic 10 | representability audit ของ 2D/3D, mapping/units, negative controls, mobility/cap/clip report | ได้ admissible fluid state map หรือ scoped no-go พร้อมขอบเขต legacy; ไม่ยอมรับ vortex ที่มาจาก numerical error |
| J02 · Topic 13 + Core | He-4 frozen-parameter protocol card และ independent-response source manifest | ล็อก Z, theta_T, e0, alpha พร้อม covariance; ระบุ fixed variables, normal component/full material, response timescale; มี observable ที่ไม่ใช้ matching หรือบันทึก acquisition blocker |
| J03 · Topic 13 | graphite anchor/alpha, Ding-compatible C_src, physical transport เป็นสาม record แยกกัน | ใช้ existing minimal-input validators; derived/calibrated/no-go disposition ชัด; ไม่ยืม He-4 coefficient มาเติม graphite |
| J04 · Topic 10 | analytic/manufactured controls, matched NS comparator, convergence/error budget | state admission ผ่านก่อนทดสอบ physical candidate; mass/divergence/momentum/energy residual และ spatial/temporal error อยู่ใน budget ที่ล็อกก่อนผล |
| J05 · Core เจ้าของ admission; Topic 13 เจ้าของ thermal/transport; Topic 10 เจ้าของ flow | registered interface และ conservation/reciprocity tests | หน่วย/state/flux สอดคล้อง; exchange terms ยกเลิกใน total ledger; entropy accounting และ limiting cases ผ่าน; required Core gate ต้องผ่านจริง |
| J06 · ทั้งสอง topic | bounded He-4 flow–response pilot พร้อม source uncertainty และ ablations | ทำ independent held-out response หลัง freeze; thermal response ที่ต้อง conductivity/noise เพิ่มยัง BLOCKED จนมี record; no-go/limited validity รับได้ |
| J07 · Topic 10 ใช้ diagnostic Core | tangent/shadow spectrum และ stationarity/boundedness/convergence report | resolved sign เหนือ resolution budget, method agreement; positive exponent อย่างเดียวไม่ใช่ turbulence หรือ external physics validation |
| J08 · Topic 10 | work–precision curves, runtime trials, memory และ failure table | เปรียบเทียบที่ QoI/error/horizon เดียวกันก่อน timing; ถ้า accuracy ไม่ผ่าน ไม่รายงาน physical speed advantage; gate >2 เดิมแยกไว้ |
| J09 · ผู้ทบทวนด้านวิธีและหลักฐาน | lane-by-lane closure review, external comparison package, claim map | แยก standard comparator, calibrated UET candidate, independent observation และ external replication; ผลลบอยู่ในสรุป; ไม่ auto-promote topic |

การแบ่งเจ้าของเป็นหน้าที่วิจัย ไม่ใช่การอ้างว่าได้มอบหมายบุคคลหรือเปิด agent แล้ว

## 5. สัญญาเชื่อม Core–fluid–thermal

ก่อน implementation ใหม่ ต้องกรอกสัญญา F0–F4 ตาม [มาตรฐานสมการ](../For%20Work/EQUATION_RESEARCH_AND_PHYSICAL_CORRESPONDENCE_STANDARD.md) แล้วผ่าน F5–F8 ตามลำดับ:

| ช่องสัญญา | สิ่งที่ต้องบันทึก | ข้อห้าม / falsification |
| --- | --- | --- |
| State | C, Phi, Pi และ momentum/current/phase ที่จำเป็น; algebraic constraints; canonical equation IDs | C ไม่เท่ากับ mass/charge โดยอัตโนมัติ; R_gen/R_obs เป็น output ไม่ใช่ dynamical reservoir |
| Material state | material/specimen, T, P, chemical potential, equilibrium path, phase, normal/superfluid fractions และ geometry | He-4 SVP equilibrium derivative ไม่เท่ากับ finite-frequency response จนแสดง correspondence |
| SI map | length/time/energy scales, field normalization, Jacobian และ uncertainty/covariance | Phi energy-dimension E^1 กับ E^0 ต้องมี explicit conversion; ห้ามใช้ normalized shape ตรึง amplitude |
| Transport | shear/bulk viscosity, heat conductivity, relaxation, mutual friction เฉพาะที่ model ต้องใช้; frame, Kubo operator, frequency/wavenumber limits | shear coefficient ไม่แทน conductivity; static susceptibility ไม่แทน dynamic Landau density; missing coefficient ทำให้ branch BLOCKED |
| Energy | kinetic/internal/response/storage terms, source work, boundary flux, dissipative conversion | normalized availability ไม่ใช่ SI total energy; viscous loss ต้องไม่สูญหายจาก total budget หรือถูกนับซ้ำ |
| Entropy | thermodynamic entropy, entropy flux, production, bath exchange; uncertainty | ต้องตรวจ total balance ที่ตรงกับ closed/open ensemble ไม่ใช่บังคับ subsystem entropy เพิ่มทุก timestep |
| Observation | velocity/pressure/temperature/flux operator, detector response, averaging และ units | TTG normalized trace ไม่ใช่ absolute thermometer; no circular parameter use |
| Stochastic response | noise covariance, discretization, FDT/KMS scope และ common-noise tangent/shadow protocol | ไม่สร้าง synthetic noise แล้วเรียก physical bath; unresolved physical noise ทำให้ stochastic physical claim BLOCKED |

สมการ continuity, momentum, energy และ entropy ของ standard physics ให้เป็น **reference obligations** ก่อน ไม่ประกาศเป็น UET-derived เพียงเพราะต่อ solver มาตรฐานกับ Phi ได้ ถ้าผลที่ดีที่สุดเป็น thermodynamically consistent hybrid ให้เรียก hybrid และแสดง source ของทุก term

## 6. ลำดับการทดลองและเกณฑ์ที่ล็อกก่อนรัน

ค่าด้านล่างเป็น **ข้อเสนอสำหรับ preregistration รุ่นแรก** ไม่ใช่ตัวเลขที่ตรวจผ่านแล้ว J00 ต้องตรวจ feasibility จาก analytic controls และล็อก configuration ก่อน production; ถ้าเปลี่ยนภายหลังให้ version ใหม่และระบุ exploratory ห้ามปรับ threshold เพื่อให้ผล candidate ผ่าน

### A. ความสามารถแทนการไหลและความถูกต้องเชิงตัวเลข

- เริ่ม periodic nonzero-vorticity field และตรวจ representation residual ก่อน evolve; scalar constant-mobility map ต้องถูกคัดออกจาก general rotational-flow claim หากแทนไม่ได้
- ตั้ง 2D periodic vortex/decay control, shear diffusion และ manufactured mass/momentum/energy source โดย derive exact forcing จาก analytic fields แยก implementation ที่ตรวจ
- Couette/Poiseuille ให้เป็น wall/forcing controls หลัง boundary contract พร้อม; lid-driven cavity ต้องมี source benchmark ที่ระบุ Re/geometry/precision; ไม่ใช้ scalar boundary gradient แทน moving-wall velocity โดยไม่พิสูจน์
- เสนอ periodic grids 32/64/128 และ time-step refinements dt, dt/2, dt/4 แยก spatial/temporal errors บนช่วงเวลาและ physical coefficients เดียวกัน ใช้ observed order/GCI เมื่ออยู่ใน asymptotic regime; ไม่บังคับสูตรนี้กับ discontinuities
- สำหรับ smooth second-order spatial candidate เสนอ observed order >=1.8 บนสอง finest refinements; method คนละ order ต้องใช้ declared order ของตัวเอง ไม่ให้ RK/Euler ได้เกณฑ์เดียวกันโดยพลการ
- เสนอ finest-grid relative L2 velocity error <=1e-2; incompressible normalized divergence <=1e-6; periodic closed mass drift <=1e-8; normalized integrated energy-budget residual <=1e-4 และต้องลดตาม refinement ทั้งหมดต้องนิยาม nonzero reference scale ก่อนรัน
- Pressure error ต้องจัดการ additive gauge; open-domain mass/energy ต้องหัก integrated source/boundary flux ก่อนคำนวณ drift ไม่มี NaN, hidden coefficient cap, clip หรือ fallback ที่นับผ่าน
- Numerical budgets เหล่านี้ใช้กับ manufactured/analytic tests เท่านั้น ไม่แทน experimental uncertainty หรือ theorem bound

แนวทาง three-grid convergence และข้อจำกัด Richardson/GCI อ้างอิง [NASA NPARC spatial-convergence tutorial](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html) อ่าน 2026-09-26 ตัวเลข acceptance ข้างต้นเป็นข้อเสนอของแผนนี้ ไม่ได้อ้างว่า NASA กำหนดไว้

### B. He-4 pilot ที่ทำได้โดยไม่ลัดขั้น

1. เลือก normal-component shear relaxation เป็น candidate แรกเพราะมี source-locked shear viscosity อยู่แล้ว แต่ต้องระบุ inertia/density ของ subsystem และการ coupling กับ superfluid ให้ชัดก่อน derive decay rate
2. ทดสอบ standard shear reference ก่อน UET coupling; ทดสอบ zero coupling, zero drive, equilibrium, inviscid/zero-dissipation limits ที่สมการอนุญาต และ response ต่อ forcing เล็ก
3. Freeze theta_T, Z, e0 และ source coefficients จาก calibration set; ห้าม rematch ต่อ state/frequency ของ test เพื่อรักษาความตรงกัน
4. ใช้ response derivative หรือ time/frequency response ที่ไม่ได้ใช้สร้าง calibration; ระบุ thermodynamic constraints ให้ตรงแหล่งวัด ถ้า source ไม่มีให้ผลเป็น source-blocked ไม่ใช้ matching identity เป็นข้อมูลใหม่
5. เพิ่ม thermal pulse/finite-wavevector หรือ counterflow หลังมี required conductivity/relaxation/mutual-friction/EOS และ protocol source ครบเท่านั้น ไม่อนุมานว่าหนึ่ง shear channel ทำให้ two-fluid hydrodynamics สมบูรณ์
6. Propagate source, scale, numerical และ measurement uncertainty รวม covariance; หาก covariance ไม่ทราบใช้ sensitivity bounds ที่ติดป้าย ไม่เรียก confidence interval

### C. Chaos และ turbulence

นำ method ที่ผ่านแล้วกับ normalized Topic 13 pilot มา reuse ให้ชัดว่าอะไรยังเดิม อะไรเปลี่ยน ก่อนคำนวณ exponent ของ candidate ใหม่ต้องผ่าน state, ledger และ numerical gates; positive exponent จาก clipping/unstable timestep ถูกคัดออก

เสนอ perturbations 1e-8, 1e-7, 1e-6 ใน normalized state metric; state ที่มีหลายหน่วยต้องกำหนด scale/inner product ก่อน QR ตรวจ timestep/grid, transient window, block length, seed และ tangent/shadow agreement ใช้ resolution budget เดิม `max(delta_dt, delta_dx, 2*SE_block, delta_method)` รายงาน sign ว่า resolved หรือ unresolved ไม่ปัด unresolved เป็น chaos

สำหรับ turbulence ให้เพิ่ม kinetic energy, enstrophy ในมิติที่เหมาะสม, dissipation, energy spectrum และ stationarity diagnostics; 2D ผลไม่ครอบคลุม 3D stretching ใช้ 3D เฉพาะหลัง 2D control และ state admission ผ่าน ระยะยาวควรเปรียบเทียบสถิติ/uncertainty ไม่บังคับ trajectory ให้ตรงหลัง predictability horizon

[JHTDB](https://turbulence.idies.jhu.edu/home) เป็น **candidate source catalog ที่ตรวจพบ** ไม่ใช่ dataset ที่รับเข้าแล้ว J09 ต้องเลือก dataset/version, Re, forcing, domain, viscosity, query coordinates/times, interpolation method, license/citation และ query log ก่อนนำมาเป็น external numerical reference ข้อมูล DNS ของผู้อื่นไม่ใช่การวัดทดลองและไม่ใช่ external replication ของ UET

### D. Runtime และการทดสอบกลไกเพิ่มจาก baseline

ตรึง observable error budget, physical end time, boundary/initial state, dtype, hardware, threads และ output cadence ให้ตรงกัน ทำ warm-up แล้วเสนออย่างน้อย 10 paired timing trials สลับลำดับเพื่อบรรเทา drift รายงาน median, dispersion/interval, peak memory และ unsuccessful runs เปรียบเทียบหลาย grid และ time-to-accuracy รวม setup ที่จำเป็นสำหรับวิธีนั้น ไม่มีการตัดงาน pressure/observation ออกจากฝั่งเดียว

เกณฑ์ >2 ของ legacy artifact คงเดิม สำหรับ matched benchmark ใหม่ speed improvement เป็นผลตาม error budget ไม่ใช่เกณฑ์รับรองฟิสิกส์ ทดสอบ baseline, UET candidate และ coupling-off ด้วย parameter freedom ที่เปิดเผย ถ้า UET ไม่เพิ่ม out-of-sample skill ให้รายงานว่า standard baseline เพียงพอในขอบเขตนั้น

## 7. Graphite ทำขนานอย่างไรโดยไม่ลากทุกงานให้รอ

แยก J03 เป็นสาม input records ตาม [minimal-input contract](../../core/07_artifacts/topic13/t13_full_closure_minimal_input_contract.json):

1. **Phi–SI/alpha/beta:** dimensionful action anchor หรือ paired calibration อิสระ พร้อม field scale/Jacobian และ covariance; normalized TTG ใช้ตรึง amplitude ไม่ได้
2. **Ding-compatible C_src:** authorized numeric source หรือ independently reproduced same-regime package; specimen/state, modal weighting, thermodynamic correction และ uncertainty ต้องเข้ากัน comparator คนละวัสดุ/สภาวะไม่ผ่านโดยอัตโนมัติ
3. **Physical transport:** Kubo/current operator, state, units, FDT/KMS/entropy และ uncertainty ต้องเชื่อมกัน ไม่ใช้ synthetic positive matrix แทน physical coefficient

Axial Raman ต้องได้ independent matched-state strain/Raman row พร้อม uncertainty; DFT comparison ไม่เพิ่ม empirical rank แผนนี้ไม่เปิดดู Xie 2026 และไม่ค้นผล held-out เพื่อเลือกแบบจำลอง ต้องตรวจ exposure declaration และกำหนด fresh holdout หรือ label retrospective หากมี prior exposure ห้ามอ้าง pristine blind validation จาก no-access flag เก่า

หากไม่มี source ใหม่ ให้หยุดสแกนกลุ่มเดิมและบันทึก exact missing fields/eligible acquisition route การติดต่อผู้เขียนขอข้อมูลเป็นงานแยกที่ต้องได้รับคำสั่งส่งข้อความก่อน ขณะรอให้ J01/J04 และ protocol design เดินได้โดยไม่ใช้ graphite calibration ปลอม

## 8. การปิดประเด็น การเผยแพร่ และวงรอบงาน

แยกผลปิดเป็น: source-ready, representation admitted/no-go, numerical-control accepted, bounded constitutive interface, independent physical validation และ external replication ห้ามบวกจำนวนทุกประเภทเป็นเปอร์เซ็นต์ theory completion

ในแต่ละ wave ให้มีหนึ่ง controlling blocker, artifact ที่คำนวณจาก input จริง, verdict กับ reason, hash ของ source/code/config, metric/threshold, claim boundary, UPDATE_LOG และ scoped commit ก่อนเริ่ม wave ถัดไป Rerun เฉพาะ evidence-producing state เปลี่ยน; missing record ต้องให้ BLOCKED ไม่ใช่ PASS จาก `all([])` หรือ manual checkbox

เส้นทางปิดเชิงวิจัยมีสามแบบที่บันทึกได้: (1) ผ่านเฉพาะ domain ที่ล็อก (2) no-go พร้อมสมมติฐานและ counterexample (3) deferred/source-blocked พร้อมสิ่งที่จะเปิดงานใหม่ ไม่เรียกแบบที่สามว่า scientific closure

**ลำดับเริ่มทำจริง:** J00 แล้ว J01 เป็น pilot แรก; พร้อมกันเตรียม J02 และ source admission ของ J03; J04 ตามหลังการตัดสิน representation; J05/J06 ต้องมี Core admission; J07/J08 ตามหลัง numerical/physical prerequisites; J09 ทบทวนผลแยก lane ไม่มีเส้นตายที่รับประกันแก้ปัญหาทางฟิสิกส์ได้

**หน่วยงานแรกที่พร้อมลงมือ:** source-hashed representability audit ของ Engine_UET_2D/3D และ baseline contract โดยยังไม่เปลี่ยนสมการ Core ผลส่งมอบคือ admissibility/no-go report, mobility/cap/clip counterexamples, exact next candidate contract และ update log ผลนี้จะบอกว่าควรปรับ implementation หรือออกแบบ state ใหม่ ไม่ใช่เริ่มเพิ่ม benchmark จำนวนมากบน mapping ที่ยังไม่ผ่าน

## 9. การเชื่อมงานก่อนหน้าและขอบเขต rollout

- Core matter-space/Noether/O(2): reuse registry, tangent/JVP, EOS, energy and entropy interfaces พร้อม version/hash; ใหม่ทุก term ต้องมี origin และ mapping
- Topic 13: reuse normalized regime pilot, causal named-branch/no-go และ reciprocal material/entropy lessons ตาม material scope; อย่าย้าย graphite thermoelastic coupling ไป He-4 โดยไม่มี derivation
- Topic 0.11: เป็น optional diagnostic-method consumer หลัง source/estimator gate ของตนผ่าน ไม่รับ phase-transition exponent มาเป็น fluid transport input
- Topic 0.4: ใช้ได้เฉพาะ source/phase context ที่ถูกตรวจ admission; ชื่อ superfluid ไม่ทำให้ static natural-unit response กลายเป็น full physical two-fluid dynamics
- Topic 0.23: sync dependency แบบแยก lane เมื่อผลร่วมยอมรับแล้ว; ไม่เปิด universal scale claim มาปิด fluid blocker
- Curved 3+1/Topic 0.19: ใช้ prescribed stress interface เป็น diagnostic ได้ตาม gate แต่ conservation ของ dynamically coupled source และ boundary admission ต้องผ่านก่อน self-consistent gravitational claim
- Navier–Stokes theorem: แยกเป็น optional future proof program พร้อม exact PDE/domain/forcing/regularity/solution class และ proof obligations ของตน ไม่อยู่ใน acceptance ของแผน benchmark นี้; formal checker ของ lemma ไม่แทนหลักฐาน physical correspondence

ครอบคลุมในแผนนี้หมายถึงมีทางตัดสินทุกชั้นของคำอ้าง ไม่ใช่เปิดทุก topic หรือทุก physical regime พร้อมกัน ผลของการออกแบบครั้งนี้คือ dependency และ acceptance ที่ชัดขึ้น ยังไม่มี fluid/thermal scientific blocker ใดถูกประกาศว่าปิดใหม่

## Source review: OpenAI Navier–Stokes and Euler relevance to Topic 10

The [paper applicability assessment](OPENAI_NAVIER_STOKES_APPLICABILITY_2026-09-26.md)
prioritizes theorem scope, norm separation, rotational-flow representability and
vorticity-aware observables inside J00/J01. A finite-window NS or Euler stress
case is conditional on later source and model admission. These papers add no
scientific dependency, alter no numerical threshold and close no work package.

## Vector-state checkpoint — 2026-09-30

J01's legacy no-go remains scoped and unchanged. Its follow-up now provides a
[vector/material-rate candidate](VECTOR_STATE_RESEARCH_CONTRACT.md) and a separate
instantaneous normalized audit (150 checks). Independent u supports vortical
states; conditional scalar/fluid work exchange, stress gauge and frame identities
pass the selected controls. The initial control's cancelling-work FAIL is retained;
the amended harmonic controls detect missing/reversed force and Pi/Q confusion
without tolerance relaxation.

This does not admit physical J04/J05, run a trajectory or close UET/Core.
The controller has narrowed to
vector_momentum_constitutive_origin_and_material_frame_admission_open.
Starting at rest is not the same as freezing u and its acceleration to zero;
the parent Eulerian Pi evolution needs the latter for this limit.

Topic 13 consumes only a proposed reciprocal-work/frame interface. He-II second
sound still requires an admitted two-fluid entropy/temperature/relative-flow state,
state-matched transport and a primary measurement protocol. The current
[Topic 13 protocol](../0.13_Thermodynamic_Bridge/HE4_SECOND_SOUND_PROTOCOL_CARD.md)
also records calibration/response source ancestry overlap: the recommended rows
are neither blind nor established as independent. J02/J03 source work can continue
in parallel, with no He-4-to-graphite parameter transfer.
## Conditional conservative-origin follow-up (2026-09-30)

The [variational derivation](VECTOR_VARIATIONAL_ORIGIN.md) and its
[72-check audit](Result/artifacts/fluid_vector_variational_origin_audit.json)
show that the reversible subset of the vector/material-rate reference follows
from one declared volume-preserving action with an independent internal scalar.
This narrows the conditional reference-origin question only. The action choice
and material attachment are not a microscopic UET derivation; the overall
vector_momentum_constitutive_origin_and_material_frame_admission_open controller
remains. Next assess the physical configuration/material assignment, coefficient
origins and SI observable map. Physical J04/J05, two-fluid J02/J06, graphite and
all blocked upstream gates remain blocked.

Canonical m=rho0 u+h Q grad Phi is a rate derivative, not a new mass or an automatic
measurement of total mechanical momentum. Local Q transport needs a separate
test because its work integrates to zero. The full dissipative/thermal closure
and Topic 13's calibration/response ancestry overlap are unaffected. Reference
mathematics can continue under explicit labels without unlocking physical lanes.

## Coupled mode-eligibility checkpoint (2026-09-30)

The [139-check mode audit](SECOND_SOUND_MODE_ELIGIBILITY.md) narrows the J05
candidate question: the current stable homogeneous single-velocity model has
diffusive/gapped sectors but no hydrodynamic second-sound acoustic pair.
This diagnostic is a J01/J05 candidate screening follow-up, not physical J05
execution. Its coupled controller is
isothermal_single_velocity_candidate_counterflow_acoustic_mode_missing.

J02/J05/J06 must use a separately registered and materially justified
entropy/temperature, normal-superfluid relative-motion and superfluid
phase/chemical-potential operator. Do not fit the existing oscillator to the
exposed recommended speed rows; calibration/response ancestry remains unresolved.
The current candidate remains a bounded isothermal/scalar-fluid reference.

A separate synthetic standard two-fluid operator validates acoustic/work
sensitivity. The initial complex-metric preview is retained as invalid; the
repaired controls pass with original tolerances and an explicit post-preview
harness amendment. No physical/Core/Topic 13 dependency unlock occurs.
The overall momentum/material-frame/SI admission controller remains unchanged.

## Standard two-fluid/EOS checkpoint (2026-09-30)

The [standard state/EOS comparator](TWO_FLUID_STATE_EOS_REFERENCE.md) extends the
earlier counterflow control to full longitudinal density/entropy mixing and
both sound branches. Its 59-check reference verifies reciprocal work and
identifies the limited conditions for zero-mass-current reduction. It is a
J02/J05 preparation follow-up, not physical package execution.

The new coupled input controller is
two_fluid_fixed_pressure_EOS_and_UET_state_mapping_missing.
J02/J05 need independent material rho/rho_s/entropy, fixed-pressure EOS derivatives
and a physical Core state/Legendre/phase correspondence. SVP path slopes alone
leave isothermal compressibility undetermined; two positive local EOS witnesses
make that ambiguity explicit. Source overlap, primary response protocol,
uncertainty and the separate dissipative tensor remain controlling downstream.
No parent gate, legacy single-velocity exclusion, matching constant or physical
J04/J05/J06 status is promoted.

## He-II source-acquisition checkpoint (2026-09-30)

The [fixed-constraint source card](HE4_FIXED_CONSTRAINT_EOS_SOURCE_CARD.md)
packages three TN1334 fitted-EOS liquid rows with explicit derivative constraints.
The source audit passes 56 transcription/unit/printing checks and detects five
incorrect interpretations. This is J02 source preparation, not physical J05/J06.

Fixed-pressure/volume/temperature derivatives are found, but per-row uncertainty,
covariance, the selected entropy reference and exact EOS/response experimental
ancestry remain unresolved. Source-computed sound speeds cannot validate UET
independently. Modern IR8474 is outside the He-II domain. No source rs fit or
two-fluid numerical speed is imported or predicted in this wave.

The narrower acquisition controller is
he4_fixed_constraint_EOS_source_found_but_covariance_entropy_anchor_and_independence_open.
Resolve that source package or select a better source, then freeze a primary
state/frequency/geometry/uncertainty response and independent experiment split.
The physical Legendre/state/SI and superfluid-phase response correspondence,
dissipative closure and earlier single-velocity exclusion remain controlling.
All physical package states and Core/Topic 13 dependency gates are unchanged.

## Entropy-source/reference transfer checkpoint (2026-09-30)

J02 preparation now includes [six source entropy tokens and a coordinate contract](HE4_ENTROPY_SOURCE_AND_REFERENCE_CONTRACT.md),
with a [116-check audit](Result/artifacts/he4_entropy_source_reference_audit.json).
Table 8.5 states its own zero-T integration convention; Table 8.3 has a distinct
fountain-pressure lineage. These narrow source identification, not physical
J05/J06 or an independent response split. Original TN1334 and Topic 13 packages
stay unchanged.

The current acquisition controller is
he4_entropy_integration_anchor_found_but_TN1334_reference_transfer_covariance_and_independence_open.
Next resolve selected-edition reference conversion or replace that candidate,
source derivative covariance and exact experimental ancestry, and lock a primary
matched response protocol. The ideal two-fluid coordinate check demonstrates why
both entropy current and chemical-potential force must accompany a reference
change; positive work alone is insufficient. No material entropy offset or sound
prediction is fitted. Physical Core state/SI/phase/transport admission, the earlier
single-velocity mode exclusion and blocked J04/J05/J06 remain unchanged.

## Current Core common-flow composition checkpoint (2026-09-30)

J01/J02 preparation now includes a [Core source-function composition contract](CORE_O2_COMMON_FLOW_COMPOSITION_CONTRACT.md)
and [69-check execution artifact](Result/artifacts/fluid_core_o2_common_flow_composition_audit.json).
The ideal common-flow scalar target FAIL_REQUIRED_COMMON_FLOW_IDENTITY at all
three declared condensed points rejects the shortcut of combining formal Doppler
normal response with tree phase stiffness as one physical two-fluid inertia.
Normal/tree controls and separate component refinements pass. This is not
physical J04/J05/J06 execution or a complete failure of the existing O(2) lane.

The narrower candidate controller is
finite_temperature_phase_stiffness_and_normal_momentum_common_action_match_missing.
Next derive flow-dependent finite-T phase stiffness/current/stress/normal response
from one common effective action with Ward/entrainment consistency. Do not fit a
coefficient from this identity. Source entropy-reference transfer/covariance and
independent response protocol remain separate required work; their current
snapshots are retained. Overall material/frame/SI admission and physical package
states are unchanged; the normal-only heat balance cannot cover condensed He-II.

## Fixed-Phi flow-Hessian candidate handoff (2026-09-30)

The [new independent phase-flow reference](CORE_O2_FLOW_HESSIAN_DERIVATION.md)
derives thermal stiffness from a tree-reduced Gaussian action rather than
forcing the common-flow identity. Implicit and finite-flow curvatures agree,
and the separate scalar target passes at all three prior condensed controls.
The previous tree-only shortcut FAIL remains as historical/current comparison.

The machine plan now records a separate flow-Hessian snapshot/history item.
Next derive complete current/stress/entrainment and longitudinal two-fluid
modes at the same ensemble. Material/SI, independent EOS/entropy/protocol,
Core admission and physical J04/J05/J06 remain separate prerequisites.
This narrows J01/J02 preparation only; no work-package status or dependency
is promoted. Original null material inputs and Topic 13 constants are unchanged.

## Local ideal operator preparation (2026-09-30)

The [current/stress/ideal-mode reference](CORE_O2_LOCAL_IDEAL_TWO_FLUID_DERIVATION.md)
extends the independently derived phase curvature with current source/metric
variation, EOS derivatives and local entrainment. Its conditional ideal operator
has two acoustic pairs at all three controls and positive reciprocal work.
Both reference coefficients and operators are evaluated without sound-speed fitting.

The new snapshot/history records the additional local-equilibrium entropy
assumption. Nonlinear/interacting/live-response completion, collision/thermalization
and a physical hydrodynamic window are explicit remaining blockers, followed by
material/SI and independent source/protocol admission. J01/J02 preparation narrows;
J04/J05/J06 remain NOT_STARTED and no package dependency is unlocked.
The source acquisition and overall material/frame controller remain unchanged.

## Connected collision handoff (2026-10-01)

[The Goldstone channel](CORE_O2_GOLDSTONE_COLLISION_DERIVATION.md) adds
action-derived microscopic preparation to the ideal two-current reference.
It audits T=0 single-mode decay, Bose triad invariants and derivative soft
behavior; the joint JSON retains previous snapshots and adds the current
159-control package plus the first failed diagnostic.

Existing Topic13 scalar/gain-loss/contact/Kubo evidence remains scoped. Next
requires connected condensed collision/current matching, including vector
heat-current projection, interacting thermal state and resolution/allowed-channel
control. A single-mode width or positive disconnected graph cannot establish
omega*tau <<1. Material/independent EOS/entropy/response sources and nonlinear/
live-response work remain separate; J04/J05/J06 stay NOT_STARTED.

## Shared-basis kinetic current handoff (2026-10-01)

[The Galerkin package](CORE_O2_GOLDSTONE_GALERKIN_DERIVATION.md) replaces
disconnected representative-triad diagnostics with shared scalar/vector event
integrals for the selected leading Goldstone cubic process. Raw invariants,
four finite-basis nulls, source momentum constraint and independent finite
resolvents pass; the joint JSON preserves every earlier snapshot.

The1% cutoff and basis response gates FAIL. Current-source representation and
quadrature PASS cannot promote this package. The controlling measured blocker
is finite_basis_and_cutoff_current_response_not_converged.
Next: stable higher-order vector functions, low-energy-valid cutoff/soft-current
convergence, then full kinetic-to-condensate/charge heat-current/frame and
interacting thermal collision completion. Material/SI/He-II ancestry and
nonlinear/live-response obligations remain. Physical J04/J05/J06 stay NOT_STARTED.

## Stable-vector and low-momentum handoff (2026-10-01)

[The vector refinement](CORE_O2_GOLDSTONE_VECTOR_REFINEMENT.md) resolves
Gram-conditioning ambiguity under the same selected cubic process.541 structural
controls pass, including shared off-grid recurrence, raw momentum, same-span
old response and whole-action scaling. SOFT within-family refinement passes.

Overall1% convergence still FAILS: EVEN basis/cutoff and cross-family response.
Controller:
stable_vector_basis_cross_family_or_cutoff_current_response_not_converged.
Next: an independently soft-enriched family and infrared/continuum-current
bounds while retaining the old failed targets, then physical heat-current/frame/
interacting-state and material/SI/source admission. Earlier snapshots remain
immutable and physical J04/J05/J06 stay NOT_STARTED; no dependency unlock.

## Enriched finite targets and continuum-domain handoff (2026-10-01)

[The infrared trial package](CORE_O2_GOLDSTONE_INFRARED_TRIALS.md) tests
independent soft enrichment of the old EVEN space and smooth-origin trials.
664 structural controls and declared1% finite enriched/smooth targets pass.
HYBRID/SOFT differences0.04684%/0.04251%; no prior FAIL is relabeled.

First near-collinear rounding failure and source are retained; the separately
registered numerical geometry repair changes no collision weights or thresholds.
Controlling measured blocker:
infrared_collision_form_domain_continuum_current_and_physical_heat_current_admission_open.
Next: collision-form domain and continuum source-weighted upper/error bounds,
then microscopic condensate/charge heat-current/frame and interacting thermal
completion. Gram-norm approximation or discrete variational ordering alone
cannot unlock physical J04/J05/J06, material/SI or independent-source admission.

## OpenAI direct-bridge and current-blocker review (2026-10-01)

The [additional review](OPENAI_FORMAL_TRANSFER_REVIEW_2026-10-01.md) and
[source/design record](Data/03_Research/openai_topic10_formal_transfer_review_2026_10_01.json)
add a scoped static comparison of pinned reference/submission definitions and
direct theorem bridges. No formal checker was run. OA0 is completed source
inspection; OA1-OA6 are proposed design tasks within J00-J09, not new gates or
package promotions. Current finite enriched/smooth trial targets do not close
continuum collision-domain/source-weighted upper bounds, physical heat current
or two-fluid/material/SI correspondence. Analytic versus smooth forcing and
regularity assumptions must remain explicit in any future adversarial source.
Physical J04/J05/J06 remain NOT_STARTED and the machine-readable plan/DAG is unchanged.

## Selected finite-cutoff form-domain and no-uniform-gap checkpoint (2026-10-01)

J01/J02 preparation now has a [conditional internal continuum-form derivation](CORE_O2_GOLDSTONE_CONTINUUM_FORM.md)
and [292-check source/unit/bound diagnostic](Result/artifacts/fluid_core_o2_continuum_form_audit.json).
Bounded soft trials are admitted to the selected finite-K form and smooth
approximation is controlled in both G/Q norms. The radial vector null is
momentum only; compact projected soft bumps show no uniform positive vector
gap. This is a scoped internal derivation with independent/formal review open.

The machine-readable plan retains prior snapshots/history and physical states,
and now exposes the selected next controller:
source_weighted_continuum_current_upper_bound_and_microscopic_heat_current_correspondence_open.
Derive a source-specific upper/error bound without an assumed uniform gap,
then microscopic heat-current/frame/interacting-state, nonlinear/live and
material/SI/independent-source admission. No-uniform-gap is not a divergent-current
result or blanket denial of source-specific hydrodynamics. J04/J05/J06 remain
NOT_STARTED; Topic13/Core admission and all old failed/enriched finite targets
are unchanged. OpenAI source reviews remain dated historical design snapshots.
