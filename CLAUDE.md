# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

A Claude skill for creating professional reveal.js presentations as self-contained HTML files. `SKILL.md` is the main manifest and workflow guide. All companion files live at the repo root alongside it.

## Key Commands

All utilities are Python scripts with no build step required:

```bash
# Scaffold a new presentation
python scripts/create_deck.py --structure "title,overview,d,table,key-findings" --title "My Talk" --theme swiss --output ./deck/

# Validate all slides fit within 960x540 (overflow = hard failure)
python scripts/check_overflow.py presentation.html

# Export slides as 4x retina PNGs
python scripts/export_slides.py presentation.html --slides 1,3,5-7 --scale 4

# Export as PDF (uses reveal.js ?print-pdf mode)
python scripts/export_pdf.py presentation.html --output talk.pdf

# Launch browser-based inline editor
python scripts/edit_deck.py presentation.html --port 8000
```

Export scripts require Playwright:
```bash
pip install --break-system-packages playwright
python -m playwright install chromium
```

## Architecture

The skill follows a strict 7-step workflow defined in `SKILL.md`:

1. **Gather context** from the user
2. **Plan** narrative arc, slide structure, theme selection
3. **Scaffold** with `scripts/create_deck.py` → produces `presentation.html` + `styles.css`
4. **Fill slides** by replacing `{{PLACEHOLDER}}` tokens in templates using the Edit tool
5. **Add custom CSS** to `styles.css` if needed (prefer existing component classes)
6. **Validate** overflow with `scripts/check_overflow.py`
7. **Deliver** — open in browser; optionally export

### CSS Architecture

All slides render at a fixed **960×540 viewport** (hard constraint). Two CSS layers:

- `themes/<name>.css` — defines CSS custom properties (`--color-bg`, `--accent-color`, `--font-body`, etc.)
- `base-styles.css` — component classes that consume those variables (layouts, grids, tables, emphasis boxes, utility classes)

`scripts/create_deck.py` concatenates the chosen theme + `base-styles.css` into `styles.css` in the output directory. The script resolves companion paths via `SKILL_DIR = Path(__file__).resolve().parent.parent` (i.e., one level above `scripts/`).

### Templates

13 HTML `<section>` fragments in `templates/` with `{{PLACEHOLDER}}` slots. The structure string passed to `create_deck.py` maps template names plus:
- `d` — inserts a `section-divider` slide
- `+` — creates a vertical slide stack

### Themes

Five themes in `themes/`: `swiss` (default, monochrome), `dark` (navy/blue), `warm` (parchment), `minimal` (white/blue), `contrast` (black/gold).

### Masters

Pre-built structure strings for common presentation types in `masters/`: `research-talk.json`, `paper-review.json`, `project-update.json`.

## Hard Design Rules

- No `border-radius`, no `box-shadow` — flat design only
- Font sizes must use `pt` units (viewport is fixed, not fluid)
- All text must use semantic elements (`h2`–`h4`, `p`, `li`) — no bare text in `div`/`span`
- Overflow is a hard failure: every slide must fit within 960×540
- CDN dependencies: reveal.js 5.2.1, Chart.js 4.4.7, KaTeX 0.16.11, IBM Plex Sans/Mono (Google Fonts)
