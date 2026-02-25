#!/usr/bin/env python3
"""
Build a reveal.js presentation from a YAML content file.

Usage:
    python build_from_yaml.py deck.yaml
    python build_from_yaml.py deck.yaml --output ./my-deck --theme dark

The YAML file defines slide content and layout. Each slide either picks a
template (title, overview, table, …) and supplies content fields, or describes
a custom layout in natural language for Claude to fill in later.

See yaml-schema.md for the full schema reference.
"""

import argparse
import json
import sys
import textwrap
from html import escape as _esc
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

SKILL_DIR = Path(__file__).resolve().parent.parent

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


# ═══════════════════════════════════════════════════════════════════════
# Utilities
# ═══════════════════════════════════════════════════════════════════════

def esc(value):
    """HTML-escape a value. Handles None and non-string types."""
    if value is None:
        return ""
    return _esc(str(value))


def notes_el(slide):
    """Return <aside class='notes'> from slide's 'notes' field."""
    notes = slide.get("notes", "")
    return f'<aside class="notes">{esc(notes)}</aside>'


def header_el(title):
    """Standard slide header bar."""
    return (
        f'<div class="slide-header">\n'
        f'          <h2>{esc(title)}</h2>\n'
        f'        </div>'
    )


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


# ═══════════════════════════════════════════════════════════════════════
# Template builders — one function per template
# ═══════════════════════════════════════════════════════════════════════

def build_title(slide, num):
    title = esc(slide.get("title", "Untitled"))
    subtitle = slide.get("subtitle", "")
    author = slide.get("author", "")
    date = slide.get("date", "")

    subtitle_html = ""
    if subtitle:
        subtitle_html = f'\n          <p class="subtitle">{esc(subtitle)}</p>'

    parts = [p for p in [author, date] if p]
    author_date = " &middot; ".join(esc(str(p)) for p in parts)

    return (
        f'      <!-- SLIDE {num}: title -->\n'
        f'      <section class="title-slide" data-slide-id="{num}">\n'
        f'        <div style="flex:1; display:flex; flex-direction:column; justify-content:center">\n'
        f'          <h1>{title}</h1>{subtitle_html}\n'
        f'        </div>\n'
        f'        <p class="author-date">{author_date}</p>\n'
        f'        {notes_el(slide)}\n'
        f'      </section>'
    )


def build_divider(slide, num, divider_count):
    if isinstance(slide.get("divider"), str):
        section_title = slide["divider"]
    else:
        section_title = slide.get("title", f"Section {divider_count}")

    section_label = slide.get("label", f"Part {divider_count}")

    return (
        f'      <!-- SLIDE {num}: section-divider -->\n'
        f'      <section class="section-divider" data-slide-id="{num}">\n'
        f'        <p class="section-number">{esc(section_label)}</p>\n'
        f'        <h2>{esc(section_title)}</h2>\n'
        f'        {notes_el(slide)}\n'
        f'      </section>'
    )


def build_overview(slide, num):
    title = slide.get("title", f"Slide {num}")
    parts = []

    # Modules
    modules = slide.get("modules", [])
    if modules:
        label = slide.get("modules_label", "")
        if label:
            parts.append(f'        <p class="section-title-bar">{esc(label)}</p>')
        module_items = []
        for m in modules:
            module_items.append(
                f'          <div class="module">\n'
                f'            <h4>{esc(m.get("title", ""))}</h4>\n'
                f'            <p>{esc(m.get("description", ""))}</p>\n'
                f'          </div>'
            )
        parts.append(
            f'        <div class="module-grid">\n'
            + "\n".join(module_items) + "\n"
            f'        </div>'
        )

    # Pipeline
    pipeline = slide.get("pipeline", [])
    if pipeline:
        label = slide.get("pipeline_label", "")
        if label:
            parts.append(f'        <p class="section-title-bar">{esc(label)}</p>')
        steps = []
        for i, step in enumerate(pipeline):
            if i > 0:
                steps.append('<span class="pipeline-arrow">&rarr;</span>')
            steps.append(f'<span class="pipeline-step">{esc(step)}</span>')
        parts.append(
            f'        <div class="pipeline-flow">\n'
            f'          ' + "\n          ".join(steps) + "\n"
            f'        </div>'
        )

    # Stats
    stats = slide.get("stats", [])
    if stats:
        stat_items = []
        for s in stats:
            stat_items.append(
                f'          <div class="stat-box">\n'
                f'            <p class="stat-value">{esc(s.get("value", ""))}</p>\n'
                f'            <p class="stat-label">{esc(s.get("label", ""))}</p>\n'
                f'          </div>'
            )
        parts.append(
            f'        <div class="stat-row">\n'
            + "\n".join(stat_items) + "\n"
            f'        </div>'
        )

    content = "\n\n".join(parts)

    return (
        f'      <!-- SLIDE {num}: overview -->\n'
        f'      <section data-slide-id="{num}">\n'
        f'        {header_el(title)}\n'
        f'        <div class="content">\n'
        f'{content}\n'
        f'        </div>\n'
        f'        {notes_el(slide)}\n'
        f'      </section>'
    )


