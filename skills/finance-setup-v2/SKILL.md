---
name: finance-setup-v2
description: First-time setup for KJ Finance Dashboard 2.0. Walks the user step by step from "just installed" to a working personal finance dashboard (a private claude.ai page plus a local HTML backup), kept updated fully automatically (Era + a daily cloud routine on GitHub), or from bank CSV files only for people who don't want a bank connection. Triggers on "/finance-setup-v2", "set up my finance dashboard", "set up KJ finance dashboard", "finance dashboard 2.0 setup", "set up my finances", or when update-finances-v2 finds no data/config.json.
---

# KJ Finance Dashboard 2.0: setup

Take the person from nothing to a dashboard that looks and works like KJ's: Daily Recap, Overview,
Transactions, Budget, Insights and Accounts tabs, published as a private claude.ai artifact (opens on
their phone) with a local HTML backup. Go one step at a time, wait for them between steps, and keep
each message short. Do the technical work yourself; only ask them for what they must do (sign-ups,
signing in to their bank, choices).

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
  they see (or a screenshot). Use the built-in browser pane only for checking the dashboard itself.
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

## 0. Era and GitHub ready? (before anything else)
KJ's course sets up Era (account, every bank and card linked, the Era Context connector) and GitHub
(`gh` signed in, the GitHub connector on Claude) **before** the dashboard is built. Check quietly:
ToolSearch for "list_financial_accounts" (Era), and `gh auth status` (GitHub).
- **Both there**: say nothing and go to step 1.
- **Otherwise**: open with a one-line hello (what they're about to get, about 30-45 minutes, one step at
  a time), then run the missing setup skill(s) first, in this order: **era-setup**, then
  **github-setup** (Skill tool `kj-finance-dashboard-2:era-setup` / `kj-finance-dashboard-2:github-setup`,
  or read `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md` and follow it). They hold the walk-throughs;
  don't repeat them here. When they finish, come back to step 1.
- If era-setup ends with "start a new Code session" (the Era tools only show up in a new session), they
  type "/finance-setup-v2" in the new session; nothing is lost, setup starts again at step 0 and moves on.
(If they say up front they don't want a bank connection at all, skip this step: that's the CSV-only
setup, step 4.)
If anything goes wrong anywhere in setup, check `references/where-people-get-stuck.md` first.

