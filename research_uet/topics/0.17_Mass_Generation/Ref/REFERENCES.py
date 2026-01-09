"""
References: Mass Generation
===========================

DOIs for all data sources used in this topic.
"""

REFERENCES = {
    "lepton_masses": [
        {
            "title": "Review of Particle Physics",
            "authors": "Particle Data Group",
            "journal": "Prog. Theor. Exp. Phys. 2024, 083C01",
            "year": 2024,
            "doi": "10.1093/ptep/ptac097",
            "data": "Electron, muon, tau masses",
            "source": "PDG 2024",
        },
    ],
    "higgs_mechanism": [
        {
            "title": "Observation of a new particle (Higgs)",
            "authors": "CMS Collaboration",
            "journal": "Phys. Lett. B 716, 30",
            "year": 2012,
            "doi": "10.1016/j.physletb.2012.08.021",
            "data": "Higgs mass 125.09 GeV",
        },
    ],
}

DATA_FILES = {
    "Code/lepton_mass/test_lepton_mass.py": {
        "source": "PDG 2024",
        "doi": "10.1093/ptep/ptac097",
        "verified": True,
    },
}


def list_references():
    """List all references."""
    print("=" * 60)
    print("0.17 MASS GENERATION REFERENCES")
    print("=" * 60)
    for category, refs in REFERENCES.items():
        print(f"\n{category.upper()}:")
        for ref in refs:
            print(f"  [{ref['year']}] {ref['title']}")
            print(f"         DOI: {ref['doi']}")


if __name__ == "__main__":
    list_references()
