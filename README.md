# OmniLint

> **AI Dataset Quality Auditor** — detect, report, and score quality issues in tabular and image datasets before they break your model.

[![PyPI version](https://img.shields.io/pypi/v/omnilint)](https://pypi.org/project/omnilint/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

OmniLint sits between your raw data and your ML pipeline. It runs a battery of quality checks on CSV/Parquet tabular datasets and COCO/YOLO image datasets, then produces a single **Data Quality Score (DQS)** alongside a detailed, actionable report.

---

> 📄 **Read the Full Business Case Study:**
> [How OmniLint Accelerates Digital Transformation in ML Pipelines →](./CASE_STUDY.md)

---

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [CLI](#cli)
  - [Python API](#python-api)
  - [Streamlit UI](#streamlit-ui)
- [Input Formats](#input-formats)
- [CLI Reference](#cli-reference)
- [Python API Reference](#python-api-reference)
- [Data Quality Score (DQS)](#data-quality-score-dqs)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Development](#development)
- [Changelog](#changelog)
- [License](#license)

---

## Features

### Tabular Auditing

| Check | What it detects |
|---|---|
| **Basic** | Missing values, data type mismatches, constant columns, duplicate rows |
| **Distribution** | Skewed columns (high skewness), IQR and Z-score outliers |
| **Labels** | Class imbalance, rare class warnings |
| **Leakage** | High Pearson/Spearman correlation with target, categorical leakage via Cramér's V |
| **Feature Importance** | Random-Forest probe to flag noise columns and suspiciously high-importance features |
| **Deduplication** | Exact row duplicates and near-duplicates via cosine similarity / FAISS embeddings |

### Image Auditing *(Beta)*

| Check | What it detects |
|---|---|
| **Integrity** | Corrupt files, resolution outliers, inconsistent image formats |
| **Distribution** | Brightness, contrast, and per-channel color imbalance |
| **Labels** | Label-file mismatches (images without annotations, annotations without images), class imbalance |
| **Duplicates** | Perceptual-hash (pHash) exact duplicates, CLIP-based near-duplicates |
| **Anomalies** | Blurry images (Laplacian variance), over/under-exposed images, blank images |

---

## Installation

### Base (Tabular only)

```bash
pip install omnilint
```

### With Image Support

```bash
pip install omnilint[image]
```

> **Note:** Image support pulls in `Pillow`, `opencv-python`, `imagehash`, `torch`, and `clip`. These are heavy dependencies — only install if you need image auditing.

### Development

```bash
git clone https://github.com/Audric-Nagata/OmniLint.git
cd OmniLint
pip install -e ".[dev,image]"
```

---

## Quick Start

### CLI

**Audit a CSV file with a target column:**
```bash
omnilint run dataset.csv --target label
```

**Save the report as HTML:**
```bash
omnilint run dataset.csv --target label --output report.html
```

**Audit an image dataset (YOLO format):**
```bash
omnilint run dataset/ --mode image --format yolo --output report.json
```

**Audit a COCO dataset:**
```bash
omnilint run dataset/ --mode image --format coco
```

**Fail a CI pipeline if quality is too low:**
```bash
omnilint run dataset.csv --target label --fail-below 70
```

**Run only specific checks:**
```bash
omnilint run dataset.csv --target label --checks basic,distribution,leakage
```

**Check the installed version:**
```bash
omnilint version
```

---

### Python API

**Tabular audit:**
```python
from omnilint import AuditEngine, load
from omnilint.core.engine import AuditConfig

# Load dataset
df, schema = load("dataset.csv")

# Configure the audit
config = AuditConfig(
    target_col="label",            # Column to treat as the prediction target
    checks=["basic", "distribution", "labels", "leakage", "importance", "dedup"],
    missing_threshold=0.05,        # Flag columns with >5% missing values
    dedup_threshold=0.95,          # Cosine similarity threshold for near-duplicates
)

# Run
engine = AuditEngine(df, config)
result = engine.run()

print(f"DQS: {result.quality_score}")      # e.g. 73.4
print(f"Band: {result.score_band}")         # e.g. "Fair"
print(f"Issues: {result.total_issues}")

for issue in result.issues:
    print(f"[{issue.severity.upper()}] {issue.check} — {issue.detail}")
    print(f"  ↳ {issue.suggestion}")
```

**Image audit:**
```python
from omnilint import AuditEngine, load
from omnilint.core.engine import AuditConfig

dataset, schema = load("path/to/yolo_dataset/")

config = AuditConfig(
    mode="image",
    checks=["integrity", "distribution", "labels", "duplicates", "anomalies"],
)

engine = AuditEngine(dataset, config)
result = engine.run()

print(f"DQS: {result.quality_score}")
print(f"Per-module scores: {result.module_scores}")
```

**Saving reports from the API:**
```python
from omnilint.report import builder, renderer_html, renderer_json, renderer_cli

report = builder.build(result, schema.source, schema.rows, schema.columns, mode="tabular")

renderer_cli.render(report)           # Print to terminal
renderer_html.render(report, "report.html")   # Save HTML
renderer_json.render(report, "report.json")   # Save JSON
```

---

### Streamlit UI

Launch the interactive web interface:

```bash
omnilint-ui
```

Or run it directly:

```bash
streamlit run omnilint/app/streamlit_app.py
```

Upload your CSV or image dataset folder in-browser and get an interactive visual report with charts, per-module scores, and a full issue table.

---

## Input Formats

| Mode | Format | Description |
|---|---|---|
| Tabular | `.csv` | Standard comma-separated file |
| Tabular | `.parquet` | Apache Parquet columnar format |
| Image | COCO JSON | A folder with a JSON annotations file (`instances_*.json`) plus an `images/` directory |
| Image | YOLO | A folder with a `data.yaml` (or `train/images` + `train/labels` sub-structure) |

The loader auto-detects the format by inspecting the file extension and directory structure. You can override with `--format {csv,parquet,coco,yolo}`.

---

## CLI Reference

```
omnilint run [OPTIONS] SOURCE
```

| Option | Default | Description |
|---|---|---|
| `SOURCE` | *(required)* | Path to a dataset file (CSV/Parquet) or directory (COCO/YOLO) |
| `--target TEXT` | `None` | Target/label column name (tabular mode) |
| `--mode TEXT` | `tabular` | Audit mode: `tabular` or `image` |
| `--format TEXT` | `auto` | Input format: `csv`, `parquet`, `coco`, `yolo`, `auto` |
| `--output TEXT` | `None` | Output file path; `.json` or `.html` extension selects renderer |
| `--fail-below INT` | `None` | Exit with code `1` if DQS is below this threshold (useful in CI) |
| `--checks TEXT` | `all` | Comma-separated list of checks to run (e.g. `basic,leakage`) |
| `--missing-threshold FLOAT` | `0.05` | Fraction of missing values that triggers a warning |
| `--dedup-threshold FLOAT` | `0.95` | Cosine similarity above which two rows are near-duplicates |
| `--blur-threshold FLOAT` | `100` | Laplacian variance below which an image is flagged as blurry |

---

## Python API Reference

### `load(source: str) -> tuple[DataFrame | ImageDataset, DataSchema]`

Loads any supported dataset. Returns the data object and a schema with metadata (`source`, `rows`, `columns`).

### `AuditConfig`

```python
@dataclass
class AuditConfig:
    target_col: str | None = None          # Target column (tabular)
    split_col: str | None = None           # Optional split column
    checks: list[str] = [...]              # List of check names to run
    missing_threshold: float = 0.05        # Missing value threshold
    dedup_threshold: float = 0.95          # Near-duplicate cosine threshold
    fail_below: int | None = None          # DQS failure threshold
    mode: Literal["tabular", "image"] = "tabular"
```

### `AuditEngine(data, config)`

Orchestrates the full audit. Call `.run()` to execute all configured checks and return an `AuditResult`.

### `AuditResult`

```python
@dataclass
class AuditResult:
    quality_score: float           # DQS (0–100)
    score_band: str                # "Critical" | "Poor" | "Fair" | "Good"
    total_issues: int
    issues: list[IssueRecord]      # Sorted by severity
    module_scores: dict[str, float]  # Per-module DQS breakdown
```

### `IssueRecord`

```python
@dataclass
class IssueRecord:
    check: str          # Name of the check that raised the issue
    severity: str       # "critical" | "high" | "medium" | "low"
    detail: str         # Human-readable description
    suggestion: str     # Recommended fix
    column: str | None  # Affected column (tabular)
    asset: str | None   # Affected file path (image)
```

---

## Data Quality Score (DQS)

The DQS is a single number from 0 to 100. It is computed as a **weighted penalty** across all check modules, where each module contributes based on the severity of its findings.

### Severity Penalties

| Severity | Penalty weight |
|---|---|
| Critical | 1.00 |
| High | 0.75 |
| Medium | 0.50 |
| Low | 0.25 |

### Tabular Module Weights

| Module | Weight |
|---|---|
| Basic | 25% |
| Leakage | 20% |
| Deduplication | 20% |
| Distribution | 10% |
| Labels | 5% |
| Feature Importance | 5% |

### Image Module Weights

| Module | Weight |
|---|---|
| Integrity | 30% |
| Duplicates | 25% |
| Anomalies | 20% |
| Labels | 15% |
| Distribution | 10% |

### Score Bands

| Score | Band | Recommended Action |
|---|---|---|
| 81 – 100 | ✅ **Good** | Dataset is ready for training |
| 66 – 80 | 🟡 **Fair** | Minor fixes recommended |
| 41 – 65 | 🟠 **Poor** | Major fixes required before training |
| 0 – 40 | 🔴 **Critical** | Do not train — serious data quality problems detected |

---

## Project Structure

```
OmniLint/
├── omnilint/
│   ├── __init__.py              # Public API exports & version
│   ├── core/
│   │   ├── engine.py            # AuditEngine, AuditConfig, AuditResult, IssueRecord
│   │   ├── loader.py            # load() — CSV, Parquet, COCO, YOLO loaders
│   │   └── scorer.py            # DQS calculation & weighting
│   ├── tabular/
│   │   ├── checks/
│   │   │   ├── basic.py         # Missing values, type mismatches, constants, duplicates
│   │   │   ├── distribution.py  # Skewness, IQR/Z-score outliers
│   │   │   ├── labels.py        # Class imbalance, rare classes
│   │   │   ├── leakage.py       # Pearson/Spearman/Cramér's V leakage
│   │   │   ├── importance.py    # RF probe for noise/importance
│   │   │   └── dedup.py         # Exact & FAISS near-duplicate detection
│   │   └── utils/               # Shared stats helpers, embedding utilities
│   ├── image/
│   │   ├── checks/
│   │   │   ├── integrity.py     # Corrupt files, resolution, format checks
│   │   │   ├── distribution.py  # Brightness, contrast, channel imbalance
│   │   │   ├── labels.py        # Label-image mismatch, class imbalance
│   │   │   ├── duplicates.py    # pHash exact + CLIP near-duplicates
│   │   │   └── anomalies.py     # Blur, exposure, blank image detection
│   │   └── utils/               # pHash, CLIP encoder, pixel stats helpers
│   ├── report/
│   │   ├── builder.py           # Builds a unified report object
│   │   ├── renderer_cli.py      # Rich terminal renderer
│   │   ├── renderer_html.py     # Jinja2 HTML renderer
│   │   └── renderer_json.py     # JSON renderer
│   ├── cli/
│   │   ├── main.py              # Typer CLI commands (run, version)
│   │   └── ui.py                # omnilint-ui entry point
│   ├── app/
│   │   ├── streamlit_app.py     # Main Streamlit application
│   │   └── components/          # Tabular & image UI components
│   └── templates/               # Jinja2 HTML report templates
├── examples/
│   ├── run_audit.py             # Minimal Python API example
│   ├── sample_clean.csv         # Example clean dataset
│   └── sample_dirty.csv         # Example dirty dataset (with injected issues)
├── tests/
│   ├── tabular/                 # Tabular check unit tests
│   └── image/                   # Image check unit tests
├── pyproject.toml
├── requirements.txt
└── CHANGELOG.md
```

---

## Tech Stack

### Core (always installed)

| Library | Purpose |
|---|---|
| `pandas`, `numpy`, `scipy` | Data loading and statistical analysis |
| `scikit-learn` | RF probe (feature importance), scalers |
| `faiss-cpu` | Near-duplicate vector search |
| `sentence-transformers` | Text/row embedding for semantic dedup |
| `typer`, `rich` | CLI framework and terminal output |
| `streamlit`, `plotly` | Interactive web UI and charts |
| `jinja2` | HTML report rendering |
| `pyyaml` | YOLO `data.yaml` parsing |

### Image extras (`pip install omnilint[image]`)

| Library | Purpose |
|---|---|
| `Pillow` | Image loading and pixel analysis |
| `opencv-python` | Blur detection (Laplacian), color stats |
| `imagehash` | Perceptual hashing (pHash) for exact duplicate detection |
| `torch`, `clip` | CLIP embeddings for semantic near-duplicate detection |

### Dev tools (`pip install omnilint[dev]`)

| Tool | Purpose |
|---|---|
| `pytest` | Test runner |
| `black` | Code formatter (line length 88) |
| `ruff` | Fast linter |
| `mypy` | Static type checker |
| `build`, `twine` | Package building and PyPI publishing |

---

## Development

### Running tests

```bash
pytest
```

### Formatting & linting

```bash
black omnilint/
ruff check omnilint/
mypy omnilint/
```

### Building the package

```bash
python -m build
```

### Publishing to PyPI

```bash
twine upload dist/*
```

---

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for the full release history.

---

## License

[MIT](./LICENSE) © Audric Nagata
