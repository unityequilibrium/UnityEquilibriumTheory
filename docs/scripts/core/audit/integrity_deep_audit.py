import os

TOPICS_DIR = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0\docs\topics"


def check_file_content(path, target_headers):
    if not os.path.exists(path):
        return False, "Missing File"

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    missing = []
    for header in target_headers:
        if header not in content:
            missing.append(header)

    if not missing:
        return True, "Passed"
    else:
        return False, f"Missing Headers: {', '.join(missing)}"


# Define required headers based on templates
REQUIREMENTS = {
    "README.md": ["## 1. 📂 5x4 Grid Structure", "## 2. ⚡ Quick Start"],
    "Code/README.md": ["## 🚀 Run Commands", "## 📊 Test Results", "## 🧬 Key Physics"],
    "ANALYSIS": [
        "## 1. 📄 Executive Summary",
        "## 2. 🧱 Theoretical Framework",
        "## 4. 📊 Validation & Results",
        "## 6. 📚 References & Data",
    ],
}


def deep_audit():
    topics = [
        d
        for d in os.listdir(TOPICS_DIR)
        if os.path.isdir(os.path.join(TOPICS_DIR, d)) and d[0].isdigit()
    ]

    report = []

    for topic in sorted(topics):
        topic_path = os.path.join(TOPICS_DIR, topic)

        # 1. Root README
        readme_path = os.path.join(topic_path, "README.md")
        r_ok, r_msg = check_file_content(readme_path, REQUIREMENTS["README.md"])

        # 2. Code README
        code_readme_path = os.path.join(topic_path, "Code", "README.md")
        cr_ok, cr_msg = check_file_content(code_readme_path, REQUIREMENTS["Code/README.md"])

        # 3. Analysis Files (check at least the first one)
        doc_dir = os.path.join(topic_path, "Doc")
        a_ok, a_msg = True, "No Analysis Files Found"
        if os.path.exists(doc_dir):
            a_files = [
                f for f in os.listdir(doc_dir) if f.startswith("ANALYSIS_") and f.endswith(".md")
            ]
            if a_files:
                # Audit the first one as a representative of the topic's style
                a_path = os.path.join(doc_dir, a_files[0])
                a_ok, a_msg = check_file_content(a_path, REQUIREMENTS["ANALYSIS"])
            else:
                a_ok, a_msg = False, "Missing ANALYSIS_*.md"
        else:
            a_ok, a_msg = False, "Missing Doc/ directory"

        report.append({"Topic": topic, "README": r_msg, "Code_README": cr_msg, "Analysis": a_msg})

    report_path = r"c:\Users\santa\.gemini\antigravity\brain\cffb5f8f-e211-46a9-b2c3-033fdc9bf012\UET_INTEGRITY_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f_out:
        f_out.write("# 🛡️ UET Documentation Integrity Report\n\n")
        f_out.write("Generated for: Phase 8 (Deep Audit)\n\n")
        f_out.write("| Topic | README Standard | Code/README Standard | Analysis Standard |\n")
        f_out.write("|---|---|---|---|\n")
        for r in report:
            f_out.write(
                f"| {r['Topic']} | {r['README']} | {r['Code_README']} | {r['Analysis']} |\n"
            )

    print(f"Report generated at: {report_path}")


if __name__ == "__main__":
    deep_audit()