def build_table(slide, num):
    title = slide.get("title", f"Slide {num}")
    label = slide.get("label", "")
    columns = slide.get("columns", [])
    rows = slide.get("rows", [])

    label_html = ""
    if label:
        label_html = f'        <p class="section-label">{esc(label)}</p>\n'

    # Header row
    th_cells = "".join(f'<th scope="col">{esc(c)}</th>' for c in columns)
    thead = f'          <thead>\n            <tr>{th_cells}</tr>\n          </thead>'

    # Body rows
    tr_rows = []
    for row in rows:
        td_cells = "".join(f"<td>{esc(c)}</td>" for c in row)
        tr_rows.append(f"            <tr>{td_cells}</tr>")
    tbody = f'          <tbody>\n' + "\n".join(tr_rows) + "\n          </tbody>"

    return (
        f'      <!-- SLIDE {num}: table -->\n'
        f'      <section data-slide-id="{num}">\n'
        f'        {header_el(title)}\n'
        f'        <div class="content">\n'
        f'{label_html}'
        f'        <table class="data-table">\n'
        f'{thead}\n'
        f'{tbody}\n'
        f'        </table>\n'
        f'        </div>\n'
        f'        {notes_el(slide)}\n'
        f'      </section>'
    )


def build_problem_solution(slide, num):
    title = slide.get("title", f"Slide {num}")
    prob = slide.get("problem", {})
    sol = slide.get("solution", {})

    def build_col(data, css_box_class):
        label = data.get("label", "")
        col_title = data.get("title", "")
        desc = data.get("description", "")
        points = data.get("points", [])

        label_html = f'          <p class="section-label">{esc(label)}</p>\n' if label else ""
        box_html = (
            f'          <div class="{css_box_class}">\n'
            f'            <h4>{esc(col_title)}</h4>\n'
            f'            <p>{esc(desc)}</p>\n'
            f'          </div>'
        )
        li_items = "\n".join(f"            <li>{esc(p)}</li>" for p in points)
        ul_html = f"          <ul>\n{li_items}\n          </ul>" if points else ""

        return (
            f'        <div class="split-col">\n'
            f'{label_html}'
            f'{box_html}\n'
            f'{ul_html}\n'
            f'        </div>'
        )

    left = build_col(prob, "emphasis-box-light")
    right = build_col(sol, "emphasis-box")

    return (
        f'      <!-- SLIDE {num}: problem-solution -->\n'
        f'      <section data-slide-id="{num}">\n'
        f'        {header_el(title)}\n'
        f'        <div class="content">\n'
        f'        <div class="split-row">\n'
        f'{left}\n'
        f'        <div class="split-divider"></div>\n'
        f'{right}\n'
        f'        </div>\n'
        f'        </div>\n'
        f'        {notes_el(slide)}\n'
        f'      </section>'
    )


def build_key_findings(slide, num):
    title = slide.get("title", f"Slide {num}")
    label = slide.get("label", "")
    findings = slide.get("findings", [])

    label_html = ""
    if label:
        label_html = f'        <p class="section-label">{esc(label)}</p>\n'

    finding_items = []
    for i, f in enumerate(findings, 1):
        finding_items.append(
            f'          <div class="finding">\n'
            f'            <p class="finding-num">{i:02d}</p>\n'
            f'            <h4>{esc(f.get("title", ""))}</h4>\n'
            f'            <p>{esc(f.get("description", ""))}</p>\n'
            f'          </div>'
        )

    return (
        f'      <!-- SLIDE {num}: key-findings -->\n'
        f'      <section data-slide-id="{num}">\n'
        f'        {header_el(title)}\n'
        f'        <div class="content">\n'
        f'{label_html}'
        f'        <div class="findings-grid">\n'
        + "\n".join(finding_items) + "\n"
        f'        </div>\n'
        f'        </div>\n'
        f'        {notes_el(slide)}\n'
        f'      </section>'
    )


