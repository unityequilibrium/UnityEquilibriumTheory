# UET v0.8.7 — สิ่งที่ต้องรู้

**One-page summary สำหรับผู้ที่เพิ่งมาอ่าน**

---

## 🎯 UET คืออะไร?

**Unity Equilibrium Theory** คือ framework ทางคณิตศาสตร์ที่ศึกษาการ relaxation ของระบบเข้าหา equilibrium ผ่าน gradient flow:

$$\partial_t \phi = \nabla^2 \frac{\delta \Omega}{\delta \phi}$$

---

## ✅ สิ่งที่พิสูจน์ได้แล้ว (Math)

| หัวข้อ | Status | Proof |
|--------|--------|-------|
| Lyapunov stability | ✅ | dΩ/dt ≤ 0 proven |
| Energy conservation | ✅ | Numerical 39/39 |
| Coercivity bounds | ✅ | Sobolev estimates |

---

## ⚠️ สิ่งที่ยังไม่พิสูจน์ (Physics)

| Claim | Status | Note |
|-------|--------|------|
| Gauge symmetry derivation | ❌ | Demonstrate only |
| Lorentz invariance | ❌ | Euclidean analog |
| Fine structure constant | ❌ | 25% error |
| Fermion statistics | ❌ | Pauli-like only |

---

## 📋 เอกสาร

| ไฟล์ | คำอธิบาย |
|------|----------|
| [PAPER_FULL.md](PAPER_FULL.md) | Full paper |
| [INTUITIVE_EXPLANATION.md](INTUITIVE_EXPLANATION.md) | อธิบายแบบ common sense |
| [CHALLENGE.md](CHALLENGE.md) | เชิญชวนมาพิสูจน์ว่าผิด |
| [LIMITATIONS.md](LIMITATIONS.md) | ข้อจำกัดที่ยอมรับ |
| [RESPONSE_TO_CRITICISM.md](RESPONSE_TO_CRITICISM.md) | ตอบข้อวิพากษ์ |
| [RESEARCH_SUMMARY.md](RESEARCH_SUMMARY.md) | สรุปการวิจัย |

---

## 🔗 Links

- **GitHub:** https://github.com/unityequilibrium/Equation-UET-v0.8.7
- **Zenodo:** Connected (DOI pending)
- **arXiv:** Account created (endorsement pending)

---

**Version 0.8.7 | 2025-12-30**
