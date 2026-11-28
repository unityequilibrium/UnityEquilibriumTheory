# Post-mortem: why the cards T030 and T033-T036 failed or could not decide (question design, not only theory)

Written 2026-11-27 by Claude (AI) at the author's request. The author asked whether these cards failed because the
theory is wrong or because the AI set poor research questions without following a research-design procedure. This
is a self-review of the AI's work. It changes no level, verdict or criterion: every FAILED stays FAILED (STANDARD.md
section 7 forbids renaming a failure). It records what each failure does and does not tell us, so a later reader does
not misread it.

## สรุปภาษาไทย

- **ส่วนใหญ่เป็นความผิดของ AI ในการตั้งโจทย์** ไม่ใช่หลักฐานว่าสมการแกนของ UET ผิด แต่ก็**ไม่ใช่หลักฐานว่า UET ถูก**ด้วย
- AI กระโดดจากสมการไปหาข้อมูลเลย โดย**ไม่ได้ศึกษางานของวงการก่อน** (Hall, Forbes, Cahill เรื่องการอดอาหาร; Esposito 2010
  เรื่องโรงไฟฟ้า) ถ้าศึกษาก่อนจะเห็นว่าหลายข้อขัดกับสิ่งที่วงการรู้อยู่แล้ว หรือต่อให้ผ่านก็ไม่ได้บอกอะไรที่เป็นของ UET
- การจับคู่ "ไขมัน = pool, เนื้อ = โครงสร้าง, น้ำหนักตัว = ของสำรองชั้น 3" **AI เลือกเอง** ผู้เขียนไม่ได้เสนอ
- มาตรฐาน v2 บังคับเรื่องความเรียบร้อย (ลงทะเบียนเกณฑ์ก่อน อนุมัติก่อนรัน รันครั้งเดียว) ซึ่ง AI ทำครบ
  แต่มาตรฐาน**ไม่ได้มีขั้นตรวจคุณภาพของโจทย์** และ AI ก็ไม่ได้ตรวจเอง
- ข้อที่ผ่าน (T031 GP-B, T032 ดาวคู่) ก็ไม่ได้ยืนยันอะไรที่เป็นของ UET เพราะเป็นฟิสิกส์ที่ GR และทฤษฎีแรงไทดัลทายไว้แล้ว

## 1. Card by card

| Card | Claim | Outcome | What went wrong in the question | Whose error |
|---|---|---|---|---|
| T030 | C_L3_OPENNESS_LAYER3 | FAIL -> FAILED | Tested "a fasting body loses mass at a constant specific rate" (D14's exponential leak). Fasting physiology has known since Keys (1950) and Hall's models that energy use falls as the body shrinks and adapts; a constant specific rate was contrary to known data before the run. The body-as-layer-3-pool mapping was the AI's. | AI: no literature map; AI-chosen mapping |
| T033 | C_L3_OPENNESS_ORDER | INCONCLUSIVE (L2) | Tested "real plants run near the Curzon-Ahlborn efficiency". The claim says openness sets a ceiling; "systems run at the ceiling" was an AI reading, labelled as such in the card. Esposito et al. 2010, the data source itself, already shows plants scatter around eta_CA and that eta_CA is not a bound. A PASS would only have repeated that paper. | AI: weak reading of the claim; source not read for what it already concluded |
| T034 | C_L3_AFTER_CLOSING | INCONCLUSIVE | The card needed at least 6 points; the source plotted 3 fasting days. The mapping "lean tissue eats the fat pool" contradicts Forbes (fat and lean are lost together in a proportion set by fat mass) and Cahill (protein loss falls as ketones take over). The trend seen (41.7 -> 31.3 g/day) is what Cahill predicts. | AI: data shape not checked; AI mapping against known physiology |
| T035 | C_L3_SURVIVAL_BURN | INCONCLUSIVE | Needed a weight series; Figure 1 of Stewart & Fleming 1973 is a photograph, only start and end weights exist. | AI: data shape not checked |
| T036 | C_L3_SURVIVAL_BURN | FAIL -> FAILED | D20's curve P = P0 (R/R0)^beta was chosen by the AI after T030 failed, beta calibrated on one person, then expected to hold for ten other people. Individual differences in fasting loss are known (Forbes: fatter people lose less lean and more energy per kg). The fit form had no derivation from the core equations. | AI: post-hoc curve; one-subject calibration extended to a population known to vary |

## 2. The common causes

1. **No map of the mainstream field before the question.** Each card named a "nearest theory" as a label only
   (STANDARD.md section 3 item 3 asks for the nearest theory and a variable map; it was filled as a name, not studied).
   The literature map (LITERATURE_MAP_FASTING.md) was written only after the author asked, after T036.
2. **The question could not tell UET apart from the mainstream.** No card asked "what does the established model
   predict for the same data, and would a PASS favour UET over it?". Even the passes (T031, T032) reproduce GR and
   tidal theory, so they confirm the composition is consistent with known physics, not that UET adds anything.
3. **AI-chosen mappings tested as if they were the theory.** Fat = pool, lean = structures, body mass = layer-3
   stock, "plants run at the ceiling": all AI interpretations (AGENTS.md section 3 item 9). A failure of such a
   mapping says the mapping is wrong; it does not test the core equation in a system where the mapping is right.
4. **Data shape not checked before the card** (T034, T035): two approval cycles spent on cards that could not decide.
5. **Rescue by a new curve.** After T030 failed, D20 added a free exponent to save the fasting application. It was
   registered honestly as a new L0 claim, but it was the pattern the standard warns against (adding a branch to escape
   a comparator), and it failed on the next independent data.

## 3. What the failures do and do not mean

- C_L3_OPENNESS_LAYER3 is FAILED and stays FAILED. Read: the composition, as applied by the AI to fasting bodies,
  does not describe them. The algebra of the composition (its L1 derivation checks) was not shown wrong; testing it
  again needs a new claim with a mapping justified from the mainstream model, and a new card.
- C_L3_SURVIVAL_BURN is FAILED. It was an AI curve, not a core relation; nothing about the core follows from it.
- The INCONCLUSIVE cards tell us nothing about the theory; they were undecidable by design.
- None of this is evidence that UET is right. The project still has no confirmed UET-distinct prediction from this line.

## 4. Questions to answer before drafting a card (AI practice from now on)

1. What does the mainstream model of this field predict for the same observable (name the source and equation)?
2. Would a PASS favour UET over that model, or only agree with both? If only both, say so in the card.
3. Who chose the mapping from UET variables to this system: the author or the AI? If the AI, label it and justify it
   from the field's own variables.
4. Does the source really contain the series the criterion needs (count points with digits masked)?
5. Is any parameter calibrated on one case and then extended to cases the field already knows vary?

These are the AI's working rules (Claude memory), not a new gate: adding a gate to the standard needs the author's
approval (AGENTS.md section 3 item 8).
