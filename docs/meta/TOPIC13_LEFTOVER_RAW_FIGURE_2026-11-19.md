# Topic 0.13 leftover under `docs/topics/` (diagnosis, 2026-11-19)

Status: resolved with option 1 on 2026-11-19 at the owner's request (see "Resolution" at the end). The figure was not moved.

## What is left

After the root move (PR #60, 2026-11-14) exactly one tracked file stayed under `docs/topics/0.13_Thermodynamic_Bridge/`:

`docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_fig1.png` (207,142 bytes, added in `2ffb6ca7f`, 2026-08-10).

It is the Ding et al. 2022 Fig. 1 image. The producer records its licence context as "CC BY 4.0 article figure asset".

## Why it was left behind

- `.github/workflows/pr-scope.yml` blocks any changed path that contains a `raw/` folder.
  A `git mv` of this file counts as a change, so moving it would turn the "Scope and public boundary" check red.
- `.gitignore` lines 412–413 ignore `/docs/topics/**/raw/`. The file is tracked only because it was force-added before that rule.

## What is broken

`topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_Ding2022_Figure_Digitization.py` reads
`topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_fig1.png`, which does not exist.
Running it now stops with `FileNotFoundError` (checked 2026-11-19).

The saved outputs it produced earlier (`ding_2022_fig1d_digitized.csv` and `ding_2022_fig1d_digitized_manifest.json`) are still in
`topics/0.13_Thermodynamic_Bridge/Data/03_Research/`. Their recorded image hash is unaffected, so existing results are not invalid.
Only a re-run of the digitization is blocked.

## Related gap

The `raw/` ignore rules were not copied to the new root. `/topics/**/raw/` is not in `.gitignore`, so a raw file placed under
`topics/` would show up as untracked and could be added by mistake. The pr-scope check would still block it in CI.

## Options (owner decision)

1. Leave the file where it is, and make the producer fall back to the old location through `core.core_paths.canonical_existing_path`. This is a code change to one Topic 0.13 script.
2. Move the file to `topics/.../raw/` and let pr-scope accept pure renames (R100) of already-tracked raw files. This is a CI-gate change.
3. Untrack the file (keep it local and record its hash), as the raw/private rule in AGENTS.md §2 suggests. This changes what is published.

In every option, add `/topics/**/Data/**/raw/` and `/topics/**/raw/` to `.gitignore`.

## Resolution (2026-11-19, owner chose option 1)

- `Research_Ding2022_Figure_Digitization.py` now reads `topics/.../raw/ding_2022_fig1.png` if a copy is present and otherwise reads the tracked file at `docs/topics/.../raw/`.
  The recorded input path and hash in the manifest are unchanged.
- Check: the figure's sha256 is `d88faf2f…`, matching the manifest. A re-run gives 432 rows and CSV sha256 `c4117bb4…`, which equals the `pre_repair_sha256` recorded before the later series-mapping repair, so the first digitization step is reproduced byte for byte.
  The saved, repaired outputs were left as they are.
- `test_ding2022_figure_locator.py` (3 software tests) is now in the Topic 0.13 suite.
- `.gitignore` now also ignores `/topics/**/Data/**/raw/` and `/topics/**/raw/`.
