"""
REFERENCES.py - 0.4 Superconductivity & Superfluids
===================================================
Central registry for external citations and analysis.
"""

from pathlib import Path

REF_DIR = Path(__file__).parent

REFERENCES = {
    "ANALYSIS": REF_DIR / "BIBLIOGRAPHY_ANALYSIS.md",
    "PDF_DIR": REF_DIR / "PDF_Downloads",
    "DATA_DIR": REF_DIR / "Data_Source",
    "KEY_PAPERS": {
        "BCS_1957": "Bardeen, Cooper, Schrieffer (1957) - BCS Theory",
        "GL_1950": "Ginzburg-Landau (1950) - Order Parameter",
        "Landau_1941": "Landau (1941) - Superfluid Helium",
    },
    "BCS_Metadata": {
        "title": "Theory of Superconductivity",
        "authors": ["Bardeen", "Cooper", "Schrieffer"],
        "journal": "Physical Review",
        "year": 1957,
        "doi": "10.1103/PhysRev.108.1175",
    },
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    # Common mappings
    mapping = {
        "BCS_1957": "Theory of Superconductivity",
        "GL_1950": "Ginzburg Landau",
        "Landau_1941": "Theory of the Superfluidity",
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
    print("0.4 Superconductivity & Superfluids - References")
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
