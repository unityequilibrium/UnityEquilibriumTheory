# 🛡️ Audit Scripts

Scripts for verifying the scientific integrity, data coverage, and code quality of the UET project.

## 📋 Script Inventory

| Script | Purpose | Run Command |
| :--- | :--- | :--- |
| `audit_figure_coverage.py` | **Visual Gap Analysis**: Checks if research scripts are actually generating the expected plots. | `python docs/scripts/Audit/audit_figure_coverage.py` |
| `audit_data_sources.py` | **Data Inventory**: Scans `Data/` folders and verifies checksums/sizes. | `python docs/scripts/Audit/audit_data_sources.py` |
| `audit_system_integrity.py` | **Deep Scan**: Checks for broken imports, missing constants, and "Shadow Math". | `python docs/scripts/Audit/audit_system_integrity.py` |
| `validate_foundation.py` | **Core Check**: Ensures `Engine` matches `UETParameters`. | `python docs/scripts/Audit/validate_foundation.py` |
| `stress_test_integrity.py` | **Load Test**: Simulates high-load scenarios. | `python docs/scripts/Audit/stress_test_integrity.py` |

---

## 🚀 Usage Scenarios

### 1. "Why do I only have 94 images?"
Run the coverage audit to identify "Silent Scripts":
```powershell
python docs/scripts/Audit/audit_figure_coverage.py
```

### 2. "Are my Data files corrupted?"
Run the data source audit:
```powershell
python docs/scripts/Audit/audit_data_sources.py
```
