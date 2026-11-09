"""
REFERENCES.py - 0.9 Quantum Nonlocality
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
        "EPR_1935": "Einstein et al. (1935) - EPR Paradox",
        "Bell_1964": "John Bell (1964) - Bell's Inequality",
        "Aspect_1982": "Alain Aspect (1982) - Bell Test Evidence",
        "Hensen_2015": "Hensen et al. (2015) - Loophole-free Bell Test",
    },
    "Internal_Refs": {"Hensen_PDF": "Quantum_Hensen2015_Bell.pdf"},
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    # Check internal first
    if name == "Hensen":
        path = REFERENCES["PDF_DIR"] / REFERENCES["Internal_Refs"]["Hensen_PDF"]
        if path.exists():
            return path

    # Common mappings
    mapping = {
        "EPR_1935": "Can Quantum-Mechanical Description of Physical Reality",
        "Bell_1964": "On the Einstein Podolsky Rosen paradox",
        "Aspect_1982": "Experimental Test of Bell's Inequalities",
        "Hensen_2015": "Loophole-free Bell inequality violation",
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
    print("0.9 Quantum Nonlocality - References")
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
