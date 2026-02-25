# Component Reference

CSS classes available in every generated `styles.css`. All values come from theme tokens via `var()` — components adapt automatically to any theme.

Read this before writing slide HTML. Use these classes to compose slide layouts. For one-off grid ratios, use inline styles. For patterns repeated 3+ times, prefer these classes.

---

## Layout Primitives

### Title Slide
```html
<section class="title-slide">
  <div style="flex:1; display:flex; flex-direction:column; justify-content:center">
    <h1>Title</h1>
    <p class="subtitle">Subtitle</p>
  </div>
  <p class="author-date">Author &middot; Date</p>
</section>
```
Full-white centered layout. Title + subtitle centered vertically, author pinned to bottom.

### Section Divider
```html
<section class="section-divider">
  <p class="section-number">Part 1</p>
  <h2>Section Title</h2>
</section>
```
Full-bleed header-colored background. Centered text. Use between major deck sections.

### Slide Header
```html
<div class="slide-header">
  <span class="slide-num">1</span>  <!-- optional -->
  <h2>Slide Title</h2>
</div>
```
Colored banner at the top of content slides. `.slide-num` adds a small numbered badge.

### Content Area
```html
<div class="content">
  <!-- All slide body content goes here -->
</div>
```
Flex column that fills the remaining space below the header. Handles padding, gap, and overflow.

---

## Content Components

### Section Labels
```html
<p class="section-label">Label with left border</p>
<p class="section-title-bar">Label with bottom border</p>
```
Uppercase, letter-spaced labels to introduce subsections within a slide.

### Module Grid
```html
<div class="module-grid">
  <div class="module">
    <h4>Module Title</h4>
    <p>Description text.</p>
  </div>
  <!-- 2-column grid, add more .module blocks -->
</div>
```
2-column grid of bordered cards. Good for system components, feature lists, definitions.

### Data Table
```html
<table class="data-table">
  <thead><tr><th>Col 1</th><th>Col 2</th></tr></thead>
  <tbody>
    <tr><td>Value</td><td>Value</td></tr>
  </tbody>
</table>
```
Styled table with uppercase headers, monospace data cells, alternating row backgrounds. Set `flex: 1` on the table if it should fill remaining vertical space.

### Pipeline Flow
```html
<div class="pipeline-flow">
  <span class="pipeline-step">Step 1</span>
  <span class="pipeline-arrow">&rarr;</span>
  <span class="pipeline-step">Step 2</span>
  <span class="pipeline-arrow">&rarr;</span>
  <span class="pipeline-step">Step 3</span>
</div>
```
Horizontal process flow with arrows. Monospace font.

### Stat Boxes
```html
<div class="stat-row">
  <div class="stat-box">
    <p class="stat-value">42.3%</p>
    <p class="stat-label">Accuracy</p>
  </div>
  <!-- Add more .stat-box blocks -->
</div>
```
Horizontal row of metric displays. Accent-colored top border.

### Timeline
```html
<div class="timeline">
  <div class="timeline-step">
    <span class="timeline-num">1</span>
    <div class="timeline-content">
      <h4>Step Title</h4>
      <p>Description.</p>
    </div>
  </div>
  <!-- Add more .timeline-step blocks -->
</div>
```
Vertical numbered progression. Good for protocols, methods, sequential processes.

### Findings Grid
```html
<div class="findings-grid">
  <div class="finding">
    <p class="finding-num">01</p>
    <h4>Finding Title</h4>
    <p>Description.</p>
  </div>
  <!-- 2x2 grid -->
</div>
```
2-column grid of numbered findings/takeaways. Accent-colored numbers.

### Comparison Columns
```html
<div class="comparison-row">
  <div class="comparison-col">
    <h3>Method A</h3>
    <div class="comparison-item">
      <p class="label">Metric</p>
      <p class="value">Value</p>
    </div>
  </div>
  <div class="split-divider"></div>
  <div class="comparison-col">
    <h3>Method B</h3>
    <!-- ... -->
  </div>
</div>
```
Side-by-side evaluation with a vertical divider.

### Notes Layout
```html
<div class="notes-layout">
  <div class="notes-main">
    <h3>Heading</h3>
    <ul><li>Note point</li></ul>
  </div>
  <div class="notes-sidebar">
    <h4>Reference</h4>
    <p>Citation info.</p>
  </div>
</div>
```
Two-column: main notes (flex: 1) + reference sidebar (35% width).

