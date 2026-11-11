"""Build the synthetic Trust Tiers example in data-quality/example/.

Three parts, kept apart on purpose:
  1. simulate(): a fictional month of signals for 13 invented Sales datasets,
     with a few scripted incidents. Everything here is made up.
  2. score() and tier(): the rules of data-quality/trust-tiers.md, applied as
     written. If the page changes, this part has to change with it.
  3. the outputs: CSV files, two SVG charts, and the tables in the example's
     README between its GENERATED markers.

The script asserts the outcomes the incidents were scripted to produce, so a
change to the rules that breaks the example fails loudly instead of quietly
drawing different charts.

Usage: python3 tools/build_trust_tiers_example.py
"""
import csv
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data-quality" / "example"
DAYS = 30
START, END = "<!-- GENERATED: do not edit by hand -->", "<!-- END GENERATED -->"

# ---------------------------------------------------------------- 1. simulate
# consumers: E = executive report, A = AI system, P = other pipelines, H = ad hoc analysis
DATASETS = [
    # id, consumers, owner, steward, agreed lag (hours), critical elements, elements with a rule, rules, certified definitions, lineage
    ("daily_revenue_summary", "E", "Finance reporting lead", "Sales data steward", 24, 8, 8, 12, 8, True),
    ("sales_orders", "E P", "Order management lead", "Sales data steward", 24, 14, 14, 18, 14, True),
    ("sales_order_lines", "E P", "Order management lead", "Sales data steward", 24, 10, 10, 14, 10, True),
    ("store_targets", "E", "Regional sales director", "Sales data steward", 168, 6, 6, 7, 6, True),
    ("sales_forecast_features", "A", "Forecasting lead", "Analytics data steward", 24, 16, 16, 22, 16, True),
    ("assistant_policy_index", "A", "Sales operations lead", "Knowledge steward", 168, 5, 5, 6, 5, True),
    ("customers", "E A P", "Customer data lead", "Customer data steward", 24, 12, 12, 16, 12, True),
    ("price_list", "E A P", "Pricing lead", "Sales data steward", 24, 6, 6, 9, 6, True),
    ("products", "P", "Product data lead", "Product data steward", 24, 9, 9, 11, 9, True),
    ("returns", "P H", "Order management lead", "Sales data steward", 24, 7, 7, 8, 7, True),
    ("crm_accounts", "H", "Sales operations lead", "Customer data steward", 24, 14, 14, 15, 10, True),
    ("rep_quota", "H", "Sales operations lead", "Sales data steward", 168, 6, 5, 6, 6, True),
    ("promotions", "P H", "Marketing operations lead", "Sales data steward", 24, 9, 9, 10, 7, False),
]
CONSUMER_NAMES = {"E": "executive report", "A": "AI system", "P": "pipelines", "H": "ad hoc"}


def simulate():
    """Return {dataset: [state for day 1..30]} with the scripted incidents applied."""
    out = {}
    for (name, cons, owner, steward, lag, crit, covered, rules, cert, lineage) in DATASETS:
        days = []
        for d in range(1, DAYS + 1):
            s = dict(dataset=name, day=d, consumers=cons, owner=owner, steward=steward,
                     agreed_lag_h=lag, critical_elements=crit, elements_with_rule=covered,
                     rules=rules, rules_failed=0, blocking_failed=0,
                     hours_since_load=6, certified=cert, lineage=lineage, measured=True)
            days.append(s)
        out[name] = days

    def on(name, first, last, **changes):
        for s in out[name][first - 1:last]:
            s.update(changes)

    # Two failed nightly loads of sales_orders (days 8 and 9); the summary built on it stops too on day 9.
    on("sales_orders", 8, 8, hours_since_load=30)
    on("sales_orders", 9, 9, hours_since_load=54)
    on("daily_revenue_summary", 9, 9, hours_since_load=30)
    # A blocking rule (no negative prices) fails on price_list for one day.
    on("price_list", 15, 15, rules_failed=1, blocking_failed=1)
    # The customers steward leaves on day 18 and is not replaced this month.
    on("customers", 18, 30, steward="")
    # A completeness rule on the forecast features fails from day 22 (new stores have no region).
    on("sales_forecast_features", 22, 30, rules_failed=1)
    # A misconfigured rule fails on returns for one day: a false alarm.
    on("returns", 25, 25, rules_failed=1)
    # The owner of store_targets changes role on day 27; a new owner is named on day 29.
    on("store_targets", 27, 28, owner="")
    # promotions is not onboarded until day 13: its signals cannot be measured before then.
    on("promotions", 1, 12, measured=False)
    return out


