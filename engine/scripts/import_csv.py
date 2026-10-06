#!/usr/bin/env python3
"""Turn a bank or card CSV export into data/raw/csv-<account>-<time>.json for sync.py.

Finds the header row, the date / description / amount columns (or separate debit and credit
columns), and puts amounts in the dashboard's convention: negative = money out. On a credit card
that means charges are negative and payments or refunds positive; many card exports use the
opposite sign, which is detected (or forced with --flip / --no-flip).

Each row gets a stable id from account + date + amount + description (+ a counter for exact
repeats), so importing an overlapping export again never double counts and edits stay attached.
Pending rows (a Status column saying Pending) are skipped. After a good import the CSV is moved
into csv/imported/ (use --keep to leave it).

Usage:
  python3 scripts/import_csv.py csv/export.csv --account "Chase Checking" --type Checking --institution Chase
  python3 scripts/import_csv.py csv/amex.csv --account "Amex Gold" --type CreditCard --dry-run
Column overrides when detection guesses wrong (header names or 0-based numbers):
  --date "Posting Date" --desc Payee --amount Amount     or     --debit Withdrawal --credit Deposit
"""
import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw")
DONE_DIR = os.path.join(ROOT, "csv", "imported")
TYPES = ("Checking", "Savings", "CreditCard")

DATE_NAMES = ["transaction date", "trans. date", "trans date", "date", "posting date", "post date", "posted date", "posted"]
DESC_NAMES = ["description", "payee", "merchant", "name", "transaction description", "details", "memo", "narrative"]
AMOUNT_NAMES = ["amount", "transaction amount", "amount (usd)", "amt"]
DEBIT_NAMES = ["debit", "withdrawal", "withdrawals", "debits", "money out", "charge", "charges"]
CREDIT_NAMES = ["credit", "deposit", "deposits", "credits", "money in", "payment", "payments"]
DATE_FORMATS = ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y", "%m-%d-%Y", "%Y/%m/%d", "%b %d, %Y", "%d %b %Y", "%B %d, %Y")


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def parse_date(s):
    s = (s or "").strip().split(" ")[0] if re.match(r"^\d", (s or "").strip()) else (s or "").strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def parse_amount(s):
    s = (s or "").strip()
    if not s:
        return None
    neg = s.startswith("(") and s.endswith(")") or s.endswith("-") or re.search(r"\bDR\b", s, re.I) is not None
    s = re.sub(r"[^\d.\-]", "", s.replace("(", "-") if s.startswith("(") else s)
    if s in ("", "-", ".", "-."):
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    return -abs(v) if neg else v


def read_rows(path):
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
        text = f.read()
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    return [r for r in csv.reader(io.StringIO(text), dialect) if any(c.strip() for c in r)]


def find_header(rows):
    """First row that names a date column and an amount (or debit/credit) column. Some banks put a
    summary block above it; some exports have no header at all (returns None)."""
    for i, r in enumerate(rows[:30]):
        names = [norm(c) for c in r]
        has_date = any(n in DATE_NAMES or n.endswith(" date") for n in names)
        has_amt = any(n in AMOUNT_NAMES + DEBIT_NAMES + CREDIT_NAMES for n in names)
        if has_date and has_amt:
            return i
    return None


def pick(names, wanted, override=None):
    if override is not None:
        if re.fullmatch(r"\d+", str(override)):
            return int(override)
        o = norm(override)
        if o in names:
            return names.index(o)
        sys.exit("Column %r not found. Columns: %s" % (override, ", ".join(names)))
    for w in wanted:
        if w in names:
            return names.index(w)
    return None


