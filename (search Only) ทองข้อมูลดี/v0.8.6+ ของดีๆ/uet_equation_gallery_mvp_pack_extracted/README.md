# UET Equation Gallery (Interactive MVP Pack)

This zip is a **small, hackable scaffold** to turn equations into a runnable gallery:
- Click an equation card
- Input numbers
- Run locally in the browser
- Auto-backup every run to a **Ledger** (localStorage)
- Export/Import runs as JSON

## What’s inside
- `original/gallery.html` — your current gallery (unchanged)
- `mvp/gallery_mvp.html` — same gallery + **Interactive Equations** section + **Compute Panel**
- `mvp/js/` — modular JS (Runner + Ledger + UI)
- `mvp/data/equations.json` — equation definitions (edit/add here)
- `mvp/specs/` — lightweight JSON schema for EquationDef + RunRecord

## Quick run
From the `mvp/` folder:
```bash
python -m http.server 8000
```
Open:
- http://localhost:8000/gallery_mvp.html

(Needs a local server because modules + fetch are blocked on `file://`.)

## Extend (one-liner concept)
- Add new entry to `mvp/data/equations.json`
- Implement its function in `mvp/js/local_runner.js`
- Done.

## Backup / Replay
Every run becomes a `RunRecord` and is saved in browser localStorage.
Use:
- Export Ledger (JSON)
- Import Ledger (JSON)

See `notes/PLAN.md` for the architecture and the “runner swap” to Docker/API.
