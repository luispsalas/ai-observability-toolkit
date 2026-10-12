"""Generate the summary tables in crosswalk/README.md from the CSV files.

Rewrites only the text between the two GENERATED markers, so the numbers in the
README always match the data. Run after any change to the crosswalk:
  python3 tools/build_crosswalk_summary.py
"""
import collections
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "crosswalk/README.md"
START, END = "<!-- GENERATED: do not edit by hand -->", "<!-- END GENERATED -->"
FUNCTIONS = ["GOVERN", "MAP", "MEASURE", "MANAGE"]


def rows(path):
    with open(ROOT / path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    metrics = {r["id"]: r["name"] for r in rows("data/metrics.csv")}
    nist = rows("data/nist-ai-rmf.csv")
    links = rows("crosswalk/nist-ai-rmf-crosswalk.csv")
    by_sub = collections.defaultdict(list)
    for l in links:
        by_sub[l["subcategory_id"]].append(l)

    def level(sid):
        rels = {l["relation"] for l in by_sub[sid]}
        return "primary" if "primary" in rels else "supporting" if rels else "none"

    out = [START, "", "### Coverage by function", "",
           "| Function | Subcategories | With primary evidence | Supporting only | No metric |",
           "|---|---|---|---|---|"]
    for f in FUNCTIONS:
        subs = [r["subcategory_id"] for r in nist if r["function"] == f]
        c = collections.Counter(level(s) for s in subs)
        out.append(f"| {f} | {len(subs)} | {c['primary']} | {c['supporting']} | {c['none']} |")
    total = collections.Counter(level(r["subcategory_id"]) for r in nist)
    out.append(f"| **All** | **{len(nist)}** | **{total['primary']}** | **{total['supporting']}** | **{total['none']}** |")

    out += ["", "### Coverage by category", "",
            "Each subcategory is shown as its id, marked **bold** where at least one metric is primary evidence, plain where metrics only support it, and ~~struck~~ where no metric links to it.", "",
            "| Category | Subcategories |", "|---|---|"]
    cats = collections.OrderedDict()
    for r in nist:
        cats.setdefault((r["category_id"], r["category"]), []).append(r["subcategory_id"])
    for (cid, ctext), subs in cats.items():
        marks = []
        for s in subs:
            n = s.split(" ")[1]
            marks.append(f"**{n}**" if level(s) == "primary" else n if level(s) == "supporting" else f"~~{n}~~")
        out.append(f"| **{cid}**: {ctext} | {' · '.join(marks)} |")

    out += ["", "### Most-linked subcategories", "", "| Subcategory | Metrics linked | Of which primary |", "|---|---|---|"]
    top = sorted(by_sub, key=lambda s: (-len(by_sub[s]), s))[:5]
    for s in top:
        out.append(f"| {s} | {len(by_sub[s])} | {sum(l['relation'] == 'primary' for l in by_sub[s])} |")

    unc = [l for l in links if l["uncertain"] == "yes"]
    out += ["", f"### Uncertain calls ({len(unc)} of {len(links)} links)", "",
            "| Metric | Subcategory | Relation | Why it is uncertain |", "|---|---|---|---|"]
    for l in unc:
        out.append(f"| {l['metric_id']} {metrics[l['metric_id']]} | {l['subcategory_id']} | {l['relation']} | {l['rationale']} |")
    out += ["", END]

    text = README.read_text(encoding="utf-8")
    assert text.count(START) == 1 and text.count(END) == 1, "markers must appear exactly once"
    before, rest = text.split(START)
    _, after = rest.split(END)
    README.write_text(before + "\n".join(out) + after, encoding="utf-8")
    print(f"summary written: {len(links)} links, {total['none']} subcategories with no metric, {len(unc)} uncertain calls")


if __name__ == "__main__":
    main()