def detect_columns(rows, opts):
    h = find_header(rows)
    if h is None:
        # No header (e.g. Wells Fargo): date = first column that parses, amount = first numeric, desc = longest text.
        first = rows[0]
        di = next((i for i, c in enumerate(first) if parse_date(c)), None)
        ai = next((i for i, c in enumerate(first) if i != di and parse_amount(c) is not None), None)
        texts = [(len(c), i) for i, c in enumerate(first) if i not in (di, ai)]
        si = max(texts)[1] if texts else None
        cols = {"date": di, "desc": si, "amount": ai, "debit": None, "credit": None, "status": None}
        return None, rows, cols
    names = [norm(c) for c in rows[h]]
    cols = {
        "date": pick(names, DATE_NAMES, opts.date),
        "desc": pick(names, DESC_NAMES, opts.desc),
        "amount": pick(names, AMOUNT_NAMES, opts.amount),
        "debit": pick(names, DEBIT_NAMES, opts.debit),
        "credit": pick(names, CREDIT_NAMES, opts.credit),
        "status": pick(names, ["status", "transaction status"]),
    }
    if opts.debit or opts.credit:
        cols["amount"] = None
    elif cols["amount"] is not None:
        cols["debit"] = cols["credit"] = None
    if cols["date"] is None:
        cols["date"] = next((i for i, n in enumerate(names) if n.endswith(" date")), None)
    if cols["desc"] is None:
        cols["desc"] = next((i for i, n in enumerate(names) if i not in cols.values()), None)
    return rows[h], rows[h + 1:], cols


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--account", required=True, help="label shown in the dashboard, e.g. 'Chase Checking'")
    ap.add_argument("--type", choices=TYPES, required=True)
    ap.add_argument("--institution", default="")
    ap.add_argument("--mask", default="", help="last four digits, optional")
    ap.add_argument("--date"), ap.add_argument("--desc"), ap.add_argument("--amount")
    ap.add_argument("--debit"), ap.add_argument("--credit")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--flip", action="store_true", help="the export uses + for money out")
    g.add_argument("--no-flip", action="store_true", help="the export already uses - for money out")
    ap.add_argument("--dry-run", action="store_true", help="show what would be imported, write nothing")
    ap.add_argument("--keep", action="store_true", help="leave the CSV where it is after importing")
    opts = ap.parse_args()

    for path in opts.files:
        rows = read_rows(path)
        if not rows:
            print("%s: empty file, skipped" % path)
            continue
        header, body, cols = detect_columns(rows, opts)
        if cols["date"] is None or (cols["amount"] is None and cols["debit"] is None and cols["credit"] is None):
            sys.exit("%s: couldn't find the date and amount columns. Header: %s\nPass --date/--desc/--amount "
                     "(or --debit/--credit) with the column names." % (path, header or rows[0]))

        out, skipped, pending = [], 0, 0
        for r in body:
            get = lambda k: r[cols[k]] if cols[k] is not None and cols[k] < len(r) else ""
            if cols["status"] is not None and "pend" in get("status").lower():
                pending += 1
                continue
            dt = parse_date(get("date"))
            if cols["amount"] is not None:
                amt = parse_amount(get("amount"))
            else:
                deb, cre = parse_amount(get("debit")), parse_amount(get("credit"))
                amt = None if deb is None and cre is None else (abs(cre or 0) - abs(deb or 0))
            desc = re.sub(r"\s+", " ", get("desc")).strip()
            if not dt or amt is None or not desc:
                skipped += 1
                continue
            out.append({"date": dt, "rawDescription": desc, "amount": round(amt, 2)})
        if not out:
            sys.exit("%s: no rows could be read (%d skipped). Check the columns with --dry-run." % (path, skipped))

        # Sign: negative must mean money out. Only a single Amount column can be backwards.
        flip, why = False, "kept as exported"
        if opts.flip:
            flip, why = True, "flipped (--flip)"
        elif not opts.no_flip and cols["amount"] is not None:
            pay = [t for t in out if re.search(r"payment|thank you|autopay|pymt", t["rawDescription"], re.I)]
            pos = sum(1 for t in out if t["amount"] > 0) / len(out)
            if opts.type == "CreditCard":
                if pay and sum(1 for t in pay if t["amount"] < 0) > len(pay) / 2:
                    flip, why = True, "flipped: card payments were negative in the export"
                elif not pay and pos > 0.7:
                    flip, why = True, "flipped: most card rows were positive (charges)"
            elif pos > 0.9 and len(out) > 5:
                why = "kept, but almost every row is money in; if these are purchases, rerun with --flip"
        if flip:
            for t in out:
                t["amount"] = -t["amount"]

        seen = {}
        for t in out:
            k = (opts.account, t["date"], "%.2f" % t["amount"], t["rawDescription"].upper())
            seen[k] = seen.get(k, 0) + 1
            t["id"] = "csv-" + hashlib.sha1(("|".join(k) + "|%d" % seen[k]).encode()).hexdigest()[:14]

        out.sort(key=lambda t: t["date"], reverse=True)
        money_in = sum(t["amount"] for t in out if t["amount"] > 0)
        money_out = -sum(t["amount"] for t in out if t["amount"] < 0)
        print("%s -> %s (%s)" % (os.path.basename(path), opts.account, opts.type))
        print("  columns: %s" % ", ".join("%s=%s" % (k, (header[v] if header else "col %d" % v))
                                          for k, v in cols.items() if v is not None))
        print("  %d rows, %s to %s, money in $%s, money out $%s; sign %s" % (
            len(out), out[-1]["date"], out[0]["date"], format(money_in, ",.2f"), format(money_out, ",.2f"), why))
        if skipped or pending:
            print("  skipped %d unreadable row(s), %d pending row(s)" % (skipped, pending))
        for t in out[:5]:
            print("    %s %10.2f  %s" % (t["date"], t["amount"], t["rawDescription"][:60]))
        if opts.dry_run:
            print("  dry run: nothing written")
            continue

        now = datetime.now(timezone.utc)
        os.makedirs(RAW_DIR, exist_ok=True)
        slug = re.sub(r"[^a-z0-9]+", "-", opts.account.lower()).strip("-")
        dest = os.path.join(RAW_DIR, "csv-%s-%s.json" % (slug, now.strftime("%Y%m%d-%H%M%S")))
        with open(dest, "w") as f:
            json.dump({"source_file": os.path.basename(path), "imported_at": now.isoformat(timespec="seconds"),
                       "account": {"label": opts.account, "type": opts.type, "institution": opts.institution,
                                   "mask": opts.mask},
                       "rows": out}, f, indent=1)
        print("  saved %s" % os.path.relpath(dest, ROOT))
        if not opts.keep:
            os.makedirs(DONE_DIR, exist_ok=True)
            shutil.move(path, os.path.join(DONE_DIR, now.strftime("%Y%m%d-") + os.path.basename(path)))
            print("  moved the CSV to csv/imported/")


if __name__ == "__main__":
    main()
