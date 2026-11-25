# Literature map: what mainstream physiology already knows about fasting, and where waves D14, D15 and D20 stand

Written 2026-11-25 at the author's request ("connect to the mainstream academic knowledge; do not only choose our
explanation and pick data to support it"). Status: review, no new claim. Sources below were read for this map;
quotations are short and attributed, equations are restated in our notation.

## สรุปภาษาไทย

- วงการสรีรวิทยามีแบบจำลองการลดน้ำหนักระหว่างอดอาหารที่ทดสอบกับข้อมูลจริงมาแล้ว (Hall; Chow & Hall) แยกร่างกายเป็น
  ไขมัน F กับเนื้อเยื่อไม่ใช่ไขมัน L การใช้พลังงานขึ้นกับทั้งสองส่วน และสัดส่วนที่เสียไปจากแต่ละส่วนขึ้นกับปริมาณไขมันที่มี (Forbes)
- สามเรื่องที่เราทดสอบแล้วตกหรือสรุปไม่ได้ วงการอธิบายไว้แล้วทั้งหมด: (1) การลดน้ำหนักช้าลง (การใช้พลังงานลดตามมวลที่ลด
  และ adaptive thermogenesis), (2) โปรตีนสลายลดลงในช่วงแรก (คีโตนแทนกลูโคสในสมอง, Cahill), (3) แต่ละคนต่างกัน
  (คนที่มีไขมันมากเสียเนื้อน้อยกว่าและพลังงานต่อกิโลกรัมที่เสียสูงกว่า)
- D14 ขัดกับวงการตั้งแต่ต้น D15 มีโครงสร้างสองส่วนเหมือนวงการแต่จับคู่ผิด (วงการ: ไขมันกับเนื้อถูกใช้ร่วมกันตามสัดส่วน Forbes
  ไม่ใช่ "เนื้อกินไขมัน") D20 เป็นเส้นโค้งที่ AI เลือกเอง ซึ่งวงการแทนด้วยกลไกที่วัดได้
- ทางที่ถูก: เอาแบบจำลองของวงการ (พารามิเตอร์จากงานตีพิมพ์ ไม่ฟิต) มาเป็นเกณฑ์อ้างอิง แล้วดูว่าชั้น 3 ของ UET ประกอบให้ได้
  แบบจำลองนั้นหรือไม่ และเพิ่มอะไรได้บ้าง

## 1. Established knowledge

### 1.1 Fuel sequence and protein sparing (Cahill; Owen)

- Source: G. F. Cahill Jr, "Fuel metabolism in starvation", Annu. Rev. Nutr. 26, 1-22 (2006); summarised in
  C. J. Rebello et al., "From starvation to time-restricted eating: a review of fasting physiology", Int. J. Obes. 49,
  43 (2025), PMC12455479.
- Glycogen carries the first day or two; then gluconeogenesis from protein; within days ketone bodies (from fat)
  replace glucose as the brain's main fuel. The review states that only about half of body protein can be mobilised
  before death, so "a reduction in protein catabolism during prolonged starvation ... is necessary for survival", and
  that "a decline in urinary nitrogen provides evidence that hepatic gluconeogenesis is diminished".
