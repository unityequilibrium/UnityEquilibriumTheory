"""
REFERENCES.py - 0.2 Black Hole Physics
========================================
Central registry for external citations and analysis.
"""

from pathlib import Path

REF_DIR = Path(__file__).parent

REFERENCES = {
    "ANALYSIS": REF_DIR / "BIBLIOGRAPHY_ANALYSIS.md",
    "PDF_DIR": REF_DIR / "PDF_Downloads",
    "DATA_DIR": REF_DIR / "Data_Source",
    "KEY_PAPERS": {
        "Jacobson": "Thermodynamics of Spacetime (1995)",
        "Farrah": "Cosmological Coupling of Black Holes (2023)",
        "EHT": "M87 Event Horizon Shadow (2019)",
    },
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    # Common mappings
    mapping = {
        "Jacobson": "Thermodynamics of Spacetime The Einstein equation",
        "Farrah": "Observational Evidence for Cosmological Coupling",
        "EHT": "First M87 Event Horizon Telescope Results I The",
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
    print("0.2 Black Hole Physics - References")
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
