# Metric catalog data

43 AI metrics in one CSV file, each placed in one area of an AI system and tagged with the trustworthiness characteristic it gives evidence for. Every other item in the toolkit refers to a metric by its `id`, so this file is the shared vocabulary.

## What this does not do (read first)

- **The audit is only partly done.** The metrics came over from the [AI Metrics Catalog](https://luispsalas.github.io/ai-governance-scorecard/) (last updated August 2026). Their structure, formulas, targets and wording were reviewed in October 2026. Checking each one against current research is under way: [`metric-audit.csv`](metric-audit.csv) records the result for every metric, and 20 of the 43 are done so far (one more, M14, was merged into M07 and retired). Until a metric's row says otherwise, treat its tool names and ranges as a starting point.
- **Healthy targets are rules of thumb.** They suit a typical deployment and need to be set again for each system. Where no general number makes sense, the target says "Set per system" and gives the rule for setting it.
- **22 of the 43 metrics rest on a judgment.** Their formulas count things ("supported claims ÷ total claims"), but deciding what counts is done by an AI judge or a human rater. The `measurement_method` column says which, so read those scores as judgments with their own error.
- **The `toolkit_use_cases` column is empty for now.** It fills in as the use cases are written.

## Files

| File | Holds |
|---|---|
| `metrics.csv` | One row per metric, 17 columns (below) |
| `areas.csv` | The 6 areas in display order, with a description of each and whether it is a known gap |
| `metric-audit.csv` | The audit result for each metric: `pending`, `assessed` (with its outcome: keep, revise, split, merge or retire) or `proposed` (a split, merge or retirement awaiting a decision), with the reason, the sources (ids in [`../sources/sources.csv`](../sources/sources.csv)) and the date |
| `nist-ai-rmf.csv` | The 19 categories and 72 subcategories of the NIST AI RMF 1.0, verbatim, extracted from [the PDF](../sources/) by `tools/extract_nist_rmf.py`. Used by the [crosswalk](../crosswalk/). |

## How the metrics are organized

Each metric sits in **one area**, chosen by the part of the AI system it measures. Five of the six areas take their names from the [OECD Framework for the Classification of AI Systems](https://www.oecd.org/en/publications/oecd-framework-for-the-classification-of-ai-systems_cb6d9eca-en.html) (2022), which the NIST AI RMF adapts for its view of the AI lifecycle. The sixth covers the running service, which those frameworks do not separate out.

| Area | What it covers | Metrics |
|---|---|---|
| Data & Input | Source and training data, retrieved context, agent memory, incoming prompts | 14 |
| AI Model | Properties of the model itself: robustness, explainability, drift in its predictions | 3 |
| Task & Output | The quality and safety of outputs, and the success of the actions the system takes | 15 |
| Application Context | Human oversight, records of decisions, adoption, satisfaction and business results | 5 |
| People & Planet | Effects on people, society and the environment, such as fairness and environmental impact | 0 (a known gap) |
| Runtime Operations | Latency, availability, errors and cost of the running service | 6 |

Each metric also carries a **`characteristic`**: the trustworthiness characteristic of the [NIST AI RMF](../sources/) (§3) it gives evidence for. The values are `valid_reliable`, `safe`, `secure_resilient`, `accountable_transparent`, `explainable_interpretable`, `privacy_enhanced` and `fair`, plus `environmental` (NIST's MEASURE 2.12) and `none` for metrics, such as cost or adoption, that bear on none of them. No metric is tagged `fair` or `environmental` yet: those are the catalog's clearest gaps, also listed in the [crosswalk](../crosswalk/).

And each carries a **`measurement_method`**, how the number is actually produced, one or more of:

| Value | Meaning | Metrics |
|---|---|---|
| `deterministic` | Counted or computed by fixed code from logs or data | 17 |
| `human_rating` | Rated by people, or scored against labels people made | 18 |
| `llm_judge` | Rated by an AI model following a rubric | 17 |
| `model_score` | Produced by a specialized model, such as an embedding or a toxicity classifier | 7 |
| `statistical` | A statistical test or divergence measure | 3 |

Counts add up to more than 43 because a metric can use more than one method.

## Columns of `metrics.csv`

| Column | Meaning |
|---|---|
| `id` | Permanent identifier (`M01`, `M02`, …). A merged or retired metric leaves this file but keeps its row in `metric-audit.csv`, and its id is never reused, so a reference to an id never changes meaning. |
| `name` | Metric name |
| `area` | One of the 6 areas in `areas.csv` |
| `goal` | Technical Quality, Governance & Risk, or Business Value |
| `tier` | Foundational, Intermediate or Advanced: how mature a team needs to be before the metric is worth running |
| `characteristic` | The NIST trustworthiness characteristic it gives evidence for, or `none` (semicolon-separated if more than one) |
| `measurement_method` | How the number is produced (values above, semicolon-separated if more than one) |
| `description` | What the metric tells you |
| `calculation` | How to compute it |
| `example` | A worked value |
| `applications` | Kinds of system where the metric is commonly used |
| `when_to_implement` | The point in a project where it starts to pay off |
| `healthy_target` | A typical target, or the rule for setting one per system |
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

The first command proves the checker works. Each of its 22 rules must catch a planted error and miss it when switched off, and the run ends with `ALL PASSED`. The second checks the data and the crosswalk, including that every area and method is one of the allowed values, that an area is empty only when marked as a known gap, that a metric's characteristic agrees with its primary links in the crosswalk, and that every audit result cites registered sources. Run both after any edit.
