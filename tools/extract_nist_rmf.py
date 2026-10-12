"""Extract the categories and subcategories of the NIST AI RMF 1.0 (NIST AI 100-1)
from the PDF in sources/, into data/nist-ai-rmf.csv.

Reads Tables 1-4 (GOVERN, MAP, MEASURE, MANAGE) from `pdftotext -layout`, which
keeps the two table columns side by side. Words broken across lines with a
hyphen are rejoined by checking how the word is written elsewhere in the
document; any join that cannot be decided that way is printed for a person to
check.

Checks before writing:
  - 72 subcategories in 19 categories, numbered without gaps
  - no word lost or added: the words written equal the words in the tables

Needs pdftotext (poppler). Run: python3 tools/extract_nist_rmf.py
"""
import collections
import csv
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "sources/NIST.AI.100-1.pdf"
OUT = ROOT / "data/nist-ai-rmf.csv"
FUNCTIONS = ["GOVERN", "MAP", "MEASURE", "MANAGE"]
EXPECTED = {"GOVERN": (6, 19), "MAP": (5, 18), "MEASURE": (4, 22), "MANAGE": (4, 13)}  # (categories, subcategories)

SKIP = re.compile(r"^\s*(Continued on next page|Page \d+|NIST AI 100-1\s+AI RMF 1\.0|Table [1-4]:.*|Categories\s+Subcategories)\s*$")
ID = re.compile(r"^(GOVERN|MAP|MEASURE|MANAGE) (\d+)(?:\.(\d+))?:\s*")


def pdf_text(layout):
    args = ["pdftotext"] + (["-layout"] if layout else []) + [str(PDF), "-"]
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def table_lines(text):
    """Yield (left, right) fragments for every line inside Tables 1-4.

    The right column starts at a fixed position on each table page, which the
    PDF sometimes separates from the left column by a single space. So the
    split position is measured from the page's right-column-only lines and
    subcategory ids, never guessed from the width of the gap.
    """
    inside, page = False, []

    def flush(lines):
        # The left column's width changes from one category row to the next, so
        # measure the split separately for each block that starts with a category id.
        block = []
        for line in lines:
            if re.match(r"^ (GOVERN|MAP|MEASURE|MANAGE) \d+:", line) and block:
                yield from split_block(block)
                block = []
            block.append(line)
        yield from split_block(block)

    def split_block(lines):
        starts = collections.Counter()
        for line in lines:
            indent = len(line) - len(line.lstrip())
            if indent >= 10:
                starts[indent] += 1
            for m in re.finditer(r"(?<=\s)(?:GOVERN|MAP|MEASURE|MANAGE) \d+\.\d+:", line):
                starts[m.start()] += 1
        if not starts:
            return
        col = starts.most_common(1)[0][0]
        for line in lines:
            indent = len(line) - len(line.lstrip())
            if indent >= 10:
                yield "", line.strip()
            elif len(line) > col - 4:
                # Justified text moves the column start by a few characters: split at
                # the word start nearest the measured column.
                cands = [j for j in range(col - 4, min(col + 2, len(line))) if line[j - 1] == " " and line[j] != " "]
                if not cands and len(line.rstrip()) <= col + 1:  # left column only, ending near the split
                    yield line.strip(), ""
                    continue
                assert cands, f"no column split near {col}: {line!r}"
                j = min(cands, key=lambda j: (abs(j - col), -j))
                yield line[:j].strip(), line[j:].strip()
            else:
                yield line.strip(), ""

    for line in text.splitlines():
        if re.match(r"^\s*Table [1-4]: Categories and subcategories", line):
            yield from flush(page)
            inside, page = True, []
            continue
        if not inside or not line.strip() or SKIP.match(line):
            continue
        if not line.startswith(" "):  # body text starts at column 0: the table has ended
            yield from flush(page)
            inside, page = False, []
            continue
        page.append(line)
    yield from flush(page)


def dehyphenate(fragments, vocabulary, report):
    out = ""
    for frag in fragments:
        if out.endswith("-") and frag:
            head, tail = re.search(r"(\S*)-$", out).group(1), frag.split()[0]
            joined, hyphened = head + tail, head + "-" + tail
            strip = lambda w: re.sub(r"\W+$", "", w).lower()
            if vocabulary[strip(joined)] and not vocabulary[strip(hyphened)]:
                out = out[:-1] + frag
            elif vocabulary[strip(hyphened)]:
                out += frag
            else:
                out = out[:-1] + frag
                report.append(f"{hyphened!r} -> {joined!r} (undecided: neither form appears elsewhere)")
        else:
            out = (out + " " + frag).strip()
    return out


def main():
    layout = pdf_text(layout=True)
    words = re.findall(r"[A-Za-z’']+(?:-[A-Za-z’']+)*", pdf_text(layout=False))
    vocabulary = collections.Counter(re.sub(r"\W+$", "", w).lower() for w in words)

    cats, subs, report = {}, collections.OrderedDict(), []
    cur_cat = cur_sub = None
    cat_frags, sub_frags = collections.defaultdict(list), collections.defaultdict(list)
    left_stream = right_stream = ""
    for left, right in table_lines(layout):
        left_stream += left + "\n" if left else ""
        right_stream += right + "\n" if right else ""
        if left:
            m = ID.match(left)
            if m:
                cur_cat = f"{m.group(1)} {m.group(2)}"
                left = left[m.end():]
            if left:
                cat_frags[cur_cat].append(left)
        if right:
            m = ID.match(right)
            if m and m.group(3):
                cur_sub = f"{m.group(1)} {m.group(2)}.{m.group(3)}"
                subs[cur_sub] = cur_cat
                right = right[m.end():]
            sub_frags[cur_sub].append(right)

    for c in cat_frags:
        cats[c] = dehyphenate(cat_frags[c], vocabulary, report)
    rows = []
    for s, c in subs.items():
        assert s.split(".")[0] == c, f"{s} filed under {c}"
        rows.append([s.split()[0], c, cats[c], s, dehyphenate(sub_frags[s], vocabulary, report)])

    # Check 1: counts and numbering, per function.
    for f, (n_cat, n_sub) in EXPECTED.items():
        fc = [c for c in cats if c.startswith(f + " ")]
        fs = [r for r in rows if r[0] == f]
        assert len(fc) == n_cat and len(fs) == n_sub, f"{f}: {len(fc)} categories, {len(fs)} subcategories"
        assert fc == [f"{f} {i}" for i in range(1, n_cat + 1)], fc
        for c in fc:
            nums = [int(r[3].split(".")[1]) for r in fs if r[1] == c]
            assert nums == list(range(1, len(nums) + 1)), (c, nums)

    # Check 2: conservation, per column and in order. Rejoining a hyphenated word only
    # removes a hyphen and a space, so the letters and digits must match exactly.
    alnum = lambda s: re.sub(r"[^0-9A-Za-z]", "", s)
    left_out = "".join(c + cats[c] for c in cats)
    right_out = "".join(r[3] + r[4] for r in rows)
    assert alnum(left_stream) == alnum(left_out), "category column: text lost, added or reordered"
    assert alnum(right_stream) == alnum(right_out), "subcategory column: text lost, added or reordered"
    joins = left_stream.count("-\n") + right_stream.count("-\n")

    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["function", "category_id", "category", "subcategory_id", "subcategory"])
        w.writerows(rows)
    print(f"{len(cats)} categories and {len(rows)} subcategories written to {OUT.relative_to(ROOT)}")
    print(f"{joins} hyphenated line breaks resolved; {len(report)} undecided:")
    for line in report:
        print("  " + line)


if __name__ == "__main__":
    main()
