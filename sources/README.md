# Sources

Primary documents this toolkit quotes or maps against, kept here so every claim can be checked against the exact version it was built from.

## NIST AI 100-1: AI Risk Management Framework (AI RMF 1.0)

| | |
|---|---|
| **Files** | [`NIST.AI.100-1.pdf`](NIST.AI.100-1.pdf), 48 pages, and [`NIST.AI.100-1.txt`](NIST.AI.100-1.txt), its text in reading order (`pdftotext`, SHA-256 `7cf380a1e7c019fa2124ed10b66e20b61bd75d90a57ae07035f4ab35d75a0516`), which `tools/check_data.py` searches to confirm quotations |
| **Citation** | Tabassi E (2023), *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*, NIST AI 100-1, National Institute of Standards and Technology, Gaithersburg, MD, https://doi.org/10.6028/NIST.AI.100-1 (Accessed October 12, 2026) |
| **Downloaded from** | https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf, the primary resource registered for the DOI in Crossref |
| **SHA-256** | `7576edb531d9848825814ee88e28b1795d3a84b435b4b797d3670eafdc4a89f1` |
| **Used by** | [`data/nist-ai-rmf.csv`](../data/nist-ai-rmf.csv) (Tables 1 to 4, extracted by [`tools/extract_nist_rmf.py`](../tools/extract_nist_rmf.py)) and the [NIST AI RMF crosswalk](../crosswalk/), whose quotations marked `AI RMF 1.0 §…` come from this file |

**Status of this version.** As of October 12, 2026, NIST's [AI RMF page](https://www.nist.gov/itl/ai-risk-management-framework) still offers version 1.0 for download and states that it "is being revised as part of the White House AI Action Plan." Everything here is pinned to 1.0. When a revision is published, the extraction and the crosswalk have to be redone against it, and this file will say so.

**Author.** The PDF's title page names no author. The name comes from the DOI's Crossref record, which lists Elham Tabassi. The citation follows NIST's recommended format for technical series publications.

**Reuse.** NIST's [copyright and licensing statement](https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications) says that works by NIST employees are not subject to copyright protection in the United States. Outside the United States, NIST grants a worldwide, royalty-free right to reprint them. This is why the PDF and the verbatim text of its tables can be included here.

**How the extracted text was checked.** All 19 categories and 72 subcategories were compared with a second, independent extraction of the same PDF (`pdftotext -raw`, which follows the document's own content order). 85 of the 91 texts match word for word. The other 6 match letter for letter: there, the second extraction drops spaces in justified lines or keeps the hyphens of words broken across lines.

## NIST AI RMF Playbook

| | |
|---|---|
| **Files** | [`NIST-AI-RMF-Playbook.json`](NIST-AI-RMF-Playbook.json) (all 72 subcategories as structured data) and [`NIST-AI-RMF-Playbook.pdf`](NIST-AI-RMF-Playbook.pdf) (147 pages) |
| **Citation** | National Institute of Standards and Technology, *NIST AI RMF Playbook*, NIST Trustworthy and Responsible AI Resource Center, https://airc.nist.gov/airmf-resources/playbook/ (Accessed October 12, 2026) |
| **Downloaded from** | https://airc.nist.gov/docs/playbook.json and https://airc.nist.gov/docs/AI_RMF_Playbook.pdf, both linked from the Playbook page that NIST's AI RMF page points to |
| **SHA-256** | JSON `aecbee3d3c8820816d295b11d10fb61324b17c25c2ff39ee95e2aa5654555bba` · PDF `65d6101d806502875aadb0fd19a75c3a9cc9a5e9461129e9398a39192d8202d2` |
| **Version** | The Playbook has no version number. The latest entry in its [audit log](https://airc.nist.gov/airmf-resources/playbook/audit-log/) is August 2023, and the PDF's own metadata gives a creation date of August 2, 2024. |
| **Used by** | The [crosswalk](../crosswalk/): links whose `basis` starts with `Playbook` quote this file's JSON, and `tools/check_data.py` confirms each quotation word for word |

**What it is.** NIST's companion to the framework: for each subcategory, an explanation, suggested actions, questions to document and references. The Playbook states that it is "neither a checklist nor set of steps to be followed in its entirety" and that its suggestions are voluntary, and the framework says "NIST plans to update the AI RMF Playbook frequently."

**Its wording differs from the framework in places.** The subcategory text in the Playbook matches the framework PDF letter for letter for 51 of the 72 subcategories. The other 21 differ in small edits (for example "processes, and procedures" where the framework says "processes, procedures, and practices", or "TEVV" written out in full). The framework PDF is the authority for the subcategory wording in this repository, and the Playbook is quoted only for its guidance.

**Reuse.** The Playbook is a NIST publication, covered by the same [statement](https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications) as the framework. Its reference lists cite other authors' work, which is not reproduced here beyond the citations themselves.
