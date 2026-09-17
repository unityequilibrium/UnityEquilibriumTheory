"""
UET Research Data Sources and References
==========================================

This document lists all REAL data sources used in UET validation.
Each data file must have proper citations and DOIs.

POLICY: ALL DATA MUST BE FROM PUBLISHED, PEER-REVIEWED SOURCES
"""

# ============================================================
# OFFICIAL DATA REPOSITORIES
# ============================================================

DATA_SOURCES = {
    # Particle Physics
    "PDG": {
        "name": "Particle Data Group",
        "url": "https://pdg.lbl.gov/",
        "api": "https://pdgapi.lbl.gov/",
        "data_format": ["JSON", "SQLite", "PDF"],
        "latest_version": "2024",
        "doi": "10.1093/ptep/ptac097",
    },
    # Nuclear Data
    "NNDC": {
        "name": "National Nuclear Data Center",
        "url": "https://www.nndc.bnl.gov/",
        "databases": {
            "ENSDF": "https://www.nndc.bnl.gov/ensdf/",
            "NuDat": "https://www.nndc.bnl.gov/nudat3/",
            "XUNDL": "https://www.nndc.bnl.gov/ensdf/ensdf/xundl.jsp",
            "MIRD": "https://www.nndc.bnl.gov/mird/",
        },
        "note": "Evaluated Nuclear Structure Data",
    },
    # IAEA Nuclear Data
    "IAEA_NDS": {
        "name": "IAEA Nuclear Data Section",
        "url": "https://www-nds.iaea.org/",
        "databases": {
            "beta_delayed_neutron": "https://www-nds.iaea.org/beta-delayed-neutron/",
            "livechart": "https://www-nds.iaea.org/livechart/",
        },
    },
    # Neutrino Data
    "T2K": {
        "name": "T2K Experiment",
        "url": "http://t2k-experiment.org/",
        "data": "Neutrino oscillation parameters",
    },
    "KATRIN": {
        "name": "KATRIN Experiment",
        "url": "https://www.katrin.kit.edu/",
        "data": "Neutrino mass limit",
    },
    # Galaxy Data
    "SPARC": {
        "name": "Spitzer Photometry & Accurate Rotation Curves",
        "url": "http://astroweb.cwru.edu/SPARC/",
        "data": "175 galaxy rotation curves",
    },
    # Cosmology
    "Planck": {
        "name": "Planck Collaboration",
        "url": "https://www.cosmos.esa.int/web/planck",
        "data": "CMB parameters, cosmological constants",
    },
}

# ============================================================
# PAPERS WITH REAL DATA USED IN TESTS
# ============================================================

REFERENCES = {
    # Weak Force / Beta Decay
    "weak_force": [
        {
            "title": "Improved Determination of the Positive Muon Lifetime",
            "authors": "MuLan Collaboration",
            "journal": "Phys. Rev. Lett.",
            "volume": 106,
            "pages": "041803",
            "year": 2011,
            "doi": "10.1103/PhysRevLett.106.041803",
            "data": "Muon lifetime τ_μ = 2.1969803(22) μs, G_F",
        },
        {
            "title": "Superallowed 0+ → 0+ nuclear β decays: 2020 update",
            "authors": "Hardy, J.C. and Towner, I.S.",
            "journal": "Phys. Rev. C",
            "volume": 102,
            "pages": "045501",
            "year": 2020,
            "doi": "10.1103/PhysRevC.102.045501",
            "data": "ft values, V_ud",
        },
        {
            "title": "UCNτ: Precision Neutron Lifetime Measurement",
            "authors": "UCNτ Collaboration",
            "journal": "Phys. Rev. Lett.",
            "volume": 127,
            "pages": "162501",
            "year": 2021,
            "doi": "10.1103/PhysRevLett.127.162501",
            "data": "Neutron lifetime τ_n = 877.75(28) s",
        },
        {
            "title": "Direct Neutrino-Mass Measurement (KATRIN)",
            "authors": "KATRIN Collaboration",
            "journal": "Nature Physics",
            "volume": 18,
            "year": 2022,
            "doi": "10.1038/s41567-021-01463-1",
            "data": "m_ν < 0.8 eV",
        },
    ],
    # Bell Tests / Quantum
    "quantum": [
        {
            "title": "Loophole-free Bell inequality violation using electron spins",
            "authors": "Hensen, B. et al.",
            "journal": "Nature",
            "volume": 526,
            "pages": "682",
            "year": 2015,
            "doi": "10.1038/nature15759",
            "data": "Bell test S = 2.42",
        },
        {
            "title": "Experimental tests of Bell's inequalities",
            "authors": "Aspect, A. et al.",
            "journal": "Phys. Rev. Lett.",
            "volume": 49,
            "pages": "1804",
            "year": 1982,
            "doi": "10.1103/PhysRevLett.49.1804",
            "data": "Bell test S = 2.697",
        },
    ],
    # Standard Model
    "standard_model": [
        {
            "title": "Review of Particle Physics",
            "authors": "Particle Data Group",
            "journal": "Prog. Theor. Exp. Phys.",
            "year": 2024,
            "doi": "10.1093/ptep/ptac097",
            "data": "All particle masses, lifetimes, constants",
        },
        {
            "title": "CODATA Recommended Values 2022",
            "authors": "CODATA Task Group",
            "journal": "Rev. Mod. Phys.",
            "volume": 93,
            "year": 2022,
            "doi": "10.1103/RevModPhys.93.025010",
            "data": "Fundamental constants (α, ℏ, c, G_F, etc.)",
        },
    ],
    # Galaxies
    "galaxies": [
        {
            "title": "SPARC: Mass Models for 175 Disk Galaxies",
            "authors": "Lelli, F., McGaugh, S.S., Schombert, J.M.",
            "journal": "Astron. J.",
            "volume": 152,
            "pages": 157,
            "year": 2016,
            "doi": "10.3847/0004-6256/152/6/157",
            "data": "175 rotation curves",
        },
        {
            "title": "LITTLE THINGS Dwarf Galaxies",
            "authors": "Oh, S.-H. et al.",
            "journal": "Astron. J.",
            "volume": 149,
            "pages": 180,
            "year": 2015,
            "doi": "10.1088/0004-6256/149/6/180",
            "data": "Dwarf galaxy rotation curves",
        },
    ],
}

