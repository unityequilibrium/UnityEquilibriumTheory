# UET Research Standard v2

> **สถานะเอกสาร: APPROVED — อนุมัติโดยผู้เขียน 2026-11-08 (W2); แก้ไข §15 อนุมัติ 2026-11-09**
> เอกสารนี้เป็นมาตรฐานควบคุม**ฉบับเดียว**ด้านการยืนยันหลักฐานและสถานะ claim ของงานวิจัยใน Harness
> มาตรฐานด้าน**ปฏิบัติงาน**ใน `docs/topics/For Work/` (โครงสร้าง topic, README โค้ด, data, reference,
> result, formula audit, paper, visualization, template และ calculation contract) **ยังมีผลบังคับ** ตาม §15
> ส่วนชุดคำศัพท์สถานะและบันไดขั้นตอนเดิมถูกแทนด้วยเอกสารนี้
> ไฟล์ใน `For Work/` อยู่ที่เดิมและห้ามแก้ (calculation contract เดิม 6 ฉบับล็อก hash ไว้เป็น REQUIRED)
> ยกเว้นประกาศ superseded
> Schema ที่เครื่องตรวจ: [`docs/standard/schema.json`](standard/schema.json)

## 0. หลักการ 5 ข้อ

1. **ความจริงมาจากการเผชิญข้อมูล ไม่ใช่จากจำนวน gate ที่ผ่าน** งานจะมีน้ำหนักทางวิทยาศาสตร์เมื่อทฤษฎีมีโอกาสแพ้ข้อมูลภายนอกได้จริง
2. **ผลลบคือผลวิจัย** ตกให้บันทึก `FAILED` ตรง ๆ ห้ามแปลงชื่อเป็น PASS ห้ามหั่น scope ห้ามแตก branch เพื่อหนีผล
3. **เกณฑ์ต้องมาก่อนผล** เกณฑ์ผ่าน/ตกของการทดสอบภายนอกต้อง commit และได้รับอนุมัติก่อนรัน
4. **ทดลองอิสระ อ้างผลเข้มงวด** การสำรวจไม่มี gate ส่วนการยกระดับ claim มี gate
5. **สั้นและบังคับด้วยเครื่อง** กฎที่เครื่องตรวจไม่ได้ให้เก็บไว้น้อยที่สุด กฎที่เครื่องตรวจได้ต้องอยู่ใน CI

---

## 1. ระดับหลักฐาน (enum เดียวทั้ง repo)

| ระดับ | ความหมาย | เงื่อนไขขั้นต่ำ | ใครยกระดับได้ |
|---|---|---|---|
| `L0_SPECULATIVE` | ไอเดีย สมมติฐาน งาน sandbox | ไม่มี | ใครก็ได้ |
| `L1_CONSISTENT` | คณิตศาสตร์สอดคล้องในตัวเอง | derivation check + unit check + known-limit แบบไม่ tautological (§6) | AI ได้ เมื่อ physics test ผ่านใน CI |
| `L2_CONFRONTED` | เผชิญข้อมูลภายนอกตาม Test Card ที่ล็อกไว้ล่วงหน้า (จะผ่านหรือตกก็ได้) | Test Card ที่ approved และ commit ก่อน Result (§4) | ต้องได้รับอนุมัติจากผู้เขียน |
| `L3_REPLICATED` | คนนอกหรือโค้ดอิสระทำซ้ำได้ หรือผ่าน peer review | หลักฐานภายนอกที่มีแหล่งอ้างอิง | ผู้เขียนเท่านั้น |
| `FAILED` | ตกการทดสอบระดับ L1 หรือ L2 | ระบุการทดสอบที่ตก | ใครก็ได้ ห้ามลบภายหลัง |

