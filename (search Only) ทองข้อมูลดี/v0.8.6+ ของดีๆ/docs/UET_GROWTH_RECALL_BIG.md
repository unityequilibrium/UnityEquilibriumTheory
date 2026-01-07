# UET — GROWTH CYCLE RECALL FILE (Big Matrix)
**File name (suggested):** `UET_GROWTH_RECALL_BIG.md`
**Purpose:** คู่มือรีคอลสำหรับพัฒนาแพลตฟอร์มให้โตแบบเป็นระบบ (Doc→Plan→Implement→Verify→Test→Release)
**Rule:** ไฟล์นี้เป็นคู่มือสั่งงาน ห้าม AI แก้ไฟล์นี้เองโดยพลการ

---

## 0) What this file is
- ใช้ตอนทำ milestone / ยกระดับระบบ / ทำให้พร้อมปล่อยจริง
- ใช้ร่วมกับ "Small Matrix" (VERIFY/REDOC/RECODE) ในขั้น VERIFY_CORE

---

## 1) Non-Negotiable Global Rules
1) Pages = 3 only: /home /lab /gallery
2) /lab = ONE SHELL: left output + center renderer + right panel + bottom dock
3) Rooms come ONLY from roomRegistry (no demo routes/world split)
4) Save/Export exist ONLY in left output panel
5) No dead buttons: every control has data-action-id + observable effect
6) Doc-first: requirement changes happen in DOC_UPGRADE, not in IMPLEMENT

---

## 2) Big Cycle Overview
```
RESEARCH_GAP
  → DOC_UPGRADE
  → AUDIT_PLAN
  → IMPLEMENT
  → VERIFY_CORE (invoke Small Matrix until D✅ C✅)
  → PTE_TEST_EDITION
  → RELEASE_FEEDBACK
  → loop back to RESEARCH_GAP or DOC_UPGRADE depending on findings
```

---

# 3) PROMPT SET (BIG PACK) — COPY/PASTE READY

## 3.1 PROMPT — RESEARCH_GAP (Blueprint/Reference-driven)
**Goal:** หา "สิ่งที่ขาด/เกิน/เสี่ยง" จาก Blueprint/Reference และของเดิม โดยไม่ invent feature ใหม่  
**Hard rules:** no coding, no doc edits yet (analysis only)

```
COPY PROMPT:
You are Research & Gap Analyst (READ-ONLY).
Do NOT modify docs. Do NOT modify code.
Read: blueprint/reference + existing platform docs + notes.
Output:
1) Gap List (priority): missing/weak/contradictory items
2) Alignment check to Global Rules
3) Recommendations: which doc sections must be upgraded (doc-only proposals)
No new features unless supported by references.
```

---

## 3.2 PROMPT — DOC_UPGRADE (A→E, make Doc the law)
**Goal:** ปรับ Doc ให้ครบ A–E + traceability + global rules + action map + registries  
**Hard rules:** doc-only, no code, no new routes

```
COPY PROMPT:
You are Documentation Architect (DOC-ONLY).
Do NOT modify code.
Update documentation to be the single source of truth:
- A UX/UI intent & interaction rules
- B frontend shell/component/state/action contracts
- C API contract + validation + error semantics + traceId
- D flow/engine determinism + telemetry + test-gate rules
- E DB persistence policy + replay requirements + minimal schema mapping
Must include:
- Global Rules (non-negotiable)
- UI Action Map (action_id + expected_effect + owner_layer)
- Registries spec (roomRegistry/metricRegistry/testRegistry)
- Traceability set (A↔B↔C↔D↔E + cross checks)
Output:
- Doc Patch List
- Updated Doc Structure
- Declaration: Ready for AUDIT_PLAN? YES/NO
```

---

## 3.3 PROMPT — AUDIT_PLAN (Code↔Doc verification + Implementation plan)
**Goal:** ตรวจ code เทียบ doc + ออกแผนแก้ (no coding)  
**Hard rules:** read-only, no edits