# What people did about each drop. Synthetic, like everything else in part 1.
RESPONSES = {
    ("sales_orders", 8): dict(ack=8, cause="Upstream order system changed its export path; load job pointed at the old one", real=True),
    ("daily_revenue_summary", 9): dict(ack=9, cause="Halted on purpose while its source table was stale", real=True),
    ("price_list", 15): dict(ack=15, cause="Currency conversion applied twice to one supplier file", real=True),
    ("customers", 18): dict(ack=20, cause=None, real=True),
    ("sales_forecast_features", 22): dict(ack=23, cause=None, real=True),
    ("returns", 25): dict(ack=25, cause="Rule compared against a deprecated status code; rule fixed, data was fine", real=False),
    ("store_targets", 27): dict(ack=27, cause="Owner changed role; regional sales director named as the new owner", real=True),
}

# ------------------------------------------------------- 2. the page's rules
WEIGHTS = dict(quality=40, freshness=20, ownership=15, definitions=15, lineage=10)


def signals(s):
    lag = s["agreed_lag_h"]
    h = s["hours_since_load"]
    return dict(
        quality=(s["rules"] - s["rules_failed"]) / s["rules"],
        freshness=1.0 if h <= lag else (0.5 if h <= 2 * lag else 0.0),
        ownership=(bool(s["owner"]) + bool(s["steward"])) / 2,
        definitions=s["certified"] / s["critical_elements"],
        lineage=1.0 if s["lineage"] else 0.0,
    )


def score(sig):
    return round(sum(WEIGHTS[k] * sig[k] for k in WEIGHTS), 1)


def tier(s, sig, sc):
    """Return (tier, reason, protection) following trust-tiers.md."""
    if not s["measured"]:
        return "Unrated", "not onboarded yet, so its signals cannot be measured", "treated as Tier 3"
    lag, h = s["agreed_lag_h"], s["hours_since_load"]
    blocking = []
    if s["blocking_failed"]:
        blocking.append(f"{s['blocking_failed']} blocking rule failed")
    if h > 2 * lag:
        blocking.append(f"last load {h} hours ago, more than twice the agreed {lag}")
    if not s["owner"]:
        blocking.append("no owner assigned")
    if blocking or sc < 70:
        why = blocking or [f"score {sc} is below 70"]
        return "Tier 3", "; ".join(why), "block" if s["blocking_failed"] else "quarantine"
    gaps = []
    if s["rules_failed"]:
        gaps.append(f"{s['rules_failed']} of {s['rules']} rules on critical elements failed")
    if h > lag:
        gaps.append(f"last load {h} hours ago against an agreed {lag}")
    if not s["steward"]:
        gaps.append("no steward assigned")
    if s["certified"] < s["critical_elements"]:
        k = s['critical_elements'] - s['certified']
        gaps.append(f"{k} of {s['critical_elements']} critical elements {'has' if k == 1 else 'have'} no certified definition")
    if s["elements_with_rule"] < s["critical_elements"]:
        k = s['critical_elements'] - s['elements_with_rule']
        gaps.append(f"{k} of {s['critical_elements']} critical elements {'has' if k == 1 else 'have'} no rule")
    if not s["lineage"]:
        gaps.append("lineage not recorded")
    if sc >= 90 and not gaps:
        return "Tier 1", "every condition met", "none"
    return "Tier 2", "; ".join(gaps) or f"score {sc} is below 90", "warn"


RANK = {"Tier 1": 1, "Tier 2": 2, "Unrated": 3, "Tier 3": 3}


