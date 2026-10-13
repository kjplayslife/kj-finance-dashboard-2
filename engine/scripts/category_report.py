#!/usr/bin/env python3
"""Show what this person actually spends on, so their categories can be fitted to it.

Reads data/finance-data.json (run sync.py first) and data/config.json, and prints:
  1. each spending category with its number of purchases and total spent,
  2. categories with no spending at all (candidates to remove),
  3. the biggest merchants in "Other" or that no rule matched (candidates for new categories or rules),
  4. money coming in, by category (to check Income vs Transfers).

Usage: python3 scripts/category_report.py [--top 20]
"""
import argparse
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def money(n):
    return "$" + format(round(n), ",")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=20, help="how many unsorted merchants to list")
    a = ap.parse_args()
    with open(os.path.join(ROOT, "data", "config.json")) as f:
        cfg = json.load(f)
    with open(os.path.join(ROOT, "data", "finance-data.json")) as f:
        fin = json.load(f)
    non_spend = set(cfg.get("non_spend", []))
    spend_cats = [c for c in cfg["categories"] if c not in non_spend]
    hidden = set(cfg.get("hidden", []))

    count, total = defaultdict(int), defaultdict(float)
    unsorted = defaultdict(lambda: [0, 0.0])
    money_in = defaultdict(lambda: [0, 0.0])
    for t in fin["transactions"]:
        c, amt = t["category"], t["amount"]
        if amt < 0 and c not in non_spend:
            count[c] += 1
            total[c] += -amt
            if c == "Other" or t.get("needsReview"):
                u = unsorted[t.get("displayDescription") or t.get("rawDescription", "?")]
                u[0] += 1
                u[1] += -amt
        elif amt > 0 and c not in hidden:
            m = money_in[c]
            m[0] += 1
            m[1] += amt

    months = fin.get("months", [])
    print("Spending by category, %s to %s:" % (months[0], months[-1]) if months else "Spending by category:")
    for c in sorted(spend_cats, key=lambda c: -total[c]):
        if count[c]:
            print("  %-26s %4d purchases  %10s" % (c, count[c], money(total[c])))
    extra = sorted(c for c in count if c not in spend_cats)
    for c in extra:
        print("  %-26s %4d purchases  %10s  (not in the category list)" % (c, count[c], money(total[c])))
    empty = [c for c in spend_cats if not count[c]]
    print("\nNo spending at all: " + (", ".join(empty) if empty else "none"))
    print("\nBiggest unsorted merchants (in Other, or no rule matched):")
    rows = sorted(unsorted.items(), key=lambda kv: -kv[1][1])[: a.top]
    for name, (n, amt) in rows:
        print("  %-40s %4d x  %10s" % (name[:40], n, money(amt)))
    if not rows:
        print("  none")
    print("\nMoney in, by category:")
    for c, (n, amt) in sorted(money_in.items(), key=lambda kv: -kv[1][1]):
        print("  %-26s %4d  %10s" % (c, n, money(amt)))


if __name__ == "__main__":
    main()
