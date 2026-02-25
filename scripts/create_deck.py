#!/usr/bin/env python3
"""
Scaffold a reveal.js presentation deck.

Usage:
    python create_deck.py --structure "title,overview,d,table,key-findings" \
                          --title "My Presentation" \
                          --theme swiss \
                          --output ./deck/

Structure format (comma-separated):
    template-name   → horizontal slide (title, overview, table, problem-solution,
                      reference, timeline, key-findings, comparison, notes, panels,
                      code, chart, image)
    d               → section divider slide
    name+name+...   → vertical slide stack (e.g. table+chart)
"""

import argparse
import os
import shutil
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent  # scripts/ → reveal-deck/

VALID_TEMPLATES = {
    "title", "overview", "table", "problem-solution", "reference",
    "timeline", "key-findings", "comparison", "notes", "panels",
    "code", "chart", "image",
}

VALID_THEMES = {"swiss", "dark", "warm", "minimal", "contrast"}

CDN_BASE = "https://cdn.jsdelivr.net/npm"
REVEAL_VERSION = "5.2.1"
CHARTJS_VERSION = "4.4.7"
KATEX_VERSION = "0.16.11"

HTML_TEMPLATE = """\
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>

  <!-- Reveal.js core -->
  <link rel="stylesheet" href="{cdn}/reveal.js@{reveal}/dist/reset.css">
  <link rel="stylesheet" href="{cdn}/reveal.js@{reveal}/dist/reveal.css">

  <!-- Syntax highlighting -->
  <link rel="stylesheet" href="{cdn}/reveal.js@{reveal}/plugin/highlight/monokai.css">

  <!-- KaTeX math -->
  <link rel="stylesheet" href="{cdn}/katex@{katex}/dist/katex.min.css">

  <!-- Google Fonts -->
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">

  <!-- Presentation styles -->
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <div class="reveal">
    <div class="slides">

{slides}

    </div>
  </div>

  <!-- Reveal.js and plugins -->
  <script src="{cdn}/reveal.js@{reveal}/dist/reveal.js"></script>
  <script src="{cdn}/reveal.js@{reveal}/plugin/highlight/highlight.js"></script>
  <script src="{cdn}/reveal.js@{reveal}/plugin/notes/notes.js"></script>
  <script src="{cdn}/reveal.js@{reveal}/plugin/math/math.js"></script>
  <script src="{cdn}/reveal.js@{reveal}/plugin/zoom/zoom.js"></script>

  <!-- Chart.js -->
  <script src="{cdn}/chart.js@{chartjs}/dist/chart.umd.min.js"></script>

  <script>
    Reveal.initialize({{
      width: 960,
      height: 540,
      margin: 0,
      minScale: 0.2,
      maxScale: 2.0,

      hash: true,
      controls: true,
      progress: true,
      center: false,

      transition: 'slide',
      transitionSpeed: 'default',
      backgroundTransition: 'fade',

      plugins: [RevealHighlight, RevealNotes, RevealMath.KaTeX, RevealZoom]
    }});

    // Auto-initialize Chart.js canvases with data-chart attribute
    document.querySelectorAll('canvas[data-chart]').forEach(function(canvas) {{
      try {{
        var config = JSON.parse(canvas.getAttribute('data-chart'));
        new Chart(canvas, config);
      }} catch (e) {{
        console.error('Chart init error:', e, canvas);
      }}
    }});
  </script>
</body>
</html>
"""


def make_title_placeholder(slide_num):
    return f"""\
      <!-- SLIDE {slide_num}: title -->
      <section class="title-slide" data-slide-id="{slide_num}">
        <div style="flex:1; display:flex; flex-direction:column; justify-content:center">
          <h1>Slide {slide_num} — Presentation Title Here</h1>
          <p class="subtitle">Slide {slide_num} Subtitle Here</p>
        </div>
        <p class="author-date">Author Name &middot; Date</p>
        <aside class="notes">Speaker notes for slide {slide_num}.</aside>
      </section>"""


def make_divider_placeholder(slide_num, divider_count):
    return f"""\
      <!-- SLIDE {slide_num}: section-divider -->
      <section class="section-divider" data-slide-id="{slide_num}">
        <p class="section-number">Part {divider_count}</p>
        <h2>Slide {slide_num} — Section Title Here</h2>
        <aside class="notes">Speaker notes for slide {slide_num}.</aside>
      </section>"""