**กฎของระดับ**
- ระดับเป็นของ **claim** ไม่ใช่ของ topic หรือโฟลเดอร์ หนึ่ง topic อาจมี claim หลายระดับปนกัน
- `L2_CONFRONTED` มีสองแบบ ซึ่งต้องระบุใน Test Card (`test_kind`):
  - `CONSTRAINT`: ข้อมูลเป็นที่รู้กันแล้ว เช่น ขอบเขต Cassini ผลที่ได้คือบริเวณ parameter ที่รอด หรือการตัดทิ้ง **ห้ามเรียกว่า "ทำนาย"**
  - `BLIND_PREDICTION`: คำนวณก่อนดูข้อมูล holdout เท่านั้นที่ใช้คำว่า "ทำนาย" ได้
- ถ้า claim ระดับ `L2` ถูกแก้สมการหรือ parameter หลังรัน ระดับจะกลับไปเป็น `L1` จนกว่าจะเปิด Test Card ใหม่
- `FAILED` ไม่ใช่ความอับอาย แต่เป็นข้อมูลที่บอกว่าทางไหนไปไม่ได้ ถ้าจะเสนอ branch หรือ term ใหม่หลังตก ให้นับเป็นสมมติฐานใหม่ที่ `L0` และเปิด Test Card ใหม่ claim เดิมยังคงเป็น `FAILED`
- **ห้ามสร้างค่าสถานะใหม่** นอกจาก 5 ค่านี้ในไฟล์ใหม่ ถ้าต้องการรายละเอียดให้ใช้ฟิลด์ข้อความ `note`

## 2. สองโซน

| โซน | ที่อยู่ | กฎ |
|---|---|---|
| **Sandbox** | `sandbox/<ชื่อ>/` หรือไฟล์ที่ประกาศ `level: L0_SPECULATIVE` | ไม่มี gate ไม่มี hash ไม่มี contract อ้างผลใน README หรือ claim ไม่ได้ |
| **Claims** | `docs/standard/claims.json` + ไฟล์ที่มันลิงก์ถึง | ทุกข้อความเชิงวิทยาศาสตร์ใน README และเอกสารสาธารณะต้องชี้ไปยัง claim id ที่มีระดับกำกับ |

ข้อความใน README ที่ไม่มี claim id กำกับให้ถือเป็น `L0` โดยอัตโนมัติ

## 3. Theory Card (การ์ดทฤษฎี)

ไฟล์: `docs/core/THEORY_CARD.md` (คนอ่าน) + `docs/core/theory_card.json` (เครื่องตรวจ, schema `theory_card`)

ต้องมีหัวข้อต่อไปนี้ ถ้ายังตอบไม่ได้ให้เขียนว่า "none yet" ห้ามเว้นว่าง:

1. **สมการแกน**: action หรือสมการเคลื่อนที่ พร้อม sign convention และระบบหน่วย
2. **ตาราง field/parameter**: ชื่อ ความหมาย mass dimension และค่าหรือช่วงที่อนุญาต
3. **คลาสทฤษฎีที่รู้จักแล้วที่ใกล้ที่สุด** และ map ระหว่างตัวแปร UET กับตัวแปรของคลาสนั้น
4. **สิ่งที่ต่างจากคลาสนั้น** ระบุเป็นรายการที่ตรวจได้ ถ้าไม่มี ให้บอกตรง ๆ
5. **Parameter ที่ซ้ำซ้อน** ที่ดูดซับได้ด้วย field redefinition หรือการเปลี่ยนหน่วย และชุด parameter อิสระที่ใช้แทน
6. **Prediction ที่วัดได้**: observable, ระบบที่วัด, และ claim id ที่เกี่ยวข้อง
7. **Lane mapping**: C, Φ และ Π map ไปยังปริมาณมาตรฐานใดในแต่ละ lane โดย C ไม่ใช่มวลโดยทั่วไป
8. **ผู้อนุมัติและวันที่**

การ์ดแต่ละฉบับมี `version` ถ้าแก้สมการแกนต้องขึ้น version และระบุ claim ที่ได้รับผลกระทบ

## 4. Test Card = preregistration

ไฟล์: `docs/standard/tests/<TEST_ID>.json` (schema `test_card`)

