# UET Atlas Runner Pack (0.8.5-pre) — คู่มือ “กดรันได้เลย” (Windows PowerShell)

> แพ็กนี้ทำไว้เพื่อให้คุณ “ไม่ต้องรู้ Python” ก็รัน Atlas A/B/C ได้ โดยใช้คำสั่ง PowerShell ทีละบรรทัด  
> **หมายเหตุ:** สคริปต์นี้ *เรียกไฟล์ใน repo* ดังนี้ (แก้ path ได้ถ้า repo ของคุณต่างไป):
> - scripts\make_atlas_A.py
> - scripts\make_atlas_B.py
> - scripts\make_atlas_C.py
> - scripts\run_suite.py
> - scripts\plot_atlas_A.py
> - scripts\plot_atlas_BC.py
> - scripts\grid_audit.py  (ถ้ามี)

---

## 0) ก่อนเริ่ม: เปิด PowerShell ในโฟลเดอร์ repo root
ตัวอย่างโครง:
```
uet_harness_v0_1_35_fixed_clean/
  scripts/
  matrices/
  uet_core/
  .venv/   (จะถูกสร้างโดย ensure_venv.ps1)
```

---

## 1) สร้าง/เปิด venv และลงของจำเป็น (ครั้งแรกครั้งเดียว)
รัน:
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\ensure_venv.ps1
```

ถ้าผ่าน จะขึ้นว่าใช้ python จาก `.venv`

---

## 2) ล้างผลรันเก่า (ถ้าอยาก clean slate)
```powershell
.\clean_outputs.ps1
```

---

## 3) รัน Atlas-A (a × delta=λ) — phase map หลุมศักย์
```powershell
.\run_atlas_A.ps1
```

ผลที่ต้องได้:
- runs\atlas_A\ledger.csv
- reports\atlas_A\atlas_summary.csv
- reports\atlas_A\*.png

---

## 4) รัน Atlas-B (kappa sweep) + Atlas-C (s sweep)
```powershell
.\run_atlas_B.ps1
.\run_atlas_C.ps1
```

---

## 5) (ถ้ามี) รัน grid invariance audit (32/64/128)
```powershell
.\run_grid_audit.ps1
```

---

## 6) ถ้ามันเออเรอร์ ดูตรงไหนก่อน
### 6.1 venv/python ไม่ตรง
รัน:
```powershell
python -c "import sys; print(sys.executable)"
```
ต้องชี้ไป `.venv\Scripts\python.exe`

### 6.2 หาไฟล์สคริปต์ไม่เจอ
เช็คว่า repo ของคุณมีจริง:
- scripts\make_atlas_A.py
- scripts\run_suite.py
- scripts\plot_atlas_A.py
ถ้าไม่มีก็ให้ Agent สร้างตามสเปคก่อน

### 6.3 บรรทัด error บอกว่าขาด package
ให้ติดตั้งเพิ่ม:
```powershell
pip install numpy pandas matplotlib
```

---

## 7) “ไฟล์ไหนคือของจริง”
ยึดตามนี้เสมอ (กันงง):
- ข้อมูลดิบ: `runs\atlas_*\ledger.csv`
- สรุป/กราฟ: `reports\atlas_*`

---

## 8) P1–P3 (จุดอ้างอิงมาตรฐาน)
สคริปต์ Atlas-B ใช้ P1–P3:
- P1: a=-1, delta=1, kappa sweep, s=0
- P2: a=+0.5, delta=1, kappa sweep, s=0
- P3: a=-1, delta=4, kappa sweep, s=0

Atlas-C ใช้ P1 แล้ว sweep s

---

ถ้าต้องการ “รันทีเดียวจบ A→B→C→Audit”
```powershell
.\run_all.ps1
```
