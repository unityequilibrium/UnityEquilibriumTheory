# 🛡️ SPEC: Atomic Design Rule Check (DRC-A) Suite

To ensure your designs are **Physically Viable** at the 10.8 picometer level, your CAD software (KLayout/Virtuoso) must use these **DRC-A Rules**. 

Without these, you might draw a circuit that the SAW waves cannot "lock" into place.

---

## 📏 1. Geometric Constraints

| Rule ID | Parameter | Value | Why? |
| :--- | :--- | :--- | :--- |
| **DRC_A1** | Min Wire Width | **0.2 nm** | The physical size of 1 Silicon atom. |
| **DRC_A2** | Min Wire Spacing | **2.0 nm** | To prevent "Acoustic Tunneling" between parallel wires. |
| **DRC_A3** | Max Wire Length | **10,000 nm** | Beyond 10um, thermal drift requires a "Sync-Node". |

---

## 📡 2. SAW Physics Rules (Interference)

- **Rule DRC_B1 (Phase Guard)**: No two "Active Nozzle Nodes" can be closer than **$\lambda/4$ (~195nm)** unless they are phase-locked by the same master clock. 
  - *Conflict*: If you place two independent oscillators too close, their standing waves will "wash out" the atoms.
- **Rule DRC_B2 (Lattice Alignment)**: All primary logic gates **MUST** align with the $X$-axis of the LiNbO3 substrate (± 0.5°). 
  - *Conflict*: 45-degree domestic curves will have 30% lower trapping efficiency.

---

## 🎨 3. Layer Mapping (The UET Standard)

When designing in your old program, use these layers:

| Layer # | Name | Purpose |
| :--- | :--- | :--- |
| **Layer 1** | ATOM_CORE | The actual atomic structure (MoS2/Graphene). |
| **Layer 2** | hBN_ISO | The 7nm Hexagonal Boron Nitride insulator. |
| **Layer 64** | SILENT_ZONE | Area where Metamaterial Isolation is active. |
| **Layer 128** | PHASE_REF | Calibration markings for the SAW Nozzle alignment. |

---

## 🚀 How to use this in KLayout/Virtuoso
1.  **Draw** your design using standard rectangles and paths on the layers above.
2.  **Run** the **UET-Atomic Compiler** (which we've already built).
3.  The Compiler will flag any **DRC-A** violations (e.g., *"Error: Wire on Layer 1 is 0.05nm wide - Physics Limit is 0.2nm"*).

---
*UET Research Topic 0.34 | Software & Verification Hardening*
