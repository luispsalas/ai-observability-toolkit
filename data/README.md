# Metric catalog data

42 AI metrics in one CSV file, across 11 lifecycle layers. Every other item in the toolkit refers to a metric by its `id`, so this file is the shared vocabulary.

## What this does not do (read first)

- **The metrics have not been re-audited.** They were moved over unchanged from the [AI Metrics Catalog](https://luispsalas.github.io/ai-governance-scorecard/), last updated in August 2026. Tool names and healthy-target ranges in particular may be out of date.
- **Healthy targets are rules of thumb.** They suit a typical deployment and need to be set again for each system.
- **The `toolkit_use_cases` column is empty for now.** It fills in as the use cases are written.

## Files

| File | Holds |
|---|---|
| `metrics.csv` | One row per metric, 15 columns (below) |
| `layers.csv` | The 11 layers in display order, each with a one-line description |
| `nist-ai-rmf.csv` | The 19 categories and 72 subcategories of the NIST AI RMF 1.0, verbatim, extracted from [the PDF](../sources/) by `tools/extract_nist_rmf.py`. Used by the [crosswalk](../crosswalk/). |

## Columns of `metrics.csv`

| Column | Meaning |
|---|---|
| `id` | Permanent identifier, `M01` to `M42`. A retired metric keeps its id and a replacement gets a new one, so a reference to an id never changes meaning. |
| `name` | Metric name |
| `layer` | Lifecycle layer, one of the 11 in `layers.csv` |
| `goal` | Technical Quality, Governance & Risk, or Business Value |
| `tier` | Foundational, Intermediate or Advanced: how mature a team needs to be before the metric is worth running |
| `description` | What the metric tells you |
| `calculation` | How to compute it |
| `example` | A worked value |
| `applications` | Kinds of system where the metric is commonly used |
| `when_to_implement` | The point in a project where it starts to pay off |
| `healthy_target` | A typical target range |
| `pitfalls` | How the metric misleads when read on its own |
| `tools` | Tools that compute or track it, comma-separated |
| `prerequisites` | What has to exist before it can be measured |
| `toolkit_use_cases` | Which of this toolkit's use cases use it, semicolon-separated (empty for now) |

`applications` and `toolkit_use_cases` answer different questions. The first says where a metric is generally useful, and the second says where this toolkit shows it at work.

## Checking the data

```bash
python3 tools/test_check_data.py
python3 tools/check_data.py
```

The first command proves the checker works. Each of its 17 rules must catch a planted error and miss it when switched off, and the run ends with `ALL PASSED`. The second checks the data and the crosswalk. Run both after any edit.
