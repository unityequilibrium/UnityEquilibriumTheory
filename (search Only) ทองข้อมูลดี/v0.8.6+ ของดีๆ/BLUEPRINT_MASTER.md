# UET LAB - BLUEPRINT MASTER v1.0

> **เอกสารมาตรฐานของโปรเจค - ทุกคน/AI ต้องยึดตามนี้**  
> Created: 2024-12-23  
> Version: 1.0  

---

## TL;DR

```
เว็บมี 3 routes: /home, /lab, /gallery
ทั้งระบบใช้ Shell เดียว (LabShell)
Registry 3 ก้อน: room, metric, test
Room มี 2 type: sim3d, test_terminal
ห้ามสร้าง demo route แยก!
```

---

# 1. MASTER ARCHITECTURE DIAGRAM

```
UET APP (3 ROUTES ONLY)
┌────────────────────────────────────────────────────────────┐
│ 1) /          = Home (3D background + minimal overlay)     │
│ 2) /lab       = LabShell + RoomRouter + Panels + Dock      │
│ 3) /gallery   = List rooms → opens /lab?room=...           │
└────────────────────────────────────────────────────────────┘

SPECIAL ROUTES (dev/test only):
• /test-lab    = Test gates runner (should merge into /lab as room_type=test_terminal)
```

---

# 2. LAB = ONE SHELL ARCHITECTURE

```
/lab (ONE SHELL - ALL ROOMS USE THIS)
┌───────────────────────────────────────────────────────────────┐
│ TopNav (fixed) + Room Selector (dropdown)                     │
├───────────────────────────────────────────────────────────────┤
│ Left Panel (Output)  │  Center (Room Renderer) │ Right Panel  │
│ • MetricCards        │  sim3d OR test_terminal │ • Equations   │
│ • Validation Strip   │                         │ • Params      │
│ • Save/Export        │                         │ • Inspector   │
│                      │                         │ • Notes(+)    │
├───────────────────────────────────────────────────────────────┤
│ Bottom GraphDock (selected metrics overlay by plot_group)     │
└───────────────────────────────────────────────────────────────┘
```

### สิ่งที่ไม่เปลี่ยนตามห้อง:
- Left Output Panel
- Right Studio Panel  
- GraphDock
- TopNav

### สิ่งที่เปลี่ยนตามห้อง:
- **Center Renderer เท่านั้น**
  - `sim3d` → 3D Canvas
  - `test_terminal` → Terminal UI

---

# 3. FILE STRUCTURE STANDARD

## ✅ TARGET STRUCTURE (ต้องเป็นแบบนี้)

```
frontend/src/
├── app/
│   ├── page.tsx              # / (Home)
│   ├── lab/page.tsx          # /lab (ใช้ LabShell)
│   └── gallery/page.tsx      # /gallery
│
├── shell/                    # [ยังไม่มี - ต้องสร้าง]
│   ├── LabShell.tsx          # TopNav + Panels + Dock + RoomRouter
│   └── AppTokens.ts          # Design tokens
│
├── registries/               # [ยังไม่มี - ต้องสร้าง]
│   ├── roomRegistry.ts       # Room definitions
│   ├── metricRegistry.ts     # Move from lib/registry/
│   └── testRegistry.ts       # Test gates definitions
│
├── features/
│   ├── metrics/              # [ย้ายจาก components/lab/]
│   │   ├── MetricCard.tsx
│   │   ├── MetricCardList.tsx
│   │   ├── GraphDock.tsx
│   │   └── plotGrouping.ts
│   │
│   ├── rooms/                # [ยังไม่มี - ต้องสร้าง]
│   │   ├── RoomRouter.tsx
│   │   ├── Sim3DRoom.tsx
│   │   └── TestTerminalRoom.tsx
│   │
│   └── panels/               # [ย้ายจาก components/layout/]
│       ├── LeftOutputPanel.tsx
│       └── RightStudioPanel.tsx
│
└── services/                 # [มีแล้ว แต่อยู่ใน lib/services/]
    ├── telemetryService.ts
    ├── persistenceService.ts
    └── notesService.ts
```

## ❌ CURRENT STRUCTURE (ปัจจุบัน - มีปัญหา)

