---
name: finance-customize-v2
description: Change anything about a KJ Finance Dashboard 2.0 - budgets, the tax/tithe/savings set-asides and their percentages, categories (add, rename, remove, "+ New category"), category rules for a merchant, account names, hiding an account, the dashboard title, the Bible verse footers, or updating the dashboard to the plugin's newest version. Triggers on "/finance-customize-v2", "change my budget", "add a category", "new category", "rename this account", "turn off the verses", "change my savings percent", "stop counting X as income", "update my dashboard to the new version".
---

# KJ Finance Dashboard 2.0: customize

Work in the finance folder (has `data/config.json`). For a cloud setup (`setup_option: "cloud"`),
**first `git pull -q origin claude/data`** (the routine commits every morning), and at the end commit and
push to `claude/data` so the routine uses the change. After any change: `python3 scripts/sync.py`, publish
`dashboard/artifact.html` to `artifact_url` (read it first for cloud; `url` set, no `capabilities`, no
`icon`), and check the change in the browser pane (local backup file, desktop and phone width).

## Where things live
- `data/config.json`: `dashboard_title`, `verses` (true/false), `goals` (`taxPct`, `tithePct`,
  `savingsPct`; 0 = off), `budgets` (category -> monthly $), `categories` (list; order = menu order),
  `need_defaults` (category -> starting rating 1 Want / 2 Could skip / 3 Need), `non_spend` (categories
  that aren't spending: Income, Card Payments, Transfers, Reimbursed, Gift), `hidden` (left out of the
  Daily Recap), `era.account_labels` (Era account key -> display name), `era.exclude_accounts` (Era keys
  to ignore), `era.only_accounts` (when set, ONLY these Era keys are read; use it when one Era login
  feeds two dashboards, e.g. personal and business, since a relinked account gets a new key that an
  exclude list would miss), `bill_month_shift` (`{"match": REGEX, "days_before": 2}`: a matching bill
  that posts in a month's last N days counts on the 1st of the next month; balances keep the real
  date), `manual_balances` (CSV accounts), `sign_in` (institution -> sign-in URL for the Accounts tab).
- `data/category-rules.json`: ordered rules, first match wins; put the person's own rules at the top.
  `{"match": "REGEX", "category": "...", "display": "Clean Name", "when": "in"|"out", "amount": 12.34}`.
- `data/overrides.json`: one-off fixes by transaction id: `{"byId": {"<id>": {"category", "display", "date", "need"}}}`.
- Changes they make in the dashboard itself (categories, ratings, notes, budgets edited on the Budget
  tab, sent check-offs) are saved by the page, not in these files. If they ask why a file change didn't show for one
  transaction, the page's own edit for that row wins.
- `dashboard/template.html`: the page itself. Don't edit it for preferences; config covers those. If
  they want a design change, edit it, run `python3 scripts/build_dashboard.py`, check desktop + phone,
  and note it in FINANCE.md (an update with --refresh would replace it).

## Common requests
- **New category** (also what the dashboard's "+ New category" option points to): add it to
  `categories` (before "Card Payments"), give it a budget, add `need_defaults` if obvious, and add rules
  for the merchants that belong in it (ask which; look at their transactions for candidates). It gets a
  neutral color automatically. Rows they already re-categorized in the dashboard keep their choice.
- **Rename or remove a category**: update `categories`, `budgets`, `need_defaults`, and every rule using it
  (removed -> point those rules at another category).
- **Budgets**: edit `budgets`, or `python3 scripts/suggest_budgets.py` to see their averages
  (`--write --all` to replace all).
- **Set-asides**: `goals` percents; 0 hides that tile. Tithe on -> make sure "Tithe" is in `categories`.
- **Verses**: `"verses": false` removes the Bible verse footers (true brings them back).
- **Title**: `dashboard_title`.
- **Account name**: Era -> `era.account_labels[key]`; CSV -> rename the `label` in each `data/raw/csv-*.json`
  for that account and the key in `manual_balances`, and use the new name on future imports.
- **Hide an account**: Era -> add its key to `era.exclude_accounts` (or, if `era.only_accounts` is set,
  remove it there).
- **Owner's pay / owner draws** (business dashboards): add an "Owner's Pay" category (put it in
  `non_spend`) and a rule for transfers to the owner's personal account. Its Overview card and chart
  appear automatically when that category exists.
- **A bill paid a day early lands in the wrong month** (e.g. a phone bill on the 31st for next month):
  set `bill_month_shift` with a regex for that payee.
- **Something counted wrong** ("that's not income, it's my own transfer"): add a rule (e.g. category
  Transfers, `"when": "in"`) rather than one-off overrides, so future rows are right too.
- **Update to the newest plugin version**: first the plugin itself, which they do in the Claude app:
  Customize > Plugins > white **+ Add** dropdown > **Manage marketplaces** > the **...** next to **kj-finance** > **Check for updates** (wait for "Marketplace updated") > **Done**; then Plugins > **Yours** > the KJ Finance Dashboard plugin > **Update** (it says "Updated"). New sessions have the new version. Then in a new session: `python3 "${CLAUDE_PLUGIN_ROOT}/engine/scripts/setup_folder.py"
  --dest . --refresh` (replaces scripts/ and dashboard/template.html only; their config, rules, data and
  edits stay). Cloud setups also take the new routine steps: `cp "${CLAUDE_PLUGIN_ROOT}/engine/ROUTINE.md" .`
  (the routine reads this file every morning). Then sync, publish, check, and (cloud) commit + push.
