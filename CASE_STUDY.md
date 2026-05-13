# 📊 Case Study: How OmniLint Accelerates Digital Transformation in ML Pipelines

> *A real-world look at how automated dataset auditing cuts time-to-model and prevents costly training failures.*

---

## Executive Summary

Modern machine learning projects often fail not because of bad models — but because of bad data. In a typical enterprise ML workflow, data engineers and scientists spend **40–70% of their project time** on data cleaning and validation, much of it manual and undocumented.

**OmniLint** was built to solve this problem: a single, automated Data Quality Score (DQS) engine that sits between raw data and the training pipeline, catching critical issues before they cost GPU hours, production incidents, or model failures.

This case study walks through two representative scenarios — one with **tabular data** and one with an **image dataset** — demonstrating how OmniLint surfaces issues, scores quality, and drives faster, safer model delivery.

---

## The Problem: Silent Data Failures in ML

Before tools like OmniLint, a typical data quality workflow looked like this:

```
Raw Data ──► Manual EDA ──► Ad-hoc scripts ──► Training ──► (Failure discovered late) ──► Fix & Repeat
```

Common failure modes that go undetected:

| Issue | Business Impact |
|---|---|
| Target leakage in features | Model performs perfectly in testing, fails in production |
| Near-duplicate rows | Model overfits, poor generalization |
| Class imbalance | Silent accuracy inflation; minority class performance collapses |
| Corrupt/blurry images | CV model trains on noise, degrading mAP silently |
| High-cardinality or noise columns | Longer training time, worse feature extraction |

These are not edge cases. They are routine — and they are expensive.

---

## Case Study 1: Tabular Data — Customer Churn Prediction

### 🏢 Context

A telecommunications company wanted to build a churn prediction model using 18 months of customer behavior data (~120,000 rows, 47 features). The data science team had previously shipped a model that performed well offline but degraded significantly in production within 2 weeks.

### 🔍 OmniLint Audit

```bash
omnilint run churn_dataset.csv --target churned --output report.html --fail-below 70
```

**Results — DQS: 54 / 100 (🟠 Poor)**

| Module | Score | Key Findings |
|---|---|---|
| Basic | 61 | 3 columns >20% missing; 2 constant columns |
| Leakage | 28 | `days_before_cancellation` had Pearson r=0.97 with target |
| Deduplication | 70 | 1,200 near-duplicate rows (cosine similarity > 0.95) |
| Distribution | 74 | `monthly_charges` skewness = 3.8 |
| Labels | 82 | Class imbalance: 91% non-churn / 9% churn |
| Feature Importance | 55 | 6 columns flagged as noise (RF importance < 0.001) |

### 🚨 Critical Issue: Target Leakage

```
[CRITICAL] leakage — Column 'days_before_cancellation' has Pearson correlation 0.97 with target 'churned'
  ↳ This column likely encodes future information. Remove it before training.
```

The column `days_before_cancellation` was computed retroactively in the data warehouse — it existed only for customers who had already churned. This was the reason the previous model looked perfect offline: it was essentially seeing the answer.

### ✅ Actions Taken

1. **Dropped** `days_before_cancellation` and 2 other high-leakage columns.
2. **Removed** 1,200 near-duplicate rows to prevent train/test contamination.
3. **Applied** SMOTE oversampling to address class imbalance.
4. **Imputed** missing values in the 3 flagged columns using median strategy.
5. **Dropped** 6 noise columns to reduce dimensionality.

### 📈 Outcome

| Metric | Before OmniLint | After OmniLint |
|---|---|---|
| Offline AUC-ROC | 0.98 *(leakage inflated)* | 0.84 |
| Production AUC-ROC (2 weeks) | 0.61 | 0.82 |
| Data prep time | ~3 days (manual) | ~4 hours |
| DQS after fixes | 54 | 88 ✅ Good |

> **Key insight:** The model that looked worse in offline evaluation was actually far better — because the leakage was removed. OmniLint surfaced this in minutes, not weeks.

---

## Case Study 2: Image Dataset — Retail Product Detection (YOLO)

### 🏢 Context

An e-commerce platform was training a YOLO-based object detection model to automatically tag product categories from shelf images. The dataset consisted of ~28,000 images across 12 product classes, annotated by a mix of in-house staff and outsourced annotators.

