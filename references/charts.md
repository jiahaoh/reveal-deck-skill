# Chart.js Integration

Chart.js is loaded via CDN in every scaffolded deck. Charts are initialized automatically from `data-chart` attributes on `<canvas>` elements.

---

## Basic Usage

```html
<div class="chart-container">
  <canvas data-chart='{
    "type": "bar",
    "data": {
      "labels": ["A", "B", "C", "D"],
      "datasets": [{
        "label": "Score",
        "data": [85, 92, 78, 95],
        "backgroundColor": ["#111", "#444", "#777", "#aaa"]
      }]
    },
    "options": {
      "responsive": true,
      "maintainAspectRatio": false
    }
  }'></canvas>
</div>
```

**Required**: Always set `"maintainAspectRatio": false` so the chart fills its container.

**Required**: Always wrap `<canvas>` in a `.chart-container` div (provides `flex: 1; position: relative; min-height: 0`).

---

## Chart Types

### Bar Chart
```json
{
  "type": "bar",
  "data": {
    "labels": ["Model A", "Model B", "Model C"],
    "datasets": [{
      "label": "Accuracy (%)",
      "data": [92.1, 88.5, 95.3],
      "backgroundColor": ["#111", "#555", "#999"]
    }]
  },
  "options": {
    "responsive": true,
    "maintainAspectRatio": false,
    "scales": { "y": { "beginAtZero": false, "min": 80 } }
  }
}
```

### Horizontal Bar
Set `"indexAxis": "y"` in options.

### Line Chart
```json
{
  "type": "line",
  "data": {
    "labels": ["Epoch 1", "Epoch 2", "Epoch 3", "Epoch 4", "Epoch 5"],
    "datasets": [{
      "label": "Loss",
      "data": [2.5, 1.8, 1.2, 0.8, 0.5],
      "borderColor": "#111",
      "backgroundColor": "rgba(0,0,0,0.05)",
      "fill": true,
      "tension": 0.3
    }]
  },
  "options": { "responsive": true, "maintainAspectRatio": false }
}
```

### Pie / Doughnut
```json
{
  "type": "doughnut",
  "data": {
    "labels": ["Category A", "Category B", "Category C"],
    "datasets": [{
      "data": [40, 35, 25],
      "backgroundColor": ["#111", "#666", "#bbb"]
    }]
  },
  "options": {
    "responsive": true,
    "maintainAspectRatio": false,
    "plugins": { "legend": { "position": "right" } }
  }
}
```

### Scatter
```json
{
  "type": "scatter",
  "data": {
    "datasets": [{
      "label": "Samples",
      "data": [
        {"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 5, "y": 3}
      ],
      "backgroundColor": "#111"
    }]
  },
  "options": { "responsive": true, "maintainAspectRatio": false }
}
```

### Radar
```json
{
  "type": "radar",
  "data": {
    "labels": ["Accuracy", "Speed", "Memory", "Scalability", "Ease of Use"],
    "datasets": [{
      "label": "Tool A",
      "data": [90, 75, 60, 85, 70],
      "borderColor": "#111",
      "backgroundColor": "rgba(0,0,0,0.1)"
    }, {
      "label": "Tool B",
      "data": [70, 90, 80, 60, 85],
      "borderColor": "#888",
      "backgroundColor": "rgba(0,0,0,0.05)"
    }]
  },
  "options": { "responsive": true, "maintainAspectRatio": false }
}
```

---

## Layout Patterns

### Full-Slide Chart
```html
<div class="content">
  <div class="chart-container">
    <canvas data-chart='...'></canvas>
  </div>
</div>
```

### Half-Width (Chart + Text)
```html
<div class="content">
  <div class="split-row">
    <div class="split-col">
      <div class="chart-container">
        <canvas data-chart='...'></canvas>
      </div>
    </div>
    <div class="split-col">
      <h3>Key Takeaway</h3>
      <p>Description of what the chart shows.</p>
    </div>
  </div>
</div>
```

### Two Charts Side-by-Side
```html
<div class="content">
  <div class="split-row">
    <div class="split-col" style="position:relative; min-height:0">
      <canvas data-chart='...'></canvas>
    </div>
    <div class="split-col" style="position:relative; min-height:0">
      <canvas data-chart='...'></canvas>
    </div>
  </div>
</div>
```

---

## Styling Tips

### Theme-Aware Colors
Use theme token values in chart configs for consistency. Common mappings:

| Swiss | Dark | Warm | Minimal | Contrast |
|-------|------|------|---------|----------|
| `#111` | `#58a6ff` | `#8b4513` | `#2563eb` | `#fbbf24` |
| `#444` | `#8b949e` | `#8b7355` | `#6b7280` | `#a0a0a0` |
| `#999` | `#6e7681` | `#a89279` | `#9ca3af` | `#737373` |

### Font Matching
```json
"plugins": {
  "legend": {
    "labels": {
      "font": { "family": "'IBM Plex Sans'", "size": 11 }
    }
  }
},
"scales": {
  "x": { "ticks": { "font": { "family": "'IBM Plex Mono'", "size": 10 } } },
  "y": { "ticks": { "font": { "family": "'IBM Plex Mono'", "size": 10 } } }
}
```

### Grid Lines
```json
"scales": {
  "x": { "grid": { "color": "rgba(0,0,0,0.08)" } },
  "y": { "grid": { "color": "rgba(0,0,0,0.08)" } }
}
```

---

## PNG Export Note

When exporting slides to PNG, Chart.js animations may not complete in time. The export script waits 300ms per slide. If charts appear incomplete, increase the wait time in `export_slides.py`.
