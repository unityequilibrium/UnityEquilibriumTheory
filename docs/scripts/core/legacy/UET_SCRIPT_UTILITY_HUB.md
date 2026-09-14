# 🛠️ UET Script Utility Hub

The `docs/scripts` folder contains the "Nervous System" of the project: Tools for auditing, testing, migrating, and reporting.

---

## 🚀 **Top-Level Runners (For Users)**

These are the main entry points for running the experiment suites.

| Script | Purpose | Run Command |
| :--- | :--- | :--- |
| **Physics Anomalies** | Solve the Big 5 (Dark Matter, Singularity, etc.) | `python docs/scripts/run_physics_anomalies.py` |
| **Millennium Problems** | Solve the 7 Math Challenges (Navier-Stokes, etc.) | `python docs/scripts/run_millennium_problems.py` |
| **System Audit** | Full Project Integrity Check (Pass/Fail) | `python docs/scripts/integrity_auditor_v2.py` |

---

## 📂 **Folder Structure (The 5 Pillars of Ops)**

| Folder | Purpose | Key Script |
| :--- | :--- | :--- |
| **[Audit/](./Audit/)** | Verify data, integrity, and coverage. | `audit_figure_coverage.py` |
| **[Data/](./Data/)** | Download and manage external datasets. | `download_all_data.py` |
| **[Maintenance/](./Maintenance/)** | Fix paths, imports, and clean legacy files. | `fix_paths.py` |
| **[Reporting/](./Reporting/)** | Generate PDFs, Figures, and Docs. | `collect_paper_figures.py` |
| **[Runners/](./Runners/)** | Execute tests and topics. | `run_topic_tests.py` |
| **[Legacy/](./Legacy/)** | Archived/Deprecated tools. | *(Storage only)* |

---

## 🔧 **Common Usage Guide**

### 1. "I want to generate the Paper Figures."
Go to **Reporting**:
```powershell
python docs/scripts/Reporting/collect_paper_figures.py
```

### 2. "I want to fix broken paths."
Go to **Maintenance**:
```powershell
python docs/scripts/Maintenance/fix_paths.py
```

### 3. "I want to audit my Data Sources."
Go to **Audit**:
```powershell
python docs/scripts/Audit/audit_data_sources.py
```

### 4. "I want to see if I'm missing any images."
Go to **Audit**:
```powershell
python docs/scripts/Audit/audit_figure_coverage.py
```

---

## 🛡️ **Integrity Standard**

All scripts in this directory MUST:
1.  Run from the **Project Root** (`c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0`).
2.  Use **Relative Paths** starting with `docs/...`.
3.  Be strictly categorized (No loose files except major Runners).

---
*Maintained by UET DevOps - v0.9.0*