### Panels
```html
<div class="panels-row">
  <div class="panel">
    <div class="panel-tab">Tab Label</div>
    <div class="panel-body">
      <h4>Heading</h4>
      <ul><li>Point</li></ul>
    </div>
  </div>
  <!-- Add more .panel blocks -->
</div>
```
Side-by-side tabbed containers. Panel tab uses header colors.

---

## Split Layouts

```html
<div class="split-row">
  <div class="split-col">Left content</div>
  <div class="split-divider"></div>
  <div class="split-col">Right content</div>
</div>
```
Flexible 50/50 split. For unequal splits, use inline styles: `style="flex: 2"` / `style="flex: 1"`.

---

## Emphasis & Highlight

```html
<div class="emphasis-box">
  <h4>Bold statement</h4>
  <p>On accent-colored background.</p>
</div>

<div class="emphasis-box-light">
  <h4>Highlighted info</h4>
  <p>Subtle background with accent left border.</p>
</div>
```

---

## Tags

```html
<div class="tag-list">
  <span class="tag">Python</span>
  <span class="tag">PyTorch</span>
  <span class="tag">scRNA-seq</span>
</div>
```
Lightweight inline labels with borders.

---

## Code Block

```html
<div class="code-block">
  <pre><code class="language-python" data-trim data-line-numbers="1-3|4-6">
def hello():
    print("world")
  </code></pre>
  <p class="code-caption">Optional caption.</p>
</div>
```
`data-line-numbers` enables line numbers. Pipe-separated ranges create step-by-step highlights (fragments).

---

## Chart Container

```html
<div class="chart-container">
  <canvas data-chart='{ "type": "bar", "data": {...}, "options": { "maintainAspectRatio": false } }'></canvas>
</div>
```
Flex container that fills remaining space. The scaffold auto-initializes Chart.js canvases.
**Required**: `"maintainAspectRatio": false` in chart options.

---

## Image Slide

```html
<!-- Full-bleed cover -->
<section class="image-slide">
  <img src="path.jpg" alt="Description">
  <div class="image-caption">Optional caption</div>
</section>

<!-- Contained with padding -->
<section class="image-slide contain">
  <img src="diagram.png" alt="Description">
</section>

<!-- Background image (reveal.js native) -->
<section data-background-image="path.jpg" data-background-size="cover">
  <h2>Title over image</h2>
</section>
```

---

## Utility Classes

| Class | Effect |
|-------|--------|
| `.text-sm` | 0.68rem |
| `.text-base` | 0.78rem |
| `.text-lg` | 0.88rem |
| `.text-xl` | 1.0rem |
| `.text-2xl` | 1.2rem |
| `.text-3xl` | 1.5rem |
| `.text-4xl` | 2.0rem |
| `.text-muted` | Muted color |
| `.text-faint` | Faint color |
| `.text-dark` | Dark color |
| `.text-accent` | Accent color |
| `.font-mono` | Monospace font |
| `.font-bold` | Bold weight |
| `.font-semibold` | Semibold weight |
| `.mt-auto` | Push to bottom |
| `.flex-1` | Flex grow |
| `.flex-row` | Horizontal flex |
| `.flex-col` | Vertical flex |
| `.gap-sm` | 0.4rem gap |
| `.gap-md` | 0.8rem gap |
| `.gap-lg` | 1.2rem gap |

---

## Fragments (Progressive Reveal)

Add `class="fragment"` to any element to reveal it on click/advance:

```html
<p class="fragment">Appears first</p>
<p class="fragment">Appears second</p>
```

Fragment animations (add alongside `.fragment`):
- `fade-up`, `fade-down`, `fade-left`, `fade-right`
- `fade-in-then-out`, `fade-in-then-semi-out`
- `grow`, `shrink`
- `highlight-red`, `highlight-green`, `highlight-blue`
- `strike`

Custom order: `data-fragment-index="0"`

---

## Speaker Notes

```html
<aside class="notes">
  These notes are visible in Speaker View (press S).
  Supports <strong>HTML</strong> formatting.
</aside>
```
Place as the last child of each `<section>`. Press `S` in the browser to open Speaker View.
