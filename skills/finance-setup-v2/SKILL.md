---
name: finance-setup-v2
description: Builds the KJ Finance Dashboard 2.0 once Era and GitHub are ready (from /era-setup and /github-setup) - checks they're ready and fills any small gap, then creates the dashboard (a private claude.ai page plus a local HTML backup), brings in the year's history, publishes it, and sets up the daily cloud update. Also does a CSV-only dashboard for people who don't want a bank connection. Runs only when you type its slash command.
disable-model-invocation: true
---

# KJ Finance Dashboard 2.0: setup

Setup is three commands, in this order: **/era-setup** (Era account, banks linked, Era connected to
Claude), **/github-setup** (GitHub, the GitHub tools and connector, and KJ's setup checklist), then
**this one**, which builds the dashboard. So by the time someone types /finance-setup-v2, Era and
GitHub should already be ready. **Expect that, check it quietly, and don't walk them through it
again.** Something can still be missing (a bank still syncing, a connector that only shows in a new
session, `gh` signed out, or a step they skipped): find it in step 0 and fix just that piece.

What they end up with looks and works like KJ's: Daily Recap, Overview, Transactions, Budget, Insights
and Accounts tabs, published as a private claude.ai artifact (opens on their phone) with a local HTML
backup, updated every morning by a cloud routine. Go one step at a time, wait for them between steps,
and keep each message short. Do the technical work yourself; only ask them for what they must do
(choices, the year-to-date downloads, signing in).

## Paths
- Engine (copied into their folder): `E="${CLAUDE_PLUGIN_ROOT}/engine"`.
- Their finance folder = the folder this session runs in (ask before using it; see step 1).
- Detailed guides, read when you reach that part: `${CLAUDE_PLUGIN_ROOT}/skills/finance-setup-v2/references/`
  `era.md` (Era), `option-cloud.md` (fully automatic), `option-csv.md` (CSV-only, and the year-to-date CSVs),
  `option-local.md` (Era from this computer, only if asked),
  `publish-and-verify.md` (every option).

## How to run this setup (read first)
- **Simple and step by step.** Ask **one or two questions at a time**, with the AskUserQuestion tool
  (recommended option first, marked "(Recommended)"). Never send a wall of questions or a long plan.
  Keep each message to a few short lines, then wait for their answer.
- **Do the technical work yourself**, quietly. Only bring them in for choices, sign-ups and signing in.
  Don't narrate commands, file names or checks unless something needs their attention.

## Ground rules (follow throughout; mention only when they come up)
- **Sign-ups and bank logins happen in their own browser** (Chrome, Safari, whatever they normally use),
  not the Claude app's built-in browser. That's where their saved passwords are, and when Era connects
  a bank it hands off to the bank's site or app, which works best there. Open each link in their
  default browser for them: `open "<url>"` on a Mac, `cmd.exe /c start "" "<url>"` on Windows (or just
  give them the link). Then ask them to tell you when each step is done; if they get stuck, ask what
  they see (or a screenshot). Use the built-in browser pane only for checking the dashboard itself, and
  close it before you publish (one panel open for them at a time; publish-and-verify.md).
- **They type their own passwords.** Never type passwords, bank logins, card numbers or codes for them,
  never read them aloud from the screen, and never ask for them in chat. When a login page is up, hand
  over: "Sign in there; tell me when you're in."
- **Read-only money.** Era is used to read balances and transactions only. Never move money or change
  anything at a bank.
- Best place to run this: the Claude desktop app's **Code** tab (Claude Code). The Era options rely on
  Claude Code's session logs; Cowork and claude.ai chat can't run them.
- **Mac or Windows.** These steps are written for a Mac. On Windows: use `py -3` (or `python`) wherever
  they say `python3`; install missing tools with winget (`winget install Python.Python.3.12`,
  `winget install GitHub.cli`; Git is already there because Claude Code on Windows needs it); paths
  are like `C:\Users\<name>\Documents\Finances`. The cloud routine itself runs the same for everyone.

## 0. Ready check (quiet; Era and GitHub should already be done)
Check, without narrating:
1. **Era**: ToolSearch for "list_financial_accounts". If found, call `accounts__list_financial_accounts`
   once (`include_hidden: true`) and keep the result: it's the account list for step 3.
2. **GitHub**: `gh auth status` shows an active account.
(The GitHub connector and Claude GitHub App can't be checked from here; github-setup's checklist
covered them, and option-cloud.md B confirms them before the routine is made.)

Then:
- **Everything there**: one line ("Era and GitHub are ready, so let's build your dashboard") and go to
  step 1. Don't recap the prep steps.
- **A small gap**: fix only that piece, right here, using the matching step of the prep skill (read
  `${CLAUDE_PLUGIN_ROOT}/skills/era-setup/SKILL.md` or `.../github-setup/SKILL.md`; those skills only
  start from their slash command, so read the file instead of invoking them). Common ones:
  - **Era connected on claude.ai but its tools aren't in this session**: connectors only show up in a
    new session. Tell them: "Start a new Code session in this folder and type /finance-setup-v2 again;
    nothing is lost." Then stop.
  - **Era works but a bank or card is missing**: if they linked it under an hour ago, that's normal;
    carry on and check again in step 6. Otherwise link it now (era-setup step 3).
  - **Accounts come back `visibility: "tier_excluded"`**: past Era's free 2 accounts; they need the
    Organize plan (era-setup step 2). They upgrade themselves; carry on meanwhile.
  - **`gh` not signed in, or the wrong account**: github-setup step 3 (they run `gh auth login`).
- **Era or GitHub not started at all** (they skipped the prep commands): say so in one line and ask
  (AskUserQuestion): "Set it up here now (Recommended)" / "I'll run /era-setup and /github-setup first".
  Here now: follow era-setup, then github-setup (just the steps not done yet), then come back to
  step 1. Either way, don't make them repeat anything that's already done.
- **They don't want a bank connection at all**: skip the Era and GitHub checks; that's the CSV-only
  setup (step 4).
If anything goes wrong anywhere in setup, check `references/where-people-get-stuck.md` first.

## 1. Quiet checks (say nothing unless something needs them)
1. **Folder**: `pwd`, `ls -A`. The dashboard lives in its own folder. If this folder isn't empty and isn't
   meant for this, suggest a new one such as `~/Documents/Finances` and ask them to open a new Code
   session in it and type "/finance-setup-v2" again. If `data/config.json` already exists: with an
   `artifact_url` in it, this folder is already set up (tell them to type `/customize-fin-dashboard` or
   `/update-finances-v2` instead); without one, setup was interrupted (often the new session after adding
   Era): read FINANCE.md if it exists, and pick up where it left off (usually step 6) without asking the
   step 2-5 questions again.
2. **Other finance plugins**: look for any other finance, budget or money plugin that's installed **and
   turned on**: check your own skill list for finance/budget/dashboard skills that don't come from
   `kj-finance-dashboard-2`, and read `~/.claude/settings.json` (`enabledPlugins`) and
   `~/.claude/plugins/installed_plugins.json` if they exist. **If there are none, don't mention it.** If
   there are, name them in one line and suggest turning them off first (Customize > Plugins, or type
   `/plugin`), since Claude could pick up one of their skills mid-setup; then start a new Code session in
   this folder and type "/finance-setup-v2" again. If they'd rather keep going, continue.
3. **Python**: `python3 --version` (3.9+). If missing on a Mac, running `python3` once offers to install
   the command line tools; ask them to accept, then continue. On Windows: `py -3 --version`; if missing,
   `winget install Python.Python.3.12`, then open a new session.

Then (unless you already said hello in step 0) greet them in one or two lines (what they're about to
get, about 20-30 minutes now that Era and GitHub are done, most of it the year-to-date downloads in
step 6) and go straight to the first question.

## 2. Personal, business or both
AskUserQuestion: **"Is this dashboard for your personal money, a business, or both?"**
Options: Personal / Business / Both (one dashboard for each).
- **Both**: in the same call or right after, ask **"Which one should we set up first?"** (Personal
  (Recommended) / Business). Tell them the other one comes right after this one finishes, in its own
  folder, and goes much faster because Era, GitHub and the phone app are already done. Note the choice
  in FINANCE.md so you remember to offer it at the end. (One Era login holds both sets of accounts.)
- Then one plain question for the title: personal: their first name ("Sam's Finances"); business: the
  business name ("Acme Studio Finances").

## 3. Which accounts go on this dashboard
Their banks are already linked in Era, so don't ask which banks they use. Show the accounts from step 0
as a short list (name, bank, type; no balances) and ask one AskUserQuestion:
- **Only one dashboard** (personal or business): **"Are these all the accounts for this dashboard?"**
  ("Yes, that's everything (Recommended)" / "One is missing" / "Leave some out").
- **"Both"**: **"Which of these are for <your personal money / the business>?"** (multiSelect, one
  option per account; if there are more than four, ask by bank, or list them and let them type the
  names under "Other").
Then: anything to leave out goes in `era.exclude_accounts` (or, with "Both", put this dashboard's keys
in `era.only_accounts`; `references/era.md` D.1) when the folder exists in step 5b. A missing one:
recently linked, wait (step 6 checks again); otherwise link it now (era-setup step 3).
Keep the list: it's your checklist for the year-to-date CSVs in step 6. Era's cost was covered in
era-setup; bring it up only if accounts come back `tier_excluded` (step 0).

## 4. How it will work (fully automatic)
Era and GitHub being ready means they're set for the **fully automatic** version (`--option cloud`).
Don't ask them to choose again or re-sell it; just say in two or three lines what happens from here:
you build the dashboard and bring in this year's history, publish it to their Claude account, then set
up the routine that updates it **every morning in the cloud** (even with their computer off) and sends a
phone notification with a link to it.

Other versions, only when they come up:
- **They don't want a bank connection** (said in step 0, or now): the **CSV-only** version
  (`--option csv`, `references/option-csv.md`). Nothing connects to their bank; each update they download
  a CSV from each account and drop it in. The most private and the most manual, no automatic updates.
- **Era is ready but they've decided against GitHub/the cloud**: first answer their actual worry in a few
  plain words (the repo is private; you do the GitHub steps; the cloud run works with their computer off
  and needs nothing from them day to day). Only if they still insist: "Era from this computer"
  (`--option local`, `references/option-local.md`), with its limits and the Claude app's **keep awake**
  setting; they can move to the cloud version any time ("set up the automatic version").

## 5. Monthly set-asides
First explain in two lines: the Overview shows what to move each month from last month's income, worked
out **in order: taxes first (off the top), then tithe from what's left, then savings from what's left
after that.** Then:
1. AskUserQuestion (multiSelect): **"What do you want to set aside each month?"**
   - **Taxes**: for business owners, freelancers and creators (anyone without taxes taken out of their
     pay). Recommend it for a business dashboard; most people with a regular paycheck skip it.
   - **Tithe / giving**
   - **Savings**
   - (Picking none is fine: the card is hidden.)
2. Their percentages, at most two questions per AskUserQuestion call (if they picked all three, ask
   savings in a second call), recommended option first:
   - Taxes: **25% (Recommended)** / 30% / 20%. (Business: 25-30%.)
   - Tithe / giving: **10% (Recommended)** / 15% / 5%.
   - Savings: **10% (Recommended)** / 15% / 20%.
   They can type any other number under "Other". Anything they didn't pick is 0 (off). A tithe adds a
   Tithe category.
**Don't ask about the Bible verses here**: they're on by default and come up at the end (step 11).

## 5b. Create the folder
```bash
python3 "$E/scripts/setup_folder.py" --dest . --name "<first name or business name>" --option <cloud|local|csv> \
  --tax <n> --tithe <n> --savings <n> [--business]
```
`--business` for a business dashboard (adds an "Owner's Pay" category, counted apart from spending, with
its own Overview card; the title becomes "<Business> Finances"). It copies scripts/,
dashboard/template.html, data/category-rules.json, and writes data/config.json and data/overrides.json.
**Setting up both?** Each dashboard is its own folder, Era login shared: in each folder set
`era.only_accounts` to that dashboard's own account keys (see `references/era.md`), so business accounts
never show up on the personal dashboard or the other way round.
Right away, start `FINANCE.md` with their answers so far (personal or business, "Both" and which comes
next, which Era accounts belong to this dashboard, set-asides); write step 3's `exclude_accounts` /
`only_accounts` into data/config.json now; if the session restarts, step 1 picks up from it. Step 10
fills in the rest.

## 6. Connect the data
- Fully automatic (and "Era from this computer"): Era is connected and their banks are linked
  (era-setup, checked in step 0). If an account was still syncing in step 3, call
  `accounts__list_financial_accounts` again and see if it's there now; if it still isn't after an hour,
  link it again (era-setup step 3: white **Connect** > **Link with MX**; **Stripe** if MX doesn't work).
  Then the first full pull (era.md D), and `references/option-cloud.md` in step 9.
  **Before the first pull, explain history** in a few plain lines: **Era can only pull about the last
  1 to 3 months** of transactions, plus everything from now on. To have **all of this year** in the
  dashboard, they download a **year-to-date CSV** (Jan 1 to today) from **every** bank account and card
  they linked, **once**, during this setup. After that, Era keeps it current and they never need CSVs
  again. Budgets, insights and the month-over-month charts depend on it, so treat it as part of setup,
  not an extra: walk them through each bank's download (`references/option-csv.md`, "First import"
  step 2) and import them as in "The rest of the year (options 1 and 2)" after the first pull; it won't
  double count. Only if they firmly decline, say history will build up from here. After the pull, tell
  them how far back Era reached (the first month sync.py prints).
- CSV-only: follow `references/option-csv.md` (download year-to-date CSVs, import, balances).

Finish this step with `python3 scripts/sync.py` succeeding. Show them the month totals it prints and ask
if they look about right.

## 7. Fit the categories to them (the first thing you work on together)
The folder starts with a generic personal list (Groceries, Dining Out, Shopping, Rent and Utilities,
Gas & Auto, ...). Most people, and every business, have categories in it they never use and spending it
doesn't fit. Empty categories make a brand-new dashboard look broken, so **before anything is published,
build their category list from their own transactions, with them**. Don't skip this or leave it for later.
1. `python3 scripts/category_report.py`: each category's purchases and total, the categories with **no
   spending at all**, the biggest **unsorted merchants** (in Other or no rule matched), and money in.
2. Propose their list in one short message, plain words, no file names:
   - **Keep**: categories with real spending (with the total, e.g. "Software & Tools, $2,340").
   - **Remove**: every category with no spending (say which).
   - **New**: categories their unsorted merchants clearly form. Business examples: Software & Tools,
     Contractors, Advertising, Travel, Equipment, Payment Fees, Payroll. Personal: Pets, Kids, Health,
     Travel, Gifts. Name the merchants that would go in each.
   - **Rename** anything that reads better for them (business: "Rent and Utilities" -> "Office & Rent").
   Aim for roughly 6-12 spending categories; "Other" stays as the catch-all.
3. AskUserQuestion: **"Use these categories?"** ("Yes, looks right (Recommended)" / "I want to change
   some"). Changes: ask what, one or two questions at a time.
4. Apply it:
   - `categories` in data/config.json: their list, plus the ones the engine needs that aren't spending:
     **Income, Card Payments, Transfers, Reimbursed, Gift** (and **Owner's Pay** on a business
     dashboard; **Tithe** if they set a tithe goal). Order = dropdown order; put Card Payments and the
     non-spending ones last.
   - Removed or renamed categories: take them out of `budgets` and `need_defaults`, and fix every rule in
     data/category-rules.json that points at them (to the new name, or the category those merchants
     really belong in) so nothing lands in a category that no longer exists.
   - New categories: add rules at the TOP of data/category-rules.json for their merchants
     (`{"match": "REGEX", "category": "...", "display": "Clean Name"}`; `"when": "in"|"out"` for money
     in/out), and `need_defaults` if obvious (3 Need for business costs like Software & Tools).
5. Then the rest of the unsorted rows: group by merchant, propose a category for the frequent ones, and
   ask about anything ambiguous (Venmo, Zelle, checks, transfers between their own accounts, where
   income comes from). Income that's really a transfer from their own other account is `Transfers`.
6. `python3 scripts/sync.py`, then `category_report.py` again: **no category without spending** (unless
   they asked to keep one for the future; give it a budget so it shows) and only a little left in Other.
   Show them the final list with totals.

## 7b. Account names and budgets
1. **Account names**: Era names accounts like "CREDIT CARD-1234". Offer short names ("Chase Card") and
   save them under `era.account_labels` in data/config.json (key = account_group_key from the accounts
   list). CSV accounts already have the names they gave.
2. **Budgets** (after the categories are final, so there's one for each real category):
   `python3 scripts/suggest_budgets.py`, show the table (their own monthly averages rounded up), adjust
   anything they want, then `python3 scripts/suggest_budgets.py --write --all` (and edit
   data/config.json budgets for their changes).
3. `python3 scripts/sync.py` again.

## 8. Publish and verify
Follow `references/publish-and-verify.md`: check the local backup quietly in the browser pane (desktop
and phone widths), **close the browser pane**, then publish the private artifact with its database (it
opens in the app by itself; that's the only thing they should see), save the URL in data/config.json,
and walk them through the tabs in the panel that opened. Every setup ends with them **pinning the dashboard** in the claude.ai sidebar and
**installing the Claude phone app** (signed in, notifications on), so it's one tap away on their phone.

## 9. Keep it updated
- Fully automatic: `references/option-cloud.md` (the private repo, the daily routine, the first test run, the phone
  notification).
- "Era from this computer" (only if they insisted in step 4): `references/option-local.md` (how
  /update-finances-v2 works; the daily task on this computer, and the desktop app's keep-awake setting).
- CSV-only: `references/option-csv.md`, "Next updates" (what to download each time).

## 10. Leave notes for future chats
Write `FINANCE.md` in their folder (short): which option, the artifact URL, accounts and where each comes
from, their goals, how to update ("/update-finances-v2"), how to change things ("/customize-fin-dashboard"), and
anything decided during setup (rules added, accounts excluded, routine id and time).
Write a two-line `CLAUDE.md`: "This folder is a KJ Finance Dashboard 2.0 finance folder. Read FINANCE.md
first. To update or change the dashboard, type /update-finances-v2 or /customize-fin-dashboard (the
plugin's skills only run from their slash commands)."
For the fully automatic setup, commit and push these (see option-cloud.md).

## 11. Wrap up
Tell them, in a few lines: where the dashboard is (artifact link; local backup file name), how it updates
for their option, that ratings and category changes they make in the dashboard save to the dashboard,
and the three commands: "/update-finances-v2", "/customize-fin-dashboard", and asking you anything about their money.
Then, in one line: each tab ends with a short Bible verse; if they'd rather not have them, they can say
"turn off the verses" any time.
**If they chose "Both" in step 2**, offer to set up the other dashboard now: they make a new folder
(e.g. `~/Documents/Business Finances`), open a new Code session in it and type "/finance-setup-v2". Era,
GitHub and the phone app are already done, so it's mostly picking that dashboard's accounts, the
year-to-date CSVs, and its own routine.
