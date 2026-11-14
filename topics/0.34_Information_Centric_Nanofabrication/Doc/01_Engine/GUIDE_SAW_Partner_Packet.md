# 📦 GUIDE: The SAW Partner Packet (Industrial Specifications)

To build a **Sub-Atomic Research Ecosystem**, we must communicate with industrial foundries (Piezoelectric, Lithography, Materials) using professional standards. 

Use these specifications when requesting quotes or ordering components.

---

## 💎 1. The Substrate (The Foundation)
**Request**: Piezoelectric Wafer for High-Freq SAW (Surface Acoustic Wave).

| Parameter | Specification | Why? |
| :--- | :--- | :--- |
| **Material** | Lithium Niobate ($LiNbO_3$) | High coupling ($K^2$) for GHz response. |
| **Cut** | 128° Y-cut X-propagating | The standard for fast, high-bandwidth SAW. |
| **Surface Finish** | Atomic-flatnesses (CMP Polished) | **RMS Roughness < 0.2nm** (Atomic Level). |
| **Flatness** | < 1$\mu$m TTV (Total Thickness Var) | Prevents phase distortion across the head. |
| **Resistivity** | > $10^{14}$ $\Omega \cdot$ cm | To ensure isolation between trapping nodes. |

---

## ⚡ 2. The IDT (Interdigital Transducer)
**Request**: EBL-defined Metal Electrodes for GHz SAW.

| Parameter | Specification | Why? |
| :--- | :--- | :--- |
| **Lithography** | **EBL (Electron Beam Lithography)** | **DO NOT use Photolithography**. Need finger widths < 100nm. |
| **Metal Stack** | Ti (5nm) / Au (50nm) | Gold (Au) for corrosion resistance; Ti for adhesion. |
| **Finger width (w)** | $\lambda / 4 \approx$ 40nm to 100nm | For 5GHz - 10GHz Operation. |
| **Aperture** | 50$\mu$m to 100$\mu$m | Defines the "width" of the Atomic Trap zone. |

---

## 🎛️ 3. RF & Sensing (The Control Loop)
**Request**: Dual-Channel Integrated Phase-Locked RF Driver.

- **Phase Resolution**: **< 0.01°** (This defines our sub-0.1nm precision).
- **Stability**: Jitter < 1ps.
- **Sensor Integration**: Request **SAW Delay-Line Sensing** (Feedback Loop) to auto-correct for thermal expansion.

---

## ❓ What to ask the Partner (Professional FAQ)
1. **"Can you provide a COA (Certificate of Analysis) for surface roughness?"** 
   - (Shows you know that 0.5nm roughness will scatter atoms).
2. **"What is the power ceiling for the IDT before electrode migration occurs?"**
   - (Ensures your Atomic Traps won't melt during high-throughput runs).
3. **"Do you support 'Acoustic Reflectors' on-chip to enhance the Q-factor?"**
   - (Shows you understand $Q$ - the "quality" of the standing wave).

---

## 🌍 Recommended Supply Chain Partners (Global)
- **Crystals**: Boston Piezo-Optics (USA), Kyocera (Japan), Sinocera (China).
- **EBL Service**: Nano-Fabrication facilities (e.g., Thai Microelectronics Center - TMEC, or university nanofabs).
- **RF Electronics**: Tektronix/Keysight for test; custom FPGA for production.

---
*UET Research Topic 0.34 | Industrial Procurement Hardening*