ฟิลด์บังคับ:
- `hypothesis`
- `observable` (ปริมาณ หน่วย และ domain)
- `test_kind` (`CONSTRAINT` หรือ `BLIND_PREDICTION`)
- `data_sources` (DOI/URL + sha256 ของไฟล์ดิบ + `exposure`: `UNSEEN`, `SEEN_SUMMARY` หรือ `SEEN_FULL`)
- `prediction_method` (สคริปต์ + theory card version)
- `free_parameters` และ `fixed_parameters` (ที่ห้าม fit)
- `pass_criterion` และ `fail_criterion` เป็น**ตัวเลขหรือนิพจน์ที่คำนวณได้**
- `approval` (ชื่อ + วันที่) และ `status` ของการ์ด (`DRAFT`, `APPROVED` หรือ `CLOSED`)

กฎ:
- Commit ที่ทำให้การ์ดเป็น `APPROVED` ต้อง**มาก่อน** commit แรกของ Result ที่อ้างถึงการ์ดนั้น CI ตรวจลำดับนี้
- หลัง `APPROVED` แล้ว ห้ามแก้ `pass_criterion`, `fail_criterion`, `data_sources`, `free_parameters` และ `fixed_parameters` ถ้าต้องแก้ให้เปิดการ์ดใหม่ และการ์ดเดิมยังเก็บไว้
- `BLIND_PREDICTION` ต้องมี `exposure: UNSEEN` สำหรับข้อมูล holdout
- **เกณฑ์ที่ห้ามใช้**: "ไม่ได้แตะข้อมูล", "สคริปต์รันจบ", "hash ตรง", "ผ่าน N/N ข้อ" ถ้าข้อเหล่านั้นไม่ได้เทียบกับข้อมูล เพราะทั้งหมดนี้เป็นเรื่องความเรียบร้อย ไม่ใช่หลักฐาน
- AI ร่างการ์ดได้ แต่**อนุมัติการ์ดของตัวเองไม่ได้**

## 5. Result record

ไฟล์: `docs/standard/results/<RESULT_ID>.json` (schema `result`)

ฟิลด์บังคับ:
- `claim_id`, `level` (enum §1)
- `test_card_id` (บังคับเมื่อ level เป็น L2 ขึ้นไป หรือเป็น FAILED จาก L2)
- `outcome` (`PASS`, `FAIL` หรือ `INCONCLUSIVE` เทียบกับเกณฑ์ในการ์ด)
- `numbers` (ค่าที่คำนวณได้ ความไม่แน่นอน หน่วย)
- `producer` (สคริปต์ + commit) และ `artifacts`

ถ้ามี calculation contract v1 เดิม (`docs/meta/schemas/calculation_contract_v1.schema.json`) ให้อ้างผ่าน `calculation_contract_id` แทนการเขียนรายละเอียด model/observation/error budget ซ้ำ Contract v1 ยังใช้ได้ต่อและ CI ยังตรวจตามเดิม

## 6. มาตรฐานคณิตศาสตร์และฟิสิกส์ (สิ่งที่นับเป็น "physics test")

Test ที่นับเป็นหลักฐานระดับ L1 ต้องติด pytest marker `physics` และเป็นแบบใดแบบหนึ่งต่อไปนี้:

| แบบ | ข้อกำหนด |
|---|---|
| **Derivation check** | ใช้ sympy (หรือเทียบเท่า) แปรผัน action หรือ derive สมการจากหลักการที่ประกาศ แล้วเทียบกับฟังก์ชันในโค้ดที่จุดสุ่มอย่างน้อย 20 จุด ค่าต่างสัมพัทธ์ < 1e-10 |
| **Known solution / known limit** | เทียบกับคำตอบ analytic ที่ตีพิมพ์แล้ว (เช่น Schwarzschild, de Sitter, PPN ของ Brans–Dicke) **ผ่าน code path เดียวกับกรณีทั่วไป** ถ้า limit ไปออก branch `if param == 0: return reference(...)` ไม่นับ เพราะเป็น tautology |
| **Convergence** | ลำดับการลู่เข้าที่วัดได้ ตรงกับลำดับที่ออกแบบ ±0.2 บน grid อย่างน้อย 3 ระดับ |
| **Conservation / identity** | กฎอนุรักษ์หรือ identity (เช่น Bianchi หรือ Noether) ที่ต้องเป็นจริง**เพราะฟิสิกส์** ไม่ใช่เพราะโค้ดเขียนให้เป็นจริงโดยตรง |
| **External comparison** | ตาม Test Card §4 |