def build_comparison(slide, num):
    title = slide.get("title", f"Slide {num}")
    col_a = slide.get("column_a", {})
    col_b = slide.get("column_b", {})

    def build_col(data):
        col_title = data.get("title", "")
        items = data.get("items", [])

        item_divs = []
        for it in items:
            item_divs.append(
                f'            <div class="comparison-item">\n'
                f'              <p class="label">{esc(it.get("label", ""))}</p>\n'
                f'              <p class="value">{esc(it.get("value", ""))}</p>\n'
                f'            </div>'
            )

        return (
            f'          <div class="comparison-col">\n'
            f'            <h3>{esc(col_title)}</h3>\n'
            + "\n".join(item_divs) + "\n"
            f'          </div>'
        )

    left = build_col(col_a)
    right = build_col(col_b)

    return (
        f'      <!-- SLIDE {num}: comparison -->\n'
        f'      <section data-slide-id="{num}">\n'
        f'        {header_el(title)}\n'
        f'        <div class="content">\n'
        f'        <div class="comparison-row">\n'
        f'{left}\n'
        f'          <div class="split-divider"></div>\n'
        f'{right}\n'
        f'        </div>\n'
        f'        </div>\n'
        f'        {notes_el(slide)}\n'
        f'      </section>'
    )


def build_timeline(slide, num):
    title = slide.get("title", f"Slide {num}")
    label = slide.get("label", "")
    steps = slide.get("steps", [])

    label_html = ""
    if label:
        label_html = f'        <p class="section-label">{esc(label)}</p>\n'

    step_items = []
    for i, s in enumerate(steps, 1):
        step_items.append(
            f'          <div class="timeline-step">\n'
            f'            <span class="timeline-num">{i}</span>\n'
            f'            <div class="timeline-content">\n'
            f'              <h4>{esc(s.get("title", ""))}</h4>\n'
            f'              <p>{esc(s.get("description", ""))}</p>\n'
            f'            </div>\n'
            f'          </div>'
        )

    return (
        f'      <!-- SLIDE {num}: timeline -->\n'
        f'      <section data-slide-id="{num}">\n'
        f'        {header_el(title)}\n'
        f'        <div class="content">\n'
        f'{label_html}'
        f'        <div class="timeline">\n'
        + "\n".join(step_items) + "\n"
        f'        </div>\n'
        f'        </div>\n'
        f'        {notes_el(slide)}\n'
        f'      </section>'
    )


def build_reference(slide, num):
    title = slide.get("title", f"Slide {num}")
    label = slide.get("label", "")
    definitions = slide.get("definitions", [])

    label_html = ""
    if label:
        label_html = f'        <p class="section-label">{esc(label)}</p>\n'

    def_items = []
    for d in definitions:
        def_items.append(
            f'          <div class="module">\n'
            f'            <h4>{esc(d.get("term", ""))}</h4>\n'
            f'            <p>{esc(d.get("description", ""))}</p>\n'
            f'          </div>'
        )

    return (
        f'      <!-- SLIDE {num}: reference -->\n'
        f'      <section data-slide-id="{num}">\n'
        f'        {header_el(title)}\n'
        f'        <div class="content">\n'
        f'{label_html}'
        f'        <div class="module-grid">\n'
        + "\n".join(def_items) + "\n"
        f'        </div>\n'
        f'        </div>\n'
        f'        {notes_el(slide)}\n'
        f'      </section>'
    )


