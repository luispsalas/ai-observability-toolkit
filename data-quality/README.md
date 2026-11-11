# Data quality dimensions for AI

Data quality has a well-tested vocabulary: accuracy, completeness, consistency, timeliness, validity, uniqueness. It was written for stored records, where a value is either right or wrong and a rule can check it. This page takes each of those dimensions and asks what it becomes when the thing being judged is text an AI system generated, and which metrics in this toolkit give evidence for it.

The companion page, [Data trust score and Trust Tiers](trust-tiers.md), uses these dimensions to decide whether a dataset is fit to feed reporting and AI.

## What this does not do (read first)

- **The generated-output readings are mine, not a standard's.** The six definitions are quoted from a published framework. What each one becomes for generated text is my reading, given with its reason, and the calls that could go either way are marked *uncertain*. None of those readings is taken from a standard.
- **It covers six dimensions, not every one in use.** ISO/IEC 25012, the international data quality model, has fifteen characteristics. It is a paid standard, so its list is not reproduced here (see [Sources](#sources)). The six used here are the set the UK government adopted from DAMA UK, and they are free to quote.
- **A mapped metric is evidence, not a measurement of the dimension.** Faithfulness says whether an answer stays within its sources. It does not say whether those sources were right, which is a question about the stored data, upstream.
- **Nothing here has been run on a real system yet.** The worked use cases planned for this toolkit will test it.

## Why it matters

A data quality rule assumes that the same record gives the same verdict every time: a date of birth is in the future or it is not. Generated output breaks that assumption in two ways. The same question can produce a different answer tomorrow, so a single check proves less. And an answer can be fluent, well formatted and wrong, so the checks that catch broken records (format, range, missing values) pass while the content fails. Teams that already run data quality programs need to know which of their habits carry over to AI output, which change meaning, and where they need a new kind of evidence.

## The six classic dimensions

The definitions below are quoted from the UK's [Government Data Quality Framework](https://www.gov.uk/government/publications/the-government-data-quality-framework/the-government-data-quality-framework) (Government Data Quality Hub, 2020; S75), which takes its six core dimensions "as defined by DAMA UK" (the UK chapter of DAMA International, the data management association). The framework itself says this "is not a prescriptive list" and that "a seventh dimension may be added to measure the quality of any specialist data". That permission matters below.

| Dimension | Definition (quoted) |
|---|---|
| Accuracy | "Accuracy describes the degree to which data matches reality." |
| Completeness | "Completeness describes the degree to which records are present." |
| Uniqueness | "Uniqueness describes the degree to which there is no duplication in records." |
| Consistency | "Consistency describes the degree to which values in a data set do not contradict other values representing the same entity." |
| Timeliness | "Timeliness describes the degree to which the data is an accurate reflection of the period that they represent, and that the data and its values are up to date." |
| Validity | "Validity describes the degree to which the data is in the range and format expected." |

## What each becomes for generated output

| Dimension | For stored data, a rule checks | For generated output, the question becomes | Evidence in this toolkit | Call |
|---|---|---|---|---|
| Accuracy | A value against a trusted reference | Is each statement in the answer true, and is it supported by the sources the system was given? These are two different questions: an answer can be faithful to a wrong document. NIST calls the failure confabulation, "confidently stated but erroneous or false content" (S74). | M07 Faithfulness, M44 Factual Precision, M09 Answer Correctness, M10 Citation Precision | settled |
| Completeness | Required records and fields are present | Does the answer contain everything the question needs? On the retrieval side, did the system fetch everything needed to answer? | M02 Context Recall, M43 Citation Recall, M30 Metadata Completeness for the documentation of the data itself | **uncertain**: no metric in the catalog measures whether an answer leaves out something it should have said; M09 catches it only when a reference answer exists |
| Uniqueness | No entity is stored twice | Duplicates move upstream: the same passage indexed several times crowds out other evidence in retrieval, and the answer repeats one source while looking like it rests on several. | None | **uncertain**: a gap. Duplicate detection belongs in the retrieval index's own data quality rules (M29 Data Quality Rule Coverage counts whether such rules exist) |
| Consistency | Two records about one entity do not contradict | Does the system give compatible answers to the same question asked twice, or reworded? Does an answer contradict its own sources, or itself? | M11 Semantic Similarity (against a reference), M22 Agent Task Completion Rate when reported as success in all of several runs | **uncertain**: no metric measures agreement between repeated answers directly |
| Timeliness | The data reflects the current period, within an agreed lag | Does the answer reflect the current state of things? Two clocks matter: when the model's training data ends, and when the retrieval index was last refreshed. | M34 Data Drift Score, indirectly | **uncertain**: freshness of the index is a dataset property, scored in [Trust Tiers](trust-tiers.md), not an output metric |
| Validity | Values are in the expected range and format | Is the output in the form downstream code expects (a schema, a label set, a tool call with the right arguments)? This is the dimension that carries over most directly, because it can still be checked by a rule. | M45 Tool Call Correctness, M36 Error Rate (which counts a success code with wrong content as an error) | settled |

**The reason behind the pattern.** Validity and the format side of accuracy stay rule-checkable, because they are about shape. Accuracy of content, completeness and consistency become judgments: they need a reference answer, a judge model or a person, and the [metric catalog](../data/) says for each metric which of those it uses (`measurement_method`). That is the line this toolkit draws between data quality and AI evaluation.

## The dimension AI adds: representativeness

For the data used to train, validate and test a high-risk AI system, the European Union's AI Act asks for more than the six dimensions cover. Article 10(3) (S73) says those data sets "shall be relevant, sufficiently representative, and to the best extent possible, free of errors and complete in view of the intended purpose."

"Free of errors" and "complete" map onto accuracy, validity and completeness. "Relevant" and "sufficiently representative" do not map onto any of the six. A data set can be accurate, complete, unique, consistent, timely and valid, and still describe only some of the people a system will be used on. Article 10(2)(f) asks for an "examination in view of possible biases", which is the same gap seen from the other side, and NIST's Generative AI Profile lists "performance disparities between sub-groups or languages, possibly due to non-representative training data" under harmful bias (S74).

So for AI, the seventh dimension the UK framework allows for is **representativeness**: whether the data covers the groups, languages and situations the system will meet, in proportions that do not distort its results. The catalog has no metric for it yet. The [crosswalk](../crosswalk/) records the related finding that fairness and bias (MEASURE 2.11 in NIST's framework) has no metric, and both are open items.

## Sources

- **S75** Government Data Quality Hub, *The Government Data Quality Framework* (2020), GOV.UK. Quoted for the six definitions. Crown copyright, published under the Open Government Licence v3.0. GOV.UK records no change to it since first publication on December 3, 2020 (checked November 11, 2026).
- **S76** ISO/IEC 25012:2008, *Data quality model*. ISO's [page for the standard](https://www.iso.org/standard/35736.html) says it "categorizes quality attributes into fifteen characteristics considered by two points of view: inherent and system dependent" and that it was last reviewed and confirmed in 2025, so it is current. The fifteen are not listed here because the standard is sold by ISO and its online preview requires accepting ISO's terms of use.
- **S73** Regulation (EU) 2024/1689, the AI Act, Article 10, read on EUR-Lex.
- **S74** NIST AI 600-1, the Generative AI Profile, for the definitions of confabulation and harmful bias.

Every quotation on this page was checked word for word against the text of its source.
