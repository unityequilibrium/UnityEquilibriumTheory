"""
Biophysics References (UET Topic 0.22)
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
        "Schrodinger": "What is Life? (1944)",
        "England_2013": "J. England - Statistical physics of self-replication",
        "Lane_2010": "Lane & Martin - Energetics of genome complexity",
        "Friston_2010": "K. Friston - The Free Energy Principle",
        "Kauffman_1995": "S. Kauffman - Self-Organization laws",
        "Miller_1953": "S. Miller - Production of amino acids under primitive earth conditions",
    },
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    mapping = {
        "Schrodinger": "What is Life",
        "England_2013": "Statistical physics of self-replication",
        "Lane_2010": "Energetics of genome complexity",
        "Friston_2010": "The free-energy principle",
        "Kauffman_1995": "Self-Organization laws"
    }
    
    search_name = mapping.get(name, name)
    
    for pdf in REFERENCES["PDF_DIR"].glob("*.pdf"):
        if search_name.lower() in pdf.name.lower():
            return pdf
            
    return None