def build_notes_slide(slide, num):
    title = slide.get("title", f"Slide {num}")
    main_sections = slide.get("main", [])
    sidebar = slide.get("sidebar", {})

    # Main column
    main_parts = []
    for section in main_sections:
        heading = section.get("heading", "")
        items = section.get("items", [])
        li_html = "\n".join(f"            <li>{esc(it)}</li>" for it in items)
        main_parts.append(
            f'          <h3>{esc(heading)}</h3>\n'
            f'          <ul>\n{li_html}\n          </ul>'
        )
    main_html = "\n".join(main_parts)

    # Sidebar
    sidebar_title = sidebar.get("title", "")
    sidebar_items = sidebar.get("items", [])
    sidebar_lines = "\n".join(f"            <p>{esc(it)}</p>" for it in sidebar_items)
    sidebar_html = (
        f'          <div class="notes-sidebar">\n'
        f'            <h4>{esc(sidebar_title)}</h4>\n'
        f'{sidebar_lines}\n'
        f'          </div>'
    )

    return (
        f'      <!-- SLIDE {num}: notes -->\n'
        f'      <section data-slide-id="{num}">\n'
        f'        {header_el(title)}\n'
        f'        <div class="content">\n'
        f'        <div class="notes-layout">\n'
        f'          <div class="notes-main">\n'
        f'{main_html}\n'
        f'          </div>\n'
        f'{sidebar_html}\n'
        f'        </div>\n'
        f'        </div>\n'
        f'        {notes_el(slide)}\n'
        f'      </section>'
    )


def build_panels(slide, num):
    title = slide.get("title", f"Slide {num}")
    panel_a = slide.get("panel_a", {})
    panel_b = slide.get("panel_b", {})

    def build_panel(data):
        tab = data.get("tab", "")
        heading = data.get("heading", "")
        points = data.get("points", [])
        image = data.get("image", "")

        img_html = ""
        if image:
            alt = data.get("image_alt", "")
            img_html = f'            <img src="{esc(image)}" alt="{esc(alt)}">\n'

        li_items = "\n".join(f"              <li>{esc(p)}</li>" for p in points)

        return (
            f'          <div class="panel">\n'
            f'            <div class="panel-tab">{esc(tab)}</div>\n'
            f'            <div class="panel-body">\n'
            f'{img_html}'
            f'              <h4>{esc(heading)}</h4>\n'
            f'              <ul>\n{li_items}\n              </ul>\n'
            f'            </div>\n'
            f'          </div>'
        )

    left = build_panel(panel_a)
    right = build_panel(panel_b)

    return (
        f'      <!-- SLIDE {num}: panels -->\n'
        f'      <section data-slide-id="{num}">\n'
        f'        {header_el(title)}\n'
        f'        <div class="content">\n'
        f'        <div class="panels-row">\n'
        f'{left}\n'
        f'{right}\n'
        f'        </div>\n'
        f'        </div>\n'
        f'        {notes_el(slide)}\n'
        f'      </section>'
    )


def build_code(slide, num):
    title = slide.get("title", f"Slide {num}")
    language = slide.get("language", "")
    code = slide.get("code", "")
    line_highlights = slide.get("line_highlights", "")
    caption = slide.get("caption", "")

    line_attr = f' data-line-numbers="{esc(line_highlights)}"' if line_highlights else ""
    caption_html = ""
    if caption:
        caption_html = f'\n          <p class="code-caption">{esc(caption)}</p>'

    # Code content: escape HTML but preserve whitespace
    code_escaped = _esc(str(code)).rstrip()

    return (
        f'      <!-- SLIDE {num}: code -->\n'
        f'      <section data-slide-id="{num}">\n'
        f'        {header_el(title)}\n'
        f'        <div class="content">\n'
        f'        <div class="code-block">\n'
        f'          <pre><code class="language-{esc(language)}" data-trim{line_attr}>\n'
        f'{code_escaped}\n'
        f'          </code></pre>{caption_html}\n'
        f'        </div>\n'
        f'        </div>\n'
        f'        {notes_el(slide)}\n'
        f'      </section>'
    )


def build_chart(slide, num):
    title = slide.get("title", f"Slide {num}")
    chart_config = slide.get("chart", {})

    # Ensure responsive options
    if isinstance(chart_config, dict):
        opts = chart_config.setdefault("options", {})
        opts.setdefault("responsive", True)
        opts.setdefault("maintainAspectRatio", False)
        config_json = json.dumps(chart_config, indent=2)
    else:
        config_json = str(chart_config)

    # Escape single quotes in JSON for the HTML attribute
    config_attr = config_json.replace("'", "&#39;")

    return (
        f'      <!-- SLIDE {num}: chart -->\n'
        f'      <section data-slide-id="{num}">\n'
        f'        {header_el(title)}\n'
        f'        <div class="content">\n'
        f"        <div class=\"chart-container\">\n"
        f"          <canvas data-chart='{config_attr}'></canvas>\n"
        f'        </div>\n'
        f'        </div>\n'
        f'        {notes_el(slide)}\n'
        f'      </section>'
    )


