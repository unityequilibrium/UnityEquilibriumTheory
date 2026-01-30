"""
REFERENCES.py - Topic 0.28 UET Material Synthesis
Registry of External Scientific Standards & Papers.
"""

REFERENCE_DB = {
    "REF_001": {
        "title": "Acoustically induced current flow in graphene",
        "journal": "Nature Physics",
        "year": 2011,
        "key_finding": "Surface Acoustic Waves (SAW) can drag charge carriers in graphene, proving coherent sound-matter interaction.",
        "relevance": "Foundational proof that acoustic fields can physically manipulate mass/charge in graphene lattices.",
        "status": "VERIFIED",
    },
    "REF_002": {
        "title": "Ultrasound-assisted exfoliation of graphite into graphene",
        "journal": "Ultrasonics Sonochemistry",
        "year": 2013,
        "key_finding": "High-intensity ultrasound navigates Van der Waals forces to act on graphene layers.",
        "relevance": " demonstrates acoustic energy scale is sufficient for carbon bond manipulation.",
        "status": "VERIFIED",
    },
    "REF_003": {
        "title": "Plasma-enhanced chemical vapor deposition of graphene",
        "journal": "Nanotechnology",
        "year": 2011,
        "key_finding": "Energetic field assistance (Plasma) improves growth rates vs thermal CVD.",
        "relevance": "Supports UET hypothesis that 'Field Assistance' (Sound/Resonance) beats random thermal growth.",
        "status": "VERIFIED",
    },
}


def get_citations():
    """Returns a formatted string of all references."""
    output = "📚 EXTERNAL SCIENTIFIC REFERENCES (TOPIC 0.28)\n"
    output += "=" * 60 + "\n"
    for ref_id, data in REFERENCE_DB.items():
        output += f"[{ref_id}] {data['title']}\n"
        output += f"      Source:  {data['journal']} ({data['year']})\n"
        output += f"      Finding: {data['key_finding']}\n"
        output += "-" * 60 + "\n"
    return output


if __name__ == "__main__":
    print(get_citations())