```
COPY PROMPT:
You are System Auditor + Implementation Planner (READ-ONLY).
Do NOT modify docs. Do NOT modify code.
Use Doc as source of truth.
Deliver:
1) Verification Table A–E (Doc requires vs Code does vs status + evidence)
2) Cross-layer issues (A↔B↔C↔D↔E and A↔C, A↔E, B↔D)
3) Gap classification: Structural/Missing/Misplaced/Orphan
4) Implementation Plan (ordered tasks): Task ID, Layer, Action, Files, Dependencies, DoD
Output: Ready for IMPLEMENT? YES/NO
```

---

## 3.4 PROMPT — IMPLEMENT (No deviation)
**Goal:** ทำโค้ดตาม Implementation Plan เท่านั้น  
**Hard rules:** no doc changes, no new routes, no feature invention

```
COPY PROMPT:
You are Implementation Engineer (CODE-ONLY).
Do NOT modify documentation.
Implement code EXACTLY according to the Implementation Plan with NO deviation:
- no new routes/pages/demos
- respect Global Rules (3 pages, one shell, registry-first, output-only save/export, no dead buttons)
Deliver:
- List of changed files
- Requirement/Task → code mapping
- Notes on any blockers (but do NOT change docs)
```

---

## 3.5 PROMPT — VERIFY_CORE (Invoke Small Matrix)
**Goal:** หลัง implement ให้ใช้ Small Matrix จน D✅ C✅  
**Hard rules:** follow firewall: verify-only or doc-only or code-only per round

```
COPY PROMPT:
Run the Small Matrix Core Cycle:
1) VERIFY_ONLY (read-only) to compute D and C status
2) If D✅ C❌ → RECODE_ONLY
   If D❌ C✅ → REDOC_ONLY
   If D❌ C❌ → REDOC(minimal lock) then RECODE
3) Repeat until D✅ C✅
Do NOT mix doc and code edits in the same round.
```

---

## 3.6 PROMPT — PTE_TEST_EDITION (Production Test Edition)
**Goal:** เทสจริงเพื่อปล่อย  
**Hard rules:** no edits, report only

```
COPY PROMPT:
You are Release Auditor + Test Lead (READ-ONLY).
Do NOT modify docs or code.
Run Production Test Edition suites:
T0 Doc Tests: A–E + traceability + action map + registries + global rules
T1 UI Function Tests: button sweep (data-action-id) => no dead buttons
T2 Integration Tests: FE↔API schema, traceId end-to-end, engine determinism, telemetry registry, save/reopen
T3 Golden Flows:
F1 Gallery→Lab→Run→Select metrics→Dock→Save→Reopen
F2 Lab→Validate→TestGate room→Run→Save counterexample→Replay
F3 Notes create→refresh→persist
Output:
- PASS/FAIL per suite
- GO/NO-GO release decision
- Bug list (Critical/High/Med/Low) with evidence pointers
```

---

## 3.7 PROMPT — RELEASE_FEEDBACK (Post-test decision + learning)
**Goal:** ตัดสินปล่อย + เก็บ feedback เพื่อนำไป loop ต่อ  
**Hard rules:** no coding, no doc edits

```
COPY PROMPT:
You are Release Manager (READ-ONLY).
Given PTE results, decide:
- GO or NO-GO
If NO-GO: classify root cause:
- Doc gap (go to DOC_UPGRADE)
- Code mismatch (go to RECODE via Small Matrix)
- Test spec gap (update PTE spec in doc cycle)
Define next loop entry point: RESEARCH_GAP or DOC_UPGRADE or AUDIT_PLAN.
```

---

## 4) When to loop where (Big Decision)
- If blueprint/reference suggests missing capability → RESEARCH_GAP then DOC_UPGRADE
- If doc is updated → AUDIT_PLAN
- If plan exists → IMPLEMENT
- After implement → VERIFY_CORE (Small Matrix)
- When D✅ C✅ → PTE_TEST_EDITION
- After PTE → RELEASE_FEEDBACK then loop

---

## 5) What this file is NOT
- Not the small matrix prompt file
- Not implementation code
- Not a substitute for documentary content
This is the orchestration program only.

---
