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
         "data/metric-audit.csv", "sources/sources.csv"]


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


# The id of the last metric in the file, so a fixture deletes a row by identity, not by position.
with open(ROOT / "data/metrics.csv", newline="", encoding="utf-8") as _f:
    LAST = list(csv.reader(_f))[-1][0]

# Rule id -> (what is planted, how). Row 1 is the first data row.
FAULTS = {
    "r01": ("a renamed column", edit_rows("metrics.csv", lambda r: r[0].__setitem__(r[0].index("toolkit_use_cases"), "use_cases"))),
    "r02": ("a metric deleted along with its links and audit row", lambda d: (
             edit_rows("metrics.csv", lambda r: r.pop())(d),
             edit_rows("nist-ai-rmf-crosswalk.csv", lambda r: [r.remove(x) for x in [x for x in r if x[0] == LAST]])(d),
             edit_rows("metric-audit.csv", lambda r: [r.remove(x) for x in [x for x in r if x[0] == LAST]])(d))),
    "r03": ("a row with an extra field", edit_rows("metrics.csv", lambda r: r[5].append("stray"))),
    "r04": ("a duplicated id, with its links renamed and its audit row removed", lambda d: (
             edit_rows("metrics.csv", lambda r: [x.__setitem__(0, "M01") for x in r if x[0] == "M13"])(d),
             edit_rows("nist-ai-rmf-crosswalk.csv", lambda r: [x.__setitem__(0, "M01") for x in r if x[0] == "M13"])(d),
             edit_rows("metric-audit.csv", lambda r: [r.remove(x) for x in [x for x in r if x[0] == "M13"]])(d))),
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
