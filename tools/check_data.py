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
    "id", "name", "area", "goal", "tier", "characteristic", "measurement_method", "description",
    "calculation", "example", "applications", "when_to_implement", "healthy_target", "pitfalls",
    "tools", "prerequisites", "toolkit_use_cases",
]
AREA_COLUMNS = ["order", "area", "known_gap", "description"]
OPTIONAL = {"toolkit_use_cases"}  # filled in as use cases are written

# How many rows the checks expect to see. A check that inspects fewer rows than
# this fails loudly instead of passing quietly on an empty or truncated file.
EXPECTED_METRICS = 43
EXPECTED_AREAS = 6
EXPECTED_NIST = (19, 72)  # AI RMF 1.0 categories, subcategories

NIST_COLUMNS = ["function", "category_id", "category", "subcategory_id", "subcategory"]
CROSSWALK_COLUMNS = ["metric_id", "subcategory_id", "relation", "uncertain", "rationale", "basis", "basis_quote"]

GOALS = {"Technical Quality", "Governance & Risk", "Business Value"}
TIERS = {"Foundational", "Intermediate", "Advanced"}
# NIST AI RMF 1.0 trustworthiness characteristics (§3), plus environmental impact
# (MEASURE 2.12); "none" when a metric gives evidence for none of them.
CHARACTERISTICS = {
    "valid_reliable", "safe", "secure_resilient", "accountable_transparent",
    "explainable_interpretable", "privacy_enhanced", "fair", "environmental", "none",
}
# Which crosswalk subcategory stands for which characteristic.
CHARACTERISTIC_OF = {
    "MEASURE 2.5": "valid_reliable", "MEASURE 2.6": "safe", "MEASURE 2.7": "secure_resilient",
    "MEASURE 2.8": "accountable_transparent", "MEASURE 2.9": "explainable_interpretable",
    "MEASURE 2.10": "privacy_enhanced", "MEASURE 2.11": "fair", "MEASURE 2.12": "environmental",
}
MEASUREMENT_METHODS = {"deterministic", "model_score", "llm_judge", "human_rating", "statistical"}

AUDIT_COLUMNS = ["metric_id", "status", "outcome", "reason", "sources", "assessed_on"]
AUDIT_STATUSES = {"pending", "proposed", "assessed"}  # proposed = a split, merge or retirement awaiting a decision
AUDIT_OUTCOMES = {"keep", "revise", "split", "merge", "retire"}
SOURCE_COLUMNS = ["id", "title", "authors", "year", "identifier", "url", "kind"]
SOURCE_KINDS = {"standard", "preprint", "paper", "regulation", "documentation", "report"}
TOOLKIT_USE_CASES = {
    "privacy-gate", "ai-search", "prompt-evaluation",
    "retrieval-pipeline", "runtime-monitoring", "agent-observability",
}


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        return header, [dict(zip(header, row)) | {"_len": len(row)} for row in reader]


# Each rule takes the loaded tables (metrics, areas, NIST, crosswalk) and yields messages.
def r01_headers(d):
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    if mh != METRIC_COLUMNS:
        yield f"metrics.csv header is {mh}, expected {METRIC_COLUMNS}"
    if lh != AREA_COLUMNS:
        yield f"areas.csv header is {lh}, expected {AREA_COLUMNS}"
    if d["nh"] != NIST_COLUMNS:
        yield f"nist-ai-rmf.csv header is {d['nh']}, expected {NIST_COLUMNS}"
    if d["xh"] != CROSSWALK_COLUMNS:
        yield f"nist-ai-rmf-crosswalk.csv header is {d['xh']}, expected {CROSSWALK_COLUMNS}"


def r02_row_counts(d):
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    if len(m) != EXPECTED_METRICS:
        yield f"metrics.csv has {len(m)} rows, expected {EXPECTED_METRICS} (update EXPECTED_METRICS when adding metrics)"
    if len(l) != EXPECTED_AREAS:
        yield f"areas.csv has {len(l)} rows, expected {EXPECTED_AREAS}"


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