def make_content_placeholder(slide_num, template_name):
    return f"""\
      <!-- SLIDE {slide_num}: {template_name} -->
      <section data-slide-id="{slide_num}">
        <div class="slide-header">
          <h2>Slide {slide_num} Title Here</h2>
        </div>
        <div class="content">
          <p>Slide {slide_num} content here. Template: {template_name}.</p>
        </div>
        <aside class="notes">Speaker notes for slide {slide_num}.</aside>
      </section>"""


def parse_structure(structure_str):
    """Parse comma-separated structure into list of slide specs."""
    entries = [s.strip() for s in structure_str.split(",") if s.strip()]
    slides = []
    for entry in entries:
        if "+" in entry:
            # Vertical stack
            parts = [p.strip() for p in entry.split("+") if p.strip()]
            for p in parts:
                if p != "d" and p not in VALID_TEMPLATES:
                    raise ValueError(f"Unknown template '{p}'. Valid: {sorted(VALID_TEMPLATES)}")
            slides.append(("vstack", parts))
        elif entry == "d":
            slides.append(("divider", None))
        elif entry in VALID_TEMPLATES:
            slides.append(("slide", entry))
        else:
            raise ValueError(f"Unknown template '{entry}'. Valid: {sorted(VALID_TEMPLATES)}, 'd' for divider, '+' for vertical stacks")
    return slides


def generate_slides_html(structure):
    """Generate placeholder HTML for all slides."""
    sections = []
    slide_num = 0
    divider_count = 0

    for kind, data in structure:
        slide_num += 1

        if kind == "divider":
            divider_count += 1
            sections.append(make_divider_placeholder(slide_num, divider_count))

        elif kind == "slide":
            if data == "title":
                sections.append(make_title_placeholder(slide_num))
            else:
                sections.append(make_content_placeholder(slide_num, data))

        elif kind == "vstack":
            inner = []
            for tmpl in data:
                slide_num_inner = slide_num
                if tmpl == "title":
                    inner.append(make_title_placeholder(slide_num_inner))
                elif tmpl == "d":
                    divider_count += 1
                    inner.append(make_divider_placeholder(slide_num_inner, divider_count))
                else:
                    inner.append(make_content_placeholder(slide_num_inner, tmpl))
                slide_num += 1
            slide_num -= 1  # Adjust because outer loop increments too

            vstack_html = "\n".join(inner)
            sections.append(f"      <!-- VERTICAL STACK -->\n      <section>\n{vstack_html}\n      </section>")

    return "\n\n".join(sections)


def generate_styles(theme_name):
    """Read theme CSS and base-styles CSS, concatenate them."""
    theme_path = SKILL_DIR / "themes" / f"{theme_name}.css"
    base_path = SKILL_DIR / "base-styles.css"

    if not theme_path.exists():
        raise FileNotFoundError(f"Theme not found: {theme_path}")
    if not base_path.exists():
        raise FileNotFoundError(f"Base styles not found: {base_path}")

    theme_css = theme_path.read_text()
    base_css = base_path.read_text()

    return f"/* Theme: {theme_name} */\n{theme_css}\n\n{base_css}"


def main():
    parser = argparse.ArgumentParser(description="Scaffold a reveal.js presentation deck.")
    parser.add_argument("--structure", required=True,
                        help='Comma-separated slide types, e.g. "title,overview,d,table,key-findings"')
    parser.add_argument("--title", default="Untitled Presentation",
                        help="Presentation title (used in <title> tag)")
    parser.add_argument("--theme", default="swiss", choices=sorted(VALID_THEMES),
                        help="Color theme (default: swiss)")
    parser.add_argument("--output", default="./deck",
                        help="Output directory (default: ./deck)")
    args = parser.parse_args()

    # Parse structure
    structure = parse_structure(args.structure)

    # Generate HTML
    slides_html = generate_slides_html(structure)
    full_html = HTML_TEMPLATE.format(
        title=args.title,
        cdn=CDN_BASE,
        reveal=REVEAL_VERSION,
        chartjs=CHARTJS_VERSION,
        katex=KATEX_VERSION,
        slides=slides_html,
    )

    # Generate styles
    styles_css = generate_styles(args.theme)

    # Write output
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    html_path = out_dir / "presentation.html"
    css_path = out_dir / "styles.css"

    html_path.write_text(full_html)
    css_path.write_text(styles_css)

    slide_count = sum(
        len(data) if kind == "vstack" else 1
        for kind, data in structure
    )

    print(f"Created {html_path}  ({slide_count} slides, theme: {args.theme})")
    print(f"Created {css_path}")
    print(f"\nOpen {html_path} in a browser to view the presentation.")
    print("Use the Edit tool to replace placeholder content one slide at a time.")


if __name__ == "__main__":
    main()