ข้อกำหนดเพิ่มเติม:
- **Dimensional analysis**: ทุกสมการใหม่ต้องมีตาราง mass dimension และ test ที่ตรวจความสอดคล้องของมิติ
- **Parameter redundancy**: ก่อนอ้างว่า parameter มีความหมายทางกายภาพ ให้ตรวจก่อนว่าดูดซับได้ด้วย field redefinition หรือไม่ (ตัวอย่างคือ ε ใน parent action)
- **Well-posedness**: PDE ที่จะใช้ทำนายต้องแสดง hyperbolicity หรือ well-posedness ใน regime ที่ใช้
- **Error budget**: ผลเชิงตัวเลขที่จะเทียบกับข้อมูลต้องมีความไม่แน่นอนทั้งจาก numerics และจาก input
- Test ที่ assert ชื่อสถานะ, hash หรือการมีอยู่ของไฟล์ เขียนได้ตามสะดวก แต่**ไม่นับเป็นหลักฐาน** และ CI รายงานจำนวนแยกกัน

## 7. ข้อมูลและ provenance

- ข้อมูลดิบภายนอกทุกไฟล์ลงทะเบียนใน `docs/standard/data_manifest.json` (schema `data_entry`) พร้อม source, DOI/URL, วันที่ดึง, sha256, license และสถานะ public/private
- **Hash-lock เฉพาะข้อมูลดิบภายนอก** ไม่ใช้กับ log, เอกสาร หรือ artifact ที่ generate ใหม่ได้ ห้ามใช้ baseline ที่นับจำนวนไฟล์
- Artifact ที่ generate ต้อง regenerate ได้จาก `producer` + input ที่ลงทะเบียนไว้ ถ้า regenerate ไม่ได้ ให้ถือเป็น `L0`
- ข้อมูลที่ใช้ calibrate หรือ fit แล้ว ห้ามใช้เป็น validation ของ claim เดียวกัน (density circularity ใน Topic 13 เป็นตัวอย่างที่ต้องหลีกเลี่ยง)

## 8. Legacy

- ทุก artifact, gate, contract, update log และผลเดิมที่มีก่อนวันอนุมัติเอกสารนี้ **ห้ามแก้ไขหรือลบ** และได้สถานะรวมว่า `LEGACY_UNREVIEWED` (เป็นป้ายบอกที่มา ไม่ใช่ระดับหลักฐาน)
- ผลเดิมจะถูก**ยกเป็น claim** ได้ต่อเมื่อผ่านเงื่อนไขของระดับนั้นใหม่ (เช่น เขียน physics test ตาม §6) ถ้า code ไม่เปลี่ยนก็ไม่ต้องรันผลทางวิทยาศาสตร์เดิมซ้ำ
- สูตร legacy 263 แถวใน FORMULA_AUDIT และ foundation gate F0–F8 **ไม่อยู่บนเส้นทางวิกฤต**ของ Core อีกต่อไป
- ตารางแปลงคำศัพท์เดิมอยู่ใน §13

## 9. รูปแบบของ wave และงบเวลา

- **หนึ่ง wave** = หนึ่งคำถาม + ผลใหม่อย่างน้อยหนึ่งอย่าง (ตัวเลขที่คำนวณ, derivation, หรือผล FAILED) + หนึ่ง commit
- **บันทึก wave** ลงใน `UPDATE_LOG.md` ของ topic หรือ `docs/core/UPDATE_LOG.md` ไม่เกิน 6 บรรทัด:
  ```
  ## YYYY-MM-DD — <คำถาม>
  ทำ: <สิ่งที่ทำ>
  ผล: <ตัวเลข/ข้อสรุป + หน่วย>
  ระดับ: <claim id> → <level>
  ถัดไป: <คำถามถัดไปหนึ่งข้อ>
  commit: <sha>
  ```
