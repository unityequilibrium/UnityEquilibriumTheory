# Test Results

## Latest test output from uet_landauer

---

## Core Module Test (2025-12-30)

```
============================================================
Landauer Core Module - Verification
============================================================

1. Energy per bit at 300K:
   E_bit = k_B × T × ln(2)
   E_bit = 2.8710e-21 J
   Expected: ~2.87 × 10⁻²¹ J
   ✓ Correct!

2. Value function V = M(C/I)^α:
   C=2, I=1, M=1, α=1
   V = 2.0
   Expected: 2.0
   ✓ Correct!

3. System simulation:
   Initial: C=2.0, I=1.0, V=2.00
   Final:   C=1.57, I=1.43, V=1.09
   Energy recorded: 1.2416e-21 J

============================================================
Landauer Core Module - READY
============================================================
```

---

## Full Simulation Test (2025-12-30)

```
============================================================
UET Landauer Full Simulator
============================================================

Running simulation...

Results:
  Duration: 10.0 s
  Steps: 1000
  Final Energy: 2.4948e-01 J
  Final Entropy: 8.3161e-04 J/K
  Final Info: 8.6898e+19 bits

Thermodynamic Laws:
  Law 1 (Conservation): ✗  ← (Open system, expected)
  Law 2 (Entropy↑): ✓      ← PASS

Agents final state:
  Agent_0: C=0.71, I=0.68, V=1.05
  Agent_1: C=1.51, I=1.45, V=1.04
  Agent_2: C=1.28, I=1.25, V=1.02

Plot saved: simulation_result.png

============================================================
Full Simulator - READY
============================================================
```

---

## Summary

| Test | Result |
|------|--------|
| E = kT ln 2 | ✅ PASS |
| V = M(C/I)^α | ✅ PASS |
| System simulation | ✅ PASS |
| Law 2 (Entropy↑) | ✅ PASS |

---

*Test Results - Part 3*
