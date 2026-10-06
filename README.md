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

## Three ways to keep it updated (you pick during setup)
1. **Fully automatic (recommended).** [Era Context](https://era.app) reads your bank accounts
   (read-only); a Claude routine in the cloud updates the dashboard every morning and sends a phone
   notification, even when your computer is off. Needs an Era account (free for up to 2 accounts,
   $9/month for more), a free GitHub account, and a Claude Pro plan or higher.
2. **Era, updated from your computer.** Same bank connection and Era cost, no GitHub. Say
   "/update-finances-v2" when you want fresh numbers, or let a daily task run while your computer is on.
3. **Bank CSV files only.** Nothing connects to your bank; you download a CSV from each account when you
   want to update. Most private, most manual.

## Before you set up
- **Turn off any older KJ finance plugin** (anything before 2.0) in Customize > Plugins. If it's still
  on, Claude can pick up one of its old skills and mix the two versions. Every 2.0 skill ends in "-v2".
- **Your full year of history:** connecting through Era only brings in recent transactions (usually the
  last couple of months) and everything from then on. To have all of this year in the dashboard, download
  a year-to-date CSV (Jan 1 to today) from every bank account and card **once**, during setup. Claude
  shows you where and adds them; after that Era keeps it current.
- **Link your banks through MX** when Era offers a choice: MX updates balances daily.

## Requirements
- The Claude desktop app, using the **Code** tab (Claude Code). Its built-in browser is where you'll do
  the sign-ups so Claude can help if you get stuck.
- Python 3.9 or newer (macOS offers to install it the first time it's needed).
- For options 1 and 2: an Era Context account. **Free for up to 2 linked accounts; more than 2 (each
  checking, savings and credit card counts) is $9/month** (check era.app for current pricing).
- For option 1: a GitHub account (free) and Claude Pro or higher.

## Install
In the Claude desktop app: **Customize > Plugins > Add**, then add this repository as a marketplace, or
**Upload plugin** with the zip of this folder. From a terminal:
```bash
claude plugin marketplace add kjplayslife/kj-finance-dashboard-2
claude plugin install kj-finance-dashboard-2@kj-finance
```

## Set up
1. Make an empty folder for your finances (for example `Documents/Finances`).
2. Open a new Claude Code session in that folder.
3. Say **"/finance-setup-v2"**. Claude asks which version you want, walks you through each step, builds the
   dashboard and checks it with you. Plan on 20 to 40 minutes, most of it the bank and account sign-ups.

## Use
- **/update-finances-v2**: fresh numbers (automatic in option 1).
- **/finance-customize-v2**: budgets, categories, set-aside percentages, account names, the title, the Bible
  verse footers, or updating to a newer version of the dashboard.
- Or just ask Claude about your money in that folder.

## What it does with your data
- Your transactions stay in your finance folder on your computer (and, for option 1, in your own
  private GitHub repository).
- Bank access goes through Era, read-only; Claude never sees bank passwords and never moves money.
- The dashboard is a private page in your own Claude account; only you can open it unless you share it.
- Scripts run locally with Python's standard library: no packages are installed and nothing is sent
  anywhere except what you set up (Era, your GitHub repo, your Claude account).

## License
Free for personal use: install it and run your own finance dashboard. Please don't resell, rebrand or
redistribute it. See [LICENSE](LICENSE). Not financial advice.