## 1. Quiet checks (say nothing unless something needs them)
1. **Folder**: `pwd`, `ls -A`. The dashboard lives in its own folder. If this folder isn't empty and isn't
   meant for this, suggest a new one such as `~/Documents/Finances` and ask them to open a new Code
   session in it and type "/finance-setup-v2" again. If `data/config.json` already exists: with an
   `artifact_url` in it, this folder is already set up (offer `finance-customize-v2` or
   `update-finances-v2` instead); without one, setup was interrupted (often the new session after adding
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
get, roughly 30-45 minutes, you'll go one step at a time) and go straight to the first question.

## 2. Personal, business or both
AskUserQuestion: **"Is this dashboard for your personal money, a business, or both?"**
Options: Personal / Business / Both (one dashboard for each).
- **Both**: in the same call or right after, ask **"Which one should we set up first?"** (Personal
  (Recommended) / Business). Tell them the other one comes right after this one finishes, in its own
  folder, and goes much faster because Era, GitHub and the phone app are already done. Note the choice
  in FINANCE.md so you remember to offer it at the end.
- Then one plain question for the title: personal: their first name ("Sam's Finances"); business: the
  business name ("Acme Studio Finances").

## 3. Banks and cards (for the dashboard you're setting up now)
One AskUserQuestion call with two questions:
1. **"Which banks do you use for <your personal money / the business>?"** (multiSelect): offer the
   four most common (Chase, Bank of America, Wells Fargo, Capital One); they pick "Other" to type the
   rest (Ally, a credit union, ...). Include the banks behind their credit cards too.
2. **"How many credit cards do you use for <it>?"** Options: None / 1 / 2-3 / 4 or more.
Keep the answers: they're your checklist for linking in Era, for the year-to-date CSVs, and for the Era
cost. Right after they answer, tell them plainly how many accounts that comes to (each checking, savings
and credit card counts as one) and that **linking more than 2 accounts in Era costs about $9 a month**
(Era's **Organize** plan, up to 15 accounts; 2 or fewer is free; confirm the price on era.app).

## 4. How it will work (fully automatic)
Everyone sets up the **fully automatic** version (`--option cloud`); that's what makes this dashboard
worth having. In a few short lines (no menu):
- **Era** reads their bank accounts (read-only), so nothing has to be downloaded by hand.
- A **Claude routine in the cloud** updates the dashboard every morning, even with their computer off,
  and sends a phone notification with a link to it.
- A free **GitHub** account keeps their finance folder private and reachable by the routine; you do the
  GitHub steps, they just sign in.
- Cost: **Claude Pro ($20/month) or higher** (Max, Team, Enterprise). Era is free for up to 2 linked
  accounts; more than 2 needs Era's **Organize** plan (about $9/month; confirm on era.app). From their answers in step 3, say how
  many accounts that is and whether it means the paid Era plan.
Then AskUserQuestion: **"Ready to set it up this way?"** Options: "Yes, let's go (Recommended)" /
"I'd rather not connect my bank". If they're on the free Claude plan, they can upgrade at
claude.ai/settings first.

**Only if they don't want it** (no bank connection, no GitHub, no cloud, no Era cost): offer the
**CSV-only** version (`--option csv`, `references/option-csv.md`). Nothing connects to their bank; each
update they download a CSV from each account and drop it in. The most private and the most manual, with
no automatic morning updates.

**If they hesitate about GitHub or the cloud, make the case for it first; don't switch on the first
"hmm".** In plain words: the cloud version runs every morning even when their computer is off or asleep,
sends the phone notification with the link, and needs nothing from them day to day. Running from their
computer only works while it's on, awake and the Claude app is open, so updates get missed. GitHub is
free and the repo is private (only they can see it), and you do the GitHub steps for them; they only
sign in. Answer their actual worry (privacy, another account, "I don't code") and ask again.

**Only if they still insist on running it from their computer:** set up "Era from this computer"
(`--option local`, `references/option-local.md`). That's when you explain its limits and the Claude
app's **keep awake** setting (option-local.md), and remind them they can move to the cloud version any
time ("set up the automatic version"); everything carries over.

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
next, banks, number of cards, set-asides); if the session restarts, step 1 picks up from it. Step 10
fills in the rest.

## 6. Connect the data
- Fully automatic (and "Era from this computer"): Era is already connected and their banks linked
  (step 0, era-setup). Call `accounts__list_financial_accounts` and compare with their bank list from
  step 3. Anything missing: link it now as in era-setup step 3 (white **Connect** > **Link with MX**;
  **Stripe** if MX doesn't work for that bank; it can take **15 minutes to 1 hour** to show up, so keep
  going and check again later). Then the first full pull (era.md D), and `references/option-cloud.md`
  in step 9.
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

## 7. Make it theirs
1. **Account names**: Era names accounts like "CREDIT CARD-1234". Offer short names ("Chase Card") and
   save them under `era.account_labels` in data/config.json (key = account_group_key from the accounts
   list). CSV accounts already have the names they gave.
2. **Categories**: sync.py lists rows no rule matched. Group them by merchant, propose a category for the
   frequent ones, and add rules at the TOP of data/category-rules.json (`{"match": "REGEX", "category":
   "...", "display": "Clean Name"}`; `"when": "in"|"out"` for money in/out). Ask about anything
   ambiguous (Venmo, Zelle, checks, transfers between their own accounts, where income comes from).
   Income that's really a transfer from their own other account should be `Transfers`.
3. **Budgets**: `python3 scripts/suggest_budgets.py`, show the table (their own monthly averages rounded
   up), adjust anything they want, then `python3 scripts/suggest_budgets.py --write` (and edit
   data/config.json budgets for their changes).
4. `python3 scripts/sync.py` again.

## 8. Publish and verify
Follow `references/publish-and-verify.md`: publish the private artifact with its database, save the URL
in data/config.json, open the local backup in the browser pane, check desktop and phone widths, and walk
them through the tabs. Every setup ends with them **pinning the dashboard** in the claude.ai sidebar and
**installing the Claude phone app** (signed in, notifications on), so it's one tap away on their phone.

## 9. Keep it updated
- Fully automatic: `references/option-cloud.md` (the private repo, the daily routine, the first test run, the phone
  notification).
- "Era from this computer" (only if they insisted in step 4): `references/option-local.md` (how
  /update-finances-v2 works; the daily task on this computer, and the desktop app's keep-awake setting).
- CSV-only: `references/option-csv.md`, "Next updates" (what to download each time).

## 10. Leave notes for future chats
Write `FINANCE.md` in their folder (short): which option, the artifact URL, accounts and where each comes
from, their goals, how to update ("/update-finances-v2"), how to change things ("/finance-customize-v2"), and
anything decided during setup (rules added, accounts excluded, routine id and time).
Write a two-line `CLAUDE.md`: "This folder is a KJ Finance Dashboard 2.0 finance folder. Read FINANCE.md
first; use the kj-finance-dashboard-2 skills (update-finances-v2, finance-customize-v2)."
For the fully automatic setup, commit and push these (see option-cloud.md).

## 11. Wrap up
Tell them, in a few lines: where the dashboard is (artifact link; local backup file name), how it updates
for their option, that ratings and category changes they make in the dashboard save to the dashboard,
and the three commands: "/update-finances-v2", "/finance-customize-v2", and asking you anything about their money.
Then, in one line: each tab ends with a short Bible verse; if they'd rather not have them, they can say
"turn off the verses" any time.
**If they chose "Both" in step 2**, offer to set up the other dashboard now: they make a new folder
(e.g. `~/Documents/Business Finances`), open a new Code session in it and type "/finance-setup-v2". Era,
GitHub and the phone app are already done, so it's mostly linking that dashboard's accounts, the
year-to-date CSVs, and its own routine.
