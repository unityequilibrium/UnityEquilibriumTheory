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

- `41` topic directories are currently present under `docs/topics/`
- `39` of those are numbered research-topic directories
- `2` are supporting workspaces
- `14` automated test files are tracked as `test_*.py`
- `8` topic-level verification scripts are tracked as `Verify_*.py`
- `23` bibliography entries are currently curated in `references.bib`

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
