# Data trust score and Trust Tiers

A way to decide, every day, whether a dataset is fit to feed reporting and AI, to explain that decision in one sentence, and to act when it changes. Each dataset gets a score from a few signals, the score and a set of hard conditions place it in a tier, a drop in tier starts an agreed escalation, and two views report the result: a daily list of exceptions for the people who fix data, and a short risk-indicator report for leadership.

## What this does not do (read first)

- **It is a design. Nothing real has run through it yet.** The weights and thresholds below are starting points with a stated reason, not values tested on data. They are marked *uncertain* until a lab or a real system has produced evidence for them. The planned test is a trust score lab on a small data platform, scored daily on one domain.
- **The score only knows the checks that exist.** A dataset with three rules that all pass can look better than one with forty rules and one failure. The coverage condition below limits this, and it does not remove it.
- **It scores datasets, not AI answers.** Whether a generated answer is right is measured by the output metrics in the [catalog](../data/). This page decides whether the data going into a report or an AI system deserves trust.
- **It is not a compliance claim.** The sources quoted here are a banking supervisor's principles and a European regulation. Following this design does not make anyone compliant with either.

## Why it matters

A dashboard, a forecast and an AI assistant can all look healthy while the table under them stopped loading two days ago. People find out from a wrong number in a meeting. A trust score moves that moment earlier and puts it in front of the person who can fix it. The Basel Committee's principles for bank risk data put the expectation plainly: "Supervisors expect banks to measure and monitor the accuracy of data and to develop appropriate escalation channels and action plans to be in place to rectify poor data quality" (S77, paragraph 40). The same need exists outside banking wherever a decision rests on data nobody is watching.

## The signals

Each dataset in scope is measured on five signals that make up the score, and one more that sets the stakes. Scope starts small: one domain and the data elements its key reports and AI systems actually use. The UK framework's advice is to "Prioritise efforts on the data which is most critical" (S75).

| Signal | What is measured | Why it is in the score |
|---|---|---|
| **Quality checks passing** | Share of the data quality rules on critical elements that passed on the latest run, reported by [dimension](README.md) (completeness, validity, uniqueness, consistency, accuracy where a reference exists) | The direct evidence that the content is right today |
| **Freshness** | Time since the last successful load, against the lag agreed with the people who use the data | Stale data looks exactly like current data on a report, so nothing flags it unless the load time is checked |
| **Ownership assigned** | A named business owner and a named steward, both still in role | Nobody can fix what nobody owns. The Basel principles ask that "Roles and responsibilities should be established as they relate to the ownership and quality of risk data" (S77, paragraph 34) |
| **Definitions certified** | Share of critical elements with an approved business definition whose review date has not passed | Two teams can read the same column differently. The Basel principles ask for a dictionary of concepts "such that data is defined consistently across an organisation" (S77, paragraph 37) |
| **Lineage known** | Whether the dataset's upstream sources are recorded (the catalog's M31 Lineage Coverage, at dataset level) | Without lineage, a failure upstream cannot be traced to the reports and models it reaches |
| **Usage** (not in the score) | Who reads the dataset: executive reports, production AI systems, other pipelines, ad hoc analysis | It decides how serious a drop is, so it drives escalation and reporting instead |

**Why usage is kept out of the score.** Popular data is not more trustworthy. If usage added points, a heavily used table could stay in a high tier while failing its checks, which is the opposite of what the people using it need. Usage answers a different question, *how much does it matter if this is wrong*, and the escalation path and the leadership view both use it.

## From signals to a score

Each signal is turned into a value from 0 to 1:

- Quality checks passing: passed rules divided by rules on critical elements.
- Freshness: 1 within the agreed lag, 0.5 up to twice the lag, 0 beyond that.
- Ownership: 1 if both roles are filled, 0.5 if one is, 0 if neither is.
- Definitions certified: certified critical elements divided by all critical elements.
- Lineage known: 1 or 0.

