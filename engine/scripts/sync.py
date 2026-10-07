#!/usr/bin/env python3
"""Merge every saved pull, categorize it, and write data/finance-data.json, then build the dashboard.

Sources (any mix):
- data/raw/era-*.json  Era Context pulls saved by save_pull.py. Merged by transaction id (newest copy
                       wins), so history keeps building even though Era only reaches back ~90 days.
- data/raw/csv-*.json  bank CSV exports normalized by import_csv.py. For an account that Era also
                       covers (same label), CSV rows are kept only for dates before Era's first row,
                       so an old CSV can extend history without double counting.

Then: data/category-rules.json categorizes; a card refund that matches a purchase on the same card
makes both rows Reimbursed; data/overrides.json (fixes made by Claude) wins over everything.
Category and rating changes made in the dashboard itself are saved by the page, not here.

Usage:
  python3 scripts/sync.py
"""
import calendar
import glob
import json
import os
import re
import statistics
from collections import defaultdict
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


CONFIG = load_json(os.path.join(DATA, "config.json"))
if CONFIG is None:
    raise SystemExit("data/config.json is missing. Run the finance-setup-v2 skill first.")
RULES = load_json(os.path.join(DATA, "category-rules.json"), {"rules": []})["rules"]
for _r in RULES:
    _r["_re"] = re.compile(_r["match"], re.I)
NON_SPEND = set(CONFIG["non_spend"])
ERA_CFG = CONFIG.get("era") or {}
EXCLUDED = ERA_CFG.get("exclude_accounts", {})
# era.only_accounts: when set, every Era account NOT listed is left out (safer than exclude_accounts
# when one Era login holds accounts for two dashboards: a relinked account gets a new key).
ONLY = ERA_CFG.get("only_accounts") or None
def skip_account(key):
    return key in EXCLUDED or (ONLY is not None and key not in ONLY)
LATEST_PULL = None  # start time of the newest pull or import (set in main)


def d(s):
    return date.fromisoformat(s)


def merchant_key(desc):
    s = re.sub(r"^(SQ ?\*|TST\* ?|DD \*|SP |PY \*|NNT |WAL |CLT )", "", desc.upper().strip())
    words = re.findall(r"[A-Z]{2,}", s)
    return words[0] if words else s[:6]


def clean_display(desc):
    """Readable name for merchants no rule covers."""
    s = re.sub(r"^(SQ ?\*|TST\* ?|DD \*|SP |PY \*|NNT )", "", desc.strip(), flags=re.I)
    s = s.split("~")[0]
    s = re.split(r"\s#|\*|\s\d{3,}|\s{2,}", s)[0]
    s = re.sub(r",?\s+[A-Z]{2}(,\s*US)?$", "", s).strip(" ,.-")
    return s.title() if s.isupper() else (s or desc.strip())


# ---------- loading: Era ----------

