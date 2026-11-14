# REFERENCES.py - Topic 0.30: Mega-Flora Biotech

REFERENCES = {
    "BOTANICAL_URBANISM": {
        "title": "Plant-derived materials and structures: A review",
        "author": "Gibson, L. J.",
        "year": 2012,
        "journal": "Journal of the Royal Society Interface",
        "summary": "Mechanics of plant cell walls and cellular solids—the basis for Yggdrasil-class wood strength.",
    },
    "ROOT_MECHANICS": {
        "title": "Root reinforcement of soil: A review",
        "author": "Mickovski, S. B.",
        "year": 2009,
        "summary": "Quantifies the contribution of root systems to soil shear strength (The Bio-Anchor logic).",
    },
    "MOLECULAR_FARMING": {
        "title": "Plant molecular farming: Host systems, production platforms and emergence of commercial products",
        "author": "Tschofen, M. et al.",
        "year": 2016,
        "summary": "Proof of concept for protein expression (Myoglobin/Vitamins) in plant tissues.",
    },
}


def get_ref(key):
    return REFERENCES.get(key, "Reference not found.")
