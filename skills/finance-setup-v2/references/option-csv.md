# Option 3: bank CSV files only (also: older history for options 1 and 2)

Nothing connects to their bank. They download a CSV export from each account; Claude imports it.

## First import
1. **List the accounts** they want in the dashboard: for each, a short name ("Chase Checking"), the type
   (Checking, Savings or CreditCard), the bank, and the last four digits (optional).
2. **Download each CSV** in their own browser (saved passwords): open the bank's website for them, they sign in themselves,
   then you guide them to the export. Typical places:
   - Chase: account > Download account activity (icon above transactions) > CSV, date range.
   - Bank of America: account > Download > "Microsoft Excel format" (CSV).
   - Wells Fargo: Download Account Activity > Comma delimited.
   - Capital One: account > View more transactions > Download Transactions > CSV.
   - American Express: Statements & Activity > Download (arrow icon) > CSV, "include all additional details" off.
   - Citi: account > Download (above transactions) > CSV.
   - Discover: Activity > Download > CSV. Ally: account > Download > CSV.
   - Credit unions and others: look for "Export", "Download", or a down-arrow near the transactions.
   Ask for **year-to-date at least** (Jan 1 of this year to today) so the dashboard has the whole year;
   more is fine if the bank allows it. Downloads land in their Downloads
   folder; have them put every CSV in the `csv/` folder
   inside the finance folder (tell them the full path).
3. **Import each file**, checking first with `--dry-run`:
   ```bash
   python3 scripts/import_csv.py "csv/<file>.csv" --account "Chase Checking" --type Checking \
     --institution Chase --mask 1234 --dry-run
   ```
   Look at the summary: columns found, date range, money in vs out, the first rows. Purchases must be
   negative. On cards the script detects backwards signs; if the sample still shows purchases as
   positive, add `--flip` (or `--no-flip` if it flipped wrongly). If the columns are wrong, pass
   `--date/--desc/--amount` (or `--debit/--credit`) with the header names it printed. When it looks
   right, run again without `--dry-run`. The CSV moves to `csv/imported/`.
4. **Balances**: CSVs don't carry a reliable current balance. Ask for each account's current balance
   (card = amount owed) and save them in data/config.json:
   ```json
   "manual_balances": {"Chase Checking": {"balance": 3120.55, "asOf": "2026-10-01"},
                       "Amex Gold": {"balance": 512.30, "asOf": "2026-10-01"}}
   ```
   They can skip this; the Accounts tab then says "Not set" for that account and net worth leaves it out.
5. `python3 scripts/sync.py`, then back to SKILL.md step 6.

Importing the same period again is safe: rows get stable ids from account + date + amount + description,
so overlaps don't double count and their ratings stay attached.

## Next updates (tell them this at the end of setup)
Each time they want fresh numbers ("/update-finances-v2"): download a new CSV for each account covering
at least the days since the last one (overlap is fine), drop them in `csv/`, and tell Claude the current
balances if they want the Accounts tab current. Weekly or every two weeks works well. There's no
automatic schedule for this option because the bank download is a manual step.

## The rest of the year (options 1 and 2)
Era only brings recent transactions (often ~2-3 months) plus new ones from now on, so the year's earlier
months come from a **one-time year-to-date CSV** (Jan 1 to today) for every linked account, done during
setup. Download them as in "First import" step 2, then import each with `--account` set to the **same
name** the Era account has in the dashboard (its label, from `era.account_labels`) and the same `--type`.
sync.py keeps CSV rows for that account only from before Era's first row, so nothing doubles. No
balances step: Era provides them. After this, Era keeps everything current; they never need CSVs again.