```
frontend/src/
├── app/
│   ├── page.tsx              # Home ✅
│   ├── lab/page.tsx          # Lab ✅ (แต่ยังไม่ใช้ LabShell)
│   ├── gallery/              # ✅
│   ├── test-lab/             # ⚠️ ควรเป็น room ใน /lab ไม่ใช่ route แยก
│   └── api/                  # ✅
│
├── components/
│   ├── lab/                  # ⚠️ ควรย้ายไป features/metrics/
│   │   ├── MetricCard.tsx
│   │   ├── MetricCardList.tsx
│   │   ├── GraphDock.tsx
│   │   └── ... (12 files)
│   │
│   ├── layout/               # ⚠️ ควรย้ายไป features/panels/
│   │   ├── LeftOutputPanel.tsx
│   │   ├── RightStudioPanel.tsx
│   │   ├── TopNav.tsx
│   │   └── CenterHUD.tsx
│   │
│   └── [18 other files]      # ❓ รกมาก ต้อง organize
│
├── lib/
│   ├── registry/             # ⚠️ ควรย้ายไป registries/
│   ├── services/             # ⚠️ ควรย้ายไป services/
│   ├── oracle/               # ✅
│   ├── equations/            # ✅
│   └── SimCore*.ts           # ✅
│
└── store/                    # ⚠️ ควรรวมกับ shell state
```

---

# 4. THREE REGISTRIES (Single Source of Truth)

## 4.1 Room Registry
```typescript
interface RoomDefinition {
  room_id: string;
  type: 'sim3d' | 'test_terminal';
  title: string;
  description: string;
  tags: string[];
  defaultModules: string[];     // ['newtonian', 'uet']
  defaultMetrics: string[];     // metric_ids to show by default
  permissions: {
    saveToDB: boolean;
    export: boolean;
  };
}
```

**Rooms ที่ต้องมี:**
- `solarSystem` - sim3d
- `keplerOrbit` - sim3d
- `testGates` - test_terminal
- `diagnostics` - test_terminal

## 4.2 Metric Registry (มีแล้ว ✅)
```typescript
interface MetricDefinition {
  metric_id: string;
  label: string;
  symbol: string;
  unit: string;
  unit_category: 'QNT' | 'QLT' | 'COUNT';
  mode_default: 'PHY' | 'UET' | 'IND' | '#';
  plot_group: string;
  dimension_group: string;
  format: 'decimal' | 'scientific' | 'percent';
  default_visible: boolean;
}
```

## 4.3 Test Registry
```typescript
interface TestGateDefinition {
  gate_id: 'G0' | 'G1' | 'G2' | 'G3' | 'G4';
  name: string;
  description: string;
  scenarios: string[];
  tolerances: Record<string, number>;
  expectedResults: 'PASS' | 'FAIL' | 'EXPECTED_FAIL';
}
```

---

# 5. COMPONENT RULES (1-1-1 Pattern)

## MetricCard (1 metric = 1 card)
```
┌─────────────────────────────┐
│ [▢] Total Energy (E)        │  ← Checkbox + Label + Symbol
│ -2534.11  J  [QNT][PHY]     │  ← Value + Unit + CategoryBadge + ModeBadge
│ [Graph ▾]                   │  ← Expand/Collapse mini plot
└─────────────────────────────┘
```

**Requirements:**
- Checkbox → เลือกแล้วไปโผล่ใน GraphDock
- CategoryBadge: `[QNT]` / `[QLT]` / `[COUNT]`
- ModeBadge: `[PHY]` / `[UET]` / `[IND]` / `[#]`
- ไม่มีปุ่ม X บนการ์ด

## GraphDock (Auto-Grouping)
```
[▲] Selected: [E ✕] [K ✕] [U ✕]  [Clear]  View:[Time▼]  Range:[Auto▼]
┌────────────────────────────────────────────────────────────────────┐
│ PLOT AREA                                                          │
│ • Overlay: same plot_group only                                    │
│ • Different groups → stacked plots                                 │
└────────────────────────────────────────────────────────────────────┘
```

---

# 6. SAVE/EXPORT RULES

## ✅ ALLOWED LOCATIONS
- **Left Output Panel** → `[💾 Save to Gallery]` + `[⬇ Export...]`

## ❌ FORBIDDEN LOCATIONS
- ~~Right Studio Panel~~ (Input side - ไม่มี Save/Export)
- ~~Center HUD~~ (ไม่มี Save/Export)
- ~~Anywhere else~~

## Behavior
- **Save** = บันทึกลง Database → ไปโผล่ใน Gallery
- **Export** = ออกไฟล์ (เลือก format ตอนกด: CSV/JSON/HTML)

---

# 7. WORK PATTERN (บังคับทุกครั้ง)

เวลาแก้ไขอะไรก็ตาม ต้องทำตาม checklist นี้:

## STEP 1: UX SPEC (ก่อนเขียนโค้ด)
- [ ] แก้อะไร? (ตำแหน่ง/พฤติกรรม/สถานะ)
- [ ] กระทบ component ไหน?
- [ ] ต้องเพิ่ม field ใน registry ไหม?

