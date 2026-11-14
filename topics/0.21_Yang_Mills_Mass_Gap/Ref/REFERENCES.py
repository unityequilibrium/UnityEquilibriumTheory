"""
REFERENCES.py - 0.21 Yang-Mills & Mass Gap
==========================================
Central registry for external citations and analysis.
"""

from pathlib import Path

REF_DIR = Path(__file__).parent

REFERENCES = {
    "ANALYSIS": REF_DIR / "BIBLIOGRAPHY_ANALYSIS.md",
    "PDF_DIR": REF_DIR / "PDF_Downloads",
    "DATA_DIR": REF_DIR / "Data_Source",
    "KEY_PAPERS": {
        "YangMills_1954": "Yang & Mills - Conservation of Isotopic Spin",
        "Witten_2000": "Jaffe & Witten - Quantum Yang-Mills Theory (Millennium Prize)",
        "tHooft_1972": "Gerard 't Hooft - Renormalization of gauge fields",
    },
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    mapping = {
        "YangMills_1954": "Yang-Mills Conservation Isotopic Spin",
        "Witten_2000": "Quantum Yang-Mills Theory millennium prize",
        "tHooft_1972": "Regularization and renormalization of gauge fields",
    }

    search_name = mapping.get(name, name)

    for pdf in REFERENCES["PDF_DIR"].glob("*.pdf"):
        if search_name.lower() in pdf.name.lower():
            return pdf

    return None


def list_references():
    """List all references."""
    print("=" * 60)
    print("0.21 Yang-Mills & Mass Gap - References")
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
