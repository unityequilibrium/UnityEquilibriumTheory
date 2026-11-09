"""
REFERENCES.py - 0.17 Mass Generation
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
        "Higgs_1964": "Peter Higgs - Broken Symmetries and the Masses of Gauge Bosons",
        "Englert_1964": "Englert & Brout - Broken Symmetry and the Mass of Gauge Vector Mesons",
        "YangMills_Gap": "Jaffe & Witten - Quantum Yang-Mills Theory (Millennium Prize)",
    },
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    # Common mappings
    mapping = {
        "Higgs_1964": "Broken Symmetries and the Masses of Gauge Bosons Higgs",
        "Englert_1964": "Broken Symmetry and the Mass of Gauge Vector Mesons",
        "YangMills_Gap": "Quantum Yang-Mills theory mass gap witten",
    }

    search_name = mapping.get(name, name)

    # Try generic search in PDF folder
    for pdf in REFERENCES["PDF_DIR"].glob("*.pdf"):
        if search_name.lower() in pdf.name.lower():
            return pdf

    return None


def list_references():
    """List all references."""
    print("=" * 60)
    print("0.17 Mass Generation - References")
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
