# docs/scripts

| Folder | Contents |
| :-- | :-- |
| `standard/` | Research Standard v2 checks run in CI: `check_schema.py`, `check_preregistration.py`, `check_physics_tests.py`, `new_formal_contract.py`, and their tests |
| `maintenance/` | Work-ledger index builder and its test |
| `audit/` | `audit_calculation_completeness.py` (CI contract checker) and the scripts that calculation contracts lock or kept topic 0.13 code calls |
| `core/` | Helpers that kept core or topic code imports |
| `recovery/` | `prepare_pages_math.py`, used by the Pages workflow |
| `debug/` | Four old debug scripts, kept only because the public-boundary CI check blocks any change, deletions included, to a folder named `debug`; remove them once that check ignores deletions |

The other legacy scripts (about 1,000 audit, sync, gate, migration, reporting and runner scripts) were removed on
2026-11-27 under STANDARD §8. They are kept at git tag `archive/legacy-2026-11`:
`git show archive/legacy-2026-11:docs/scripts/<path>`.
