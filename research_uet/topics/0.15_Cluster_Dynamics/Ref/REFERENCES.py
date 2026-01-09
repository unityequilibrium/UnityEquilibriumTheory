"""
References: Cluster Dynamics
============================

DOIs for all data sources used in this topic.
"""

REFERENCES = {
    "galaxy_clusters": [
        {
            "title": "The Virial Masses of Galaxy Clusters",
            "authors": "Girardi, M. et al.",
            "journal": "ApJ 505, 74",
            "year": 1998,
            "doi": "10.1086/306157",
            "data": "Cluster mass-velocity dispersion relation",
        },
        {
            "title": "X-ray study of galaxy clusters",
            "authors": "Vikhlinin, A. et al.",
            "journal": "ApJ 640, 691",
            "year": 2006,
            "doi": "10.1086/500288",
            "data": "Cluster mass profiles",
        },
    ],
}

DATA_FILES = {
    "Code/cluster_virial/test_cluster_virial.py": {
        "source": "Girardi 1998, Vikhlinin 2006",
        "doi": "10.1086/306157",
        "verified": True,
    },
}


def list_references():
    """List all references."""
    print("=" * 60)
    print("0.15 CLUSTER DYNAMICS REFERENCES")
    print("=" * 60)
    for category, refs in REFERENCES.items():
        print(f"\n{category.upper()}:")
        for ref in refs:
            print(f"  [{ref['year']}] {ref['title']}")
            print(f"         DOI: {ref['doi']}")


if __name__ == "__main__":
    list_references()
