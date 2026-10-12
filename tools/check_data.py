"""Check the toolkit's data and crosswalk before anything is published from them.

Usage:
  python3 tools/check_data.py            # checks this repository
  python3 tools/check_data.py ROOT       # checks ROOT/data/ and ROOT/crosswalk/

Prints one line per problem and exits 1 if there are any. Standard library only.
"""
import csv
import json
import re
import sys
from pathlib import Path

METRIC_COLUMNS = [
    "id", "name", "layer", "goal", "tier", "description", "calculation", "example",
    "applications", "when_to_implement", "healthy_target", "pitfalls", "tools",
    "prerequisites", "toolkit_use_cases",
]
LAYER_COLUMNS = ["order", "layer", "description"]
OPTIONAL = {"toolkit_use_cases"}  # filled in as use cases are written

# How many rows the checks expect to see. A check that inspects fewer rows than
# this fails loudly instead of passing quietly on an empty or truncated file.
EXPECTED_METRICS = 42
EXPECTED_LAYERS = 11
EXPECTED_NIST = (19, 72)  # AI RMF 1.0 categories, subcategories

NIST_COLUMNS = ["function", "category_id", "category", "subcategory_id", "subcategory"]
CROSSWALK_COLUMNS = ["metric_id", "subcategory_id", "relation", "uncertain", "rationale", "basis", "basis_quote"]

GOALS = {"Technical Quality", "Governance & Risk", "Business Value"}
TIERS = {"Foundational", "Intermediate", "Advanced"}
TOOLKIT_USE_CASES = {
    "privacy-gate", "ai-search", "prompt-evaluation",
    "retrieval-pipeline", "runtime-monitoring", "agent-observability",
}


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        return header, [dict(zip(header, row)) | {"_len": len(row)} for row in reader]


# Each rule takes (metric header, metric rows, layer header, layer rows) and yields messages.
def r01_headers(d):
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    if mh != METRIC_COLUMNS:
        yield f"metrics.csv header is {mh}, expected {METRIC_COLUMNS}"
    if lh != LAYER_COLUMNS:
        yield f"layers.csv header is {lh}, expected {LAYER_COLUMNS}"
    if d["nh"] != NIST_COLUMNS:
        yield f"nist-ai-rmf.csv header is {d['nh']}, expected {NIST_COLUMNS}"
    if d["xh"] != CROSSWALK_COLUMNS:
        yield f"nist-ai-rmf-crosswalk.csv header is {d['xh']}, expected {CROSSWALK_COLUMNS}"


def r02_row_counts(d):
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    if len(m) != EXPECTED_METRICS:
        yield f"metrics.csv has {len(m)} rows, expected {EXPECTED_METRICS} (update EXPECTED_METRICS when adding metrics)"
    if len(l) != EXPECTED_LAYERS:
        yield f"layers.csv has {len(l)} rows, expected {EXPECTED_LAYERS}"


def r03_row_width(d):
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    for i, row in enumerate(m, 2):
        if row["_len"] != len(mh):
            yield f"metrics.csv line {i}: {row['_len']} fields, header has {len(mh)}"


def r04_ids(d):
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    seen = set()
    for i, row in enumerate(m, 2):
        mid = row.get("id", "")
        if not re.fullmatch(r"M\d{2,}", mid):
            yield f"metrics.csv line {i}: id {mid!r} is not of the form M01"
        elif mid in seen:
            yield f"metrics.csv line {i}: id {mid} is used twice (an id names one metric forever)"
        seen.add(mid)


def r05_unique_names(d):
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    seen = {}
    for row in m:
        key = row.get("name", "").casefold()
        if key and key in seen:
            yield f"{row['id']}: name {row['name']!r} duplicates {seen[key]}"
        seen.setdefault(key, row.get("id"))


def r06_required_fields(d):
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    for row in m:
        for col in METRIC_COLUMNS:
            if col not in OPTIONAL and not row.get(col, "").strip():
                yield f"{row.get('id', '?')}: {col} is blank"


def r07_layer_known(d):
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    layers = {x.get("layer") for x in l}
    for row in m:
        if row.get("layer") and row["layer"] not in layers:
            yield f"{row['id']}: layer {row['layer']!r} is not in layers.csv"


def r08_goal_and_tier(d):
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    for row in m:
        if row.get("goal") and row["goal"] not in GOALS:
            yield f"{row['id']}: goal {row['goal']!r} is not one of {sorted(GOALS)}"
        if row.get("tier") and row["tier"] not in TIERS:
            yield f"{row['id']}: tier {row['tier']!r} is not one of {sorted(TIERS)}"


def r09_every_layer_used(d):
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    used = {row.get("layer") for row in m}
    for x in l:
        if x.get("layer") not in used:
            yield f"layer {x.get('layer')!r} has no metrics"


def r10_toolkit_use_cases(d):
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    for row in m:
        for tag in filter(None, (t.strip() for t in row.get("toolkit_use_cases", "").split(";"))):
            if tag not in TOOLKIT_USE_CASES:
                yield f"{row['id']}: toolkit use case {tag!r} is not one of {sorted(TOOLKIT_USE_CASES)}"


