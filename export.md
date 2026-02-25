# Export Workflow

## Prerequisites

```bash
pip install --break-system-packages playwright
python -m playwright install chromium
```

---

## PNG Export (Per-Slide)

Export all slides as 4x retina PNGs (3840x2160):

```bash
python scripts/export_slides.py presentation.html
```

Export specific slides only:

```bash
python scripts/export_slides.py presentation.html --slides 1,3,5-7
```

Custom output directory and scale:

```bash
python scripts/export_slides.py presentation.html --output ./pngs/ --scale 2
```

Output: `slides/slide-01.png`, `slides/slide-02.png`, etc.

---

## PDF Export

```bash
python scripts/export_pdf.py presentation.html
python scripts/export_pdf.py presentation.html --output talk.pdf
```

Uses reveal.js `?print-pdf` mode for proper page layout.

---

## Overflow Check

Run before export to catch slides where content exceeds the viewport:

```bash
python scripts/check_overflow.py presentation.html
```

Reports which slides overflow and by how many pixels. Exit code 1 if any overflow detected.

---

## Browser Editor

For quick text tweaks without re-running Claude:

```bash
python scripts/edit_deck.py presentation.html
```

Opens `http://localhost:8000`. Click any text to edit, press Escape to deselect, Ctrl/Cmd+S or click Save to write changes back to the HTML file.

---

## Common Pitfalls

1. **Fonts not loading** — Google Fonts loads via CDN. If offline, Chromium falls back to system fonts. Workaround: install IBM Plex TTF files locally.

2. **Charts not rendering in PNG** — Chart.js needs time to animate. The export script waits 300ms per slide. Increase `wait_for_timeout` if charts are incomplete.

3. **Content overflow** — Slides are fixed at 960x540. Reduce font sizes, remove content, or split across multiple slides. Run `check_overflow.py` to detect.

4. **White margins in PNG** — Caused by body padding or reveal.js margin. The scaffold sets `margin: 0` in Reveal config. Ensure `styles.css` has no body padding.

5. **Speaker notes visible** — Notes use `display: none` in the base styles. If they appear, check for CSS specificity conflicts.

6. **PDF page breaks wrong** — The `?print-pdf` mode renders each slide as a separate page. Avoid `overflow: visible` on sections.
