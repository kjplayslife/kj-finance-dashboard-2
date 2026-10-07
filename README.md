# KJ Finance Dashboard 2.0

A personal finance dashboard that Claude sets up and keeps updated for you. It lives as a private page
in your Claude account (opens on your phone and computer) with a backup copy on your computer.

## What you get
- **Daily Recap**: everything new since you last checked. Rate each purchase 1 Want, 2 Could skip,
  3 Need, fix categories with a tap, see bills due this week.
- **Overview**: the month's income, spending, net, card debt and savings, with month-over-month charts;
  what to set aside for taxes, giving and savings from last month's income; bills coming up.
- **Transactions**: every transaction, searchable, with spending by category or by need over time.
  Add a note to any transaction from your phone or computer.
- **Budget**: budget vs actual for each category, built from your own averages.
- **Insights**: a month-by-month review: how you did, where to improve, a plan for next month.
- **Accounts**: every bank account and card, what's owed, net worth over time, one tap to each bank's
  sign-in page.

## How it stays updated
**Fully automatic.** [Era Context](https://era.app) reads your bank accounts (read-only), and a Claude
routine in the cloud updates your dashboard every morning, even when your computer is off. You get a
phone notification with a link straight to it. Setup walks you through all of it.

Don't want to connect your bank? Tell Claude during setup and it will set you up with **bank CSV files
only** instead: nothing connects to your bank, and you download a file from each account whenever you
want to update. Fully private, fully manual.

## What you need
- **A paid Claude plan: Pro or higher** (Max, Team or Enterprise also work). The daily cloud update
  needs it.
- **The Claude desktop app** (Mac or Windows), using the **Code** tab. Its built-in browser is where
  you'll do the sign-ups, so Claude can help if you get stuck.
- **The Claude phone app** (iPhone or Android), signed in, with notifications on: that's where the
  morning update and your dashboard show up.
- **An Era account** ([era.app](https://era.app)). Free for up to 2 linked accounts; more than 2 (each
  checking, savings and credit card counts) is a paid plan, about $9/month (check era.app for current
  pricing).
- **A free GitHub account** ([github.com](https://github.com)). It privately stores your finance folder
  so the morning update can reach it.
- **Python 3.9 or newer.** A Mac offers to install it the first time it's needed; on Windows, Claude
  installs it for you.
Plan on 30 to 45 minutes, most of it sign-ups and signing in to your banks.

## Before you set up
- **Turn off any older KJ finance plugin** (anything before 2.0) in Customize > Plugins. If it's still
  on, Claude can pick up one of its old skills and mix the two versions. Every 2.0 skill ends in "-v2".
- **Your full year of history:** Era can only pull about the last 1 to 3 months of transactions, plus
  everything from then on. To have **all of this year** in your dashboard, you'll download a
  year-to-date CSV (Jan 1 to today) from every bank account and card **once**, during setup. Claude
  shows you where on each bank's site and adds them; after that, Era keeps it current.
- **Link your banks through MX** when Era offers a choice: MX updates balances daily.

## Install
**In the Claude desktop app** (no terminal needed):
1. Open the plugin settings: **Customize > Plugins** (or the **+** button > **Plugins** > **Manage
   plugins**).
2. Go to **Marketplaces** > **Add**, and enter `kjplayslife/kj-finance-dashboard-2`.
3. Find **KJ Finance Dashboard 2.0** in the list and click **Install**.

**Or from a terminal:**
```bash
claude plugin marketplace add kjplayslife/kj-finance-dashboard-2 && claude plugin install kj-finance-dashboard-2@kj-finance
```

## Set up
1. Make an empty folder for your finances (for example `Documents/Finances`).
2. In the Claude desktop app, open the **Code** tab and start a new session in that folder.
3. Type **/finance-setup-v2**. Claude walks you through each step, builds the dashboard and checks it
   with you. When it asks for permission to run something, approve it.
4. At the end, **pin your dashboard** in the claude.ai sidebar and open it once on your phone.

## Use
- **/update-finances-v2**: fresh numbers right now (it also happens by itself every morning).
- **/finance-customize-v2**: budgets, categories, set-aside percentages, account names, the title, the Bible
  verse footers, or updating to a newer version of the dashboard.
- Or just ask Claude about your money in that folder.

## What it does with your data
- Your transactions stay in your finance folder on your computer and in your own private GitHub
  repository.
- Bank access goes through Era, read-only; Claude never sees bank passwords and never moves money.
- The dashboard is a private page in your own Claude account; only you can open it unless you share it.
- Scripts run locally with Python's standard library: no packages are installed and nothing is sent
  anywhere except what you set up (Era, your GitHub repo, your Claude account).

## License
Free for personal use: install it and run your own finance dashboard. Please don't resell, rebrand or
redistribute it. See [LICENSE](LICENSE). Not financial advice.