def r07_area_known(d):
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    areas = {x.get("area") for x in l}
    for row in m:
        if row.get("area") and row["area"] not in areas:
            yield f"{row['id']}: area {row['area']!r} is not in areas.csv"


def r08_goal_and_tier(d):
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    for row in m:
        if row.get("goal") and row["goal"] not in GOALS:
            yield f"{row['id']}: goal {row['goal']!r} is not one of {sorted(GOALS)}"
        if row.get("tier") and row["tier"] not in TIERS:
            yield f"{row['id']}: tier {row['tier']!r} is not one of {sorted(TIERS)}"


def r09_areas_used_or_known_gaps(d):
    """An area is empty exactly when it is marked as a known gap, so a metric moved
    out by mistake, or a gap that has since been filled, is reported."""
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    used = {row.get("area") for row in m}
    for x in l:
        gap = x.get("known_gap")
        if gap not in ("yes", "no"):
            yield f"area {x.get('area')!r}: known_gap {gap!r} is not yes or no"
        elif gap == "no" and x.get("area") not in used:
            yield f"area {x.get('area')!r} has no metrics but is not marked as a known gap"
        elif gap == "yes" and x.get("area") in used:
            yield f"area {x.get('area')!r} is marked as a known gap but has metrics"


def r10_toolkit_use_cases(d):
    mh, m, lh, l = d["mh"], d["m"], d["lh"], d["l"]
    for row in m:
        for tag in filter(None, (t.strip() for t in row.get("toolkit_use_cases", "").split(";"))):
            if tag not in TOOLKIT_USE_CASES:
                yield f"{row['id']}: toolkit use case {tag!r} is not one of {sorted(TOOLKIT_USE_CASES)}"


def r11_clean_whitespace(d):
    for name, rows in (("metrics.csv", d["m"]), ("areas.csv", d["l"]), ("nist-ai-rmf.csv", d["n"]), ("nist-ai-rmf-crosswalk.csv", d["x"]),
                       ("metric-audit.csv", d["a"]), ("sources.csv", d["s"])):
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


def _parts(value):
    return [p.strip() for p in value.split(";") if p.strip()]


def r18_characteristics(d):
    for row in d["m"]:
        parts = _parts(row.get("characteristic", ""))
        for p in parts:
            if p not in CHARACTERISTICS:
                yield f"{row.get('id')}: characteristic {p!r} is not one of {sorted(CHARACTERISTICS)}"
        if "none" in parts and len(parts) > 1:
            yield f"{row.get('id')}: characteristic 'none' cannot be combined with others"


def r19_measurement_methods(d):
    for row in d["m"]:
        for p in _parts(row.get("measurement_method", "")):
            if p not in MEASUREMENT_METHODS:
                yield f"{row.get('id')}: measurement_method {p!r} is not one of {sorted(MEASUREMENT_METHODS)}"


def r20_characteristic_matches_crosswalk(d):
    """A primary crosswalk link to a characteristic's MEASURE subcategory means the
    metric must carry that characteristic."""
    tags = {row.get("id"): set(_parts(row.get("characteristic", ""))) for row in d["m"]}
    for i, r in enumerate(d["x"], 2):
        want = CHARACTERISTIC_OF.get(r.get("subcategory_id"))
        if want and r.get("relation") == "primary" and want not in tags.get(r.get("metric_id"), {want}):
            yield f"crosswalk line {i}: {r.get('metric_id')} is primary evidence for {r.get('subcategory_id')} but its characteristic does not include {want}"


