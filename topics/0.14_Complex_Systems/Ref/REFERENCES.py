"""
REFERENCES.py - 0.14 Complex Systems
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
        "Anderson_1972": "P.W. Anderson - More is Different (Emergence)",
        "Barabasi_1999": "Barabasi & Albert - Scaling in Random Networks",
        "Prigogine_1977": "Nicolis & Prigogine - Self-Organization in Non-Equilibrium Systems",
        "Granger_1969": "C.W.J. Granger - Investigating Causal Relations",
    },
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    # Common mappings
    mapping = {
        "Anderson_1972": "More is different science 1972",
        "Barabasi_1999": "Emergence of Scaling in Random Networks",
        "Prigogine_1977": "Self-Organization in Non-Equilibrium Systems",
        "Granger_1969": "Investigating Causal Relations by Econometric Models",
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
    print("0.14 Complex Systems - References")
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