def run():
    sim = simulate()
    rows = []
    for name, days in sim.items():
        for s in days:
            sig = signals(s)
            sc = score(sig) if s["measured"] else ""
            t, why, prot = tier(s, sig, sc if sc != "" else 0)
            rows.append(dict(day=s["day"], dataset=name, consumers=s["consumers"],
                             quality=round(sig["quality"], 3), freshness=sig["freshness"],
                             ownership=sig["ownership"], definitions=round(sig["definitions"], 3),
                             lineage=sig["lineage"], score=sc, tier=t, protection=prot,
                             reason=f"{t} because {why}" if t != "Tier 1" else "Tier 1: every condition met"))
    return sim, rows


def exceptions(rows):
    """Open an exception when a dataset's tier gets worse than the day before; close it when it is back."""
    by = {}
    for r in rows:
        by.setdefault(r["dataset"], []).append(r)
    ex = []
    for name, days in by.items():
        days.sort(key=lambda r: r["day"])
        cur = None
        for i, r in enumerate(days):
            prev = days[i - 1]["tier"] if i else None
            if cur is None and prev and prev != "Unrated" and RANK[r["tier"]] > RANK[prev]:
                resp = RESPONSES[(name, r["day"])]
                cur = dict(dataset=name, consumers=r["consumers"], opened=r["day"], tier_before=prev,
                           worst=r["tier"], ack=resp["ack"], cause=resp["cause"], real=resp["real"], closed=None)
                ex.append(cur)
            elif cur is not None:
                if RANK[r["tier"]] > RANK[cur["worst"]]:
                    cur["worst"] = r["tier"]
                if RANK[r["tier"]] <= RANK[cur["tier_before"]]:
                    cur["closed"] = r["day"]
                    cur = None
    for n, e in enumerate(sorted(ex, key=lambda e: (e["opened"], e["dataset"])), 1):
        e["id"] = f"EX-{n:02d}"
        high = any(c in e["consumers"] for c in "EA")
        e["agreed_days"] = 1 if (e["worst"] == "Tier 3" and high) else 3
    return sorted(ex, key=lambda e: e["id"])


def state_on(e, day):
    """Escalation state of exception e at the end of `day`. The example counts calendar days; the design says business days."""
    if e["opened"] > day:
        return None
    open_ = e["closed"] is None or e["closed"] > day
    age = (day if open_ else e["closed"]) - e["opened"]
    past = open_ and age > e["agreed_days"]
    high = any(c in e["consumers"] for c in "EA")
    step = "1. owner"
    if e["ack"] > e["opened"] + 1 or (e["ack"] > day and age >= 1) or past:
        step = "2. steward"
    if past or (open_ and e["worst"] == "Tier 3" and high):
        step = "4. leadership"
    return dict(open=open_, age=age, past=past, step=step)


def kris(rows, ex, day):
    today = [r for r in rows if r["day"] == day]
    n = len(today)
    closed = [e for e in ex if e["closed"] and e["closed"] <= day]
    restore = [e["closed"] - e["opened"] for e in closed]
    verdicts = [e["real"] for e in closed]
    exposed = [r for r in today if r["tier"] in ("Tier 3", "Unrated") and any(c in r["consumers"] for c in "EA")]
    return {
        "Datasets in Tier 1": f"{sum(r['tier'] == 'Tier 1' for r in today)} of {n} ({100 * sum(r['tier'] == 'Tier 1' for r in today) / n:.0f}%)",
        "Tier 3 or Unrated, feeding an executive report or AI system": str(len(exposed)),
        "Exceptions open past their agreed time": str(sum(1 for e in ex if (st := state_on(e, day)) and st["past"])),
        "Median days to restore (closed exceptions)": f"{statistics.median(restore):g}" if restore else "none closed yet",
        "Datasets Unrated": f"{sum(r['tier'] == 'Unrated' for r in today)} of {n}",
        "Tier drops confirmed as real problems": f"{sum(verdicts)} of {len(verdicts)}" if verdicts else "none closed yet",
    }


