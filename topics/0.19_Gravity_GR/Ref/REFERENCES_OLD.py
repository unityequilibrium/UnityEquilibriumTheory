"""
REFERENCES.py - 0.19 Gravity GR
================================
"""

REFERENCES = {
    "primary": {
        "Gravity_Foundations": {
            "title": "Foundations of Gravity and Spacetime",
            "local_files": ["gr-qc_9504004.pdf", "1606.09251.pdf", "1609.05917.pdf"],
        }
    }
}


def list_references():
    print("0.19 Gravity GR References")
    for name, ref in REFERENCES["primary"].items():
        print(f"📚 {name}: Files {ref['local_files']}")


if __name__ == "__main__":
    list_references()
