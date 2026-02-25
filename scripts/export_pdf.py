#!/usr/bin/env python3
"""
Export a reveal.js presentation to PDF.

Uses Playwright to print the presentation in reveal.js print mode.

Usage:
    python export_pdf.py presentation.html
    python export_pdf.py presentation.html --output talk.pdf

Requires: pip install playwright && python -m playwright install chromium
"""

import argparse
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def export_pdf(html_path: str, output_path: str | None):
    """Export presentation to PDF using reveal.js print-pdf mode."""
    html_path = Path(html_path).resolve()
    if not html_path.exists():
        print(f"Error: file not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    if output_path:
        pdf_path = Path(output_path).resolve()
    else:
        pdf_path = html_path.with_suffix(".pdf")

    # Append ?print-pdf to trigger reveal.js print layout
    url = f"file://{html_path}?print-pdf"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(3000)  # Wait for fonts, charts, layout reflow

        # Wait for reveal.js to be ready
        page.evaluate("Reveal.isReady() || new Promise(r => Reveal.on('ready', r))")
        page.wait_for_timeout(500)

        page.pdf(
            path=str(pdf_path),
            width="960px",
            height="540px",
            print_background=True,
            prefer_css_page_size=True,
        )

        browser.close()

    print(f"Exported PDF: {pdf_path}")


def main():
    parser = argparse.ArgumentParser(description="Export reveal.js presentation to PDF.")
    parser.add_argument("html", help="Path to presentation.html")
    parser.add_argument("--output", default=None, help="Output PDF path (default: same name as HTML)")
    args = parser.parse_args()

    export_pdf(args.html, args.output)


if __name__ == "__main__":
    main()
