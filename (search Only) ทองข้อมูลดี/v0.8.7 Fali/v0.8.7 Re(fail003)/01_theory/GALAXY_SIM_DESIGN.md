# Galaxy Simulation Design Doc (UET Layer)

## 1. Objective
Prove that the "Missing Mass" (Dark Matter) in galaxies can be explained by **Information Closure (I-Field)** without inventing new particles.

## 2. The Data Problem
- **User Requirement:** "Use Real Data", "Don't download new big files".
- **Status:** No large datasets found in `research/`.
- **Solution:** Hardcode representative data points from the **SPARC database** (standard galaxy rotation data).
    - We don't need 1TB of raw images.
    - We just need `(radius, velocity)` curves for 3-4 typical galaxies.
    - **Target:** Galaxy NGC 6503 (Textbook example).

## 3. The Physics Logic
1.  **Newton:** $v_{newton} = \sqrt{GM/r}$ (Falls off as $1/\sqrt{r}$)
2.  **Reality:** $v_{obs}$ stays flat (doesn't fall).
3.  **Standard Fix:** Add invisible mass ($M_{dark}$).
4.  **UET Fix:** Add **Information Frixtion (I)**.
    - As you go further out, Space is "less observed" / "more closed" (I increases).
    - High I = High resistance to change = "Effective Mass" effect.

## 4. Implementation Plan (`galaxy_sim.py`)
1.  **Load Data:** Hardcoded arrays for NGC 6503 (Radius, V_gas, V_disk, V_obs).
2.  **Calculate Newton:** Compute what velocity *should* be ($V_{baryon}$).
3.  **Apply UET:**
    - Define I-field: $I(r) \propto r^\alpha$ (Closure increases with distance).
    - Modify Potential: $\Phi_{eff} = \Phi_{newton} \times (1 + k \cdot I(r))$.
    - Calculate $V_{uet}$.
4.  **Compare:** Does $V_{uet}$ match $V_{obs}$?

## 5. Success Criteria
- If $V_{uet}$ overlays $V_{obs}$ closely...
- PROOF: "Information Closure" ($I$) is mathematically equivalent to "Dark Matter Halo".