### 🔍 OmniLint Audit

```bash
omnilint run product_dataset/ --mode image --format yolo --output report.json
```

**Results — DQS: 61 / 100 (🟠 Poor)**

| Module | Score | Key Findings |
|---|---|---|
| Integrity | 73 | 214 corrupt/unreadable files; 88 resolution outliers |
| Duplicates | 42 | 3,400 pHash duplicates; 890 CLIP near-duplicates |
| Anomalies | 65 | 512 blurry images (Laplacian < 100); 143 overexposed |
| Labels | 71 | 320 images missing annotation files |
| Distribution | 80 | Moderate brightness imbalance across splits |

### 🚨 High-Impact Issue: Perceptual Duplicates Across Train/Val Split

```
[HIGH] duplicates — 890 near-duplicate image pairs detected across train and val splits (CLIP similarity > 0.92)
  ↳ Near-duplicates spanning splits cause optimistic validation metrics. Deduplicate before re-splitting.
```

Nearly 900 training images had semantically near-identical counterparts in the validation set. This inflated mAP scores and masked the model's true generalization ability.

### ✅ Actions Taken

1. **Removed** 214 corrupt image files and their orphaned label files.
2. **Deduplicated** pHash exact duplicates, retaining 1 image per group.
3. **Flagged and reviewed** CLIP near-duplicates; removed cross-split leakage.
4. **Deleted** 512 blurry images below the Laplacian threshold.
5. **Regenerated** train/val/test split after deduplication.
6. **Manually reviewed** 320 unannotated images; 190 were usable and re-annotated.

### 📈 Outcome

| Metric | Before OmniLint | After OmniLint |
|---|---|---|
| Reported mAP@50 | 0.91 | 0.79 |
| Actual mAP@50 (held-out test) | 0.73 | 0.78 |
| Dataset size (post-clean) | 28,000 | 23,400 |
| Annotation coverage | 98.9% | 100% |
| DQS after fixes | 61 | 85 ✅ Good |

> **Key insight:** The cleaned, smaller dataset produced a *better* model. Fewer but higher-quality images — with no split leakage — improved real-world detection performance by ~7% mAP.

---

## CI/CD Integration: Shifting Quality Left

Both case studies above detected issues *after* data had already been collected. A more powerful pattern is integrating OmniLint directly into your **data pipeline CI/CD**, so quality gates are enforced automatically.

```yaml
# .github/workflows/data-quality.yml
name: Dataset Quality Gate

on:
  push:
    paths:
      - 'data/**'

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install OmniLint
        run: pip install omnilint
      - name: Run Audit
        run: |
          omnilint run data/train.csv \
            --target label \
            --checks basic,leakage,dedup \
            --fail-below 75 \
            --output report.html
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: omnilint-report
          path: report.html
```

With `--fail-below 75`, any data commit that drops the DQS below 75 will **block the pipeline** — preventing bad data from ever reaching training.

---

## Summary: Business Value of OmniLint

| Dimension | Traditional Approach | With OmniLint |
|---|---|---|
| **Time to detect leakage** | Discovered in production (weeks) | Detected pre-training (minutes) |
| **Data prep time** | 3–5 days manual EDA | 2–4 hours with guided fixes |
| **Reproducibility** | Ad-hoc scripts, undocumented | Versioned config + JSON/HTML reports |
| **CI/CD integration** | Rare or manual | Native `--fail-below` threshold |
| **Auditability** | Hard to audit | Full `IssueRecord` trail per check |
| **Team alignment** | Subjective ("the data looks fine") | Objective DQS score shared across team |

---

## Conclusion

Data quality is not a one-time task — it is a continuous engineering discipline. OmniLint brings **structure, automation, and objectivity** to a process that has historically been manual, inconsistent, and expensive.

By catching leakage, duplicates, class imbalance, and image anomalies *before* training, teams ship better models faster — and trust their data.

---

> 📦 Get started: `pip install omnilint`
>
> 🔗 GitHub: [https://github.com/Audric-Nagata/OmniLint](https://github.com/Audric-Nagata/OmniLint)
>
> 📄 Back to [README](./README.md)
