# Section 3 Dependency Map

Status: `PASS`  
Section Blueprint: `section-03-v1`  
Profile: `THREE_BOOK_SECTION`  

---

## 1. Cross-Section Dependency Matrix (การเชื่อมโยงข้ามเซกชัน)

| Dependency ID | From Section | To Section | Dependency Concept | Handoff Description | Status |
| :---: | :---: | :---: | :--- | :--- | :--- |
| `D-SEC-01` | **Section 0** (`03_imprints_capital`) | **Section 3** (All Volumes) | **Physical Landscape & Pre-Existing Consent** | เล่ม 0.3 ส่งมอบรากฐานทางกายภาพ (แม่น้ำ 5 สาย, ภาษียุ้งฉางข้าว, ข้อจำกัดแคลอรี) ให้ Section 3 นำไปเป็นฐานอธิบาย 'ความยินยอมในจารีตธรรมชาติ' | `PASS` |
| `D-SEC-02` | **Section 1** (Biology & Psychology) | **Section 3** (Vol 1 & 2) | **Neurobiological Compliance Machinery** | Section 1 ส่งมอบกลไกสมอง (Amygdala Fear, Brain Economy, Social Pain dACC/Insula) ให้ Section 3 ใช้ผ่ากลไกการสยบยอมของปัจเจก | `PASS` |
| `D-SEC-03` | **Section 2** (Society & Institutions) | **Section 3** (Vol 2 & 3) | **Social Coordination & Institutional Software** | Section 2 ส่งมอบโครงสร้างสถาบันกลุ่ม กฎหมาย และตลาด ให้ Section 3 ใช้เป็นผืนผ้าใบในการวิเคราะห์การสวมทับวาทกรรมและการปลดแอก | `PASS` |

---

## 2. Cross-Volume Dependency Matrix (การเชื่อมโยงระหว่าง 3 เล่มใน Section 3)

| Dependency ID | From | To | Dependency & Shared Concept | Handoff Description | Current Status | Controller |
| :---: | :---: | :---: | :--- | :--- | :--- | :---: | :---: |
| `D03-01` | Volume 1 | Volume 2 | **Discourse & 4-Power Model $\rightarrow$ Hardened Tradition** | เล่ม 1 ส่งมอบมโนทัศน์เรื่อง *วาทกรรม, การเลือกพูด (Selective Framing)* และ *ทฤษฎีอำนาจ 4 มิติ* ให้เล่ม 2 นำไปใช้ผ่ากลไกการตกผลึกเป็น *จารีต (Tradition)* | `PASS` | `S05` |
| `D03-02` | Volume 2 | Volume 3 | **Authoritarian Anatomy & Pluralistic Ignorance $\rightarrow$ New Tradition Design** | เล่ม 2 ส่งมอบผลการวิเคราะห์ปัญหากายวิภาคอำนาจนิยม สภาวะสมยอมเทียม (*Pluralistic Ignorance*) และจารีตที่กดทับ ให้เล่ม 3 นำไปสลายอคติและสถาปนา *จารีตใหม่ที่ดี* | `PASS` | `S05` |
| `D03-03` | Volume 1 | Volume 3 | **Selective Framing Mechanism $\rightarrow$ Ethical Selective Framing** | เล่ม 1 ส่งมอบกลไกการเลือกพูด (Selective Framing) ให้เล่ม 3 นำไปใช้เชิงจริยธรรม (*Ethical Selective Framing*) สกัดมรดกดีเดิม (พุทธ/เล่าจื้อ) | `PASS` | `S05` |
| `D03-04` | Section | Volumes 1-3 | **Shared Terms & Controlled Definitions** | ศัพท์สากลประจำเซกชัน (*Discourse, Selective Framing, 4-Power Model, Tradition, Pluralistic Ignorance, Moral-Legal Tech*) ถูกควบคุมนิยามตรงกันที่ `SHARED_TERMS.md` | `PASS` | `SHARED_TERMS.md` |
| `D03-05` | Volume 3 | Section | **Section Synthesis & Bounded Conclusion** | เล่ม 3 สรุปบทสังเคราะห์ของ Section 3 ทั้งหมด โดยแยกแยะชัดเจนระหว่าง *สิ่งที่พิสูจน์แล้ว*, *ข้อเสนอเชิงโครงสร้าง*, และ *ขอบเขตข้อจำกัด* | `PASS` | `S07` |

---

## 3. Handoff Safeguards & Reopen Rules

1. **Physical Grounding Guarantee:** Section 3 จะไม่อธิบายวาทกรรมว่าเกิดขึ้นลอยๆ ในอากาศ แต่ต้องเชื่อมโยงกลับไปยังรากฐานกายภาพและสิ่งแวดล้อมที่ Section 0 เล่ม 0.3 วางรากฐานไว้เสมอ
2. **Prerequisite Guarantee:** เล่ม 2 จะไม่อธิบายจารีตลอยๆ โดยไม่เชื่อมกลับมายังกรอบวาทกรรมและอำนาจ 4 มิติที่เล่ม 1 สร้างไว้
3. **Solution Alignment:** เล่ม 3 จะไม่ออกแบบทางออกเชิงจริยธรรมโดยไม่ตอบโจทย์ปัญหากายวิภาคอำนาจนิยมและกลไกสมองที่เล่ม 2 วิเคราะห์ไว้
4. **Reopen Rule:** หากเล่มใดเปลี่ยนแปลงนิยามศัพท์ร่วม หรือเปลี่ยนบทบาทการส่งต่อ (Handoff) ให้ทำการ Reopen เกต S04-S05 ทันที