def load_era():
    """All Era transactions (deduped by id) plus the latest info for each account."""
    raw_files = sorted(glob.glob(os.path.join(DATA, "raw", "era-*.json")))
    calls, accounts = [], {}
    for path in raw_files:
        raw = load_json(path)
        for resp in raw.get("accounts_responses", []):
            calls.append((resp.get("called_at") or "", "accounts", resp["response"], path))
        for page in raw.get("transaction_pages", []):
            calls.append((page.get("called_at") or "", "tx", page["response"], path))
    calls.sort(key=lambda c: c[0])
    # Every row from one pull gets that pull's start time as firstSeen (pages are called seconds apart).
    pull_start = {}
    for called_at, _, _, path in calls:
        if called_at and path not in pull_start:
            pull_start[path] = called_at
    newest_file = max((c[3] for c in calls), key=lambda p: os.path.getmtime(p), default=None)

    labels = ERA_CFG.get("account_labels", {})
    by_id, first_seen, ever_pending = {}, {}, {}
    for called_at, kind, resp, path in calls:
        if kind == "accounts":
            for a in resp.get("accounts", []):
                if a.get("visibility") == "tier_excluded" or skip_account(a["account_group_key"]):
                    continue
                a = dict(a, label=labels.get(a["account_group_key"], a["name"]), as_of=called_at)
                accounts[a["account_group_key"]] = a
            continue
        for t in resp.get("transactions", []):
            if skip_account(t["account_group_key"]):
                continue
            t = dict(t, _file=path, _called_at=called_at)
            by_id[t["transaction_id"]] = t
            # calls are in time order, so the first pull that had a row is when it showed up.
            first_seen.setdefault(t["transaction_id"], pull_start.get(path, called_at))
            if t.get("is_pending"):
                ever_pending[t["transaction_id"]] = t

    # Two accounts with the same name (e.g. "Savings Account" at two banks) get their last four
    # digits added, so balances and rows never merge. Names set in config are kept as given.
    names = defaultdict(list)
    for k, a in accounts.items():
        if k not in labels:
            names[a["label"]].append(k)
    for same in names.values():
        if len(same) > 1:
            for k in same:
                mask = accounts[k].get("account_mask") or k[-4:]
                accounts[k]["label"] = "%s ··%s" % (accounts[k]["label"], mask)
    seen = defaultdict(int)  # still the same (the same account linked twice): number them
    for k in sorted(accounts):
        lb = accounts[k]["label"]
        seen[lb] += 1
        if seen[lb] > 1:
            accounts[k]["label"] = "%s (%d)" % (lb, seen[lb])

    rows = []
    for t in by_id.values():
        pending = bool(t.get("is_pending"))
        # Pending rows only count from the newest pull; $0 holds never count.
        if pending and (t["_file"] != newest_file or abs(t["amount"]) < 0.005):
            continue
        acct = accounts.get(t["account_group_key"], {})
        rows.append({
            "id": t["transaction_id"],
            "date": t["transaction_date"],
            "account": t["account_group_key"],
            "accountLabel": acct.get("label", t.get("account_name", "")),
            "accountType": acct.get("type", ""),
            "rawDescription": (t.get("original_description") or t["description"]).strip(),
            "amount": round(float(t["amount"]), 2),
            "pending": pending,
            "source": "era",
            "firstSeen": first_seen.get(t["transaction_id"]),
        })

    # A pending row gets a new id when it settles; drop it once the posted copy exists.
    posted = defaultdict(list)
    for r in rows:
        if not r["pending"]:
            posted[(r["account"], r["amount"], merchant_key(r["rawDescription"]))].append(r["date"])
    rows = [r for r in rows if not (r["pending"] and any(
        abs((d(r["date"]) - d(x)).days) <= 5
        for x in posted.get((r["account"], r["amount"], merchant_key(r["rawDescription"])), [])))]
    link_settled(rows, ever_pending, first_seen)
    return rows, accounts, max(pull_start.values(), default=None)


def link_settled(rows, ever_pending, first_seen):
    """A pending charge gets a new id when it posts, sometimes for a different amount (tips).
    Point each posted row at the pending id(s) it replaced (prevIds), so ratings made on the
    pending row carry over, and keep the earlier firstSeen so the daily recap doesn't show it twice."""
    live = {r["id"] for r in rows}
    gone = [p for i, p in ever_pending.items() if i not in live]
    used = set()
    for r in sorted((r for r in rows if not r["pending"]), key=lambda r: r["date"]):
        key = merchant_key(r["rawDescription"])
        best = None
        for p in gone:
            if p["transaction_id"] in used or p["account_group_key"] != r["account"]:
                continue
            if merchant_key((p.get("original_description") or p["description"]).strip()) != key:
                continue
            gap = (d(r["date"]) - d(p["transaction_date"])).days
            pa, ra = abs(float(p["amount"])), abs(r["amount"])
            if not (-1 <= gap <= 7) or (p["amount"] < 0) != (r["amount"] < 0):
                continue
            diff = abs(pa - ra)
            if diff > max(0.01, 0.3 * pa):
                continue
            if best is None or diff < best[0]:
                best = (diff, p)
        if best:
            pid = best[1]["transaction_id"]
            used.add(pid)
            r["prevIds"] = [pid]
            seen = [x for x in (first_seen.get(pid), r.get("firstSeen")) if x]
            r["firstSeen"] = min(seen) if seen else None


