"""
UET Atomic Physics Reference Downloader
=======================================
Searches arXiv for seminal papers on:
- Koide Formula (Fermion Mass)
- Fine Structure Constant Precision
- Fundamental Constants (CODATA)

Uses public APIs to fetch metadata and PDF links.
"""

import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
import time
from pathlib import Path

# --- CONFIG ---
SEARCH_QUERIES = [
    "ti:Koide formula fermion mass",
    "all:precision measurement fine structure constant",
    "all:CODATA recommended values fundamental constants",
    "all:electron anomalous magnetic moment alpha",
    "all:topological insulator fine structure constant",
]

OUTPUT_DIR = Path(__file__).parent / "PDF_Downloads"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def search_arxiv(query, max_results=3):
    """Search arXiv API."""
    base_url = "http://export.arxiv.org/api/query?"
    params = {"search_query": query, "start": 0, "max_results": max_results}
    url = base_url + urllib.parse.urlencode(params)

    print(f"🔍 Searching arXiv for: '{query}'...")
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            root = ET.fromstring(data)

            results = []
            for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                title = entry.find("{http://www.w3.org/2005/Atom}title").text.strip()
                pdf_link = ""
                for link in entry.findall("{http://www.w3.org/2005/Atom}link"):
                    if link.get("title") == "pdf":
                        pdf_link = link.get("href")

                results.append({"title": title, "pdf": pdf_link, "source": "arXiv"})

            return results
    except Exception as e:
        print(f"❌ Error searching arXiv: {e}")
        return []


def download_pdf(url, title):
    """Download PDF file."""
    if not url:
        return

    safe_title = "".join(
        [c for c in title if c.isalnum() or c in (" ", "-", "_")]
    ).strip()
    safe_title = safe_title[:50]  # Truncate
    filename = OUTPUT_DIR / f"{safe_title}.pdf"

    if filename.exists():
        print(f"  Example: {filename.name} (Already exists)")
        return

    print(f"  ⬇️ Downloading: {safe_title}...")
    try:
        # User-Agent needed for some servers
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            },
        )
        with urllib.request.urlopen(req) as response:
            with open(filename, "wb") as f:
                f.write(response.read())
        print("  ✅ Success!")
        time.sleep(2)  # Be polite
    except Exception as e:
        print(f"  ⚠️ download failed: {e}")


def main():
    print("📚 UET Atomic Reference Downloader")
    print("==================================")

    total_found = 0
    for query in SEARCH_QUERIES:
        papers = search_arxiv(query)
        total_found += len(papers)

        for p in papers:
            print(f"  Found: {p['title']}")
            download_pdf(p["pdf"], p["title"])

    print("\n" + "=" * 40)
    print(f"Done. Found {total_found} relevant papers.")
    print(f"Saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