def r21_metric_audit(d):
    """One audit row per metric; a decided or proposed row has an outcome, a reason,
    sources that exist in sources.csv, and a date."""
    if d["ah"] != AUDIT_COLUMNS:
        yield f"metric-audit.csv header is {d['ah']}, expected {AUDIT_COLUMNS}"
        return
    ids = [r.get("metric_id") for r in d["a"]]
    known = {r.get("id") for r in d["s"]}
    for m in d["m"]:
        n = ids.count(m.get("id"))
        if n != 1:
            yield f"{m.get('id')} has {n} rows in metric-audit.csv, expected 1"
    # A metric merged or retired leaves metrics.csv but keeps its audit row, so its id is never reused.
    active = {m.get("id") for m in d["m"]}
    for r in d["a"]:
        gone = r.get("outcome") in ("merge", "retire")
        if r.get("metric_id") not in active and not gone:
            yield f"metric-audit: {r.get('metric_id')} is not in metrics.csv and is not recorded as merged or retired"
        if r.get("metric_id") in active and gone:
            yield f"metric-audit: {r.get('metric_id')} is recorded as {r.get('outcome')}d but is still in metrics.csv (a retired id is never reused)"
    for mid in {x for x in ids if ids.count(x) > 1}:
        yield f"metric-audit: {mid} has more than one row"
    for i, r in enumerate(d["a"], 2):
        st, out = r.get("status"), r.get("outcome", "")
        if st not in AUDIT_STATUSES:
            yield f"metric-audit line {i}: status {st!r} is not one of {sorted(AUDIT_STATUSES)}"
        elif st == "pending":
            if out or r.get("reason") or r.get("sources") or r.get("assessed_on"):
                yield f"metric-audit line {i}: a pending row must be blank apart from its id and status"
        else:
            if out not in AUDIT_OUTCOMES:
                yield f"metric-audit line {i}: outcome {out!r} is not one of {sorted(AUDIT_OUTCOMES)}"
            if not r.get("reason", "").strip():
                yield f"metric-audit line {i}: a {st} row needs a reason"
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", r.get("assessed_on", "")):
                yield f"metric-audit line {i}: assessed_on {r.get('assessed_on')!r} is not a date"
            srcs = _parts(r.get("sources", ""))
            if not srcs:
                yield f"metric-audit line {i}: a {st} row needs at least one source"
            for s in srcs:
                if s not in known:
                    yield f"metric-audit line {i}: source {s!r} is not in sources/sources.csv"


def r22_sources_registry(d):
    if d["sh"] != SOURCE_COLUMNS:
        yield f"sources.csv header is {d['sh']}, expected {SOURCE_COLUMNS}"
        return
    seen = set()
    for i, r in enumerate(d["s"], 2):
        sid = r.get("id", "")
        if not re.fullmatch(r"S\d{2,}", sid):
            yield f"sources.csv line {i}: id {sid!r} is not of the form S01"
        elif sid in seen:
            yield f"sources.csv line {i}: id {sid} is used twice (an id names one source forever)"
        seen.add(sid)
        if not r.get("url", "").startswith("https://"):
            yield f"sources.csv line {i}: url {r.get('url')!r} is not an https link"
        if r.get("kind") not in SOURCE_KINDS:
            yield f"sources.csv line {i}: kind {r.get('kind')!r} is not one of {sorted(SOURCE_KINDS)}"


RULES = {f.__name__.split("_")[0]: f for f in (
    r01_headers, r02_row_counts, r03_row_width, r04_ids, r05_unique_names, r06_required_fields,
    r07_area_known, r08_goal_and_tier, r09_areas_used_or_known_gaps, r10_toolkit_use_cases, r11_clean_whitespace,
    r12_nist_table, r13_crosswalk_references, r14_crosswalk_values, r15_crosswalk_duplicates, r16_every_metric_mapped,
    r17_quotes_verbatim, r18_characteristics, r19_measurement_methods, r20_characteristic_matches_crosswalk,
    r21_metric_audit, r22_sources_registry,
)}


def check(root, disabled=()):
    """Return a list of (rule id, message). `disabled` switches rules off, for the tests."""
    root = Path(root)
    d = {}
    d["mh"], d["m"] = read(root / "data/metrics.csv")
    d["lh"], d["l"] = read(root / "data/areas.csv")
    d["nh"], d["n"] = read(root / "data/nist-ai-rmf.csv")
    d["xh"], d["x"] = read(root / "crosswalk/nist-ai-rmf-crosswalk.csv")
    d["ah"], d["a"] = read(root / "data/metric-audit.csv")
    d["sh"], d["s"] = read(root / "sources/sources.csv")
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
