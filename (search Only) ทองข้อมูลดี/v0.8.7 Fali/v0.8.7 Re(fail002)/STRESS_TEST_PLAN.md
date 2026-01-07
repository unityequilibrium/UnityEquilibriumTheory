# 🧪 UET "Torture Test" Plan (Pre-Release Stress Testing)

**Objective:** Break the theory. Before releasing to the world, we must attack our own creation with the most extreme, brutal, and challenging physical scenarios possible. If UET survives, it's real.

## 1. The "Big Bang" Singularities (Extreme Density)
*   **Concept:** Can UET handle infinite density without crashing?
*   **Test:** Initialize a simulation with $\phi = 1,000,000$ (normal is $\approx 1$) at a single point.
*   **Failure Condition:** Numerical Overflow (NaN), Program Crash, or weird non-physical spikes.
*   **Success Condition:** The energy dissipates smoothly or forms a stable soliton/black hole.

## 2. The "Chaos" Simulation (Long-Term Stability)
*   **Concept:** Does the universe decay over billions of years?
*   **Tests:** Run a simulation for `max_steps = 10,000,000` (or as long as we can wait).
*   **Failure Condition:** Energy drift (gradually gaining/losing energy for no reason).
*   **Success Condition:** Perfect conservation or monotonic entropy increase (Arrow of Time).

## 3. The "Anti-Matter" Collision (Annihilation)
*   **Concept:** Explicitly collide a "Positive Mass" soliton with a "Negative Mass" soliton.
*   **Failure Condition:** They pass through each other like ghosts or create infinite energy.
*   **Success Condition:** They annihilate and release "radiation" (waves) into the vacuum field.

## 4. The "Light-Speed" Limit (Relativistic Checks)
*   **Concept:** Move an object faster than the grid can handle.
*   **Test:** Inject a soliton with initial velocity $v > c$ (in simulation units).
*   **Failure Condition:** It actually moves faster than light (causality violation).
*   **Success Condition:** The structure distorts ("Lorentz Contraction") but refuses to exceed the speed limit defined by the grid diffusion.

## 5. Statistical Aggression (The "Trillion" Particle Test)
*   **Concept:** Statistical Mechanics validation.
*   **Test:** Not literally a trillion, but a very dense gas of particles.
*   **Failure Condition:** The Ideal Gas Law ($PV=nRT$) fails to emerge from the interactions.
*   **Success Condition:** We recover standard thermodynamics from pure field dynamics.

---

**Action Plan:**
1. Create `research/03-stress-tests/` directory.
2. Implement script `torture_bang.py` (Big Bang Test).
3. Implement script `torture_scramble.py` (Entropy/Chaos Test).
4. Run these overnight and log every single unexpected anomaly.
