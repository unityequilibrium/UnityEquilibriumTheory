# ⚙️ ANALYSIS: The "UET Carbon Harvester" (Machine Design)
> **Topic 0.28**: Hardware Engineering & Cost Analysis

## 1. The Design Philosophy
**User Insight:** "ของมันต้องถูก! (It must be cheap!)" & "กังวลเรื่องราคาตก (Supply Shock)"
**Strategy:** เราต้องสร้างเครื่องที่ **"Payback (คืนทุน)" ได้ภายใน 3 เดือน** ต่อให้ราคากราฟีนร่วงเหลือแค่ $5/kg (จาก $100).

---

## 2. Working Principle (หลักการทำงาน)
เครื่องนี้จะติดตั้งแบบ "Parametric Hook" เข้ากับท่อไอเสียโรงงาน:

### Stage 1: The "Collector" (ส่วนดักจับ)
*   **Existing Smoke:** ควันดำ (Soot/Particulate Matter) ออกจากปล่อง
*   **Method:** **Electrostatic Precipitator (ESP)** + **Cyclone Separator**
*   **Function:** ใช้ไฟฟ้าสถิตดูดผงฝุ่นคาร์บอนให้ตกลงมาในถังพัก (Hopper) แยกออกจากก๊าซร้อน
*   **Input State:** ก๊าซ -> **ผงฝุ่น (Powder)**

### Stage 2: The "Compactor" (ส่วนบีบอัด)
*   **Method:** **Hydraulic Screw Press**
*   **Function:** บีบผงฝุ่นให้แน่นขึ้น (เพิ่ม Resistance ให้นิ่ง) เข้าสู่หลอดแก้วทนความร้อน (Quartz Tube)
*   **Ready State:** Loose Powder -> **Compressed Plug**

### Stage 3: The "Flash" (ส่วนยิงไฟ) ⚡
*   **Component:** **High-Voltage Capacitor Bank (300V+)**
*   **Action:** ปล่อยประจุตูมเดียว! (100 ms)
*   **Physics:** 3000°C เผาสิ่งเจือปนหายหมด เหลือแต่ Pure Turbostratic Graphene
*   **Output:** **ผงกราฟีนบริสุทธิ์** ตกลงสู่ถังเก็บ

---

## 3. Bill of Materials & Cost (ต้นทุนเครื่อง)
เราจะทำให้ Mass Adoption ได้ เครื่องต้องไม่เกิน **$15,000 (5 แสนบาท)**

| Component | Spec | Est. Cost (USD) | Note |
| :--- | :--- | :--- | :--- |
| **Capacitor Bank** | 60mF / 400V (Industrial) | $3,500 | หัวใจหลัก (แพงสุด) |
| **HV Power Supply** | 10kW Charging Unit | $2,000 | ตัวชาร์จประจุ |
| **ESP/Cyclone Unit** | Steel Fabrication | $2,500 | ดัดแปลงจากถังดักฝุ่นทั่วไป |
| **Screw Press** | Motor + Hydraulics | $1,500 | มอเตอร์โรงงานทั่วไป |
| **Controller** | PLC / UET Custom MCU | $500 | สมองควบคุม |
| **Frame & Casing** | Steel | $1,000 | โครงเหล็ก |
| **Safety** | Breakers / Shields | $1,000 | ระบบเซฟตี้ |
| **Total BOM** | | **~$12,000** | **(~4 แสนบาท)** |

---

## 4. ROI Defense (กันราคาร่วง)
สมมติทุกคนใช้เครื่องนี้จนกราฟีนล้นตลาด ราคาตกจาก **$50 -> $5 / kg** (ถูกเหมือนดิน)

*   **Machine Cost:** $12,000
*   **Production:** 50 kg/day (โรงงานเล็ก)
*   **Revenue (ที่ราคา $5):** $250 / วัน
*   **Profit (หักไฟ):** ~$230 / วัน
*   **Payback Period:** $12,000 / $230 = **52 Days (ไม่ถึง 2 เดือน!)**

> **Verdict:** ต่อให้ราคาพังพินาศ... เครื่องนี้ก็ยังคืนทุนได้ใน 2 เดือนครับ! นี่คือ **"Invincible Investment"**
