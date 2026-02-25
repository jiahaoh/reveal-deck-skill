# reveal-deck

A Claude skill for creating polished [reveal.js](https://revealjs.com) presentation decks as self-contained HTML files — viewable in any browser with keyboard navigation, speaker notes, and smooth transitions. Optionally export individual slides as 4× retina PNGs or the full deck as a PDF.

## What It Does

Trigger phrases: *"make a presentation"*, *"create slides"*, *"build a deck"*, *"slideshow about"*

Claude follows a structured workflow to:
1. Plan a narrative arc and slide-by-slide outline
2. Scaffold the deck with `scripts/create_deck.py`
3. Fill each slide from one of 13 typed templates
4. Validate that all slides fit the fixed 960×540 viewport
5. Deliver the HTML + CSS, with optional PNG/PDF export

## Themes

| Theme | Palette | Best for |
|---|---|---|
| **swiss** (default) | Black / white / grey | Research, data-heavy, academic |
| **dark** | Navy / cool blue | Engineering, tech demos |
| **warm** | Parchment / saddlebrown | Humanities, narrative talks |
| **minimal** | White / single blue accent | Product, business |
| **contrast** | True black / gold | Keynotes, accessibility |

## Slide Templates

13 reusable `<section>` templates with `{{PLACEHOLDER}}` slots:

`title` · `section-divider` · `overview` · `table` · `problem-solution` · `reference` · `timeline` · `key-findings` · `comparison` · `notes` · `panels` · `code` · `chart` · `image`

## Deck Masters

Pre-built slide structures for common talk types in `masters/`:

- `research-talk.json` — title → background → methods → results → discussion → conclusion
- `paper-review.json` — title → overview → related work → methods → results → analysis
- `project-update.json` — title → status → progress → blockers → metrics → next steps

## Scripts

| Script | Purpose |
|---|---|
| `scripts/create_deck.py` | Scaffold `presentation.html` + `styles.css` |
| `scripts/check_overflow.py` | Detect slides that exceed 960×540 |
| `scripts/export_slides.py` | Export slides as 4× retina PNGs |
| `scripts/export_pdf.py` | Export full deck as PDF |
| `scripts/edit_deck.py` | Launch a browser-based inline text editor |

### Quick start

```bash
python scripts/create_deck.py \
  --structure "title,overview,d,table,key-findings" \
  --title "My Talk" \
  --theme swiss \
  --output ./deck/
```

### Export (requires Playwright)

```bash
pip install --break-system-packages playwright
python -m playwright install chromium

python scripts/export_slides.py deck/presentation.html
python scripts/export_pdf.py deck/presentation.html
```

## Technology

- **reveal.js 5.2.1** — presentation framework (CDN)
- **Chart.js 4.4.7** — data visualizations (CDN)
- **KaTeX 0.16.11** — math rendering (CDN)
- **IBM Plex Sans / Mono** — typography (Google Fonts CDN)
- **Playwright** — headless Chromium for export and overflow validation

## Repository Layout

```
SKILL.md              ← skill manifest (read by Claude)
components.md         ← CSS class reference
base-styles.css       ← component definitions (consumed by all themes)
export.md             ← export workflow and pitfalls
scripts/              ← Python utilities
templates/            ← 13 slide HTML fragments
themes/               ← 5 CSS theme files
masters/              ← 3 pre-built deck structures
references/           ← advanced features and Chart.js guides
```
