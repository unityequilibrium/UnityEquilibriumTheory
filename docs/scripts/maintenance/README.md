# 🔧 Maintenance Scripts

Utilities for fixing codebase issues, refactoring, and general cleanup.

Current cleanup: `python docs/scripts/maintenance/cleanup_outputs.py` previews ignored Python caches; add `--apply` to remove them. It preserves research results, raw inputs and tracked files. The older Core tooling entrypoint delegates to this command. Generic logger output uses `.uet-run-reports/logs/`; topic-bound logs use `topics/<topic>/Result/_Logs/`. Explicit legacy `docs/topics/` and `docs/core/` output locations are redirected to the canonical roots.

Review topic logs with `python docs/scripts/maintenance/log/reset_topic_logs.py --topic 0.4`.
After checking that a particular run is disposable and no writer or reader is using it,
add `--apply --run <folder-name>`. Repeat `--run` for other reviewed folders.
Folders with unknown files, tracked content, or no matching summary stay in place.
Use `python topics/run_all_tests.py --all --list --verbose` to locate candidate
input/output calls by source line without running research producers.

## 📋 Script Inventory

| Script | Purpose | Run Command |
| :--- | :--- | :--- |
| `fix_paths.py` | **Path Repair**: Updates legacy `parents[1]` logic to Robust Path Finding. | `python docs/scripts/Maintenance/fix_paths.py` |
| `update_readmes.py` | **Doc Updater**: Batch updates `README.md` files across topics. | `python docs/scripts/Maintenance/update_readmes.py` |
| `cleanup_outputs.py` | Preview/remove ignored Python caches only. | `python docs/scripts/maintenance/cleanup_outputs.py` |
| `migrate_to_golden_result.py` | **Result Standardization**: Moves outputs to `Result/` folder. | `python docs/scripts/Maintenance/migrate_to_golden_result.py` |

---

## 🚀 Usage Scenarios

### 1. "My scripts crash effectively finding 'Code' directory."
Run the path fixer:
```powershell
python docs/scripts/Maintenance/fix_paths.py
```
