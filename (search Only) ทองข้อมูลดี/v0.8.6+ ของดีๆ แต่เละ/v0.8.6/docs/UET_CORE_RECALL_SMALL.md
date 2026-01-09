# UET — CORE CYCLE RECALL FILE (Small Matrix)
**File name (suggested):** `UET_CORE_RECALL_SMALL.md`  
**Purpose:** คู่มือรีคอลสำหรับสั่ง AI ทำงาน "แกนเล็ก" แบบไม่มั่ว ไม่แตะข้ามโลก  
**Scope:** ใช้เฉพาะ Core Cycle (VERIFY / REDOC / RECODE) เท่านั้น  
**Rule:** ไฟล์นี้เป็น "คู่มือสั่งงาน" ห้าม AI แก้ไขไฟล์นี้เองโดยพลการ

---

## 0) What this file is
ไฟล์นี้คือ "Manual สำหรับเรียกใช้ Prompt" แบบ copy/paste  
ใช้เมื่อ:
- แก้โค้ดแล้วพัง
- AI ทำมั่ว แก้ข้ามโลก
- ต้องรีเช็คว่าตอนนี้ควร REDOC หรือ RECODE
- ต้องวน cycle ให้ระบบกลับมาสอดคล้อง

---

## 1) Non-Negotiable Global Rules (ใช้เป็นเกณฑ์ตัดสินเสมอ)
1) **Pages = 3 เท่านั้น**: `/home`, `/lab`, `/gallery`
2) **/lab = ONE SHELL**: left output + center renderer + right panel + bottom dock
3) **Rooms = Registry**: ห้องทั้งหมดมาจาก `roomRegistry` เท่านั้น (ห้าม demo route/โลกแยก)
4) **Save/Export อยู่ Output panel เท่านั้น**
5) **No dead buttons**: ทุกปุ่ม/setting ต้องมี `data-action-id` + observable effect

> ถ้า AI เสนอการละเมิดกฎข้อใดข้อหนึ่ง = ถือว่าผิดทันที

---

## 2) The Small Matrix (D,C)
นิยามสถานะ:
- **D = Doc correctness** (Doc ครบ, ไม่ขัดกัน, traceable)
- **C = Code correctness** (Code ทำตาม doc+rules และ flow ผ่าน)

Decision Matrix:
- **D✅ C✅** → ผ่าน (จบ cycle)
- **D✅ C❌** → ใช้ `RECODE_ONLY`
- **D❌ C✅** → ใช้ `REDOC_ONLY`
- **D❌ C❌** → ห้ามแก้พร้อมกัน: `VERIFY → REDOC(minimal lock) → VERIFY → RECODE`

---

## 3) The Core Cycle (loop)
Run:
1) `VERIFY_ONLY`
2) ดูผล D/C → เลือก `REDOC_ONLY` หรือ `RECODE_ONLY` (เลือกอย่างใดอย่างหนึ่งเท่านั้น)
3) กลับไป `VERIFY_ONLY`
4) วนจนได้ D✅ C✅

**กฎเหล็ก:** 1 รอบทำได้แค่อย่างเดียว (Verify หรือ Doc หรือ Code)

---

# 4) PROMPT SET (COPY/PASTE READY)
> หมายเหตุ: ใช้ตามลำดับใน cycle เท่านั้น

---

## 4.1 PROMPT — VERIFY_ONLY (Read-only Judge)
**When to use:** ไม่แน่ใจว่าใครผิด / ก่อนเลือก REDOC หรือ RECODE / หลัง implement เพื่อเช็คซ้ำ  
**Hard rule:** ห้ามแก้ Doc/Code/ห้ามเสนอ solution/ห้ามเขียนโค้ด

