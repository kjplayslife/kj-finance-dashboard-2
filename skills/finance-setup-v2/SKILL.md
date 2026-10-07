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

## Ground rules (tell them once, briefly, at the start)
- **Older KJ finance plugins off first.** If they ever installed an earlier KJ finance plugin (anything
  before 2.0, such as the first KJ Finance Dashboard), ask them to turn it off before going further
  (Customize > Plugins, switch it off or uninstall), then start a new Code session in this folder and say
  "/finance-setup-v2" again. Otherwise Claude can pick up one of the old skills mid-setup and mix the two
  versions. Every 2.0 skill ends in "-v2" (finance-setup-v2, update-finances-v2, finance-customize-v2); if
  your skill list shows other finance or dashboard skills without "-v2" from another plugin, that's an
  old one: name it for them.
- **Do sign-ups in the built-in browser.** Recommend they do every account step (Era, their bank, GitHub,
  claude.ai settings) in the browser pane inside the Claude app (Claude Code's built-in browser), so you
  can see where they are and help if they get stuck. Open pages there with the browser tools
  (`mcp__Claude_Browser__*`). If those tools aren't available, give them the link to open themselves.
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

## 1. Folder
Check where you are (`pwd`, `ls -A`). The dashboard lives in its own folder. If the current folder isn't
empty and isn't meant for this, suggest a new one such as `~/Documents/Finances` and ask them to open a
new Claude Code session in it (Code tab, choose that folder), then say "/finance-setup-v2" again. If
`data/config.json` already exists, this folder is already set up: offer `finance-customize-v2` or
`update-finances-v2` instead.

Check Python: `python3 --version` (3.9+). If missing on a Mac, running `python3` once offers to install
the command line tools; accept, then continue. On Windows: `py -3 --version`; if missing,
`winget install Python.Python.3.12`, then open a new session.

Check their Claude plan once: the daily cloud routine needs **Claude Pro or higher** (Max, Team,
Enterprise). If they're on the free plan, say so now: they can upgrade at claude.ai/settings, or use the
CSV-only setup (step 2).

## 2. The plan: fully automatic
Everyone sets up the **fully automatic** version (`--option cloud`); that's what makes this dashboard
worth having. Don't offer a menu. Tell them in a few lines what they're about to set up and why:
- **Era** reads their bank accounts (read-only) so nothing has to be downloaded by hand.
- A **Claude routine in the cloud** updates the dashboard every morning, even with their computer off,
  and sends a phone notification with a link to it.
- A free **GitHub** account holds their finance folder privately so the routine can reach it.
- What it costs: Claude Pro or higher (step 1), and Era is free for up to 2 linked accounts, **paid for
  more than 2** (each checking, savings and card counts as one; about $9/month, confirm on era.app).
  Ask how many accounts they'd link; with 3 or more, say the Era cost plainly.
Then ask if they're ready to go ahead.

**Only if they say they don't want it** (no bank connection, no GitHub, no cloud, no Era cost): offer
the **CSV-only** version (`--option csv`, `references/option-csv.md`). Nothing connects to their bank;
each update they download a CSV from each account and drop it in. It's the most private and the most
manual, and has no automatic morning updates. If they want Era but specifically refuse GitHub, the
"Era from this computer" version also exists (`--option local`, `references/option-local.md`): bring it
up only then.

## 3. Their preferences
Ask, in one short message (or AskUserQuestion where it fits):
- **Name** for the title ("Sam's Finances"); default "<first name>'s Finances".
- **Monthly set-asides** (the Overview's "Transfers to make" card). Ask which they want, then the
  percent for each:
  - **Taxes**: for business owners, freelancers, creators (anyone without taxes withheld). Common: 25%.
    Most people with a regular paycheck skip this.
  - **Tithe / giving**: common 10%. Figured after taxes.
  - **Savings**: common 10%. Figured after taxes and giving.
  Any they skip are off (0) and their tile is hidden. If they choose tithe, a Tithe category is added.
- **Bible verses**: each tab ends with a short Bible verse. They're on; tell them they can turn them off
  any time ("finance-customize-v2"). Don't ask them to opt in.

## 4. Create the folder
```bash
python3 "$E/scripts/setup_folder.py" --dest . --name "<Name>" --option <cloud|local|csv> \
  --tax <n> --tithe <n> --savings <n>
```
(`--title "<custom title>"` if they gave one.) It copies scripts/, dashboard/template.html,
data/category-rules.json, and writes data/config.json and data/overrides.json.

## 5. Connect the data
- Fully automatic (and "Era from this computer"): follow `references/era.md` (Era account, link banks
  through MX, connect Era to Claude, first full pull), then `references/option-cloud.md` in step 8.
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

## 6. Make it theirs
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

## 7. Publish and verify
Follow `references/publish-and-verify.md`: publish the private artifact with its database, save the URL
in data/config.json, open the local backup in the browser pane, check desktop and phone widths, and walk
them through the tabs. Every setup ends with them **pinning the dashboard** in the claude.ai sidebar and
**installing the Claude phone app** (signed in, notifications on), so it's one tap away on their phone.

## 8. Keep it updated
- Fully automatic: `references/option-cloud.md` (GitHub, the daily routine, the first test run, the phone
  notification).
- "Era from this computer": `references/option-local.md` (how /update-finances-v2 works; offer the daily
  task on this computer, and the desktop app's keep-awake setting).
- CSV-only: `references/option-csv.md`, "Next updates" (what to download each time).

## 9. Leave notes for future chats
Write `FINANCE.md` in their folder (short): which option, the artifact URL, accounts and where each comes
from, their goals, how to update ("/update-finances-v2"), how to change things ("/finance-customize-v2"), and
anything decided during setup (rules added, accounts excluded, routine id and time).
Write a two-line `CLAUDE.md`: "This folder is a KJ Finance Dashboard 2.0 finance folder. Read FINANCE.md
first; use the kj-finance-dashboard-2 skills (update-finances-v2, finance-customize-v2)."
For the fully automatic setup, commit and push these (see option-cloud.md).

## 10. Wrap up
Tell them, in a few lines: where the dashboard is (artifact link; local backup file name), how it updates
for their option, that ratings and category changes they make in the dashboard save to the dashboard,
and the three commands: "/update-finances-v2", "/finance-customize-v2", and asking you anything about their money.
