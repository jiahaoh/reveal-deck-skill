# YAML Deck Schema

Define slide content and layout in a YAML file, then build with:

```bash
python scripts/build_from_yaml.py deck.yaml
python scripts/build_from_yaml.py deck.yaml --output ./my-deck --theme dark
```

---

## Top-Level Fields

```yaml
title: "Presentation Title"    # required — used in <title> tag
theme: swiss                    # optional — swiss, dark, warm, minimal, contrast (default: swiss)
output: ./deck                  # optional — output directory (default: ./deck)
slides: [...]                   # required — list of slide definitions
```

---

## Slide Types

Every slide entry is a YAML mapping with one of these keys:

| Key | Purpose |
|---|---|
| `template: <name>` | Use a built-in template and supply content fields |
| `divider: "Section Title"` | Shorthand for a section-divider slide |
| `layout: "description"` | Describe a custom layout in natural language (Claude fills it in) |
| `stack: [...]` | Vertical slide stack (nested list of slides) |

All slide types accept an optional `notes:` field for speaker notes.

---

## Template Reference

### title

Opening slide with title, subtitle, author, and date.

```yaml
- template: title
  title: "Deep Learning for Drug Discovery"
  subtitle: "Novel Architectures"        # optional
  author: "Jane Doe, MIT"                # optional
  date: "February 2026"                  # optional
```

### divider (section-divider)

Shorthand form:
```yaml
- divider: "Background & Motivation"
```

Full form with custom label:
```yaml
- template: divider
  title: "Background & Motivation"
  label: "Part 1"                        # optional, auto-numbered by default
```

### overview

System components, pipeline stages, architecture summaries. All sub-sections are optional — include only what you need.

```yaml
- template: overview
  title: "System Architecture"
  modules_label: "Core Components"       # optional section heading
  modules:                               # optional, any number of items
    - title: "Encoder"
      description: "GNN-based structure encoding"
    - title: "Predictor"
      description: "Multi-task regression head"
  pipeline_label: "Data Flow"            # optional section heading
  pipeline:                              # optional, list of step names
    - "Input"
    - "Encode"
    - "Predict"
    - "Output"
  stats:                                 # optional, any number of items
    - value: "94.2%"
      label: "AUC-ROC"
    - value: "< 50ms"
      label: "Inference"
```

### table

Tabular data with column headers and rows.

```yaml
- template: table
  title: "Benchmark Results"
  label: "MoleculeNet Comparison"        # optional table caption
  columns: ["Dataset", "Our Model", "Baseline"]
  rows:
    - ["BBBP", "94.2", "89.1"]
    - ["Tox21", "87.5", "82.3"]
    - ["HIV", "80.1", "75.2"]
```

### problem-solution

Split view with problem on the left, solution on the right.

```yaml
- template: problem-solution
  title: "Addressing Latency"
  problem:
    label: "Problem"                     # optional
    title: "High Inference Latency"
    description: "P95 latency exceeds 500ms under load"
    points:                              # optional, any number
      - "Bottleneck in attention layers"
      - "No batching for concurrent requests"
      - "Synchronous preprocessing"
  solution:
    label: "Solution"                    # optional
    title: "Optimized Pipeline"
    description: "Reduced P95 to 45ms with three changes"
    points:
      - "Flash Attention 2 integration"
      - "Dynamic batching with padding"
      - "Async preprocessing pipeline"
```

### key-findings

Numbered takeaways in a 2-column grid. Auto-numbered 01, 02, etc.

```yaml
- template: key-findings
  title: "Key Takeaways"
  label: "Summary"                       # optional
  findings:                              # any number of items
    - title: "Performance"
      description: "7-point improvement over baseline"
    - title: "Efficiency"
      description: "3x faster inference with quantization"
    - title: "Generalization"
      description: "Consistent gains across 5 datasets"
```

### comparison

Side-by-side evaluation with label/value pairs.

```yaml
- template: comparison
  title: "Method Comparison"
  column_a:
    title: "Approach A"
    items:                               # any number of items
      - label: "Accuracy"
        value: "92.1%"
      - label: "Speed"
        value: "45ms"
  column_b:
    title: "Approach B"
    items:
      - label: "Accuracy"
        value: "89.3%"
      - label: "Speed"
        value: "120ms"
```

### timeline

Sequential steps with numbered progression.

