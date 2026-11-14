"""
REFERENCES.py - 0.23 Unity Scale Link
=====================================
Central registry for external citations and analysis.
"""

from pathlib import Path

REF_DIR = Path(__file__).parent

REFERENCES = {
    "ANALYSIS": REF_DIR / "BIBLIOGRAPHY_ANALYSIS.md",
    "PDF_DIR": REF_DIR / "PDF_Downloads",
    "DATA_DIR": REF_DIR / "Data_Source",
    "KEY_PAPERS": {
        "Wilson_1975": "Kenneth Wilson - The Renormalization Group",
        "Mandelbrot_1967": "Benoit Mandelbrot - Fractal Scale Invariance",
        "West_1997": "Geoffrey West - Universal Scaling Laws",
    },
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    mapping = {
        "Wilson_1975": "The renormalization group Critical phenomena",
        "Mandelbrot_1967": "How Long Is the Coast of Britain",
        "West_1997": "origin of allometric scaling laws",
    }

    search_name = mapping.get(name, name)

    for pdf in REFERENCES["PDF_DIR"].glob("*.pdf"):
        if search_name.lower() in pdf.name.lower():
            return pdf

    return None


def list_references():
    """List all references."""
    print("=" * 60)
    print("0.23 Unity Scale Link - References")
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