- **งบ governance**: งานจัดระเบียบ เอกสาร หรือเครื่องมือตรวจ ไม่เกินประมาณ 20% ของ wave ในแต่ละสัปดาห์ ถ้าจะสร้าง **audit script หรือ gate ใหม่** ต้องได้รับอนุมัติจากผู้เขียนก่อน
- WORK_LEDGER รายวันยังใช้ต่อตาม `WORK_LEDGER/README.md` แต่ให้สั้น ไม่เกินประมาณ 12 บรรทัดต่อรายการ

## 10. บทบาทของคนและ AI

| การกระทำ | AI | ผู้เขียน |
|---|---|---|
| ทำงานใน sandbox, เขียนโค้ดและ test | ได้ | ได้ |
| ยกระดับเป็น `L1` (เมื่อ physics test ผ่าน CI) | ได้ | ได้ |
| ร่าง Theory Card / Test Card | ได้ | ได้ |
| อนุมัติ Theory Card / Test Card | **ไม่ได้** | ได้ |
| ยกระดับเป็น `L2`, `L3` | **ไม่ได้** | ได้ |
| บันทึก `FAILED` | ได้ (ต้องบันทึก) | ได้ |
| สร้าง gate หรือ audit script ใหม่ | ต้องขออนุมัติ | ได้ |
| ติดต่อคนภายนอก หรือ publish | **ไม่ได้** | ได้ |

AI ต้องแยกให้ชัดว่าเป็น**เจตนาของผู้เขียน**หรือ**ข้อเสนอของ AI** ตัวอย่างที่ AI เลือกขึ้นเอง (เช่น โซ่ 4 อะตอม หรือวัสดุบางชนิด) ต้องระบุว่าเป็นตัวอย่าง ไม่ใช่ข้อกำหนดของทฤษฎี

ทุกประมาณ 3 เดือน ผู้เขียนพิจารณาส่งโน้ตไม่เกิน 5 หน้าที่สรุป Theory Card และผล L2 ให้นักฟิสิกส์ภายนอกอ่าน

## 11. Git และพื้นที่ทำงาน

- ชื่อ branch: `codex/<area>/<task>` (ตาม `pr-scope.yml`) ใช้ได้ทั้ง Codex และ Claude
- Branch ที่เปิดค้างพร้อมกันไม่เกินประมาณ 5 ตัว ส่วน branch ที่ merge แล้วหรือ remote หายแล้ว ให้เก็บกวาดหลังตรวจว่าไม่มี commit ที่ไม่ซ้ำ
- **Working tree ต้องสะอาดก่อนจบวัน** commit สิ่งที่เสร็จ ไฟล์ที่ไม่ใช่งานของเรา**ห้ามแบกข้าม wave** ให้บันทึกแล้วแยกออก
- หนึ่ง wave = หนึ่ง commit ที่ stage เฉพาะไฟล์ของ wave นั้น
- Push หรือเปิด PR เมื่อผู้เขียนสั่ง ส่วน `main` เข้าได้ผ่าน PR เท่านั้น
- Interpreter มาตรฐานในเครื่องคือ `.venv/Scripts/python.exe` และ dependency ด้านวิจัยอยู่ใน `requirements-research.txt` (จะเพิ่มใน W2)

## 12. การบังคับด้วย CI (จะติดตั้งใน W2)

| Check | ตรวจอะไร | ขอบเขต |
|---|---|---|
| `docs/scripts/standard/check_schema.py` | การ์ด, result, claims และ data manifest ต้องผ่าน `schema.json` และค่าระดับต้องอยู่ใน enum | ไฟล์ใหม่หรือที่แก้ |
| `docs/scripts/standard/check_preregistration.py` | ลำดับ commit ระหว่าง Test Card กับ Result, เกณฑ์ไม่ถูกแก้หลัง APPROVED, การ์ดไม่ได้อนุมัติโดยผู้เขียนเอง | การ์ดและ result ทั้งหมด |
| `docs/scripts/standard/check_physics_tests.py` | รัน `pytest -m physics` และรายงานจำนวน physics test กับ bookkeeping test | Core + topic ที่เปลี่ยน |
| `audit_calculation_completeness.py --changed --check` | ตรวจ contract v1 ตามเดิม | ไม่เปลี่ยน |