# ------------------------------------------------------------ 3. the outputs
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
TIER_FILL = {"Tier 1": "#0ca30c", "Tier 2": "#fab219", "Tier 3": "#d03b3b", "Unrated": "#c3c2b7"}
TIER_MARK = {"Tier 1": "", "Tier 2": "2", "Tier 3": "3", "Unrated": "?"}
TIER_MARK_INK = {"Tier 2": INK, "Tier 3": "#ffffff", "Unrated": INK}
FONT = "font-family=\"-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif\""


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def order(names_consumers):
    """Datasets with executive or AI consumers first, as the daily view sorts them."""
    return sorted(names_consumers, key=lambda nc: (not any(c in nc[1] for c in "EA"), [d[0] for d in DATASETS].index(nc[0])))


def tier_history_svg(rows):
    cell, gap, left, top = 18, 2, 370, 76
    names = order([(d[0], d[1]) for d in DATASETS])
    w = left + DAYS * (cell + gap) + 24
    h = top + len(names) * (cell + gap) + 70
    lookup = {(r["dataset"], r["day"]): r for r in rows}
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {FONT}>',
         f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="{SURFACE}" stroke="{GRID}"/>',
         f'<text x="20" y="30" font-size="16" font-weight="600" fill="{INK}">Trust Tier of each dataset, day by day</text>',
         f'<text x="20" y="49" font-size="12" fill="{INK2}">Synthetic data for a fictional Sales domain. Datasets that feed an executive report or an AI system are listed first.</text>']
    p.append(f'<text x="{left - 8}" y="{top - 4}" font-size="10" fill="{INK2}" text-anchor="end">Day</text>')
    for d in range(1, DAYS + 1):
        if d == 1 or d % 5 == 0:
            x = left + (d - 1) * (cell + gap) + cell / 2
            p.append(f'<text x="{x}" y="{top - 4}" font-size="10" fill="{INK2}" text-anchor="middle">{d}</text>')
    for i, (name, cons) in enumerate(names):
        y = top + i * (cell + gap)
        tag = ", ".join(CONSUMER_NAMES[c] for c in cons.split())
        p.append(f'<text x="20" y="{y + 13}" font-size="12" fill="{INK}">{esc(name)}</text>')
        p.append(f'<text x="{left - 8}" y="{y + 13}" font-size="10" fill="{INK2}" text-anchor="end">{esc(tag)}</text>')
        for d in range(1, DAYS + 1):
            r = lookup[(name, d)]
            x = left + (d - 1) * (cell + gap)
            p.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{TIER_FILL[r["tier"]]}"><title>{esc(name)}, day {d}: {esc(r["reason"])}</title></rect>')
            m = TIER_MARK[r["tier"]]
            if m:
                p.append(f'<text x="{x + cell / 2}" y="{y + 13}" font-size="10" font-weight="600" fill="{TIER_MARK_INK[r["tier"]]}" text-anchor="middle">{m}</text>')
    ly = top + len(names) * (cell + gap) + 26
    x = 20
    for t, label in [("Tier 1", "Tier 1: trusted"), ("Tier 2", "2  Tier 2: use with care"), ("Tier 3", "3  Tier 3: not fit for decisions"), ("Unrated", "?  Unrated")]:
        p.append(f'<rect x="{x}" y="{ly}" width="14" height="14" rx="3" fill="{TIER_FILL[t]}"/>')
        p.append(f'<text x="{x + 20}" y="{ly + 11}" font-size="12" fill="{INK}">{esc(label)}</text>')
        x += 34 + int(6.6 * len(label))
    p.append(f'<text x="20" y="{ly + 34}" font-size="11" fill="{INK2}">Numbers in the cells repeat the tier, so the chart does not rely on color alone. The same data is in daily-tiers.csv.</text>')
    p.append("</svg>")
    return "\n".join(x for x in p if x)