- Ketone concentrations rise for about three weeks and then reach a steady state (review, citing Owen et al.).
- Consequence for us: protein loss falls early in a fast (T034's observed trend) because the brain switches fuel,
  not because protein is a "structure" that feeds on fat.

### 1.2 Energy-balance models with fat and lean compartments (Hall; Chow and Hall)

- Sources: C. C. Chow and K. D. Hall, "The dynamics of human body weight change", PLoS Comput. Biol. 4, e1000045
  (2008), PMC2266991; K. D. Hall, "Predicting metabolic adaptation, body weight change, and energy intake in humans",
  Am. J. Physiol. Endocrinol. Metab. 298, E449 (2010), PMC2838532; K. D. Hall, "Computational model of in vivo human
  energy metabolism during semistarvation and refeeding", Am. J. Physiol. Endocrinol. Metab. 291, E23 (2006).
- Two-compartment form (Chow and Hall): fat mass F and lean mass L change as
      rho_F dF/dt = (1 - p)(I - E),   rho_L dL/dt = p (I - E),
  with rho_L = 7.6 MJ/kg (lean tissue with its water), rho_F about 39.5 MJ/kg (9.44 kcal/g in Hall 2010), intake I,
  expenditure E, and p the fraction of the imbalance taken from lean tissue.
- Forbes partition (Chow and Hall Eq. 14, from Forbes): F = D exp(L / 10.4 kg), so along the path dL/dF = 10.4/F and
      p = dL/dM = 10.4 / (10.4 + F)   (F in kg).
  A person with 5 kg of fat loses about two thirds of each kilogram as lean tissue; one with 40 kg about one fifth.
  Chow and Hall: weight-loss data find "more fat lost if the body fat is initially higher".
- Expenditure depends on composition, for example E = 0.14 L + 0.05 F + 1.55 MJ/day (Chow and Hall, from cross-sectional
  resting data plus sedentary activity); Hall 2010 uses organ-specific rates (adipose 4.5 kcal kg^-1 day^-1, lean 19,
  brain 240 for 1.4 kg).
- Adaptive thermogenesis: "the dependence of energy expenditure on F and L for an individual is steeper than for the
  population" (Chow and Hall, citing Leibel et al. 1995); Hall 2010 adds an adaptive term fitted to the Minnesota
  semistarvation experiment (Keys et al. 1950).
- Validation: Hall 2006/2010 fitted to the Minnesota study and tested on other diet studies; the models are
  standard in the field (NIH Body Weight Planner).

### 1.3 Animal fasts (Le Maho, Cherel, Robin)

- Birds and seals show three phases: short phase I (glycogen, falling specific loss), long phase II (fat, low and
  steady specific mass loss with protein spared), phase III (fat near a threshold, protein loss and mass loss rise,
  refeeding drive). Source read: abstract of Robin et al., Am. J. Physiol. 254, R61 (1988); full text not open.

## 2. What these models imply for the quantities we tested

- Slowing of mass loss in a total fast (I = 0): E falls as L and F fall, and adaptive thermogenesis lowers it further,
  so kg/day falls; in mass-specific terms the effect depends on composition through p and rho_eff = p rho_L + (1-p) rho_F.
- Body-to-body differences: through F, p differs between bodies, so the time course differs. A single curvature
  parameter shared by different bodies (D20's beta) is not expected by these models.
- Protein: high early, falling as ketosis sets in (phase II), rising again in phase III when F is small (p large).

## 3. Where waves D14, D15 and D20 stand against this

| wave | our form | mainstream counterpart | verdict |
|---|---|---|---|
| D14 (C_L3_OPENNESS_LAYER3) | one pool, constant leak, exponential | E depends on L, F and adaptation; not a constant fraction of mass | in conflict from the start; FAILED in T030 |
| D15 (C_L3_AFTER_CLOSING) | pool R feeding structures n | two compartments drawn together in the Forbes ratio; lean is not built from fat in a fast | right number of compartments, wrong coupling; T034 trend against |
| D20 (C_L3_SURVIVAL_BURN) | P = P0 (R/R0)^beta, one beta for all | composition-dependent p and E, plus measured adaptive thermogenesis | an AI curve where a mechanistic model exists; FAILED in T036 |

The tests were run honestly, but the forms were chosen before the field's models were read. The failures repeat,
less precisely, what Hall, Chow and Forbes already showed.

## 4. What UET can do here (synthesis, not novelty)

- Layer 3's language (store F, burn P, threshold R*) maps onto the energy-balance model: store = F + L with
  energy densities, burn = E(F, L) with adaptation, threshold = the fat level where phase III starts. The question
  for UET is whether its layer-3 composition reproduces the Chow-Hall equations without new parameters, and whether
  the same composition then carries to another field (author's path: one law across scales).
- A fair benchmark before any new UET form: run the published Chow-Hall model with literature parameters (no fit)
  on the fasts we already hold (Benedict 1915, L. and Table 2). This is a sandbox check of the mainstream model on
  seen data, not a test of UET, and it must not be used to tune a UET form afterwards.
- Only after that: a Test Card on unseen data where the UET composition and the mainstream model could differ.

## 5. Sources read for this map

- Chow and Hall 2008, PLoS Comput. Biol. 4, e1000045 (PMC2266991): equations, Forbes p, E(F, L), adaptive thermogenesis.
- Hall 2010, Am. J. Physiol. Endocrinol. Metab. 298, E449 (PMC2838532): macronutrient balance, parameter tables, Minnesota fit.
- Rebello et al. 2025, Int. J. Obes. (PMC12455479): fuel sequence, protein sparing, ketone kinetics.
- Cahill 2006, Annu. Rev. Nutr. 26, 1; Hall 2007, Br. J. Nutr. 97, 1059 (Forbes revisited); Hall 2006, Am. J. Physiol.
  Endocrinol. Metab. 291, E23; Keys et al. 1950; Leibel et al. 1995: cited through the papers above, not read in full here.
