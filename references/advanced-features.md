# Advanced Reveal.js Features

Reference for features beyond basic slide content. Read when the user requests animations, interactive elements, or advanced layouts.

---

## Fragments (Progressive Reveal)

Reveal elements step-by-step within a slide:

```html
<p class="fragment">Appears on first click</p>
<p class="fragment">Appears on second click</p>
```

### Animation Classes
Add alongside `.fragment`:

| Class | Effect |
|-------|--------|
| `fade-up` | Fade in from below |
| `fade-down` | Fade in from above |
| `fade-left` | Fade in from right |
| `fade-right` | Fade in from left |
| `fade-in-then-out` | Fade in, then fade out on next step |
| `fade-in-then-semi-out` | Fade in, then dim on next step |
| `grow` | Scale up |
| `shrink` | Scale down |
| `highlight-red` | Turn text red |
| `highlight-green` | Turn text green |
| `highlight-blue` | Turn text blue |
| `highlight-current-red` | Red only while current |
| `strike` | Strikethrough |

### Custom Order
```html
<p class="fragment" data-fragment-index="2">Second</p>
<p class="fragment" data-fragment-index="1">First</p>
```

### Nested Fragments
```html
<div class="fragment">
  <p>This appears first</p>
  <p class="fragment">This appears second (nested)</p>
</div>
```

---

## Auto-Animate

Smooth transitions between consecutive slides. Add `data-auto-animate` to both slides:

```html
<section data-auto-animate>
  <h2>Title</h2>
</section>
<section data-auto-animate>
  <h2 style="color: red;">Title</h2>
  <p>New content appears</p>
</section>
```

### Element Matching
Elements are matched between slides by:
1. **`data-id`** (explicit, highest priority): `<div data-id="box1">`
2. **Text content**: headings/paragraphs matched by text
3. **Media source**: images/videos matched by `src`

### Per-Element Timing
```html
<div data-id="box" data-auto-animate-delay="0.5" data-auto-animate-duration="0.8">
```

### Animatable Properties
Position, dimensions, opacity, color, background-color, padding, font-size, line-height, letter-spacing, border-width, border-color, border-radius, outline.

### Grouping
Use `data-auto-animate-id` to group non-consecutive auto-animate pairs:
```html
<section data-auto-animate data-auto-animate-id="group1">
```

Use `data-auto-animate-restart` to prevent animation from previous slide:
```html
<section data-auto-animate data-auto-animate-restart>
```

---

## Speaker Notes

```html
<section>
  <h2>Slide Content</h2>
  <aside class="notes">
    Speaker-only notes. Supports <strong>HTML</strong>.
    - Bullet points work
    - Timing guidance
  </aside>
</section>
```

Press **S** in the browser to open Speaker View (shows notes, next slide preview, timer).

Per-slide timing: `<section data-timing="120">` (seconds).

---

## Slide Backgrounds

```html
<!-- Solid color -->
<section data-background-color="#1a1a2e">

<!-- Image -->
<section data-background-image="path.jpg"
         data-background-size="cover"
         data-background-position="center">

<!-- Gradient -->
<section data-background-gradient="linear-gradient(to bottom, #283b95, #17b2c3)">

<!-- Video -->
<section data-background-video="video.mp4"
         data-background-video-loop
         data-background-video-muted>

<!-- Iframe -->
<section data-background-iframe="https://example.com"
         data-background-interactive>
```

Background opacity: `data-background-opacity="0.5"`

---

## Per-Slide Transitions

```html
<!-- Override the global transition for this slide -->
<section data-transition="zoom">

<!-- Different in/out transitions -->
<section data-transition="fade-in slide-out">
```

Available: `none`, `fade`, `slide`, `convex`, `concave`, `zoom`

---

## Code Highlighting

```html
<pre><code class="language-python" data-trim data-line-numbers="1,4-8">
def process(data):
    # Step 1: validate
    validate(data)
    # Step 2: transform
    result = transform(data)
    cleaned = clean(result)
    normalized = normalize(cleaned)
    return normalized
</code></pre>
```

### Step-by-Step Highlighting
Pipe-separated ranges create fragments:
```html
<pre><code data-line-numbers="1-3|4-6|7-9">
```
Each step highlights the specified lines and dims the rest.

### Attributes
- `data-trim`: Smart indentation removal
- `data-noescape`: Prevent HTML entity escaping
- `data-line-numbers`: Enable line numbers and/or highlighting

---

## Vertical Slides

Nested `<section>` elements create a vertical stack:
```html
<section>
  <section>Vertical slide 1 (top)</section>
  <section>Vertical slide 2 (below)</section>
</section>
```
Navigate down with arrow keys. Good for drill-down content.

---

## Built-in Utility Classes

| Class | Effect |
|-------|--------|
| `r-fit-text` | Auto-size text to fill the slide |
| `r-stretch` | Stretch element to fill remaining space |
| `r-stack` | Stack elements on top of each other (use with fragments) |
| `r-frame` | Add a border frame |

### r-stack Example (image swapping)
```html
<div class="r-stack">
  <img class="fragment" src="step1.png">
  <img class="fragment" src="step2.png">
  <img class="fragment" src="step3.png">
</div>
```

---

## Math (KaTeX)

Inline: `$E = mc^2$`

Display block:
```html
$$\int_0^\infty f(x)\, dx = F(\infty) - F(0)$$
```

Or explicit delimiters:
```html
\[\sum_{i=1}^{n} x_i = x_1 + x_2 + \cdots + x_n\]
```

KaTeX is loaded via CDN in the scaffold. No additional setup needed.

---

## Keyboard Shortcuts (for the presenter)

| Key | Action |
|-----|--------|
| `→` / `Space` | Next slide |
| `←` | Previous slide |
| `↓` / `↑` | Navigate vertical slides |
| `S` | Speaker view |
| `O` | Overview mode |
| `F` | Fullscreen |
| `Esc` | Exit overview/fullscreen |
| `B` / `.` | Black screen (pause) |
| `Alt+Click` | Zoom into element (zoom plugin) |
| `?` | Show keyboard shortcuts |
