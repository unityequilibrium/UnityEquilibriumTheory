---
layout: home
title: "Unity Equilibrium Theory (UET) Research Hub"
description: "Repository-backed research hub for UET methods, topic modules, and documentation standards."
author: "Unity Equilibrium Team"
---

# Unity Equilibrium Theory Research Hub

<!-- UET-RESEARCH-RETROSPECTIVE: 2026-10-19; navigation notice, not a physics gate -->
> **ทบทวนก่อนวิจัยต่อ — 19 ต.ค. 2026:** ผลรันและความครบของเอกสารไม่เท่ากับการยืนยันทางฟิสิกส์ ตรวจข้อจำกัดและตัวควบคุมก่อนนำผลเก่าไปอ้างใหม่ อ่าน [รายงานข้อผิดพลาดและบทเรียน UET](meta/UET_RESEARCH_RETROSPECTIVE.md) โดยเฉพาะข้อ R01–R18 และลำดับแก้ใน §8 ก่อนขยายงาน สถานะจริงยังอ้างอิง artifact/gate ของเส้นทางนั้น

This documentation hub is the normative entry point for the repository's technical and
research-facing material. It is organized to distinguish repository infrastructure from
scientific claims, and to distinguish current standards from archived historical material.

## Canonical sources

- Release metadata: [docs/meta/release_manifest.json](./meta/release_manifest.json)
- Citation metadata: [docs/CITATION.cff](./CITATION.cff)
- Bibliography: [docs/references.bib](./references.bib)
- Claim inventory: [docs/meta/claim_inventory.md](./meta/claim_inventory.md)
- Topic readiness map: [docs/meta/topic_readiness.json](./meta/topic_readiness.json)

<a id="latest-research-updates"></a>
## Latest research updates

**ตรวจถึง 23 ตุลาคม 2026** — แหล่งวิจัยคือ [UET Theory Argument](./meta/UET_THEORY_ARGUMENT.md) ใน local source commit `1346edfc07c2d2f9eb2adbd5257e820fa186a37b` บน `codex/research/source-backaction-discrimination` ไม่ใช่การออก release หรือการรับรองว่า public `main` อัปเดตตรงกันแล้ว