def tier1_share_svg(rows):
    w, h, left, right, top, bottom = 760, 300, 56, 24, 64, 48
    pw, ph = w - left - right, h - top - bottom
    n = len(DATASETS)
    share = [100 * sum(1 for r in rows if r["day"] == d and r["tier"] == "Tier 1") / n for d in range(1, DAYS + 1)]
    X = lambda d: left + (d - 1) * pw / (DAYS - 1)
    Y = lambda v: top + ph - v * ph / 100
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {FONT}>',
         f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="{SURFACE}" stroke="{GRID}"/>',
         f'<text x="20" y="30" font-size="16" font-weight="600" fill="{INK}">Share of datasets in Tier 1</text>',
         f'<text x="20" y="49" font-size="12" fill="{INK2}">The leadership view\'s first indicator, for the same synthetic month ({n} datasets in scope).</text>']
    for v in (0, 25, 50, 75, 100):
        p.append(f'<line x1="{left}" x2="{w - right}" y1="{Y(v)}" y2="{Y(v)}" stroke="{GRID}" stroke-width="1"/>')
        p.append(f'<text x="{left - 8}" y="{Y(v) + 4}" font-size="11" fill="{INK2}" text-anchor="end">{v}%</text>')
    for d in (1, 5, 10, 15, 20, 25, 30):
        p.append(f'<text x="{X(d)}" y="{h - bottom + 18}" font-size="11" fill="{INK2}" text-anchor="middle">{d}</text>')
    p.append(f'<text x="{left + pw / 2}" y="{h - 10}" font-size="11" fill="{INK2}" text-anchor="middle">Day</text>')
    pts = " ".join(f"{X(d):.1f},{Y(v):.1f}" for d, v in zip(range(1, DAYS + 1), share))
    p.append(f'<polyline points="{pts}" fill="none" stroke="#2a78d6" stroke-width="2" stroke-linejoin="round"/>')
    for d, v in zip(range(1, DAYS + 1), share):
        p.append(f'<circle cx="{X(d):.1f}" cy="{Y(v):.1f}" r="4" fill="#2a78d6" stroke="{SURFACE}" stroke-width="2"><title>Day {d}: {v:.0f}%</title></circle>')
    lo = min(range(DAYS), key=lambda i: share[i])
    p.append(f'<text x="{X(lo + 1)}" y="{Y(share[lo]) + 22}" font-size="11" fill="{INK}" text-anchor="middle">Lowest, day {lo + 1}: {share[lo]:.0f}%</text>')
    p.append(f'<text x="{X(DAYS)}" y="{Y(share[-1]) - 12}" font-size="11" fill="{INK}" text-anchor="end">Day {DAYS}: {share[-1]:.0f}%</text>')
    p.append("</svg>")
    return "\n".join(p), share


def write_csv(path, rows, cols):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def generated_block(rows, ex):
    day = DAYS
    by_today = {r["dataset"]: r for r in rows if r["day"] == day}
    by_yday = {r["dataset"]: r for r in rows if r["day"] == day - 1}
    view = []
    for name, cons in order([(d[0], d[1]) for d in DATASETS]):
        r = by_today[name]
        open_ex = [e for e in ex if e["dataset"] == name and (st := state_on(e, day)) and st["open"]]
        dropped = r["tier"] != by_yday[name]["tier"]
        if not (open_ex or r["tier"] == "Unrated" or dropped):
            continue
        st = state_on(open_ex[0], day) if open_ex else None
        view.append([f"`{name}`", ", ".join(CONSUMER_NAMES[c] for c in cons.split()), f"{by_yday[name]['tier']} → {r['tier']}",
                     r["reason"], r["protection"], open_ex[0]["id"] if open_ex else "",
                     f"{st['step']}, {st['age']} days open" + (" (past agreed time)" if st["past"] else "") if st else ""])
    weeks = [7, 14, 21, 28, 30]
    k = {d: kris(rows, ex, d) for d in weeks}
    kri_rows = [[name] + [k[d][name] for d in weeks] for name in k[weeks[0]]]
    ex_rows = [[e["id"], f"`{e['dataset']}`", e["opened"], e["closed"] or "open", f"{e['tier_before']} → {e['worst']}",
                e["cause"] or "not yet found", "yes" if e["closed"] and e["real"] else ("no" if e["closed"] else "")] for e in ex]
    return "\n\n".join([
        f"### Daily exception view, day {day}",
        md_table(["Dataset", "Consumers", "Tier (yesterday → today)", "Reason", "Protection", "Exception", "Escalation"], view),
        "### Leadership risk indicators, by week",
        md_table(["Indicator", "Day 7", "Day 14", "Day 21", "Day 28", f"Day {day} (today)"], kri_rows),
        "### Every exception this month",
        md_table(["Id", "Dataset", "Opened (day)", "Closed (day)", "Tier", "Cause recorded at closing", "Real problem?"], ex_rows),
    ])


