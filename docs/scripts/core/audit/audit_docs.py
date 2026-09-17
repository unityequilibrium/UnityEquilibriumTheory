import os

topics_dir = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0\docs\topics"
topics = [
    d
    for d in os.listdir(topics_dir)
    if os.path.isdir(os.path.join(topics_dir, d)) and d[0].isdigit()
]

audit_results = []

for topic in sorted(topics):
    topic_path = os.path.join(topics_dir, topic)
    readme_path = os.path.join(topic_path, "README.md")
    code_readme_path = os.path.join(topic_path, "Code", "README.md")
    doc_dir = os.path.join(topic_path, "Doc")
    analysis_files = []
    if os.path.exists(doc_dir):
        analysis_files = [f for f in os.listdir(doc_dir) if f.startswith("ANALYSIS_")]

    status = {
        "Topic": topic,
        "README": os.path.exists(readme_path),
        "Code/README": os.path.exists(code_readme_path),
        "Analysis_Files": len(analysis_files),
        "Analysis_List": analysis_files,
    }
    audit_results.append(status)

print("| Topic | README | Code/README | Analysis Files |")
print("|---|---|---|---|")
for r in audit_results:
    rm = "✅" if r["README"] else "❌"
    crm = "✅" if r["Code/README"] else "❌"
    af = f"✅ ({r['Analysis_Files']})" if r["Analysis_Files"] > 0 else "❌"
    print(f"| {r['Topic']} | {rm} | {crm} | {af} |")