| ทางเข้า | สิ่งที่อ่านได้ / ขอบเขต |
| --- | --- |
| [§23.3 steady-response certificate](./meta/UET_THEORY_ARGUMENT.md#233-uniform-certificate-ไม่ใช้กริดที่บังเอิญผ่านแทนทั้งช่วง) | first-mode เทียบ full normalized rod–polarization reference; F_b-only steady harmonic input, f_P=0, omega/omega_0 ใน [0.99,1.01]; error ของ complex p/F_b และ x/F_b <0.9%<1% ไม่ใช่ความแม่นยำกับธรรมชาติ |
| [§24.6 prepared-history limitation](./meta/UET_THEORY_ARGUMENT.md#246-คำตัดสิน-ขอบเขต-และจุดหยุด) | smooth write + controlled wait + released read: projected state เดียวกันอาจละ higher modes ที่ยังเปลี่ยน output ได้ จึงไม่พอสำหรับ protocol นี้ ไม่ปฏิเสธทุก reduction หรือผล steady ของ §23 |
| [§25.2–5 equation/term relationships](./meta/UET_THEORY_ARGUMENT.md#252-คำตอบเรื่อง-สมการหลัก-ต้องแยกสามระดับ) | generator ต่างจาก kinetics; C/I ไม่ใช่การ rename เป็น C/Phi/Pi; แยก exact rewrite, coordinate map, conditional reduction และ model alternatives ไม่รับรองทุกสูตรใน registry |
| [§25.7 next research question](./meta/UET_THEORY_ARGUMENT.md#257-คำวินิจฉัยและโจทย์ถัดไปที่ไม่วนเพิ่มสมการ) | ผลคงอยู่จำขนาดหรือทิศ/เครื่องหมาย และเปลี่ยน response ผ่าน state/input ใด ก่อนเลือก realization ไม่เปิด scan/fit เพื่อหนี comparator |
| [Core current realization](./core/README.md#current-response-realization) | Omega + complete C/Phi/Pi state + evolution/input/boundary/readout; opt-in normalized prototype ไม่ใช่ universal master; default ยัง legacy_local |
| [Calculation contract ของ cycle](./topics/0.13_Thermodynamic_Bridge/calculation_contracts/energy_memory_cycle.json) | T13_ENERGY_MEMORY_CYCLE_FORMAL_V1, review INCOMPLETE / physical correspondence UNKNOWN; ใช้เฉพาะ declared path ไม่ครอบทุก family |
| [Foundation controller](./core/07_artifacts/gates/uet_foundation_compatibility_decision.json) / [Topic 13 full bridge controller](./topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json) | FOUNDATION_NOT_CLOSED; legacy graphite/TTG aggregate BLOCKED_OPEN_T13_FULL_BRIDGE แยกจาก O(2)/He-4 Core-ready; ไม่มี external/global promotion |
| [Topic 13 UPDATE_LOG](./topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md) / [daily WORK_LEDGER](../WORK_LEDGER/2026/2026-10-23.md) | ประวัติงานที่ทำจริงและขอบเขต commit/publication; logs ไม่แทนผลใน artifact |

สำหรับผู้อ่านทั่วไป ดู [สรุปข้อเสนอรวมและบทบาทเทอมในหน้าแรก](../README.md#research-updates-2026-10-23) ซึ่งยังรักษาสมมติฐานระดับจักรวาลของผู้เขียนไว้โดยไม่ใช้ subsystem result ตัดสินแทน ทั้งผลบวก/ข้อจำกัดข้างต้นเป็น FORMAL/normalized ยังขาด physical mapping, หน่วย, parameter origins, preparation และ measurement uncertainty รวมถึงสิ่งที่เพิ่มเหนือ standard comparator

**ข้อจำกัดการเข้าถึงหลักฐาน:** working copy, local commit และ public main เป็นคนละชั้น รายงาน §§23–25 อยู่ใน source commit นี้ แต่ [retrospective](./meta/UET_RESEARCH_RETROSPECTIVE.md) และ source/verifier สามไฟล์ที่รายงานระบุยังไม่อยู่ใน tree ของ commit นี้ จึงเป็น publication gap แม้ไฟล์มีในเครื่อง ไม่ใช่ชุดทำซ้ำครบทุกงาน และไม่ใช่ข้อยืนยันว่าทุก branch/remote ขาดไฟล์เหล่านี้ ไม่มีการเผยแพร่หรือยกระดับ physics gate จากการอัปเดต hub

## Documentation architecture

### Technical

- [01 Introduction](./UET_Documentation_Details/01_Introduction/)
- [02 Installation](./UET_Documentation_Details/02_Installation/)
- [04 User Guides](./UET_Documentation_Details/04_User_Guides/)
- [05 API Reference](./UET_Documentation_Details/05_API_Reference/)
- [scripts](./scripts/)
- [core](./core/)

### Academic

- [03 Core Theory](./UET_Documentation_Details/03_Core_Theory/)
- [06 Evidence and Research](./UET_Documentation_Details/06_Evidence_and_Research/)
- [references.bib](./references.bib)
- [topics](./topics/)

### Public

- This landing page
- Topic README files under `docs/topics/*`
- Release summary in the repository root [README.md](../README.md)

### Archive

- [LEGACY_REPORTS](./UET_Documentation_Details/LEGACY_REPORTS/)

Legacy material is preserved for context and traceability, but it is not the normative
source for release metadata, claim wording, or current standards.

## Standards used in this release

- [Standards overview](./UET_Documentation_Details/STANDARDS/README.md)
- [Documentation style guide](./UET_Documentation_Details/STANDARDS/documentation_style_guide.md)
- [Topic README standard](./UET_Documentation_Details/STANDARDS/topic_readme_standard.md)
- [Verification contract](./UET_Documentation_Details/STANDARDS/verification_contract.md)
- [Release checklist](./UET_Documentation_Details/STANDARDS/release_checklist.md)

## Repository counts used by this release

> **Historical snapshot:** เก็บจำนวนเดิมตาม release summary โดยไม่ทราบ run identity/วันตัดยอดที่พอรับรองความสดในรอบนี้ ตัวเลขไม่ใช่จำนวนผลที่ผ่านการยืนยัน และไม่ได้แทนด้วยจำนวนคาดเดาใหม่

- `41` topic directories were reported under `docs/topics/` in the original snapshot
- `39` of those are numbered research-topic directories
- `2` are supporting workspaces
- `14` automated test files are tracked as `test_*.py`
- `8` topic-level verification scripts are tracked as `Verify_*.py`
- `23` bibliography entries were reported in `references.bib` in the original snapshot

## Normalized flagship topics

- [0.1 Galaxy Rotation Problem](./topics/0.1_Galaxy_Rotation_Problem/)
- [0.3 Cosmology and Hubble Tension](./topics/0.3_Cosmology_Hubble_Tension/)
- [0.10 Fluid Dynamics and Chaos](./topics/0.10_Fluid_Dynamics_Chaos/)
- [0.21 Yang-Mills Mass Gap](./topics/0.21_Yang_Mills_Mass_Gap/)

These topics now act as reference examples for how repository claims should be qualified:
problem statement, assumptions, data source, method, fitting status, baselines,
limitations, and readiness are expected to be explicit.

## Notes on interpretation

- Repository documentation can describe internal numerical behavior without claiming
  external validation.
- A topic marked `Structured` or `Reproduced internally` is not automatically
  `Externally replicated` or `Peer-reviewed`.
- When a topic uses fitted parameters, the documentation must say so explicitly.

---

*Unity Equilibrium Theory Team | repository-first standards pass*

---

<a id="wording-history-2026-10-23"></a>
## ภาคผนวก: ถ้อยคำที่ปรับในรอบนี้

ตรวจ 23 ตุลาคม 2026 — ตารางนี้เก็บข้อความที่ถูกแทนเพื่อการทบทวน ไม่ใช่การนำคำอ้างเก่ากลับมารับรอง ข้อความ/ตัวเลข/สูตรส่วนอื่นคงไว้พร้อมคำกำกับขอบเขต ตารางแสดงเฉพาะ cell ที่เปลี่ยนเมื่อเนื้อหาแถวอื่นไม่เปลี่ยน; ไม่อาศัย Git history เพียงอย่างเดียว

| ตำแหน่ง | ข้อความเดิม | ข้อความใหม่ | เหตุผล | หลักฐาน/ขอบเขต |
| --- | --- | --- | --- | --- |
| Repository counts / topic directories | <code>- &#96;41&#96; topic directories are currently present under &#96;docs/topics/&#96;</code> | <code>- &#96;41&#96; topic directories were reported under &#96;docs/topics/&#96; in the original snapshot</code> | เก็บ 41 เดิมในฐานะ original snapshot; รอบนี้ไม่รับรองความสด/วันตัดยอด | [release metadata](./meta/release_manifest.json) / [claim rubric](./topics/For%20Work/04_Claim_and_Evidence_Rubric.md) |
| Repository counts / bibliography | <code>- &#96;23&#96; bibliography entries are currently curated in &#96;references.bib&#96;</code> | <code>- &#96;23&#96; bibliography entries were reported in &#96;references.bib&#96; in the original snapshot</code> | เก็บ 23 และจำนวนอื่นครบ โดยไม่อ้างว่าเป็นการนับใหม่ | [release metadata](./meta/release_manifest.json) / [claim rubric](./topics/For%20Work/04_Claim_and_Evidence_Rubric.md) |