def build_image(slide, num):
    title = slide.get("title", "")
    src = slide.get("src", "")
    alt = slide.get("alt", "")
    caption = slide.get("caption", "")
    contain = slide.get("contain", False)

    css_class = "image-slide contain" if contain else "image-slide"

    caption_html = ""
    if caption:
        caption_html = f'\n        <div class="image-caption">{esc(caption)}</div>'

    # Image slides don't use the standard header — the image is full-bleed
    title_comment = f" — {esc(title)}" if title else ""

    return (
        f'      <!-- SLIDE {num}: image{title_comment} -->\n'
        f'      <section class="{css_class}" data-slide-id="{num}">\n'
        f'        <img src="{esc(src)}" alt="{esc(alt)}">{caption_html}\n'
        f'        {notes_el(slide)}\n'
        f'      </section>'
    )


def build_custom_layout(slide, num):
    """Generate a placeholder for a custom-layout slide described in natural language.

    The layout description and content data are embedded as HTML comments
    so Claude can interpret them and fill in the actual HTML.
    """
    layout_desc = slide.get("layout", "")
    title = slide.get("title", f"Slide {num}")
    content = slide.get("content", {})

    # Serialize content data as YAML inside an HTML comment
    content_yaml = ""
    if content:
        content_yaml = yaml.dump(content, default_flow_style=False, indent=2).rstrip()
        content_yaml = textwrap.indent(content_yaml, "           ")

    content_comment = ""
    if content_yaml:
        content_comment = (
            f'\n        <!-- CONTENT DATA:\n'
            f'{content_yaml}\n'
            f'        -->'
        )

    return (
        f'      <!-- SLIDE {num}: custom-layout -->\n'
        f'      <!-- LAYOUT: {esc(layout_desc)} -->{content_comment}\n'
        f'      <section data-slide-id="{num}">\n'
        f'        {header_el(title)}\n'
        f'        <div class="content">\n'
        f'          <p>Custom layout — fill based on layout description above.</p>\n'
        f'        </div>\n'
        f'        {notes_el(slide)}\n'
        f'      </section>'
    )


# ═══════════════════════════════════════════════════════════════════════
# Dispatcher
# ═══════════════════════════════════════════════════════════════════════

BUILDERS = {
    "title": build_title,
    "overview": build_overview,
    "table": build_table,
    "problem-solution": build_problem_solution,
    "key-findings": build_key_findings,
    "comparison": build_comparison,
    "timeline": build_timeline,
    "reference": build_reference,
    "notes": build_notes_slide,
    "panels": build_panels,
    "code": build_code,
    "chart": build_chart,
    "image": build_image,
}


