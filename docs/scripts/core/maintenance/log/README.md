# Log Reset System

ระบบลบ log เพื่อให้เครื่องเร็วขึ้น

## วิธีใช้งาน (แค่ Copy-Paste)

### 1. ดูว่า log เยอะไหน

```bash
python docs/scripts/maintenance/log/analyze_log_distribution.py
```

### 2. ลบ log เยอะๆ (เก็บ 10 ล่าสุด)

```bash
python docs/scripts/maintenance/log/reset_topic_logs.py --category EXCESSIVE --keep-recent 10
```

### 3. ลบ log หัวข้อเดียว

```bash
python docs/scripts/maintenance/log/reset_topic_logs.py --topic 0.10 --keep-recent 10
```

### 4. ลบ log ทั้งหมด (อันตราย!)

```bash
python docs/scripts/maintenance/log/reset_topic_logs.py --all --keep-recent 10 --force
```

### 5. ลบไฟล์รายงานทิ้ง

```bash
python docs/scripts/maintenance/log/cleanup_reports.py
```

## อธิบายไฟล์ต่างๆ

- `analyze_log_distribution.py` - วิเคราะห์ log ว่าหัวข้อไหนมีเยอะ
- `reset_topic_logs.py` - ระบบลบ log หลัก
- `diagnose_log_systems.py` - เช็คว่าหัวข้อไหน log พัง
- `log_reset_manager.py` - เมนูหลัก
- `cleanup_reports.py` - ลบไฟล์รายงานทิ้ง
- `reset_logs/` - ปุ่มลบ log แต่ละหัวข้อ

## คำสั่งที่ใช้บ่อย

```bash
# ลบ log เยอะๆ
python docs/scripts/maintenance/log/reset_topic_logs.py --category EXCESSIVE --keep-recent 10

# ลบ log หัวข้อเดียว
python docs/scripts/maintenance/log/reset_topic_logs.py --topic 0.10 --keep-recent 10

# ลบ log ทั้งหมด
python docs/scripts/maintenance/log/reset_topic_logs.py --all --keep-recent 10 --force

# ลบไฟล์รายงาน
python docs/scripts/maintenance/log/cleanup_reports.py
```

## สถานะปัจจุบัน

หลังลบ log แล้ว:
- 0.10: 12 logs (เคย 1535)
- 0.14: 12 logs (เคย 1095)
- ทุกหัวข้อ: เก็บ 10 ล่าสุด