## STEP 2: CONTRACTS
- [ ] ถ้าเกี่ยวกับข้อมูล → แก้ registry
- [ ] ถ้าเกี่ยวกับ state → แก้ store schema
- [ ] ถ้าเกี่ยวกับหน่วย → แก้ unit_category + plot_group

## STEP 3: FRONTEND
- [ ] แก้ component ที่ใช้ร่วม (ไม่แก้ในหน้า)
- [ ] **ห้ามสร้างหน้า demo ใหม่**
- [ ] dev sandbox ได้ แต่ต้องใช้ shell เดียว

## STEP 4: BACKEND/API
- [ ] endpoint ยังตรง contract ไหม?
- [ ] save/export อยู่ถูกที่ไหม?

## STEP 5: DATABASE
- [ ] schema เก็บพอ replay ไหม? (seed/params/versions)
- [ ] migration needed?

## STEP 6: GATES (รันบังคับ)
- [ ] UI gate: card→dock ยังถูก
- [ ] Integration: save/export ยังถูกที่
- [ ] Deterministic: ไม่พัง

---

# 8. CURRENT STATUS CHECK

## ✅ Done
- [x] Metric Registry (JSON + TypeScript contracts)
- [x] MetricCard component (1-1-1 pattern)
- [x] MetricCardList component
- [x] GraphDock with auto-grouping
- [x] LeftOutputPanel with Save/Export
- [x] RightStudioPanel with 4 tabs
- [x] TopNav, CenterHUD
- [x] Telemetry/Persistence/Notes services
- [x] API routes for runs/notes/telemetry
- [x] Oracle module (kepler, invariants, testRunner)
- [x] TypeScript errors fixed (0 errors)

## ⚠️ Needs Refactoring
- [ ] Move components to features/ structure
- [ ] Create shell/ directory with LabShell
- [ ] Create registries/ directory
- [ ] Merge /test-lab into /lab as room_type=test_terminal
- [ ] Create RoomRouter component
- [ ] Create roomRegistry.ts and testRegistry.ts

## ❌ Not Started
- [ ] TestTerminalRoom component
- [ ] Room selector dropdown in HUD
- [ ] URL sync (/lab?room=xxx)

---

# 9. FORBIDDEN ACTIONS

1. ❌ **ห้ามสร้าง route ใหม่** เพื่อ demo UI
2. ❌ **ห้าม hardcode metric** ใน component
3. ❌ **ห้ามสร้าง state แยก** สำหรับ demo
4. ❌ **ห้ามใส่ Save/Export** นอก Left Panel
5. ❌ **ห้ามใส่ปุ่ม X** บน cards/panels
6. ❌ **ห้ามเดา unit/plot_group** - ต้องอ่านจาก registry

---

# 10. VALIDATION GATES

## G0: Data/Schema
- metric_registry มี unit_category/mode ครบ
- runs/presets/templates join ได้
- Save ทำงาน: run สร้าง record ครบ

## G1: Runner
- deterministic (seed เดิม = ผลเดิม)
- no NaN/Inf
- snapshot/replay ทำได้

## G2: Oracle/Validation
- inertial 1-body exact
- kepler 2-body analytic comparison
- dt convergence order = 2

## G3: Integration
- FE กด Save → DB มี run/telemetry
- FE กด Validate → diag record ครบ

## G4: UI
- checkbox metric → dock แสดงถูก
- overlay rules ไม่มั่ว (plot_group)
- Save/Export มีเฉพาะ output side
- Notes มี New Note + autosave

---

# APPENDIX: MIGRATION CHECKLIST

```
[ ] 1. Create shell/ directory
    [ ] LabShell.tsx
    [ ] AppTokens.ts

[ ] 2. Create registries/ directory
    [ ] roomRegistry.ts
    [ ] Move metricRegistry.ts from lib/registry/
    [ ] testRegistry.ts

[ ] 3. Create features/ directory
    [ ] features/metrics/ (move from components/lab/)
    [ ] features/panels/ (move from components/layout/)
    [ ] features/rooms/ (new)

[ ] 4. Update /lab/page.tsx to use LabShell

[ ] 5. Create RoomRouter
    [ ] Sim3DRoom (wrap WorldBackground)
    [ ] TestTerminalRoom (from test-lab logic)

[ ] 6. Merge /test-lab into /lab?room=testGates

[ ] 7. Clean up old files
```

---

**Document maintained by: Development Team**  
**Last updated: 2024-12-23**
