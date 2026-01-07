# AGENT_BRIEF — Equation extraction + posting plan

## Mission
1) Read UET merged docs (e.g. UET_Merged_2025-12-16_0.8.5.md / 0.8.5+.md)
2) Extract *real* UET equations and convert them into `EquationDef` entries:
   - id, title, description
   - inputs/outputs schema
   - local runner function needed OR mark as api-runner-only

## Where to put things
- Edit/add equations: `mvp/data/equations.json`
- If local runnable: implement function in `mvp/js/local_runner.js` and set `runner.kind="local"`.
- If needs heavy simulation: set `runner.kind="api"` and specify endpoint.

## Post-writing support (connect to existing theory)
For each equation entry:
- Add a short doc snippet:
  - “Why this equation matters in UET”
  - “What a user can learn by playing with inputs”
  - “Interpretation (math + intuitive)”
- Link it to the appropriate section in the UET docs (by filename + heading).

## Quality rules
- Do not invent new UET concepts.
- If uncertain, mark TODO with references to where the equation should be verified in the docs.