# ---------- loading: CSV imports ----------

def load_csv():
    """Rows from import_csv.py, deduped by id. firstSeen = when the first update that had a row ran;
    files imported within 30 minutes of each other count as one update (one CSV per account)."""
    by_id, first_seen, accounts, latest = {}, {}, {}, None
    raws = sorted((load_json(p) for p in glob.glob(os.path.join(DATA, "raw", "csv-*.json"))),
                  key=lambda r: r.get("imported_at", ""))
    batch = None
    for raw in raws:
        at = raw.get("imported_at")
        if batch is None or (datetime.fromisoformat(at) - datetime.fromisoformat(batch)).total_seconds() > 1800:
            batch = at
        acct = raw["account"]
        accounts[acct["label"]] = acct
        latest = batch
        at = batch
        for t in raw["rows"]:
            by_id[t["id"]] = dict(t, accountLabel=acct["label"], accountType=acct.get("type", ""),
                                  account="csv:" + acct["label"], pending=False, source="csv")
            first_seen.setdefault(t["id"], at)
    rows = []
    for i, r in by_id.items():
        r["firstSeen"] = first_seen[i]
        rows.append(r)
    return rows, accounts, latest


# ---------- categorizing ----------

def apply_rules(r):
    out = r["amount"] < 0
    for rule in RULES:
        if rule.get("when") == "in" and out or rule.get("when") == "out" and not out:
            continue
        if "amount" in rule and abs(abs(r["amount"]) - rule["amount"]) > 0.005:
            continue
        if rule["_re"].search(r["rawDescription"]):
            return rule
    return None


def categorize_all(rows):
    """Set category + displayDescription (in place)."""
    cats = set(CONFIG["categories"])
    for r in rows:
        rule = apply_rules(r)
        if rule and rule["category"] not in cats:
            rule = None  # a rule for a category this person doesn't use (e.g. Tithe) is skipped
        r["needsReview"] = rule is None
        if rule:
            r["category"], r["displayDescription"] = rule["category"], rule.get("display") or clean_display(r["rawDescription"])
        else:
            r["category"] = "Income" if r["amount"] > 0 else "Other"
            r["displayDescription"] = clean_display(r["rawDescription"])
        # Money back on a card from a store = a refund: Income unless it pairs with its purchase below.
        if (r.get("accountType") == "CreditCard" and r["amount"] > 0 and rule and "when" not in rule
                and r["category"] not in NON_SPEND):
            r["category"] = "Income"
            r["displayDescription"] += " Refund"
    pair_refunds(rows)
    return rows


def pair_refunds(rows):
    """A card credit that exactly matches an earlier charge on the same card (same merchant,
    or any charge for Amex points credits) marks both rows Reimbursed: they net to zero."""
    charges = [r for r in rows if r.get("accountType") == "CreditCard" and r["amount"] < 0]
    paired = set()
    credits = sorted((r for r in rows if r.get("accountType") == "CreditCard" and r["amount"] > 0
                      and r["category"] == "Income"), key=lambda r: r["date"])
    for c in credits:
        any_merchant = "POINTS FOR" in c["rawDescription"].upper()
        best = None
        for ch in charges:
            if ch["id"] in paired or ch["account"] != c["account"] or abs(ch["amount"] + c["amount"]) > 0.005:
                continue
            gap = (d(c["date"]) - d(ch["date"])).days
            if not (-10 if any_merchant else -3) <= gap <= 90:
                continue
            if not any_merchant and merchant_key(ch["rawDescription"]) != merchant_key(c["rawDescription"]):
                continue
            if best is None or abs(gap) < best[0]:
                best = (abs(gap), ch)
        if best:
            paired.add(best[1]["id"])
            c["category"] = best[1]["category"] = "Reimbursed"


