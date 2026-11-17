# T017 ร่าง: กฎ abundance ชั้น 3 กับรอบเซลล์ (topic 0.22) — 2026-11-17

> สถานะ: **ร่างการออกแบบ ยังไม่ใช่ Test Card** เพราะยังไม่มีข้อมูลที่ลงทะเบียนได้ (schema ต้องการ data_id ที่มีไฟล์และ hash)
> ทุกเกณฑ์ในเอกสารนี้ AI เสนอ ผู้เขียนเป็นคนตัดสิน ยังไม่ได้รันเทียบกับข้อมูลใด

## คำถาม

กฎ N = bτ ฉบับที่ประชากรโต (`C_L3_GROWING_ABUNDANCE`, L1) เชื่อม **เวลาของแต่ละ phase ที่วัดจาก time-lapse** กับ **สัดส่วนเซลล์ในแต่ละ phase จาก snapshot** ของเซลล์สายเดียวกันได้หรือไม่

## วิธี (จะล็อกก่อนอนุมัติ)

1. Input จากการวัดชุดที่ 1 (time-lapse): ค่าเฉลี่ยเวลา G1, S, G2, M และรอบรวม T
2. ทำนาย: สัดส่วน φ_i = 2(2^{-a_i/T} − 2^{-a_{i+1}/T}) ด้วย a_i คืออายุที่เริ่ม phase (สูตรรอบคงที่, `layer23.phase_fraction_dividing`)
3. ความคลาดของแบบจำลอง: รอบจริงแปรผัน (cv รวมราว 0.2–0.3 ตาม Chao et al. 2019) สูตรรอบคงที่จึงคลาดราว O(cv²) ใช้ agent model ที่มี cv จากข้อมูลชุดที่ 1 ประเมิน σ_model ล่วงหน้า (ที่ cv 0.2 คลาดราว 0.008)
4. เทียบกับข้อมูลชุดที่ 2 (snapshot: flow cytometry DNA content หรือ EdU/PCNA ของ population เดียวกัน): |φ_pred − φ_obs| / σ_tot ต่อ phase
5. Negative control: ค่าแบบ steady (φ = τ_i/T) ต้องคำนวณควบคู่ ถ้าข้อมูลแยกสองแบบไม่ออก (ต่างกันน้อยกว่า 2σ_tot) ผลเป็น INCONCLUSIVE

## เกณฑ์ที่เสนอ

- PASS: z ≤ 2 ทุก phase และแยกจาก steady ได้
- FAILED: z > 3 ใน phase ใดก็ตาม
- INCONCLUSIVE: นอกเหนือจากนั้น หรือข้อมูลสองชุดไม่ได้มาจาก condition เดียวกัน

## ข้อมูลที่ต้องการ (ยังหาไม่ได้)

ต้องมีทั้งสองชุดจาก **เซลล์สายเดียวกัน condition เดียวกัน** และเป็นอิสระต่อกัน:

| ที่ตรวจแล้ว | มีอะไร | ขาดอะไร |
|---|---|---|
| Chao et al. 2019, Mol Syst Biol (PMC6423720), RPE1/U2OS/H9 | เวลา G1/S/G2/M จาก PCNA time-lapse หลายพันเซลล์ | ตัวเลขอยู่ในรูป, ไม่มี snapshot fraction |
| Drewinko et al. 1978 (lymphoma), Gray et al. 1983 | เวลา phase จาก labeled mitoses | เข้าถึงได้เฉพาะ abstract |
| Hahn, Jones & Meyer 2009 (PC12 biosensor) | ตั้งใจเทียบ live-cell กับ fixed | ดึงข้อความไม่ได้ |

ทางเลือก:
- (ก) ใช้ข้อมูล time-lapse ที่เปิดเป็นไฟล์ (เช่น supplementary ของ Chao 2019 ถ้ามี) คู่กับ flow cytometry ของ RPE1 ในงานอื่น ข้อเสีย: คนละห้องแล็บ condition อาจไม่ตรง
- (ข) หาเปเปอร์ที่วัดทั้งสองแบบในงานเดียว (เช่นงาน FUCCI ที่รายงาน flow cytometry ควบคู่) ต้องค้นต่อ
- (ค) ถามผู้เขียนว่ามีแหล่งข้อมูลที่รู้จัก