```yaml
- template: timeline
  title: "Experimental Protocol"
  label: "Methods"                       # optional
  steps:                                 # any number of steps
    - title: "Data Collection"
      description: "Gathered 1.2M compounds from ChEMBL"
    - title: "Preprocessing"
      description: "SMILES canonicalization and 3D conformer generation"
    - title: "Training"
      description: "5-fold CV with early stopping"
    - title: "Evaluation"
      description: "Held-out test set + external validation"
```

### reference

Glossary-style definitions in a 2-column grid.

```yaml
- template: reference
  title: "Key Definitions"
  label: "Glossary"                      # optional
  definitions:                           # any number of items
    - term: "AUC-ROC"
      description: "Area under the receiver operating characteristic curve"
    - term: "SMILES"
      description: "Simplified molecular-input line-entry system"
```

### notes

Reading notes with a main section and sidebar.

```yaml
- template: notes
  title: "Summary & References"
  main:                                  # list of sections
    - heading: "Key Points"
      items:
        - "Novel architecture outperforms baselines"
        - "Scalable to large compound libraries"
        - "Open-source implementation available"
    - heading: "Limitations"
      items:
        - "Tested on small-molecule datasets only"
        - "Requires 3D conformer generation"
  sidebar:
    title: "References"
    items:
      - "Smith et al. (2025) Nature"
      - "Chen et al. (2024) ICML"
      - "github.com/example/repo"
```

### panels

Tabbed side-by-side panels with optional images.

```yaml
- template: panels
  title: "Framework Comparison"
  panel_a:
    tab: "PyTorch"
    heading: "Strengths"
    points:
      - "Dynamic computation graphs"
      - "Pythonic API"
      - "Strong research ecosystem"
    image: "pytorch-logo.png"            # optional
    image_alt: "PyTorch logo"            # optional
  panel_b:
    tab: "JAX"
    heading: "Strengths"
    points:
      - "Functional transformations"
      - "XLA compilation"
      - "Native TPU support"
```

### code

Code walkthrough with syntax highlighting.

```yaml
- template: code
  title: "API Example"
  language: python
  code: |
    from model import Predictor

    predictor = Predictor.load("checkpoint.pt")
    result = predictor.predict(smiles="CCO")
    print(f"Toxicity: {result.score:.3f}")
  line_highlights: "3|4-5"              # optional, pipe-separated ranges
  caption: "Basic usage of the prediction API"  # optional
```

### chart

Chart.js data visualization. The `chart` field accepts a standard Chart.js configuration object.

```yaml
- template: chart
  title: "Performance Across Datasets"
  chart:
    type: bar
    data:
      labels: ["BBBP", "Tox21", "HIV", "BACE", "ClinTox"]
      datasets:
        - label: "Our Model"
          data: [94.2, 87.5, 80.1, 88.3, 91.7]
          backgroundColor: ["#111", "#333", "#555", "#777", "#999"]
    options:
      plugins:
        legend:
          position: bottom
```

### image

Full-bleed or contained image slide.

```yaml
- template: image
  src: "figures/architecture.png"
  alt: "Model architecture diagram"
  caption: "Figure 1: Overall architecture"  # optional
  contain: true                              # optional, default false (full-bleed)
```

---

## Custom Layouts

Describe any layout in natural language. The script generates a placeholder that Claude fills in using the available CSS classes from `components.md`.

```yaml
- layout: "Two columns: left has a bullet list of key features, right has a code snippet"
  title: "Design Principles"
  content:                               # freeform data for Claude
    features:
      - "Type-safe API with generics"
      - "Zero-copy serialization"
      - "Async-first design"
    code_snippet:
      language: rust
      code: "fn predict(input: &Molecule) -> Score { ... }"
  notes: "Walk through each principle"
```

The `content` field is freeform — structure it however makes sense for the described layout. Claude reads the layout description and content data to generate appropriate HTML.

---

## Vertical Stacks

Group slides into a vertical stack (navigate with up/down arrows):

```yaml
- stack:
    - template: table
      title: "Results Overview"
      columns: ["Metric", "Value"]
      rows:
        - ["Accuracy", "94.2%"]
        - ["F1 Score", "0.91"]
    - template: chart
      title: "Results Visualization"
      chart:
        type: bar
        data:
          labels: ["Accuracy", "F1"]
          datasets:
            - label: "Score"
              data: [94.2, 91.0]
              backgroundColor: ["#111", "#333"]
```

---

## CLI Overrides

Command-line arguments override YAML values:

```bash
python scripts/build_from_yaml.py deck.yaml --theme dark --output ./my-deck
```

| YAML field | CLI flag | Default |
|---|---|---|
| `theme` | `--theme` | swiss |
| `output` | `--output` | ./deck |
