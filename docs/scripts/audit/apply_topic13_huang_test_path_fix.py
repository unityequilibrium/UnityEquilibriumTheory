from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "docs/core/test/test_topic13_huang_2023_supplementary_payload_boundary.py"

text = PATH.read_text(encoding="utf-8")
text = text.replace(
    'ROOT = Path(__file__).resolve().parents[2]\nARTIFACT = ROOT / "artifacts/t13_huang_2023_supplementary_payload_boundary_audit.json"',
    'ROOT = Path(__file__).resolve().parents[3]\nARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_huang_2023_supplementary_payload_boundary_audit.json"',
)
PATH.write_text(text, encoding="utf-8")
print(PATH)