ข้อสังเกต: ไม่ใช่ UET-distinct เพราะเป็นสูตรมาตรฐานของ cell kinetics และไม่ blind ถ้าผู้ร่างเห็นตัวเลขทั้งสองชุดก่อน

## ค้นต่อ (2026-11-17, รอบ 2)

| ที่ตรวจเพิ่ม | ผล |
|---|---|
| Zerjatke et al. 2017, Cell Rep (PMC5464964), RPE-1 PCNA | ข้อความไม่มีตัวเลขเวลาของ phase หรือ snapshot fraction |
| Wheeler 2015, MBoC (PMC4710220), ergodic rate analysis | ดึงข้อความไม่ได้ |
| เอกสาร INIS-IAEA (HeLa cell kinetics) และ LBNL eScholarship | server error / timeout |

ข้อสังเกต: สูตร mitotic index = ln2 · t_M/T (อันดับแรกของสูตรนี้) เป็นสูตรในตำรา cell kinetics อยู่แล้ว การทดสอบนี้จึงเป็นการเทียบสูตรมาตรฐานกับข้อมูล
ทางที่ยังเหลือ: (1) ไฟล์ supplementary/source data ของงาน time-lapse (เช่น Chao 2019) คู่กับ flow cytometry จากงานอื่น (2) ยีสต์ budding index กับ time-lapse ในงานเดียว (3) แหล่งที่ผู้เขียนรู้จัก

## ยีสต์ (2026-11-17, รอบ 3): พบแหล่งที่น่าจะใช้ได้

**Hartwell & Unger 1977, J Cell Biol 75:422 (PMC2109951)**, ยีสต์ C276 และ 2180a โตแบบ exponential บน agar ที่ความเร็วต่าง ๆ (ใช้ cycloheximide)
- generation time ของ parent (P) และ daughter (D) วัดจากการติดตามเซลล์เดี่ยว (pedigree) เช่น ที่ T_d = 167 นาที: P = 132 ± 26, D = 203 ± 38
- snapshot: สัดส่วนของเซลล์ไม่มีตาที่เป็น daughter (ย้อม bud scar) เช่น T_d 165: สังเกต 78.8 ± 2.0% เทียบที่ผู้แต่งคำนวณ 82%; T_d 220: 86.4 ± 1.7% เทียบ 79%
- ข้อควรระวัง: ช่วง budded B ใน Fig. 5 อาจคำนวณจาก budded fraction (Eq. 3) ไม่ได้วัดตรง ต้องอ่านจากต้นฉบับก่อนใช้ ข้อความที่ดึงจาก PDF สแกนปนกันระหว่างตาราง
- สูตรที่จะใช้: ยีสต์แบ่งตัวไม่เท่ากัน สูตรเซลล์แบ่งเท่ากันใช้ไม่ได้ ต้อง derive กฎ abundance แบบ asymmetric (parent/daughter) ก่อน ข้อดีคือสัดส่วนเซลล์ที่มีตา = 2^{B/T_d} − 1 ไม่ขึ้นกับความไม่สมมาตร
- ถัดไป: อ่านตารางจากต้นฉบับ (ต้องดาวน์โหลด PDF ผู้เขียนต้องอนุญาต), derive สูตร asymmetric + physics test, แล้วร่าง Test Card

## ร่าง Test Card แล้ว (2026-11-17)

อ่านต้นฉบับแล้ว: ช่วง budded B ของ Fig. 5 คำนวณจาก budded fraction (Eq. 3) จึงไม่อิสระ เปลี่ยนตัวตัดสินเป็น **doubling time ของประชากร** ที่นับจาก field เดียวกัน เทียบกับค่าที่คำนวณจาก P และ D ของเซลล์เดี่ยว (2^{-P/T} + 2^{-D/T} = 1)
ไฟล์: `docs/standard/tests/T017.json` (DRAFT), `core/03_lanes/persistence/t017_yeast_asymmetric.py`, ข้อมูล `docs/data/external/biology/yeast_cell_cycle/hartwell_unger1977_cycle_times.csv`
