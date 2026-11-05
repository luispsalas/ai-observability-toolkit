# Metrics and business goals

Start from the question you need answered, find the metrics that answer it, and turn them into a scorecard your team can own. The people who fund an AI system ask whether it is used, whether it helps and what it costs. They rarely ask for context precision by name, so this page connects the two.

## What this does not do (read first)

- **The questions are a starting set, not a complete list.** There are 15, written so that every metric in the catalog answers at least one. Your system will raise questions of its own.
- **The worked example is fictional.** "Atlas" shows how a filled-in scorecard reads. Its system, numbers and owners are invented, so it shows the format and none of the real difficulty. Use cases in this toolkit will add real scorecards.
- **A metric's card gives a rule for its target, not your target.** Most cards say "set per system" and explain how. Your scorecard records the target you chose and why.
- **The template does not measure anything.** It is a plan for who measures what, how often and against which target.

## Why it matters

A dashboard of 45 metric names is hard to read for anyone outside the team that built the system, and hard to act on for anyone inside it. Starting from a question does three things. It limits the scorecard to metrics someone will use, it gives each metric a reader, and it makes clear when a number is good enough. The old AI Metrics Catalog had a short goal-to-questions table and a fill-in template, and both were among the things that worked. This page brings them back, built on the audited metrics.

## How to use it

1. **Pick the questions your system has to answer** from the table below, and add your own.
2. **Take the metrics listed for each question.** Begin with the ones marked *(F)*, the Foundational tier, which suit a system from its first release. Add an Intermediate or Advanced metric only when it answers a question you actually have.
3. **Copy the [scorecard template](scorecard-template.csv)** into a spreadsheet and keep the rows you chose. For each, write the target you set for your system and when it was approved, the team that measures it, the person accountable for it, and the date of its next review.
4. **Review by that date**, record the current value and a note on what changed, and set the next date.

There is no recommended number of metrics. The old catalog suggested 20 to 25, a figure tied to a layer scheme the toolkit no longer uses and backed by no source. The 17 Foundational metrics are a reasonable first set, and the questions decide what comes next.

## Questions and the metrics that answer them

Questions are grouped by the goal they serve: Business Value, Technical Quality, or Governance & Risk. *(F)* marks a Foundational metric. The same data is in [`../data/business-questions.csv`](../data/business-questions.csv), with a short note on how the metrics answer each question.

<!-- GENERATED: do not edit by hand -->

| Goal | Question | Metrics that answer it |
|---|---|---|
| Business Value | **Q01** Are people using it, and are they satisfied with it? | M41 Adoption Rate<br>M38 User Satisfaction Score *(F)* |
| Business Value | **Q02** Is it improving the result it was built for, compared with not using it? | M39 Business Outcome Lift |
| Business Value | **Q03** What does a unit of work cost, and does that fit the business case? | M20 Cost per Request *(F)*<br>M19 Token Consumption *(F)* |
| Technical Quality | **Q04** Does it find the right information to answer from? | M01 Context Precision *(F)*<br>M02 Context Recall *(F)*<br>M03 Context Relevance *(F)*<br>M05 MRR (Mean Reciprocal Rank) *(F)*<br>M06 NDCG<br>M25 Memory Retrieval Accuracy |
| Technical Quality | **Q05** Are its answers correct and supported by its sources? | M07 Faithfulness *(F)*<br>M08 Answer Relevance *(F)*<br>M09 Answer Correctness<br>M11 Semantic Similarity<br>M44 Factual Precision *(F)* |
| Technical Quality | **Q06** Does it hold up when inputs are messy or change over time? | M04 Noise Sensitivity<br>M34 Data Drift Score<br>M33 Model Drift Score |
| Technical Quality | **Q07** Do its agents finish tasks reliably and use their tools correctly? | M22 Agent Task Completion Rate<br>M21 Tool Call Success Rate<br>M45 Tool Call Correctness<br>M23 Agent Handoff Success Rate<br>M24 Planning Accuracy |
| Technical Quality | **Q08** Is it fast and available enough for the people who use it? | M18 Latency (P50/P95/P99) *(F)*<br>M40 Time to First Token (TTFT) *(F)*<br>M35 Availability/Uptime *(F)*<br>M36 Error Rate *(F)* |
| Technical Quality | **Q09** Do changes to its prompts make it better or worse? | M12 Prompt Success Rate *(F)* |
| Governance & Risk | **Q10** Does it keep personal and sensitive data where it belongs? | M27 PII Detection Recall<br>M28 PII Detection Precision<br>M26 Data Classification Accuracy |
| Governance & Risk | **Q11** Can it be attacked, or made to produce harmful content? | M13 Prompt Injection Detection Rate<br>M16 Safety Violation Rate<br>M15 Toxicity Score *(F)* |
| Governance & Risk | **Q12** Does it refuse what it should, and only that? | M17 Refusal Accuracy<br>M46 Over-Refusal Rate |
| Governance & Risk | **Q13** Can a reviewer trace and explain what it did? | M42 Audit Trail Coverage<br>M32 Explainability Score<br>M10 Citation Precision<br>M43 Citation Recall |
| Governance & Risk | **Q14** Is the data it depends on governed and documented? | M29 Data Quality Rule Coverage<br>M30 Metadata Completeness *(F)*<br>M31 Lineage Coverage |
| Governance & Risk | **Q15** Do people stay in control of the decisions that matter? | M37 Human Override Rate |

