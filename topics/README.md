# UET topics

Evidence is tracked per claim in [`docs/standard/claims.json`](../docs/standard/claims.json) under
[`docs/STANDARD.md`](../docs/STANDARD.md), not per topic.

On 2026-11-27 the old core-research topics (0.0–0.26) were removed from the working tree with the author's approval
(STANDARD §8, plan in [`docs/meta/CLEANUP_PLAN_2026-11-27.md`](../docs/meta/CLEANUP_PLAN_2026-11-27.md)).
They used topic-local engines with fitted or anchored values and none passed the distinctness screen
([`docs/meta/TOPIC_DISTINCTNESS_SCREEN_2026-11-16.md`](../docs/meta/TOPIC_DISTINCTNESS_SCREEN_2026-11-16.md)).
Every removed file is kept at git tag `archive/legacy-2026-11`: `git show archive/legacy-2026-11:topics/<path>`.

## Kept research topics

| Topic | Why it is kept |
| :-- | :-- |
| [0.3](./0.3_Cosmology_Hubble_Tension/) | Proposals of Test Cards T040 and T041 |
| [0.11](./0.11_Phase_Transitions/) | Only the 8 files a calculation contract locks |
| [0.13](./0.13_Thermodynamic_Bridge/) | Uses the parent action; T015 and its contracts |
| [0.18](./0.18_Mathnicry/) | Active Lean work |
| [0.23](./0.23_Unity_Scale_Link/) | Stress tests of UET (T028, open PR #96) |
| [0.25](./0.25_Strategy_Power_Economics/) | Test Cards T021 and T024 |

## Future concepts (0.27–0.39)

The author's ideas for later development. They are exploratory, carry no evidence level, and were kept on purpose.

## Other folders

- [`For Work/`](./For%20Work/) operational standards still in force under STANDARD §15 (do not edit).
- `run_all_tests.py`, `tests/`, `test_suite_config.json` the shared test runner used by CI.
