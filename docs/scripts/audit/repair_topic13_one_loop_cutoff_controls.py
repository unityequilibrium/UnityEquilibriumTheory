"""Expose explicit thermal cutoff controls for convergence auditing."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
COMPARATOR = ROOT / "docs/core/02_equations/o2/standard_o2_finite_temperature_comparator.py"
ONE_LOOP = ROOT / "docs/core/02_equations/o2/uet_o2_one_loop_normal_branch.py"


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"{label} not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    replace_once(
        COMPARATOR,
        "    quadrature_order: int = 192,\n) -> StandardO2ThermalNormalState:",
        "    quadrature_order: int = 192,\n    cutoff_factor: float = 50.0,\n) -> StandardO2ThermalNormalState:",
        "standard comparator signature",
    )
    replace_once(
        COMPARATOR,
        '    temperature = _positive_finite(temperature, "temperature")\n',
        '    temperature = _positive_finite(temperature, "temperature")\n    cutoff_factor = _positive_finite(cutoff_factor, "cutoff_factor")\n',
        "standard comparator cutoff validation",
    )
    replace_once(
        COMPARATOR,
        "    cutoff = max(50.0 * temperature, 50.0 * mass, 50.0 * abs(chemical_potential), 1.0)\n",
        "    cutoff = max(cutoff_factor * temperature, cutoff_factor * mass, cutoff_factor * abs(chemical_potential), 1.0)\n",
        "standard comparator cutoff use",
    )
    replace_once(
        ONE_LOOP,
        "    quadrature_order: int = 192,\n) -> UETO2OneLoopNormalState:",
        "    quadrature_order: int = 192,\n    cutoff_factor: float = 50.0,\n) -> UETO2OneLoopNormalState:",
        "one-loop signature",
    )
    replace_once(
        ONE_LOOP,
        "        quadrature_order=quadrature_order,\n    )\n",
        "        quadrature_order=quadrature_order,\n        cutoff_factor=cutoff_factor,\n    )\n",
        "one-loop cutoff forwarding",
    )
    print("PATCHED_T13_ONE_LOOP_CUTOFF_CONTROLS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
