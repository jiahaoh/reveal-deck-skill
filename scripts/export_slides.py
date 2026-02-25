#!/usr/bin/env python3
"""
Export reveal.js slides as high-resolution PNGs.

Usage:
    python export_slides.py presentation.html                       # Export all slides
    python export_slides.py presentation.html --slides 1,3,5-7     # Export specific slides
    python export_slides.py presentation.html --scale 4            # 4x retina (default)
    python export_slides.py presentation.html --output ./pngs/     # Custom output dir

Requires: pip install playwright && python -m playwright install chromium
"""

import argparse
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def parse_slide_spec(spec: str) -> set[int]:
    """Parse slide spec like '1,3,5-7' into a set of 1-based indices."""
    indices = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            indices.update(range(int(start), int(end) + 1))
        else:
            indices.add(int(part))
    return indices


def export_slides(html_path: str, output_dir: str, scale: int, slide_spec: str | None):
    """Export slides as PNGs."""
    html_path = Path(html_path).resolve()
    if not html_path.exists():
        print(f"Error: file not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    requested = parse_slide_spec(slide_spec) if slide_spec else None

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 960, "height": 540},
            device_scale_factor=scale,
        )
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(1500)  # Wait for fonts, reveal.js, charts

        # Disable transitions so screenshots capture clean frames
        page.evaluate("Reveal.configure({ transition: 'none', backgroundTransition: 'none', controls: false, progress: false })")

        # Get all slide indices
        indices = page.evaluate("""
            (() => {
                const slides = Reveal.getSlides();
                return slides.map((s, i) => {
                    const idx = Reveal.getIndices(s);
                    return { h: idx.h, v: idx.v, num: i + 1 };
                });
            })()
        """)

        exported = 0
        for idx in indices:
            num = idx["num"]

            if requested and num not in requested:
                continue

            h, v = idx["h"], idx["v"] or 0
            page.evaluate(f"Reveal.slide({h}, {v})")
            page.wait_for_timeout(300)  # Wait for transitions + rendering

            png_name = f"slide-{num:02d}.png"
            png_path = out_dir / png_name

            page.screenshot(
                path=str(png_path),
                clip={"x": 0, "y": 0, "width": 960, "height": 540},
            )
            exported += 1
            actual_px = 960 * scale
            print(f"  Exported {png_name} ({actual_px}x{540 * scale}px)")

        browser.close()

    print(f"\n{exported} slide(s) exported to {out_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Export reveal.js slides as PNGs.")
    parser.add_argument("html", help="Path to presentation.html")
    parser.add_argument("--slides", default=None,
                        help='Slide numbers to export, e.g. "1,3,5-7" (default: all)')
    parser.add_argument("--scale", type=int, default=4,
                        help="Device scale factor (default: 4 = retina)")
    parser.add_argument("--output", default=None,
                        help="Output directory (default: same dir as HTML)")
    args = parser.parse_args()

    output_dir = args.output or str(Path(args.html).resolve().parent / "slides")
    export_slides(args.html, output_dir, args.scale, args.slides)


if __name__ == "__main__":
    main()
