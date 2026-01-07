# PATCH_NOTES (gallery_mvp.html)

## What changed vs original
1) Added a new gallery section:
   - “🧮 UET Equations (Interactive)”
   - Host element id: `uet-equations-host`

2) Injected a Compute Panel placeholder inside the modal:
   - `<div id="compute-panel" ...></div>`
   - Rendered dynamically by `mvp/js/ui_compute.js`

3) Injected minimal CSS for compute widgets

4) Added one module script:
   - `<script type="module" src="./js/app.js"></script>`

Original inline scripts remain untouched.
