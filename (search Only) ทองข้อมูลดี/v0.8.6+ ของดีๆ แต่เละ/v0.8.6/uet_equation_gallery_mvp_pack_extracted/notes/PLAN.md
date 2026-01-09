# PLAN (MVP-first)

## Goal-1 (your request)
“Not just a museum: a participatory museum.”
- Equations are the gallery items.
- People can type numbers and run them.
- Every run is backed up clearly (Ledger).

## Minimal architecture (Runner Pattern)

UI (gallery_mvp.html)
  └── Compute Panel (ui_compute.js)
        ├── Runner (local_runner.js now; api_runner.js later)
        └── Ledger (ledger.js)

## Run flow (tiny diagram)
[Click equation card] → [Modal + Compute Panel]
     → [Run] → [LocalRunner] → [Outputs]
     → [Auto-save RunRecord] → [Ledger localStorage]
     → [Export/Import JSON] (Backup)

## “Swap to Docker later” plan
Replace LocalRunner with ApiRunner by:
1) set equationDef.runner.kind = "api"
2) provide endpoint
3) your container runs harness and returns {result}

No UI rewrite needed.

## Important constraints
- MVP uses *safe* pure JS functions (no eval).
- 0D demos only (no spatial gradients), by design.
- Agent can later map full UET equations (Ω-functional etc.) into the same EquationDef schema.

## Suggested next step after MVP works
- Add a 1D/2D discretized Ω estimator (small grid) (optional)
- Add “Run history view” page
- Add API runner that calls your docker harness