<!-- END GENERATED -->

## The scorecard template

[`scorecard-template.csv`](scorecard-template.csv) has one row per metric, Foundational first. The first eight columns come from the catalog and the rest are yours to fill in.

| Column | Holds |
|---|---|
| `tier`, `metric_id`, `metric_name`, `area`, `characteristic` | The metric, as in [`../data/metrics.csv`](../data/metrics.csv) |
| `definition` | What the metric measures, in one line (the card's description) |
| `answers_questions` | The questions above that the metric answers |
| `card_target` | The card's rule or starting point for a target |
| `system_target` | The target you set for your system |
| `target_approved_on` | When the accountable person approved that target |
| `current_value` | The latest value, updated at each review |
| `owner` | The team that measures the metric and keeps it current |
| `accountable` | The person who answers for the target and has the authority to change it or act on it (a named person in a real scorecard) |
| `next_review` | The date of the next review |
| `notes` | Trends, blockers, planned changes |

The template is generated from the data by `tools/build_scorecard.py`, so it changes when a card changes and never drifts from the catalog.

### Who owns a metric

The columns separate the team that measures a metric from the person accountable for its target, because the sources ask for both:

- The NIST AI Risk Management Framework asks that roles for measuring AI risk be documented and clear "to individuals and teams throughout the organization" (GOVERN 2.1). Its Playbook adds that accountability "ensures that a specific team and individual is responsible" (GOVERN 2.3).
- Google's SRE workbook says a reliability target "needs to be owned by someone in the organization who is empowered to make tradeoffs", usually the product owner. It asks each target's record to name who approved it, when, and when it will next be reviewed. ([Implementing SLOs](https://sre.google/workbook/implementing-slos/), where SLO stands for service level objective.)
- For high-risk systems, the European Union's AI Act requires deployers to "assign human oversight to natural persons who have the necessary competence, training and authority" ([Article 26(2)](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32024R1689)). That makes accountability for oversight metrics, such as human override rate (M37), a named person's by law.

None of them says every metric needs its own person. One person can be accountable for several metrics, as long as they have the authority to act on each.

## Worked example: Atlas (fictional)

[`atlas-example.csv`](atlas-example.csv) is the scorecard of an invented internal support assistant. It answers staff questions from a human resources and IT knowledge base and files tickets through an agent. It tracks 17 metrics chosen from 12 questions, mostly Foundational plus those its questions required. Each row names a measuring team and an accountable role; the roles stand in for the named people a real scorecard would list.

A few rows show how a scorecard is read rather than just filled in:

- **Satisfaction looks fine and still cannot be read alone.** The score is 4.1 of 5, but only 8% of users answer the question, so the team looks to the pilot's measured lift (Q02) before drawing conclusions.
- **Repeated runs change the picture.** Ticket filing succeeds 88% of the time in a single run and 78% when it must succeed in all three, which is the number the team tracks.
- **One metric is off track, and the note says why.** Over-refusal is 7.5% against a 5% target, because the assistant refuses most questions about medical leave.

## Checks

`tools/check_data.py` checks this page's data along with the rest of the toolkit. Every question must name real metrics, every metric must answer at least one question, the template must match what `tools/build_scorecard.py` generates, and every row of the example must use a metric's current name under a question that lists it, name an accountable role, and give its approval and next-review dates.
