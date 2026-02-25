---
name: reveal-deck
description: "Create polished reveal.js presentation decks as self-contained HTML. Use when the user asks to create slides, a presentation, a deck, a slideshow, or presentation cards. Supports multiple themes, code highlighting, math (KaTeX), charts (Chart.js), speaker notes, fragments, and auto-animate. Generates HTML + CSS viewable in any browser, with optional per-slide PNG and PDF export. Trigger on phrases like 'make a presentation', 'create slides', 'build a deck', 'presentation about', 'slide deck for', or 'slideshow'."
---

# Reveal-Deck Skill

Create professional reveal.js presentation decks rendered as self-contained HTML + CSS, viewable in any browser with keyboard navigation, transitions, and speaker notes. Optionally export individual slides as 4x retina PNGs or the full deck as PDF.

---

## Companion Files

All companions are co-located with this skill file.

| File | Role | When to read |
|---|---|---|
| `components.md` | CSS component reference — all available classes, layout patterns, fragments, speaker notes | Before writing any slide HTML |
| `base-styles.css` | Component class definitions using `var()` tokens | Reference only — auto-included in styles.css |
| `themes/<name>.css` | Theme token definitions (swiss, dark, warm, minimal, contrast) | When choosing or customizing a theme |
| `templates/<name>.html` | Slide `<section>` templates with `{{PLACEHOLDER}}` slots | When building each slide |
| `export.md` | PNG/PDF export workflow, prerequisites, common pitfalls | Before running export scripts |
| `references/advanced-features.md` | Fragments, auto-animate, backgrounds, transitions, code highlighting, math | When using advanced reveal.js features |
| `references/charts.md` | Chart.js integration — all chart types, layout patterns, styling | When adding charts |
| `masters/<name>.json` | Pre-built deck structures for common presentation types | When user asks for a research talk, paper review, etc. |
| `scripts/create_deck.py` | Scaffold generator — creates presentation.html + styles.css | Step 3 of workflow |
| `scripts/check_overflow.py` | Playwright overflow detector | Step 6 of workflow |
| `scripts/export_slides.py` | Playwright PNG exporter | When user requests PNG export |
| `scripts/export_pdf.py` | Playwright PDF exporter | When user requests PDF export |
| `scripts/edit_deck.py` | Browser-based inline text editor | Suggest to user after delivery |

---

## Themes

| Theme | Palette | Best for |
|---|---|---|
| **swiss** (default) | Black / white / grey — monochrome | Research, data-heavy, academic |
| **dark** | Navy / cool blue / grey | Engineering, tech demos |
| **warm** | Parchment / saddlebrown | Humanities, narrative talks |
| **minimal** | White / single blue accent | Product, business, general |
| **contrast** | True black / gold | Keynotes, high-energy, accessibility |

---

## Slide Templates

All templates are in `templates/`. Each is a `<section>` fragment with `{{PLACEHOLDER}}` slots.

| Template | Use when the content is… |
|---|---|
| **title** | Opening slide — presentation title, author, date |
| **section-divider** | Visual break between major sections |
| **overview** | System components, pipeline stages, architecture |
| **table** | Benchmark results, metrics grids, tabular data |
| **problem-solution** | Before/after, root cause analysis |
| **reference** | QC metrics, API references, formula glossaries |
| **timeline** | Sequential processes, protocols, methods |
| **key-findings** | Takeaways, highlights, numbered conclusions |
| **comparison** | Side-by-side method/tool evaluation |
| **notes** | Reading notes + paper reference sidebar |
| **panels** | Tabbed side-by-side panels with optional images |
| **code** | Code walkthroughs, syntax examples |
| **chart** | Data visualizations (bar, line, pie, scatter, radar) |
| **image** | Full-bleed or captioned images, diagrams |

---

## Deck Masters (Pre-Built Structures)

When the user asks for a common presentation type, read the corresponding master file:

| Master | Structure | Use when |
|---|---|---|
| `research-talk.json` | title → overview → methods → results → discussion → conclusion | "Research talk", "conference presentation" |
| `paper-review.json` | title → overview → related work → methods → results → analysis | "Paper review", "journal club" |
| `project-update.json` | title → status → progress → blockers → metrics → next steps | "Project update", "status report" |

Use the master's `structure` field as the `--structure` argument to `create_deck.py`. Adapt by adding/removing slides as the content requires.

---

## Design Principles

Before writing any HTML, internalize these rules:

1. **One idea per slide** — no walls of text. If content doesn't fit, split into multiple slides.
2. **Visual diversity** — vary templates across the deck. Don't use the same layout 3+ times in a row.
3. **Semantic elements only** — all text must be in `<p>`, `<li>`, `<h2>`–`<h4>`, `<td>`, `<th>`. Never put bare text in `<div>` or `<span>`.
4. **Use `pt` for custom font sizes** — the viewport is fixed at 960x540, so `pt` is predictable.
5. **Inline styles for one-off layouts** — use `style="display:grid; grid-template-columns: 2fr 1fr"` for per-slide grids. Use CSS classes for patterns repeated 3+ times.
6. **Speaker notes on every content slide** — include `<aside class="notes">` with talking points.
7. **Overflow is a hard failure** — all content must fit within 960x540. Reduce content or font sizes, never rely on scrolling.

---

## Hard Rules

- **No border-radius** — sharp corners only (theme may override for specific elements)
- **No box-shadow** — flat design by default
- **Edge-to-edge slides** — no body padding (reveal.js margin is 0)
- **Fonts via CDN** — IBM Plex Sans/Mono via Google Fonts
- **All slides must fit** — 960x540 viewport, `overflow: hidden` on sections

---

## Workflow

### Step 1: Gather Context

Identify what the user provided:
- **Outline** — slide-by-slide plan? Just a topic?
- **Content** — detailed text? Bullet points? Raw data?
- **Assets** — images, links, code snippets, paper references?
- **Preferences** — theme? audience? number of slides? export format?

If the scope is ambiguous, ask:
- How many slides (roughly)?
- What audience?
- Any specific theme preference?
- Need PNG or PDF export?

### Step 2: Plan the Deck

**Before writing any code**, output a plan:

1. **Narrative arc** — how the deck flows (intro → body → conclusion)
2. **Slide-by-slide plan** — for each slide: template type, key content, any assets
3. **Theme selection** — which theme and why
4. **Structure string** — the `--structure` argument for `create_deck.py`

If a deck master matches, start from its structure and adapt.

### Step 3: Scaffold

Read `scripts/create_deck.py` to understand the script interface, then run it:

```bash
python "<skill-dir>/scripts/create_deck.py" \
  --structure "title,overview,d,table,key-findings" \
  --title "Presentation Title" \
  --theme swiss \
  --output "<output-dir>"
```

This creates:
- `presentation.html` — reveal.js boilerplate with placeholder slides
- `styles.css` — theme + component CSS

### Step 4: Fill Slides

Read `components.md` for available CSS classes.

For each slide, read the corresponding template in `templates/<name>.html` to understand the expected structure.

Use the **Edit tool** to replace placeholder content one slide at a time. Each slide has unique text (e.g., `Slide 2 Title Here`, `Slide 2 content here. Template: overview.`) so Edit can target it precisely.

For each slide:
- Replace heading, body content, speaker notes
- Embed images: `<img src="path/url" alt="description">`
- Add links: `<a href="url">text</a>`
- Add code: `<pre><code class="language-python" data-trim data-line-numbers>...</code></pre>`
- Add math: `$inline$` or `$$display$$`
- Add charts: read `references/charts.md` first
- Add fragments: `class="fragment"` for progressive reveal (read `references/advanced-features.md`)
- Add auto-animate: `data-auto-animate` on consecutive sections that share elements

### Step 5: Custom CSS (if needed)

If the slide content requires CSS beyond the base components, add custom rules to `styles.css` at the bottom. Prefer using existing component classes and utility classes over writing new CSS.

### Step 6: Validate

Run the overflow checker:

```bash
python "<skill-dir>/scripts/check_overflow.py" "<output-dir>/presentation.html"
```

If any slides overflow, fix them by:
- Reducing font sizes
- Removing less important content
- Splitting into multiple slides
- Using a more compact template

Re-run until all slides pass.

### Step 7: Deliver

Present the output files to the user:
- `presentation.html` — open in any browser, navigate with arrow keys
- `styles.css` — theme + components
- Press **S** for speaker view, **O** for overview, **F** for fullscreen

If the user requested PNG export:
```bash
python "<skill-dir>/scripts/export_slides.py" "<output-dir>/presentation.html"
```

If the user requested PDF export:
```bash
python "<skill-dir>/scripts/export_pdf.py" "<output-dir>/presentation.html"
```

Suggest the browser editor for quick text tweaks:
```bash
python "<skill-dir>/scripts/edit_deck.py" "<output-dir>/presentation.html"
```

---

## Tips for Content-Dense Slides

- Use `.text-sm` (0.68rem) for secondary information
- Use `.font-mono` for data values in body text
- Use 3-column `module-grid` with `grid-template-columns: 1fr 1fr 1fr` for compact grids
- Split long tables across two slides rather than shrinking fonts below readability
- Use vertical slide stacks (`+` in structure) for drill-down content
- Stat boxes, pipeline flows, and tag lists are space-efficient ways to convey information
