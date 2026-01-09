"""
References: Gravity & General Relativity
=========================================

DOIs for all data sources used in this topic.
"""

REFERENCES = {
    "equivalence_principle": [
        {
            "title": "Test of the equivalence principle using a rotating torsion balance",
            "authors": "Schlamminger, S., Choi, K.-Y., Wagner, T.A., Gundlach, J.H. & Adelberger, E.G.",
            "journal": "Phys. Rev. Lett. 100, 041101",
            "year": 2008,
            "doi": "10.1103/PhysRevLett.100.041101",
            "data": "η(Earth) = (0.3 ± 1.8) × 10⁻¹³",
            "source": "Eöt-Wash Group, University of Washington",
        },
        {
            "title": "MICROSCOPE Mission: Final Results of the Test of the Equivalence Principle",
            "authors": "MICROSCOPE Collaboration",
            "journal": "Phys. Rev. Lett. 129, 121102",
            "year": 2022,
            "doi": "10.1103/PhysRevLett.129.121102",
            "data": "η = (−1.5 ± 2.7) × 10⁻¹⁵",
            "source": "CNES/ONERA",
        },
    ],
    "fundamental_constants": [
        {
            "title": "CODATA recommended values of the fundamental physical constants: 2018",
            "authors": "Tiesinga, E., Mohr, P.J., Newell, D.B. & Taylor, B.N.",
            "journal": "Rev. Mod. Phys. 93, 025010",
            "year": 2021,
            "doi": "10.1103/RevModPhys.93.025010",
            "data": "G, c, ℏ, Planck units",
            "source": "NIST",
        },
    ],
}

DATA_FILES = {
    "Code/equivalence/test_equivalence_principle.py": {
        "source": "Eöt-Wash, MICROSCOPE",
        "doi": "10.1103/PhysRevLett.100.041101",
        "verified": True,
    },
    "Code/gravitational_constant/test_gravitational_constant.py": {
        "source": "CODATA 2018",
        "doi": "10.1103/RevModPhys.93.025010",
        "verified": True,
    },
}


def list_references():
    """List all references."""
    print("=" * 60)
    print("0.19 GRAVITY/GR REFERENCES")
    print("=" * 60)
    for category, refs in REFERENCES.items():
        print(f"\n{category.upper()}:")
        for ref in refs:
            print(f"  [{ref['year']}] {ref['title']}")
            print(f"         DOI: {ref['doi']}")


if __name__ == "__main__":
    list_references()