Gate และ audit script เดิม (inventory, compatibility, aggregate, reconcile v4, migration, scientific-links ฯลฯ) **ยังรันได้** แต่เป็นเครื่องมือวินิจฉัย ไม่มีสถานะเป็นตัวควบคุม และไม่ใช่เงื่อนไขในการยกระดับ claim

## 13. ตารางแปลงคำศัพท์เดิม

| ชุดเดิม | ค่าเดิม | แปลงเป็น |
|---|---|---|
| Rubric 04 | A Hypothesis, B Model statement | `L0` |
| Rubric 04 | C Internal benchmark | สูงสุด `L1` ถ้ามี physics test ตาม §6 ไม่อย่างนั้นเป็น `L0` |
| Rubric 04 | D External replication, E Peer-reviewed | `L3` (ต้องมีหลักฐานภายนอกจริง) |
| EQUATION vocabulary | DRAFT, CANDIDATE, INTERNAL, SIMULATION_ONLY, WARN | `L0` จนกว่าจะมี physics test |
| EQUATION vocabulary | LEGACY | `LEGACY_UNREVIEWED` |
| EQUATION vocabulary | EXTERNAL_COMPARISON | สูงสุด `L1` (การเทียบย้อนหลังที่ไม่ได้ preregister) ถ้าจะเป็น `L2` ต้องเปิด Test Card ใหม่ |
| EQUATION vocabulary | BLOCKED | ไม่ใช่ระดับ ให้เขียนเป็นข้อความ "ถัดไป" ใน log |
| Contract v1 | `COMPLETE_FOR_SCOPE` + `FORMAL_RESULT` | ผู้สมัคร `L1` (ต้องมี physics test) |
| Contract v1 | `PHYSICAL_ACCEPTANCE` | ต้องมี Test Card จึงเป็น `L2` ได้ |
| Topic 13 / Core | `CLOSED_FOR_CORE`, `CLOSED_FOR_LANE`, `PASS_*` | สูงสุด `L1` และต้องตรวจตาม §6 ก่อน |
| ทุกชุด | `*_NO_GO`, `CLOSED_AS_NO_GO`, `FAIL` | `FAILED` (ระบุ scope ใน `note`) |
| 32 TD0–TD6, 02 lifecycle, 18/25 hardening, F0–F8 | ขั้นตอนของ workflow | แทนด้วยรูปแบบ wave §9 + ระดับ §1 |
| Topic tier A–D | ความครบของแพ็กเกจเอกสาร | metadata เรื่องโครงสร้าง ไม่ใช่หลักฐาน |

## 14. การเปลี่ยนผ่าน

| Wave | งาน |
|---|---|
| W1 | ร่างเอกสารนี้และ `schema.json` (เสร็จ) |
| W2 | อนุมัติ, ติดตั้ง CI 3 ตัว, `requirements-research.txt`, marker `physics`, แช่แข็ง For Work ไว้ที่เดิม, ลด `AGENTS.md` และ `docs/core/AGENTS.md` |
| W3 | Theory Card v1 ของ parent action |
| W4 | Derivation check ด้วย sympy ของ parent action (ยืนยันโค้ดเดิม) |
| W5 | Strong-field module: map ξ_c, m_ψ ไปยัง DEF β₀ และ scalar charge ของดาวนิวตรอน + physics tests (เทียบกับผล DEF ที่ตีพิมพ์แล้ว) ส่วน PPN γ ใช้เป็น sanity check |
| W6 | Test Card `T001` (binary-pulsar scalarization/dipole-radiation bounds; ผู้เขียนเลือก 2026-11-08) → อนุมัติ → รัน → Result `L2` หรือ `FAILED` |
| W7 | ซิงค์ `docs/topics/README.md` และ `claims.json` |