The score is a weighted sum on a scale of 0 to 100: quality 40, freshness 20, ownership 15, definitions 15, lineage 10. **Uncertain.** The reason for this split is that quality and freshness change from day to day and move the numbers people read, while ownership, definitions and lineage are conditions that change rarely and make problems fixable. The split has not been tested against real incidents.

The score is for trends and for comparing datasets. It does not decide the tier on its own, because an average hides exactly the failure that matters: a dataset can score 85 with its most important rule failing. The tier rules below add hard conditions for that reason.

## Trust Tiers

| Tier | Meaning | Conditions |
|---|---|---|
| **Tier 1: Trusted** | Fit for executive reporting and for AI systems in production | Score 90 or more, every critical rule passing, within the agreed lag, both owner roles filled, every critical element defined, and rules covering every critical element (the catalog's M29 Data Quality Rule Coverage at 100% for the dataset) |
| **Tier 2: Use with care** | Usable, with a visible warning | Score 70 or more and no blocking condition, but not every Tier 1 condition met |
| **Tier 3: Not fit for decisions** | Consumers are protected from it until it is fixed | Score below 70, or any blocking condition: a rule marked blocking fails, the data is more than twice the agreed lag, or no owner is assigned |
| **Unrated** | Not assessed yet, or a signal could not be measured | Shown as its own state, never as a blank and never folded into Tier 3 |

The thresholds of 90 and 70 are **uncertain**, chosen so that a single failing non-blocking rule on a dataset with good governance stays in Tier 2 rather than dropping to Tier 3.

**Why Unrated is a separate state.** A dataset that could not be measured and a dataset that failed are different problems with different owners. Folding one into the other makes coverage of the program invisible: a domain with half its datasets unmeasured would look healthier than one where everything is measured and a few fail. Consumers treat an Unrated dataset as they would a Tier 3 one, and the reports count the two separately.

**For data that feeds an AI system.** A training, evaluation or retrieval dataset for a high-risk AI system needs one more condition for Tier 1: a recorded check that it is representative of the people and situations the system will meet. The EU AI Act asks for such data to be "relevant, sufficiently representative, and to the best extent possible, free of errors and complete in view of the intended purpose" (S73, Article 10(3)), and the [dimensions page](README.md#the-dimension-ai-adds-representativeness) explains why the classic dimensions miss this. **Uncertain**: how to record that check is part of the planned evidence-record work.

**Every tier comes with its reason.** Each dataset carries one sentence, built from the conditions it fails, for example: *Tier 2 because the last load was 30 hours ago against an agreed 24, and 2 of 14 critical elements have no certified definition.* An owner who cannot see why a dataset dropped cannot fix it, and a rule-based score can always give that sentence. A model could weigh the signals more subtly, but it could not always say why. Rules come first for that reason, and AI is better kept for the judgments rules cannot make, such as reading a free-text definition for ambiguity.

## Escalation when trust drops

The path is agreed before anything fails, the way Google's example error budget policy sets in advance what happens when a service misses its target (S80). That policy also says what it is not for: it "is not intended to serve as a punishment for missing SLOs" (service level objectives, the targets it protects). The same holds here: escalation exists to protect the people using the data and to get the problem fixed.

| Step | Who | When |
|---|---|---|
| 1. Notify the owner | Business owner of the dataset | At the drop, the same day |
| 2. Involve the steward | Data steward or data governance team | If the owner has not acknowledged within one business day, or the dataset is not restored within the agreed time (**uncertain**: three business days for Tier 2, one for Tier 3 feeding executive reports or production AI) |
| 3. Protect consumers | Automatic, set per tier | Immediately, without waiting for people (below) |
| 4. Report to leadership | The leadership view | Tier 3 on a dataset with executive or AI consumers, or an exception past its agreed time |

Protecting consumers does not wait for steps 1 and 2. The three actions match the ones data pipeline tools already offer. Databricks' pipeline expectations, for example, have three: under *warn* "Invalid records are written to the target", under *drop* "Invalid records are dropped before data is written to the target", and under *fail* "Invalid records prevent the update from succeeding. Manual intervention is required before reprocessing" (S79).

- **Warn** (Tier 2): the data flows, and the warning is shown where people read it, in the catalog and on the reports built from it.
- **Quarantine** (Tier 3): failing records are held aside for review, or publication stays at the last good version. Quarantine keeps the records, where *drop* in the quote above discards them, which matters when someone has to find out what went wrong.
- **Block** (a blocking rule fails): the load stops and nothing new is published until someone intervenes.

Each drop opens an exception with an identifier, a date, an owner and a status, and it stays open until it is fixed at the source. The UK framework asks teams to "use root cause analysis to solve data quality issues at source, rather than apply temporary fixes" (S75), so an exception closes with its cause recorded, not just with the score back above the line.

## The two views

### Daily exception view (for owners and stewards)

One row per dataset that dropped a tier, is Unrated, or has an open exception:

| Column | Holds |
|---|---|
| Dataset | Name and domain |
| Consumers | Its usage: which reports, AI systems and pipelines read it |
| Tier today and yesterday | So a new drop stands out from a known one |
| Reason | The one-sentence explanation |
| Failing signals | Which rules, which lag, which missing role or definition |
| Protection in force | Warn, quarantine or block |
| Owner, steward | Named people |
| Escalation step and days open | Where the exception stands |

Sorted with datasets that have executive or AI consumers first, because usage is what makes a drop urgent.

### Leadership risk-indicator view (weekly or monthly)

A short report of key risk indicators (KRIs). The Basel Committee names key risk indicators among the risk identification and assessment tools its operational risk principles cover, and describes risk metrics as providing "early warning information to monitor ongoing performance of the business and the control environment" (S78). Its principles for risk reporting leave the timing to the readers: the board and senior management, or other recipients as appropriate, "should set the frequency of risk management report production and distribution" (S77, Principle 10).

| Indicator | What it shows |
|---|---|
| Share of critical datasets in Tier 1, by domain, with its trend | Overall health |
| Datasets in Tier 3 or Unrated that feed executive reports or AI systems in production | Where decisions currently rest on data that should not be trusted |
| Exceptions open past their agreed time | Whether escalation works |
| Median time to restore a dataset to its previous tier | How fast problems get fixed |
| Share of datasets in scope that are Unrated | How much of the program is actually measured |
| Share of tier drops the owner confirmed as a real problem | Whether the score itself can be trusted |

The last indicator measures the measurement. A score that raises many false alarms is soon ignored, and one that raises none may be blind. Owners record, for each drop, whether it was a real problem, and that ratio decides when the weights and thresholds need revising.

## Building on the scorecard

Each signal and each indicator above is a measure with a target, so it goes into the [scorecard](../business-goals/) the same way an AI metric does: the team that measures it (`owner`), the person accountable for its target (`accountable`), the target and when it was approved (`system_target`, `target_approved_on`), and the date of its next review (`next_review`). Two example rows, fictional:

| Measure | Owner | Accountable | Target | Next review |
|---|---|---|---|---|
| Share of critical Sales datasets in Tier 1 | Data governance | Head of sales operations | At least 90% by the end of the quarter | Quarterly |
| Tier drops confirmed as real problems | Data governance | Chief data officer | At least 70%; revise the weights if lower for two months | Monthly |

The same rule about ownership applies as in the scorecard: one accountable person per target, someone with the authority to act on it.

## Sources

- **S77** Basel Committee on Banking Supervision, *Principles for effective risk data aggregation and risk reporting* (2013), known as BCBS 239. Read from the Bank for International Settlements' PDF through an archived copy, because the live site refused automated access. Its page there lists the document as current.
- **S78** Basel Committee on Banking Supervision, *Revisions to the Principles for the Sound Management of Operational Risk* (2021).
- **S75** Government Data Quality Hub, *The Government Data Quality Framework* (2020).
- **S73** Regulation (EU) 2024/1689, the AI Act, Article 10.
- **S79** Databricks documentation, *Manage data quality with pipeline expectations*, read November 11, 2026.
- **S80** Google, *The Site Reliability Workbook*, Appendix B, *Example Error Budget Policy* (2018).

Every quotation on this page was checked word for word against the text of its source.
