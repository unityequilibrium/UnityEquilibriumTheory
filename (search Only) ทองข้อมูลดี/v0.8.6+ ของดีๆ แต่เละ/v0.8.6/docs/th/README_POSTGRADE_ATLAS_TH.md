# UET Post-Grade Atlas Pack — ทำ “PASS-only Atlas” จาก grade_runs.py

## ต้องมีอะไรก่อน
1) คุณรัน Atlas แล้วได้ runs/atlas_*/ledger.csv
2) คุณรัน physics grading แล้วได้ runs/atlas_*/grades.csv
   ตัวอย่าง:
   ```powershell
   python .\scripts\grade_runs.py --runs .\runs\atlas_A
   ```

## 1) สร้าง PASS-only report ของ Atlas-A
```powershell
python .\scripts\plot_atlas_A_graded.py --runs .\runs\atlas_A --out .\reports\atlas_A_PASS --only_grade PASS
```

ดู WARN/FAIL:
```powershell
python .\scripts\plot_atlas_A_graded.py --runs .\runs\atlas_A --out .\reports\atlas_A_WARN --only_grade WARN
python .\scripts\plot_atlas_A_graded.py --runs .\runs\atlas_A --out .\reports\atlas_A_FAIL --only_grade FAIL
```

## 2) สร้าง PASS-only report ของ Atlas-B/Atlas-C
```powershell
python .\scripts\plot_atlas_BC_graded.py --runs .\runs\atlas_B --out .\reports\atlas_B_PASS --only_grade PASS
python .\scripts\plot_atlas_BC_graded.py --runs .\runs\atlas_C --out .\reports\atlas_C_PASS --only_grade PASS
```

## 3) ทำ “ตาราง Identifiability” 1 หน้า
หลังคุณมี report summaries แล้ว:
```powershell
python .\scripts\make_identifiability_table.py ^
  --atlasA .\reports\atlas_A_PASS\atlas_summary.csv ^
  --out .\reports\identifiability_table.csv
```

> ตารางนี้เป็น pre-master: บอกว่า α/λ/κ/s ควรผูกกับ observable ไหน และพิสูจน์ด้วย atlas ไหน
