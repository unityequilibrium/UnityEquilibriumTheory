# 📊 Reporting Scripts

Tools for generating papers, figures, and high-level documentation.

## 📋 Script Inventory

| Script | Purpose | Run Command |
| :--- | :--- | :--- |
| `collect_paper_figures.py` | **Figure Harvester**: Copies validation plots from Topics to `paper/Figures`. | `python docs/scripts/Reporting/collect_paper_figures.py` |
| `generate_analysis_docs.py` | **Doc Generator**: Creates `ANALYSIS_*.md` templates for incomplete topics. | `python docs/scripts/Reporting/generate_analysis_docs.py` |
| `apply_viz.py` | **Style Applicator**: Enforces UET styling on existing matplotlib figures. | `python docs/scripts/Reporting/apply_viz.py` |

---

## 🚀 Usage Scenarios

### 1. "I need the figures for my LaTeX paper."
Run the harvester:
```powershell
python docs/scripts/Reporting/collect_paper_figures.py
```
