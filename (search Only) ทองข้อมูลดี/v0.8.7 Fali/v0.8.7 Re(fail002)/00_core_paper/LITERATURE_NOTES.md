# Literature Notes: ทำความเข้าใจ Physics Foundations

**สร้าง:** 2025-12-30
**วัตถุประสงค์:** สรุปความรู้จาก key papers เพื่อเข้าใจว่า UET ทำอะไรได้/ไม่ได้

---

## 📚 1. Jacobson 1995 — Thermodynamics of Spacetime

### Key Insight:
> **Einstein equations = equation of state for spacetime**

### วิธีการ:
1. ใช้ **Clausius relation**: δQ = TdS
2. Apply locally กับ **Rindler causal horizons**
3. δQ = energy flux across horizon
4. T = **Unruh temperature** (accelerated observer)
5. S ∝ **horizon area** (Bekenstein-Hawking)

### Result:
$$\delta Q = T dS \implies G_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}$$

### ความหมาย:
- Gravity = thermodynamic, not fundamental force
- Spacetime อาจเป็น **emergent phenomenon**
- **ต้องมี local equilibrium** ถึงจะใช้ได้

### Relevance to UET:
- ✅ UET ใช้ thermodynamics เหมือนกัน
- ❌ แต่ UET ไม่มี causal horizon, Unruh temperature
- ❌ Euclidean UET ไม่มี causal structure

---

## 📚 2. Verlinde 2010 — Entropic Gravity

### Key Insight:
> **Gravity = entropic force from information on holographic screens**

### วิธีการ:
1. Information encoded on **holographic screen** (boundary)
2. Mass changes information distribution → **entropy change**
3. System wants to **maximize entropy** → creates force

### Result:
- Newton's inverse-square law emerges naturally!
- Einstein's equations follow from same principles

### Formula:
$$F = T \frac{\Delta S}{\Delta x} \implies F = \frac{GMm}{r^2}$$

### Criticisms:
- ⚠️ Holographic screens อาจไม่เป็น thermodynamic ไกลจาก horizons
- ⚠️ Some galaxy rotation predictions fail

### Relevance to UET:
- ✅ Both use thermodynamics for gravity
- ❌ Verlinde needs holographic principle (UET doesn't have)
- ❌ Verlinde is about gravity only, not gauge forces

---

## 📚 3. Why Gauge Symmetry ≠ Gradient Flow

### Key Point:
> **Gauge symmetry requires quantum entanglement/topology, not thermodynamics**

### Comparison:

| Gauge Symmetry | Gradient Flow |
|----------------|---------------|
| Invariance of equations | Dissipative evolution |
| Creates force particles | Relaxes to equilibrium |
| From quantum entanglement | From entropy increase |
| Structure of interactions | Kinetics of relaxation |

### Emergent Gauge (real physics):
- **String-net condensation** (Xiao-Gang Wen)
- **Topological order** in quantum spin liquids
- Requires **long-range entanglement**

### Gradient Flow (what it does):
- Relaxes system to minimum energy
- **Loses information** about initial state
- Second law of thermodynamics

### Conclusion:
> **Cannot derive U(1), SU(2), SU(3) from thermodynamics!**
> 
> Gauge symmetries are about **structure**, gradient flow is about **kinetics**

---

## 🎯 Summary for UET

### What Thermodynamics CAN Do:
- ✅ Derive gravity (Jacobson, Verlinde)
- ✅ Explain entropy-driven forces
- ✅ Pattern formation (Cahn-Hilliard)
- ✅ Phase transitions

### What Thermodynamics CANNOT Do:
- ❌ Derive gauge symmetries (U(1), SU(2), SU(3))
- ❌ Create force-carrying particles
- ❌ Reproduce Standard Model

### Honest Position for UET:
```
UET = Framework for:
  ✅ Gradient flow dynamics
  ✅ Phase separation patterns
  ✅ Lyapunov stability
  ✅ Thermodynamic-like gravity analog

UET ≠ Theory of:
  ❌ Gauge forces
  ❌ Particle physics
  ❌ Standard Model
```

---

## 📖 References

1. Jacobson, T. (1995). Thermodynamics of Spacetime: The Einstein Equation of State. [gr-qc/9504004](https://arxiv.org/abs/gr-qc/9504004)

2. Verlinde, E. (2011). On the Origin of Gravity and the Laws of Newton. JHEP. [arXiv:1001.0785](https://arxiv.org/abs/1001.0785)

3. Bass, S. (2022). Emergent gauge symmetry and the Standard Model. Royal Society.

4. Wen, X.-G. (2017). Colloquium: Zoo of quantum-topological phases of matter. RMP.

---

**Last Updated:** 2025-12-30
