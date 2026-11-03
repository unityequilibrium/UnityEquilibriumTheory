# Local Recovery Manifest

## 2026-11-03 owner-directed history workspace relocation

The owner reports moving the complete `uet_history` workspace into the separate
Superapp project and explicitly requests removing its former Harness files from
main. This supersedes earlier recovery plans to keep that workspace here.

- Scope: all 78 tracked paths under `uet_history/`; no research topic results,
  raw data, cache, or other workspace is added or removed by this publication.
- Evidence retained: the pre-removal Git parent contains the original 78 files
  and their history. No history rewrite or force push is requested.
- Destination: reported by the owner, not inspected or modified by Harness.
- CI: removed JSON files are not parsed as live inputs. A missing book registry
  is acceptable only when no tracked history/book workspace remains; a partial
  removal still fails validation.

**Date:** 2026-07-02
**Branch:** `codex/recover-local-workspace-batch`
**Purpose:** Recover important local workspace material into GitHub `main` in one auditable batch without importing build output, credentials, or large raw assets.

## Included in this batch

| Area | Included | Notes |
| :-- | :-- | :-- |
| `services_and_experiments/` | source code, docs, manifests, migrations, and small config files | Restores prototype service source tree from PR #9 into the batch branch. Build outputs, binaries, local env files, and caches stay excluded. |
| `thailand_proposals/` | 64 markdown/source files, `.gitkeep` files, proposal structure, and standards | Raw media assets are not committed in this batch. |
| `Result/` | `emergent_sandbox_result.md`, `sandbox_emergence.png` | Small sandbox result artifact only. |
| `docs/core/test/sandbox_emergent.py` | sandbox script | Included so the top-level sandbox result has a source script. |
| `docs/topics/0.11_Phase_Transitions/` | pending docs, verifier, manifest, data, and result artifacts for the TeX formula-fragment gate and local status sync | Keeps 0.11 claim boundary controlled by gates/artifacts rather than prose memory. |

## Excluded from this batch

| Area | Excluded | Reason |
| :-- | :-- | :-- |
| `thailand_proposals/` raw assets | 18 PDF/audio/image files, about 109 MB total | Too large for this source recovery batch. Track separately as an asset/raw-data PR or external artifact package. |
| Root scratch files | `output.txt`, `transcript.th.vtt` | Local scratch/transcript state; not a canonical source file yet. |
| `docs/topics/For_Work/` | duplicate underscore path | `docs/topics/For Work/` is the canonical standards path. Underscore path needs a separate migration decision. |
| `uet_history/` deletions | local deletion set | Destructive cleanup risk; keep out of recovery batch. |
| Service build/runtime output | `.env`, `debug/`, `target/`, `target_*`, `*.exe`, `*_linux`, cache markers | Local machine state or compiled artifacts; publish binaries via releases if needed. |

## Largest excluded Thailand raw assets

- `thailand_proposals/00_Inbox/raw/?????????????????????_??????????????????...` (~29.3 MB)
- `thailand_proposals/00_Inbox/raw/Thailand_s_Water_Opportunity.pdf` (~17.3 MB)
- `thailand_proposals/00_Inbox/raw/Thai_Water_City.pdf` (~16.0 MB)
- Multiple `thailand_proposals/03_logistics_and_infra/???/.../Screenshot ...png` files between ~1.5 MB and ~6.5 MB each

## Follow-up queue

1. Close PR #9 as superseded by this batch PR once this branch is pushed.
2. Create a dedicated raw-asset plan for `thailand_proposals` if those PDFs/audio/images should be versioned.
3. Decide whether `docs/topics/For_Work/` should be deleted locally, migrated, or archived.
4. Audit `uet_history` separately before accepting any deletion-heavy cleanup.