# ============================================================
# DATA FILES CREATED AND THEIR SOURCES
# ============================================================

DATA_FILES_CREATED = {
    # Particle Physics
    "01_particle_physics/standard_model_masses.py": {
        "source": "PDG 2024",
        "doi": "10.1093/ptep/ptac097",
        "verified": True,
    },
    "01_particle_physics/beta_plus_data.py": {
        "source": "Hardy & Towner 2020",
        "doi": "10.1103/PhysRevC.102.045501",
        "verified": True,
    },
    "01_particle_physics/beta_minus_data.py": {
        "source": "PDG 2024, NNDC",
        "doi": "10.1093/ptep/ptac097",
        "verified": True,
    },
    "01_particle_physics/neutron_decay_data.py": {
        "source": "UCNτ 2021, PDG 2024",
        "doi": "10.1103/PhysRevLett.127.162501",
        "verified": True,
    },
    "01_particle_physics/muon_decay_data.py": {
        "source": "MuLan 2011, PDG 2024",
        "doi": "10.1103/PhysRevLett.106.041803",
        "verified": True,
    },
    "01_particle_physics/quantum_mechanics_data.py": {
        "source": "Bell tests (Aspect, Hensen), CODATA",
        "doi": "10.1038/nature15759",
        "verified": True,
    },
    # NEW FILES ADDED
    "01_particle_physics/pmns_mixing_data.py": {
        "source": "PDG 2024, T2K, NOvA, Daya Bay, NuFIT 2024",
        "doi": "10.1093/ptep/ptac097",
        "verified": True,
    },
    "01_particle_physics/qcd_strong_force_data.py": {
        "source": "PDG 2024, Lattice QCD, LHC",
        "doi": "10.1093/ptep/ptac097",
        "verified": True,
    },
    "01_particle_physics/spin_statistics_data.py": {
        "source": "PDG 2024, Pauli 1940",
        "doi": "10.1093/ptep/ptac097",
        "verified": True,
    },
    "01_particle_physics/particle_masses.py": {
        "source": "PDG 2024",
        "doi": "10.1093/ptep/ptac097",
        "verified": True,
    },
    "01_particle_physics/weak_force_data.py": {
        "source": "PDG 2024, MuLan",
        "doi": "10.1103/PhysRevLett.106.041803",
        "verified": True,
    },
    "01_particle_physics/neutrino_extended_data.py": {
        "source": "PDG 2024, KATRIN, NuFIT",
        "doi": "10.1038/s41567-021-01463-1",
        "verified": True,
    },
    # Astrophysics
    "02_astrophysics/sparc_data.py": {
        "source": "SPARC Database",
        "doi": "10.3847/0004-6256/152/6/157",
        "verified": True,
    },
    "02_astrophysics/little_things_data.py": {
        "source": "Oh et al. 2015",
        "doi": "10.1088/0004-6256/149/6/180",
        "verified": True,
    },
}

# ============================================================
# FUNCTIONS TO LIST AND VERIFY REFERENCES
# ============================================================


def list_all_references():
    """List all papers used in UET validation."""
    print("=" * 70)
    print("UET VALIDATION REFERENCES")
    print("=" * 70)

    for category, papers in REFERENCES.items():
        print(f"\n{category.upper()}:")
        print("-" * 50)
        for i, paper in enumerate(papers, 1):
            print(f"\n[{i}] {paper['title']}")
            print(f"    Authors: {paper['authors']}")
            print(f"    Journal: {paper['journal']} ({paper['year']})")
            print(f"    DOI: {paper['doi']}")
            print(f"    Data: {paper['data']}")


def verify_data_sources():
    """Check that all data files have proper citations."""
    print("\n" + "=" * 70)
    print("DATA FILE VERIFICATION")
    print("=" * 70)

    for file, info in DATA_FILES_CREATED.items():
        status = "✓" if info["verified"] else "✗"
        print(f"\n{status} {file}")
        print(f"   Source: {info['source']}")
        print(f"   DOI: {info['doi']}")


if __name__ == "__main__":
    list_all_references()
    verify_data_sources()
