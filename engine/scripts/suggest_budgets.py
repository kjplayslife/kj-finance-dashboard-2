#!/usr/bin/env python3
"""Suggest a monthly budget per spending category from the person's own history.

Average of the full months in data/finance-data.json (the current, unfinished month is left out;
if there's only one month, that month is used), rounded up to the next $25. Categories with no
spending get $0. Prints the table; --write saves it to data/config.json (only categories that
don't have a budget yet, unless --all), then re-run sync.py.

Usage:
  python3 scripts/suggest_budgets.py            # show
  python3 scripts/suggest_budgets.py --write    # fill in missing budgets
"""
import argparse
import json
import math
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--all", action="store_true", help="replace existing budgets too")
    a = ap.parse_args()
    cfg_path = os.path.join(ROOT, "data", "config.json")
    with open(cfg_path) as f:
        cfg = json.load(f)
    with open(os.path.join(ROOT, "data", "finance-data.json")) as f:
        fin = json.load(f)
    non_spend = set(cfg["non_spend"])
    cats = [c for c in cfg["categories"] if c not in non_spend]
    months = fin["months"]
    cur = date.today().strftime("%Y-%m")
    full = [m for m in months if m != cur] or months
    tot = {c: 0.0 for c in cats}
    for t in fin["transactions"]:
        if t["date"][:7] in full and t["amount"] < 0 and t["category"] in tot:
            tot[t["category"]] += -t["amount"]
    sugg = {c: int(math.ceil(tot[c] / len(full) / 25.0) * 25) for c in cats}
    print("Average of %d month(s): %s" % (len(full), ", ".join(full)))
    for c in cats:
        have = cfg["budgets"].get(c)
        print("  %-20s $%6d%s" % (c, sugg[c], "" if have is None else "   (now $%s)" % have))
    print("  %-20s $%6d" % ("Total", sum(sugg.values())))
    if a.write:
        for c in cats:
            if a.all or c not in cfg["budgets"]:
                cfg["budgets"][c] = sugg[c]
        with open(cfg_path, "w") as f:
            json.dump(cfg, f, indent=1)
        print("Saved to data/config.json. Run python3 scripts/sync.py to rebuild the dashboard.")


if __name__ == "__main__":
    main()
