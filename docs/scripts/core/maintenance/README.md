# 🔧 Maintenance Scripts

Utilities for fixing codebase issues, refactoring, and general cleanup.

## 📋 Script Inventory

| Script | Purpose | Run Command |
| :--- | :--- | :--- |
| `fix_paths.py` | **Path Repair**: Updates legacy `parents[1]` logic to Robust Path Finding. | `python docs/scripts/Maintenance/fix_paths.py` |
| `update_readmes.py` | **Doc Updater**: Batch updates `README.md` files across topics. | `python docs/scripts/Maintenance/update_readmes.py` |
| `cleanup_outputs.py` | **Disk Cleaner**: Removes temp logs and failed run artifacts. | `python docs/scripts/Maintenance/cleanup_outputs.py` |
| `migrate_to_golden_result.py` | **Result Standardization**: Moves outputs to `Result/` folder. | `python docs/scripts/Maintenance/migrate_to_golden_result.py` |

---

## 🚀 Usage Scenarios

### 1. "My scripts crash effectively finding 'Code' directory."
Run the path fixer:
```powershell
python docs/scripts/Maintenance/fix_paths.py
```
