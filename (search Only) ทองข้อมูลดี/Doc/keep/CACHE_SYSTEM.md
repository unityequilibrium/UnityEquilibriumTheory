# 🗂️ Centralized Cache System

> **ปัญหา**: `__pycache__` กระจายทุกโฟลเดอร์เมื่อรัน Python
> **วิธีแก้**: ใช้ `PYTHONPYCACHEPREFIX` ให้ cache ไปที่เดียว

---

## ⚙️ วิธีตั้งค่า

### Option 1: ใช้ Environment Variable (แนะนำ)

สร้างไฟล์ `.env` หรือเพิ่มใน activate script:

```powershell
# Set in PowerShell profile or .env
$env:PYTHONPYCACHEPREFIX = "C:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\.cache\pycache"
```

### Option 2: ใช้ pyproject.toml (Python 3.8+)

```toml
[tool.python]
# Python doesn't support this in pyproject.toml directly
# Use environment variable instead
```

---

## 📁 โครงสร้างใหม่

```
Lab_uet_harness_v0.8.7/
├── .cache/                    ← รวม cache ทั้งหมดที่นี่
│   ├── pycache/               ← __pycache__ ทั้งหมด
│   └── pytest/                ← pytest cache
├── .gitignore                 ← ignore .cache/
└── research_uet/              ← สะอาด ไม่มี __pycache__
```

---

## 🔧 วิธี Activate

### สำหรับ .venv (activate.ps1)

เพิ่มบรรทัดนี้ใน `\.venv\Scripts\Activate.ps1`:

```powershell
$env:PYTHONPYCACHEPREFIX = "$PSScriptRoot\..\..\\.cache\pycache"
```

### สำหรับ run ทุกครั้ง

สร้างไฟล์ `run.ps1`:

```powershell
$env:PYTHONPYCACHEPREFIX = ".\.cache\pycache"
python $args
```

---

## ✅ ผลลัพธ์

- `research_uet/` จะไม่มี `__pycache__` อีกต่อไป
- Cache ทั้งหมดไป `.cache/pycache/`
- Git ignore `.cache/` folder

---

*Cache Centralization v1.0*
