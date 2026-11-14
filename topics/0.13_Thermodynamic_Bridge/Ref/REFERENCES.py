"""
REFERENCES.py - 0.13 Thermodynamic Bridge
=========================================
Central registry for external citations and analysis.
"""

from pathlib import Path

REF_DIR = Path(__file__).parent

REFERENCES = {
    "ANALYSIS": REF_DIR / "BIBLIOGRAPHY_ANALYSIS.md",
    "PDF_DIR": REF_DIR / "PDF_Downloads",
    "DATA_DIR": REF_DIR / "Data_Source",
    "KEY_PAPERS": {
        "Boltzmann_1877": "L. Boltzmann - Probabilistic basis of entropy",
        "Landauer_1961": "R. Landauer - Irreversibility and Heat Generation",
        "Clausius_1865": "R. Clausius - Mechanical Heat Theory and Entropy",
        "Shannon_1948": "C. Shannon - Mathematical Theory of Communication",
    },
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    # Common mappings
    mapping = {
        "Boltzmann_1877": "Boltzmann entropy probability",
        "Landauer_1961": "Irreversibility and Heat Generation",
        "Clausius_1865": "Second law of thermodynamics Clausius",
        "Shannon_1948": "Shannon information theory entropy",
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
    print("0.13 Thermodynamic Bridge - References")
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
