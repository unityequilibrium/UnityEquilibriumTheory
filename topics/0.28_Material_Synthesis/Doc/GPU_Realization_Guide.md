# 🏗️ GPU Realization Guide: The UET Carbon Harvester (v1.0)

This guide provides a "buildable" blueprint for the **Graphene Production Unit (GPU)** using Flash Joule Heating (FJH). This machine is designed for localization in Thailand using industrial-grade components available on the open market.

---

## ⚡ 1. Critical Safety Protocols (เตือนอันตราย!)

> [!CAUTION]
> **HIGH VOLTAGE (300V-400V):** The capacitor bank stores enough energy to be LETHAL.
> 1. Use a **Bleeder Resistor** (10kΩ/5W) across the capacitor bank to discharge after use.
> 2. Implement a **Physical Safety Interlock** (limit switch) so the flash cannot trigger if the shield is open.
> 3. Wear **UV-Rated Safety Goggles** - The flash at 3000°C emits intense UV radiation.

---

## ⚙️ 2. Mechanical Assembly (โครงสร้างเครื่อง)

### 2.1 The Reaction Chamber (หลอดเผา)
- **Component:** Fused Quartz Tube (หลอดแก้วควอตซ์)
- **Spec:** OD 15mm, ID 10mm, Length 100mm.
- **Why:** Must withstand 1600°C continuous and thermal shock from the 3000°C flash.
- **Sourcing:** "Fused Quartz Tube" on Shopee/Lazada or local glass blowing shops.

### 2.2 Electrode & Compression (ลูกสูบและหัวจ่ายไฟ)
- **Material:** Pure Copper or High-Density Graphite rods (10mm diameter).
- **Drive:** Pneumatic Cylinder (10-20 Bar) or a fine-thread manual screw press.
- **Goal:** Compress carbon powder to a resistance of **1-10 Ohms**.

---

## 🔌 3. Electrical System (ระบบไฟฟ้า)

### 3.1 Capacitor Bank (ตัวเก็บประจุ)
To achieve 3000°C, you need approx. **600 Joules per gram** of carbon.
- **Recipe:** 4 units of **15,000μF / 450V** Electrolytic Capacitors in parallel.
- **Total Capacity:** 60,000μF (60mF).
- **Potential Energy:** $E = 0.5 \times 0.06 \times 400^2 = 4,800$ Joules (Enough for 5-8g of graphene per flash).

### 3.2 Pulse Control (วงจรจุดชนวน)
- **Switch:** High-Current SCR (Silicon Controlled Rectifier) or a Heavy-Duty Magnetic Contactor (rated for 500A peak).
- **Trigger:** Time-delay relay set to **100ms - 500ms** discharge time.

---

## 🌍 4. Raw Materials & "Recipes" (วัตถุดิบและสูตร)

| Source | Preparation | Flash Recipe (Voltage/Pressure) |
| :--- | :--- | :--- |
| **Industrial Soot (ควันดำ)** | Decant with Ethanol, Dry | 350V / High Pressure (20 Bar) |
| **Rice Husk Biochar (แกลบดำ)** | Grind to < 100 mesh | 400V / Med Pressure (10 Bar) |
| **Plastic Waste (Mixed)** | Pre-pyrolysis to 400°C | 380V / High Pressure (15 Bar) |

---

## 🛠️ 5. Step-by-Step Production (ขั้นตอนการทำ)

1.  **Loading:** Fill the Quartz tube with 2-5g of processed carbon powder.
2.  **Compression:** Engage the press until the multimeter shows a resistance of ~5Ω across the electrodes.
3.  **Charging:** Power up the High-Voltage supply until the bank reaches the target voltage.
4.  **FLASH:** Trigger the pulse. You will see a bright white flash and the powder will "pop" slightly.
5.  **Cooling:** Wait 30 seconds for the tube to cool.
6.  **Harvest:** Extract the **Turbostratic Graphene** powder (High-purity black flakes).

---

## 📊 6. Bill of Materials (BOM) Logic

| Item | Local Source (TH) | Est. Price (THB) |
| :--- | :--- | :--- |
| **Fused Quartz Tube** | Shopee/Lazada (Laboratory Glassware) | 800 - 1,200 |
| **HV Capacitors (4Units)** | Industrial Electronics Shops (Ban Mo / Shopee) | 4,000 - 6,000 |
| **Copper Rods (Electrodes)** | Hardware Store / Scrap Yard | 500 - 1,000 |
| **Pneumatic Cylinder** | Industrial Surplus (ตลาดพูนทรัพย์ / Shopee) | 1,500 - 2,500 |
| **Safety Shield (Polycarbonate)** | HomePro / Local Plastic Shop | 500 |
| **Total Build Cost** | | **~10,000 - 15,000 THB** |

---
*UET Materials Realization Unit - Technical Guide v1.0*