def generate_slides(slides_yaml):
    """Walk the YAML slides list and build HTML for each."""
    sections = []
    slide_num = 0
    divider_count = 0

    for slide in slides_yaml:
        slide_num += 1

        # Shorthand divider: - divider: "Section Name"
        if "divider" in slide:
            divider_count += 1
            sections.append(build_divider(slide, slide_num, divider_count))

        # Custom layout described in natural language
        elif "layout" in slide:
            sections.append(build_custom_layout(slide, slide_num))

        # Vertical stack: - stack: [...]
        elif "stack" in slide:
            inner_slides = slide["stack"]
            inner_sections = []
            for inner in inner_slides:
                inner_num = slide_num
                if "divider" in inner:
                    divider_count += 1
                    inner_sections.append(build_divider(inner, inner_num, divider_count))
                elif "layout" in inner:
                    inner_sections.append(build_custom_layout(inner, inner_num))
                elif "template" in inner:
                    tmpl = inner["template"]
                    if tmpl == "divider":
                        divider_count += 1
                        inner_sections.append(build_divider(inner, inner_num, divider_count))
                    elif tmpl in BUILDERS:
                        inner_sections.append(BUILDERS[tmpl](inner, inner_num))
                    else:
                        print(f"Warning: Unknown template '{tmpl}' in stack, skipping.", file=sys.stderr)
                slide_num += 1
            slide_num -= 1  # Adjust because outer loop increments

            vstack_html = "\n".join(inner_sections)
            sections.append(
                f'      <!-- VERTICAL STACK -->\n'
                f'      <section>\n{vstack_html}\n      </section>'
            )

        # Template-based slide: - template: name
        elif "template" in slide:
            tmpl = slide["template"]
            if tmpl == "divider":
                divider_count += 1
                sections.append(build_divider(slide, slide_num, divider_count))
            elif tmpl in BUILDERS:
                sections.append(BUILDERS[tmpl](slide, slide_num))
            else:
                print(f"Warning: Unknown template '{tmpl}', generating placeholder.", file=sys.stderr)
                sections.append(
                    f'      <!-- SLIDE {slide_num}: unknown template "{esc(tmpl)}" -->\n'
                    f'      <section data-slide-id="{slide_num}">\n'
                    f'        <div class="slide-header"><h2>Slide {slide_num}</h2></div>\n'
                    f'        <div class="content"><p>Unknown template: {esc(tmpl)}</p></div>\n'
                    f'        {notes_el(slide)}\n'
                    f'      </section>'
                )
        else:
            print(f"Warning: Slide {slide_num} has no 'template', 'divider', 'layout', or 'stack' key. Skipping.", file=sys.stderr)
            slide_num -= 1

    return "\n\n".join(sections)


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Build a reveal.js presentation from a YAML content file."
    )
    parser.add_argument("yaml_file", help="Path to the YAML deck file")
    parser.add_argument("--output", default=None,
                        help="Output directory (overrides YAML 'output' field)")
    parser.add_argument("--theme", default=None, choices=sorted(VALID_THEMES),
                        help="Color theme (overrides YAML 'theme' field)")
    args = parser.parse_args()

    # Load YAML
    yaml_path = Path(args.yaml_file)
    if not yaml_path.exists():
        print(f"Error: File not found: {yaml_path}", file=sys.stderr)
        sys.exit(1)

    with open(yaml_path) as f:
        deck = yaml.safe_load(f)

    if not deck or "slides" not in deck:
        print("Error: YAML must have a 'slides' key with a list of slides.", file=sys.stderr)
        sys.exit(1)

    # Resolve settings (CLI overrides YAML)
    title = deck.get("title", "Untitled Presentation")
    theme = args.theme or deck.get("theme", "swiss")
    output = args.output or deck.get("output", "./deck")

    if theme not in VALID_THEMES:
        print(f"Error: Unknown theme '{theme}'. Valid: {sorted(VALID_THEMES)}", file=sys.stderr)
        sys.exit(1)

    # Generate HTML
    slides_html = generate_slides(deck["slides"])
    full_html = HTML_TEMPLATE.format(
        title=title,
        cdn=CDN_BASE,
        reveal=REVEAL_VERSION,
        chartjs=CHARTJS_VERSION,
        katex=KATEX_VERSION,
        slides=slides_html,
    )

    # Generate styles
    styles_css = generate_styles(theme)

    # Write output
    out_dir = Path(output)
    out_dir.mkdir(parents=True, exist_ok=True)

    html_path = out_dir / "presentation.html"
    css_path = out_dir / "styles.css"

    html_path.write_text(full_html)
    css_path.write_text(styles_css)

    # Count slides
    slide_count = 0
    for slide in deck["slides"]:
        if "stack" in slide:
            slide_count += len(slide["stack"])
        else:
            slide_count += 1

    # Count custom layouts that need Claude's attention
    custom_count = sum(1 for s in deck["slides"] if "layout" in s)
    stack_custom = sum(
        sum(1 for inner in s["stack"] if "layout" in inner)
        for s in deck["slides"] if "stack" in s
    )
    custom_count += stack_custom

    print(f"Created {html_path}  ({slide_count} slides, theme: {theme})")
    print(f"Created {css_path}")

    if custom_count > 0:
        print(f"\n{custom_count} slide(s) use custom layouts — search for '<!-- LAYOUT:' in the HTML")
        print("and replace the placeholder content with the described layout.")
    else:
        print(f"\nAll slides populated from YAML. Open {html_path} in a browser to view.")


if __name__ == "__main__":
    main()