def shift_early_bills(rows):
    """config bill_month_shift = {"match": REGEX, "days_before": N}: a matching bill that posts in the
    last N days of a month is paid early for the next month, so it counts on the 1st of that month.
    The real posting date is kept as postedDate (balances use it) and shown in the name."""
    cfg = CONFIG.get("bill_month_shift")
    if not cfg:
        return rows
    rx, n = re.compile(cfg["match"], re.I), int(cfg.get("days_before", 2))
    for r in rows:
        if r["amount"] >= 0 or not rx.search(r["rawDescription"]):
            continue
        dt = d(r["date"])
        last = calendar.monthrange(dt.year, dt.month)[1]
        if dt.day <= last - n:
            continue
        nxt = date(dt.year + 1, 1, 1) if dt.month == 12 else date(dt.year, dt.month + 1, 1)
        r["postedDate"] = r["date"]
        r["date"] = nxt.isoformat()
        r["displayDescription"] = "%s (%s bill, posted %s)" % (
            r["displayDescription"], nxt.strftime("%b"), dt.strftime("%b %-d"))
    return rows


def apply_overrides(rows):
    ov = load_json(os.path.join(DATA, "overrides.json"), {}).get("byId", {})
    for r in rows:
        o = ov.get(r["id"])
        if not o:
            continue
        if o.get("category"):
            r["category"] = o["category"]
            r["needsReview"] = False
        if o.get("display"):
            r["displayDescription"] = o["display"]
        if o.get("date"):
            r["date"] = o["date"]
        if "need" in o:  # 1 = want, 2 = could skip, 3 = need, 0 = not rated
            r["need"] = o["need"]
    return rows


# ---------- accounts and balances ----------

def account_list(era_accounts, csv_accounts):
    """One entry per account: Era accounts first (live balances), then CSV-only accounts, whose
    balance comes from config.manual_balances (asked for during setup and each update)."""
    manual = CONFIG.get("manual_balances", {})
    out, seen = [], set()
    for k, a in era_accounts.items():
        seen.add(a["label"])
        out.append({"label": a["label"], "institution": a.get("institution", ""), "type": a.get("type", ""),
                    "mask": a.get("account_mask", ""), "balance": (a.get("balance") or {}).get("current"),
                    "balanceAsOf": a.get("balance_as_of")})
    for label, a in csv_accounts.items():
        if label in seen:
            continue
        m = manual.get(label) or {}
        as_of = m.get("asOf")
        if as_of and len(as_of) == 10:
            as_of += "T12:00:00"  # a plain date would be read as UTC midnight (the day before in the US)
        out.append({"label": label, "institution": a.get("institution", ""), "type": a.get("type", ""),
                    "mask": a.get("mask", ""), "balance": m.get("balance"), "balanceAsOf": as_of})
    return out


def month_end_balances(rows, accounts, months):
    """Each checking/savings/card account's balance at the end of every month, worked back from its
    current balance: balance(end of M) = balance now - every change after M."""
    def month_end(m):
        y, mm = int(m[:4]), int(m[5:7])
        return "%s-%02d" % (m, calendar.monthrange(y, mm)[1])

    out = []
    for a in accounts:
        if a["type"] not in ("Checking", "Savings", "CreditCard") or a["balance"] is None:
            continue
        changes = [(r.get("postedDate", r["date"]), r["amount"]) for r in rows
                   if r["accountLabel"] == a["label"] and not r["pending"]]
        first = min((dt for dt, _ in changes), default=None)
        # Checking/savings: money in raises the balance. Cards: a charge (negative) raises what's owed.
        sign = -1 if a["type"] == "CreditCard" else 1
        values = [round(a["balance"] - sign * sum(amt for dt, amt in changes if dt > month_end(m)), 2) + 0.0
                  for m in months]
        out.append({"label": a["label"], "type": a["type"], "values": values, "eraFrom": first,
                    # Before an account's first transaction its balance can't be worked out: an estimate.
                    "estimatedBefore": first if first and first[:7] > months[0] else None})
    return {"months": months, "accounts": out}


