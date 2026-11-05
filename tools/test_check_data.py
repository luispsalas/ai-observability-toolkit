"""Prove check_data.py works: every rule must catch a planted error, and the
error must go unnoticed when that rule alone is switched off (which shows the
rule is needed, not just that it fires).

Run: python3 tools/test_check_data.py   (ends with ALL PASSED)
"""
import csv
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FILES = ["data/metrics.csv", "data/areas.csv", "data/nist-ai-rmf.csv", "crosswalk/nist-ai-rmf-crosswalk.csv",
         "sources/NIST-AI-RMF-Playbook.json", "sources/NIST.AI.100-1.txt",
         "data/metric-audit.csv", "sources/sources.csv", "data/business-questions.csv",
         "business-goals/scorecard-template.csv", "business-goals/atlas-example.csv"]


def edit_rows(name, change):
    def apply(d):
        path = next(d / f for f in FILES if f.endswith("/" + name))
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        change(rows)
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f, lineterminator="\n").writerows(rows)
    return apply


def set_cell(name, row, col, value):
    def change(rows):
        rows[row][rows[0].index(col)] = value
    return edit_rows(name, change)


def regenerate_template(d):
    """Rebuild the derived template after a planted change, as an author would with tools/build_scorecard.py."""
    _, metrics = check_data.read(d / "data/metrics.csv")
    _, questions = check_data.read(d / "data/business-questions.csv")
    with open(d / "business-goals/scorecard-template.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(check_data.TEMPLATE_COLUMNS)
        w.writerows(check_data.scorecard_rows(metrics, questions))


def drop_metric_from_questions(mid):
    return edit_rows("business-questions.csv", lambda r: [x.__setitem__(3, ";".join(i for i in x[3].split(";") if i != mid)) for x in r[1:]])


# The id of the last metric in the file, so a fixture deletes a row by identity, not by position.
with open(ROOT / "data/metrics.csv", newline="", encoding="utf-8") as _f:
    LAST = list(csv.reader(_f))[-1][0]

# Rule id -> (what is planted, how). Row 1 is the first data row.
FAULTS = {
    "r01": ("a renamed column", edit_rows("metrics.csv", lambda r: r[0].__setitem__(r[0].index("toolkit_use_cases"), "use_cases"))),
    "r02": ("a metric deleted along with its links and audit row", lambda d: (
             edit_rows("metrics.csv", lambda r: r.pop())(d),
             edit_rows("nist-ai-rmf-crosswalk.csv", lambda r: [r.remove(x) for x in [x for x in r if x[0] == LAST]])(d),
             edit_rows("metric-audit.csv", lambda r: [r.remove(x) for x in [x for x in r if x[0] == LAST]])(d),
             drop_metric_from_questions(LAST)(d),
             edit_rows("atlas-example.csv", lambda r: [r.remove(x) for x in [x for x in r if x[1] == LAST]])(d))),
    "r03": ("a row with an extra field", edit_rows("metrics.csv", lambda r: r[5].append("stray"))),
    "r04": ("a duplicated id, with its links renamed and its audit row removed", lambda d: (
             edit_rows("metrics.csv", lambda r: [x.__setitem__(0, "M01") for x in r if x[0] == "M13"])(d),
             edit_rows("nist-ai-rmf-crosswalk.csv", lambda r: [x.__setitem__(0, "M01") for x in r if x[0] == "M13"])(d),
             edit_rows("metric-audit.csv", lambda r: [r.remove(x) for x in [x for x in r if x[0] == "M13"]])(d),
             drop_metric_from_questions("M13")(d))),
    "r05": ("a duplicated name", set_cell("metrics.csv", 3, "name", "context precision")),
    "r06": ("a blank required field", set_cell("metrics.csv", 4, "pitfalls", "")),
    "r07": ("an area that does not exist", set_cell("metrics.csv", 5, "area", "Retrieval")),
    "r08": ("a tier outside the scale", set_cell("metrics.csv", 6, "tier", "Expert")),
    "r09": ("an area left with no metrics", edit_rows("metrics.csv", lambda r: [row.__setitem__(2, "AI Model") for row in r[1:] if row[2] == "Runtime Operations"])),
    "r10": ("an unknown use-case tag", set_cell("metrics.csv", 7, "toolkit_use_cases", "privacy-gate;search")),
    "r11": ("a line break inside a field", set_cell("metrics.csv", 8, "example", "two\nlines")),
    "r12": ("an unlinked subcategory deleted", edit_rows("nist-ai-rmf.csv", lambda r: r.pop(1))),
    "r13": ("a link to a subcategory that does not exist", set_cell("nist-ai-rmf-crosswalk.csv", 3, "subcategory_id", "MEASURE 2.14")),
    "r14": ("a blank rationale", set_cell("nist-ai-rmf-crosswalk.csv", 4, "rationale", "")),
    "r15": ("a link entered twice", edit_rows("nist-ai-rmf-crosswalk.csv", lambda r: r.insert(6, list(r[5])))),
    "r17": ("one word changed inside a NIST quote", edit_rows("nist-ai-rmf-crosswalk.csv",
             lambda r: [x.__setitem__(6, x[6].replace("frequency", "rate")) for x in r if x[0] == "M37" and x[1] == "MEASURE 4.2"])),
    "r18": ("a characteristic outside the list", set_cell("metrics.csv", 18, "characteristic", "trustworthy")),
    "r19": ("a measurement method outside the list", set_cell("metrics.csv", 19, "measurement_method", "vibes")),
    "r20": ("a characteristic that contradicts the crosswalk", set_cell("metrics.csv", 15, "characteristic", "valid_reliable")),
    "r21": ("an assessed row citing a source that is not registered", set_cell("metric-audit.csv", 7, "sources", "S03;S99")),
    "r22": ("a source registered twice under one id", set_cell("sources.csv", 16, "id", "S15")),
    "r23": ("a question naming a metric that does not exist", set_cell("business-questions.csv", 1, "metric_ids", "M41;M38;M99")),
    "r24": ("a hand edit to the generated template", set_cell("scorecard-template.csv", 1, "card_target", "≥ 0.5")),
    "r25": ("an example row with a status outside the scale", set_cell("atlas-example.csv", 1, "status", "great")),
    "r16": ("a metric's only link deleted", edit_rows("nist-ai-rmf-crosswalk.csv", lambda r: [r.remove(x) for x in [x for x in r if x[0] == "M11"]])),
}


def main():
    failures = 0
    clean = check_data.check(ROOT)
    if clean:
        print(f"FAIL: the real data is not clean to start with: {clean[:3]}")
        sys.exit(1)
    if set(FAULTS) != set(check_data.RULES):
        print(f"FAIL: rules without a test: {sorted(set(check_data.RULES) - set(FAULTS))}")
        sys.exit(1)
    for rid, (what, plant) in FAULTS.items():
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            for f in FILES:
                (d / f).parent.mkdir(exist_ok=True)
                shutil.copy(ROOT / f, d / f)
            plant(d)
            if rid != "r24":
                regenerate_template(d)
            fired = {r for r, _ in check_data.check(d)}
            without = check_data.check(d, disabled={rid})
        caught, missed = rid in fired, not without
        ok = caught and missed
        failures += not ok
        note = "" if ok else ("  <- rule did not fire" if not caught else f"  <- also caught by {sorted({r for r, _ in without})}")
        print(f"{'ok  ' if ok else 'FAIL'} {rid}: {what}: caught={caught}, unnoticed when off={missed}{note}")
    print("ALL PASSED" if not failures else f"{failures} FAILED")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