def r11_clean_whitespace(d):
    for name, rows in (("metrics.csv", d["m"]), ("layers.csv", d["l"]), ("nist-ai-rmf.csv", d["n"]), ("nist-ai-rmf-crosswalk.csv", d["x"])):
        for i, row in enumerate(rows, 2):
            for col, val in row.items():
                if col != "_len" and isinstance(val, str) and (val != val.strip() or "\n" in val or "​" in val):
                    yield f"{name} line {i}: {col} has stray whitespace, a line break or a zero-width space"


def r12_nist_table(d):
    cats = {r.get("category_id") for r in d["n"]}
    subs = [r.get("subcategory_id") for r in d["n"]]
    if (len(cats), len(subs)) != EXPECTED_NIST:
        yield f"nist-ai-rmf.csv has {len(cats)} categories and {len(subs)} subcategories, expected {EXPECTED_NIST}"
    for s in {s for s in subs if subs.count(s) > 1}:
        yield f"nist-ai-rmf.csv: subcategory {s} appears more than once"


def r13_crosswalk_references(d):
    metrics = {r.get("id") for r in d["m"]}
    subs = {r.get("subcategory_id") for r in d["n"]}
    for i, r in enumerate(d["x"], 2):
        if r.get("metric_id") not in metrics:
            yield f"crosswalk line {i}: metric {r.get('metric_id')!r} is not in metrics.csv"
        if r.get("subcategory_id") not in subs:
            yield f"crosswalk line {i}: subcategory {r.get('subcategory_id')!r} is not in nist-ai-rmf.csv"


def r14_crosswalk_values(d):
    for i, r in enumerate(d["x"], 2):
        if r.get("relation") not in ("primary", "supporting"):
            yield f"crosswalk line {i}: relation {r.get('relation')!r} is not primary or supporting"
        if r.get("uncertain") not in ("yes", "no"):
            yield f"crosswalk line {i}: uncertain {r.get('uncertain')!r} is not yes or no"
        if not r.get("rationale", "").strip():
            yield f"crosswalk line {i}: rationale is blank"


def r15_crosswalk_duplicates(d):
    seen = set()
    for i, r in enumerate(d["x"], 2):
        key = (r.get("metric_id"), r.get("subcategory_id"))
        if key in seen:
            yield f"crosswalk line {i}: {key[0]} is linked to {key[1]} twice"
        seen.add(key)


def r16_every_metric_mapped(d):
    mapped = {r.get("metric_id") for r in d["x"]}
    for r in d["m"]:
        if r.get("id") not in mapped:
            yield f"{r.get('id')} has no link in the crosswalk"


def _ws(s):
    return re.sub(r"\s+", " ", s).strip()


def r17_quotes_verbatim(d):
    """Every quoted basis must appear word for word in the NIST file it cites."""
    checked = 0
    for i, r in enumerate(d["x"], 2):
        basis, quote = r.get("basis", ""), r.get("basis_quote", "")
        if bool(basis) != bool(quote):
            yield f"crosswalk line {i}: basis and basis_quote must both be filled or both be blank"
            continue
        if not basis:
            continue
        checked += 1
        if basis.startswith("Playbook "):
            entry = d["playbook"].get(basis[len("Playbook "):])
            text = _ws(" ".join(entry[k] for k in ("description", "section_about", "section_actions", "section_doc"))) if entry else ""
        elif basis.startswith("AI RMF 1.0 "):
            text = d["framework"]
        else:
            yield f"crosswalk line {i}: basis {basis!r} names no known source"
            continue
        if _ws(quote) not in text:
            yield f"crosswalk line {i}: the quote is not word for word in {basis}"
    if d["x"] and not checked:
        yield "no quoted basis was checked: the crosswalk should have some"


RULES = {f.__name__.split("_")[0]: f for f in (
    r01_headers, r02_row_counts, r03_row_width, r04_ids, r05_unique_names, r06_required_fields,
    r07_layer_known, r08_goal_and_tier, r09_every_layer_used, r10_toolkit_use_cases, r11_clean_whitespace,
    r12_nist_table, r13_crosswalk_references, r14_crosswalk_values, r15_crosswalk_duplicates, r16_every_metric_mapped,
    r17_quotes_verbatim,
)}


def check(root, disabled=()):
    """Return a list of (rule id, message). `disabled` switches rules off, for the tests."""
    root = Path(root)
    d = {}
    d["mh"], d["m"] = read(root / "data/metrics.csv")
    d["lh"], d["l"] = read(root / "data/layers.csv")
    d["nh"], d["n"] = read(root / "data/nist-ai-rmf.csv")
    d["xh"], d["x"] = read(root / "crosswalk/nist-ai-rmf-crosswalk.csv")
    with open(root / "sources/NIST-AI-RMF-Playbook.json", encoding="utf-8") as f:
        d["playbook"] = {x["title"].strip(): x for x in json.load(f)}
    # Words split across lines in the PDF text are rejoined before matching.
    d["framework"] = _ws(re.sub(r"-\n(?=[a-z])", "", (root / "sources/NIST.AI.100-1.txt").read_text(encoding="utf-8")))
    return [(rid, msg) for rid, rule in RULES.items() if rid not in disabled for msg in rule(d)]


def main():
    data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    problems = check(data_dir)
    for rid, msg in problems:
        print(f"[{rid}] {msg}")
    print(f"{len(problems)} problem(s) in {data_dir}" if problems else f"OK: {data_dir} passes all {len(RULES)} rules")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
