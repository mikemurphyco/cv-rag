#!/usr/bin/env python3
"""Convert a CV markdown file to a styled PDF using WeasyPrint."""

import sys
import subprocess
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "docs"
VERSIONS_DIR = DOCS_DIR / "versions"
VERSIONS_DIR.mkdir(exist_ok=True)

MD_FILE = DOCS_DIR / "cv_mike-murphy_langchain-tse.md"
PDF_FILE = VERSIONS_DIR / "cv_mike-murphy_langchain-tse.pdf"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

@page {
    size: letter;
    margin: 0.65in 0.75in 0.65in 0.75in;
}

body {
    font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 9.5pt;
    line-height: 1.45;
    color: #1a1a1a;
}

h1 {
    font-size: 20pt;
    font-weight: 700;
    color: #111;
    margin-bottom: 2px;
    letter-spacing: -0.3px;
}

/* Subtitle line (bold italic paragraph right after h1) */
h1 + p {
    font-size: 9pt;
    color: #555;
    margin-bottom: 6px;
    font-weight: 500;
}

/* Contact line */
h1 + p + p {
    font-size: 8.5pt;
    color: #444;
    margin-bottom: 14px;
    line-height: 1.7;
}

h2 {
    font-size: 10pt;
    font-weight: 700;
    color: #1a1a1a;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 14px;
    margin-bottom: 5px;
    padding-bottom: 3px;
    border-bottom: 1.5px solid #1a1a1a;
}

h3 {
    font-size: 9.5pt;
    font-weight: 600;
    color: #1a1a1a;
    margin-top: 9px;
    margin-bottom: 3px;
}

p {
    margin-bottom: 5px;
}

ul {
    margin: 3px 0 5px 14px;
    padding: 0;
}

li {
    margin-bottom: 2.5px;
}

hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 10px 0;
}

a {
    color: #1a1a1a;
    text-decoration: none;
}

strong {
    font-weight: 600;
}
"""

def md_to_html(md_path: Path) -> str:
    result = subprocess.run(
        ["pandoc", "--from=markdown", "--to=html5", "--standalone=false", str(md_path)],
        capture_output=True, text=True, check=True
    )
    return result.stdout

def build_html(content: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
{CSS}
</style>
</head>
<body>
{content}
</body>
</html>"""

def main():
    print(f"Reading {MD_FILE}...")
    html_body = md_to_html(MD_FILE)
    full_html = build_html(html_body)

    print("Rendering PDF with WeasyPrint...")
    from weasyprint import HTML
    HTML(string=full_html).write_pdf(str(PDF_FILE))

    print(f"PDF saved to: {PDF_FILE}")

if __name__ == "__main__":
    main()
