# NIST AI RMF crosswalk

The toolkit's 44 metrics mapped onto the 72 subcategories of the NIST AI Risk Management Framework (AI RMF 1.0). It shows where each metric can serve as evidence for the framework, and where the framework asks for something no metric in the catalog provides.

**Files:** [`nist-ai-rmf-crosswalk.csv`](nist-ai-rmf-crosswalk.csv) (86 links, one row per metric and subcategory) · [`../data/nist-ai-rmf.csv`](../data/nist-ai-rmf.csv) (the framework's 19 categories and 72 subcategories, verbatim) · [`../data/metrics.csv`](../data/metrics.csv) (the metrics) · [the framework itself](../sources/)

## What this does not do (read first)

- **It is not a compliance assessment.** A metric linked to a subcategory can supply evidence for it. Collecting that evidence does not by itself meet the subcategory, which usually also asks for a process, a decision or documentation.
- **It is one person's mapping, checked against NIST's own guidance.** Every link is a judgment written with its reason. The links that were in doubt were checked against the NIST AI RMF Playbook, and 18 now quote the NIST passage they rest on. 6 of the 86 links remain uncertain and are listed at the end. No independent reviewer has checked them yet.
- **It covers AI RMF 1.0 only.** NIST states that version 1.0 "is being revised as part of the White House AI Action Plan" (checked October 12, 2026). The Generative AI Profile (NIST AI 600-1) is not mapped yet and is planned for the next version. The Playbook was used to check links, not mapped as a separate document.
- **It maps the catalog as it stands.** The metrics are being re-audited against current research ([`../data/metric-audit.csv`](../data/metric-audit.csv)), and until a metric has been audited, a gap here can be a gap in this catalog rather than in measurement practice.

## How to read it

Each row of the CSV links one metric to one subcategory:

| Column | Meaning |
|---|---|
| `relation` | **primary**: the metric's value is direct evidence for what the subcategory asks for. **supporting**: the metric is an input to that activity but does not satisfy it on its own. |
| `uncertain` | **yes** where the call could reasonably go the other way. The reason is in the rationale. |
| `rationale` | Why the link holds, written against the subcategory's own wording. |
| `basis` | Where a NIST text supports the link beyond the subcategory's wording: `Playbook <subcategory>` for the [AI RMF Playbook](../sources/), or `AI RMF 1.0 §<section>` for the framework itself. Blank where the subcategory's wording is the only basis. |
| `basis_quote` | The supporting passage, word for word. `tools/check_data.py` fails if it is not found verbatim in the cited source. |

To find the evidence for a subcategory, filter the CSV by `subcategory_id`. To find what a metric can support, filter by `metric_id`.

## Method

1. The framework text was extracted from the PDF of NIST AI 100-1 and checked against a second, independent extraction ([details](../sources/)). Every subcategory is quoted verbatim in `data/nist-ai-rmf.csv`, so each link can be read against the exact words it maps to.
2. Each metric was read against every subcategory in the MEASURE function, then against the rest of the framework. A link was recorded only where the metric's output is something the subcategory's activity would use.
3. The links in doubt, and the whole crosswalk, were then read against the [NIST AI RMF Playbook](../sources/), NIST's companion guidance with suggested actions for every subcategory. That review changed 12 links, removed 1 and added 5. Where the Playbook names what a metric measures, the link quotes it.
4. The tables below are generated from the CSV files by `tools/build_crosswalk_summary.py`, and `tools/check_data.py` checks that every link points at a real metric and a real subcategory.

## Findings

**Metrics evidence the MEASURE function and little else.** 10 of the 11 subcategories with any primary evidence are in MEASURE. GOVERN and MAP ask mostly for policies, roles, context and documentation, which a metric cannot show: none of the 19 GOVERN subcategories and 13 of the 18 MAP subcategories have a metric. That is expected, and it is the useful point for anyone building an AI governance program on metrics: a dashboard covers roughly one function out of four.

**The 46 subcategories with no metric are mostly not missing metrics.** The framework describes itself as "outcome-focused and non-prescriptive": it lists outcomes to achieve and defines no metrics of its own, and many of those outcomes are not measurable things. Sorted by what they actually ask for, the 46 fall into three groups:

- **43 ask for something other than a metric:** policies, assigned roles, training, documented context, risk tolerances, consultation. That is all 19 GOVERN subcategories, 13 in MAP, 5 in MANAGE and 6 in MEASURE (1.1 to 1.3, 2.1, 2.2 and 4.1). They are met with other kinds of assets, such as templates, procedures and documented decisions, which this toolkit can offer but a metric catalog cannot.
- **1 is a real metric gap:** fairness and bias (MEASURE 2.11), described below.
- **2 are hard by nature:** MEASURE 2.13 asks whether the measurement itself works, and MEASURE 3.2 covers risks for which "metrics are not yet available".

So "metrics reach 26 of 72 subcategories" is a map of where metrics belong, not a coverage score. Three subcategories that do have a link would also be stronger with metrics NIST's Playbook names and the catalog lacks: energy, water and emissions indicators (MEASURE 2.12), appeal and feedback-participation rates (MEASURE 3.3), and comparison with simpler models or human baselines (MEASURE 3.1).

**The catalog is weighted toward performance, measured on test sets.** 19 of the 44 metrics link to MEASURE 2.3 (performance measured in conditions like deployment), and 10 of them link to nothing else. NIST's guidance for that subcategory warns that performance measured on test data alone is insufficient, and asks for measurement in the deployment context with the people who use the system, and for the differences between the test setting and deployment to be documented. Retrieval and agent metrics in particular say a great deal about how well the system works on a test set and little about its other trustworthiness characteristics.

**NIST asks for comparisons the catalog cannot make.** The Playbook's guidance for MEASURE 3.1 asks to compare an AI system with simpler or traditional models and with human baseline performance. No metric in the catalog does this.

**Three gaps inside MEASURE matter most:**

- **Fairness and bias (MEASURE 2.11) has no metric.** It is the clearest gap in the catalog. The Playbook names established starting points (demographic parity, equalized odds, equal opportunity) and calls for context-specific metrics developed with affected communities.
- **Whether the metrics themselves work (MEASURE 2.13) has no metric.** The framework asks for the effectiveness of the measurement to be evaluated. Nothing in the catalog measures its own measures.
- **Risks that current techniques cannot measure (MEASURE 3.2) have no metric,** by definition. This is the question behind the toolkit's planned item on improving what can't be graded.

**Environmental impact (MEASURE 2.12) has only a proxy.** NIST asks for indicators of energy and water consumption and emissions. Token consumption tracks usage, which relates to energy only loosely, and is listed as an uncertain call.

**Content safety waits for the Generative AI Profile.** The framework defines safety as not endangering human life, health, property or the environment. The catalog's toxicity, policy-violation and refusal metrics are linked to MEASURE 2.6 on a broader reading and marked uncertain until the Profile, which treats harmful content directly, is mapped.

**Every metric links somewhere.** All 44 have at least one link, and 38 provide primary evidence for at least one subcategory. The other 6 only support.

## Summary tables

<!-- GENERATED: do not edit by hand -->

### Coverage by function

| Function | Subcategories | With primary evidence | Supporting only | No metric |
|---|---|---|---|---|
| GOVERN | 19 | 0 | 0 | 19 |
| MAP | 18 | 0 | 5 | 13 |
| MEASURE | 22 | 10 | 3 | 9 |
| MANAGE | 13 | 1 | 7 | 5 |
| **All** | **72** | **11** | **15** | **46** |

### Coverage by category

Each subcategory is shown as its id, marked **bold** where at least one metric is primary evidence, plain where metrics only support it, and ~~struck~~ where no metric links to it.

| Category | Subcategories |
|---|---|
| **GOVERN 1**: Policies, processes, procedures, and practices across the organization related to the mapping, measuring, and managing of AI risks are in place, transparent, and implemented effectively. | ~~1.1~~ · ~~1.2~~ · ~~1.3~~ · ~~1.4~~ · ~~1.5~~ · ~~1.6~~ · ~~1.7~~ |
| **GOVERN 2**: Accountability structures are in place so that the appropriate teams and individuals are empowered, responsible, and trained for mapping, measuring, and managing AI risks. | ~~2.1~~ · ~~2.2~~ · ~~2.3~~ |
| **GOVERN 3**: Workforce diversity, equity, inclusion, and accessibility processes are prioritized in the mapping, measuring, and managing of AI risks throughout the lifecycle. | ~~3.1~~ · ~~3.2~~ |
| **GOVERN 4**: Organizational teams are committed to a culture that considers and communicates AI risk. | ~~4.1~~ · ~~4.2~~ · ~~4.3~~ |
| **GOVERN 5**: Processes are in place for robust engagement with relevant AI actors. | ~~5.1~~ · ~~5.2~~ |
| **GOVERN 6**: Policies and procedures are in place to address AI risks and benefits arising from third-party software and data and other supply chain issues. | ~~6.1~~ · ~~6.2~~ |
| **MAP 1**: Context is established and understood. | ~~1.1~~ · ~~1.2~~ · ~~1.3~~ · ~~1.4~~ · ~~1.5~~ · ~~1.6~~ |
| **MAP 2**: Categorization of the AI system is performed. | ~~2.1~~ · ~~2.2~~ · 2.3 |
| **MAP 3**: AI capabilities, targeted usage, goals, and expected benefits and costs compared with appropriate benchmarks are understood. | 3.1 · 3.2 · ~~3.3~~ · ~~3.4~~ · 3.5 |
| **MAP 4**: Risks and benefits are mapped for all components of the AI system including third-party software and data. | 4.1 · ~~4.2~~ |
| **MAP 5**: Impacts to individuals, groups, communities, organizations, and society are characterized. | ~~5.1~~ · ~~5.2~~ |
| **MEASURE 1**: Appropriate methods and metrics are identified and applied. | ~~1.1~~ · ~~1.2~~ · ~~1.3~~ |
| **MEASURE 2**: AI systems are evaluated for trustworthy characteristics. | ~~2.1~~ · ~~2.2~~ · **2.3** · **2.4** · **2.5** · **2.6** · **2.7** · **2.8** · **2.9** · **2.10** · ~~2.11~~ · 2.12 · ~~2.13~~ |
| **MEASURE 3**: Mechanisms for tracking identified AI risks over time are in place. | **3.1** · ~~3.2~~ · 3.3 |
| **MEASURE 4**: Feedback about efficacy of measurement is gathered and assessed. | ~~4.1~~ · **4.2** · 4.3 |
| **MANAGE 1**: AI risks based on assessments and other analytical output from the MAP and MEASURE functions are prioritized, responded to, and managed. | **1.1** · ~~1.2~~ · ~~1.3~~ · ~~1.4~~ |
| **MANAGE 2**: Strategies to maximize AI benefits and minimize negative impacts are planned, prepared, implemented, documented, and informed by input from relevant AI actors. | 2.1 · 2.2 · ~~2.3~~ · 2.4 |
| **MANAGE 3**: AI risks and benefits from third-party entities are managed. | 3.1 · 3.2 |
| **MANAGE 4**: Risk treatments, including response and recovery, and communication plans for the identified and measured AI risks are documented and monitored regularly. | 4.1 · ~~4.2~~ · 4.3 |

### Most-linked subcategories

| Subcategory | Metrics linked | Of which primary |
|---|---|---|
| MEASURE 2.3 | 19 | 18 |
| MEASURE 2.5 | 11 | 5 |
| MEASURE 2.4 | 8 | 6 |
| MEASURE 2.6 | 5 | 3 |
| MEASURE 2.8 | 5 | 1 |

### Uncertain calls (6 of 86 links)

| Metric | Subcategory | Relation | Why it is uncertain |
|---|---|---|---|
| M15 Toxicity Score | MEASURE 2.6 | primary | Read broadly, harmful content is a safety risk; the framework defines safety as endangering life, health, property or the environment, so the fit is settled when the Generative AI Profile is mapped. |
| M16 Safety Violation Rate | MEASURE 2.6 | primary | Policy breaches are safety failures only where the policy protects life, health, property or the environment; settled when the Generative AI Profile is mapped. |
| M17 Refusal Accuracy | MEASURE 2.6 | primary | Refusing unsafe requests is a way to fail safely, which the subcategory names; whether the requests endanger anyone in the framework's sense is settled with the Generative AI Profile. |
| M19 Token Consumption | MEASURE 2.12 | supporting | NIST asks for energy, water and emissions indicators; token use is only a proxy for them. |
| M35 Availability/Uptime | MANAGE 3.1 | supporting | When the model is a third-party service its availability is one risk to monitor, but NIST frames the monitoring around trustworthiness characteristics, not uptime. |
| M38 User Satisfaction Score | MEASURE 3.3 | supporting | NIST asks to measure participation in feedback and appeal processes; a satisfaction score is feedback but not a problem-reporting or appeal channel. |

<!-- END GENERATED -->

## Related

- [`../data/`](../data/): the metrics and the framework text this crosswalk joins
- [`../sources/`](../sources/): the NIST AI RMF 1.0 PDF, its citation and how its text was checked
- From the [Applied AI Concepts](https://luispsalas.github.io/applied-ai-concepts/) wiki: [Evaluation](https://luispsalas.github.io/applied-ai-concepts/concepts/evaluation.html) · [Observability](https://luispsalas.github.io/applied-ai-concepts/concepts/observability.html)
