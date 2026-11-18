"""Physics tests for the T021 method (lighting succession, stage 1 of test D, topic 0.25).

docs/STANDARD.md section 6:
- identity: lumens per watt and lumen-hours per 1,000 Btu in the transcribed table agree through
  1,000 Btu = 293.07 Wh (checks the transcription, not the hypothesis)
- identity: labor hours = price / wage wherever both are legible (checks the transcription)
- known limits of the classifier: a successor that is better in both resources dominates, worse in both is
  WORSE_BOTH, one up and one down is TRADE_OFF, and differences inside the tolerance are ties
These tests do not compare successors with incumbents; that comparison runs only after author approval.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

pytestmark = pytest.mark.physics

_PATH = Path(__file__).resolve().parents[2] / "03_lanes" / "persistence" / "t021_lighting_succession.py"
_spec = importlib.util.spec_from_file_location("t021_lighting_succession", _PATH)
t021 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(t021)


def test_efficiency_columns_obey_btu_identity() -> None:
    rows = t021.load_rows()
    for rid, r in rows.items():
        lpw, per_btu = float(r["lumens_per_watt"]), float(r["lmh_per_1000btu"])
        expected = lpw * 1000.0 * t021.BTU_WH
        assert abs(per_btu - expected) / expected < 0.03, rid


def test_labor_price_equals_price_over_wage() -> None:
    rows = t021.load_rows()
    checked = 0
    for rid, r in rows.items():
        try:
            wage, price, labor = (float(r[k]) for k in
                                  ("wage_cents_per_hour", "price_cents_per_1000lmh", "labor_hours_per_1000lmh"))
        except ValueError:
            continue
        assert abs(price / wage - labor) / labor < 0.02, rid
        checked += 1
    assert checked >= 25


def test_every_pair_row_has_both_resources() -> None:
    rows = t021.load_rows()
    for old, new, _ in t021.PAIRS:
        for rid in (old, new):
            e, t = t021.resources(rows[rid])
            assert e > 0 and t > 0


@pytest.mark.parametrize(
    "e_new,t_new,expected",
    [(0.5, 0.5, "DOMINATES"), (0.5, 1.0, "DOMINATES"), (2.0, 2.0, "WORSE_BOTH"),
     (0.5, 2.0, "TRADE_OFF"), (2.0, 0.5, "TRADE_OFF"), (1.03, 0.97, "TIE")],
)
def test_classifier_limits(e_new: float, t_new: float, expected: str) -> None:
    assert t021.classify(1.0, 1.0, e_new, t_new) == expected