def check(rows, ex):
    """The outcomes the incidents were scripted to produce."""
    t = {(r["dataset"], r["day"]): r for r in rows}
    assert t[("price_list", 15)]["tier"] == "Tier 3" and t[("price_list", 15)]["score"] > 90, "a blocking rule must override a high score"
    assert t[("price_list", 15)]["protection"] == "block"
    assert t[("sales_orders", 8)]["tier"] == "Tier 2" and t[("sales_orders", 9)]["tier"] == "Tier 3"
    assert t[("customers", 30)]["tier"] == "Tier 2" and "no steward" in t[("customers", 30)]["reason"]
    assert t[("store_targets", 27)]["tier"] == "Tier 3" and t[("store_targets", 29)]["tier"] == "Tier 1"
    assert all(t[("promotions", d)]["tier"] == "Unrated" for d in range(1, 13)) and t[("promotions", 13)]["tier"] == "Tier 2"
    assert all(t[("crm_accounts", d)]["tier"] == "Tier 2" for d in range(1, DAYS + 1)), "chronic Tier 2 never opens an exception"
    assert all(t[("rep_quota", d)]["tier"] == "Tier 2" for d in range(1, DAYS + 1)), "rule coverage below 100% keeps it out of Tier 1"
    assert t[("products", 30)]["tier"] == "Tier 1"
    assert len(ex) == len(RESPONSES), (len(ex), sorted((e["dataset"], e["opened"]) for e in ex))
    assert [e for e in ex if not e["real"]] and all(e["closed"] for e in ex if not e["real"])


def main():
    sim, rows = run()
    ex = exceptions(rows)
    check(rows, ex)
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "datasets.csv", [dict(zip(["dataset", "consumers", "owner", "steward", "agreed_lag_hours", "critical_elements",
                                               "elements_with_rule", "rules", "certified_definitions", "lineage_recorded"], d)) for d in DATASETS],
              ["dataset", "consumers", "owner", "steward", "agreed_lag_hours", "critical_elements", "elements_with_rule", "rules",
               "certified_definitions", "lineage_recorded"])
    sig_rows = [dict(day=s["day"], dataset=s["dataset"], hours_since_load=s["hours_since_load"], rules_failed=s["rules_failed"],
                     blocking_failed=s["blocking_failed"], owner=s["owner"], steward=s["steward"], measured=s["measured"])
                for days in sim.values() for s in days]
    write_csv(OUT / "daily-signals.csv", sorted(sig_rows, key=lambda r: (r["day"], r["dataset"])),
              ["day", "dataset", "hours_since_load", "rules_failed", "blocking_failed", "owner", "steward", "measured"])
    write_csv(OUT / "daily-tiers.csv", sorted(rows, key=lambda r: (r["day"], r["dataset"])),
              ["day", "dataset", "consumers", "quality", "freshness", "ownership", "definitions", "lineage", "score", "tier", "protection", "reason"])
    write_csv(OUT / "exceptions.csv", [dict(e, closed=e["closed"] or "", cause=e["cause"] or "", real="" if not e["closed"] else e["real"]) for e in ex],
              ["id", "dataset", "consumers", "opened", "closed", "tier_before", "worst", "ack", "agreed_days", "cause", "real"])
    (OUT / "tier-history.svg").write_text(tier_history_svg(rows) + "\n", encoding="utf-8")
    svg, share = tier1_share_svg(rows)
    (OUT / "tier1-share.svg").write_text(svg + "\n", encoding="utf-8")
    readme = OUT / "README.md"
    text = readme.read_text(encoding="utf-8")
    assert text.count(START) == 1 and text.count(END) == 1, "README needs exactly one pair of GENERATED markers"
    head, rest = text.split(START)
    _, tail = rest.split(END)
    readme.write_text(f"{head}{START}\n\n{generated_block(rows, ex)}\n\n{END}{tail}", encoding="utf-8")
    print(f"{len(DATASETS)} datasets x {DAYS} days, {len(ex)} exceptions, Tier 1 share from {min(share):.0f}% to {max(share):.0f}%")


if __name__ == "__main__":
    main()
