"""
REFERENCES.py - 0.16 Heavy Nuclei
===================================
Central registry for external citations and analysis.
"""

from pathlib import Path

REF_DIR = Path(__file__).parent

REFERENCES = {
    "ANALYSIS": REF_DIR / "BIBLIOGRAPHY_ANALYSIS.md",
    "PDF_DIR": REF_DIR / "PDF_Downloads",
    "DATA_DIR": REF_DIR / "Data_Source",
    "KEY_PAPERS": {
        "Oganessian_2015": "Yu. Oganessian - Superheavy Element Research",
        "Mayer_1949": "M. G. Mayer - Nuclear Shell Model (Magic Numbers)",
        "Gamow_1928": "G. Gamow - Alpha Decay Quantum Theory",
        "Hofmann_2000": "S. Hofmann - Production of Superheavy Elements",
    },
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    # Common mappings
    mapping = {
        "Oganessian_2015": "Oganessian superheavy element research",
        "Mayer_1949": "Maria Goeppert Mayer nuclear shell model",
        "Gamow_1928": "George Gamow alpha decay quantum theory",
        "Hofmann_2000": "Production of Superheavy Elements",
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
    print("0.16 Heavy Nuclei - References")
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
