from pathlib import Path
from html import escape
import json
import re
import subprocess
from markdown_it import MarkdownIt

root = Path(__file__).resolve().parents[3]
source = root / ".publish-core-handoff" / "README.md"
text = source.read_text(encoding="utf-8")
start = "<!-- UET-CURRENT-MASTER-PRESENTATION:START -->"
end = "<!-- UET-CURRENT-MASTER-PRESENTATION:END -->"
assert text.count(start) == text.count(end) == 1
block = text.split(start, 1)[1].split(end, 1)[0]
md = MarkdownIt("commonmark", {"html": True}).enable("table")
tokens = md.parse(block)
table_cells, current_row, in_table = [], 0, False
for token in tokens:
    if token.type == "table_open":
        in_table = True
    elif token.type == "table_close":
        in_table = False
    elif in_table and token.type == "tr_open":
        current_row = 0
    elif in_table and token.type in {"th_open", "td_open"}:
        current_row += 1
    elif in_table and token.type == "tr_close":
        table_cells.append(current_row)
assert table_cells and set(table_cells) == {3}, table_cells
assert sum(t.type == "table_open" for t in tokens) == 4
assert sum(t.type == "heading_open" for t in tokens) == 7
assert len(re.findall(r"(?m)^\$\$$", block)) == 10
assert sum(t.type == "fence" and t.info == "mermaid" for t in tokens) == 1
ids = re.findall(r'<a id="([^"]+)"', text)
assert len(ids) == len(set(ids)), "duplicate explicit anchor"
links = []
for inline in (t for t in tokens if t.type == "inline"):
    for child in inline.children or []:
        if child.type == "link_open":
            links.append(child.attrGet("href"))
for link in links:
    path, _, fragment = link.partition("#")
    if not path:
        assert fragment in ids, link
    else:
        target = source.parent / path
        assert target.is_file(), link
        if fragment:
            assert f'id="{fragment}"' in target.read_text(encoding="utf-8"), link
        subprocess.run(["git", "-c", "core.fsmonitor=false", "cat-file", "-e", "origin/main:" + path], cwd=source.parent, check=True, capture_output=True)
new_ids = [key for key in ids if key.startswith("current-master-")]
assert len(new_ids) == 7
for key in new_ids:
    assert f"](#{key})" in text, "new TOC link missing: " + key
assert not re.search(r"(?:[A-Z]:[\\/]|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|gh[pousr]_[A-Za-z0-9]{20,}|BEGIN [A-Z ]*PRIVATE KEY)", block)
math_blocks = re.findall(r"(?ms)^\$\$\n(.*?)\n\$\$", block)
for formula in math_blocks:
    assert formula.count("{") == formula.count("}"), "unbalanced math braces"
    assert re.findall(r"\\begin\{(\w+)\}", formula) == re.findall(r"\\end\{(\w+)\}", formula), "unbalanced environments"
rendered = re.sub(r"(?ms)^\$\$\n(.*?)\n\$\$", lambda m: '<pre class="math-source">' + escape(m.group(1)) + "</pre>\n", block)
body = md.render(rendered)
style = """*{box-sizing:border-box}body{font-family:"Leelawadee UI","Segoe UI",sans-serif;margin:24px auto;max-width:1180px;padding:0 24px;color:#20252b;background:white;line-height:1.65}h3,h4{line-height:1.4;margin-top:28px}h3{font-size:25px}h4{font-size:21px;border-bottom:1px solid #d8dee4;padding-bottom:8px}p{margin:12px 0}table{border-collapse:collapse;width:100%;font-size:14px;margin:20px 0}th,td{border:1px solid #d0d7de;padding:9px 11px;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#f4f6f8}code{background:#eef1f4;font-family:Consolas,monospace;font-size:.9em;overflow-wrap:anywhere}pre{padding:15px;background:#f4f6f8;overflow:auto}pre code{white-space:pre}.math-source{font-size:14px;color:#364152}blockquote{border-left:4px solid #b7c5d3;margin:18px 0;padding:0 16px;color:#485466}a{color:#0969da;text-decoration:none}.preview{padding:12px;background:#fff8c5;border:1px solid #d4a72c;font-size:13px}"""
out = Path(__file__).with_name("preview.html")
out.write_text('<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'"><title>Master formulation — local Markdown preview</title><style>' + style + '</style><body><div class="preview">Local Markdown preview only. TeX and Mermaid are shown as source; math/diagram rendering and Jekyll/Pages build are not verified. ตรวจเฉพาะ Markdown และการอ่านตาราง ไม่ใช่ผล build เว็บไซต์จริง</div>' + body + "</body></html>", encoding="utf-8")
print(json.dumps({"new_tables": 4, "new_table_row_cell_counts": sorted(set(table_cells)), "new_headings": 7, "display_formula_blocks": len(math_blocks), "mermaid_source_blocks": 1, "new_block_links": len(links), "new_TOC_links": len(new_ids), "new_public_target_files": len({link.split('#')[0] for link in links if not link.startswith('#')}), "duplicate_explicit_anchors": 0, "new_privacy_matches": 0, "preview": str(out)}, ensure_ascii=False))