**COPY PROMPT:**
```
You are **System Verifier (READ-ONLY)**.
Do NOT modify documentation. Do NOT modify code. Do NOT propose fixes. Only verify and report.

Use these **Global Rules** as mandatory checks:
1) Pages = 3 only: /home /lab /gallery
2) /lab = one shell (left output + center renderer + right panel + bottom dock)
3) Rooms come ONLY from roomRegistry (no demo routes)
4) Save/Export exist ONLY in left output panel
5) No dead buttons: every button/control has data-action-id + observable effect

Tasks:
A) Evaluate Documentary (D):
- Check A→E completeness and traceability A↔B↔C↔D↔E
- Check action map exists and is complete
- Check global rules are explicitly documented
Return D = ✅ or ❌ with reasons.

B) Evaluate Codebase (C):
- Check routes, shell structure, registry usage, save/export placement, button wiring, basic flows
Return C = ✅ or ❌ with reasons.

C) Cross-layer consistency:
Report issues in A↔B↔C↔D↔E and cross-checks A↔C, A↔E, B↔D.

D) Classify gaps into:
1) Structural Violation
2) Missing Implementation
3) Misplaced Logic
4) Orphan (doc-only or code-only)

Output format (STRICT):
VERIFY REPORT
- D: ✅/❌ + reasons
- C: ✅/❌ + reasons
- Gap List (priority): [Type] description + evidence pointers
- Decision: Next Mode = REDOC_ONLY or RECODE_ONLY (choose one) + reason
End with: "NO CHANGES performed in this round."
```

---

## 4.2 PROMPT — REDOC_ONLY (Documentation-only)
**When to use:** D❌ C✅ (Doc ไม่ครบ/ไม่ชัด) หรือ Verify ชี้ว่า Doc ต้อง lock ก่อน  
**Hard rule:** ห้ามแตะโค้ด ห้ามแนะนำ refactor code ในรอบนี้

**COPY PROMPT:**
```
You are **Documentation Architect (DOC-ONLY)**.
Do NOT modify code. Do NOT propose code changes. Only update documentation to become the single source of truth.

Goal:
- Fix documentation A→E completeness
- Add/clarify: Global Rules, Action Map, Registries Spec, Traceability A↔B↔C↔D↔E
- Remove contradictions and ambiguity
- Do NOT invent new features or new routes not supported by blueprint/reference

Output format (STRICT):
REDOC REPORT
- Files/sections updated (doc-only)
- What was missing/ambiguous
- What is now clarified (key rules + action map + registries + traceability)
- Doc Status: Ready for RECODE? YES/NO + reason

End with: "NO CODE CHANGES performed in this round."
```

---

## 4.3 PROMPT — RECODE_ONLY (Code-only)
**When to use:** D✅ C❌ (Doc ถูกแล้ว แต่โค้ดไม่ตรง)  
**Hard rule:** ห้ามแก้เอกสาร ห้ามเปลี่ยน requirement ห้ามเพิ่ม route/demo

**COPY PROMPT:**
```
You are **Implementation Engineer (CODE-ONLY)**.
Do NOT modify documentation. Documentation is the law (source of truth).
Do NOT invent new features/routes. No demo pages.

Task:
- Modify code minimally to match documentation and Global Rules:
1) Pages = 3 only
2) /lab = one shell
3) Rooms only from roomRegistry
4) Save/Export only in left output panel
5) No dead buttons (data-action-id + observable effect)

Deliverables (STRICT):
RECODE REPORT
- Files changed (code-only)
- Requirement → code mapping (which doc rule each change satisfies)
- Remaining gaps (if any) but do NOT suggest changing docs

End with: "NO DOC CHANGES performed in this round."
```

---

# 5) Safety Locks (เพื่อกัน AI มั่ว)
- If this is VERIFY round → any suggestion to change doc/code is disallowed.
- If this is REDOC round → any code edits or refactor plans are disallowed.
- If this is RECODE round → any doc edits or requirement changes are disallowed.
- If D❌ C❌ → MUST run two separate rounds: REDOC minimal lock first, then RECODE.

---

# 6) Quick Start (คำสั่งใช้งานเร็ว)
1) Run VERIFY_ONLY
2) If D✅ C❌ → run RECODE_ONLY → then VERIFY_ONLY again
3) If D❌ C✅ → run REDOC_ONLY → then VERIFY_ONLY again
4) Repeat until D✅ C✅

---

# 7) What this file is NOT
- Not the big growth roadmap
- Not implementation plan
- Not test edition suite (PTE)
This is the **small control matrix only**.

---
