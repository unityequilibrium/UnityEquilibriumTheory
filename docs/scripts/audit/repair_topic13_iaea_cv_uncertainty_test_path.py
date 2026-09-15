from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "docs/core/test/test_topic13_iaea_cv_uncertainty_boundary.py"


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    text = text.replace(
        'ROOT = Path(__file__).resolve().parents[2]\nLANE = ROOT / "artifacts/t13_iaea_cv_uncertainty_boundary_audit.json"\nPACKAGE = ROOT.parent / (\n    "topics/0.13_Thermodynamic_Bridge/Data/03_Research/"\n',
        'ROOT = Path(__file__).resolve().parents[3]\nLANE = ROOT / "docs/core/07_artifacts/topic13/t13_iaea_cv_uncertainty_boundary_audit.json"\nPACKAGE = ROOT / (\n    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"\n',
    )
    text = text.replace(
        'FULL = ROOT.parent / (\n    "topics/0.13_Thermodynamic_Bridge/Result/artifacts/"\n',
        'FULL = ROOT / (\n    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"\n',
    )
    text = text.replace(
        'REGISTER = ROOT / "artifacts/uet_major_result_closure_register.json"',
        'REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"',
    )
    TARGET.write_text(text, encoding="utf-8")
    print("repaired Topic 13 uncertainty-boundary test paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