BILL_CATEGORIES = {"Rent and Utilities", "Subscriptions", "Gas & Auto", "Fees", "Other"}
NOT_BILLS = re.compile(r"^(Venmo|Zelle|PayPal|Cash App|Cash Withdrawal|Check|Gas|Restaurant|Amazon)$", re.I)


def detect_bills(rows, ref_date):
    """Monthly bills found in the transactions: the same payee charging a similar amount
    about once a month (median gap 24-38 days over the last 6 months), still active (paid
    in the last 45 days). The next due date is the last payment's day of the month, a
    month later. The dashboard shows the ones due in the next 7 days."""
    def add_month(dt):
        y, m = (dt.year + 1, 1) if dt.month == 12 else (dt.year, dt.month + 1)
        return date(y, m, min(dt.day, calendar.monthrange(y, m)[1]))

    ref = d(ref_date)
    by_name = defaultdict(list)
    for r in rows:
        # Money sent to people and generic names (gas, checks) repeat without being bills.
        if (r["amount"] < 0 and not r.get("pending") and r["category"] in BILL_CATEGORIES
                and not NOT_BILLS.match(r["displayDescription"])):
            by_name[r["displayDescription"]].append(r)

    bills = []
    for name, group in by_name.items():
        # One payee can have several bills (e.g. rent and a separate monthly fee): split by amount.
        clusters = []
        for r in sorted(group, key=lambda r: -r["amount"]):
            amt = -r["amount"]
            if clusters and amt <= clusters[-1]["anchor"] * 1.15 + 1:
                clusters[-1]["rows"].append(r)
            else:
                clusters.append({"anchor": amt, "rows": [r]})
        for c in clusters:
            recent = sorted((r for r in c["rows"] if (ref - d(r["date"])).days <= 180), key=lambda r: r["date"])
            if len(recent) < 2:
                continue
            dates = [d(r["date"]) for r in recent]
            gap = statistics.median((b - a).days for a, b in zip(dates, dates[1:]))
            if not 24 <= gap <= 38 or (ref - dates[-1]).days > 45:
                continue
            last = recent[-1]
            bills.append({"name": name, "amount": round(-last["amount"], 2), "category": last["category"],
                          "accountLabel": last.get("accountLabel", ""), "lastDate": last["date"],
                          "nextDate": add_month(dates[-1]).isoformat()})
    bills.sort(key=lambda b: (b["nextDate"], b["name"]))
    return bills


def totals(rows):
    """Same math as the dashboard: Income = money in tagged Income; spend = money out in any
    category that isn't Income, card payments, transfers, reimbursed or gifts."""
    income = sum(r["amount"] for r in rows if r["category"] == "Income" and r["amount"] > 0)
    by_cat = defaultdict(float)
    for r in rows:
        if r["category"] not in NON_SPEND and r["amount"] < 0:
            by_cat[r["category"]] += -r["amount"]
    return {"income": round(income, 2), "spend": round(sum(by_cat.values()), 2),
            "by_cat": {k: round(v, 2) for k, v in by_cat.items()}}


# ---------- build ----------

