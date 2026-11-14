"""
REFERENCES.py - 0.18 Quantum Computing
=======================================
Central registry for external citations and analysis.
"""

from pathlib import Path

REF_DIR = Path(__file__).parent

REFERENCES = {
    "ANALYSIS": REF_DIR / "BIBLIOGRAPHY_ANALYSIS.md",
    "PDF_DIR": REF_DIR / "PDF_Downloads",
    "DATA_DIR": REF_DIR / "Data_Source",
    "KEY_PAPERS": {
        "NielsenChuang": "Nielsen & Chuang - Quantum Computation and Information",
        "Shor_1994": "Peter Shor - Polynomial-Time Factoring",
        "Grover_1996": "Lov Grover - Fast Database Search",
        "Devoret_2013": "Devoret & Schoelkopf - Superconducting Circuits Outlook",
    },
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    mapping = {
        "Shor_1994": "Polynomial-Time Algorithms for Prime",
        "Grover_1996": "fast quantum mechanical algorithm for database",
        "Devoret_2013": "Superconducting Circuits for Quantum Information",
    }

    search_name = mapping.get(name, name)

    for pdf in REFERENCES["PDF_DIR"].glob("*.pdf"):
        if search_name.lower() in pdf.name.lower():
            return pdf

    return None


def list_references():
    """List all references."""
    print("=" * 60)
    print("0.18 Quantum Computing - References")
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
