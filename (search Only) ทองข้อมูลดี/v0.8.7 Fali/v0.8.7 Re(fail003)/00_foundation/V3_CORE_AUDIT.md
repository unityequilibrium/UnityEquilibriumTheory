# 🛑 Research V3 Core Audit
**User Mandate:** "Stop messing with the broken V2 legacy. Understand V3 first. Don't fix the old; build the new."

## 1. The Core Conflict
I was trying to "respect legacy" by fixing old scripts. The user views those old scripts as "trash that caused the problem."
**New Directive:** Focus 100% on `research_v3`.

## 2. V3 Architecture Check
I need to verify:
- `research_v3/00_foundation/`: The new Laws of Physics (UET).
- `research_v3/04_analysis/`: The new Analysis Engine.
- `research_v3/01_data/`: Where the data *should* be.

## 3. Action Plan
1.  **Read V3 Foundation:** Re-read `UET_VARIABLES.md` and `PHYSICS_FIRST_MAP.md` to ensure I'm using the *new* definitions.
2.  **Audit V3 Scripts:** Check `research_v3/04_analysis/` to see what is already built.
3.  **Migrate Data (IF NEEDED):** If `research_v3` needs data, I will *copy* the valid CSVs from legacy to `research_v3/01_data`, standardizing them, and ignoring the old mess.
4.  **Run V3 Analysis:** Run the analysis using `research_v3` scripts only.
