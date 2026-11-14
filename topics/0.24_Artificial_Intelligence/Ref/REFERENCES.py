"""
REFERENCES.py - 0.24 AI & Alignment
====================================
Central registry for external citations and analysis.
"""

from pathlib import Path

REF_DIR = Path(__file__).parent

REFERENCES = {
    "ANALYSIS": REF_DIR / "BIBLIOGRAPHY_ANALYSIS.md",
    "PDF_DIR": REF_DIR / "PDF_Downloads",
    "DATA_DIR": REF_DIR / "Data_Source",
    "KEY_PAPERS": {
        "Vaswani_2017": "Vaswani et al. - Attention Is All You Need (Transformers)",
        "Kaplan_2020": "Kaplan et al. - Scaling Laws for Neural Language Models",
        "Amodei_2016": "Amodei et al. - Concrete Problems in AI Safety",
        "Bostrom_2014": "Nick Bostrom - Superintelligence",
    },
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    mapping = {
        "Vaswani_2017": "Attention Is All You Need",
        "Kaplan_2020": "Scaling Laws for Neural Language Models",
        "Amodei_2016": "Concrete Problems in AI Safety",
    }

    search_name = mapping.get(name, name)

    for pdf in REFERENCES["PDF_DIR"].glob("*.pdf"):
        if search_name.lower() in pdf.name.lower():
            return pdf

    return None


def list_references():
    """List all references."""
    print("=" * 60)
    print("0.24 AI & Alignment - References")
    print("=" * 60)
    print(f"Analysis: {REFERENCES['ANALYSIS']}")
    print(f"Pdf Dir: {REFERENCES['PDF_DIR']}\n")

    print("Key Papers:")
    for key, desc in REFERENCES["KEY_PAPERS"].items():
        ref_path = get_ref_path(key)
        status = "✅ FOUND" if ref_path else "❌ MISSING (Run Downloader)"
        print(f"  * {key}: {desc} [{status}]")


if __name__ == "__main__":
    list_references()