กฎที่ขัดกันระหว่างเอกสารนี้กับเอกสารเดิม: **เอกสารนี้ชนะ** ยกเว้นกฎขอบเขต Harness/Superapp, กฎ raw/private และกฎ publication ใน `AGENTS.md` ซึ่งยังมีผลเต็มที่ มาตรฐานด้านปฏิบัติงานที่ระบุใน §15 ยังใช้ต่อในส่วนที่ไม่ขัดกับเอกสารนี้

## 15. มาตรฐานด้านปฏิบัติงานที่ยังมีผลบังคับ

เอกสารนี้ไม่ได้เขียนกฎด้านการจัดไฟล์และการทำงานประจำวันซ้ำ ไฟล์ใน `docs/topics/For Work/` ต่อไปนี้**ยังเป็นมาตรฐานที่ต้องทำตาม** (ไฟล์อยู่ที่เดิมและห้ามแก้):

| เรื่อง | ไฟล์ที่ยังใช้ |
|---|---|
| โครงสร้างและสถาปัตยกรรมของ topic | `10_Topic_Architecture_5x4.md`, `20_TEMPLATE_README.md` |
| README ของโค้ด | `11_Code_README_Standard.md` |
| การดึง เก็บ และระบุที่มาของข้อมูล | `12_Data_Standard.md` |
| การอ้างอิงแหล่งที่มา | `13_Reference_Standard.md` |
| ผลลัพธ์และ artifact | `14_Result_Standard.md`, `21_TEMPLATE_ANALYSIS.md` |
| paper | `15_Paper_Standard.md`, `22_UET_PAPER_TEMPLATE.tex` |
| visualization | `16_Cinematic_Viz_Standard.md` |
| ที่มาของสูตร หน่วย และค่าคงที่ | `17_Formula_Audit_Standard.md`, `23_TEMPLATE_FORMULA_AUDIT.md` |
| update log ของ topic | `24_TEMPLATE_UPDATE_LOG.md` (ใช้รูปแบบสั้นตาม §9 สำหรับ wave ใหม่) |
| calculation contract | `30_Calculation_and_Observation_Completeness_Standard.md`, `31_TEMPLATE_CALCULATION_CONTRACT.md` |

**กฎการใช้ร่วมกัน:**
1. ถ้าไฟล์ข้างบนใช้คำศัพท์สถานะเดิม (เช่น claim class A–E, proof-status, `PASS`/`BLOCKED`, TD0–TD6, F0–F8) ให้แปลงเป็นระดับตาม §1 โดยใช้ตาราง §13 ห้ามสร้างค่าสถานะใหม่
2. ถ้าไฟล์ข้างบนกำหนดให้ hash-lock ไฟล์ที่ generate ซ้ำได้ (log, เอกสาร, artifact) ให้ทำตาม §7 แทน คือ hash เฉพาะข้อมูลดิบภายนอก
3. การยกระดับ claim, Test Card และเกณฑ์ผ่าน/ตก ใช้เอกสารนี้เท่านั้น
4. ข้อมูลภายนอกต้องเก็บและระบุที่มาตาม `12` **และ**ลงทะเบียนใน `docs/standard/data_manifest.json` ตาม §7 ส่วนการอ้างอิงในเอกสารให้ทำตาม `13` และระบุ DOI/URL ใน data manifest หรือ Test Card ด้วย

**ไฟล์ที่ถูกแทนแล้ว** (เป็นประวัติเท่านั้น): `00_README.md` (index เดิม), `01`, `02`, `03`, `04`, `18`, `25`, `26`–`29`, `32`, `EQUATION_RESEARCH_AND_PHYSICAL_CORRESPONDENCE_STANDARD.md` และ `UPDATE_LOG.md` ของ For Work หน้าที่ของไฟล์เหล่านี้ถูกแทนด้วย §0–§14

