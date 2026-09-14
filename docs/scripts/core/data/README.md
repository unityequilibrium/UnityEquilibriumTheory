# 💾 Data Scripts

Tools for managing the external datasets (SPARC, LIGO, Planck, etc.) required for UET validation.

## 📋 Script Inventory

| Script | Purpose | Run Command |
| :--- | :--- | :--- |
| `download_all_data.py` | **Master Downloader**: Fetches all missing datasets from the UET mirrors. | `python docs/scripts/Data/download_all_data.py` |

---

## 🚀 Usage Scenarios

### 1. "I'm missing the SPARC galaxy data."
Run the downloader (it skips existing files):
```powershell
python docs/scripts/Data/download_all_data.py
```