def main():
    global LATEST_PULL
    era, era_accounts, era_latest = load_era()
    csv_rows, csv_accounts, csv_latest = load_csv()
    LATEST_PULL = max([x for x in (era_latest, csv_latest) if x], default=None)

    # Era wins where it has data: a CSV row for an account Era also covers only counts before Era's first row.
    era_first = {}
    for r in era:
        era_first[r["accountLabel"]] = min(era_first.get(r["accountLabel"], r["date"]), r["date"])
    csv_rows = [r for r in csv_rows if r["accountLabel"] not in era_first or r["date"] < era_first[r["accountLabel"]]]
    rows = era + csv_rows
    if not rows:
        raise SystemExit("No transactions yet. Pull from Era (save_pull.py) or import a CSV (import_csv.py) first.")
    categorize_all(rows)
    apply_overrides(rows)
    shift_early_bills(rows)

    keep = ("id", "date", "accountLabel", "rawDescription", "displayDescription", "amount",
            "category", "need", "pending", "source", "needsReview", "postedDate")
    txs = [{k: r.get(k, 0 if k == "need" else False) for k in keep} for r in rows]
    for t, r in zip(txs, rows):
        if r.get("firstSeen"):
            t["firstSeen"] = r["firstSeen"]
        if r.get("prevIds"):
            t["prevIds"] = r["prevIds"]
    txs.sort(key=lambda r: (r["date"], r["id"]), reverse=True)
    months = sorted({t["date"][:7] for t in txs})

    accounts = account_list(era_accounts, csv_accounts)
    ref = (LATEST_PULL or txs[0]["date"])[:10]
    out = {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "lastPull": LATEST_PULL,
        "source": "era" if era and not csv_rows else "csv" if csv_rows and not era else "mixed",
        "eraStart": min(era_first.values(), default=None),
        "title": CONFIG.get("dashboard_title") or "Personal Finances",
        "verses": CONFIG.get("verses", True),
        "accounts": accounts,
        "months": months,
        "categories": CONFIG["categories"],
        "nonSpend": CONFIG["non_spend"],
        "hidden": CONFIG["hidden"],
        "budgets": CONFIG["budgets"],
        "goals": CONFIG["goals"],
        "needDefaults": CONFIG.get("need_defaults", {}),
        "signIn": CONFIG.get("sign_in", {}),
        "balances": month_end_balances(rows, accounts, months),
        "bills": detect_bills(rows, ref),
        "overrides": load_json(os.path.join(DATA, "overrides.json"), {}).get("byId", {}),
        "transactions": txs,
    }
    with open(os.path.join(DATA, "finance-data.json"), "w") as f:
        json.dump(out, f, indent=1)

    import build_dashboard
    html = build_dashboard.build()
    print("Wrote data/finance-data.json: %d transactions, %s to %s" % (len(txs), months[0], months[-1]))
    print("Wrote %s and dashboard/artifact.html" % os.path.relpath(html, ROOT))
    for m in months:
        n = [t for t in txs if t["date"][:7] == m]
        tot = totals(n)
        print("  %s  %4d rows  income %10.2f  spend %10.2f" % (m, len(n), tot["income"], tot["spend"]))
    for a in accounts:
        bal = "no balance yet" if a["balance"] is None else "%.2f" % a["balance"]
        print("  account  %-24s %-10s %s" % (a["label"], a["type"], bal))

    # One line for the phone notification / chat summary. Same rows as the dashboard's Daily Recap:
    # first seen in the newest pull or import, hidden categories left out.
    new = [t for t in txs if t.get("firstSeen") and t["firstSeen"] == LATEST_PULL
           and t["category"] not in CONFIG.get("hidden", [])]
    buys = [t for t in new if t["category"] not in NON_SPEND and t["amount"] < 0]
    cur = months[-1]
    mtd = totals([t for t in txs if t["date"][:7] == cur])
    print("\nNOTIFY: %s. %s so far: $%s spent, $%s income." % (
        ("%d new transaction%s to review (%d purchase%s, $%s)" % (
            len(new), "" if len(new) == 1 else "s", len(buys), "" if len(buys) == 1 else "s",
            format(sum(-t["amount"] for t in buys), ",.2f"))) if new else "No new transactions",
        date(int(cur[:4]), int(cur[5:]), 1).strftime("%B"),
        format(mtd["spend"], ",.2f"), format(mtd["income"], ",.2f")))

    review = [t for t in txs if t["needsReview"]]
    if review:
        print("\nNo rule matched these (guessed Income/Other); add a rule to data/category-rules.json:")
        for t in review[:60]:
            print("  %s %9.2f  %-8s %s" % (t["date"], t["amount"], t["category"], t["rawDescription"][:60]))
        if len(review) > 60:
            print("  ... and %d more" % (len(review) - 60))


if __name__ == "__main__":
    main()
