"""Generate the business-goals files that are derived from the data.

Writes business-goals/scorecard-template.csv from data/metrics.csv and
data/business-questions.csv, and the question table in business-goals/README.md
between its GENERATED markers. Run it after editing either data file;
check_data.py rule r24 fails until the template matches.

Usage: python3 tools/build_scorecard.py
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_data import TEMPLATE_COLUMNS, read, scorecard_rows  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
START, END = "<!-- GENERATED: do not edit by hand -->", "<!-- END GENERATED -->"


def question_table(metrics, questions):
    names = {m["id"]: m["name"] for m in metrics}
    tiers = {m["id"]: m["tier"] for m in metrics}
    lines = ["| Goal | Question | Metrics that answer it |", "|---|---|---|"]
    for q in questions:
        ids = q["metric_ids"].split(";")
        cells = [f"{i} {names[i]}" + (" *(F)*" if tiers[i] == "Foundational" else "") for i in ids]
        lines.append(f"| {q['goal']} | **{q['id']}** {q['question']} | {'<br>'.join(cells)} |")
    return "\n".join(lines)


def main():
    _, metrics = read(ROOT / "data/metrics.csv")
    _, questions = read(ROOT / "data/business-questions.csv")
    out = ROOT / "business-goals/scorecard-template.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(TEMPLATE_COLUMNS)
        w.writerows(scorecard_rows(metrics, questions))
    readme = ROOT / "business-goals/README.md"
    text = readme.read_text(encoding="utf-8")
    assert text.count(START) == 1 and text.count(END) == 1, "README needs exactly one pair of GENERATED markers"
    head, rest = text.split(START)
    _, tail = rest.split(END)
    readme.write_text(f"{head}{START}\n\n{question_table(metrics, questions)}\n\n{END}{tail}", encoding="utf-8")
    print(f"template: {len(metrics)} metrics; question table: {len(questions)} questions")


if __name__ == "__main__":
    main()
