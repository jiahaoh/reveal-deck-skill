#!/usr/bin/env python3
"""
Check all slides in a reveal.js presentation for content overflow.

Usage:
    python check_overflow.py presentation.html

Requires: pip install playwright && python -m playwright install chromium
"""

import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def check_overflow(html_path: str) -> list[dict]:
    """Open the deck and check each slide for overflow."""
    html_path = Path(html_path).resolve()
    if not html_path.exists():
        print(f"Error: file not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 960, "height": 540},
        )
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(1000)  # Wait for fonts + reveal.js init

        # Get total slide count
        total = page.evaluate("Reveal.getTotalSlides()")
        print(f"Checking {total} slides for overflow...\n")

        # Iterate through all slides
        indices = page.evaluate("""
            (() => {
                const slides = Reveal.getSlides();
                return slides.map(s => {
                    const idx = Reveal.getIndices(s);
                    return { h: idx.h, v: idx.v };
                });
            })()
        """)

        for idx in indices:
            h, v = idx["h"], idx["v"]
            page.evaluate(f"Reveal.slide({h}, {v})")
            page.wait_for_timeout(100)

            overflow_info = page.evaluate(f"""
                (() => {{
                    const section = Reveal.getCurrentSlide();
                    const slideId = section.getAttribute('data-slide-id') || '';
                    const comment = section.previousSibling;
                    let label = '';
                    if (comment && comment.nodeType === 8) {{
                        label = comment.textContent.trim();
                    }}
                    return {{
                        h: {h},
                        v: {v},
                        slideId: slideId,
                        label: label,
                        scrollHeight: section.scrollHeight,
                        clientHeight: section.clientHeight,
                        overflowPx: Math.max(0, section.scrollHeight - section.clientHeight)
                    }};
                }})()
            """)

            results.append(overflow_info)

            status = "OK" if overflow_info["overflowPx"] == 0 else f"OVERFLOW by {overflow_info['overflowPx']}px"
            slide_label = overflow_info.get("label", "")
            slide_desc = f" ({slide_label})" if slide_label else ""
            print(f"  Slide [{h},{v}]{slide_desc}: {status}")

        browser.close()

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_overflow.py <presentation.html>", file=sys.stderr)
        sys.exit(1)

    results = check_overflow(sys.argv[1])

    overflows = [r for r in results if r["overflowPx"] > 0]
    print()
    if overflows:
        print(f"FAILED: {len(overflows)} slide(s) have overflow:")
        for r in overflows:
            print(f"  Slide [{r['h']},{r['v']}]: {r['overflowPx']}px overflow")
        sys.exit(1)
    else:
        print(f"PASSED: All {len(results)} slides fit within viewport.")
        sys.exit(0)


if __name__ == "__main__":
    main()
