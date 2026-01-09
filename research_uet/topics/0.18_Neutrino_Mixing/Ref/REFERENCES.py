"""
References: Neutrino Mixing
===========================

DOIs for all data sources used in this topic.
"""

REFERENCES = {
    "pmns_matrix": [
        {
            "title": "NuFIT 5.2: Updated global analysis of oscillation parameters",
            "authors": "Esteban, I. et al.",
            "journal": "arXiv",
            "year": 2024,
            "doi": "10.1007/JHEP09(2020)178",
            "data": "θ₁₂, θ₂₃, θ₁₃, δ_CP",
            "url": "http://www.nu-fit.org/",
            "source": "NuFIT Global Analysis",
        },
        {
            "title": "Review of Particle Physics",
            "authors": "Particle Data Group",
            "journal": "Prog. Theor. Exp. Phys. 2024",
            "year": 2024,
            "doi": "10.1093/ptep/ptac097",
            "data": "Neutrino mixing parameters",
            "source": "PDG 2024",
        },
    ],
    "mass_differences": [
        {
            "title": "Constraint on Neutrino Masses",
            "authors": "KATRIN Collaboration",
            "journal": "Nature Physics 18, 160",
            "year": 2022,
            "doi": "10.1038/s41567-021-01463-1",
            "data": "m_ν < 0.8 eV",
        },
    ],
}

DATA_FILES = {
    "Code/mixing_angles/test_pmns_full.py": {
        "source": "NuFIT 5.2, PDG 2024",
        "doi": "10.1093/ptep/ptac097",
        "verified": True,
    },
}


def list_references():
    """List all references."""
    print("=" * 60)
    print("0.18 NEUTRINO MIXING REFERENCES")
    print("=" * 60)
    for category, refs in REFERENCES.items():
        print(f"\n{category.upper()}:")
        for ref in refs:
            print(f"  [{ref['year']}] {ref['title']}")
            print(f"         DOI: {ref['doi']}")


if __name__ == "__main__":
    list_references()
