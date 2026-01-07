# Space as Recorder

## Space บันทึกข้อมูลจากทุกพฤติกรรม

---

## Core Insight

> **"สิ่งที่เห็น = ข้อมูลใน Space ที่เกิดจากเหตุการณ์จริงๆ"**

---

## Bekenstein Bound

Maximum information ที่ Space region เก็บได้:

```
S_max = (2π k R E) / (ħ c)
```

| Symbol | Meaning |
|--------|---------|
| S_max | Maximum entropy |
| k | Boltzmann constant |
| R | Radius of region |
| E | Total energy |
| ħ | Reduced Planck constant |
| c | Speed of light |

---

## Light Cone

เราเห็นได้เฉพาะ **past light cone**:

```
|Δx| ≤ c × Δt
```

**ความหมาย:**
- เห็นดาวเป็น "อดีต" ไม่ใช่ "ปัจจุบัน"
- ข้อมูลเดินทางด้วยความเร็วแสง
- ถ้าเห็นปัจจุบันทันที = ละเมิด causality

---

## Holographic Principle

> ข้อมูล 3D encode บน boundary 2D

**ความหมาย:**
- Space คือ holographic screen
- ข้อมูลไม่หาย — ถูกเก็บบน boundary
- นี่คือ "ระบบบันทึก" ของจักรวาล

---

## Implementation

```python
from uet_landauer import UniverseSpace, SpaceRegion

# Create universe
universe = UniverseSpace(T=300)

# Create region
star = universe.create_region("Star", radius=1.0)

# Record behavior
universe.record("Star", bits=1e20, source="Event")

# Check light cone
visible = universe.light_cone_visible(
    observer_pos=0,
    event_pos=C_LIGHT * 1,  # 1 light-second away
    event_time=0
)
```

---

*Space as Recorder - Part 3*
