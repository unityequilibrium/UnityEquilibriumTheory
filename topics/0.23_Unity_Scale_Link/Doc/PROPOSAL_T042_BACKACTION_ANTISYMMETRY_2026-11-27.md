# Proposal T042: red-blue antisymmetry of dynamical backaction (optomechanics lane)

Drafted by Claude on 2026-11-27. Status: draft for the author's approval. Claim: `C_O8_OPTOMECHANICS_LANE`.

## Question

The single coupling of the portal forces the layer-2 friction on the red side to equal the layer-3 capture on the
blue side: Gamma_opt(-Delta) = -Gamma_opt(+Delta) at the same power. Do two published devices show it?

## Why this test (STRESS_13)

It is the only junction where the UET chain layer 1 -> 2 -> 3 meets data with a measured coupling. It tests the
synthesis (one coupling across two layers), not new physics: standard optomechanics predicts the same.

## Data

- Arcizet et al. 2006, Fig. 4: damping ratio versus detuning for five powers (arXiv figure, kept local).
- Benevides et al. 2017, Fig. 3a: linewidth modification versus detuning (CC BY 4.0).
Both downloaded with the author's permission; only masked captions read so far. A table of both the cooling rate and
the threshold was not found (STRESS_13 section 7), which is why figures are used.

## Method and criteria

Pixel-based reading fixed in the script; PASS if |R| <= 0.15 in both figures, FAIL if |R| > 0.35 in either,
INCONCLUSIVE otherwise. The calibration values are entered after approval and before computing R.

## Risks

Photothermal forces, detuning offsets and the static shift can break the antisymmetry; the Benevides figure is small
(675 x 348 for the whole figure), so few points may be readable.
